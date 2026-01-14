# 数据在 CPU 和 GPU 之间传输成本较高，可通过多条 CUDA 流并行搬运与计算来支撑更大数据集。

import copy
import gc
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import csv

import joblib
import matplotlib.pyplot as plt
import numpy as np  # 1.26.2
import optuna  # 4.3.0
import pandas as pd  # 2.2.3
import shap
import statsmodels.api as sm

import torch  # 版本: 1.10.1+cu111
import torch.nn as nn
import torch.nn.functional as F
import xgboost as xgb  # 1.7.0

from torch.utils.data import Dataset, DataLoader, TensorDataset, DistributedSampler
from torch.cuda.amp import autocast, GradScaler
from torch.nn.utils import clip_grad_norm_
from torch.nn.parallel import DistributedDataParallel as DDP
import torch.distributed as dist
from sklearn.model_selection import ShuffleSplit, cross_val_score  # 1.2.2
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import log_loss, make_scorer, mean_tweedie_deviance

# 常量与工具模块
# =============================================================================
torch.backends.cudnn.benchmark = True
EPS = 1e-8


class IOUtils:
    # 文件与路径处理的小工具集合。

    @staticmethod
    def csv_to_dict(file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return [
                dict(filter(lambda item: item[0] != '', row.items()))
                for row in reader
            ]

    @staticmethod
    def ensure_parent_dir(file_path: str) -> None:
        # 若目标文件所在目录不存在则自动创建
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)


class TrainingUtils:
    # 训练阶段常用的小型辅助函数集合。

    @staticmethod
    def compute_batch_size(data_size: int, learning_rate: float, batch_num: int, minimum: int) -> int:
        estimated = int((learning_rate / 1e-4) ** 0.5 *
                        (data_size / max(batch_num, 1)))
        return max(1, min(data_size, max(minimum, estimated)))

    @staticmethod
    def tweedie_loss(pred, target, p=1.5, eps=1e-6, max_clip=1e6):
        # 为确保稳定性先将预测值裁剪为正数
        pred_clamped = torch.clamp(pred, min=eps)
        if p == 1:
            term1 = target * torch.log(target / pred_clamped + eps)  # 泊松
            term2 = -target + pred_clamped
            term3 = 0
        elif p == 0:
            term1 = 0.5 * torch.pow(target - pred_clamped, 2)  # 高斯
            term2 = 0
            term3 = 0
        elif p == 2:
            term1 = torch.log(pred_clamped / target + eps)  # 伽马
            term2 = -target / pred_clamped + 1
            term3 = 0
        else:
            term1 = torch.pow(target, 2 - p) / ((1 - p) * (2 - p))
            term2 = target * torch.pow(pred_clamped, 1 - p) / (1 - p)
            term3 = torch.pow(pred_clamped, 2 - p) / (2 - p)
        return torch.nan_to_num(  # Tweedie 负对数似然（忽略常数项）
            2 * (term1 - term2 + term3),
            nan=eps,
            posinf=max_clip,
            neginf=-max_clip
        )

    @staticmethod
    def free_cuda() -> None:
        print(">>> Moving all models to CPU...")
        for obj in gc.get_objects():
            try:
                if hasattr(obj, "to") and callable(obj.to):
                    obj.to("cpu")
            except Exception:
                pass

        print(">>> Deleting tensors, optimizers, dataloaders...")
        gc.collect()

        print(">>> Emptying CUDA cache...")
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

        print(">>> CUDA memory freed.")


class DistributedUtils:
    @staticmethod
    def setup_ddp():
        """Initialize DDP process group."""
        if 'RANK' in os.environ and 'WORLD_SIZE' in os.environ:
            rank = int(os.environ["RANK"])
            world_size = int(os.environ["WORLD_SIZE"])
            local_rank = int(os.environ["LOCAL_RANK"])

            if torch.cuda.is_available():
                torch.cuda.set_device(local_rank)

            dist.init_process_group(backend="nccl", init_method="env://")
            print(
                f">>> DDP Initialized: Rank {rank}/{world_size}, Local Rank {local_rank}")
            return True, local_rank, rank, world_size
        else:
            print(
                f">>> DDP Setup Failed: RANK or WORLD_SIZE not found in env. Keys found: {list(os.environ.keys())}")
        return False, 0, 0, 1

    @staticmethod
    def cleanup_ddp():
        """Destroy DDP process group."""
        if dist.is_initialized():
            dist.destroy_process_group()

    @staticmethod
    def is_main_process():
        return not dist.is_initialized() or dist.get_rank() == 0


class PlotUtils:
    # 多种模型共享的绘图辅助工具。

    @staticmethod
    def split_data(data: pd.DataFrame, col_nme: str, wgt_nme: str, n_bins: int = 10) -> pd.DataFrame:
        data_sorted = data.sort_values(by=col_nme, ascending=True).copy()
        data_sorted['cum_weight'] = data_sorted[wgt_nme].cumsum()
        w_sum = data_sorted[wgt_nme].sum()
        if w_sum <= EPS:
            data_sorted.loc[:, 'bins'] = 0
        else:
            data_sorted.loc[:, 'bins'] = np.floor(
                data_sorted['cum_weight'] * float(n_bins) / w_sum
            )
            data_sorted.loc[(data_sorted['bins'] == n_bins),
                            'bins'] = n_bins - 1
        return data_sorted.groupby(['bins'], observed=True).sum(numeric_only=True)

    @staticmethod
    def plot_lift_ax(ax, plot_data, title, pred_label='Predicted', act_label='Actual', weight_label='Earned Exposure'):
        ax.plot(plot_data.index, plot_data['act_v'],
                label=act_label, color='red')
        ax.plot(plot_data.index, plot_data['exp_v'],
                label=pred_label, color='blue')
        ax.set_title(title, fontsize=8)
        ax.set_xticks(plot_data.index)
        ax.set_xticklabels(plot_data.index, rotation=90, fontsize=6)
        ax.tick_params(axis='y', labelsize=6)
        ax.legend(loc='upper left', fontsize=5, frameon=False)
        ax.margins(0.05)
        ax2 = ax.twinx()
        ax2.bar(plot_data.index, plot_data['weight'],
                alpha=0.5, color='seagreen',
                label=weight_label)
        ax2.tick_params(axis='y', labelsize=6)
        ax2.legend(loc='upper right', fontsize=5, frameon=False)

    @staticmethod
    def plot_dlift_ax(ax, plot_data, title, label1, label2, act_label='Actual', weight_label='Earned Exposure'):
        ax.plot(plot_data.index, plot_data['act_v'],
                label=act_label, color='red')
        ax.plot(plot_data.index, plot_data['exp_v1'],
                label=label1, color='blue')
        ax.plot(plot_data.index, plot_data['exp_v2'],
                label=label2, color='black')
        ax.set_title(title, fontsize=8)
        ax.set_xticks(plot_data.index)
        ax.set_xticklabels(plot_data.index, rotation=90, fontsize=6)
        ax.set_xlabel(f'{label1} / {label2}', fontsize=6)
        ax.tick_params(axis='y', labelsize=6)
        ax.legend(loc='upper left', fontsize=5, frameon=False)
        ax.margins(0.1)
        ax2 = ax.twinx()
        ax2.bar(plot_data.index, plot_data['weight'],
                alpha=0.5, color='seagreen',
                label=weight_label)
        ax2.tick_params(axis='y', labelsize=6)
        ax2.legend(loc='upper right', fontsize=5, frameon=False)

    @staticmethod
    def plot_lift_list(pred_model, w_pred_list, w_act_list,
                       weight_list, tgt_nme, n_bins: int = 10,
                       fig_nme: str = 'Lift Chart'):
        lift_data = pd.DataFrame()
        lift_data.loc[:, 'pred'] = pred_model
        lift_data.loc[:, 'w_pred'] = w_pred_list
        lift_data.loc[:, 'act'] = w_act_list
        lift_data.loc[:, 'weight'] = weight_list
        plot_data = PlotUtils.split_data(lift_data, 'pred', 'weight', n_bins)
        plot_data['exp_v'] = plot_data['w_pred'] / plot_data['weight']
        plot_data['act_v'] = plot_data['act'] / plot_data['weight']
        plot_data.reset_index(inplace=True)

        fig = plt.figure(figsize=(7, 5))
        ax = fig.add_subplot(111)
        PlotUtils.plot_lift_ax(ax, plot_data, f'Lift Chart of {tgt_nme}')
        plt.subplots_adjust(wspace=0.3)

        save_path = os.path.join(
            os.getcwd(), 'plot', f'05_{tgt_nme}_{fig_nme}.png')
        IOUtils.ensure_parent_dir(save_path)
        plt.savefig(save_path, dpi=300)
        plt.close(fig)

    @staticmethod
    def plot_dlift_list(pred_model_1, pred_model_2,
                        model_nme_1, model_nme_2,
                        tgt_nme,
                        w_list, w_act_list, n_bins: int = 10,
                        fig_nme: str = 'Double Lift Chart'):
        lift_data = pd.DataFrame()
        lift_data.loc[:, 'pred1'] = pred_model_1
        lift_data.loc[:, 'pred2'] = pred_model_2
        lift_data.loc[:, 'diff_ly'] = lift_data['pred1'] / lift_data['pred2']
        lift_data.loc[:, 'act'] = w_act_list
        lift_data.loc[:, 'weight'] = w_list
        lift_data.loc[:, 'w_pred1'] = lift_data['pred1'] * lift_data['weight']
        lift_data.loc[:, 'w_pred2'] = lift_data['pred2'] * lift_data['weight']
        plot_data = PlotUtils.split_data(
            lift_data, 'diff_ly', 'weight', n_bins)
        plot_data['exp_v1'] = plot_data['w_pred1'] / plot_data['act']
        plot_data['exp_v2'] = plot_data['w_pred2'] / plot_data['act']
        plot_data['act_v'] = plot_data['act']/plot_data['act']
        plot_data.reset_index(inplace=True)

        fig = plt.figure(figsize=(7, 5))
        ax = fig.add_subplot(111)
        PlotUtils.plot_dlift_ax(
            ax, plot_data, f'Double Lift Chart of {tgt_nme}', model_nme_1, model_nme_2)
        plt.subplots_adjust(bottom=0.25, top=0.95, right=0.8)

        save_path = os.path.join(
            os.getcwd(), 'plot', f'06_{tgt_nme}_{fig_nme}.png')
        IOUtils.ensure_parent_dir(save_path)
        plt.savefig(save_path, dpi=300)
        plt.close(fig)


# 向后兼容的函数式封装
def csv_to_dict(file_path: str) -> List[Dict[str, Any]]:
    return IOUtils.csv_to_dict(file_path)


def ensure_parent_dir(file_path: str) -> None:
    IOUtils.ensure_parent_dir(file_path)


def compute_batch_size(data_size: int, learning_rate: float, batch_num: int, minimum: int) -> int:
    return TrainingUtils.compute_batch_size(data_size, learning_rate, batch_num, minimum)


# 定义在 PyTorch 环境下的 Tweedie 偏差损失函数
# 参考文档：https://scikit-learn.org/stable/modules/model_evaluation.html#mean-poisson-gamma-and-tweedie-deviances
def tweedie_loss(pred, target, p=1.5, eps=1e-6, max_clip=1e6):
    return TrainingUtils.tweedie_loss(pred, target, p=p, eps=eps, max_clip=max_clip)


# 定义释放CUDA内存函数
def free_cuda():
    TrainingUtils.free_cuda()


class TorchTrainerMixin:
    # 面向 Torch 表格训练器的共享工具方法。

    def _device_type(self) -> str:
        return getattr(self, "device", torch.device("cpu")).type

    def _build_dataloader(self,
                          dataset,
                          N: int,
                          base_bs_gpu: tuple,
                          base_bs_cpu: tuple,
                          min_bs: int = 64,
                          target_effective_cuda: int = 8192,
                          target_effective_cpu: int = 4096,
                          large_threshold: int = 200_000,
                          mid_threshold: int = 50_000):
        batch_size = TrainingUtils.compute_batch_size(
            data_size=len(dataset),
            learning_rate=self.learning_rate,
            batch_num=self.batch_num,
            minimum=min_bs
        )
        gpu_large, gpu_mid, gpu_small = base_bs_gpu
        cpu_mid, cpu_small = base_bs_cpu

        if self._device_type() == 'cuda':
            device_count = torch.cuda.device_count()
            # 多卡环境下，适当增大最小批量，确保每张卡都能分到足够数据
            if device_count > 1:
                min_bs = min_bs * device_count
                print(
                    f">>> Multi-GPU detected: {device_count} devices. Adjusted min_bs to {min_bs}.")

            if N > large_threshold:
                base_bs = gpu_large * device_count
            elif N > mid_threshold:
                base_bs = gpu_mid * device_count
            else:
                base_bs = gpu_small * device_count
        else:
            base_bs = cpu_mid if N > mid_threshold else cpu_small

        # 重新计算 batch_size，确保不小于调整后的 min_bs
        batch_size = TrainingUtils.compute_batch_size(
            data_size=len(dataset),
            learning_rate=self.learning_rate,
            batch_num=self.batch_num,
            minimum=min_bs
        )
        batch_size = min(batch_size, base_bs, N)

        target_effective_bs = target_effective_cuda if self._device_type(
        ) == 'cuda' else target_effective_cpu
        accum_steps = max(1, target_effective_bs // batch_size)

        print(
            f">>> DataLoader config: Batch Size={batch_size}, Accum Steps={accum_steps}, Workers={min(8, os.cpu_count() or 1)}")

        # Linux (posix) 采用 fork 更高效；Windows (nt) 使用 spawn，开销更大。
        if os.name == 'nt':
            workers = 0
        else:
            workers = min(8, os.cpu_count() or 1)

        sampler = None
        if dist.is_initialized():
            sampler = DistributedSampler(dataset, shuffle=True)
            shuffle = False  # Sampler handles shuffling
        else:
            shuffle = True

        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            sampler=sampler,
            num_workers=workers,
            pin_memory=(self._device_type() == 'cuda'),
            persistent_workers=workers > 0,
        )
        return dataloader, accum_steps

    def _compute_weighted_loss(self, y_pred, y_true, weights, apply_softplus: bool = False):
        task = getattr(self, "task_type", "regression")
        if task == 'classification':
            loss_fn = nn.BCEWithLogitsLoss(reduction='none')
            losses = loss_fn(y_pred, y_true).view(-1)
        else:
            if apply_softplus:
                y_pred = F.softplus(y_pred)
            y_pred = torch.clamp(y_pred, min=1e-6)
            power = getattr(self, "tw_power", 1.5)
            losses = tweedie_loss(y_pred, y_true, p=power).view(-1)
        weighted_loss = (losses * weights.view(-1)).sum() / \
            torch.clamp(weights.sum(), min=EPS)
        return weighted_loss

    def _early_stop_update(self, val_loss, best_loss, best_state, patience_counter, model):
        if val_loss < best_loss:
            return val_loss, copy.deepcopy(model.state_dict()), 0, False
        patience_counter += 1
        should_stop = best_state is not None and patience_counter >= getattr(
            self, "patience", 0)
        return best_loss, best_state, patience_counter, should_stop

    def _train_model(self,
                     model,
                     dataloader,
                     accum_steps,
                     optimizer,
                     scaler,
                     forward_fn,
                     val_forward_fn=None,
                     apply_softplus: bool = False,
                     clip_fn=None,
                     trial: Optional[optuna.trial.Trial] = None):
        device_type = self._device_type()
        best_loss = float('inf')
        best_state = None
        patience_counter = 0
        stop_training = False

        for epoch in range(1, getattr(self, "epochs", 1) + 1):
            if hasattr(self, 'dataloader_sampler') and self.dataloader_sampler is not None:
                self.dataloader_sampler.set_epoch(epoch)

            model.train()
            optimizer.zero_grad()

            for step, batch in enumerate(dataloader):
                with autocast(enabled=(device_type == 'cuda')):
                    y_pred, y_true, w = forward_fn(batch)
                    weighted_loss = self._compute_weighted_loss(
                        y_pred, y_true, w, apply_softplus=apply_softplus)
                    loss_for_backward = weighted_loss / accum_steps

                scaler.scale(loss_for_backward).backward()

                if ((step + 1) % accum_steps == 0) or ((step + 1) == len(dataloader)):
                    if clip_fn is not None:
                        clip_fn()
                    scaler.step(optimizer)
                    scaler.update()
                    optimizer.zero_grad()

            if val_forward_fn is not None:
                model.eval()
                with torch.no_grad(), autocast(enabled=(device_type == 'cuda')):
                    val_result = val_forward_fn()
                    if isinstance(val_result, tuple) and len(val_result) == 3:
                        y_val_pred, y_val_true, w_val = val_result
                        val_weighted_loss = self._compute_weighted_loss(
                            y_val_pred, y_val_true, w_val, apply_softplus=apply_softplus)
                    else:
                        val_weighted_loss = val_result

                best_loss, best_state, patience_counter, stop_training = self._early_stop_update(
                    val_weighted_loss, best_loss, best_state, patience_counter, model)

                # Optuna 剪枝：若评估值劣于历史表现则提前中止该 trial
                if trial is not None:
                    trial.report(val_weighted_loss, epoch)
                    if trial.should_prune():
                        raise optuna.TrialPruned()

                if stop_training:
                    break

        return best_state


# =============================================================================
# 绘图辅助模块
# =============================================================================

def split_data(data, col_nme, wgt_nme, n_bins=10):
    return PlotUtils.split_data(data, col_nme, wgt_nme, n_bins)

# 定义提纯曲线（Lift）绘制函数


def plot_lift_list(pred_model, w_pred_list, w_act_list,
                   weight_list, tgt_nme, n_bins=10,
                   fig_nme='Lift Chart'):
    return PlotUtils.plot_lift_list(pred_model, w_pred_list, w_act_list,
                                    weight_list, tgt_nme, n_bins, fig_nme)

# 定义双提纯曲线绘制函数


def plot_dlift_list(pred_model_1, pred_model_2,
                    model_nme_1, model_nme_2,
                    tgt_nme,
                    w_list, w_act_list, n_bins=10,
                    fig_nme='Double Lift Chart'):
    return PlotUtils.plot_dlift_list(pred_model_1, pred_model_2,
                                     model_nme_1, model_nme_2,
                                     tgt_nme, w_list, w_act_list,
                                     n_bins, fig_nme)


# =============================================================================
# ResNet 模型与 sklearn 风格封装
# =============================================================================

# 开始定义ResNet模型结构
# 残差块：两层线性 + ReLU + 残差连接
# ResBlock 继承 nn.Module
class ResBlock(nn.Module):
    def __init__(self, dim: int, dropout: float = 0.1,
                 use_layernorm: bool = False, residual_scale: float = 0.1
                 ):
        super().__init__()
        self.use_layernorm = use_layernorm

        if use_layernorm:
            Norm = nn.LayerNorm      # 对最后一维做归一化
        else:
            def Norm(d): return nn.BatchNorm1d(d)  # 保留一个开关,想试 BN 时也能用

        self.norm1 = Norm(dim)
        self.fc1 = nn.Linear(dim, dim, bias=True)
        self.act = nn.ReLU(inplace=True)
        self.dropout = nn.Dropout(dropout) if dropout > 0.0 else nn.Identity()
        self.norm2 = Norm(dim)
        self.fc2 = nn.Linear(dim, dim, bias=True)

        # 残差缩放,防止一开始就把主干搞炸
        self.res_scale = nn.Parameter(
            torch.tensor(residual_scale, dtype=torch.float32)
        )

    def forward(self, x):
        # 前置激活结构
        out = self.norm1(x)
        out = self.fc1(out)
        out = self.act(out)
        out = self.dropout(out)
        out = self.norm2(out)
        out = self.fc2(out)
        # 残差缩放再相加
        return F.relu(x + self.res_scale * out)

# ResNetSequential 继承 nn.Module,定义整个网络结构


class ResNetSequential(nn.Module):
    # 输入张量形状：(batch, input_dim)
    # 网络结构：全连接 + 归一化 + ReLU，再堆叠若干残差块，最后输出 Softplus

    def __init__(self, input_dim: int, hidden_dim: int = 64, block_num: int = 2,
                 use_layernorm: bool = True, dropout: float = 0.1,
                 residual_scale: float = 0.1, task_type: str = 'regression'):
        super(ResNetSequential, self).__init__()

        self.net = nn.Sequential()
        self.net.add_module('fc1', nn.Linear(input_dim, hidden_dim))

        if use_layernorm:
            self.net.add_module('norm1', nn.LayerNorm(hidden_dim))
        else:
            self.net.add_module('norm1', nn.BatchNorm1d(hidden_dim))

        self.net.add_module('relu1', nn.ReLU(inplace=True))

        # 多个残差块
        for i in range(block_num):
            self.net.add_module(
                f'ResBlk_{i+1}',
                ResBlock(
                    hidden_dim,
                    dropout=dropout,
                    use_layernorm=use_layernorm,
                    residual_scale=residual_scale)
            )

        self.net.add_module('fc_out', nn.Linear(hidden_dim, 1))

        if task_type == 'classification':
            self.net.add_module('softplus', nn.Identity())
        else:
            self.net.add_module('softplus', nn.Softplus())

    def forward(self, x):
        if self.training and not hasattr(self, '_printed_device'):
            print(f">>> ResNetSequential executing on device: {x.device}")
            self._printed_device = True
        return self.net(x)

# 定义ResNet模型的Scikit-Learn接口类


class ResNetSklearn(TorchTrainerMixin, nn.Module):
    def __init__(self, model_nme: str, input_dim: int, hidden_dim: int = 64,
                 block_num: int = 2, batch_num: int = 100, epochs: int = 100,
                 task_type: str = 'regression',
                 tweedie_power: float = 1.5, learning_rate: float = 0.01, patience: int = 10,
                 use_layernorm: bool = True, dropout: float = 0.1,
                 residual_scale: float = 0.1,
                 use_data_parallel: bool = True,
                 use_ddp: bool = False):
        super(ResNetSklearn, self).__init__()

        self.use_ddp = use_ddp
        self.is_ddp_enabled, self.local_rank, self.rank, self.world_size = (
            False, 0, 0, 1)

        if self.use_ddp:
            self.is_ddp_enabled, self.local_rank, self.rank, self.world_size = DistributedUtils.setup_ddp()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.block_num = block_num
        self.batch_num = batch_num
        self.epochs = epochs
        self.task_type = task_type
        self.model_nme = model_nme
        self.learning_rate = learning_rate
        self.patience = patience
        self.use_layernorm = use_layernorm
        self.dropout = dropout
        self.residual_scale = residual_scale

        # 设备选择：cuda > mps > cpu
        if self.is_ddp_enabled:
            self.device = torch.device(f'cuda:{self.local_rank}')
        elif torch.cuda.is_available():
            self.device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            self.device = torch.device('mps')
        else:
            self.device = torch.device('cpu')

        # Tweedie 幂指数设定（分类时不使用）
        if self.task_type == 'classification':
            self.tw_power = None
        elif 'f' in self.model_nme:
            self.tw_power = 1
        elif 's' in self.model_nme:
            self.tw_power = 2
        else:
            self.tw_power = tweedie_power

        # 搭建网络（先在 CPU 上建好）
        core = ResNetSequential(
            self.input_dim,
            self.hidden_dim,
            self.block_num,
            use_layernorm=self.use_layernorm,
            dropout=self.dropout,
            residual_scale=self.residual_scale,
            task_type=self.task_type
        )

        # ===== 多卡支持：DataParallel vs DistributedDataParallel =====
        if self.is_ddp_enabled:
            core = core.to(self.device)
            core = DDP(core, device_ids=[
                       self.local_rank], output_device=self.local_rank)
        elif use_data_parallel and (self.device.type == 'cuda') and (torch.cuda.device_count() > 1):
            core = nn.DataParallel(core, device_ids=list(
                range(torch.cuda.device_count())))
            # DataParallel 会把输入 scatter 到多卡上，但“主设备”仍然是 cuda:0
            self.device = torch.device('cuda')

        self.resnet = core.to(self.device)

    # ================ 内部工具 ================
    def _build_train_val_tensors(self, X_train, y_train, w_train, X_val, y_val, w_val):
        X_tensor = torch.tensor(X_train.values, dtype=torch.float32)
        y_tensor = torch.tensor(
            y_train.values, dtype=torch.float32).view(-1, 1)
        w_tensor = torch.tensor(w_train.values, dtype=torch.float32).view(
            -1, 1) if w_train is not None else torch.ones_like(y_tensor)

        has_val = X_val is not None and y_val is not None
        if has_val:
            X_val_tensor = torch.tensor(X_val.values, dtype=torch.float32)
            y_val_tensor = torch.tensor(
                y_val.values, dtype=torch.float32).view(-1, 1)
            w_val_tensor = torch.tensor(w_val.values, dtype=torch.float32).view(
                -1, 1) if w_val is not None else torch.ones_like(y_val_tensor)
        else:
            X_val_tensor = y_val_tensor = w_val_tensor = None
        return X_tensor, y_tensor, w_tensor, X_val_tensor, y_val_tensor, w_val_tensor, has_val

    def forward(self, x):
        # 处理 SHAP 的 NumPy 输入
        if isinstance(x, np.ndarray):
            x_tensor = torch.tensor(x, dtype=torch.float32)
        else:
            x_tensor = x

        x_tensor = x_tensor.to(self.device)
        y_pred = self.resnet(x_tensor)
        return y_pred

    # ---------------- 训练 ----------------

    def fit(self, X_train, y_train, w_train=None,
            X_val=None, y_val=None, w_val=None, trial=None):

        X_tensor, y_tensor, w_tensor, X_val_tensor, y_val_tensor, w_val_tensor, has_val = \
            self._build_train_val_tensors(
                X_train, y_train, w_train, X_val, y_val, w_val)

        dataset = TensorDataset(X_tensor, y_tensor, w_tensor)
        dataloader, accum_steps = self._build_dataloader(
            dataset,
            N=X_tensor.shape[0],
            base_bs_gpu=(65536, 32768, 16384),
            base_bs_cpu=(1024, 512),
            min_bs=64,
            target_effective_cuda=8192,
            target_effective_cpu=4096
        )

        # 在每个 epoch 开始前设置 sampler 的 epoch，以保证 shuffle 的随机性
        if self.is_ddp_enabled and hasattr(dataloader.sampler, 'set_epoch'):
            self.dataloader_sampler = dataloader.sampler
        else:
            self.dataloader_sampler = None

        # === 4. 优化器与 AMP ===
        self.optimizer = torch.optim.Adam(
            self.resnet.parameters(), lr=self.learning_rate)
        self.scaler = GradScaler(enabled=(self.device.type == 'cuda'))

        X_val_dev = y_val_dev = w_val_dev = None
        val_dataloader = None
        if has_val:
            # 构建验证集 DataLoader
            val_dataset = TensorDataset(
                X_val_tensor, y_val_tensor, w_val_tensor)
            # 验证阶段无需反向传播，可适当放大批量以提高吞吐
            val_bs = accum_steps * dataloader.batch_size

            # 验证集的 worker 数沿用相同的分配逻辑
            if os.name == 'nt':
                val_workers = 0
            else:
                val_workers = min(4, os.cpu_count() or 1)

            val_dataloader = DataLoader(
                val_dataset,
                batch_size=val_bs,
                shuffle=False,
                num_workers=val_workers,
                pin_memory=(self.device.type == 'cuda'),
                persistent_workers=val_workers > 0,
            )
            # 验证集通常不需要 DDP Sampler，因为我们只在主进程验证或汇总验证结果
            # 但为了简单起见，这里保持单卡验证或主进程验证

        is_data_parallel = isinstance(self.resnet, nn.DataParallel)

        def forward_fn(batch):
            X_batch, y_batch, w_batch = batch

            if not is_data_parallel:
                X_batch = X_batch.to(self.device, non_blocking=True)
            # 目标值与权重始终与主设备保持一致，便于后续损失计算
            y_batch = y_batch.to(self.device, non_blocking=True)
            w_batch = w_batch.to(self.device, non_blocking=True)

            y_pred = self.resnet(X_batch)
            return y_pred, y_batch, w_batch

        def val_forward_fn():
            total_loss = 0.0
            total_weight = 0.0
            for batch in val_dataloader:
                X_b, y_b, w_b = batch
                if not is_data_parallel:
                    X_b = X_b.to(self.device, non_blocking=True)
                y_b = y_b.to(self.device, non_blocking=True)
                w_b = w_b.to(self.device, non_blocking=True)

                y_pred = self.resnet(X_b)

                # 手动计算当前批次的加权损失，以便后续精确加总
                task = getattr(self, "task_type", "regression")
                if task == 'classification':
                    loss_fn = nn.BCEWithLogitsLoss(reduction='none')
                    losses = loss_fn(y_pred, y_b).view(-1)
                else:
                    # 此处无需再做 softplus：训练时 apply_softplus=False，模型前向结果本身已为正
                    y_pred_clamped = torch.clamp(y_pred, min=1e-6)
                    power = getattr(self, "tw_power", 1.5)
                    losses = tweedie_loss(
                        y_pred_clamped, y_b, p=power).view(-1)

                batch_weight_sum = torch.clamp(w_b.sum(), min=EPS)
                batch_weighted_loss_sum = (losses * w_b.view(-1)).sum()

                total_loss += batch_weighted_loss_sum.item()
                total_weight += batch_weight_sum.item()

            return total_loss / max(total_weight, EPS)

        clip_fn = None
        if self.device.type == 'cuda':
            def clip_fn(): return (self.scaler.unscale_(self.optimizer),
                                   clip_grad_norm_(self.resnet.parameters(), max_norm=1.0))

        # DDP 模式下，只在主进程打印日志和保存模型
        if self.is_ddp_enabled and not DistributedUtils.is_main_process():
            # 非主进程不进行验证回调中的打印操作（需在 _train_model 内部控制，这里暂略）
            pass

        best_state = self._train_model(
            self.resnet,
            dataloader,
            accum_steps,
            self.optimizer,
            self.scaler,
            forward_fn,
            val_forward_fn if has_val else None,
            apply_softplus=False,
            clip_fn=clip_fn,
            trial=trial
        )

        if has_val and best_state is not None:
            self.resnet.load_state_dict(best_state)

    # ---------------- 预测 ----------------

    def predict(self, X_test):
        self.resnet.eval()
        if isinstance(X_test, pd.DataFrame):
            X_np = X_test.values.astype(np.float32)
        else:
            X_np = X_test

        with torch.no_grad():
            y_pred = self(X_np).cpu().numpy()

        if self.task_type == 'classification':
            y_pred = 1 / (1 + np.exp(-y_pred))  # Sigmoid 函数将 logit 转换为概率
        else:
            y_pred = np.clip(y_pred, 1e-6, None)
        return y_pred.flatten()

    # ---------------- 设置参数 ----------------

    def set_params(self, params):
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Parameter {key} not found in model.")
        return self


# =============================================================================
# FT-Transformer 模型与 sklearn 风格封装
# =============================================================================
# 开始定义FT Transformer模型结构


class FeatureTokenizer(nn.Module):
    # 将数值特征与类别特征统一映射为 token，输出形状为 (batch, token_num, d_model)
    # 约定：
    #   - X_num：表示数值特征，shape=(batch, num_numeric)
    #   - X_cat：表示类别特征，shape=(batch, num_categorical)，每列是编码后的整数标签 [0, card-1]

    def __init__(self, num_numeric: int, cat_cardinalities, d_model: int):
        super().__init__()

        self.num_numeric = num_numeric
        self.has_numeric = num_numeric > 0

        if self.has_numeric:
            self.num_linear = nn.Linear(num_numeric, d_model)

        self.embeddings = nn.ModuleList([
            nn.Embedding(card, d_model) for card in cat_cardinalities
        ])

    def forward(self, X_num, X_cat):
        tokens = []

        if self.has_numeric:
            # 数值特征整体映射为一个 token
            # shape = (batch, d_model)
            num_token = self.num_linear(X_num)
            tokens.append(num_token)

        # 每个类别特征各生成一个嵌入 token
        for i, emb in enumerate(self.embeddings):
            # shape = (batch, d_model)
            tok = emb(X_cat[:, i])
            tokens.append(tok)

        # 拼接后得到 (batch, token_num, d_model)
        x = torch.stack(tokens, dim=1)
        return x

# 定义具有残差缩放的Encoder层


class ScaledTransformerEncoderLayer(nn.Module):
    def __init__(self, d_model: int, nhead: int, dim_feedforward: int = 2048,
                 dropout: float = 0.1, residual_scale_attn: float = 1.0,
                 residual_scale_ffn: float = 1.0, norm_first: bool = True,
                 ):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=nhead,
            dropout=dropout,
            batch_first=True
        )

        # 前馈网络部分
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(dim_feedforward, d_model)

        # 归一化与 Dropout
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

        self.activation = nn.GELU()
        # self.activation = nn.ReLU()
        self.norm_first = norm_first

        # 残差缩放系数
        self.res_scale_attn = residual_scale_attn
        self.res_scale_ffn = residual_scale_ffn

    def forward(self, src, src_mask=None, src_key_padding_mask=None):
        # 输入张量形状：(batch, 序列长度, d_model)
        x = src

        if self.norm_first:
            # 先归一化再做注意力
            x = x + self._sa_block(self.norm1(x), src_mask,
                                   src_key_padding_mask)
            x = x + self._ff_block(self.norm2(x))
        else:
            # 后归一化（一般不启用）
            x = self.norm1(
                x + self._sa_block(x, src_mask, src_key_padding_mask))
            x = self.norm2(x + self._ff_block(x))

        return x

    def _sa_block(self, x, attn_mask, key_padding_mask):
        # 自注意力并附带残差缩放
        attn_out, _ = self.self_attn(
            x, x, x,
            attn_mask=attn_mask,
            key_padding_mask=key_padding_mask,
            need_weights=False
        )
        return self.res_scale_attn * self.dropout1(attn_out)

    def _ff_block(self, x):
        # 前馈网络并附带残差缩放
        x2 = self.linear2(self.dropout(self.activation(self.linear1(x))))
        return self.res_scale_ffn * self.dropout2(x2)

# 定义FT-Transformer核心模型


class FTTransformerCore(nn.Module):
    # 最小可用版本的 FT-Transformer，由三部分组成：
    #   1) FeatureTokenizer：将数值/类别特征转换成 token；
    #   2) TransformerEncoder：建模特征之间的交互；
    #   3) 池化 + MLP + Softplus：输出正值，方便 Tweedie/Gamma 等任务。

    def __init__(self, num_numeric: int, cat_cardinalities, d_model: int = 64,
                 n_heads: int = 8, n_layers: int = 4, dropout: float = 0.1,
                 task_type: str = 'regression'
                 ):
        super().__init__()

        self.tokenizer = FeatureTokenizer(
            num_numeric=num_numeric,
            cat_cardinalities=cat_cardinalities,
            d_model=d_model
        )
        scale = 1.0 / math.sqrt(n_layers)  # 推荐一个默认值
        encoder_layer = ScaledTransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            residual_scale_attn=scale,
            residual_scale_ffn=scale,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=n_layers
        )
        self.n_layers = n_layers

        layers = [
            nn.LayerNorm(d_model),
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.Linear(d_model, 1),
        ]

        if task_type == 'classification':
            # 分类任务输出 logits，与 BCEWithLogitsLoss 更匹配
            layers.append(nn.Identity())
        else:
            # 回归任务需保持正值，适配 Tweedie/Gamma
            layers.append(nn.Softplus())

        self.head = nn.Sequential(*layers)

    def forward(self, X_num, X_cat):

        # 输入：
        #   X_num -> (batch, 数值特征数) 的 float32 张量
        #   X_cat -> (batch, 类别特征数) 的 long 张量

        if self.training and not hasattr(self, '_printed_device'):
            print(f">>> FTTransformerCore executing on device: {X_num.device}")
            self._printed_device = True

        tokens = self.tokenizer(X_num, X_cat)  # => (batch, token_num, d_model)
        x = self.encoder(tokens)               # => (batch, token_num, d_model)

        # 对 token 做平均池化，再送入回归头
        x = x.mean(dim=1)                      # => (batch, d_model)

        out = self.head(x)                     # => (batch, 1)，Softplus 约束为正
        return out

# 定义TabularDataset类


class TabularDataset(Dataset):
    def __init__(self, X_num, X_cat, y, w):

        # 输入张量说明：
        #   X_num: torch.float32，shape=(N, 数值特征数)
        #   X_cat: torch.long，  shape=(N, 类别特征数)
        #   y:     torch.float32，shape=(N, 1)
        #   w:     torch.float32，shape=(N, 1)

        self.X_num = X_num
        self.X_cat = X_cat
        self.y = y
        self.w = w

    def __len__(self):
        return self.y.shape[0]

    def __getitem__(self, idx):
        return (
            self.X_num[idx],
            self.X_cat[idx],
            self.y[idx],
            self.w[idx],
        )

# 定义FTTransformer的Scikit-Learn接口类


class FTTransformerSklearn(TorchTrainerMixin, nn.Module):

    # sklearn 风格包装：
    #   - num_cols：数值特征列名列表
    #   - cat_cols：类别特征列名列表（需事先做标签编码，取值 ∈ [0, n_classes-1]）

    def __init__(self, model_nme: str, num_cols, cat_cols, d_model: int = 64, n_heads: int = 8,
                 n_layers: int = 4, dropout: float = 0.1, batch_num: int = 100, epochs: int = 100,
                 task_type: str = 'regression',
                 tweedie_power: float = 1.5, learning_rate: float = 1e-3, patience: int = 10,
                 use_data_parallel: bool = True,
                 use_ddp: bool = False
                 ):
        super().__init__()

        self.use_ddp = use_ddp
        self.is_ddp_enabled, self.local_rank, self.rank, self.world_size = (
            False, 0, 0, 1)
        if self.use_ddp:
            self.is_ddp_enabled, self.local_rank, self.rank, self.world_size = DistributedUtils.setup_ddp()

        self.model_nme = model_nme
        self.num_cols = list(num_cols)
        self.cat_cols = list(cat_cols)
        self.d_model = d_model
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.dropout = dropout
        self.batch_num = batch_num
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.task_type = task_type
        self.patience = patience
        if self.task_type == 'classification':
            self.tw_power = None  # 分类时不使用 Tweedie 幂
        elif 'f' in self.model_nme:
            self.tw_power = 1.0
        elif 's' in self.model_nme:
            self.tw_power = 2.0
        else:
            self.tw_power = tweedie_power

        if self.is_ddp_enabled:
            self.device = torch.device(f"cuda:{self.local_rank}")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")
        self.cat_cardinalities = None
        self.cat_categories = {}
        self.ft = None
        self.use_data_parallel = torch.cuda.device_count() > 1 and use_data_parallel

    def _build_model(self, X_train):
        num_numeric = len(self.num_cols)
        cat_cardinalities = []

        for col in self.cat_cols:
            cats = X_train[col].astype('category')
            categories = cats.cat.categories
            self.cat_categories[col] = categories           # 保存训练集类别全集

            card = len(categories) + 1                      # 多预留 1 类给“未知/缺失”
            cat_cardinalities.append(card)

        self.cat_cardinalities = cat_cardinalities

        core = FTTransformerCore(
            num_numeric=num_numeric,
            cat_cardinalities=cat_cardinalities,
            d_model=self.d_model,
            n_heads=self.n_heads,
            n_layers=self.n_layers,
            dropout=self.dropout,
            task_type=self.task_type
        )
        if self.is_ddp_enabled:
            core = core.to(self.device)
            core = DDP(core, device_ids=[
                       self.local_rank], output_device=self.local_rank)
        elif self.use_data_parallel:
            core = nn.DataParallel(core, device_ids=list(
                range(torch.cuda.device_count())))
            self.device = torch.device("cuda")
        self.ft = core.to(self.device)

    def _encode_cats(self, X):
        # 输入 DataFrame 至少需要包含所有类别特征列
        # 返回形状 (N, 类别特征数) 的 int64 数组

        if not self.cat_cols:
            return np.zeros((len(X), 0), dtype='int64')

        X_cat_list = []
        for col in self.cat_cols:
            # 使用训练阶段记录的类别全集
            categories = self.cat_categories[col]
            # 按固定类别构造 Categorical
            cats = pd.Categorical(X[col], categories=categories)
            codes = cats.codes.astype('int64', copy=True)   # -1 表示未知或缺失
            # 未知或缺失映射到额外的“未知”索引 len(categories)
            codes[codes < 0] = len(categories)
            X_cat_list.append(codes)

        X_cat_np = np.stack(X_cat_list, axis=1)  # 形状 (N, 类别特征数)
        return X_cat_np

    def _build_train_tensors(self, X_train, y_train, w_train):
        return self._tensorize_split(X_train, y_train, w_train)

    def _build_val_tensors(self, X_val, y_val, w_val):
        return self._tensorize_split(X_val, y_val, w_val, allow_none=True)

    def _tensorize_split(self, X, y, w, allow_none: bool = False):
        if X is None:
            if allow_none:
                return None, None, None, None, False
            raise ValueError("输入特征 X 不能为空。")

        X_num = torch.tensor(
            X[self.num_cols].to_numpy(dtype=np.float32, copy=True),
            dtype=torch.float32
        )
        if self.cat_cols:
            X_cat = torch.tensor(self._encode_cats(X), dtype=torch.long)
        else:
            X_cat = torch.zeros((X_num.shape[0], 0), dtype=torch.long)

        y_tensor = torch.tensor(
            y.values, dtype=torch.float32).view(-1, 1) if y is not None else None
        if y_tensor is None:
            w_tensor = None
        elif w is not None:
            w_tensor = torch.tensor(
                w.values, dtype=torch.float32).view(-1, 1)
        else:
            w_tensor = torch.ones_like(y_tensor)
        return X_num, X_cat, y_tensor, w_tensor, y is not None

    def fit(self, X_train, y_train, w_train=None,
            X_val=None, y_val=None, w_val=None, trial=None):

        # 首次拟合时需要构建底层模型结构
        if self.ft is None:
            self._build_model(X_train)

        X_num_train, X_cat_train, y_tensor, w_tensor, _ = self._build_train_tensors(
            X_train, y_train, w_train)
        X_num_val, X_cat_val, y_val_tensor, w_val_tensor, has_val = self._build_val_tensors(
            X_val, y_val, w_val)

        # --- 构建 DataLoader ---
        dataset = TabularDataset(
            X_num_train, X_cat_train, y_tensor, w_tensor
        )

        dataloader, accum_steps = self._build_dataloader(
            dataset,
            N=X_num_train.shape[0],
            base_bs_gpu=(65536, 32768, 16384),
            base_bs_cpu=(256, 128),
            min_bs=64,
            target_effective_cuda=4096,
            target_effective_cpu=2048
        )

        if self.is_ddp_enabled and hasattr(dataloader.sampler, 'set_epoch'):
            self.dataloader_sampler = dataloader.sampler
        else:
            self.dataloader_sampler = None

        optimizer = torch.optim.Adam(
            self.ft.parameters(), lr=self.learning_rate)
        scaler = GradScaler(enabled=(self.device.type == 'cuda'))

        X_num_val_dev = X_cat_val_dev = y_val_dev = w_val_dev = None
        val_dataloader = None
        if has_val:
            val_dataset = TabularDataset(
                X_num_val, X_cat_val, y_val_tensor, w_val_tensor
            )
            val_bs = accum_steps * dataloader.batch_size

            if os.name == 'nt':
                val_workers = 0
            else:
                val_workers = min(4, os.cpu_count() or 1)

            val_dataloader = DataLoader(
                val_dataset,
                batch_size=val_bs,
                shuffle=False,
                num_workers=val_workers,
                pin_memory=(self.device.type == 'cuda'),
                persistent_workers=val_workers > 0,
            )

        is_data_parallel = isinstance(self.ft, nn.DataParallel)

        def forward_fn(batch):
            X_num_b, X_cat_b, y_b, w_b = batch

            if not is_data_parallel:
                X_num_b = X_num_b.to(self.device, non_blocking=True)
                X_cat_b = X_cat_b.to(self.device, non_blocking=True)
            y_b = y_b.to(self.device, non_blocking=True)
            w_b = w_b.to(self.device, non_blocking=True)

            y_pred = self.ft(X_num_b, X_cat_b)
            return y_pred, y_b, w_b

        def val_forward_fn():
            total_loss = 0.0
            total_weight = 0.0
            for batch in val_dataloader:
                X_num_b, X_cat_b, y_b, w_b = batch
                if not is_data_parallel:
                    X_num_b = X_num_b.to(self.device, non_blocking=True)
                    X_cat_b = X_cat_b.to(self.device, non_blocking=True)
                y_b = y_b.to(self.device, non_blocking=True)
                w_b = w_b.to(self.device, non_blocking=True)

                y_pred = self.ft(X_num_b, X_cat_b)

                # 手动计算验证损失
                task = getattr(self, "task_type", "regression")
                if task == 'classification':
                    loss_fn = nn.BCEWithLogitsLoss(reduction='none')
                    losses = loss_fn(y_pred, y_b).view(-1)
                else:
                    # 模型输出已通过 Softplus，无需再次应用
                    y_pred_clamped = torch.clamp(y_pred, min=1e-6)
                    power = getattr(self, "tw_power", 1.5)
                    losses = tweedie_loss(
                        y_pred_clamped, y_b, p=power).view(-1)

                batch_weight_sum = torch.clamp(w_b.sum(), min=EPS)
                batch_weighted_loss_sum = (losses * w_b.view(-1)).sum()

                total_loss += batch_weighted_loss_sum.item()
                total_weight += batch_weight_sum.item()

            return total_loss / max(total_weight, EPS)

        clip_fn = None
        if self.device.type == 'cuda':
            def clip_fn(): return (scaler.unscale_(optimizer),
                                   clip_grad_norm_(self.ft.parameters(), max_norm=1.0))

        best_state = self._train_model(
            self.ft,
            dataloader,
            accum_steps,
            optimizer,
            scaler,
            forward_fn,
            val_forward_fn if has_val else None,
            apply_softplus=False,
            clip_fn=clip_fn,
            trial=trial
        )

        if has_val and best_state is not None:
            self.ft.load_state_dict(best_state)

    def predict(self, X_test):
        # X_test 需要包含所有数值列与类别列

        self.ft.eval()
        X_num, X_cat, _, _, _ = self._tensorize_split(
            X_test, None, None, allow_none=True)

        with torch.no_grad():
            X_num = X_num.to(self.device, non_blocking=True)
            X_cat = X_cat.to(self.device, non_blocking=True)
            y_pred = self.ft(X_num, X_cat).cpu().numpy()

        if self.task_type == 'classification':
            # 从 logits 转换为概率
            y_pred = 1 / (1 + np.exp(-y_pred))
        else:
            # 模型已含 softplus，若需要可按需做 log-exp 平滑：y_pred = log(1 + exp(y_pred))
            y_pred = np.clip(y_pred, 1e-6, None)
        return y_pred.ravel()

    def set_params(self, params: dict):

        # 和 sklearn 风格保持一致。
        # 注意：对结构性参数（如 d_model/n_heads）修改后,需要重新 fit 才会生效。

        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Parameter {key} not found in model.")
        return self


# ===== 基础组件与训练封装 =====================================================

# =============================================================================
# 配置、预处理与训练器基类
# =============================================================================
@dataclass
class BayesOptConfig:
    model_nme: str
    resp_nme: str
    weight_nme: str
    factor_nmes: List[str]
    task_type: str = 'regression'
    binary_resp_nme: Optional[str] = None
    cate_list: Optional[List[str]] = None
    prop_test: float = 0.25
    rand_seed: Optional[int] = None
    epochs: int = 100
    use_gpu: bool = True
    use_resn_data_parallel: bool = True
    use_ft_data_parallel: bool = True
    use_resn_ddp: bool = False
    use_ft_ddp: bool = False


class OutputManager:
    # 统一管理结果、图表与模型的输出路径

    def __init__(self, root: Optional[str] = None, model_name: str = "model") -> None:
        self.root = Path(root or os.getcwd())
        self.model_name = model_name
        self.plot_dir = self.root / 'plot'
        self.result_dir = self.root / 'Results'
        self.model_dir = self.root / 'model'

    def _prepare(self, path: Path) -> str:
        ensure_parent_dir(str(path))
        return str(path)

    def plot_path(self, filename: str) -> str:
        return self._prepare(self.plot_dir / filename)

    def result_path(self, filename: str) -> str:
        return self._prepare(self.result_dir / filename)

    def model_path(self, filename: str) -> str:
        return self._prepare(self.model_dir / filename)


class DatasetPreprocessor:
    # 为各训练器准备通用的训练/测试数据视图

    def __init__(self, train_df: pd.DataFrame, test_df: pd.DataFrame,
                 config: BayesOptConfig) -> None:
        self.config = config
        self.train_data = train_df.copy(deep=True)
        self.test_data = test_df.copy(deep=True)
        self.num_features: List[str] = []
        self.train_oht_scl_data: Optional[pd.DataFrame] = None
        self.test_oht_scl_data: Optional[pd.DataFrame] = None
        self.var_nmes: List[str] = []
        self.cat_categories_for_shap: Dict[str, List[Any]] = {}

    def run(self) -> "DatasetPreprocessor":
        cfg = self.config
        # 预先计算加权实际值，后续画图、校验都依赖该字段
        self.train_data.loc[:, 'w_act'] = self.train_data[cfg.resp_nme] * \
            self.train_data[cfg.weight_nme]
        self.test_data.loc[:, 'w_act'] = self.test_data[cfg.resp_nme] * \
            self.test_data[cfg.weight_nme]
        if cfg.binary_resp_nme:
            self.train_data.loc[:, 'w_binary_act'] = self.train_data[cfg.binary_resp_nme] * \
                self.train_data[cfg.weight_nme]
            self.test_data.loc[:, 'w_binary_act'] = self.test_data[cfg.binary_resp_nme] * \
                self.test_data[cfg.weight_nme]
        # 高分位裁剪用来吸收离群值；若删除会导致极端点主导损失
        q99 = self.train_data[cfg.resp_nme].quantile(0.999)
        self.train_data[cfg.resp_nme] = self.train_data[cfg.resp_nme].clip(
            upper=q99)
        cate_list = list(cfg.cate_list or [])
        if cate_list:
            for cate in cate_list:
                self.train_data[cate] = self.train_data[cate].astype(
                    'category')
                self.test_data[cate] = self.test_data[cate].astype('category')
                cats = self.train_data[cate].cat.categories
                self.cat_categories_for_shap[cate] = list(cats)
        self.num_features = [
            nme for nme in cfg.factor_nmes if nme not in cate_list]
        train_oht = self.train_data[cfg.factor_nmes +
                                    [cfg.weight_nme] + [cfg.resp_nme]].copy()
        test_oht = self.test_data[cfg.factor_nmes +
                                  [cfg.weight_nme] + [cfg.resp_nme]].copy()
        train_oht = pd.get_dummies(
            train_oht,
            columns=cate_list,
            drop_first=True,
            dtype=np.int8
        )
        test_oht = pd.get_dummies(
            test_oht,
            columns=cate_list,
            drop_first=True,
            dtype=np.int8
        )
        for num_chr in self.num_features:
            # 逐列标准化保障每个特征在同一量级，否则神经网络会难以收敛
            scaler = StandardScaler()
            train_oht[num_chr] = scaler.fit_transform(
                train_oht[num_chr].values.reshape(-1, 1))
            test_oht[num_chr] = scaler.transform(
                test_oht[num_chr].values.reshape(-1, 1))
        # reindex 时将缺失的哑变量列补零，避免测试集列数与训练集不一致
        test_oht = test_oht.reindex(columns=train_oht.columns, fill_value=0)
        self.train_oht_scl_data = train_oht
        self.test_oht_scl_data = test_oht
        self.var_nmes = list(
            set(list(train_oht.columns)) - set([cfg.weight_nme, cfg.resp_nme])
        )
        return self

# =============================================================================
# 训练器体系
# =============================================================================


class TrainerBase:
    def __init__(self, context: "BayesOptModel", label: str, model_name_prefix: str) -> None:
        self.ctx = context
        self.label = label
        self.model_name_prefix = model_name_prefix
        self.model = None
        self.best_params: Optional[Dict[str, Any]] = None
        self.best_trial = None

    @property
    def config(self) -> BayesOptConfig:
        return self.ctx.config

    @property
    def output(self) -> OutputManager:
        return self.ctx.output_manager

    def _get_model_filename(self) -> str:
        ext = 'pkl' if self.label in ['Xgboost', 'GLM'] else 'pth'
        return f'01_{self.ctx.model_nme}_{self.model_name_prefix}.{ext}'

    def tune(self, max_evals: int, objective_fn=None) -> None:
        # 通用的 Optuna 调参循环流程。
        if objective_fn is None:
            # 若子类未显式提供 objective_fn，则默认使用 cross_val 作为优化目标
            objective_fn = self.cross_val

        def objective_wrapper(trial: optuna.trial.Trial) -> float:
            try:
                result = objective_fn(trial)
            finally:
                self._clean_gpu()
            return result

        study = optuna.create_study(
            direction='minimize',
            sampler=optuna.samplers.TPESampler(seed=self.ctx.rand_seed)
        )
        study.optimize(objective_wrapper, n_trials=max_evals)
        self.best_params = study.best_params
        self.best_trial = study.best_trial

        # 将最优参数保存为 CSV，方便复现
        params_path = self.output.result_path(
            f'{self.ctx.model_nme}_bestparams_{self.label.lower()}.csv'
        )
        pd.DataFrame(self.best_params, index=[0]).to_csv(params_path)

    def train(self) -> None:
        raise NotImplementedError

    def save(self) -> None:
        if self.model is None:
            print(f"[save] Warning: No model to save for {self.label}")
            return

        path = self.output.model_path(self._get_model_filename())
        if self.label in ['Xgboost', 'GLM']:
            joblib.dump(self.model, path)
        else:
            # Torch 模型既可以只存 state_dict，也可以整个对象一起序列化
            # 兼容历史行为：ResNetTrainer 保存 state_dict，FTTrainer 保存完整对象
            if hasattr(self.model, 'resnet'):  # ResNetSklearn
                torch.save(self.model.resnet.state_dict(), path)
            else:  # FTTransformerSklearn or others
                torch.save(self.model, path)

    def load(self) -> None:
        path = self.output.model_path(self._get_model_filename())
        if not os.path.exists(path):
            print(f"[load] Warning: Model file not found: {path}")
            return

        if self.label in ['Xgboost', 'GLM']:
            self.model = joblib.load(path)
        else:
            # Torch 模型的加载需要根据结构区别处理
            if self.label == 'ResNet' or self.label == 'ResNetClassifier':
                # ResNet 需要重新构建骨架，结构参数依赖 ctx，因此交由子类处理
                pass
            else:
                # FT-Transformer 序列化了整个对象，可直接加载后迁移到目标设备
                loaded = torch.load(path, map_location='cpu')
                self._move_to_device(loaded)
                self.model = loaded

    def _move_to_device(self, model_obj):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        if hasattr(model_obj, 'device'):
            model_obj.device = device
        if hasattr(model_obj, 'to'):
            model_obj.to(device)
        # 若对象内部还包含 ft/resnet 子模块，也要同时迁移设备
        if hasattr(model_obj, 'ft'):
            model_obj.ft.to(device)
        if hasattr(model_obj, 'resnet'):
            model_obj.resnet.to(device)

    def _clean_gpu(self):
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # 预测 + 缓存逻辑
    def _predict_and_cache(self,
                           model,
                           pred_prefix: str,
                           use_oht: bool = False,
                           design_fn=None) -> None:
        if design_fn:
            X_train = design_fn(train=True)
            X_test = design_fn(train=False)
        elif use_oht:
            X_train = self.ctx.train_oht_scl_data[self.ctx.var_nmes]
            X_test = self.ctx.test_oht_scl_data[self.ctx.var_nmes]
        else:
            X_train = self.ctx.train_data[self.ctx.factor_nmes]
            X_test = self.ctx.test_data[self.ctx.factor_nmes]

        preds_train = model.predict(X_train)
        preds_test = model.predict(X_test)

        self.ctx.train_data[f'pred_{pred_prefix}'] = preds_train
        self.ctx.test_data[f'pred_{pred_prefix}'] = preds_test
        self.ctx.train_data[f'w_pred_{pred_prefix}'] = (
            self.ctx.train_data[f'pred_{pred_prefix}'] *
            self.ctx.train_data[self.ctx.weight_nme]
        )
        self.ctx.test_data[f'w_pred_{pred_prefix}'] = (
            self.ctx.test_data[f'pred_{pred_prefix}'] *
            self.ctx.test_data[self.ctx.weight_nme]
        )

    def _fit_predict_cache(self,
                           model,
                           X_train,
                           y_train,
                           sample_weight,
                           pred_prefix: str,
                           use_oht: bool = False,
                           design_fn=None,
                           fit_kwargs: Optional[Dict[str, Any]] = None,
                           sample_weight_arg: Optional[str] = 'sample_weight') -> None:
        fit_kwargs = fit_kwargs.copy() if fit_kwargs else {}
        if sample_weight is not None and sample_weight_arg:
            fit_kwargs.setdefault(sample_weight_arg, sample_weight)
        model.fit(X_train, y_train, **fit_kwargs)
        self.ctx.model_label.append(self.label)
        self._predict_and_cache(
            model, pred_prefix, use_oht=use_oht, design_fn=design_fn)


class XGBTrainer(TrainerBase):
    def __init__(self, context: "BayesOptModel") -> None:
        super().__init__(context, 'Xgboost', 'Xgboost')
        self.model: Optional[xgb.XGBRegressor] = None

    def _build_estimator(self) -> xgb.XGBRegressor:
        params = dict(
            objective=self.ctx.obj,
            random_state=self.ctx.rand_seed,
            subsample=0.9,
            tree_method='gpu_hist' if self.ctx.use_gpu else 'hist',
            enable_categorical=True,
            predictor='gpu_predictor' if self.ctx.use_gpu else 'cpu_predictor'
        )
        if self.ctx.use_gpu:
            params['gpu_id'] = 0
            print(f">>> XGBoost using GPU ID: 0 (Single GPU Mode)")
        return xgb.XGBRegressor(**params)

    def cross_val(self, trial: optuna.trial.Trial) -> float:
        learning_rate = trial.suggest_float(
            'learning_rate', 1e-5, 1e-1, log=True)
        gamma = trial.suggest_float('gamma', 0, 10000)
        max_depth = trial.suggest_int('max_depth', 3, 25)
        n_estimators = trial.suggest_int('n_estimators', 10, 500, step=10)
        min_child_weight = trial.suggest_int(
            'min_child_weight', 100, 10000, step=100)
        reg_alpha = trial.suggest_float('reg_alpha', 1e-10, 1, log=True)
        reg_lambda = trial.suggest_float('reg_lambda', 1e-10, 1, log=True)
        if self.ctx.obj == 'reg:tweedie':
            tweedie_variance_power = trial.suggest_float(
                'tweedie_variance_power', 1, 2)
        elif self.ctx.obj == 'count:poisson':
            tweedie_variance_power = 1
        elif self.ctx.obj == 'reg:gamma':
            tweedie_variance_power = 2
        else:
            tweedie_variance_power = 1.5
        clf = self._build_estimator()
        params = {
            'learning_rate': learning_rate,
            'gamma': gamma,
            'max_depth': max_depth,
            'n_estimators': n_estimators,
            'min_child_weight': min_child_weight,
            'reg_alpha': reg_alpha,
            'reg_lambda': reg_lambda
        }
        if self.ctx.obj == 'reg:tweedie':
            params['tweedie_variance_power'] = tweedie_variance_power
        clf.set_params(**params)
        n_jobs = 1 if self.ctx.use_gpu else int(1 / self.ctx.prop_test)
        acc = cross_val_score(
            clf,
            self.ctx.train_data[self.ctx.factor_nmes],
            self.ctx.train_data[self.ctx.resp_nme].values,
            fit_params=self.ctx.fit_params,
            cv=self.ctx.cv,
            scoring=make_scorer(
                mean_tweedie_deviance,
                power=tweedie_variance_power,
                greater_is_better=False),
            error_score='raise',
            n_jobs=n_jobs
        ).mean()
        return -acc

    def train(self) -> None:
        if not self.best_params:
            raise RuntimeError('请先运行 tune() 以获得 XGB 最优参数。')
        self.model = self._build_estimator()
        self.model.set_params(**self.best_params)
        self._fit_predict_cache(
            self.model,
            self.ctx.train_data[self.ctx.factor_nmes],
            self.ctx.train_data[self.ctx.resp_nme].values,
            sample_weight=None,
            pred_prefix='xgb',
            fit_kwargs=self.ctx.fit_params,
            sample_weight_arg=None  # 样本权重已通过 fit_kwargs 传入
        )
        self.ctx.xgb_best = self.model


class GLMTrainer(TrainerBase):
    def __init__(self, context: "BayesOptModel") -> None:
        super().__init__(context, 'GLM', 'GLM')
        self.model = None

    def _select_family(self, tweedie_power: Optional[float] = None):
        if self.ctx.task_type == 'classification':
            return sm.families.Binomial()
        if self.ctx.obj == 'count:poisson':
            return sm.families.Poisson()
        if self.ctx.obj == 'reg:gamma':
            return sm.families.Gamma()
        power = tweedie_power if tweedie_power is not None else 1.5
        return sm.families.Tweedie(var_power=power, link=sm.families.links.log())

    def _prepare_design(self, data: pd.DataFrame) -> pd.DataFrame:
        # 为 statsmodels 设计矩阵添加截距项
        X = data[self.ctx.var_nmes]
        return sm.add_constant(X, has_constant='add')

    def _metric_power(self, family, tweedie_power: Optional[float]) -> float:
        if isinstance(family, sm.families.Poisson):
            return 1.0
        if isinstance(family, sm.families.Gamma):
            return 2.0
        if isinstance(family, sm.families.Tweedie):
            return tweedie_power if tweedie_power is not None else getattr(family, 'var_power', 1.5)
        return 1.5

    def cross_val(self, trial: optuna.trial.Trial) -> float:
        alpha = trial.suggest_float('alpha', 1e-6, 1e2, log=True)
        l1_ratio = trial.suggest_float('l1_ratio', 0.0, 1.0)
        tweedie_power = None
        if self.ctx.task_type == 'regression' and self.ctx.obj == 'reg:tweedie':
            tweedie_power = trial.suggest_float('tweedie_power', 1.01, 1.99)

        X_all = self._prepare_design(self.ctx.train_oht_scl_data)
        y_all = self.ctx.train_oht_scl_data[self.ctx.resp_nme]
        w_all = self.ctx.train_oht_scl_data[self.ctx.weight_nme]

        scores = []
        for train_idx, val_idx in self.ctx.cv.split(X_all):
            X_train, X_val = X_all.iloc[train_idx], X_all.iloc[val_idx]
            y_train, y_val = y_all.iloc[train_idx], y_all.iloc[val_idx]
            w_train, w_val = w_all.iloc[train_idx], w_all.iloc[val_idx]

            family = self._select_family(tweedie_power)
            glm = sm.GLM(y_train, X_train, family=family,
                         freq_weights=w_train)
            result = glm.fit_regularized(
                alpha=alpha, L1_wt=l1_ratio, maxiter=200)

            y_pred = result.predict(X_val)
            if self.ctx.task_type == 'classification':
                y_pred = np.clip(y_pred, EPS, 1 - EPS)
                fold_score = log_loss(
                    y_val, y_pred, sample_weight=w_val)
            else:
                y_pred = np.maximum(y_pred, EPS)
                fold_score = mean_tweedie_deviance(
                    y_val,
                    y_pred,
                    sample_weight=w_val,
                    power=self._metric_power(family, tweedie_power)
                )
            scores.append(fold_score)

        return float(np.mean(scores))

    def train(self) -> None:
        if not self.best_params:
            raise RuntimeError('请先运行 tune() 以获得 GLM 最优参数。')
        tweedie_power = self.best_params.get('tweedie_power')
        family = self._select_family(tweedie_power)

        X_train = self._prepare_design(self.ctx.train_oht_scl_data)
        y_train = self.ctx.train_oht_scl_data[self.ctx.resp_nme]
        w_train = self.ctx.train_oht_scl_data[self.ctx.weight_nme]

        glm = sm.GLM(y_train, X_train, family=family,
                     freq_weights=w_train)
        self.model = glm.fit_regularized(
            alpha=self.best_params['alpha'],
            L1_wt=self.best_params['l1_ratio'],
            maxiter=300
        )

        self.ctx.glm_best = self.model
        self.ctx.model_label += [self.label]
        self._predict_and_cache(
            self.model,
            'glm',
            design_fn=lambda train: self._prepare_design(
                self.ctx.train_oht_scl_data if train else self.ctx.test_oht_scl_data
            )
        )


class ResNetTrainer(TrainerBase):
    def __init__(self, context: "BayesOptModel") -> None:
        if context.task_type == 'classification':
            super().__init__(context, 'ResNetClassifier', 'ResNet')
        else:
            super().__init__(context, 'ResNet', 'ResNet')
        self.model: Optional[ResNetSklearn] = None

    # ========= 交叉验证（BayesOpt 用） =========
    def cross_val(self, trial: optuna.trial.Trial) -> float:
        # 针对 ResNet 的交叉验证流程，重点控制显存：
        #   - 每个 fold 单独创建 ResNetSklearn，结束立刻释放资源；
        #   - fold 完成后迁移模型到 CPU，删除对象并调用 gc/empty_cache；
        #   - 可选：BayesOpt 期间只抽样部分训练集以减少显存压力。

        # 1. 超参空间（基本沿用你之前的设定）
        learning_rate = trial.suggest_float(
            'learning_rate', 1e-6, 1e-2, log=True
        )
        # hidden_dim = trial.suggest_int('hidden_dim', 32, 256, step=32) # 不宜过大
        hidden_dim = trial.suggest_int('hidden_dim', 8, 32, step=2)
        block_num = trial.suggest_int('block_num', 2, 10)

        if self.ctx.task_type == 'regression':
            if self.ctx.obj == 'reg:tweedie':
                tw_power = trial.suggest_float('tw_power', 1.0, 2.0)
            elif self.ctx.obj == 'count:poisson':
                tw_power = 1.0
            elif self.ctx.obj == 'reg:gamma':
                tw_power = 2.0
            else:
                tw_power = 1.5
        else:  # classification
            tw_power = None  # Not used

        fold_losses = []

        # 2. （可选）BayesOpt 只在子样本上做 CV，减轻显存 & 时间压力
        data_for_cv = self.ctx.train_oht_scl_data
        max_rows_for_resnet_bo = min(100000, int(
            len(data_for_cv)/5))  # 你可以按 A30 情况调小，比如 50_000
        if len(data_for_cv) > max_rows_for_resnet_bo:
            data_for_cv = data_for_cv.sample(
                max_rows_for_resnet_bo,
                random_state=self.ctx.rand_seed
            )

        X_all = data_for_cv[self.ctx.var_nmes]
        y_all = data_for_cv[self.ctx.resp_nme]
        w_all = data_for_cv[self.ctx.weight_nme]

        # 用局部 ShuffleSplit，避免子样本时索引不一致
        cv_local = ShuffleSplit(
            n_splits=int(1 / self.ctx.prop_test),
            test_size=self.ctx.prop_test,
            random_state=self.ctx.rand_seed
        )

        # 使用 Hold-out 验证代替 K-Fold CV 以提高速度
        # 只取一次划分
        train_idx, val_idx = next(cv_local.split(X_all))

        X_train_fold = X_all.iloc[train_idx]
        y_train_fold = y_all.iloc[train_idx]
        w_train_fold = w_all.iloc[train_idx]

        X_val_fold = X_all.iloc[val_idx]
        y_val_fold = y_all.iloc[val_idx]
        w_val_fold = w_all.iloc[val_idx]

        # 3. 创建 ResNet 模型
        cv_net = ResNetSklearn(
            model_nme=self.ctx.model_nme,
            input_dim=X_all.shape[1],
            hidden_dim=hidden_dim,
            block_num=block_num,
            task_type=self.ctx.task_type,
            epochs=self.ctx.epochs,
            tweedie_power=tw_power,
            learning_rate=learning_rate,
            patience=5,
            use_layernorm=True,
            dropout=0.1,
            residual_scale=0.1,
            use_data_parallel=self.ctx.config.use_resn_data_parallel,
            use_ddp=self.ctx.config.use_resn_ddp
        )

        try:
            # 4. 训练
            cv_net.fit(
                X_train_fold,
                y_train_fold,
                w_train_fold,
                X_val_fold,
                y_val_fold,
                w_val_fold,
                trial=trial
            )

            # 5. 验证集预测
            y_pred_fold = cv_net.predict(X_val_fold)

            # 6. 评估：Tweedie deviance（评估用，训练 loss 不动）
            if self.ctx.task_type == 'regression':
                loss = mean_tweedie_deviance(
                    y_val_fold,
                    y_pred_fold,
                    sample_weight=w_val_fold,
                    power=tw_power
                )
            else:  # classification
                from sklearn.metrics import log_loss
                loss = log_loss(
                    y_val_fold,
                    y_pred_fold,
                    sample_weight=w_val_fold,
                )
            fold_losses.append(loss)
        finally:
            # 7. 结束后释放 GPU 资源
            try:
                if hasattr(cv_net, "resnet"):
                    cv_net.resnet.to("cpu")
            except Exception:
                pass
            del cv_net
            self._clean_gpu()

        return np.mean(fold_losses)

    # ========= 用最优超参训练最终 ResNet =========
    def train(self) -> None:
        if not self.best_params:
            raise RuntimeError('请先运行 tune() 以获得 ResNet 最优参数。')

        self.model = ResNetSklearn(
            model_nme=self.ctx.model_nme,
            input_dim=self.ctx.train_oht_scl_data[self.ctx.var_nmes].shape[1],
            task_type=self.ctx.task_type,
            use_data_parallel=self.ctx.config.use_resn_data_parallel,
            use_ddp=self.ctx.config.use_resn_ddp
        )
        self.model.set_params(self.best_params)

        self._fit_predict_cache(
            self.model,
            self.ctx.train_oht_scl_data[self.ctx.var_nmes],
            self.ctx.train_oht_scl_data[self.ctx.resp_nme],
            sample_weight=self.ctx.train_oht_scl_data[self.ctx.weight_nme],
            pred_prefix='resn',
            use_oht=True,
            sample_weight_arg='w_train'
        )

        # 方便外部调用
        self.ctx.resn_best = self.model

    # ========= 保存 / 加载 =========
    # ResNet 使用 state_dict 保存，需要特殊的 load 逻辑，所以保留 load
    # save 逻辑已经在 TrainerBase 中处理了 (check for .resnet attribute)

    def load(self) -> None:
        # 将磁盘中的 ResNet 权重加载到当前设备，保持与上下文一致。
        path = self.output.model_path(self._get_model_filename())
        if os.path.exists(path):
            resn_loaded = ResNetSklearn(
                model_nme=self.ctx.model_nme,
                input_dim=self.ctx.train_oht_scl_data[self.ctx.var_nmes].shape[1],
                task_type=self.ctx.task_type,
                use_data_parallel=self.ctx.config.use_resn_data_parallel,
                use_ddp=self.ctx.config.use_resn_ddp
            )
            state_dict = torch.load(path, map_location='cpu')
            resn_loaded.resnet.load_state_dict(state_dict)

            self._move_to_device(resn_loaded)
            self.model = resn_loaded
            self.ctx.resn_best = self.model
        else:
            print(f"[ResNetTrainer.load] 未找到模型文件：{path}")


class FTTrainer(TrainerBase):
    def __init__(self, context: "BayesOptModel") -> None:
        if context.task_type == 'classification':
            super().__init__(context, 'FTTransformerClassifier', 'FTTransformer')
        else:
            super().__init__(context, 'FTTransformer', 'FTTransformer')
        self.model: Optional[FTTransformerSklearn] = None

    def cross_val(self, trial: optuna.trial.Trial) -> float:
        # 针对 FT-Transformer 的交叉验证，重点同样在显存控制：
        #   - 收缩超参搜索空间，防止不必要的超大模型；
        #   - 每个 fold 结束后立即释放 GPU 显存，确保下一个 trial 顺利进行。
        # 超参空间适当缩小一点，避免特别大的模型
        learning_rate = trial.suggest_float(
            'learning_rate', 1e-5, 5e-4, log=True
        )
        d_model = trial.suggest_int('d_model', 32, 256, step=32)
        # n_heads = trial.suggest_categorical('n_heads', [2, 4]) 避免欠拟合
        n_heads = trial.suggest_categorical('n_heads', [2, 4, 8])
        # n_layers = trial.suggest_int('n_layers', 2, 4) 避免欠拟合
        n_layers = trial.suggest_int('n_layers', 2, 8)
        dropout = trial.suggest_float('dropout', 0.0, 0.2)

        if self.ctx.task_type == 'regression':
            if self.ctx.obj == 'reg:tweedie':
                tw_power = trial.suggest_float('tw_power', 1.0, 2.0)
            elif self.ctx.obj == 'count:poisson':
                tw_power = 1.0
            elif self.ctx.obj == 'reg:gamma':
                tw_power = 2.0
            else:
                tw_power = 1.5
        else:  # classification
            tw_power = None  # Not used

        fold_losses = []

        # 可选：只在子样本上做 BO，避免大数据直接压垮显存
        data_for_cv = self.ctx.train_data
        max_rows_for_ft_bo = min(1000000, int(
            len(data_for_cv)/2))   # 你可以根据显存情况调小或调大
        if len(data_for_cv) > max_rows_for_ft_bo:
            data_for_cv = data_for_cv.sample(
                max_rows_for_ft_bo,
                random_state=self.ctx.rand_seed
            )

        # 用局部 ShuffleSplit，避免子样本时索引不一致
        cv_local = ShuffleSplit(
            n_splits=int(1 / self.ctx.prop_test),
            test_size=self.ctx.prop_test,
            random_state=self.ctx.rand_seed
        )

        # 使用 Hold-out 验证代替 K-Fold CV 以提高速度
        # 只取一次划分
        train_idx, val_idx = next(cv_local.split(
            data_for_cv[self.ctx.factor_nmes]))

        X_train_fold = data_for_cv.iloc[train_idx][self.ctx.factor_nmes]
        y_train_fold = data_for_cv.iloc[train_idx][self.ctx.resp_nme]
        w_train_fold = data_for_cv.iloc[train_idx][self.ctx.weight_nme]
        X_val_fold = data_for_cv.iloc[val_idx][self.ctx.factor_nmes]
        y_val_fold = data_for_cv.iloc[val_idx][self.ctx.resp_nme]
        w_val_fold = data_for_cv.iloc[val_idx][self.ctx.weight_nme]

        cv_ft = FTTransformerSklearn(
            model_nme=self.ctx.model_nme,
            num_cols=self.ctx.num_features,
            cat_cols=self.ctx.cate_list,
            d_model=d_model,
            n_heads=n_heads,
            n_layers=n_layers,
            dropout=dropout,
            task_type=self.ctx.task_type,
            # batch_num=batch_num,
            epochs=self.ctx.epochs,
            tweedie_power=tw_power,
            learning_rate=learning_rate,
            patience=5,
            use_data_parallel=self.ctx.config.use_ft_data_parallel,
            use_ddp=self.ctx.config.use_ft_ddp
        )

        try:
            cv_ft.fit(
                X_train_fold, y_train_fold, w_train_fold,
                X_val_fold, y_val_fold, w_val_fold,
                trial=trial
            )
            y_pred_fold = cv_ft.predict(X_val_fold)
            if self.ctx.task_type == 'regression':
                loss = mean_tweedie_deviance(
                    y_val_fold,
                    y_pred_fold,
                    sample_weight=w_val_fold,
                    power=tw_power
                )
            else:  # classification
                from sklearn.metrics import log_loss
                loss = log_loss(
                    y_val_fold,
                    y_pred_fold,
                    sample_weight=w_val_fold,
                )
            fold_losses.append(loss)
        finally:
            # 结束后立即释放 GPU 资源
            try:
                # 如果模型在 GPU 上，先挪回 CPU
                if hasattr(cv_ft, "ft"):
                    cv_ft.ft.to("cpu")
            except Exception:
                pass
            del cv_ft
            self._clean_gpu()

        return np.mean(fold_losses)

    def train(self) -> None:
        if not self.best_params:
            raise RuntimeError('请先运行 tune() 以获得 FT-Transformer 最优参数。')
        self.model = FTTransformerSklearn(
            model_nme=self.ctx.model_nme,
            num_cols=self.ctx.num_features,
            cat_cols=self.ctx.cate_list,
            task_type=self.ctx.task_type,
            use_data_parallel=self.ctx.config.use_ft_data_parallel,
            use_ddp=self.ctx.config.use_ft_ddp
        )
        self.model.set_params(self.best_params)
        self._fit_predict_cache(
            self.model,
            self.ctx.train_data[self.ctx.factor_nmes],
            self.ctx.train_data[self.ctx.resp_nme],
            sample_weight=self.ctx.train_data[self.ctx.weight_nme],
            pred_prefix='ft',
            sample_weight_arg='w_train'
        )
        self.ctx.ft_best = self.model


# =============================================================================
# BayesOpt orchestration & SHAP utilities
# =============================================================================
class BayesOptModel:
    def __init__(self, train_data, test_data,
                 model_nme, resp_nme, weight_nme, factor_nmes, task_type='regression',
                 binary_resp_nme=None,
                 cate_list=None, prop_test=0.25, rand_seed=None,
                 epochs=100, use_gpu=True,
                 use_resn_data_parallel: bool = False, use_ft_data_parallel: bool = False,
                 use_resn_ddp: bool = False, use_ft_ddp: bool = False):
        cfg = BayesOptConfig(
            model_nme=model_nme,
            task_type=task_type,
            resp_nme=resp_nme,
            weight_nme=weight_nme,
            factor_nmes=list(factor_nmes),
            binary_resp_nme=binary_resp_nme,
            cate_list=list(cate_list) if cate_list else None,
            prop_test=prop_test,
            rand_seed=rand_seed,
            epochs=epochs,
            use_gpu=use_gpu,
            use_resn_data_parallel=use_resn_data_parallel,
            use_ft_data_parallel=use_ft_data_parallel,
            use_resn_ddp=use_resn_ddp,
            use_ft_ddp=use_ft_ddp
        )
        self.config = cfg
        self.model_nme = cfg.model_nme
        self.task_type = cfg.task_type
        self.resp_nme = cfg.resp_nme
        self.weight_nme = cfg.weight_nme
        self.factor_nmes = cfg.factor_nmes
        self.binary_resp_nme = cfg.binary_resp_nme
        self.cate_list = list(cfg.cate_list or [])
        self.prop_test = cfg.prop_test
        self.epochs = cfg.epochs
        self.rand_seed = cfg.rand_seed if cfg.rand_seed is not None else np.random.randint(
            1, 10000)
        self.use_gpu = bool(cfg.use_gpu and torch.cuda.is_available())
        self.output_manager = OutputManager(os.getcwd(), self.model_nme)

        preprocessor = DatasetPreprocessor(train_data, test_data, cfg).run()
        self.train_data = preprocessor.train_data
        self.test_data = preprocessor.test_data
        self.train_oht_scl_data = preprocessor.train_oht_scl_data
        self.test_oht_scl_data = preprocessor.test_oht_scl_data
        self.var_nmes = preprocessor.var_nmes
        self.num_features = preprocessor.num_features
        self.cat_categories_for_shap = preprocessor.cat_categories_for_shap

        self.cv = ShuffleSplit(n_splits=int(1/self.prop_test),
                               test_size=self.prop_test,
                               random_state=self.rand_seed)
        if self.task_type == 'classification':
            self.obj = 'binary:logistic'
        else:  # regression
            if 'f' in self.model_nme:
                self.obj = 'count:poisson'
            elif 's' in self.model_nme:
                self.obj = 'reg:gamma'
            elif 'bc' in self.model_nme:
                self.obj = 'reg:tweedie'
            else:
                self.obj = 'reg:tweedie'
        self.fit_params = {
            'sample_weight': self.train_data[self.weight_nme].values
        }
        self.model_label: List[str] = []

        # 记录各模型训练器，后续统一通过标签访问，方便扩展新模型
        self.trainers: Dict[str, TrainerBase] = {
            'glm': GLMTrainer(self),
            'xgb': XGBTrainer(self),
            'resn': ResNetTrainer(self),
            'ft': FTTrainer(self)
        }
        self.xgb_best = None
        self.resn_best = None
        self.glm_best = None
        self.ft_best = None
        self.best_xgb_params = None
        self.best_resn_params = None
        self.best_ft_params = None
        self.best_xgb_trial = None
        self.best_resn_trial = None
        self.best_ft_trial = None
        self.best_glm_params = None
        self.best_glm_trial = None
        self.xgb_load = None
        self.resn_load = None
        self.ft_load = None

    # 定义单因素画图函数
    def plot_oneway(self, n_bins=10):
        for c in self.factor_nmes:
            fig = plt.figure(figsize=(7, 5))
            if c in self.cate_list:
                group_col = c
                plot_source = self.train_data
            else:
                group_col = f'{c}_bins'
                bins = pd.qcut(
                    self.train_data[c],
                    n_bins,
                    duplicates='drop'  # 注意：如果分位数重复会丢 bin，避免异常终止
                )
                plot_source = self.train_data.assign(**{group_col: bins})
            plot_data = plot_source.groupby(
                [group_col], observed=True).sum(numeric_only=True)
            plot_data.reset_index(inplace=True)
            plot_data['act_v'] = plot_data['w_act'] / \
                plot_data[self.weight_nme]
            plot_data.head()
            ax = fig.add_subplot(111)
            ax.plot(plot_data.index, plot_data['act_v'],
                    label='Actual', color='red')
            ax.set_title(
                'Analysis of  %s : Train Data' % group_col,
                fontsize=8)
            plt.xticks(plot_data.index,
                       list(plot_data[group_col].astype(str)),
                       rotation=90)
            if len(list(plot_data[group_col].astype(str))) > 50:
                plt.xticks(fontsize=3)
            else:
                plt.xticks(fontsize=6)
            plt.yticks(fontsize=6)
            ax2 = ax.twinx()
            ax2.bar(plot_data.index,
                    plot_data[self.weight_nme],
                    alpha=0.5, color='seagreen')
            plt.yticks(fontsize=6)
            plt.margins(0.05)
            plt.subplots_adjust(wspace=0.3)
            save_path = self.output_manager.plot_path(
                f'00_{self.model_nme}_{group_col}_oneway.png')
            plt.savefig(save_path, dpi=300)
            plt.close(fig)

    # 定义通用优化函数
    def optimize_model(self, model_key: str, max_evals: int = 100):
        if model_key not in self.trainers:
            print(f"Warning: Unknown model key: {model_key}")
            return

        trainer = self.trainers[model_key]
        trainer.tune(max_evals)
        trainer.train()

        # Update context attributes for backward compatibility
        setattr(self, f"{model_key}_best", trainer.model)
        setattr(self, f"best_{model_key}_params", trainer.best_params)
        setattr(self, f"best_{model_key}_trial", trainer.best_trial)

    # 定义GLM贝叶斯优化函数
    def bayesopt_glm(self, max_evals=50):
        self.optimize_model('glm', max_evals)

    # 定义Xgboost贝叶斯优化函数
    def bayesopt_xgb(self, max_evals=100):
        self.optimize_model('xgb', max_evals)

    # 定义ResNet贝叶斯优化函数
    def bayesopt_resnet(self, max_evals=100):
        self.optimize_model('resn', max_evals)

    # 定义 FT-Transformer 贝叶斯优化函数
    def bayesopt_ft(self, max_evals=50):
        self.optimize_model('ft', max_evals)

    # 绘制提纯曲线
    def plot_lift(self, model_label, pred_nme, n_bins=10):
        model_map = {
            'Xgboost': 'pred_xgb',
            'ResNet': 'pred_resn',
            'ResNetClassifier': 'pred_resn',
            'FTTransformer': 'pred_ft',
            'FTTransformerClassifier': 'pred_ft',
            'GLM': 'pred_glm'
        }
        for k, v in model_map.items():
            if model_label.startswith(k):
                pred_nme = v
                break

        fig = plt.figure(figsize=(11, 5))
        for pos, (title, data) in zip([121, 122],
                                      [('Lift Chart on Train Data', self.train_data),
                                       ('Lift Chart on Test Data', self.test_data)]):
            lift_df = pd.DataFrame({
                'pred': data[pred_nme].values,
                'w_pred': data[f'w_{pred_nme}'].values,
                'act': data['w_act'].values,
                'weight': data[self.weight_nme].values
            })
            plot_data = PlotUtils.split_data(lift_df, 'pred', 'weight', n_bins)
            denom = np.maximum(plot_data['weight'], EPS)
            plot_data['exp_v'] = plot_data['w_pred'] / denom
            plot_data['act_v'] = plot_data['act'] / denom
            plot_data = plot_data.reset_index()

            ax = fig.add_subplot(pos)
            PlotUtils.plot_lift_ax(ax, plot_data, title)

        plt.subplots_adjust(wspace=0.3)
        save_path = self.output_manager.plot_path(
            f'01_{self.model_nme}_{model_label}_lift.png')
        plt.savefig(save_path, dpi=300)
        plt.show()
        plt.close(fig)

    # 绘制双提纯曲线
    def plot_dlift(self, model_comp: List[str] = ['xgb', 'resn'], n_bins: int = 10) -> None:
        # 绘制双提纯曲线，对比两个模型在不同分箱下的表现。
        # Args:
        #   model_comp: 需要对比的模型简称（如 ['xgb', 'resn']，支持 'xgb'/'resn'/'ft'）。
        #   n_bins: 分箱数量，用于控制 lift 曲线的粒度。
        if len(model_comp) != 2:
            raise ValueError("`model_comp` 必须包含两个模型进行对比。")

        model_name_map = {
            'xgb': 'Xgboost',
            'resn': 'ResNet',
            'ft': 'FTTransformer',
            'glm': 'GLM'
        }

        name1, name2 = model_comp
        if name1 not in model_name_map or name2 not in model_name_map:
            raise ValueError(f"不支持的模型简称。请从 {list(model_name_map.keys())} 中选择。")

        fig, axes = plt.subplots(1, 2, figsize=(11, 5))
        datasets = {
            'Train Data': self.train_data,
            'Test Data': self.test_data
        }

        for ax, (data_name, data) in zip(axes, datasets.items()):
            pred1_col = f'w_pred_{name1}'
            pred2_col = f'w_pred_{name2}'

            if pred1_col not in data.columns or pred2_col not in data.columns:
                print(
                    f"警告: 在 {data_name} 中找不到预测列 {pred1_col} 或 {pred2_col}。跳过绘图。")
                continue

            lift_data = pd.DataFrame({
                'pred1': data[pred1_col].values,
                'pred2': data[pred2_col].values,
                'diff_ly': data[pred1_col].values / np.maximum(data[pred2_col].values, EPS),
                'act': data['w_act'].values,
                'weight': data[self.weight_nme].values
            })
            plot_data = PlotUtils.split_data(
                lift_data, 'diff_ly', 'weight', n_bins)
            denom = np.maximum(plot_data['act'], EPS)
            plot_data['exp_v1'] = plot_data['pred1'] / denom
            plot_data['exp_v2'] = plot_data['pred2'] / denom
            plot_data['act_v'] = plot_data['act'] / denom
            plot_data.reset_index(inplace=True)

            label1 = model_name_map[name1]
            label2 = model_name_map[name2]

            PlotUtils.plot_dlift_ax(
                ax, plot_data, f'Double Lift Chart on {data_name}', label1, label2)

        plt.subplots_adjust(bottom=0.25, top=0.95, right=0.8, wspace=0.3)
        save_path = self.output_manager.plot_path(
            f'02_{self.model_nme}_dlift_{name1}_vs_{name2}.png')
        plt.savefig(save_path, dpi=300)
        plt.show()
        plt.close(fig)

    # 绘制成交率提升曲线
    def plot_conversion_lift(self, model_pred_col: str, n_bins: int = 20):
        if not self.binary_resp_nme:
            print("错误: 未在 BayesOptModel 初始化时提供 `binary_resp_nme`。无法绘制成交率曲线。")
            return

        fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
        datasets = {
            'Train Data': self.train_data,
            'Test Data': self.test_data
        }

        for ax, (data_name, data) in zip(axes, datasets.items()):
            if model_pred_col not in data.columns:
                print(f"警告: 在 {data_name} 中找不到预测列 '{model_pred_col}'。跳过绘图。")
                continue

            # 按模型预测分排序，并计算分箱
            plot_data = data.sort_values(by=model_pred_col).copy()
            plot_data['cum_weight'] = plot_data[self.weight_nme].cumsum()
            total_weight = plot_data[self.weight_nme].sum()

            if total_weight > EPS:
                plot_data['bin'] = pd.cut(
                    plot_data['cum_weight'],
                    bins=n_bins,
                    labels=False,
                    right=False
                )
            else:
                plot_data['bin'] = 0

            # 按分箱聚合
            lift_agg = plot_data.groupby('bin').agg(
                total_weight=(self.weight_nme, 'sum'),
                actual_conversions=(self.binary_resp_nme, 'sum'),
                weighted_conversions=('w_binary_act', 'sum'),
                avg_pred=(model_pred_col, 'mean')
            ).reset_index()

            # 计算成交率
            lift_agg['conversion_rate'] = lift_agg['weighted_conversions'] / \
                lift_agg['total_weight']

            # 计算整体平均成交率
            overall_conversion_rate = data['w_binary_act'].sum(
            ) / data[self.weight_nme].sum()
            ax.axhline(y=overall_conversion_rate, color='gray', linestyle='--',
                       label=f'Overall Avg Rate ({overall_conversion_rate:.2%})')

            ax.plot(lift_agg['bin'], lift_agg['conversion_rate'],
                    marker='o', linestyle='-', label='Actual Conversion Rate')
            ax.set_title(f'Conversion Rate Lift Chart on {data_name}')
            ax.set_xlabel(f'Model Score Decile (based on {model_pred_col})')
            ax.set_ylabel('Conversion Rate')
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend()

        plt.tight_layout()
        plt.show()

    # 保存模型
    def save_model(self, model_name=None):
        keys = [model_name] if model_name else self.trainers.keys()
        for key in keys:
            if key in self.trainers:
                self.trainers[key].save()
            else:
                if model_name:  # Only warn if specific model requested
                    print(f"[save_model] Warning: Unknown model key {key}")

    def load_model(self, model_name=None):
        keys = [model_name] if model_name else self.trainers.keys()
        for key in keys:
            if key in self.trainers:
                self.trainers[key].load()
                # Update context attributes
                trainer = self.trainers[key]
                if trainer.model is not None:
                    setattr(self, f"{key}_best", trainer.model)
                    # Also update xxx_load for backward compatibility if needed
                    # Original code had xgb_load, resn_load, ft_load but not glm_load
                    if key in ['xgb', 'resn', 'ft']:
                        setattr(self, f"{key}_load", trainer.model)
            else:
                if model_name:
                    print(f"[load_model] Warning: Unknown model key {key}")

    def _sample_rows(self, data: pd.DataFrame, n: int) -> pd.DataFrame:
        if len(data) == 0:
            return data
        return data.sample(min(len(data), n), random_state=self.rand_seed)

    @staticmethod
    def _shap_nsamples(arr: np.ndarray, max_nsamples: int = 300) -> int:
        min_needed = arr.shape[1] + 2
        return max(min_needed, min(max_nsamples, arr.shape[0] * arr.shape[1]))

    def _build_ft_shap_matrix(self, data: pd.DataFrame) -> np.ndarray:

        # 将原始特征 DataFrame (包含 self.factor_nmes) 转成
        # 纯数值矩阵: 数值列为 float64，类别列为整数 code（float64 存储）。
        # 列顺序与 self.factor_nmes 保持一致。

        matrices = []

        for col in self.factor_nmes:
            s = data[col]

            if col in self.cate_list:
                # 类别列：按训练时的类别全集编码
                cats = pd.Categorical(
                    s,
                    categories=self.cat_categories_for_shap[col]
                )
                # cats.codes 是一个 Index / ndarray，用 np.asarray 包一下再 reshape
                codes = np.asarray(cats.codes, dtype=np.float64).reshape(-1, 1)
                matrices.append(codes)
            else:
                # 数值列：转成 Series -> numpy -> reshape
                vals = pd.to_numeric(s, errors="coerce")
                arr = vals.to_numpy(dtype=np.float64, copy=True).reshape(-1, 1)
                matrices.append(arr)

        X_mat = np.concatenate(matrices, axis=1)  # (N, F)
        return X_mat

    def _decode_ft_shap_matrix_to_df(self, X_mat: np.ndarray) -> pd.DataFrame:

        # 将 SHAP 的数值矩阵 (N, F) 还原为原始特征 DataFrame，
        # 数值列为 float，类别列还原为 pandas 的 category 类型，
        # 以便兼容 enable_categorical=True 的 XGBoost 和 FT-Transformer 的输入。
        # 列顺序 = self.factor_nmes

        data_dict = {}

        for j, col in enumerate(self.factor_nmes):
            col_vals = X_mat[:, j]

            if col in self.cate_list:
                cats = self.cat_categories_for_shap[col]

                # SHAP 会扰动成小数，这里 round 回整数 code
                codes = np.round(col_vals).astype(int)
                # 限制在 [-1, len(cats)-1]
                codes = np.clip(codes, -1, len(cats) - 1)

                # 使用 pandas.Categorical.from_codes：
                #   - codes = -1 被当成缺失 (NaN)
                #   - 其他索引映射到 cats 中对应的类别
                cat_series = pd.Categorical.from_codes(
                    codes,
                    categories=cats
                )
                # 存的是 Categorical 类型，而不是 object
                data_dict[col] = cat_series
            else:
                # 数值列：直接 float
                data_dict[col] = col_vals.astype(float)

        df = pd.DataFrame(data_dict, columns=self.factor_nmes)

        # 再保险：确保所有类别列 dtype 真的是 category
        for col in self.cate_list:
            if col in df.columns:
                df[col] = df[col].astype("category")
        return df

    def _build_glm_design(self, data: pd.DataFrame) -> pd.DataFrame:
        # 与 GLM 训练阶段一致：在 one-hot + 标准化特征上添加截距
        X = data[self.var_nmes]
        return sm.add_constant(X, has_constant='add')

    def _compute_shap_core(self,
                           model_key: str,
                           n_background: int,
                           n_samples: int,
                           on_train: bool,
                           X_df: pd.DataFrame,
                           prep_fn,
                           predict_fn,
                           cleanup_fn=None):
        # 通用的 SHAP 计算核心逻辑：配置背景样本、构建解释器并返回结果。
        if model_key not in self.trainers or self.trainers[model_key].model is None:
            raise RuntimeError(f"Model {model_key} not trained.")

        if cleanup_fn:
            cleanup_fn()

        # Background
        bg_df = self._sample_rows(X_df, n_background)
        bg_mat = prep_fn(bg_df)

        # Explainer
        explainer = shap.KernelExplainer(predict_fn, bg_mat)

        # Explain data
        ex_df = self._sample_rows(X_df, n_samples)
        ex_mat = prep_fn(ex_df)

        nsample_eff = self._shap_nsamples(ex_mat)
        shap_values = explainer.shap_values(ex_mat, nsamples=nsample_eff)

        # Base value
        bg_pred = predict_fn(bg_mat)
        base_value = float(np.asarray(bg_pred).mean())

        return {
            "explainer": explainer,
            "X_explain": ex_df,
            "shap_values": shap_values,
            "base_value": base_value
        }

    # ========= XGBoost SHAP =========
    def compute_shap_xgb(self, n_background: int = 500,
                         n_samples: int = 200,
                         on_train: bool = True):
        data = self.train_data if on_train else self.test_data
        X_raw = data[self.factor_nmes]

        def predict_wrapper(x_mat):
            df_input = self._decode_ft_shap_matrix_to_df(x_mat)
            return self.xgb_best.predict(df_input)

        self.shap_xgb = self._compute_shap_core(
            'xgb', n_background, n_samples, on_train,
            X_df=X_raw,
            prep_fn=lambda df: self._build_ft_shap_matrix(
                df).astype(np.float64),
            predict_fn=predict_wrapper
        )
        return self.shap_xgb

    # ========= ResNet SHAP =========
    def _resn_predict_wrapper(self, X_np):
        # 保证走 CPU
        model = self.resn_best.resnet.to("cpu")
        with torch.no_grad():
            X_tensor = torch.tensor(X_np, dtype=torch.float32)
            y_pred = model(X_tensor).cpu().numpy()
        y_pred = np.clip(y_pred, 1e-6, None)
        return y_pred.reshape(-1)

    def compute_shap_resn(self, n_background: int = 500,
                          n_samples: int = 200,
                          on_train: bool = True):
        data = self.train_oht_scl_data if on_train else self.test_oht_scl_data
        X = data[self.var_nmes]

        def cleanup():
            self.resn_best.device = torch.device("cpu")
            self.resn_best.resnet.to("cpu")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        self.shap_resn = self._compute_shap_core(
            'resn', n_background, n_samples, on_train,
            X_df=X,
            prep_fn=lambda df: df.to_numpy(dtype=np.float64),
            predict_fn=lambda x: self._resn_predict_wrapper(x),
            cleanup_fn=cleanup
        )
        return self.shap_resn

    # ========= FT-Transformer SHAP =========
    def _ft_shap_predict_wrapper(self, X_mat: np.ndarray) -> np.ndarray:
        df_input = self._decode_ft_shap_matrix_to_df(X_mat)
        y_pred = self.ft_best.predict(df_input)
        return np.asarray(y_pred, dtype=np.float64).reshape(-1)

    def compute_shap_ft(self, n_background: int = 500,
                        n_samples: int = 200,
                        on_train: bool = True):
        data = self.train_data if on_train else self.test_data
        X_raw = data[self.factor_nmes]

        def cleanup():
            self.ft_best.device = torch.device("cpu")
            self.ft_best.ft.to("cpu")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        self.shap_ft = self._compute_shap_core(
            'ft', n_background, n_samples, on_train,
            X_df=X_raw,
            prep_fn=lambda df: self._build_ft_shap_matrix(
                df).astype(np.float64),
            predict_fn=self._ft_shap_predict_wrapper,
            cleanup_fn=cleanup
        )
        return self.shap_ft

    # ========= GLM SHAP =========
    def compute_shap_glm(self, n_background: int = 500,
                         n_samples: int = 200,
                         on_train: bool = True):
        data = self.train_oht_scl_data if on_train else self.test_oht_scl_data
        design_all = self._build_glm_design(data)
        design_cols = list(design_all.columns)

        matrices = []

        for col in self.factor_nmes:
            s = data[col]

            if col in self.cate_list:
                # 类别列：按训练时的类别全集编码
                cats = pd.Categorical(
                    s,
                    categories=self.cat_categories_for_shap[col]
                )
                # cats.codes 是一个 Index / ndarray，用 np.asarray 包一下再 reshape
                codes = np.asarray(cats.codes, dtype=np.float64).reshape(-1, 1)
                matrices.append(codes)
            else:
                # 数值列：转成 Series -> numpy -> reshape
                vals = pd.to_numeric(s, errors="coerce")
                arr = vals.to_numpy(dtype=np.float64, copy=True).reshape(-1, 1)
                matrices.append(arr)

        X_mat = np.concatenate(matrices, axis=1)  # (N, F)
        return X_mat

    def _decode_ft_shap_matrix_to_df(self, X_mat: np.ndarray) -> pd.DataFrame:

        # 将 SHAP 的数值矩阵 (N, F) 还原为原始特征 DataFrame，
        # 数值列为 float，类别列还原为 pandas 的 category 类型，
        # 以便兼容 enable_categorical=True 的 XGBoost 和 FT-Transformer 的输入。
        # 列顺序 = self.factor_nmes

        data_dict = {}

        for j, col in enumerate(self.factor_nmes):
            col_vals = X_mat[:, j]

            if col in self.cate_list:
                cats = self.cat_categories_for_shap[col]

                # SHAP 会扰动成小数，这里 round 回整数 code
                codes = np.round(col_vals).astype(int)
                # 限制在 [-1, len(cats)-1]
                codes = np.clip(codes, -1, len(cats) - 1)

                # 使用 pandas.Categorical.from_codes：
                #   - codes = -1 被当成缺失 (NaN)
                #   - 其他索引映射到 cats 中对应的类别
                cat_series = pd.Categorical.from_codes(
                    codes,
                    categories=cats
                )
                # 存的是 Categorical 类型，而不是 object
                data_dict[col] = cat_series
            else:
                # 数值列：直接 float
                data_dict[col] = col_vals.astype(float)

        df = pd.DataFrame(data_dict, columns=self.factor_nmes)

        # 再保险：确保所有类别列 dtype 真的是 category
        for col in self.cate_list:
            if col in df.columns:
                df[col] = df[col].astype("category")
        return df

    def _build_glm_design(self, data: pd.DataFrame) -> pd.DataFrame:
        # 与 GLM 训练阶段一致：在 one-hot + 标准化特征上添加截距
        X = data[self.var_nmes]
        return sm.add_constant(X, has_constant='add')

    def _compute_shap_core(self,
                           model_key: str,
                           n_background: int,
                           n_samples: int,
                           on_train: bool,
                           X_df: pd.DataFrame,
                           prep_fn,
                           predict_fn,
                           cleanup_fn=None):
        # 通用的 SHAP 计算核心逻辑：配置背景样本、构建解释器并返回结果。
        if model_key not in self.trainers or self.trainers[model_key].model is None:
            raise RuntimeError(f"Model {model_key} not trained.")

        if cleanup_fn:
            cleanup_fn()

        # Background
        bg_df = self._sample_rows(X_df, n_background)
        bg_mat = prep_fn(bg_df)

        # Explainer
        explainer = shap.KernelExplainer(predict_fn, bg_mat)

        # Explain data
        ex_df = self._sample_rows(X_df, n_samples)
        ex_mat = prep_fn(ex_df)

        nsample_eff = self._shap_nsamples(ex_mat)
        shap_values = explainer.shap_values(ex_mat, nsamples=nsample_eff)

        # Base value
        bg_pred = predict_fn(bg_mat)
        base_value = float(np.asarray(bg_pred).mean())

        return {
            "explainer": explainer,
            "X_explain": ex_df,
            "shap_values": shap_values,
            "base_value": base_value
        }

    # ========= XGBoost SHAP =========
    def compute_shap_xgb(self, n_background: int = 500,
                         n_samples: int = 200,
                         on_train: bool = True):
        data = self.train_data if on_train else self.test_data
        X_raw = data[self.factor_nmes]

        def predict_wrapper(x_mat):
            df_input = self._decode_ft_shap_matrix_to_df(x_mat)
            return self.xgb_best.predict(df_input)

        self.shap_xgb = self._compute_shap_core(
            'xgb', n_background, n_samples, on_train,
            X_df=X_raw,
            prep_fn=lambda df: self._build_ft_shap_matrix(
                df).astype(np.float64),
            predict_fn=predict_wrapper
        )
        return self.shap_xgb

    # ========= ResNet SHAP =========
    def _resn_predict_wrapper(self, X_np):
        # 保证走 CPU
        model = self.resn_best.resnet.to("cpu")
        with torch.no_grad():
            X_tensor = torch.tensor(X_np, dtype=torch.float32)
            y_pred = model(X_tensor).cpu().numpy()
        y_pred = np.clip(y_pred, 1e-6, None)
        return y_pred.reshape(-1)

    def compute_shap_resn(self, n_background: int = 500,
                          n_samples: int = 200,
                          on_train: bool = True):
        data = self.train_oht_scl_data if on_train else self.test_oht_scl_data
        X = data[self.var_nmes]

        def cleanup():
            self.resn_best.device = torch.device("cpu")
            self.resn_best.resnet.to("cpu")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        self.shap_resn = self._compute_shap_core(
            'resn', n_background, n_samples, on_train,
            X_df=X,
            prep_fn=lambda df: df.to_numpy(dtype=np.float64),
            predict_fn=lambda x: self._resn_predict_wrapper(x),
            cleanup_fn=cleanup
        )
        return self.shap_resn

    # ========= FT-Transformer SHAP =========
    def _ft_shap_predict_wrapper(self, X_mat: np.ndarray) -> np.ndarray:
        df_input = self._decode_ft_shap_matrix_to_df(X_mat)
        y_pred = self.ft_best.predict(df_input)
        return np.asarray(y_pred, dtype=np.float64).reshape(-1)

    def compute_shap_ft(self, n_background: int = 500,
                        n_samples: int = 200,
                        on_train: bool = True):
        data = self.train_data if on_train else self.test_data
        X_raw = data[self.factor_nmes]

        def cleanup():
            self.ft_best.device = torch.device("cpu")
            self.ft_best.ft.to("cpu")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        self.shap_ft = self._compute_shap_core(
            'ft', n_background, n_samples, on_train,
            X_df=X_raw,
            prep_fn=lambda df: self._build_ft_shap_matrix(
                df).astype(np.float64),
            predict_fn=self._ft_shap_predict_wrapper,
            cleanup_fn=cleanup
        )
        return self.shap_ft

    # ========= GLM SHAP =========
    def compute_shap_glm(self, n_background: int = 500,
                         n_samples: int = 200,
                         on_train: bool = True):
        data = self.train_oht_scl_data if on_train else self.test_oht_scl_data
        design_all = self._build_glm_design(data)
        design_cols = list(design_all.columns)

        def predict_wrapper(x_np):
            x_df = pd.DataFrame(x_np, columns=design_cols)
            y_pred = self.glm_best.predict(x_df)
            return np.asarray(y_pred, dtype=np.float64).reshape(-1)

        res = self._compute_shap_core(
            'glm', n_background, n_samples, on_train,
            X_df=design_all,
            prep_fn=lambda df: df.to_numpy(dtype=np.float64),
            predict_fn=predict_wrapper
        )
        return res
