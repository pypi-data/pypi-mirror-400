from sklearn.metrics import log_loss, mean_tweedie_deviance
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import ShuffleSplit  # 1.2.2
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.nn.utils import clip_grad_norm_
from torch.cuda.amp import autocast, GradScaler
from torch.utils.data import Dataset, DataLoader, TensorDataset, DistributedSampler
import xgboost as xgb  # 1.7.0
import torch.nn.functional as F
import torch.nn as nn
import torch  # 版本: 1.10.1+cu111
import statsmodels.api as sm
import shap
import pandas as pd  # 2.2.3
import optuna  # 4.3.0
import numpy as np  # 1.26.2
try:
    from torch_geometric.nn import knn_graph
    from torch_geometric.utils import add_self_loops, to_undirected
    _PYG_AVAILABLE = True
except Exception:
    knn_graph = None  # type: ignore
    add_self_loops = None  # type: ignore
    to_undirected = None  # type: ignore
    _PYG_AVAILABLE = False
try:
    import pynndescent
    _PYNN_AVAILABLE = True
except Exception:
    pynndescent = None  # type: ignore
    _PYNN_AVAILABLE = False
import matplotlib
import joblib
import csv
import json
import hashlib
import os
import random
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from contextlib import nullcontext
from datetime import datetime, timedelta
import time
import math
import gc
import copy

if os.name != "nt" and not os.environ.get("DISPLAY") and not os.environ.get("MPLBACKEND"):
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
# 通过限制内存块拆分让 PyTorch 分配器减少碎片化，缓解显存 OOM
# 如需自定义，可通过环境变量 PYTORCH_CUDA_ALLOC_CONF 覆盖默认设置
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "max_split_size_mb:256")


# 常量与工具模块
# =============================================================================
torch.backends.cudnn.benchmark = True
EPS = 1e-8

_XGB_CUDA_CHECKED = False
_XGB_HAS_CUDA = False
_GNN_MPS_WARNED = False


def _xgb_cuda_available() -> bool:
    # Best-effort check for XGBoost CUDA build; cached to avoid repeated checks.
    global _XGB_CUDA_CHECKED, _XGB_HAS_CUDA
    if _XGB_CUDA_CHECKED:
        return _XGB_HAS_CUDA
    _XGB_CUDA_CHECKED = True
    if not torch.cuda.is_available():
        _XGB_HAS_CUDA = False
        return False
    try:
        build_info = getattr(xgb, "build_info", None)
        if callable(build_info):
            info = build_info()
            for key in ("USE_CUDA", "use_cuda", "cuda"):
                if key in info:
                    val = info[key]
                    if isinstance(val, str):
                        _XGB_HAS_CUDA = val.strip().upper() in (
                            "ON", "YES", "TRUE", "1")
                    else:
                        _XGB_HAS_CUDA = bool(val)
                    return _XGB_HAS_CUDA
    except Exception:
        pass
    try:
        has_cuda = getattr(getattr(xgb, "core", None), "_has_cuda_support", None)
        if callable(has_cuda):
            _XGB_HAS_CUDA = bool(has_cuda())
            return _XGB_HAS_CUDA
    except Exception:
        pass
    _XGB_HAS_CUDA = False
    return False


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


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
    def _sanitize_params_dict(params: Dict[str, Any]) -> Dict[str, Any]:
        # 过滤 pandas 读写中可能出现的 "Unnamed: 0" 等索引列
        return {
            k: v
            for k, v in (params or {}).items()
            if k and not str(k).startswith("Unnamed")
        }

    @staticmethod
    def load_params_file(path: str) -> Dict[str, Any]:
        """从 JSON/CSV/TSV 文件加载参数字典。

        - JSON：支持直接 dict，或形如 {"best_params": {...}} 的包装结构
        - CSV/TSV：读取第一行作为参数
        """
        file_path = Path(path).expanduser().resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"params file not found: {file_path}")
        suffix = file_path.suffix.lower()
        if suffix == ".json":
            payload = json.loads(file_path.read_text(
                encoding="utf-8", errors="replace"))
            if isinstance(payload, dict) and "best_params" in payload:
                payload = payload.get("best_params") or {}
            if not isinstance(payload, dict):
                raise ValueError(
                    f"Invalid JSON params file (expect dict): {file_path}")
            return IOUtils._sanitize_params_dict(dict(payload))
        if suffix in (".csv", ".tsv"):
            df = pd.read_csv(file_path, sep="\t" if suffix == ".tsv" else ",")
            if df.empty:
                raise ValueError(f"Empty params file: {file_path}")
            params = df.iloc[0].to_dict()
            return IOUtils._sanitize_params_dict(params)
        raise ValueError(
            f"Unsupported params file type '{suffix}': {file_path}")

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
        print(">>> 将所有模型迁移到 CPU...")
        for obj in gc.get_objects():
            try:
                if hasattr(obj, "to") and callable(obj.to):
                    obj.to("cpu")
            except Exception:
                pass

        print(">>> 删除张量/优化器/DataLoader 引用...")
        gc.collect()

        print(">>> 清空 CUDA cache...")
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            print(">>> CUDA 显存已释放。")
        else:
            print(">>> CUDA 不可用，已跳过清理。")


class DistributedUtils:
    _cached_state: Optional[tuple] = None

    @staticmethod
    def setup_ddp():
        """初始化用于分布式训练的 DDP 进程组。"""
        if dist.is_initialized():
            if DistributedUtils._cached_state is None:
                rank = dist.get_rank()
                world_size = dist.get_world_size()
                local_rank = int(os.environ.get("LOCAL_RANK", 0))
                DistributedUtils._cached_state = (
                    True,
                    local_rank,
                    rank,
                    world_size,
                )
            return DistributedUtils._cached_state

        if 'RANK' in os.environ and 'WORLD_SIZE' in os.environ:
            rank = int(os.environ["RANK"])
            world_size = int(os.environ["WORLD_SIZE"])
            local_rank = int(os.environ["LOCAL_RANK"])

            if os.name == "nt" and torch.cuda.is_available() and world_size > 1:
                print(
                    ">>> DDP Setup Disabled: Windows CUDA DDP is not supported. "
                    "Falling back to single process."
                )
                return False, 0, 0, 1

            if torch.cuda.is_available():
                torch.cuda.set_device(local_rank)

            timeout_seconds = int(os.environ.get(
                "BAYESOPT_DDP_TIMEOUT_SECONDS", "1800"))
            timeout = timedelta(seconds=max(1, timeout_seconds))
            backend = "gloo"
            if torch.cuda.is_available() and os.name != "nt":
                try:
                    if getattr(dist, "is_nccl_available", lambda: False)():
                        backend = "nccl"
                except Exception:
                    backend = "gloo"

            dist.init_process_group(
                backend=backend, init_method="env://", timeout=timeout)
            print(
                f">>> DDP Initialized ({backend}, timeout={timeout_seconds}s): "
                f"Rank {rank}/{world_size}, Local Rank {local_rank}"
            )
            DistributedUtils._cached_state = (
                True,
                local_rank,
                rank,
                world_size,
            )
            return DistributedUtils._cached_state
        else:
            print(
                f">>> DDP Setup Failed: RANK or WORLD_SIZE not found in env. Keys found: {list(os.environ.keys())}"
            )
            print(
                ">>> Hint: launch with torchrun --nproc_per_node=<N> <script.py>"
            )
        return False, 0, 0, 1

    @staticmethod
    def cleanup_ddp():
        """销毁已创建的 DDP 进程组并清理本地缓存状态。"""
        if dist.is_initialized():
            dist.destroy_process_group()
        DistributedUtils._cached_state = None

    @staticmethod
    def is_main_process():
        return not dist.is_initialized() or dist.get_rank() == 0

    @staticmethod
    def world_size() -> int:
        return dist.get_world_size() if dist.is_initialized() else 1


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


def infer_factor_and_cate_list(train_df: pd.DataFrame,
                               test_df: pd.DataFrame,
                               resp_nme: str,
                               weight_nme: str,
                               binary_resp_nme: Optional[str] = None,
                               factor_nmes: Optional[List[str]] = None,
                               cate_list: Optional[List[str]] = None,
                               infer_categorical_max_unique: int = 50,
                               infer_categorical_max_ratio: float = 0.05) -> Tuple[List[str], List[str]]:
    """在特征列名未知时，推断 factor_nmes/cate_list。

    规则：
      - factor_nmes：默认取 train/test 共有列，排除目标列/权重列/(可选二分类目标列)。
      - cate_list：默认取 object/category/bool，外加“低基数”的整数列。
      - 始终与 train/test 的共有列取交集，避免训练/测试列不一致。
    """
    excluded = {resp_nme, weight_nme}
    if binary_resp_nme:
        excluded.add(binary_resp_nme)

    common_cols = [c for c in train_df.columns if c in test_df.columns]
    if factor_nmes is None:
        factors = [c for c in common_cols if c not in excluded]
    else:
        factors = [
            c for c in factor_nmes if c in common_cols and c not in excluded]

    if cate_list is not None:
        cats = [c for c in cate_list if c in factors]
        return factors, cats

    n_rows = max(1, len(train_df))
    cats: List[str] = []
    for col in factors:
        s = train_df[col]
        if pd.api.types.is_bool_dtype(s) or pd.api.types.is_object_dtype(s) or pd.api.types.is_categorical_dtype(s):
            cats.append(col)
            continue
        if pd.api.types.is_integer_dtype(s):
            nunique = int(s.nunique(dropna=True))
            if nunique <= infer_categorical_max_unique or (nunique / n_rows) <= infer_categorical_max_ratio:
                cats.append(col)
    return factors, cats


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

    def _resolve_num_workers(self, max_workers: int) -> int:
        if os.name == 'nt':
            return 0
        if getattr(self, "is_ddp_enabled", False):
            return 0
        return min(int(max_workers), os.cpu_count() or 1)

    def _build_dataloader(self,
                          dataset,
                          N: int,
                          base_bs_gpu: tuple,
                          base_bs_cpu: tuple,
                          min_bs: int = 64,
                          target_effective_cuda: int = 1024,
                          target_effective_cpu: int = 512,
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
            if getattr(self, "is_ddp_enabled", False):
                device_count = 1
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
        if getattr(self, "is_ddp_enabled", False):
            world_size = max(1, DistributedUtils.world_size())
            target_effective_bs = max(1, target_effective_bs // world_size)

        world_size = getattr(self, "world_size", 1) if getattr(
            self, "is_ddp_enabled", False) else 1
        samples_per_rank = math.ceil(
            N / max(1, world_size)) if world_size > 1 else N
        steps_per_epoch = max(
            1, math.ceil(samples_per_rank / max(1, batch_size)))
        # 限制梯度累积步数：避免用超过实际 batch 数的系数去缩放 loss。
        desired_accum = max(1, target_effective_bs // max(1, batch_size))
        accum_steps = max(1, min(desired_accum, steps_per_epoch))

        # Linux (posix) 采用 fork 更高效；Windows (nt) 使用 spawn，开销更大。
        workers = self._resolve_num_workers(8)
        print(
            f">>> DataLoader config: Batch Size={batch_size}, Accum Steps={accum_steps}, Workers={workers}")
        sampler = None
        if dist.is_initialized():
            sampler = DistributedSampler(dataset, shuffle=True)
            shuffle = False  # 交由 DistributedSampler 完成随机打乱
        else:
            shuffle = True

        persistent = workers > 0
        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            sampler=sampler,
            num_workers=workers,
            pin_memory=(self._device_type() == 'cuda'),
            persistent_workers=persistent,
        )
        return dataloader, accum_steps

    def _build_val_dataloader(self, dataset, train_dataloader, accum_steps):
        val_bs = accum_steps * train_dataloader.batch_size
        val_workers = self._resolve_num_workers(4)
        return DataLoader(
            dataset,
            batch_size=val_bs,
            shuffle=False,
            num_workers=val_workers,
            pin_memory=(self._device_type() == 'cuda'),
            persistent_workers=val_workers > 0,
        )

    def _compute_losses(self, y_pred, y_true, apply_softplus: bool = False):
        task = getattr(self, "task_type", "regression")
        if task == 'classification':
            loss_fn = nn.BCEWithLogitsLoss(reduction='none')
            return loss_fn(y_pred, y_true).view(-1)
        if apply_softplus:
            y_pred = F.softplus(y_pred)
        y_pred = torch.clamp(y_pred, min=1e-6)
        power = getattr(self, "tw_power", 1.5)
        return tweedie_loss(y_pred, y_true, p=power).view(-1)

    def _compute_weighted_loss(self, y_pred, y_true, weights, apply_softplus: bool = False):
        losses = self._compute_losses(
            y_pred, y_true, apply_softplus=apply_softplus)
        weighted_loss = (losses * weights.view(-1)).sum() / \
            torch.clamp(weights.sum(), min=EPS)
        return weighted_loss

    def _early_stop_update(self, val_loss, best_loss, best_state, patience_counter, model,
                           ignore_keys: Optional[List[str]] = None):
        if val_loss < best_loss:
            ignore_keys = ignore_keys or []
            state_dict = {
                k: (v.clone() if isinstance(v, torch.Tensor) else copy.deepcopy(v))
                for k, v in model.state_dict().items()
                if not any(k.startswith(ignore_key) for ignore_key in ignore_keys)
            }
            return val_loss, state_dict, 0, False
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
                     trial: Optional[optuna.trial.Trial] = None,
                     loss_curve_path: Optional[str] = None):
        device_type = self._device_type()
        best_loss = float('inf')
        best_state = None
        patience_counter = 0
        stop_training = False
        train_history: List[float] = []
        val_history: List[float] = []

        is_ddp_model = isinstance(model, DDP)

        for epoch in range(1, getattr(self, "epochs", 1) + 1):
            epoch_start_ts = time.time()
            val_weighted_loss = None
            if hasattr(self, 'dataloader_sampler') and self.dataloader_sampler is not None:
                self.dataloader_sampler.set_epoch(epoch)

            model.train()
            optimizer.zero_grad()

            epoch_loss_sum = 0.0
            epoch_weight_sum = 0.0
            for step, batch in enumerate(dataloader):
                is_update_step = ((step + 1) % accum_steps == 0) or \
                    ((step + 1) == len(dataloader))
                sync_cm = model.no_sync if (
                    is_ddp_model and not is_update_step) else nullcontext

                with sync_cm():
                    with autocast(enabled=(device_type == 'cuda')):
                        y_pred, y_true, w = forward_fn(batch)
                        weighted_loss = self._compute_weighted_loss(
                            y_pred, y_true, w, apply_softplus=apply_softplus)
                        loss_for_backward = weighted_loss / accum_steps

                    batch_weight = torch.clamp(w.sum(), min=EPS).item()
                    epoch_loss_sum += float(weighted_loss.item()
                                            * batch_weight)
                    epoch_weight_sum += float(batch_weight)
                    scaler.scale(loss_for_backward).backward()

                if is_update_step:
                    if clip_fn is not None:
                        clip_fn()
                    scaler.step(optimizer)
                    scaler.update()
                    optimizer.zero_grad()

            train_epoch_loss = epoch_loss_sum / max(epoch_weight_sum, EPS)
            train_history.append(float(train_epoch_loss))

            if val_forward_fn is not None:
                should_compute_val = (not dist.is_initialized()
                                      or DistributedUtils.is_main_process())
                val_device = getattr(self, "device", torch.device("cpu"))
                if not isinstance(val_device, torch.device):
                    val_device = torch.device(val_device)
                loss_tensor_device = val_device if device_type == 'cuda' else torch.device(
                    "cpu")
                val_loss_tensor = torch.zeros(1, device=loss_tensor_device)

                if should_compute_val:
                    model.eval()
                    with torch.no_grad(), autocast(enabled=(device_type == 'cuda')):
                        val_result = val_forward_fn()
                        if isinstance(val_result, tuple) and len(val_result) == 3:
                            y_val_pred, y_val_true, w_val = val_result
                            val_weighted_loss = self._compute_weighted_loss(
                                y_val_pred, y_val_true, w_val, apply_softplus=apply_softplus)
                        else:
                            val_weighted_loss = val_result
                    val_loss_tensor[0] = float(val_weighted_loss)

                if dist.is_initialized():
                    dist.broadcast(val_loss_tensor, src=0)
                val_weighted_loss = float(val_loss_tensor.item())

                val_history.append(val_weighted_loss)

                best_loss, best_state, patience_counter, stop_training = self._early_stop_update(
                    val_weighted_loss, best_loss, best_state, patience_counter, model)

                prune_flag = False
                is_main_rank = DistributedUtils.is_main_process()
                if trial is not None and (not dist.is_initialized() or is_main_rank):
                    trial.report(val_weighted_loss, epoch)
                    prune_flag = trial.should_prune()

                if dist.is_initialized():
                    prune_device = getattr(self, "device", torch.device("cpu"))
                    if not isinstance(prune_device, torch.device):
                        prune_device = torch.device(prune_device)
                    prune_tensor = torch.zeros(1, device=prune_device)
                    if is_main_rank:
                        prune_tensor.fill_(1 if prune_flag else 0)
                    dist.broadcast(prune_tensor, src=0)
                    prune_flag = bool(prune_tensor.item())

                if prune_flag:
                    raise optuna.TrialPruned()

                if stop_training:
                    break

            should_log_epoch = (not dist.is_initialized()
                                or DistributedUtils.is_main_process())
            if should_log_epoch:
                elapsed = int(time.time() - epoch_start_ts)
                if val_weighted_loss is None:
                    print(
                        f"[Training] Epoch {epoch}/{getattr(self, 'epochs', 1)} "
                        f"train_loss={float(train_epoch_loss):.6f} elapsed={elapsed}s",
                        flush=True,
                    )
                else:
                    print(
                        f"[Training] Epoch {epoch}/{getattr(self, 'epochs', 1)} "
                        f"train_loss={float(train_epoch_loss):.6f} "
                        f"val_loss={float(val_weighted_loss):.6f} elapsed={elapsed}s",
                        flush=True,
                    )

        history = {"train": train_history, "val": val_history}
        self._plot_loss_curve(history, loss_curve_path)
        return best_state, history

    def _plot_loss_curve(self, history: Dict[str, List[float]], save_path: Optional[str]) -> None:
        if not save_path:
            return
        if dist.is_initialized() and not DistributedUtils.is_main_process():
            return
        train_hist = history.get("train", []) if history else []
        val_hist = history.get("val", []) if history else []
        if not train_hist and not val_hist:
            return
        ensure_parent_dir(save_path)
        epochs = range(1, max(len(train_hist), len(val_hist)) + 1)
        fig = plt.figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        if train_hist:
            ax.plot(range(1, len(train_hist) + 1), train_hist,
                    label='Train Loss', color='tab:blue')
        if val_hist:
            ax.plot(range(1, len(val_hist) + 1), val_hist,
                    label='Validation Loss', color='tab:orange')
        ax.set_xlabel('Epoch')
        ax.set_ylabel('Weighted Loss')
        ax.set_title('Loss vs. Epoch')
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.legend()
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close(fig)
        print(f"[Training] Loss curve saved to {save_path}")


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
        # 如需在第二层后追加归一化，可启用下行：self.norm2 = Norm(dim)
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
        # 若启用了第二次归一化，在此处调用：out = self.norm2(out)
        out = self.fc2(out)
        # 残差缩放再相加
        return x + self.res_scale * out

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

        # 如需在首层后增加显式归一化，可按需启用下方示例代码：
        # 如果使用 LayerNorm：
        #     self.net.add_module('norm1', nn.LayerNorm(hidden_dim))
        # 否则可改用 BatchNorm：
        #     self.net.add_module('norm1', nn.BatchNorm1d(hidden_dim))

        # 如果希望在残差块前加入 ReLU，可启用：self.net.add_module('relu1', nn.ReLU(inplace=True))

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
        self.loss_curve_path: Optional[str] = None
        self.training_history: Dict[str, List[float]] = {
            "train": [], "val": []}

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
            base_bs_gpu=(2048, 1024, 512),
            base_bs_cpu=(256, 128),
            min_bs=64,
            target_effective_cuda=2048,
            target_effective_cpu=1024
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
            val_dataloader = self._build_val_dataloader(
                val_dataset, dataloader, accum_steps)
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
                losses = self._compute_losses(
                    y_pred, y_b, apply_softplus=False)

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

        best_state, history = self._train_model(
            self.resnet,
            dataloader,
            accum_steps,
            self.optimizer,
            self.scaler,
            forward_fn,
            val_forward_fn if has_val else None,
            apply_softplus=False,
            clip_fn=clip_fn,
            trial=trial,
            loss_curve_path=getattr(self, "loss_curve_path", None)
        )

        if has_val and best_state is not None:
            self.resnet.load_state_dict(best_state)
        self.training_history = history

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
    """将数值/类别/地理 token 统一映射为 Transformer 输入 tokens。"""

    def __init__(self, num_numeric: int, cat_cardinalities, d_model: int, num_geo: int = 0):
        super().__init__()

        self.num_numeric = num_numeric
        self.has_numeric = num_numeric > 0
        self.num_geo = num_geo
        self.has_geo = num_geo > 0

        if self.has_numeric:
            self.num_linear = nn.Linear(num_numeric, d_model)

        self.embeddings = nn.ModuleList([
            nn.Embedding(card, d_model) for card in cat_cardinalities
        ])

        if self.has_geo:
            # 地理 token 直接线性映射，避免对原始字符串做 one-hot；上游已编码/标准化
            self.geo_linear = nn.Linear(num_geo, d_model)

    def forward(self, X_num, X_cat, X_geo=None):
        tokens = []

        if self.has_numeric:
            num_token = self.num_linear(X_num)
            tokens.append(num_token)

        for i, emb in enumerate(self.embeddings):
            tok = emb(X_cat[:, i])
            tokens.append(tok)

        if self.has_geo:
            if X_geo is None:
                raise RuntimeError("启用了地理 token，但未提供 X_geo。")
            geo_token = self.geo_linear(X_geo)
            tokens.append(geo_token)

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
        # 如果偏好 ReLU，可将激活函数改为：self.activation = nn.ReLU()
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
                 task_type: str = 'regression', num_geo: int = 0
                 ):
        super().__init__()

        self.num_numeric = int(num_numeric)
        self.cat_cardinalities = list(cat_cardinalities or [])

        self.tokenizer = FeatureTokenizer(
            num_numeric=num_numeric,
            cat_cardinalities=cat_cardinalities,
            d_model=d_model,
            num_geo=num_geo
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
            # 如需更深的输出头，可按需启用下方示例层：
            # nn.LayerNorm(d_model),  # 额外的归一化层
            # nn.Linear(d_model, d_model),  # 额外的全连接层
            # nn.GELU(),  # 对应的激活层
            nn.Linear(d_model, 1),
        ]

        if task_type == 'classification':
            # 分类任务输出 logits，与 BCEWithLogitsLoss 更匹配
            layers.append(nn.Identity())
        else:
            # 回归任务需保持正值，适配 Tweedie/Gamma
            layers.append(nn.Softplus())

        self.head = nn.Sequential(*layers)

        # ---- 自监督重建头（masked modeling） ----
        self.num_recon_head = nn.Linear(
            d_model, self.num_numeric) if self.num_numeric > 0 else None
        self.cat_recon_heads = nn.ModuleList([
            nn.Linear(d_model, int(card)) for card in self.cat_cardinalities
        ])

    def forward(
            self,
            X_num,
            X_cat,
            X_geo=None,
            return_embedding: bool = False,
            return_reconstruction: bool = False):

        # 输入：
        #   X_num -> (batch, 数值特征数) 的 float32 张量
        #   X_cat -> (batch, 类别特征数) 的 long 张量
        #   X_geo -> (batch, 地理 token 维度) 的 float32 张量

        if self.training and not hasattr(self, '_printed_device'):
            print(f">>> FTTransformerCore executing on device: {X_num.device}")
            self._printed_device = True

        # => 张量形状 (batch, token_num, d_model)
        tokens = self.tokenizer(X_num, X_cat, X_geo)
        # => 张量形状 (batch, token_num, d_model)
        x = self.encoder(tokens)

        # 对 token 做平均池化，再送入回归头
        x = x.mean(dim=1)                      # => 张量形状 (batch, d_model)

        if return_reconstruction:
            num_pred, cat_logits = self.reconstruct(x)
            cat_logits_out = tuple(
                cat_logits) if cat_logits is not None else tuple()
            if return_embedding:
                return x, num_pred, cat_logits_out
            return num_pred, cat_logits_out

        if return_embedding:
            return x

        # => 张量形状 (batch, 1)，Softplus 约束为正
        out = self.head(x)
        return out

    def reconstruct(self, embedding: torch.Tensor) -> Tuple[Optional[torch.Tensor], List[torch.Tensor]]:
        """给定池化后的 embedding（batch, d_model），重建数值/类别输入。"""
        num_pred = self.num_recon_head(
            embedding) if self.num_recon_head is not None else None
        cat_logits = [head(embedding) for head in self.cat_recon_heads]
        return num_pred, cat_logits

# 定义TabularDataset类


class TabularDataset(Dataset):
    def __init__(self, X_num, X_cat, X_geo, y, w):

        # 输入张量说明：
        #   X_num: torch.float32，shape=(N, 数值特征数)
        #   X_cat: torch.long，  shape=(N, 类别特征数)
        #   X_geo: torch.float32，shape=(N, 地理 token 维度)，可为空张量
        #   y:     torch.float32，形状=(N, 1)
        #   w:     torch.float32，形状=(N, 1)

        self.X_num = X_num
        self.X_cat = X_cat
        self.X_geo = X_geo
        self.y = y
        self.w = w

    def __len__(self):
        return self.y.shape[0]

    def __getitem__(self, idx):
        return (
            self.X_num[idx],
            self.X_cat[idx],
            self.X_geo[idx],
            self.y[idx],
            self.w[idx],
        )


class MaskedTabularDataset(Dataset):
    def __init__(self,
                 X_num_masked: torch.Tensor,
                 X_cat_masked: torch.Tensor,
                 X_geo: torch.Tensor,
                 X_num_true: Optional[torch.Tensor],
                 num_mask: Optional[torch.Tensor],
                 X_cat_true: Optional[torch.Tensor],
                 cat_mask: Optional[torch.Tensor]):
        self.X_num_masked = X_num_masked
        self.X_cat_masked = X_cat_masked
        self.X_geo = X_geo
        self.X_num_true = X_num_true
        self.num_mask = num_mask
        self.X_cat_true = X_cat_true
        self.cat_mask = cat_mask

    def __len__(self):
        return self.X_num_masked.shape[0]

    def __getitem__(self, idx):
        return (
            self.X_num_masked[idx],
            self.X_cat_masked[idx],
            self.X_geo[idx],
            None if self.X_num_true is None else self.X_num_true[idx],
            None if self.num_mask is None else self.num_mask[idx],
            None if self.X_cat_true is None else self.X_cat_true[idx],
            None if self.cat_mask is None else self.cat_mask[idx],
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
        self._num_mean = None
        self._num_std = None
        self.ft = None
        self.use_data_parallel = torch.cuda.device_count() > 1 and use_data_parallel
        self.num_geo = 0
        self._geo_params: Dict[str, Any] = {}
        self.loss_curve_path: Optional[str] = None
        self.training_history: Dict[str, List[float]] = {
            "train": [], "val": []}

    def _build_model(self, X_train):
        num_numeric = len(self.num_cols)
        cat_cardinalities = []

        if num_numeric > 0:
            num_arr = X_train[self.num_cols].to_numpy(
                dtype=np.float32, copy=False)
            num_arr = np.nan_to_num(num_arr, nan=0.0, posinf=0.0, neginf=0.0)
            mean = num_arr.mean(axis=0).astype(np.float32, copy=False)
            std = num_arr.std(axis=0).astype(np.float32, copy=False)
            std = np.where(std < 1e-6, 1.0, std).astype(np.float32, copy=False)
            self._num_mean = mean
            self._num_std = std
        else:
            self._num_mean = None
            self._num_std = None

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
            task_type=self.task_type,
            num_geo=self.num_geo
        )
        if self.is_ddp_enabled:
            core = core.to(self.device)
            core = DDP(core, device_ids=[
                       self.local_rank], output_device=self.local_rank, find_unused_parameters=True)
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

    def _build_train_tensors(self, X_train, y_train, w_train, geo_train=None):
        return self._tensorize_split(X_train, y_train, w_train, geo_tokens=geo_train)

    def _build_val_tensors(self, X_val, y_val, w_val, geo_val=None):
        return self._tensorize_split(X_val, y_val, w_val, geo_tokens=geo_val, allow_none=True)

    def _tensorize_split(self, X, y, w, geo_tokens=None, allow_none: bool = False):
        if X is None:
            if allow_none:
                return None, None, None, None, None, False
            raise ValueError("输入特征 X 不能为空。")

        num_np = X[self.num_cols].to_numpy(dtype=np.float32, copy=True)
        num_np = np.nan_to_num(num_np, nan=0.0, posinf=0.0, neginf=0.0)
        if self._num_mean is not None and self._num_std is not None and num_np.size:
            num_np = (num_np - self._num_mean) / self._num_std
        X_num = torch.tensor(num_np, dtype=torch.float32)
        if self.cat_cols:
            X_cat = torch.tensor(self._encode_cats(X), dtype=torch.long)
        else:
            X_cat = torch.zeros((X_num.shape[0], 0), dtype=torch.long)

        if geo_tokens is not None:
            geo_np = np.asarray(geo_tokens, dtype=np.float32)
            if geo_np.ndim == 1:
                geo_np = geo_np.reshape(-1, 1)
        elif self.num_geo > 0:
            raise RuntimeError("geo_tokens 不能为空，请先准备好地理 token。")
        else:
            geo_np = np.zeros((X_num.shape[0], 0), dtype=np.float32)
        X_geo = torch.tensor(geo_np, dtype=torch.float32)

        y_tensor = torch.tensor(
            y.values, dtype=torch.float32).view(-1, 1) if y is not None else None
        if y_tensor is None:
            w_tensor = None
        elif w is not None:
            w_tensor = torch.tensor(
                w.values, dtype=torch.float32).view(-1, 1)
        else:
            w_tensor = torch.ones_like(y_tensor)
        return X_num, X_cat, X_geo, y_tensor, w_tensor, y is not None

    def fit(self, X_train, y_train, w_train=None,
            X_val=None, y_val=None, w_val=None, trial=None,
            geo_train=None, geo_val=None):

        # 首次拟合时需要构建底层模型结构
        self.num_geo = geo_train.shape[1] if geo_train is not None else 0
        if self.ft is None:
            self._build_model(X_train)

        X_num_train, X_cat_train, X_geo_train, y_tensor, w_tensor, _ = self._build_train_tensors(
            X_train, y_train, w_train, geo_train=geo_train)
        X_num_val, X_cat_val, X_geo_val, y_val_tensor, w_val_tensor, has_val = self._build_val_tensors(
            X_val, y_val, w_val, geo_val=geo_val)

        # --- 构建 DataLoader ---
        dataset = TabularDataset(
            X_num_train, X_cat_train, X_geo_train, y_tensor, w_tensor
        )

        dataloader, accum_steps = self._build_dataloader(
            dataset,
            N=X_num_train.shape[0],
            base_bs_gpu=(2048, 1024, 512),
            base_bs_cpu=(256, 128),
            min_bs=64,
            target_effective_cuda=2048,
            target_effective_cpu=1024
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
                X_num_val, X_cat_val, X_geo_val, y_val_tensor, w_val_tensor
            )
            val_dataloader = self._build_val_dataloader(
                val_dataset, dataloader, accum_steps)

        is_data_parallel = isinstance(self.ft, nn.DataParallel)

        def forward_fn(batch):
            X_num_b, X_cat_b, X_geo_b, y_b, w_b = batch

            if not is_data_parallel:
                X_num_b = X_num_b.to(self.device, non_blocking=True)
                X_cat_b = X_cat_b.to(self.device, non_blocking=True)
                X_geo_b = X_geo_b.to(self.device, non_blocking=True)
            y_b = y_b.to(self.device, non_blocking=True)
            w_b = w_b.to(self.device, non_blocking=True)

            y_pred = self.ft(X_num_b, X_cat_b, X_geo_b)
            return y_pred, y_b, w_b

        def val_forward_fn():
            total_loss = 0.0
            total_weight = 0.0
            for batch in val_dataloader:
                X_num_b, X_cat_b, X_geo_b, y_b, w_b = batch
                if not is_data_parallel:
                    X_num_b = X_num_b.to(self.device, non_blocking=True)
                    X_cat_b = X_cat_b.to(self.device, non_blocking=True)
                    X_geo_b = X_geo_b.to(self.device, non_blocking=True)
                y_b = y_b.to(self.device, non_blocking=True)
                w_b = w_b.to(self.device, non_blocking=True)

                y_pred = self.ft(X_num_b, X_cat_b, X_geo_b)

                # 手动计算验证损失
                losses = self._compute_losses(
                    y_pred, y_b, apply_softplus=False)

                batch_weight_sum = torch.clamp(w_b.sum(), min=EPS)
                batch_weighted_loss_sum = (losses * w_b.view(-1)).sum()

                total_loss += batch_weighted_loss_sum.item()
                total_weight += batch_weight_sum.item()

            return total_loss / max(total_weight, EPS)

        clip_fn = None
        if self.device.type == 'cuda':
            def clip_fn(): return (scaler.unscale_(optimizer),
                                   clip_grad_norm_(self.ft.parameters(), max_norm=1.0))

        best_state, history = self._train_model(
            self.ft,
            dataloader,
            accum_steps,
            optimizer,
            scaler,
            forward_fn,
            val_forward_fn if has_val else None,
            apply_softplus=False,
            clip_fn=clip_fn,
            trial=trial,
            loss_curve_path=getattr(self, "loss_curve_path", None)
        )

        if has_val and best_state is not None:
            self.ft.load_state_dict(best_state)
        self.training_history = history

    def fit_unsupervised(self,
                         X_train,
                         X_val=None,
                         trial: Optional[optuna.trial.Trial] = None,
                         geo_train=None,
                         geo_val=None,
                         mask_prob_num: float = 0.15,
                         mask_prob_cat: float = 0.15,
                         num_loss_weight: float = 1.0,
                         cat_loss_weight: float = 1.0) -> float:
        """通过 masked 重建进行自监督预训练（支持原始字符串的类别特征）。"""
        self.num_geo = geo_train.shape[1] if geo_train is not None else 0
        if self.ft is None:
            self._build_model(X_train)

        X_num, X_cat, X_geo, _, _, _ = self._tensorize_split(
            X_train, None, None, geo_tokens=geo_train, allow_none=True)
        has_val = X_val is not None
        if has_val:
            X_num_val, X_cat_val, X_geo_val, _, _, _ = self._tensorize_split(
                X_val, None, None, geo_tokens=geo_val, allow_none=True)
        else:
            X_num_val = X_cat_val = X_geo_val = None

        N = int(X_num.shape[0])
        num_dim = int(X_num.shape[1])
        cat_dim = int(X_cat.shape[1])
        device_type = self._device_type()

        gen = torch.Generator()
        gen.manual_seed(13 + int(getattr(self, "rank", 0)))

        base_model = self.ft.module if hasattr(self.ft, "module") else self.ft
        cardinals = getattr(base_model, "cat_cardinalities", None) or []
        unknown_idx = torch.tensor(
            [int(c) - 1 for c in cardinals], dtype=torch.long).view(1, -1)

        means = None
        if num_dim > 0:
            # 让“mask 后填充值”的数值尺度与模型真实输入保持一致（可能会在 _tensorize_split 中做归一化）。
            means = X_num.to(dtype=torch.float32).mean(dim=0, keepdim=True)

        def _mask_inputs(X_num_in: torch.Tensor,
                         X_cat_in: torch.Tensor,
                         generator: torch.Generator):
            n_rows = int(X_num_in.shape[0])
            num_mask_local = None
            cat_mask_local = None
            X_num_masked_local = X_num_in
            X_cat_masked_local = X_cat_in
            if num_dim > 0:
                num_mask_local = (torch.rand(
                    (n_rows, num_dim), generator=generator) < float(mask_prob_num))
                X_num_masked_local = X_num_in.clone()
                if num_mask_local.any():
                    X_num_masked_local[num_mask_local] = means.expand_as(
                        X_num_masked_local)[num_mask_local]
            if cat_dim > 0:
                cat_mask_local = (torch.rand(
                    (n_rows, cat_dim), generator=generator) < float(mask_prob_cat))
                X_cat_masked_local = X_cat_in.clone()
                if cat_mask_local.any():
                    X_cat_masked_local[cat_mask_local] = unknown_idx.expand_as(
                        X_cat_masked_local)[cat_mask_local]
            return X_num_masked_local, X_cat_masked_local, num_mask_local, cat_mask_local

        X_num_true = X_num.clone() if num_dim > 0 else None
        X_cat_true = X_cat.clone() if cat_dim > 0 else None
        X_num_masked, X_cat_masked, num_mask, cat_mask = _mask_inputs(
            X_num, X_cat, gen)

        X_cat_true = X_cat.clone() if cat_dim > 0 else None
        dataset = MaskedTabularDataset(
            X_num_masked, X_cat_masked, X_geo,
            X_num_true, num_mask,
            X_cat_true, cat_mask
        )
        dataloader, accum_steps = self._build_dataloader(
            dataset,
            N=N,
            base_bs_gpu=(2048, 1024, 512),
            base_bs_cpu=(256, 128),
            min_bs=64,
            target_effective_cuda=2048,
            target_effective_cpu=1024
        )
        if self.is_ddp_enabled and hasattr(dataloader.sampler, 'set_epoch'):
            self.dataloader_sampler = dataloader.sampler
        else:
            self.dataloader_sampler = None

        optimizer = torch.optim.Adam(
            self.ft.parameters(), lr=self.learning_rate)
        scaler = GradScaler(enabled=(device_type == 'cuda'))

        def _batch_recon_loss(num_pred, cat_logits, num_true_b, num_mask_b, cat_true_b, cat_mask_b, device):
            loss = torch.zeros((), device=device, dtype=torch.float32)

            if num_pred is not None and num_true_b is not None and num_mask_b is not None:
                num_mask_b = num_mask_b.to(dtype=torch.bool)
                if num_mask_b.any():
                    diff = num_pred - num_true_b
                    mse = diff * diff
                    loss = loss + float(num_loss_weight) * \
                        mse[num_mask_b].mean()

            if cat_logits and cat_true_b is not None and cat_mask_b is not None:
                cat_mask_b = cat_mask_b.to(dtype=torch.bool)
                cat_losses: List[torch.Tensor] = []
                for j, logits in enumerate(cat_logits):
                    mask_j = cat_mask_b[:, j]
                    if not mask_j.any():
                        continue
                    targets = cat_true_b[:, j]
                    cat_losses.append(
                        F.cross_entropy(logits, targets, reduction='none')[
                            mask_j].mean()
                    )
                if cat_losses:
                    loss = loss + float(cat_loss_weight) * \
                        torch.stack(cat_losses).mean()
            return loss

        train_history: List[float] = []
        val_history: List[float] = []
        best_loss = float("inf")
        best_state = None
        patience_counter = 0
        is_ddp_model = isinstance(self.ft, DDP)

        clip_fn = None
        if self.device.type == 'cuda':
            def clip_fn(): return (scaler.unscale_(optimizer),
                                   clip_grad_norm_(self.ft.parameters(), max_norm=1.0))

        for epoch in range(1, int(self.epochs) + 1):
            if self.dataloader_sampler is not None:
                self.dataloader_sampler.set_epoch(epoch)

            self.ft.train()
            optimizer.zero_grad()
            epoch_loss_sum = 0.0
            epoch_count = 0.0

            for step, batch in enumerate(dataloader):
                is_update_step = ((step + 1) % accum_steps == 0) or \
                    ((step + 1) == len(dataloader))
                sync_cm = self.ft.no_sync if (
                    is_ddp_model and not is_update_step) else nullcontext
                with sync_cm():
                    with autocast(enabled=(device_type == 'cuda')):
                        X_num_b, X_cat_b, X_geo_b, num_true_b, num_mask_b, cat_true_b, cat_mask_b = batch
                        X_num_b = X_num_b.to(self.device, non_blocking=True)
                        X_cat_b = X_cat_b.to(self.device, non_blocking=True)
                        X_geo_b = X_geo_b.to(self.device, non_blocking=True)
                        num_true_b = None if num_true_b is None else num_true_b.to(
                            self.device, non_blocking=True)
                        num_mask_b = None if num_mask_b is None else num_mask_b.to(
                            self.device, non_blocking=True)
                        cat_true_b = None if cat_true_b is None else cat_true_b.to(
                            self.device, non_blocking=True)
                        cat_mask_b = None if cat_mask_b is None else cat_mask_b.to(
                            self.device, non_blocking=True)

                        num_pred, cat_logits = self.ft(
                            X_num_b, X_cat_b, X_geo_b, return_reconstruction=True)
                        batch_loss = _batch_recon_loss(
                            num_pred, cat_logits, num_true_b, num_mask_b, cat_true_b, cat_mask_b, device=X_num_b.device)
                        if not torch.isfinite(batch_loss):
                            msg = (
                                f"[FTTransformerSklearn.fit_unsupervised] non-finite loss "
                                f"(epoch={epoch}, step={step}, loss={batch_loss.detach().item()})"
                            )
                            print(msg)
                            print(
                                f"  X_num: finite={bool(torch.isfinite(X_num_b).all())} "
                                f"min={float(X_num_b.min().detach().cpu()) if X_num_b.numel() else 0.0:.3g} "
                                f"max={float(X_num_b.max().detach().cpu()) if X_num_b.numel() else 0.0:.3g}"
                            )
                            if X_geo_b is not None:
                                print(
                                    f"  X_geo: finite={bool(torch.isfinite(X_geo_b).all())} "
                                    f"min={float(X_geo_b.min().detach().cpu()) if X_geo_b.numel() else 0.0:.3g} "
                                    f"max={float(X_geo_b.max().detach().cpu()) if X_geo_b.numel() else 0.0:.3g}"
                                )
                            if trial is not None:
                                raise optuna.TrialPruned(msg)
                            raise RuntimeError(msg)
                        loss_for_backward = batch_loss / float(accum_steps)
                    scaler.scale(loss_for_backward).backward()

                if is_update_step:
                    if clip_fn is not None:
                        clip_fn()
                    scaler.step(optimizer)
                    scaler.update()
                    optimizer.zero_grad()

                epoch_loss_sum += float(batch_loss.detach().item()) * \
                    float(X_num_b.shape[0])
                epoch_count += float(X_num_b.shape[0])

            train_history.append(epoch_loss_sum / max(epoch_count, 1.0))

            if has_val and X_num_val is not None and X_cat_val is not None and X_geo_val is not None:
                should_compute_val = (not dist.is_initialized()
                                      or DistributedUtils.is_main_process())
                loss_tensor_device = self.device if device_type == 'cuda' else torch.device(
                    "cpu")
                val_loss_tensor = torch.zeros(1, device=loss_tensor_device)

                if should_compute_val:
                    self.ft.eval()
                    with torch.no_grad(), autocast(enabled=(device_type == 'cuda')):
                        val_bs = min(
                            int(dataloader.batch_size * max(1, accum_steps)), int(X_num_val.shape[0]))
                        total_val = 0.0
                        total_n = 0.0
                        for start in range(0, int(X_num_val.shape[0]), max(1, val_bs)):
                            end = min(
                                int(X_num_val.shape[0]), start + max(1, val_bs))
                            X_num_v_true_cpu = X_num_val[start:end]
                            X_cat_v_true_cpu = X_cat_val[start:end]
                            X_geo_v = X_geo_val[start:end].to(
                                self.device, non_blocking=True)
                            gen_val = torch.Generator()
                            gen_val.manual_seed(10_000 + epoch + start)
                            X_num_v_cpu, X_cat_v_cpu, val_num_mask, val_cat_mask = _mask_inputs(
                                X_num_v_true_cpu, X_cat_v_true_cpu, gen_val)
                            X_num_v_true = X_num_v_true_cpu.to(
                                self.device, non_blocking=True)
                            X_cat_v_true = X_cat_v_true_cpu.to(
                                self.device, non_blocking=True)
                            X_num_v = X_num_v_cpu.to(
                                self.device, non_blocking=True)
                            X_cat_v = X_cat_v_cpu.to(
                                self.device, non_blocking=True)
                            val_num_mask = None if val_num_mask is None else val_num_mask.to(
                                self.device, non_blocking=True)
                            val_cat_mask = None if val_cat_mask is None else val_cat_mask.to(
                                self.device, non_blocking=True)
                            num_pred_v, cat_logits_v = self.ft(
                                X_num_v, X_cat_v, X_geo_v, return_reconstruction=True)
                            loss_v = _batch_recon_loss(
                                num_pred_v, cat_logits_v,
                                X_num_v_true if X_num_v_true.numel() else None, val_num_mask,
                                X_cat_v_true if X_cat_v_true.numel() else None, val_cat_mask,
                                device=X_num_v.device
                            )
                            if not torch.isfinite(loss_v):
                                total_val = float("inf")
                                total_n = 1.0
                                break
                            total_val += float(loss_v.detach().item()
                                               ) * float(end - start)
                            total_n += float(end - start)
                    val_loss_tensor[0] = total_val / max(total_n, 1.0)

                if dist.is_initialized():
                    dist.broadcast(val_loss_tensor, src=0)
                val_loss_value = float(val_loss_tensor.item())
                if not np.isfinite(val_loss_value):
                    msg = (
                        f"[FTTransformerSklearn.fit_unsupervised] non-finite val loss "
                        f"(epoch={epoch}, val_loss={val_loss_value})"
                    )
                    if trial is not None and (not dist.is_initialized() or DistributedUtils.is_main_process()):
                        raise optuna.TrialPruned(msg)
                    raise RuntimeError(msg)
                val_history.append(val_loss_value)

                if val_loss_value < best_loss:
                    best_loss = val_loss_value
                    best_state = {
                        k: (v.clone() if isinstance(
                            v, torch.Tensor) else copy.deepcopy(v))
                        for k, v in self.ft.state_dict().items()
                    }
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if best_state is not None and patience_counter >= int(self.patience):
                        break

                if trial is not None and (not dist.is_initialized() or DistributedUtils.is_main_process()):
                    trial.report(val_loss_value, epoch)
                    if trial.should_prune():
                        raise optuna.TrialPruned()

        self.training_history = {"train": train_history, "val": val_history}
        self._plot_loss_curve(self.training_history, getattr(
            self, "loss_curve_path", None))
        if has_val and best_state is not None:
            self.ft.load_state_dict(best_state)
        return float(best_loss if has_val else (train_history[-1] if train_history else 0.0))

    def predict(self, X_test, geo_tokens=None, batch_size: Optional[int] = None, return_embedding: bool = False):
        # X_test 需要包含所有数值列与类别列；geo_tokens 为可选的地理 token

        self.ft.eval()
        X_num, X_cat, X_geo, _, _, _ = self._tensorize_split(
            X_test, None, None, geo_tokens=geo_tokens, allow_none=True)

        num_rows = X_num.shape[0]
        if num_rows == 0:
            return np.empty(0, dtype=np.float32)

        device = self.device if isinstance(
            self.device, torch.device) else torch.device(self.device)

        def resolve_batch_size(n_rows: int) -> int:
            if batch_size is not None:
                return max(1, min(int(batch_size), n_rows))
            # 依据模型规模估算安全批量，防止多头注意力在推理阶段拉满显存
            token_cnt = len(self.num_cols) + len(self.cat_cols)
            if self.num_geo > 0:
                token_cnt += 1
            approx_units = max(1, token_cnt * max(1, self.d_model))
            if device.type == 'cuda':
                if approx_units >= 8192:
                    base = 512
                elif approx_units >= 4096:
                    base = 1024
                else:
                    base = 2048
            else:
                base = 512
            return max(1, min(base, n_rows))

        eff_batch = resolve_batch_size(num_rows)
        preds: List[torch.Tensor] = []

        with torch.no_grad():
            for start in range(0, num_rows, eff_batch):
                end = min(num_rows, start + eff_batch)
                X_num_b = X_num[start:end].to(device, non_blocking=True)
                X_cat_b = X_cat[start:end].to(device, non_blocking=True)
                X_geo_b = X_geo[start:end].to(device, non_blocking=True)
                pred_chunk = self.ft(
                    X_num_b, X_cat_b, X_geo_b, return_embedding=return_embedding)
                preds.append(pred_chunk.cpu())

        y_pred = torch.cat(preds, dim=0).numpy()

        if return_embedding:
            return y_pred

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


# =============================================================================
# 图神经网络 (GNN) 简化实现
# =============================================================================


class SimpleGraphLayer(nn.Module):
    def __init__(self, in_dim: int, out_dim: int, dropout: float = 0.1):
        super().__init__()
        self.linear = nn.Linear(in_dim, out_dim)
        self.activation = nn.ReLU(inplace=True)
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        # 基于归一化稀疏邻接矩阵的消息传递：A_hat * X * W
        h = torch.sparse.mm(adj, x)
        h = self.linear(h)
        h = self.activation(h)
        return self.dropout(h)


class SimpleGNN(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 64, num_layers: int = 2,
                 dropout: float = 0.1, task_type: str = 'regression'):
        super().__init__()
        layers = []
        dim_in = input_dim
        for _ in range(max(1, num_layers)):
            layers.append(SimpleGraphLayer(
                dim_in, hidden_dim, dropout=dropout))
            dim_in = hidden_dim
        self.layers = nn.ModuleList(layers)
        self.output = nn.Linear(hidden_dim, 1)
        if task_type == 'classification':
            self.output_act = nn.Identity()
        else:
            self.output_act = nn.Softplus()
        self.task_type = task_type
        # 用 buffer 保持邻接矩阵，便于 DataParallel 复制
        self.register_buffer("adj_buffer", torch.empty(0))

    def forward(self, x: torch.Tensor, adj: Optional[torch.Tensor] = None) -> torch.Tensor:
        adj_used = adj if adj is not None else getattr(
            self, "adj_buffer", None)
        if adj_used is None or adj_used.numel() == 0:
            raise RuntimeError("Adjacency is not set for GNN forward.")
        h = x
        for layer in self.layers:
            h = layer(h, adj_used)
        h = torch.sparse.mm(adj_used, h)
        out = self.output(h)
        return self.output_act(out)


class GraphNeuralNetSklearn(TorchTrainerMixin, nn.Module):
    def __init__(self, model_nme: str, input_dim: int, hidden_dim: int = 64,
                 num_layers: int = 2, k_neighbors: int = 10, dropout: float = 0.1,
                 learning_rate: float = 1e-3, epochs: int = 100, patience: int = 10,
                 task_type: str = 'regression', tweedie_power: float = 1.5,
                 use_data_parallel: bool = False, use_ddp: bool = False,
                 use_approx_knn: bool = True, approx_knn_threshold: int = 50000,
                 graph_cache_path: Optional[str] = None,
                 max_gpu_knn_nodes: Optional[int] = None,
                 knn_gpu_mem_ratio: float = 0.9,
                 knn_gpu_mem_overhead: float = 2.0) -> None:
        super().__init__()
        self.model_nme = model_nme
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.k_neighbors = max(1, k_neighbors)
        self.dropout = dropout
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.patience = patience
        self.task_type = task_type
        self.use_approx_knn = use_approx_knn
        self.approx_knn_threshold = approx_knn_threshold
        self.graph_cache_path = Path(
            graph_cache_path) if graph_cache_path else None
        self.max_gpu_knn_nodes = max_gpu_knn_nodes
        self.knn_gpu_mem_ratio = max(0.0, min(1.0, knn_gpu_mem_ratio))
        self.knn_gpu_mem_overhead = max(1.0, knn_gpu_mem_overhead)
        self._knn_warning_emitted = False

        if self.task_type == 'classification':
            self.tw_power = None
        elif 'f' in self.model_nme:
            self.tw_power = 1.0
        elif 's' in self.model_nme:
            self.tw_power = 2.0
        else:
            self.tw_power = tweedie_power

        self.ddp_enabled = False
        self.local_rank = int(os.environ.get("LOCAL_RANK", 0))
        self.data_parallel_enabled = False
        self._ddp_disabled = False

        if use_ddp:
            world_size = int(os.environ.get("WORLD_SIZE", "1"))
            if world_size > 1:
                print(
                    "[GNN] DDP training is not supported; falling back to single process.",
                    flush=True,
                )
                self._ddp_disabled = True
                use_ddp = False

        # DDP 仅在 CUDA 下有效；若未初始化成功则自动回退单卡
        if use_ddp and torch.cuda.is_available():
            ddp_ok, local_rank, _, _ = DistributedUtils.setup_ddp()
            if ddp_ok:
                self.ddp_enabled = True
                self.local_rank = local_rank
                self.device = torch.device(f'cuda:{local_rank}')
            else:
                self.device = torch.device('cuda')
        elif torch.cuda.is_available():
            if self._ddp_disabled:
                self.device = torch.device(f'cuda:{self.local_rank}')
            else:
                self.device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            self.device = torch.device('cpu')
            global _GNN_MPS_WARNED
            if not _GNN_MPS_WARNED:
                print(
                    "[GNN] MPS backend does not support sparse ops; falling back to CPU.",
                    flush=True,
                )
                _GNN_MPS_WARNED = True
        else:
            self.device = torch.device('cpu')
        self.use_pyg_knn = self.device.type == 'cuda' and _PYG_AVAILABLE

        self.gnn = SimpleGNN(
            input_dim=self.input_dim,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers,
            dropout=self.dropout,
            task_type=self.task_type
        ).to(self.device)

        # DataParallel 会将完整图复制到每张卡并按特征拆分，适合中等规模图
        if (not self.ddp_enabled) and use_data_parallel and (self.device.type == 'cuda') and (torch.cuda.device_count() > 1):
            self.data_parallel_enabled = True
            self.gnn = nn.DataParallel(
                self.gnn, device_ids=list(range(torch.cuda.device_count())))
            self.device = torch.device('cuda')

        if self.ddp_enabled:
            self.gnn = DDP(
                self.gnn,
                device_ids=[self.local_rank],
                output_device=self.local_rank,
                find_unused_parameters=False
            )

    def _unwrap_gnn(self) -> nn.Module:
        if isinstance(self.gnn, (DDP, nn.DataParallel)):
            return self.gnn.module
        return self.gnn

    def _set_adj_buffer(self, adj: torch.Tensor) -> None:
        base = self._unwrap_gnn()
        if hasattr(base, "adj_buffer"):
            base.adj_buffer = adj
        else:
            base.register_buffer("adj_buffer", adj)

    def _graph_cache_meta(self, X_df: pd.DataFrame) -> Dict[str, Any]:
        row_hash = pd.util.hash_pandas_object(X_df, index=False).values
        idx_hash = pd.util.hash_pandas_object(X_df.index, index=False).values
        col_sig = ",".join(map(str, X_df.columns))
        hasher = hashlib.sha256()
        hasher.update(row_hash.tobytes())
        hasher.update(idx_hash.tobytes())
        hasher.update(col_sig.encode("utf-8", errors="ignore"))
        return {
            "n_samples": int(X_df.shape[0]),
            "n_features": int(X_df.shape[1]),
            "hash": hasher.hexdigest(),
        }

    def _load_cached_adj(self, X_df: pd.DataFrame) -> Optional[torch.Tensor]:
        if self.graph_cache_path and self.graph_cache_path.exists():
            meta_expected = self._graph_cache_meta(X_df)
            try:
                payload = torch.load(self.graph_cache_path,
                                     map_location=self.device)
            except Exception as exc:
                print(
                    f"[GNN] Failed to load cached graph from {self.graph_cache_path}: {exc}")
                return None
            if isinstance(payload, dict) and "adj" in payload:
                meta_cached = payload.get("meta")
                if meta_cached == meta_expected:
                    return payload["adj"].to(self.device)
                print(
                    f"[GNN] Cached graph metadata mismatch; rebuilding: {self.graph_cache_path}")
                return None
            if isinstance(payload, torch.Tensor):
                print(
                    f"[GNN] Cached graph missing metadata; rebuilding: {self.graph_cache_path}")
                return None
            print(
                f"[GNN] Invalid cached graph format; rebuilding: {self.graph_cache_path}")
        return None

    def _build_edge_index_cpu(self, X_np: np.ndarray) -> torch.Tensor:
        n_samples = X_np.shape[0]
        k = min(self.k_neighbors, max(1, n_samples - 1))
        n_neighbors = min(k + 1, n_samples)
        use_approx = (self.use_approx_knn or n_samples >=
                      self.approx_knn_threshold) and _PYNN_AVAILABLE
        indices = None
        if use_approx:
            try:
                nn_index = pynndescent.NNDescent(
                    X_np,
                    n_neighbors=n_neighbors,
                    random_state=0
                )
                indices, _ = nn_index.neighbor_graph
            except Exception as exc:
                print(
                    f"[GNN] Approximate kNN failed ({exc}); falling back to exact search.")
                use_approx = False

        if indices is None:
            nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm="auto")
            nbrs.fit(X_np)
            _, indices = nbrs.kneighbors(X_np)

        indices = np.asarray(indices)

        rows = []
        cols = []
        for i in range(n_samples):
            for j in indices[i]:
                if i == j:
                    continue
                rows.append(i)
                cols.append(j)
                rows.append(j)
                cols.append(i)

        # 添加自环，避免度为 0 的节点
        rows.extend(range(n_samples))
        cols.extend(range(n_samples))

        edge_index = torch.tensor(
            [rows, cols], dtype=torch.long, device=self.device)
        return edge_index

    def _build_edge_index_gpu(self, X_tensor: torch.Tensor) -> torch.Tensor:
        if not self.use_pyg_knn or knn_graph is None or add_self_loops is None or to_undirected is None:
            # 防御式编程：调用前应检查 use_pyg_knn
            raise RuntimeError(
                "GPU graph builder requested but PyG is unavailable.")

        n_samples = X_tensor.size(0)
        k = min(self.k_neighbors, max(1, n_samples - 1))

        # knn_graph 运行在 GPU 上，避免 CPU 构图成为瓶颈
        edge_index = knn_graph(
            X_tensor,
            k=k,
            loop=False
        )
        edge_index = to_undirected(edge_index, num_nodes=n_samples)
        edge_index, _ = add_self_loops(edge_index, num_nodes=n_samples)
        return edge_index

    def _log_knn_fallback(self, reason: str) -> None:
        if self._knn_warning_emitted:
            return
        if (not self.ddp_enabled) or self.local_rank == 0:
            print(f"[GNN] Falling back to CPU kNN builder: {reason}")
        self._knn_warning_emitted = True

    def _should_use_gpu_knn(self, n_samples: int, X_tensor: torch.Tensor) -> bool:
        if not self.use_pyg_knn:
            return False

        reason = None
        if self.max_gpu_knn_nodes is not None and n_samples > self.max_gpu_knn_nodes:
            reason = f"node count {n_samples} exceeds max_gpu_knn_nodes={self.max_gpu_knn_nodes}"
        elif self.device.type == 'cuda' and torch.cuda.is_available():
            try:
                device_index = self.device.index
                if device_index is None:
                    device_index = torch.cuda.current_device()
                free_mem, total_mem = torch.cuda.mem_get_info(device_index)
                feature_bytes = X_tensor.element_size() * X_tensor.nelement()
                required = int(feature_bytes * self.knn_gpu_mem_overhead)
                budget = int(free_mem * self.knn_gpu_mem_ratio)
                if required > budget:
                    required_gb = required / (1024 ** 3)
                    budget_gb = budget / (1024 ** 3)
                    reason = (f"requires ~{required_gb:.2f} GiB temporary GPU memory "
                              f"but only {budget_gb:.2f} GiB free on cuda:{device_index}")
            except Exception:
                # 在较老版本或某些环境下 mem_get_info 可能不可用，默认继续尝试 GPU
                reason = None

        if reason:
            self._log_knn_fallback(reason)
            return False
        return True

    def _normalized_adj(self, edge_index: torch.Tensor, num_nodes: int) -> torch.Tensor:
        values = torch.ones(edge_index.shape[1], device=self.device)
        adj = torch.sparse_coo_tensor(
            edge_index.to(self.device), values, (num_nodes, num_nodes))
        adj = adj.coalesce()

        deg = torch.sparse.sum(adj, dim=1).to_dense()
        deg_inv_sqrt = torch.pow(deg + 1e-8, -0.5)
        row, col = adj.indices()
        norm_values = deg_inv_sqrt[row] * adj.values() * deg_inv_sqrt[col]
        adj_norm = torch.sparse_coo_tensor(
            adj.indices(), norm_values, size=adj.shape)
        return adj_norm

    def _tensorize_split(self, X, y, w, allow_none: bool = False):
        if X is None and allow_none:
            return None, None, None
        X_np = X.values.astype(np.float32)
        X_tensor = torch.tensor(X_np, dtype=torch.float32, device=self.device)
        if y is None:
            y_tensor = None
        else:
            y_tensor = torch.tensor(
                y.values, dtype=torch.float32, device=self.device).view(-1, 1)
        if w is None:
            w_tensor = torch.ones(
                (len(X), 1), dtype=torch.float32, device=self.device)
        else:
            w_tensor = torch.tensor(
                w.values, dtype=torch.float32, device=self.device).view(-1, 1)
        return X_tensor, y_tensor, w_tensor

    def _build_graph_from_df(self, X_df: pd.DataFrame, X_tensor: Optional[torch.Tensor] = None) -> torch.Tensor:
        if X_tensor is None:
            X_tensor = torch.tensor(
                X_df.values.astype(np.float32),
                dtype=torch.float32,
                device=self.device
            )
        if self.graph_cache_path:
            cached = self._load_cached_adj(X_df)
            if cached is not None:
                return cached
        use_gpu_knn = self._should_use_gpu_knn(X_df.shape[0], X_tensor)
        if use_gpu_knn:
            edge_index = self._build_edge_index_gpu(X_tensor)
        else:
            edge_index = self._build_edge_index_cpu(
                X_df.values.astype(np.float32))
        adj_norm = self._normalized_adj(edge_index, X_df.shape[0])
        if self.graph_cache_path:
            try:
                IOUtils.ensure_parent_dir(str(self.graph_cache_path))
                meta = self._graph_cache_meta(X_df)
                torch.save({"adj": adj_norm.cpu(), "meta": meta}, self.graph_cache_path)
            except Exception as exc:
                print(
                    f"[GNN] Failed to cache graph to {self.graph_cache_path}: {exc}")
        return adj_norm

    def fit(self, X_train, y_train, w_train=None,
            X_val=None, y_val=None, w_val=None,
            trial: Optional[optuna.trial.Trial] = None):

        X_train_tensor, y_train_tensor, w_train_tensor = self._tensorize_split(
            X_train, y_train, w_train, allow_none=False)
        has_val = X_val is not None and y_val is not None
        if has_val:
            X_val_tensor, y_val_tensor, w_val_tensor = self._tensorize_split(
                X_val, y_val, w_val, allow_none=False)
        else:
            X_val_tensor = y_val_tensor = w_val_tensor = None

        adj_train = self._build_graph_from_df(X_train, X_train_tensor)
        adj_val = self._build_graph_from_df(
            X_val, X_val_tensor) if has_val else None
        # DataParallel 需要将邻接矩阵缓存在模型上，避免被 scatter
        self._set_adj_buffer(adj_train)

        base_gnn = self._unwrap_gnn()
        optimizer = torch.optim.Adam(
            base_gnn.parameters(), lr=self.learning_rate)
        scaler = GradScaler(enabled=(self.device.type == 'cuda'))

        best_loss = float('inf')
        best_state = None
        patience_counter = 0

        for epoch in range(1, self.epochs + 1):
            epoch_start_ts = time.time()
            self.gnn.train()
            optimizer.zero_grad()
            with autocast(enabled=(self.device.type == 'cuda')):
                if self.data_parallel_enabled:
                    y_pred = self.gnn(X_train_tensor)
                else:
                    y_pred = self.gnn(X_train_tensor, adj_train)
                loss = self._compute_weighted_loss(
                    y_pred, y_train_tensor, w_train_tensor, apply_softplus=False)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            clip_grad_norm_(self.gnn.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()

            val_loss = None
            if has_val:
                self.gnn.eval()
                if self.data_parallel_enabled and adj_val is not None:
                    self._set_adj_buffer(adj_val)
                with torch.no_grad(), autocast(enabled=(self.device.type == 'cuda')):
                    if self.data_parallel_enabled:
                        y_val_pred = self.gnn(X_val_tensor)
                    else:
                        y_val_pred = self.gnn(X_val_tensor, adj_val)
                    val_loss = self._compute_weighted_loss(
                        y_val_pred, y_val_tensor, w_val_tensor, apply_softplus=False)
                if self.data_parallel_enabled:
                    # 恢复训练邻接矩阵
                    self._set_adj_buffer(adj_train)

                best_loss, best_state, patience_counter, stop_training = self._early_stop_update(
                    val_loss, best_loss, best_state, patience_counter, base_gnn,
                    ignore_keys=["adj_buffer"])

                if trial is not None:
                    trial.report(val_loss, epoch)
                    if trial.should_prune():
                        raise optuna.TrialPruned()
                if stop_training:
                    break

            should_log = (not dist.is_initialized()
                          or DistributedUtils.is_main_process())
            if should_log:
                elapsed = int(time.time() - epoch_start_ts)
                if val_loss is None:
                    print(
                        f"[GNN] Epoch {epoch}/{self.epochs} loss={float(loss):.6f} elapsed={elapsed}s",
                        flush=True,
                    )
                else:
                    print(
                        f"[GNN] Epoch {epoch}/{self.epochs} loss={float(loss):.6f} "
                        f"val_loss={float(val_loss):.6f} elapsed={elapsed}s",
                        flush=True,
                    )

        if best_state is not None:
            base_gnn.load_state_dict(best_state, strict=False)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        self.gnn.eval()
        X_tensor, _, _ = self._tensorize_split(
            X, None, None, allow_none=False)
        adj = self._build_graph_from_df(X, X_tensor)
        if self.data_parallel_enabled:
            self._set_adj_buffer(adj)
        with torch.no_grad():
            if self.data_parallel_enabled:
                y_pred = self.gnn(X_tensor).cpu().numpy()
            else:
                y_pred = self.gnn(X_tensor, adj).cpu().numpy()
        if self.task_type == 'classification':
            y_pred = 1 / (1 + np.exp(-y_pred))
        else:
            y_pred = np.clip(y_pred, 1e-6, None)
        return y_pred.ravel()

    def encode(self, X: pd.DataFrame) -> np.ndarray:
        """返回每个样本对应的节点 embedding（隐藏表征）。"""
        base = self._unwrap_gnn()
        base.eval()
        X_tensor, _, _ = self._tensorize_split(X, None, None, allow_none=False)
        adj = self._build_graph_from_df(X, X_tensor)
        if self.data_parallel_enabled:
            self._set_adj_buffer(adj)
        with torch.no_grad():
            h = X_tensor
            layers = getattr(base, "layers", None)
            if layers is None:
                raise RuntimeError("GNN base module does not expose layers.")
            for layer in layers:
                h = layer(h, adj)
            h = torch.sparse.mm(adj, h)
        return h.detach().cpu().numpy()

    def set_params(self, params: Dict[str, Any]):
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Parameter {key} not found in GNN model.")
        # 结构参数变化后需要重建骨架
        self.gnn = SimpleGNN(
            input_dim=self.input_dim,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers,
            dropout=self.dropout,
            task_type=self.task_type
        ).to(self.device)
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
    xgb_max_depth_max: int = 25
    xgb_n_estimators_max: int = 500
    use_resn_data_parallel: bool = False
    use_ft_data_parallel: bool = False
    use_resn_ddp: bool = False
    use_ft_ddp: bool = False
    use_gnn_data_parallel: bool = False
    use_gnn_ddp: bool = False
    gnn_use_approx_knn: bool = True
    gnn_approx_knn_threshold: int = 50000
    gnn_graph_cache: Optional[str] = None
    gnn_max_gpu_knn_nodes: Optional[int] = 200000
    gnn_knn_gpu_mem_ratio: float = 0.9
    gnn_knn_gpu_mem_overhead: float = 2.0
    region_province_col: Optional[str] = None  # 省级列名，用于层级平滑
    region_city_col: Optional[str] = None      # 市级列名，用于层级平滑
    region_effect_alpha: float = 50.0          # 层级平滑强度（伪样本量）
    geo_feature_nmes: Optional[List[str]] = None  # 用于构造地理 token 的列，空则不启用 GNN
    geo_token_hidden_dim: int = 32
    geo_token_layers: int = 2
    geo_token_dropout: float = 0.1
    geo_token_k_neighbors: int = 10
    geo_token_learning_rate: float = 1e-3
    geo_token_epochs: int = 50
    output_dir: Optional[str] = None
    optuna_storage: Optional[str] = None
    optuna_study_prefix: Optional[str] = None
    best_params_files: Optional[Dict[str, str]] = None
    # FT 角色：
    #   - "model": FT 作为单独预测模型（保留 lift/SHAP 等评估）
    #   - "embedding": FT 训练后仅导出 embedding 作为下游特征（不做 FT 单独评估）
    #   - "unsupervised_embedding": masked 重建自监督预训练后导出 embedding
    ft_role: str = "model"
    ft_feature_prefix: str = "ft_emb"
    reuse_best_params: bool = False


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


class VersionManager:
    """简单的版本记录：保存配置与最优参数快照，便于回溯。"""

    def __init__(self, output: OutputManager) -> None:
        self.output = output
        self.version_dir = Path(self.output.result_dir) / "versions"
        IOUtils.ensure_parent_dir(str(self.version_dir))

    def save(self, tag: str, payload: Dict[str, Any]) -> str:
        safe_tag = tag.replace(" ", "_")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.version_dir / f"{ts}_{safe_tag}.json"
        IOUtils.ensure_parent_dir(str(path))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
        print(f"[Version] 已保存快照：{path}")
        return str(path)

    def load_latest(self, tag: str) -> Optional[Dict[str, Any]]:
        """加载指定 tag 的最新快照（按文件名时间戳前缀排序）。"""
        safe_tag = tag.replace(" ", "_")
        pattern = f"*_{safe_tag}.json"
        candidates = sorted(self.version_dir.glob(pattern))
        if not candidates:
            return None
        path = candidates[-1]
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[Version] Failed to load snapshot {path}: {exc}")
            return None


class DatasetPreprocessor:
    # 为各训练器准备通用的训练/测试数据视图

    def __init__(self, train_df: pd.DataFrame, test_df: pd.DataFrame,
                 config: BayesOptConfig) -> None:
        self.config = config
        self.train_data = train_df.copy(deep=True)
        self.test_data = test_df.copy(deep=True)
        self.num_features: List[str] = []
        self.train_oht_data: Optional[pd.DataFrame] = None
        self.test_oht_data: Optional[pd.DataFrame] = None
        self.train_oht_scl_data: Optional[pd.DataFrame] = None
        self.test_oht_scl_data: Optional[pd.DataFrame] = None
        self.var_nmes: List[str] = []
        self.cat_categories_for_shap: Dict[str, List[Any]] = {}

    def run(self) -> "DatasetPreprocessor":
        """执行预处理：类别编码、目标值裁剪以及数值特征标准化。"""
        cfg = self.config
        missing_train = [
            col for col in (cfg.resp_nme, cfg.weight_nme)
            if col not in self.train_data.columns
        ]
        if missing_train:
            raise KeyError(
                f"Train data missing required columns: {missing_train}")
        if cfg.binary_resp_nme and cfg.binary_resp_nme not in self.train_data.columns:
            raise KeyError(
                f"Train data missing binary response column: {cfg.binary_resp_nme}")

        test_has_resp = cfg.resp_nme in self.test_data.columns
        test_has_weight = cfg.weight_nme in self.test_data.columns
        test_has_binary = bool(
            cfg.binary_resp_nme and cfg.binary_resp_nme in self.test_data.columns
        )
        if not test_has_weight:
            self.test_data[cfg.weight_nme] = 1.0
        if not test_has_resp:
            self.test_data[cfg.resp_nme] = np.nan
        if cfg.binary_resp_nme and cfg.binary_resp_nme not in self.test_data.columns:
            self.test_data[cfg.binary_resp_nme] = np.nan

        # 预先计算加权实际值，后续画图、校验都依赖该字段
        self.train_data.loc[:, 'w_act'] = self.train_data[cfg.resp_nme] * \
            self.train_data[cfg.weight_nme]
        if test_has_resp:
            self.test_data.loc[:, 'w_act'] = self.test_data[cfg.resp_nme] * \
                self.test_data[cfg.weight_nme]
        if cfg.binary_resp_nme:
            self.train_data.loc[:, 'w_binary_act'] = self.train_data[cfg.binary_resp_nme] * \
                self.train_data[cfg.weight_nme]
            if test_has_binary:
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

        # 重新索引时将缺失的哑变量列补零，避免测试集列数与训练集不一致
        test_oht = test_oht.reindex(columns=train_oht.columns, fill_value=0)

        # 保留未缩放的 one-hot 数据，供交叉验证时按折内标准化避免泄露
        self.train_oht_data = train_oht.copy(deep=True)
        self.test_oht_data = test_oht.copy(deep=True)

        train_oht_scaled = train_oht.copy(deep=True)
        test_oht_scaled = test_oht.copy(deep=True)
        for num_chr in self.num_features:
            # 逐列标准化保障每个特征在同一量级，否则神经网络会难以收敛
            scaler = StandardScaler()
            train_oht_scaled[num_chr] = scaler.fit_transform(
                train_oht_scaled[num_chr].values.reshape(-1, 1))
            test_oht_scaled[num_chr] = scaler.transform(
                test_oht_scaled[num_chr].values.reshape(-1, 1))
        # 重新索引时将缺失的哑变量列补零，避免测试集列数与训练集不一致
        test_oht_scaled = test_oht_scaled.reindex(
            columns=train_oht_scaled.columns, fill_value=0)
        self.train_oht_scl_data = train_oht_scaled
        self.test_oht_scl_data = test_oht_scaled
        excluded = {cfg.weight_nme, cfg.resp_nme}
        self.var_nmes = [
            col for col in train_oht_scaled.columns if col not in excluded
        ]
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
        self.study_name: Optional[str] = None
        self.enable_distributed_optuna: bool = False
        self._distributed_forced_params: Optional[Dict[str, Any]] = None

    @property
    def config(self) -> BayesOptConfig:
        return self.ctx.config

    @property
    def output(self) -> OutputManager:
        return self.ctx.output_manager

    def _get_model_filename(self) -> str:
        ext = 'pkl' if self.label in ['Xgboost', 'GLM'] else 'pth'
        return f'01_{self.ctx.model_nme}_{self.model_name_prefix}.{ext}'

    def _resolve_optuna_storage_url(self) -> Optional[str]:
        storage = getattr(self.config, "optuna_storage", None)
        if not storage:
            return None
        storage_str = str(storage).strip()
        if not storage_str:
            return None
        if "://" in storage_str or storage_str == ":memory:":
            return storage_str
        path = Path(storage_str)
        path = path.resolve()
        ensure_parent_dir(str(path))
        return f"sqlite:///{path.as_posix()}"

    def _resolve_optuna_study_name(self) -> str:
        prefix = getattr(self.config, "optuna_study_prefix",
                         None) or "bayesopt"
        raw = f"{prefix}_{self.ctx.model_nme}_{self.model_name_prefix}"
        safe = "".join([c if c.isalnum() or c in "._-" else "_" for c in raw])
        return safe.lower()

    def tune(self, max_evals: int, objective_fn=None) -> None:
        # 通用的 Optuna 调参循环流程。
        if objective_fn is None:
            # 若子类未显式提供 objective_fn，则默认使用 cross_val 作为优化目标
            objective_fn = self.cross_val

        if self._should_use_distributed_optuna():
            self._distributed_tune(max_evals, objective_fn)
            return

        total_trials = max(1, int(max_evals))
        progress_counter = {"count": 0}

        def objective_wrapper(trial: optuna.trial.Trial) -> float:
            should_log = DistributedUtils.is_main_process()
            if should_log:
                current_idx = progress_counter["count"] + 1
                print(
                    f"[Optuna][{self.label}] Trial {current_idx}/{total_trials} started "
                    f"(trial_id={trial.number})."
                )
            try:
                result = objective_fn(trial)
            except RuntimeError as exc:
                if "out of memory" in str(exc).lower():
                    print(
                        f"[Optuna][{self.label}] OOM detected. Pruning trial and clearing CUDA cache."
                    )
                    self._clean_gpu()
                    raise optuna.TrialPruned() from exc
                raise
            finally:
                self._clean_gpu()
                if should_log:
                    progress_counter["count"] = progress_counter["count"] + 1
                    trial_state = getattr(trial, "state", None)
                    state_repr = getattr(trial_state, "name", "OK")
                    print(
                        f"[Optuna][{self.label}] Trial {progress_counter['count']}/{total_trials} finished "
                        f"(status={state_repr})."
                    )
            return result

        storage_url = self._resolve_optuna_storage_url()
        study_name = self._resolve_optuna_study_name()
        study_kwargs: Dict[str, Any] = {
            "direction": "minimize",
            "sampler": optuna.samplers.TPESampler(seed=self.ctx.rand_seed),
        }
        if storage_url:
            study_kwargs.update(
                storage=storage_url,
                study_name=study_name,
                load_if_exists=True,
            )

        study = optuna.create_study(**study_kwargs)
        self.study_name = getattr(study, "study_name", None)

        def checkpoint_callback(check_study: optuna.study.Study, _trial) -> None:
            # 每个 trial 后都落盘 best_params，方便安全中断/重启续跑。
            try:
                best = getattr(check_study, "best_trial", None)
                if best is None:
                    return
                best_params = getattr(best, "params", None)
                if not best_params:
                    return
                params_path = self.output.result_path(
                    f'{self.ctx.model_nme}_bestparams_{self.label.lower()}.csv'
                )
                pd.DataFrame(best_params, index=[0]).to_csv(
                    params_path, index=False)
            except Exception:
                return

        completed_states = (
            optuna.trial.TrialState.COMPLETE,
            optuna.trial.TrialState.PRUNED,
            optuna.trial.TrialState.FAIL,
        )
        completed = len(study.get_trials(states=completed_states))
        progress_counter["count"] = completed
        remaining = max(0, total_trials - completed)
        if remaining > 0:
            study.optimize(
                objective_wrapper,
                n_trials=remaining,
                callbacks=[checkpoint_callback],
            )
        self.best_params = study.best_params
        self.best_trial = study.best_trial

        # 将最优参数保存为 CSV，方便复现
        params_path = self.output.result_path(
            f'{self.ctx.model_nme}_bestparams_{self.label.lower()}.csv'
        )
        pd.DataFrame(self.best_params, index=[0]).to_csv(
            params_path, index=False)

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
            # PyTorch 模型既可以只存 state_dict，也可以整个对象一起序列化
            # 兼容历史行为：ResNetTrainer 保存 state_dict，FTTrainer 保存完整对象
            if hasattr(self.model, 'resnet'):  # ResNetSklearn 模型
                torch.save(self.model.resnet.state_dict(), path)
            else:  # FTTransformerSklearn 或其他 PyTorch 模型
                torch.save(self.model, path)

    def load(self) -> None:
        path = self.output.model_path(self._get_model_filename())
        if not os.path.exists(path):
            print(f"[load] Warning: Model file not found: {path}")
            return

        if self.label in ['Xgboost', 'GLM']:
            self.model = joblib.load(path)
        else:
            # PyTorch 模型的加载需要根据结构区别处理
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
        if hasattr(model_obj, 'gnn'):
            model_obj.gnn.to(device)

    def _should_use_distributed_optuna(self) -> bool:
        if not self.enable_distributed_optuna:
            return False
        rank_env = os.environ.get("RANK")
        world_env = os.environ.get("WORLD_SIZE")
        local_env = os.environ.get("LOCAL_RANK")
        if rank_env is None or world_env is None or local_env is None:
            return False
        try:
            world_size = int(world_env)
        except Exception:
            return False
        return world_size > 1

    def _distributed_is_main(self) -> bool:
        return DistributedUtils.is_main_process()

    def _distributed_send_command(self, payload: Dict[str, Any]) -> None:
        if not self._should_use_distributed_optuna() or not self._distributed_is_main():
            return
        DistributedUtils.setup_ddp()
        if not dist.is_initialized():
            return
        message = [payload]
        dist.broadcast_object_list(message, src=0)

    def _distributed_prepare_trial(self, params: Dict[str, Any]) -> None:
        if not self._should_use_distributed_optuna():
            return
        if not self._distributed_is_main():
            return
        self._distributed_send_command({"type": "RUN", "params": params})
        if not dist.is_initialized():
            return
        dist.barrier()

    def _distributed_worker_loop(self, objective_fn: Callable[[Optional[optuna.trial.Trial]], float]) -> None:
        DistributedUtils.setup_ddp()
        if not dist.is_initialized():
            print(
                f"[Optuna][Worker][{self.label}] DDP init failed. Worker exit.",
                flush=True,
            )
            return
        while True:
            message = [None]
            dist.broadcast_object_list(message, src=0)
            payload = message[0]
            if not isinstance(payload, dict):
                continue
            cmd = payload.get("type")
            if cmd == "STOP":
                best_params = payload.get("best_params")
                if best_params is not None:
                    self.best_params = best_params
                break
            if cmd == "RUN":
                params = payload.get("params") or {}
                self._distributed_forced_params = params
                dist.barrier()
                try:
                    objective_fn(None)
                except optuna.TrialPruned:
                    pass
                except Exception as exc:
                    print(
                        f"[Optuna][Worker][{self.label}] Exception: {exc}", flush=True)
                finally:
                    self._clean_gpu()
                    dist.barrier()

    def _distributed_tune(self, max_evals: int, objective_fn: Callable[[optuna.trial.Trial], float]) -> None:
        DistributedUtils.setup_ddp()
        if not dist.is_initialized():
            rank_env = os.environ.get("RANK", "0")
            if str(rank_env) != "0":
                print(
                    f"[Optuna][{self.label}] DDP init failed on worker. Skip.",
                    flush=True,
                )
                return
            print(
                f"[Optuna][{self.label}] DDP init failed. Fallback to single-process.",
                flush=True,
            )
            prev = self.enable_distributed_optuna
            self.enable_distributed_optuna = False
            try:
                self.tune(max_evals, objective_fn)
            finally:
                self.enable_distributed_optuna = prev
            return
        if not self._distributed_is_main():
            self._distributed_worker_loop(objective_fn)
            return

        total_trials = max(1, int(max_evals))
        progress_counter = {"count": 0}

        def objective_wrapper(trial: optuna.trial.Trial) -> float:
            should_log = True
            if should_log:
                current_idx = progress_counter["count"] + 1
                print(
                    f"[Optuna][{self.label}] Trial {current_idx}/{total_trials} started "
                    f"(trial_id={trial.number})."
                )
            try:
                result = objective_fn(trial)
            except RuntimeError as exc:
                if "out of memory" in str(exc).lower():
                    print(
                        f"[Optuna][{self.label}] OOM detected. Pruning trial and clearing CUDA cache."
                    )
                    self._clean_gpu()
                    raise optuna.TrialPruned() from exc
                raise
            finally:
                self._clean_gpu()
                if should_log:
                    progress_counter["count"] = progress_counter["count"] + 1
                    trial_state = getattr(trial, "state", None)
                    state_repr = getattr(trial_state, "name", "OK")
                    print(
                        f"[Optuna][{self.label}] Trial {progress_counter['count']}/{total_trials} finished "
                        f"(status={state_repr})."
                    )
                dist.barrier()
            return result

        storage_url = self._resolve_optuna_storage_url()
        study_name = self._resolve_optuna_study_name()
        study_kwargs: Dict[str, Any] = {
            "direction": "minimize",
            "sampler": optuna.samplers.TPESampler(seed=self.ctx.rand_seed),
        }
        if storage_url:
            study_kwargs.update(
                storage=storage_url,
                study_name=study_name,
                load_if_exists=True,
            )
        study = optuna.create_study(**study_kwargs)
        self.study_name = getattr(study, "study_name", None)

        def checkpoint_callback(check_study: optuna.study.Study, _trial) -> None:
            try:
                best = getattr(check_study, "best_trial", None)
                if best is None:
                    return
                best_params = getattr(best, "params", None)
                if not best_params:
                    return
                params_path = self.output.result_path(
                    f'{self.ctx.model_nme}_bestparams_{self.label.lower()}.csv'
                )
                pd.DataFrame(best_params, index=[0]).to_csv(
                    params_path, index=False)
            except Exception:
                return

        completed_states = (
            optuna.trial.TrialState.COMPLETE,
            optuna.trial.TrialState.PRUNED,
            optuna.trial.TrialState.FAIL,
        )
        completed = len(study.get_trials(states=completed_states))
        progress_counter["count"] = completed
        remaining = max(0, total_trials - completed)
        try:
            if remaining > 0:
                study.optimize(
                    objective_wrapper,
                    n_trials=remaining,
                    callbacks=[checkpoint_callback],
                )
            self.best_params = study.best_params
            self.best_trial = study.best_trial
            params_path = self.output.result_path(
                f'{self.ctx.model_nme}_bestparams_{self.label.lower()}.csv'
            )
            pd.DataFrame(self.best_params, index=[0]).to_csv(
                params_path, index=False)
        finally:
            self._distributed_send_command(
                {"type": "STOP", "best_params": self.best_params})

    def _clean_gpu(self):
        gc.collect()
        if torch.cuda.is_available():
            device = None
            try:
                device = getattr(self, "device", None)
            except Exception:
                device = None
            if isinstance(device, torch.device):
                try:
                    torch.cuda.set_device(device)
                except Exception:
                    pass
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            torch.cuda.synchronize()

    def _standardize_fold(self,
                          X_train: pd.DataFrame,
                          X_val: pd.DataFrame,
                          columns: Optional[List[str]] = None
                          ) -> Tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
        """在训练折上拟合 StandardScaler，并同步变换训练/验证特征。

        参数:
            X_train: 训练集特征。
            X_val: 验证集特征。
            columns: 需要缩放的列名；默认对全部列进行缩放。

        返回:
            缩放后的训练/验证特征，以及已拟合好的 scaler 对象。
        """
        scaler = StandardScaler()
        cols = list(columns) if columns else list(X_train.columns)
        X_train_scaled = X_train.copy(deep=True)
        X_val_scaled = X_val.copy(deep=True)
        if cols:
            scaler.fit(X_train_scaled[cols])
            X_train_scaled[cols] = scaler.transform(X_train_scaled[cols])
            X_val_scaled[cols] = scaler.transform(X_val_scaled[cols])
        return X_train_scaled, X_val_scaled, scaler

    def cross_val_generic(
            self,
            trial: optuna.trial.Trial,
            hyperparameter_space: Dict[str, Callable[[optuna.trial.Trial], Any]],
            data_provider: Callable[[], Tuple[pd.DataFrame, pd.Series, Optional[pd.Series]]],
            model_builder: Callable[[Dict[str, Any]], Any],
            metric_fn: Callable[[pd.Series, np.ndarray, Optional[pd.Series]], float],
            sample_limit: Optional[int] = None,
            preprocess_fn: Optional[Callable[[
                pd.DataFrame, pd.DataFrame], Tuple[pd.DataFrame, pd.DataFrame]]] = None,
            fit_predict_fn: Optional[
                Callable[[Any, pd.DataFrame, pd.Series, Optional[pd.Series],
                          pd.DataFrame, pd.Series, Optional[pd.Series],
                          optuna.trial.Trial], np.ndarray]
            ] = None,
            cleanup_fn: Optional[Callable[[Any], None]] = None,
            splitter: Optional[Iterable[Tuple[np.ndarray, np.ndarray]]] = None) -> float:
        """通用的留出/交叉验证辅助函数，用于复用调参流程。

        参数:
            trial: 当前 Optuna trial。
            hyperparameter_space: 参数采样器字典，键为参数名。
            data_provider: 返回 (X, y, sample_weight) 的回调。
            model_builder: 每个折构造新模型的回调。
            metric_fn: 计算损失或得分的函数，入参为 y_true、y_pred、weight。
            sample_limit: 可选样本上限，超出时随机抽样。
            preprocess_fn: 可选的折内预处理函数，输入 (X_train, X_val)。
            fit_predict_fn: 可选自定义训练与预测逻辑，返回验证集预测。
            cleanup_fn: 可选清理函数，每个折结束后调用。
            splitter: 可选的 (train_idx, val_idx) 迭代器；默认使用单个 ShuffleSplit。

        返回:
            各折验证指标的平均值。
        """
        params: Optional[Dict[str, Any]] = None
        if self._distributed_forced_params is not None:
            params = self._distributed_forced_params
            self._distributed_forced_params = None
        else:
            if trial is None:
                raise RuntimeError(
                    "Missing Optuna trial for parameter sampling.")
            params = {name: sampler(trial)
                      for name, sampler in hyperparameter_space.items()}
            if self._should_use_distributed_optuna():
                self._distributed_prepare_trial(params)
        X_all, y_all, w_all = data_provider()
        if sample_limit is not None and len(X_all) > sample_limit:
            sampled_idx = X_all.sample(
                n=sample_limit,
                random_state=self.ctx.rand_seed
            ).index
            X_all = X_all.loc[sampled_idx]
            y_all = y_all.loc[sampled_idx]
            w_all = w_all.loc[sampled_idx] if w_all is not None else None

        split_iter = splitter or ShuffleSplit(
            n_splits=int(1 / self.ctx.prop_test),
            test_size=self.ctx.prop_test,
            random_state=self.ctx.rand_seed
        ).split(X_all)

        losses: List[float] = []
        for train_idx, val_idx in split_iter:
            X_train = X_all.iloc[train_idx]
            y_train = y_all.iloc[train_idx]
            X_val = X_all.iloc[val_idx]
            y_val = y_all.iloc[val_idx]
            w_train = w_all.iloc[train_idx] if w_all is not None else None
            w_val = w_all.iloc[val_idx] if w_all is not None else None

            if preprocess_fn:
                X_train, X_val = preprocess_fn(X_train, X_val)

            model = model_builder(params)
            try:
                if fit_predict_fn:
                    y_pred = fit_predict_fn(
                        model, X_train, y_train, w_train,
                        X_val, y_val, w_val, trial
                    )
                else:
                    fit_kwargs = {}
                    if w_train is not None:
                        fit_kwargs["sample_weight"] = w_train
                    model.fit(X_train, y_train, **fit_kwargs)
                    y_pred = model.predict(X_val)
                losses.append(metric_fn(y_val, y_pred, w_val))
            finally:
                if cleanup_fn:
                    cleanup_fn(model)
                self._clean_gpu()

        return float(np.mean(losses))

    # 预测 + 缓存逻辑
    def _predict_and_cache(self,
                           model,
                           pred_prefix: str,
                           use_oht: bool = False,
                           design_fn=None,
                           predict_kwargs_train: Optional[Dict[str, Any]] = None,
                           predict_kwargs_test: Optional[Dict[str, Any]] = None,
                           predict_fn: Optional[Callable[..., Any]] = None) -> None:
        if design_fn:
            X_train = design_fn(train=True)
            X_test = design_fn(train=False)
        elif use_oht:
            X_train = self.ctx.train_oht_scl_data[self.ctx.var_nmes]
            X_test = self.ctx.test_oht_scl_data[self.ctx.var_nmes]
        else:
            X_train = self.ctx.train_data[self.ctx.factor_nmes]
            X_test = self.ctx.test_data[self.ctx.factor_nmes]

        predictor = predict_fn or model.predict
        preds_train = predictor(X_train, **(predict_kwargs_train or {}))
        preds_test = predictor(X_test, **(predict_kwargs_test or {}))
        preds_train = np.asarray(preds_train)
        preds_test = np.asarray(preds_test)

        if preds_train.ndim <= 1 or (preds_train.ndim == 2 and preds_train.shape[1] == 1):
            col_name = f'pred_{pred_prefix}'
            self.ctx.train_data[col_name] = preds_train.reshape(-1)
            self.ctx.test_data[col_name] = preds_test.reshape(-1)
            self.ctx.train_data[f'w_{col_name}'] = (
                self.ctx.train_data[col_name] *
                self.ctx.train_data[self.ctx.weight_nme]
            )
            self.ctx.test_data[f'w_{col_name}'] = (
                self.ctx.test_data[col_name] *
                self.ctx.test_data[self.ctx.weight_nme]
            )
            return

        # 多维输出（如 embedding）按列展开缓存：pred_<prefix>_0 ... pred_<prefix>_{k-1}
        if preds_train.ndim != 2:
            raise ValueError(
                f"Unexpected prediction shape for '{pred_prefix}': {preds_train.shape}")
        if preds_test.ndim != 2 or preds_test.shape[1] != preds_train.shape[1]:
            raise ValueError(
                f"Train/test prediction dims mismatch for '{pred_prefix}': "
                f"{preds_train.shape} vs {preds_test.shape}")
        for j in range(preds_train.shape[1]):
            col_name = f'pred_{pred_prefix}_{j}'
            self.ctx.train_data[col_name] = preds_train[:, j]
            self.ctx.test_data[col_name] = preds_test[:, j]

    def _fit_predict_cache(self,
                           model,
                           X_train,
                           y_train,
                           sample_weight,
                           pred_prefix: str,
                           use_oht: bool = False,
                           design_fn=None,
                           fit_kwargs: Optional[Dict[str, Any]] = None,
                           sample_weight_arg: Optional[str] = 'sample_weight',
                           predict_kwargs_train: Optional[Dict[str, Any]] = None,
                           predict_kwargs_test: Optional[Dict[str, Any]] = None,
                           predict_fn: Optional[Callable[..., Any]] = None,
                           record_label: bool = True) -> None:
        fit_kwargs = fit_kwargs.copy() if fit_kwargs else {}
        if sample_weight is not None and sample_weight_arg:
            fit_kwargs.setdefault(sample_weight_arg, sample_weight)
        model.fit(X_train, y_train, **fit_kwargs)
        if record_label:
            self.ctx.model_label.append(self.label)
        self._predict_and_cache(
            model,
            pred_prefix,
            use_oht=use_oht,
            design_fn=design_fn,
            predict_kwargs_train=predict_kwargs_train,
            predict_kwargs_test=predict_kwargs_test,
            predict_fn=predict_fn)


class GNNTrainer(TrainerBase):
    def __init__(self, context: "BayesOptModel") -> None:
        super().__init__(context, 'GNN', 'GNN')
        self.model: Optional[GraphNeuralNetSklearn] = None
        self.enable_distributed_optuna = bool(context.config.use_gnn_ddp)

    def _build_model(self, params: Optional[Dict[str, Any]] = None) -> GraphNeuralNetSklearn:
        params = params or {}
        base_tw_power = self.ctx.default_tweedie_power()
        model = GraphNeuralNetSklearn(
            model_nme=f"{self.ctx.model_nme}_gnn",
            input_dim=len(self.ctx.var_nmes),
            hidden_dim=int(params.get("hidden_dim", 64)),
            num_layers=int(params.get("num_layers", 2)),
            k_neighbors=int(params.get("k_neighbors", 10)),
            dropout=float(params.get("dropout", 0.1)),
            learning_rate=float(params.get("learning_rate", 1e-3)),
            epochs=int(params.get("epochs", self.ctx.epochs)),
            patience=int(params.get("patience", 5)),
            task_type=self.ctx.task_type,
            tweedie_power=float(params.get("tw_power", base_tw_power or 1.5)),
            use_data_parallel=bool(self.ctx.config.use_gnn_data_parallel),
            use_ddp=bool(self.ctx.config.use_gnn_ddp),
            use_approx_knn=bool(self.ctx.config.gnn_use_approx_knn),
            approx_knn_threshold=int(self.ctx.config.gnn_approx_knn_threshold),
            graph_cache_path=self.ctx.config.gnn_graph_cache,
            max_gpu_knn_nodes=self.ctx.config.gnn_max_gpu_knn_nodes,
            knn_gpu_mem_ratio=float(self.ctx.config.gnn_knn_gpu_mem_ratio),
            knn_gpu_mem_overhead=float(
                self.ctx.config.gnn_knn_gpu_mem_overhead),
        )
        return model

    def cross_val(self, trial: optuna.trial.Trial) -> float:
        base_tw_power = self.ctx.default_tweedie_power()
        metric_ctx: Dict[str, Any] = {}

        def data_provider():
            data = self.ctx.train_oht_data if self.ctx.train_oht_data is not None else self.ctx.train_oht_scl_data
            assert data is not None, "Preprocessed training data is missing."
            return data[self.ctx.var_nmes], data[self.ctx.resp_nme], data[self.ctx.weight_nme]

        def model_builder(params: Dict[str, Any]):
            tw_power = params.get("tw_power", base_tw_power)
            metric_ctx["tw_power"] = tw_power
            return self._build_model(params)

        def preprocess_fn(X_train, X_val):
            X_train_s, X_val_s, _ = self._standardize_fold(
                X_train, X_val, self.ctx.num_features)
            return X_train_s, X_val_s

        def fit_predict(model, X_train, y_train, w_train, X_val, y_val, w_val, trial_obj):
            model.fit(
                X_train,
                y_train,
                w_train=w_train,
                X_val=X_val,
                y_val=y_val,
                w_val=w_val,
                trial=trial_obj,
            )
            return model.predict(X_val)

        def metric_fn(y_true, y_pred, weight):
            if self.ctx.task_type == 'classification':
                y_pred_clipped = np.clip(y_pred, EPS, 1 - EPS)
                return log_loss(y_true, y_pred_clipped, sample_weight=weight)
            y_pred_safe = np.maximum(y_pred, EPS)
            power = metric_ctx.get("tw_power", base_tw_power or 1.5)
            return mean_tweedie_deviance(
                y_true,
                y_pred_safe,
                sample_weight=weight,
                power=power,
            )

        # 让 GNN 的 BO 保持轻量：交叉验证阶段只抽样，最终训练再用全量数据。
        X_cap = data_provider()[0]
        sample_limit = min(200000, len(X_cap)) if len(X_cap) > 200000 else None

        param_space: Dict[str, Callable[[optuna.trial.Trial], Any]] = {
            "learning_rate": lambda t: t.suggest_float('learning_rate', 1e-4, 5e-3, log=True),
            "hidden_dim": lambda t: t.suggest_int('hidden_dim', 16, 128, step=16),
            "num_layers": lambda t: t.suggest_int('num_layers', 1, 4),
            "k_neighbors": lambda t: t.suggest_int('k_neighbors', 5, 30),
            "dropout": lambda t: t.suggest_float('dropout', 0.0, 0.3),
        }
        if self.ctx.task_type == 'regression' and self.ctx.obj == 'reg:tweedie':
            param_space["tw_power"] = lambda t: t.suggest_float(
                'tw_power', 1.0, 2.0)

        return self.cross_val_generic(
            trial=trial,
            hyperparameter_space=param_space,
            data_provider=data_provider,
            model_builder=model_builder,
            metric_fn=metric_fn,
            sample_limit=sample_limit,
            preprocess_fn=preprocess_fn,
            fit_predict_fn=fit_predict,
            cleanup_fn=lambda m: getattr(
                getattr(m, "gnn", None), "to", lambda *_args, **_kwargs: None)("cpu")
        )

    def train(self) -> None:
        if not self.best_params:
            raise RuntimeError('请先运行 tune() 以获得 GNN 最优参数。')

        data = self.ctx.train_oht_scl_data
        assert data is not None, "Preprocessed training data is missing."
        X_all = data[self.ctx.var_nmes]
        y_all = data[self.ctx.resp_nme]
        w_all = data[self.ctx.weight_nme]

        splitter = ShuffleSplit(
            n_splits=1,
            test_size=self.ctx.prop_test,
            random_state=self.ctx.rand_seed,
        )
        train_idx, val_idx = next(splitter.split(X_all))
        X_train = X_all.iloc[train_idx]
        y_train = y_all.iloc[train_idx]
        w_train = w_all.iloc[train_idx]
        X_val = X_all.iloc[val_idx]
        y_val = y_all.iloc[val_idx]
        w_val = w_all.iloc[val_idx]

        self.model = self._build_model(self.best_params)
        self.model.fit(
            X_train,
            y_train,
            w_train=w_train,
            X_val=X_val,
            y_val=y_val,
            w_val=w_val,
            trial=None,
        )
        self.ctx.model_label.append(self.label)
        self._predict_and_cache(self.model, pred_prefix='gnn', use_oht=True)
        self.ctx.gnn_best = self.model

        # 若配置了 geo_feature_nmes，则同时刷新 geo token，供 FT 作为输入使用。
        if self.ctx.config.geo_feature_nmes:
            self.prepare_geo_tokens(force=True)

    def prepare_geo_tokens(self, force: bool = False) -> None:
        """训练/更新用于 geo token 的 GNN 编码器，并将 geo token 注入 FT 输入。"""
        geo_cols = list(self.ctx.config.geo_feature_nmes or [])
        if not geo_cols:
            return
        if (not force) and self.ctx.train_geo_tokens is not None and self.ctx.test_geo_tokens is not None:
            return

        result = self.ctx._build_geo_tokens()
        if result is None:
            return
        train_tokens, test_tokens, cols, geo_gnn = result
        self.ctx.train_geo_tokens = train_tokens
        self.ctx.test_geo_tokens = test_tokens
        self.ctx.geo_token_cols = cols
        self.ctx.geo_gnn_model = geo_gnn
        print(f"[GeoToken][GNNTrainer] Generated {len(cols)} dims and injected into FT.", flush=True)

    def save(self) -> None:
        if self.model is None:
            print(f"[save] Warning: No model to save for {self.label}")
            return
        path = self.output.model_path(self._get_model_filename())
        base_gnn = getattr(self.model, "_unwrap_gnn", lambda: None)()
        state = None if base_gnn is None else base_gnn.state_dict()
        payload = {
            "best_params": self.best_params,
            "state_dict": state,
        }
        torch.save(payload, path)

    def load(self) -> None:
        path = self.output.model_path(self._get_model_filename())
        if not os.path.exists(path):
            print(f"[load] Warning: Model file not found: {path}")
            return
        payload = torch.load(path, map_location='cpu')
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid GNN checkpoint: {path}")
        params = payload.get("best_params") or {}
        state_dict = payload.get("state_dict")
        model = self._build_model(params)
        if params:
            model.set_params(dict(params))
        base_gnn = getattr(model, "_unwrap_gnn", lambda: None)()
        if base_gnn is not None and state_dict is not None:
            base_gnn.load_state_dict(state_dict, strict=False)
        self.model = model
        self.best_params = dict(params) if isinstance(params, dict) else None
        self.ctx.gnn_best = self.model


class XGBTrainer(TrainerBase):
    def __init__(self, context: "BayesOptModel") -> None:
        super().__init__(context, 'Xgboost', 'Xgboost')
        self.model: Optional[xgb.XGBModel] = None
        self._xgb_use_gpu = False
        self._xgb_gpu_warned = False

    def _build_estimator(self) -> xgb.XGBModel:
        use_gpu = bool(self.ctx.use_gpu and _xgb_cuda_available())
        self._xgb_use_gpu = use_gpu
        params = dict(
            objective=self.ctx.obj,
            random_state=self.ctx.rand_seed,
            subsample=0.9,
            tree_method='gpu_hist' if use_gpu else 'hist',
            enable_categorical=True,
            predictor='gpu_predictor' if use_gpu else 'cpu_predictor'
        )
        if self.ctx.use_gpu and not use_gpu and not self._xgb_gpu_warned:
            print(
                "[XGBoost] CUDA requested but not available; falling back to CPU.",
                flush=True,
            )
            self._xgb_gpu_warned = True
        if use_gpu:
            params['gpu_id'] = 0
            print(f">>> XGBoost using GPU ID: 0 (Single GPU Mode)")
        if self.ctx.task_type == 'classification':
            params.setdefault("eval_metric", "logloss")
            return xgb.XGBClassifier(**params)
        return xgb.XGBRegressor(**params)

    def cross_val(self, trial: optuna.trial.Trial) -> float:
        learning_rate = trial.suggest_float(
            'learning_rate', 1e-5, 1e-1, log=True)
        gamma = trial.suggest_float('gamma', 0, 10000)
        max_depth_max = max(
            3, int(getattr(self.config, "xgb_max_depth_max", 25)))
        n_estimators_max = max(
            10, int(getattr(self.config, "xgb_n_estimators_max", 500)))
        max_depth = trial.suggest_int('max_depth', 3, max_depth_max)
        n_estimators = trial.suggest_int(
            'n_estimators', 10, n_estimators_max, step=10)
        min_child_weight = trial.suggest_int(
            'min_child_weight', 100, 10000, step=100)
        reg_alpha = trial.suggest_float('reg_alpha', 1e-10, 1, log=True)
        reg_lambda = trial.suggest_float('reg_lambda', 1e-10, 1, log=True)
        if trial is not None:
            print(
                f"[Optuna][Xgboost] trial_id={trial.number} max_depth={max_depth} "
                f"n_estimators={n_estimators}",
                flush=True,
            )
        if max_depth >= 20 and n_estimators >= 300:
            raise optuna.TrialPruned(
                "XGB config is likely too slow (max_depth>=20 & n_estimators>=300)")
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
        tweedie_variance_power = None
        if self.ctx.task_type != 'classification':
            if self.ctx.obj == 'reg:tweedie':
                tweedie_variance_power = trial.suggest_float(
                    'tweedie_variance_power', 1, 2)
                params['tweedie_variance_power'] = tweedie_variance_power
            elif self.ctx.obj == 'count:poisson':
                tweedie_variance_power = 1
            elif self.ctx.obj == 'reg:gamma':
                tweedie_variance_power = 2
            else:
                tweedie_variance_power = 1.5
        X_all = self.ctx.train_data[self.ctx.factor_nmes]
        y_all = self.ctx.train_data[self.ctx.resp_nme].values
        w_all = self.ctx.train_data[self.ctx.weight_nme].values

        losses: List[float] = []
        for train_idx, val_idx in self.ctx.cv.split(X_all):
            X_train = X_all.iloc[train_idx]
            y_train = y_all[train_idx]
            w_train = w_all[train_idx]
            X_val = X_all.iloc[val_idx]
            y_val = y_all[val_idx]
            w_val = w_all[val_idx]

            clf = self._build_estimator()
            clf.set_params(**params)
            fit_kwargs = {
                k: v for k, v in (self.ctx.fit_params or {}).items()
                if k != "sample_weight"
            }
            fit_kwargs["sample_weight"] = w_train
            clf.fit(X_train, y_train, **fit_kwargs)

            if self.ctx.task_type == 'classification':
                y_pred = clf.predict_proba(X_val)[:, 1]
                y_pred = np.clip(y_pred, EPS, 1 - EPS)
                loss = log_loss(y_val, y_pred, sample_weight=w_val)
            else:
                y_pred = clf.predict(X_val)
                y_pred_safe = np.maximum(y_pred, EPS)
                loss = mean_tweedie_deviance(
                    y_val,
                    y_pred_safe,
                    sample_weight=w_val,
                    power=tweedie_variance_power,
                )
            losses.append(float(loss))
            self._clean_gpu()

        return float(np.mean(losses))

    def train(self) -> None:
        if not self.best_params:
            raise RuntimeError('请先运行 tune() 以获得 XGB 最优参数。')
        self.model = self._build_estimator()
        self.model.set_params(**self.best_params)
        predict_fn = None
        if self.ctx.task_type == 'classification':
            def _predict_proba(X, **_kwargs):
                return self.model.predict_proba(X)[:, 1]
            predict_fn = _predict_proba
        self._fit_predict_cache(
            self.model,
            self.ctx.train_data[self.ctx.factor_nmes],
            self.ctx.train_data[self.ctx.resp_nme].values,
            sample_weight=None,
            pred_prefix='xgb',
            fit_kwargs=self.ctx.fit_params,
            sample_weight_arg=None,  # 样本权重已通过 fit_kwargs 传入
            predict_fn=predict_fn
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
        param_space = {
            "alpha": lambda t: t.suggest_float('alpha', 1e-6, 1e2, log=True),
            "l1_ratio": lambda t: t.suggest_float('l1_ratio', 0.0, 1.0)
        }
        if self.ctx.task_type == 'regression' and self.ctx.obj == 'reg:tweedie':
            param_space["tweedie_power"] = lambda t: t.suggest_float(
                'tweedie_power', 1.0, 2.0)

        def data_provider():
            data = self.ctx.train_oht_data if self.ctx.train_oht_data is not None else self.ctx.train_oht_scl_data
            assert data is not None, "Preprocessed training data is missing."
            return data[self.ctx.var_nmes], data[self.ctx.resp_nme], data[self.ctx.weight_nme]

        def preprocess_fn(X_train, X_val):
            X_train_s, X_val_s, _ = self._standardize_fold(
                X_train, X_val, self.ctx.num_features)
            return self._prepare_design(X_train_s), self._prepare_design(X_val_s)

        metric_ctx: Dict[str, Any] = {}

        def model_builder(params):
            family = self._select_family(params.get("tweedie_power"))
            metric_ctx["family"] = family
            metric_ctx["tweedie_power"] = params.get("tweedie_power")
            return {
                "family": family,
                "alpha": params["alpha"],
                "l1_ratio": params["l1_ratio"],
                "tweedie_power": params.get("tweedie_power")
            }

        def fit_predict(model_cfg, X_train, y_train, w_train, X_val, y_val, w_val, _trial):
            glm = sm.GLM(y_train, X_train,
                         family=model_cfg["family"],
                         freq_weights=w_train)
            result = glm.fit_regularized(
                alpha=model_cfg["alpha"],
                L1_wt=model_cfg["l1_ratio"],
                maxiter=200
            )
            return result.predict(X_val)

        def metric_fn(y_true, y_pred, weight):
            if self.ctx.task_type == 'classification':
                y_pred_clipped = np.clip(y_pred, EPS, 1 - EPS)
                return log_loss(y_true, y_pred_clipped, sample_weight=weight)
            y_pred_safe = np.maximum(y_pred, EPS)
            return mean_tweedie_deviance(
                y_true,
                y_pred_safe,
                sample_weight=weight,
                power=self._metric_power(
                    metric_ctx.get("family"), metric_ctx.get("tweedie_power"))
            )

        return self.cross_val_generic(
            trial=trial,
            hyperparameter_space=param_space,
            data_provider=data_provider,
            model_builder=model_builder,
            metric_fn=metric_fn,
            preprocess_fn=preprocess_fn,
            fit_predict_fn=fit_predict,
            splitter=self.ctx.cv.split(self.ctx.train_oht_data[self.ctx.var_nmes]
                                       if self.ctx.train_oht_data is not None else self.ctx.train_oht_scl_data[self.ctx.var_nmes])
        )

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
        self.enable_distributed_optuna = bool(context.config.use_resn_ddp)

    # ========= 交叉验证（BayesOpt 用） =========
    def cross_val(self, trial: optuna.trial.Trial) -> float:
        # 针对 ResNet 的交叉验证流程，重点控制显存：
        #   - 每个 fold 单独创建 ResNetSklearn，结束立刻释放资源；
        #   - fold 完成后迁移模型到 CPU，删除对象并调用 gc/empty_cache；
        #   - 可选：BayesOpt 期间只抽样部分训练集以减少显存压力。

        base_tw_power = self.ctx.default_tweedie_power()

        def data_provider():
            data = self.ctx.train_oht_data if self.ctx.train_oht_data is not None else self.ctx.train_oht_scl_data
            assert data is not None, "Preprocessed training data is missing."
            return data[self.ctx.var_nmes], data[self.ctx.resp_nme], data[self.ctx.weight_nme]

        metric_ctx: Dict[str, Any] = {}

        def model_builder(params):
            power = params.get("tw_power", base_tw_power)
            metric_ctx["tw_power"] = power
            return ResNetSklearn(
                model_nme=self.ctx.model_nme,
                input_dim=len(self.ctx.var_nmes),
                hidden_dim=params["hidden_dim"],
                block_num=params["block_num"],
                task_type=self.ctx.task_type,
                epochs=self.ctx.epochs,
                tweedie_power=power,
                learning_rate=params["learning_rate"],
                patience=5,
                use_layernorm=True,
                dropout=0.1,
                residual_scale=0.1,
                use_data_parallel=self.ctx.config.use_resn_data_parallel,
                use_ddp=self.ctx.config.use_resn_ddp
            )

        def preprocess_fn(X_train, X_val):
            X_train_s, X_val_s, _ = self._standardize_fold(
                X_train, X_val, self.ctx.num_features)
            return X_train_s, X_val_s

        def fit_predict(model, X_train, y_train, w_train, X_val, y_val, w_val, trial_obj):
            model.fit(
                X_train, y_train, w_train,
                X_val, y_val, w_val,
                trial=trial_obj
            )
            return model.predict(X_val)

        def metric_fn(y_true, y_pred, weight):
            if self.ctx.task_type == 'regression':
                return mean_tweedie_deviance(
                    y_true,
                    y_pred,
                    sample_weight=weight,
                    power=metric_ctx.get("tw_power", base_tw_power)
                )
            return log_loss(y_true, y_pred, sample_weight=weight)

        sample_cap = data_provider()[0]
        max_rows_for_resnet_bo = min(100000, int(len(sample_cap)/5))

        return self.cross_val_generic(
            trial=trial,
            hyperparameter_space={
                "learning_rate": lambda t: t.suggest_float('learning_rate', 1e-6, 1e-2, log=True),
                "hidden_dim": lambda t: t.suggest_int('hidden_dim', 8, 32, step=2),
                "block_num": lambda t: t.suggest_int('block_num', 2, 10),
                **({"tw_power": lambda t: t.suggest_float('tw_power', 1.0, 2.0)} if self.ctx.task_type == 'regression' and self.ctx.obj == 'reg:tweedie' else {})
            },
            data_provider=data_provider,
            model_builder=model_builder,
            metric_fn=metric_fn,
            sample_limit=max_rows_for_resnet_bo if len(
                sample_cap) > max_rows_for_resnet_bo > 0 else None,
            preprocess_fn=preprocess_fn,
            fit_predict_fn=fit_predict,
            cleanup_fn=lambda m: getattr(
                getattr(m, "resnet", None), "to", lambda *_args, **_kwargs: None)("cpu")
        )

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
        loss_plot_path = self.output.plot_path(
            f'loss_{self.ctx.model_nme}_{self.model_name_prefix}.png')
        self.model.loss_curve_path = loss_plot_path

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
    # ResNet 以 state_dict 形式保存，需要专用的加载流程，因此保留自定义加载方法
    # 保存逻辑已在 TrainerBase 中实现（会自动检查 .resnet 属性）

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
        self.enable_distributed_optuna = bool(context.config.use_ft_ddp)
        self._cv_geo_warned = False

    def _resolve_adaptive_heads(self,
                                d_model: int,
                                requested_heads: Optional[int] = None) -> Tuple[int, bool]:
        d_model = int(d_model)
        if d_model <= 0:
            raise ValueError(f"Invalid d_model={d_model}, expected > 0.")

        default_heads = max(2, d_model // 16)
        base_heads = default_heads if requested_heads is None else int(
            requested_heads)
        base_heads = max(1, min(base_heads, d_model))

        if d_model % base_heads == 0:
            return base_heads, False

        for candidate in range(min(d_model, base_heads), 0, -1):
            if d_model % candidate == 0:
                return candidate, True
        return 1, True

    def _build_geo_tokens_for_split(self,
                                    X_train: pd.DataFrame,
                                    X_val: pd.DataFrame,
                                    geo_params: Optional[Dict[str, Any]] = None):
        if not self.ctx.config.geo_feature_nmes:
            return None
        orig_train = self.ctx.train_data
        orig_test = self.ctx.test_data
        try:
            self.ctx.train_data = orig_train.loc[X_train.index].copy()
            self.ctx.test_data = orig_train.loc[X_val.index].copy()
            return self.ctx._build_geo_tokens(geo_params)
        finally:
            self.ctx.train_data = orig_train
            self.ctx.test_data = orig_test

    def cross_val_unsupervised(self, trial: Optional[optuna.trial.Trial]) -> float:
        """Optuna 目标 A：最小化 masked 重建的验证损失。"""
        param_space: Dict[str, Callable[[optuna.trial.Trial], Any]] = {
            "learning_rate": lambda t: t.suggest_float('learning_rate', 1e-5, 5e-3, log=True),
            "d_model": lambda t: t.suggest_int('d_model', 16, 128, step=16),
            "n_layers": lambda t: t.suggest_int('n_layers', 2, 8),
            "dropout": lambda t: t.suggest_float('dropout', 0.0, 0.3),
            "mask_prob_num": lambda t: t.suggest_float('mask_prob_num', 0.05, 0.4),
            "mask_prob_cat": lambda t: t.suggest_float('mask_prob_cat', 0.05, 0.4),
            "num_loss_weight": lambda t: t.suggest_float('num_loss_weight', 0.25, 4.0, log=True),
            "cat_loss_weight": lambda t: t.suggest_float('cat_loss_weight', 0.25, 4.0, log=True),
        }

        params: Optional[Dict[str, Any]] = None
        if self._distributed_forced_params is not None:
            params = self._distributed_forced_params
            self._distributed_forced_params = None
        else:
            if trial is None:
                raise RuntimeError(
                    "Missing Optuna trial for parameter sampling.")
            params = {name: sampler(trial)
                      for name, sampler in param_space.items()}
            if self._should_use_distributed_optuna():
                self._distributed_prepare_trial(params)

        X_all = self.ctx.train_data[self.ctx.factor_nmes]
        max_rows_for_ft_bo = min(1_000_000, int(len(X_all) / 2))
        if max_rows_for_ft_bo > 0 and len(X_all) > max_rows_for_ft_bo:
            X_all = X_all.sample(n=max_rows_for_ft_bo,
                                 random_state=self.ctx.rand_seed)

        splitter = ShuffleSplit(
            n_splits=1,
            test_size=self.ctx.prop_test,
            random_state=self.ctx.rand_seed
        )
        train_idx, val_idx = next(splitter.split(X_all))
        X_train = X_all.iloc[train_idx]
        X_val = X_all.iloc[val_idx]
        geo_train = geo_val = None
        if self.ctx.config.geo_feature_nmes:
            built = self._build_geo_tokens_for_split(X_train, X_val, params)
            if built is not None:
                geo_train, geo_val, _, _ = built
            elif not self._cv_geo_warned:
                print(
                    "[FTTrainer] Geo tokens unavailable for CV split; continue without geo tokens.",
                    flush=True,
                )
                self._cv_geo_warned = True

        d_model = int(params["d_model"])
        n_layers = int(params["n_layers"])
        token_count = len(self.ctx.num_features) + len(self.ctx.cate_list)
        if geo_train is not None:
            token_count += 1
        approx_units = d_model * n_layers * max(1, token_count)
        if approx_units > 12_000_000:
            raise optuna.TrialPruned(
                f"config exceeds safe memory budget (approx_units={approx_units})")

        adaptive_heads, _ = self._resolve_adaptive_heads(
            d_model=d_model,
            requested_heads=params.get("n_heads")
        )

        mask_prob_num = float(params.get("mask_prob_num", 0.15))
        mask_prob_cat = float(params.get("mask_prob_cat", 0.15))
        num_loss_weight = float(params.get("num_loss_weight", 1.0))
        cat_loss_weight = float(params.get("cat_loss_weight", 1.0))

        model_params = dict(params)
        model_params["n_heads"] = adaptive_heads
        for k in ("mask_prob_num", "mask_prob_cat", "num_loss_weight", "cat_loss_weight"):
            model_params.pop(k, None)

        model = FTTransformerSklearn(
            model_nme=self.ctx.model_nme,
            num_cols=self.ctx.num_features,
            cat_cols=self.ctx.cate_list,
            task_type=self.ctx.task_type,
            epochs=self.ctx.epochs,
            patience=5,
            use_data_parallel=self.ctx.config.use_ft_data_parallel,
            use_ddp=self.ctx.config.use_ft_ddp
        )
        model.set_params(model_params)
        try:
            return float(model.fit_unsupervised(
                X_train,
                X_val=X_val,
                trial=trial,
                geo_train=geo_train,
                geo_val=geo_val,
                mask_prob_num=mask_prob_num,
                mask_prob_cat=mask_prob_cat,
                num_loss_weight=num_loss_weight,
                cat_loss_weight=cat_loss_weight
            ))
        finally:
            getattr(getattr(model, "ft", None), "to",
                    lambda *_args, **_kwargs: None)("cpu")
            self._clean_gpu()

    def cross_val(self, trial: optuna.trial.Trial) -> float:
        # 针对 FT-Transformer 的交叉验证，重点同样在显存控制：
        #   - 收缩超参搜索空间，防止不必要的超大模型；
        #   - 每个 fold 结束后立即释放 GPU 显存，确保下一个 trial 顺利进行。
        # 超参空间适当缩小一点，避免特别大的模型
        param_space: Dict[str, Callable[[optuna.trial.Trial], Any]] = {
            "learning_rate": lambda t: t.suggest_float('learning_rate', 1e-5, 5e-4, log=True),
            # "d_model": lambda t: t.suggest_int('d_model', 8, 64, step=8),
            "d_model": lambda t: t.suggest_int('d_model', 16, 128, step=16),
            "n_layers": lambda t: t.suggest_int('n_layers', 2, 8),
            "dropout": lambda t: t.suggest_float('dropout', 0.0, 0.2)
        }
        if self.ctx.task_type == 'regression' and self.ctx.obj == 'reg:tweedie':
            param_space["tw_power"] = lambda t: t.suggest_float(
                'tw_power', 1.0, 2.0)
        geo_enabled = bool(
            self.ctx.geo_token_cols or self.ctx.config.geo_feature_nmes)
        if geo_enabled:
            # 仅在启用地理 token 时调节 GNN 相关超参
            param_space.update({
                "geo_token_hidden_dim": lambda t: t.suggest_int('geo_token_hidden_dim', 16, 128, step=16),
                "geo_token_layers": lambda t: t.suggest_int('geo_token_layers', 1, 4),
                "geo_token_k_neighbors": lambda t: t.suggest_int('geo_token_k_neighbors', 5, 20),
                "geo_token_dropout": lambda t: t.suggest_float('geo_token_dropout', 0.0, 0.3),
                "geo_token_learning_rate": lambda t: t.suggest_float('geo_token_learning_rate', 1e-4, 5e-3, log=True),
            })

        metric_ctx: Dict[str, Any] = {}

        def data_provider():
            data = self.ctx.train_data
            return data[self.ctx.factor_nmes], data[self.ctx.resp_nme], data[self.ctx.weight_nme]

        def model_builder(params):
            d_model = int(params["d_model"])
            n_layers = int(params["n_layers"])
            token_count = len(self.ctx.factor_nmes) + \
                (1 if geo_enabled else 0)
            approx_units = d_model * n_layers * max(1, token_count)
            if approx_units > 12_000_000:
                print(
                    f"[FTTrainer] Trial pruned early: d_model={d_model}, n_layers={n_layers} -> approx_units={approx_units}")
                raise optuna.TrialPruned(
                    "config exceeds safe memory budget; prune before training")
            geo_params_local = {k: v for k, v in params.items()
                                if k.startswith("geo_token_")}

            tw_power = params.get("tw_power")
            if self.ctx.task_type == 'regression':
                base_tw = self.ctx.default_tweedie_power()
                if self.ctx.obj in ('count:poisson', 'reg:gamma'):
                    tw_power = base_tw
                elif tw_power is None:
                    tw_power = base_tw
            metric_ctx["tw_power"] = tw_power

            adaptive_heads, _ = self._resolve_adaptive_heads(
                d_model=d_model,
                requested_heads=params.get("n_heads")
            )

            return FTTransformerSklearn(
                model_nme=self.ctx.model_nme,
                num_cols=self.ctx.num_features,
                cat_cols=self.ctx.cate_list,
                d_model=d_model,
                n_heads=adaptive_heads,
                n_layers=n_layers,
                dropout=params["dropout"],
                task_type=self.ctx.task_type,
                epochs=self.ctx.epochs,
                tweedie_power=tw_power,
                learning_rate=params["learning_rate"],
                patience=5,
                use_data_parallel=self.ctx.config.use_ft_data_parallel,
                use_ddp=self.ctx.config.use_ft_ddp
            ).set_params({"_geo_params": geo_params_local} if geo_enabled else {})

        def fit_predict(model, X_train, y_train, w_train, X_val, y_val, w_val, trial_obj):
            geo_train = geo_val = None
            if geo_enabled:
                geo_params = getattr(model, "_geo_params", {})
                built = self._build_geo_tokens_for_split(
                    X_train, X_val, geo_params)
                if built is not None:
                    geo_train, geo_val, _, _ = built
                elif not self._cv_geo_warned:
                    print(
                        "[FTTrainer] Geo tokens unavailable for CV split; continue without geo tokens.",
                        flush=True,
                    )
                    self._cv_geo_warned = True
            model.fit(
                X_train, y_train, w_train,
                X_val, y_val, w_val,
                trial=trial_obj,
                geo_train=geo_train,
                geo_val=geo_val
            )
            return model.predict(X_val, geo_tokens=geo_val)

        def metric_fn(y_true, y_pred, weight):
            if self.ctx.task_type == 'regression':
                return mean_tweedie_deviance(
                    y_true,
                    y_pred,
                    sample_weight=weight,
                    power=metric_ctx.get("tw_power", 1.5)
                )
            return log_loss(y_true, y_pred, sample_weight=weight)

        data_for_cap = data_provider()[0]
        max_rows_for_ft_bo = min(1000000, int(len(data_for_cap)/2))

        return self.cross_val_generic(
            trial=trial,
            hyperparameter_space=param_space,
            data_provider=data_provider,
            model_builder=model_builder,
            metric_fn=metric_fn,
            sample_limit=max_rows_for_ft_bo if len(
                data_for_cap) > max_rows_for_ft_bo > 0 else None,
            fit_predict_fn=fit_predict,
            cleanup_fn=lambda m: getattr(
                getattr(m, "ft", None), "to", lambda *_args, **_kwargs: None)("cpu")
        )

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
        # self.model.set_params(self.best_params)
        resolved_params = dict(self.best_params)
        adaptive_heads, heads_adjusted = self._resolve_adaptive_heads(
            d_model=resolved_params.get("d_model", self.model.d_model),
            requested_heads=resolved_params.get("n_heads")
        )
        if heads_adjusted:
            print(f"[FTTrainer] Auto-adjusted n_heads from "
                  f"{resolved_params.get('n_heads')} to {adaptive_heads} "
                  f"(d_model={resolved_params.get('d_model', self.model.d_model)}).")
        resolved_params["n_heads"] = adaptive_heads
        self.model.set_params(resolved_params)
        self.best_params = resolved_params
        loss_plot_path = self.output.plot_path(
            f'loss_{self.ctx.model_nme}_{self.model_name_prefix}.png')
        self.model.loss_curve_path = loss_plot_path
        geo_train = self.ctx.train_geo_tokens
        geo_test = self.ctx.test_geo_tokens
        fit_kwargs = {}
        predict_kwargs_train = None
        predict_kwargs_test = None
        if geo_train is not None and geo_test is not None:
            fit_kwargs["geo_train"] = geo_train
            predict_kwargs_train = {"geo_tokens": geo_train}
            predict_kwargs_test = {"geo_tokens": geo_test}
        self._fit_predict_cache(
            self.model,
            self.ctx.train_data[self.ctx.factor_nmes],
            self.ctx.train_data[self.ctx.resp_nme],
            sample_weight=self.ctx.train_data[self.ctx.weight_nme],
            pred_prefix='ft',
            sample_weight_arg='w_train',
            fit_kwargs=fit_kwargs,
            predict_kwargs_train=predict_kwargs_train,
            predict_kwargs_test=predict_kwargs_test
        )
        self.ctx.ft_best = self.model

    def train_as_feature(self, pred_prefix: str = "ft_feat", feature_mode: str = "prediction") -> None:
        """训练 FT-Transformer 仅用于生成特征（不作为最终预测模型记录）。"""
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
        resolved_params = dict(self.best_params)
        adaptive_heads, heads_adjusted = self._resolve_adaptive_heads(
            d_model=resolved_params.get("d_model", self.model.d_model),
            requested_heads=resolved_params.get("n_heads")
        )
        if heads_adjusted:
            print(f"[FTTrainer] Auto-adjusted n_heads from "
                  f"{resolved_params.get('n_heads')} to {adaptive_heads} "
                  f"(d_model={resolved_params.get('d_model', self.model.d_model)}).")
        resolved_params["n_heads"] = adaptive_heads
        self.model.set_params(resolved_params)
        self.best_params = resolved_params

        geo_train = self.ctx.train_geo_tokens
        geo_test = self.ctx.test_geo_tokens
        fit_kwargs = {}
        predict_kwargs_train = None
        predict_kwargs_test = None
        if geo_train is not None and geo_test is not None:
            fit_kwargs["geo_train"] = geo_train
            predict_kwargs_train = {"geo_tokens": geo_train}
            predict_kwargs_test = {"geo_tokens": geo_test}

        if feature_mode not in ("prediction", "embedding"):
            raise ValueError(
                f"Unsupported feature_mode='{feature_mode}', expected 'prediction' or 'embedding'.")
        if feature_mode == "embedding":
            predict_kwargs_train = dict(predict_kwargs_train or {})
            predict_kwargs_test = dict(predict_kwargs_test or {})
            predict_kwargs_train["return_embedding"] = True
            predict_kwargs_test["return_embedding"] = True

        self._fit_predict_cache(
            self.model,
            self.ctx.train_data[self.ctx.factor_nmes],
            self.ctx.train_data[self.ctx.resp_nme],
            sample_weight=self.ctx.train_data[self.ctx.weight_nme],
            pred_prefix=pred_prefix,
            sample_weight_arg='w_train',
            fit_kwargs=fit_kwargs,
            predict_kwargs_train=predict_kwargs_train,
            predict_kwargs_test=predict_kwargs_test,
            record_label=False
        )

    def pretrain_unsupervised_as_feature(self,
                                         pred_prefix: str = "ft_uemb",
                                         params: Optional[Dict[str,
                                                               Any]] = None,
                                         mask_prob_num: float = 0.15,
                                         mask_prob_cat: float = 0.15,
                                         num_loss_weight: float = 1.0,
                                         cat_loss_weight: float = 1.0) -> None:
        """自监督预训练（masked 重建），并将 embedding 特征缓存到数据表中。"""
        self.model = FTTransformerSklearn(
            model_nme=self.ctx.model_nme,
            num_cols=self.ctx.num_features,
            cat_cols=self.ctx.cate_list,
            task_type=self.ctx.task_type,
            use_data_parallel=self.ctx.config.use_ft_data_parallel,
            use_ddp=self.ctx.config.use_ft_ddp
        )
        resolved_params = dict(params or {})
        # 若调用方未显式覆盖，则允许复用监督学习调参得到的结构参数。
        if not resolved_params and self.best_params:
            resolved_params = dict(self.best_params)

        # 若 params 中包含 masked 重建相关字段，则优先使用 params 的设置。
        mask_prob_num = float(resolved_params.pop(
            "mask_prob_num", mask_prob_num))
        mask_prob_cat = float(resolved_params.pop(
            "mask_prob_cat", mask_prob_cat))
        num_loss_weight = float(resolved_params.pop(
            "num_loss_weight", num_loss_weight))
        cat_loss_weight = float(resolved_params.pop(
            "cat_loss_weight", cat_loss_weight))

        adaptive_heads, heads_adjusted = self._resolve_adaptive_heads(
            d_model=resolved_params.get("d_model", self.model.d_model),
            requested_heads=resolved_params.get("n_heads")
        )
        if heads_adjusted:
            print(f"[FTTrainer] Auto-adjusted n_heads from "
                  f"{resolved_params.get('n_heads')} to {adaptive_heads} "
                  f"(d_model={resolved_params.get('d_model', self.model.d_model)}).")
        resolved_params["n_heads"] = adaptive_heads
        if resolved_params:
            self.model.set_params(resolved_params)

        loss_plot_path = self.output.plot_path(
            f'loss_{self.ctx.model_nme}_FTTransformerUnsupervised.png')
        self.model.loss_curve_path = loss_plot_path

        # 构造一个简单的 holdout 划分，用于预训练阶段的 early-stopping。
        X_all = self.ctx.train_data[self.ctx.factor_nmes]
        idx = np.arange(len(X_all))
        splitter = ShuffleSplit(
            n_splits=1,
            test_size=self.ctx.prop_test,
            random_state=self.ctx.rand_seed
        )
        train_idx, val_idx = next(splitter.split(idx))
        X_tr = X_all.iloc[train_idx]
        X_val = X_all.iloc[val_idx]

        geo_all = self.ctx.train_geo_tokens
        geo_tr = geo_val = None
        if geo_all is not None:
            geo_tr = geo_all.loc[X_tr.index]
            geo_val = geo_all.loc[X_val.index]

        self.model.fit_unsupervised(
            X_tr,
            X_val=X_val,
            geo_train=geo_tr,
            geo_val=geo_val,
            mask_prob_num=mask_prob_num,
            mask_prob_cat=mask_prob_cat,
            num_loss_weight=num_loss_weight,
            cat_loss_weight=cat_loss_weight
        )

        geo_train_full = self.ctx.train_geo_tokens
        geo_test_full = self.ctx.test_geo_tokens
        predict_kwargs_train = {"return_embedding": True}
        predict_kwargs_test = {"return_embedding": True}
        if geo_train_full is not None and geo_test_full is not None:
            predict_kwargs_train["geo_tokens"] = geo_train_full
            predict_kwargs_test["geo_tokens"] = geo_test_full

        self._predict_and_cache(
            self.model,
            pred_prefix=pred_prefix,
            predict_kwargs_train=predict_kwargs_train,
            predict_kwargs_test=predict_kwargs_test
        )


# =============================================================================
# BayesOpt 调度与 SHAP 工具集
# =============================================================================
class BayesOptModel:
    def __init__(self, train_data, test_data,
                 model_nme, resp_nme, weight_nme, factor_nmes: Optional[List[str]] = None, task_type='regression',
                 binary_resp_nme=None,
                 cate_list=None, prop_test=0.25, rand_seed=None,
                 epochs=100, use_gpu=True,
                 use_resn_data_parallel: bool = False, use_ft_data_parallel: bool = False,
                 use_gnn_data_parallel: bool = False,
                 use_resn_ddp: bool = False, use_ft_ddp: bool = False,
                 use_gnn_ddp: bool = False,
                 output_dir: Optional[str] = None,
                 gnn_use_approx_knn: bool = True,
                 gnn_approx_knn_threshold: int = 50000,
                 gnn_graph_cache: Optional[str] = None,
                 gnn_max_gpu_knn_nodes: Optional[int] = 200000,
                 gnn_knn_gpu_mem_ratio: float = 0.9,
                 gnn_knn_gpu_mem_overhead: float = 2.0,
                 ft_role: str = "model",
                 ft_feature_prefix: str = "ft_emb",
                 infer_categorical_max_unique: int = 50,
                 infer_categorical_max_ratio: float = 0.05,
                 reuse_best_params: bool = False,
                 xgb_max_depth_max: int = 25,
                 xgb_n_estimators_max: int = 500,
                 optuna_storage: Optional[str] = None,
                 optuna_study_prefix: Optional[str] = None,
                 best_params_files: Optional[Dict[str, str]] = None):
        """封装各类训练器的 BayesOpt 调度入口。

        参数:
            train_data: 训练集 DataFrame。
            test_data: 测试集 DataFrame。
            model_nme: 模型名称前缀，用于输出文件。
            resp_nme: 目标列名。
            weight_nme: 样本权重列名。
            factor_nmes: 特征列名列表。
            task_type: 'regression' 或 'classification'。
            binary_resp_nme: 可选的二分类目标，用于成交率曲线。
            cate_list: 类别型特征列表。
            prop_test: 交叉验证中验证集的占比。
            rand_seed: 随机种子。
            epochs: 神经网络训练轮数。
            use_gpu: 是否优先使用 GPU。
            use_resn_data_parallel: ResNet 是否启用 DataParallel。
            use_ft_data_parallel: FTTransformer 是否启用 DataParallel。
            use_gnn_data_parallel: GNN 是否启用 DataParallel。
            use_resn_ddp: ResNet 是否启用 DDP。
            use_ft_ddp: FTTransformer 是否启用 DDP。
            use_gnn_ddp: GNN 是否启用 DDP。
            output_dir: 模型、结果与图表的输出根目录。
            gnn_use_approx_knn: 是否在可用时使用近似 kNN。
            gnn_approx_knn_threshold: 触发近似 kNN 的行数阈值。
            gnn_graph_cache: 可选的邻接矩阵缓存路径。
            gnn_max_gpu_knn_nodes: 超过该节点数则强制使用 CPU kNN 以避免 GPU OOM。
            gnn_knn_gpu_mem_ratio: GPU kNN 允许使用的可用显存比例。
            gnn_knn_gpu_mem_overhead: GPU kNN 估算的临时显存放大倍数。
        """
        inferred_factors, inferred_cats = infer_factor_and_cate_list(
            train_df=train_data,
            test_df=test_data,
            resp_nme=resp_nme,
            weight_nme=weight_nme,
            binary_resp_nme=binary_resp_nme,
            factor_nmes=factor_nmes,
            cate_list=cate_list,
            infer_categorical_max_unique=int(infer_categorical_max_unique),
            infer_categorical_max_ratio=float(infer_categorical_max_ratio),
        )

        cfg = BayesOptConfig(
            model_nme=model_nme,
            task_type=task_type,
            resp_nme=resp_nme,
            weight_nme=weight_nme,
            factor_nmes=list(inferred_factors),
            binary_resp_nme=binary_resp_nme,
            cate_list=list(inferred_cats) if inferred_cats else None,
            prop_test=prop_test,
            rand_seed=rand_seed,
            epochs=epochs,
            use_gpu=use_gpu,
            xgb_max_depth_max=int(xgb_max_depth_max),
            xgb_n_estimators_max=int(xgb_n_estimators_max),
            use_resn_data_parallel=use_resn_data_parallel,
            use_ft_data_parallel=use_ft_data_parallel,
            use_resn_ddp=use_resn_ddp,
            use_gnn_data_parallel=use_gnn_data_parallel,
            use_ft_ddp=use_ft_ddp,
            use_gnn_ddp=use_gnn_ddp,
            gnn_use_approx_knn=gnn_use_approx_knn,
            gnn_approx_knn_threshold=gnn_approx_knn_threshold,
            gnn_graph_cache=gnn_graph_cache,
            gnn_max_gpu_knn_nodes=gnn_max_gpu_knn_nodes,
            gnn_knn_gpu_mem_ratio=gnn_knn_gpu_mem_ratio,
            gnn_knn_gpu_mem_overhead=gnn_knn_gpu_mem_overhead,
            output_dir=output_dir,
            optuna_storage=optuna_storage,
            optuna_study_prefix=optuna_study_prefix,
            best_params_files=best_params_files,
            ft_role=str(ft_role or "model"),
            ft_feature_prefix=str(ft_feature_prefix or "ft_emb"),
            reuse_best_params=bool(reuse_best_params),
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
        set_global_seed(int(self.rand_seed))
        self.use_gpu = bool(cfg.use_gpu and torch.cuda.is_available())
        self.output_manager = OutputManager(
            cfg.output_dir or os.getcwd(), self.model_nme)

        preprocessor = DatasetPreprocessor(train_data, test_data, cfg).run()
        self.train_data = preprocessor.train_data
        self.test_data = preprocessor.test_data
        self.train_oht_data = preprocessor.train_oht_data
        self.test_oht_data = preprocessor.test_oht_data
        self.train_oht_scl_data = preprocessor.train_oht_scl_data
        self.test_oht_scl_data = preprocessor.test_oht_scl_data
        self.var_nmes = preprocessor.var_nmes
        self.num_features = preprocessor.num_features
        self.cat_categories_for_shap = preprocessor.cat_categories_for_shap
        self.geo_token_cols: List[str] = []
        self.train_geo_tokens: Optional[pd.DataFrame] = None
        self.test_geo_tokens: Optional[pd.DataFrame] = None
        self.geo_gnn_model: Optional[GraphNeuralNetSklearn] = None
        self._add_region_effect()

        self.cv = ShuffleSplit(n_splits=int(1/self.prop_test),
                               test_size=self.prop_test,
                               random_state=self.rand_seed)
        if self.task_type == 'classification':
            self.obj = 'binary:logistic'
        else:  # 回归任务
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
        self.optuna_storage = cfg.optuna_storage
        self.optuna_study_prefix = cfg.optuna_study_prefix or "bayesopt"

        # 记录各模型训练器，后续统一通过标签访问，方便扩展新模型
        self.trainers: Dict[str, TrainerBase] = {
            'glm': GLMTrainer(self),
            'xgb': XGBTrainer(self),
            'resn': ResNetTrainer(self),
            'ft': FTTrainer(self),
            'gnn': GNNTrainer(self),
        }
        self._prepare_geo_tokens()
        self.xgb_best = None
        self.resn_best = None
        self.gnn_best = None
        self.glm_best = None
        self.ft_best = None
        self.best_xgb_params = None
        self.best_resn_params = None
        self.best_gnn_params = None
        self.best_ft_params = None
        self.best_xgb_trial = None
        self.best_resn_trial = None
        self.best_gnn_trial = None
        self.best_ft_trial = None
        self.best_glm_params = None
        self.best_glm_trial = None
        self.xgb_load = None
        self.resn_load = None
        self.gnn_load = None
        self.ft_load = None
        self.version_manager = VersionManager(self.output_manager)

    def default_tweedie_power(self, obj: Optional[str] = None) -> Optional[float]:
        if self.task_type == 'classification':
            return None
        objective = obj or getattr(self, "obj", None)
        if objective == 'count:poisson':
            return 1.0
        if objective == 'reg:gamma':
            return 2.0
        return 1.5

    def _build_geo_tokens(self, params_override: Optional[Dict[str, Any]] = None):
        """内部构建函数，支持传入 trial 覆盖超参，失败则返回 None。"""
        geo_cols = list(self.config.geo_feature_nmes or [])
        if not geo_cols:
            return None

        available = [c for c in geo_cols if c in self.train_data.columns]
        if not available:
            return None

        # 预处理文本/数值：数值填中位数，文本做标签编码，未知映射到额外索引
        proc_train = {}
        proc_test = {}
        for col in available:
            s_train = self.train_data[col]
            s_test = self.test_data[col]
            if pd.api.types.is_numeric_dtype(s_train):
                tr = pd.to_numeric(s_train, errors="coerce")
                te = pd.to_numeric(s_test, errors="coerce")
                med = np.nanmedian(tr)
                proc_train[col] = np.nan_to_num(tr, nan=med).astype(np.float32)
                proc_test[col] = np.nan_to_num(te, nan=med).astype(np.float32)
            else:
                cats = pd.Categorical(s_train.astype(str))
                tr_codes = cats.codes.astype(np.float32, copy=True)
                tr_codes[tr_codes < 0] = len(cats.categories)
                te_cats = pd.Categorical(
                    s_test.astype(str), categories=cats.categories)
                te_codes = te_cats.codes.astype(np.float32, copy=True)
                te_codes[te_codes < 0] = len(cats.categories)
                proc_train[col] = tr_codes
                proc_test[col] = te_codes

        train_geo_raw = pd.DataFrame(proc_train, index=self.train_data.index)
        test_geo_raw = pd.DataFrame(proc_test, index=self.test_data.index)

        scaler = StandardScaler()
        train_geo = pd.DataFrame(
            scaler.fit_transform(train_geo_raw),
            columns=available,
            index=self.train_data.index
        )
        test_geo = pd.DataFrame(
            scaler.transform(test_geo_raw),
            columns=available,
            index=self.test_data.index
        )

        tw_power = self.default_tweedie_power()

        cfg = params_override or {}
        try:
            geo_gnn = GraphNeuralNetSklearn(
                model_nme=f"{self.model_nme}_geo",
                input_dim=len(available),
                hidden_dim=cfg.get("geo_token_hidden_dim",
                                   self.config.geo_token_hidden_dim),
                num_layers=cfg.get("geo_token_layers",
                                   self.config.geo_token_layers),
                k_neighbors=cfg.get("geo_token_k_neighbors",
                                    self.config.geo_token_k_neighbors),
                dropout=cfg.get("geo_token_dropout",
                                self.config.geo_token_dropout),
                learning_rate=cfg.get(
                    "geo_token_learning_rate", self.config.geo_token_learning_rate),
                epochs=int(cfg.get("geo_token_epochs",
                           self.config.geo_token_epochs)),
                patience=5,
                task_type=self.task_type,
                tweedie_power=tw_power,
                use_data_parallel=False,
                use_ddp=False,
                use_approx_knn=self.config.gnn_use_approx_knn,
                approx_knn_threshold=self.config.gnn_approx_knn_threshold,
                graph_cache_path=None,
                max_gpu_knn_nodes=self.config.gnn_max_gpu_knn_nodes,
                knn_gpu_mem_ratio=self.config.gnn_knn_gpu_mem_ratio,
                knn_gpu_mem_overhead=self.config.gnn_knn_gpu_mem_overhead
            )
            geo_gnn.fit(
                train_geo,
                self.train_data[self.resp_nme],
                self.train_data[self.weight_nme]
            )
            train_embed = geo_gnn.encode(train_geo)
            test_embed = geo_gnn.encode(test_geo)
            cols = [f"geo_token_{i}" for i in range(train_embed.shape[1])]
            train_tokens = pd.DataFrame(
                train_embed, index=self.train_data.index, columns=cols)
            test_tokens = pd.DataFrame(
                test_embed, index=self.test_data.index, columns=cols)
            return train_tokens, test_tokens, cols, geo_gnn
        except Exception as exc:
            print(f"[GeoToken] 生成失败：{exc}")
            return None

    def _prepare_geo_tokens(self) -> None:
        """使用配置默认值构建并持久化地理 token。"""
        gnn_trainer = self.trainers.get("gnn")
        if gnn_trainer is not None and hasattr(gnn_trainer, "prepare_geo_tokens"):
            try:
                gnn_trainer.prepare_geo_tokens(force=False)  # type: ignore[attr-defined]
                return
            except Exception as exc:
                print(f"[GeoToken] GNNTrainer 生成失败：{exc}")

        result = self._build_geo_tokens()
        if result is None:
            return
        train_tokens, test_tokens, cols, geo_gnn = result
        self.train_geo_tokens = train_tokens
        self.test_geo_tokens = test_tokens
        self.geo_token_cols = cols
        self.geo_gnn_model = geo_gnn
        print(f"[GeoToken] 已生成 {len(cols)} 维地理 token，将注入 FT。")

    def _add_region_effect(self) -> None:
        """对省/市层级做部分池化，生成平滑的 region_effect 数值特征。"""
        prov_col = self.config.region_province_col
        city_col = self.config.region_city_col
        if not prov_col or not city_col:
            return
        for col in [prov_col, city_col]:
            if col not in self.train_data.columns:
                print(f"[RegionEffect] 缺少列 {col}，已跳过。")
                return

        def safe_mean(df: pd.DataFrame) -> float:
            w = df[self.weight_nme]
            y = df[self.resp_nme]
            denom = max(float(w.sum()), EPS)
            return float((y * w).sum() / denom)

        global_mean = safe_mean(self.train_data)
        alpha = max(float(self.config.region_effect_alpha), 0.0)

        prov_stats = self.train_data.groupby(prov_col).apply(safe_mean)
        prov_stats = prov_stats.to_dict()

        city_group = self.train_data.groupby([prov_col, city_col])
        city_sumw = city_group[self.weight_nme].sum()
        city_sumyw = (city_group[self.resp_nme].apply(
            lambda s: (s * self.train_data.loc[s.index, self.weight_nme]).sum()))

        city_effect: Dict[tuple, float] = {}
        for (p, c), sum_w in city_sumw.items():
            sum_yw = city_sumyw[(p, c)]
            prior = prov_stats.get(p, global_mean)
            effect = (sum_yw + alpha * prior) / max(sum_w + alpha, EPS)
            city_effect[(p, c)] = float(effect)

        def lookup_effect(df: pd.DataFrame) -> pd.Series:
            effects = []
            for _, row in df[[prov_col, city_col]].iterrows():
                p = row[prov_col]
                c = row[city_col]
                val = city_effect.get((p, c))
                if val is None:
                    val = prov_stats.get(p, global_mean)
                if not np.isfinite(val):
                    val = global_mean
                effects.append(val)
            return pd.Series(effects, index=df.index, dtype=np.float32)

        re_train = lookup_effect(self.train_data)
        re_test = lookup_effect(self.test_data)

        col_name = "region_effect"
        self.train_data[col_name] = re_train
        self.test_data[col_name] = re_test

        # 同步到 one-hot 与标准化版本
        for df in [self.train_oht_data, self.test_oht_data]:
            if df is not None:
                df[col_name] = re_train if df is self.train_oht_data else re_test

        # 标准化 region_effect 并同步
        scaler = StandardScaler()
        re_train_s = scaler.fit_transform(
            re_train.values.reshape(-1, 1)).astype(np.float32).reshape(-1)
        re_test_s = scaler.transform(
            re_test.values.reshape(-1, 1)).astype(np.float32).reshape(-1)
        for df in [self.train_oht_scl_data, self.test_oht_scl_data]:
            if df is not None:
                df[col_name] = re_train_s if df is self.train_oht_scl_data else re_test_s

        # 更新特征列表
        if col_name not in self.factor_nmes:
            self.factor_nmes.append(col_name)
        if col_name not in self.num_features:
            self.num_features.append(col_name)
        if self.train_oht_scl_data is not None:
            excluded = {self.weight_nme, self.resp_nme}
            self.var_nmes = [
                col for col in self.train_oht_scl_data.columns if col not in excluded
            ]

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

    def _require_trainer(self, model_key: str) -> "TrainerBase":
        trainer = self.trainers.get(model_key)
        if trainer is None:
            raise KeyError(f"Unknown model key: {model_key}")
        return trainer

    def _pred_vector_columns(self, pred_prefix: str) -> List[str]:
        """返回形如 pred_<prefix>_0.. 的多维特征列（按后缀序号排序）。"""
        col_prefix = f"pred_{pred_prefix}_"
        cols = [c for c in self.train_data.columns if c.startswith(col_prefix)]

        def sort_key(name: str):
            tail = name.rsplit("_", 1)[-1]
            try:
                return (0, int(tail))
            except Exception:
                return (1, tail)

        cols.sort(key=sort_key)
        return cols

    def _inject_pred_features(self, pred_prefix: str) -> List[str]:
        """将 pred_<prefix> 或 pred_<prefix>_i 列注入特征集合，并返回注入的列名。"""
        cols = self._pred_vector_columns(pred_prefix)
        if cols:
            self.add_numeric_features_from_columns(cols)
            return cols
        scalar_col = f"pred_{pred_prefix}"
        if scalar_col in self.train_data.columns:
            self.add_numeric_feature_from_column(scalar_col)
            return [scalar_col]
        return []

    def _maybe_load_best_params(self, model_key: str, trainer: "TrainerBase") -> None:
        # 1) 若显式指定了 best_params_files，则直接加载并跳过调参
        best_params_files = getattr(self.config, "best_params_files", None) or {}
        best_params_file = best_params_files.get(model_key)
        if best_params_file and not trainer.best_params:
            trainer.best_params = IOUtils.load_params_file(best_params_file)
            trainer.best_trial = None
            print(
                f"[Optuna][{trainer.label}] Loaded best_params from {best_params_file}; skip tuning."
            )

        # 2) 若开启 reuse_best_params，则优先从版本快照回放；否则从旧 CSV 回放
        reuse_params = bool(getattr(self.config, "reuse_best_params", False))
        if reuse_params and not trainer.best_params:
            payload = self.version_manager.load_latest(f"{model_key}_best")
            best_params = None if payload is None else payload.get("best_params")
            if best_params:
                trainer.best_params = best_params
                trainer.best_trial = None
                trainer.study_name = payload.get(
                    "study_name") if isinstance(payload, dict) else None
                print(
                    f"[Optuna][{trainer.label}] Reusing best_params from versions snapshot.")
                return

            params_path = self.output_manager.result_path(
                f'{self.model_nme}_bestparams_{trainer.label.lower()}.csv'
            )
            if os.path.exists(params_path):
                try:
                    trainer.best_params = IOUtils.load_params_file(params_path)
                    trainer.best_trial = None
                    print(
                        f"[Optuna][{trainer.label}] Reusing best_params from {params_path}.")
                except ValueError:
                    # 兼容旧逻辑：文件存在但为空时，忽略并继续后续调参流程
                    pass

    # 定义通用优化函数
    def optimize_model(self, model_key: str, max_evals: int = 100):
        if model_key not in self.trainers:
            print(f"Warning: Unknown model key: {model_key}")
            return

        trainer = self._require_trainer(model_key)
        self._maybe_load_best_params(model_key, trainer)

        should_tune = not trainer.best_params
        if should_tune:
            if model_key == "ft" and str(self.config.ft_role) == "unsupervised_embedding":
                if hasattr(trainer, "cross_val_unsupervised"):
                    trainer.tune(
                        max_evals,
                        objective_fn=getattr(trainer, "cross_val_unsupervised")
                    )
                else:
                    raise RuntimeError(
                        "FT trainer does not support unsupervised Optuna objective.")
            else:
                trainer.tune(max_evals)

        if model_key == "ft" and str(self.config.ft_role) != "model":
            prefix = str(self.config.ft_feature_prefix or "ft_emb")
            role = str(self.config.ft_role)
            if role == "embedding":
                trainer.train_as_feature(
                    pred_prefix=prefix, feature_mode="embedding")
            elif role == "unsupervised_embedding":
                trainer.pretrain_unsupervised_as_feature(
                    pred_prefix=prefix,
                    params=trainer.best_params
                )
            else:
                raise ValueError(
                    f"Unsupported ft_role='{role}', expected 'model'/'embedding'/'unsupervised_embedding'.")

            # 将生成的预测/embedding 列作为新特征注入（支持标量或向量两种形式）
            self._inject_pred_features(prefix)
            # 不将 FT 作为单独模型加入 model_label；下游模型负责评估与展示
        else:
            trainer.train()

        # 更新上下文字段，保证历史接口的兼容性
        setattr(self, f"{model_key}_best", trainer.model)
        setattr(self, f"best_{model_key}_params", trainer.best_params)
        setattr(self, f"best_{model_key}_trial", trainer.best_trial)
        # 保存一次版本快照，方便回溯
        study_name = getattr(trainer, "study_name", None)
        if study_name is None and trainer.best_trial is not None:
            study_obj = getattr(trainer.best_trial, "study", None)
            study_name = getattr(study_obj, "study_name", None)
        snapshot = {
            "model_key": model_key,
            "timestamp": datetime.now().isoformat(),
            "best_params": trainer.best_params,
            "study_name": study_name,
            "config": asdict(self.config),
        }
        self.version_manager.save(f"{model_key}_best", snapshot)

    def add_numeric_feature_from_column(self, col_name: str) -> None:
        """将已有列加入特征集合（同时同步到 one-hot/标准化表），用于堆叠/特征加工。"""
        if col_name not in self.train_data.columns or col_name not in self.test_data.columns:
            raise KeyError(
                f"Column '{col_name}' must exist in both train_data and test_data.")

        if col_name not in self.factor_nmes:
            self.factor_nmes.append(col_name)
        if col_name not in self.config.factor_nmes:
            self.config.factor_nmes.append(col_name)

        if col_name not in self.cate_list and col_name not in self.num_features:
            self.num_features.append(col_name)

        if self.train_oht_data is not None and self.test_oht_data is not None:
            self.train_oht_data[col_name] = self.train_data[col_name].values
            self.test_oht_data[col_name] = self.test_data[col_name].values
        if self.train_oht_scl_data is not None and self.test_oht_scl_data is not None:
            scaler = StandardScaler()
            tr = self.train_data[col_name].to_numpy(
                dtype=np.float32, copy=False).reshape(-1, 1)
            te = self.test_data[col_name].to_numpy(
                dtype=np.float32, copy=False).reshape(-1, 1)
            self.train_oht_scl_data[col_name] = scaler.fit_transform(
                tr).reshape(-1)
            self.test_oht_scl_data[col_name] = scaler.transform(te).reshape(-1)

        if col_name not in self.var_nmes:
            self.var_nmes.append(col_name)

    def add_numeric_features_from_columns(self, col_names: List[str]) -> None:
        for col in col_names:
            self.add_numeric_feature_from_column(col)

    def prepare_ft_as_feature(self, max_evals: int = 50, pred_prefix: str = "ft_feat") -> str:
        """训练 FT 作为特征加工器，并返回可供下游使用的列名（如 'pred_ft_feat'）。"""
        ft_trainer = self._require_trainer("ft")
        ft_trainer.tune(max_evals=max_evals)
        if hasattr(ft_trainer, "train_as_feature"):
            ft_trainer.train_as_feature(pred_prefix=pred_prefix)
        else:
            ft_trainer.train()
        feature_col = f"pred_{pred_prefix}"
        self.add_numeric_feature_from_column(feature_col)
        return feature_col

    def prepare_ft_embedding_as_features(self, max_evals: int = 50, pred_prefix: str = "ft_emb") -> List[str]:
        """训练 FT 并将 pooling embedding 作为多维特征注入，下游会得到 pred_<prefix>_0.. 列。"""
        ft_trainer = self._require_trainer("ft")
        ft_trainer.tune(max_evals=max_evals)
        if hasattr(ft_trainer, "train_as_feature"):
            ft_trainer.train_as_feature(
                pred_prefix=pred_prefix, feature_mode="embedding")
        else:
            raise RuntimeError(
                "FT trainer does not support embedding feature mode.")
        cols = self._pred_vector_columns(pred_prefix)
        if not cols:
            raise RuntimeError(
                f"No embedding columns were generated for prefix '{pred_prefix}'.")
        self.add_numeric_features_from_columns(cols)
        return cols

    def prepare_ft_unsupervised_embedding_as_features(self,
                                                      pred_prefix: str = "ft_uemb",
                                                      params: Optional[Dict[str,
                                                                            Any]] = None,
                                                      mask_prob_num: float = 0.15,
                                                      mask_prob_cat: float = 0.15,
                                                      num_loss_weight: float = 1.0,
                                                      cat_loss_weight: float = 1.0) -> List[str]:
        """FT 自监督( masked 重建 )预训练后导出 embedding 作为下游特征。"""
        ft_trainer = self._require_trainer("ft")
        if not hasattr(ft_trainer, "pretrain_unsupervised_as_feature"):
            raise RuntimeError(
                "FT trainer does not support unsupervised pretraining.")
        ft_trainer.pretrain_unsupervised_as_feature(
            pred_prefix=pred_prefix,
            params=params,
            mask_prob_num=mask_prob_num,
            mask_prob_cat=mask_prob_cat,
            num_loss_weight=num_loss_weight,
            cat_loss_weight=cat_loss_weight
        )
        cols = self._pred_vector_columns(pred_prefix)
        if not cols:
            raise RuntimeError(
                f"No embedding columns were generated for prefix '{pred_prefix}'.")
        self.add_numeric_features_from_columns(cols)
        return cols

    # 定义GLM贝叶斯优化函数
    def bayesopt_glm(self, max_evals=50):
        self.optimize_model('glm', max_evals)

    # 定义Xgboost贝叶斯优化函数
    def bayesopt_xgb(self, max_evals=100):
        self.optimize_model('xgb', max_evals)

    # 定义ResNet贝叶斯优化函数
    def bayesopt_resnet(self, max_evals=100):
        self.optimize_model('resn', max_evals)

    # 定义 GNN 贝叶斯优化函数
    def bayesopt_gnn(self, max_evals=50):
        self.optimize_model('gnn', max_evals)

    # 定义 FT-Transformer 贝叶斯优化函数
    def bayesopt_ft(self, max_evals=50):
        self.optimize_model('ft', max_evals)

    # 绘制提纯曲线
    def plot_lift(self, model_label, pred_nme, n_bins=10):
        model_map = {
            'Xgboost': 'pred_xgb',
            'ResNet': 'pred_resn',
            'ResNetClassifier': 'pred_resn',
            'GLM': 'pred_glm',
            'GNN': 'pred_gnn',
        }
        if str(self.config.ft_role) == "model":
            model_map.update({
                'FTTransformer': 'pred_ft',
                'FTTransformerClassifier': 'pred_ft',
            })
        for k, v in model_map.items():
            if model_label.startswith(k):
                pred_nme = v
                break

        datasets = []
        for title, data in [
            ('Lift Chart on Train Data', self.train_data),
            ('Lift Chart on Test Data', self.test_data),
        ]:
            if 'w_act' not in data.columns or data['w_act'].isna().all():
                print(
                    f"[Lift] Missing labels for {title}; skip.",
                    flush=True,
                )
                continue
            datasets.append((title, data))

        if not datasets:
            print("[Lift] No labeled data available; skip plotting.", flush=True)
            return

        fig = plt.figure(figsize=(11, 5))
        positions = [111] if len(datasets) == 1 else [121, 122]
        for pos, (title, data) in zip(positions, datasets):
            if pred_nme not in data.columns or f'w_{pred_nme}' not in data.columns:
                print(
                    f"[Lift] Missing prediction columns in {title}; skip.",
                    flush=True,
                )
                continue
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
        # 参数说明:
        #   model_comp: 需要对比的模型简称（如 ['xgb', 'resn']，支持 'xgb'/'resn'/'glm'/'gnn'/'ft'）。
        #   n_bins: 分箱数量，用于控制 lift 曲线的粒度。
        if len(model_comp) != 2:
            raise ValueError("`model_comp` 必须包含两个模型进行对比。")

        model_name_map = {
            'xgb': 'Xgboost',
            'resn': 'ResNet',
            'glm': 'GLM',
            'gnn': 'GNN',
        }
        if str(self.config.ft_role) == "model":
            model_name_map['ft'] = 'FTTransformer'

        name1, name2 = model_comp
        if name1 not in model_name_map or name2 not in model_name_map:
            raise ValueError(f"不支持的模型简称。请从 {list(model_name_map.keys())} 中选择。")

        datasets = []
        for data_name, data in [('Train Data', self.train_data),
                                ('Test Data', self.test_data)]:
            if 'w_act' not in data.columns or data['w_act'].isna().all():
                print(
                    f"[Double Lift] Missing labels for {data_name}; skip.",
                    flush=True,
                )
                continue
            datasets.append((data_name, data))

        if not datasets:
            print("[Double Lift] No labeled data available; skip plotting.", flush=True)
            return

        fig, axes = plt.subplots(1, len(datasets), figsize=(11, 5))
        if len(datasets) == 1:
            axes = [axes]

        for ax, (data_name, data) in zip(axes, datasets):
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
                if model_name:  # 仅在用户指定模型名时输出告警
                    print(f"[save_model] Warning: Unknown model key {key}")

    def load_model(self, model_name=None):
        keys = [model_name] if model_name else self.trainers.keys()
        for key in keys:
            if key in self.trainers:
                self.trainers[key].load()
                # 同步上下文字段
                trainer = self.trainers[key]
                if trainer.model is not None:
                    setattr(self, f"{key}_best", trainer.model)
                    # 如需兼容旧版字段，也同步更新 xxx_load
                    # 旧版只维护 xgb_load/resn_load/ft_load，未包含 glm_load/gnn_load
                    if key in ['xgb', 'resn', 'ft', 'gnn']:
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
        matrices = []
        for col in self.factor_nmes:
            s = data[col]
            if col in self.cate_list:
                cats = pd.Categorical(
                    s,
                    categories=self.cat_categories_for_shap[col]
                )
                codes = np.asarray(cats.codes, dtype=np.float64).reshape(-1, 1)
                matrices.append(codes)
            else:
                vals = pd.to_numeric(s, errors="coerce")
                arr = vals.to_numpy(dtype=np.float64, copy=True).reshape(-1, 1)
                matrices.append(arr)
        X_mat = np.concatenate(matrices, axis=1)  # 结果形状为 (N, F)
        return X_mat

    def _decode_ft_shap_matrix_to_df(self, X_mat: np.ndarray) -> pd.DataFrame:
        data_dict = {}
        for j, col in enumerate(self.factor_nmes):
            col_vals = X_mat[:, j]
            if col in self.cate_list:
                cats = self.cat_categories_for_shap[col]
                codes = np.round(col_vals).astype(int)
                codes = np.clip(codes, -1, len(cats) - 1)
                cat_series = pd.Categorical.from_codes(
                    codes,
                    categories=cats
                )
                data_dict[col] = cat_series
            else:
                data_dict[col] = col_vals.astype(float)

        df = pd.DataFrame(data_dict, columns=self.factor_nmes)
        for col in self.cate_list:
            if col in df.columns:
                df[col] = df[col].astype("category")
        return df

    def _build_glm_design(self, data: pd.DataFrame) -> pd.DataFrame:
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
        if model_key not in self.trainers or self.trainers[model_key].model is None:
            raise RuntimeError(f"Model {model_key} not trained.")
        if cleanup_fn:
            cleanup_fn()
        bg_df = self._sample_rows(X_df, n_background)
        bg_mat = prep_fn(bg_df)
        explainer = shap.KernelExplainer(predict_fn, bg_mat)
        ex_df = self._sample_rows(X_df, n_samples)
        ex_mat = prep_fn(ex_df)
        nsample_eff = self._shap_nsamples(ex_mat)
        shap_values = explainer.shap_values(ex_mat, nsamples=nsample_eff)
        bg_pred = predict_fn(bg_mat)
        base_value = float(np.asarray(bg_pred).mean())

        return {
            "explainer": explainer,
            "X_explain": ex_df,
            "shap_values": shap_values,
            "base_value": base_value
        }

    # ========= GLM 的 SHAP 解释 =========
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

        self.shap_glm = self._compute_shap_core(
            'glm', n_background, n_samples, on_train,
            X_df=design_all,
            prep_fn=lambda df: df.to_numpy(dtype=np.float64),
            predict_fn=predict_wrapper
        )
        return self.shap_glm

    # ========= XGBoost 的 SHAP 解释 =========
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

    # ========= ResNet 的 SHAP 解释 =========
    def _resn_predict_wrapper(self, X_np):
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

    # ========= FT-Transformer 的 SHAP 解释 =========
    def _ft_shap_predict_wrapper(self, X_mat: np.ndarray) -> np.ndarray:
        df_input = self._decode_ft_shap_matrix_to_df(X_mat)
        y_pred = self.ft_best.predict(df_input)
        return np.asarray(y_pred, dtype=np.float64).reshape(-1)

    def compute_shap_ft(self, n_background: int = 500,
                        n_samples: int = 200,
                        on_train: bool = True):
        if str(self.config.ft_role) != "model":
            raise RuntimeError(
                "FT is configured as embedding-only (ft_role != 'model'); FT SHAP is disabled.")
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
