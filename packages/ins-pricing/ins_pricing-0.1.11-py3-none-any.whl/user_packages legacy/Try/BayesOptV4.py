# 数据在CPU和GPU之间传输会带来较大开销,但可以多CUDA流同时传输数据和计算,从而实现更大数据集的操作。

import copy
from email.mime import base
import gc
import math
import os
from dataclasses import dataclass
from pathlib import Path
from re import X
from typing import Any, Dict, List, Optional

import joblib
import matplotlib.pyplot as plt
import numpy as np  # 1.26.2
import optuna  # 4.3.0
import pandas as pd  # 2.2.3
import shap

import torch  # 版本: 1.10.1+cu111
import torch.nn as nn
import torch.nn.functional as F
import xgboost as xgb  # 1.7.0

from torch.utils.data import Dataset, DataLoader, TensorDataset
from torch.cuda.amp import autocast, GradScaler
from torch.nn.utils import clip_grad_norm_
from sklearn.model_selection import ShuffleSplit, cross_val_score  # 1.2.2
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import make_scorer, mean_tweedie_deviance

# =============================================================================
# Constants & utilities
# =============================================================================
EPS = 1e-8


def ensure_parent_dir(file_path: str) -> None:
    # 若目标文件所在目录不存在则自动创建
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def compute_batch_size(data_size: int, learning_rate: float, batch_num: int, minimum: int) -> int:
    # 按学习率和样本量给出估算 batch，再夹在 [1, data_size] 范围内
    estimated = int((learning_rate / 1e-4) ** 0.5 *
                    (data_size / max(batch_num, 1)))
    return max(1, min(data_size, max(minimum, estimated)))


# 定义在 PyTorch 环境下的 Tweedie 偏差损失函数
# 参考文档：https://scikit-learn.org/stable/modules/model_evaluation.html#mean-poisson-gamma-and-tweedie-deviances


def tweedie_loss(pred, target, p=1.5, eps=1e-6, max_clip=1e6):
    # 为确保稳定性先将预测值裁剪为正数
    pred_clamped = torch.clamp(pred, min=eps)
    # 计算 Tweedie 偏差的各部分
    if p == 1:
        # 对应泊松分布
        term1 = target * torch.log(target / pred_clamped + eps)
        term2 = -target + pred_clamped
        term3 = 0
    elif p == 0:
        # 对应高斯分布
        term1 = 0.5 * torch.pow(target - pred_clamped, 2)
        term2 = 0
        term3 = 0
    elif p == 2:
        # 对应伽马分布
        term1 = torch.log(pred_clamped / target + eps)
        term2 = -target / pred_clamped + 1
        term3 = 0
    else:
        term1 = torch.pow(target, 2 - p) / ((1 - p) * (2 - p))
        term2 = target * torch.pow(pred_clamped, 1 - p) / (1 - p)
        term3 = torch.pow(pred_clamped, 2 - p) / (2 - p)
    # Tweedie 负对数似然（忽略常数项）
    return torch.nan_to_num(2 * (term1 - term2 + term3), nan=eps, posinf=max_clip, neginf=-max_clip)

# 定义释放CUDA内存函数


def free_cuda():
    print(">>> Moving all models to CPU...")
    for obj in gc.get_objects():
        try:
            if hasattr(obj, "to") and callable(obj.to):
                # 跳过 torch.device 等不可移动对象
                obj.to("cpu")
        except:
            pass

    print(">>> Deleting tensors, optimizers, dataloaders...")
    gc.collect()

    print(">>> Emptying CUDA cache...")
    torch.cuda.empty_cache()
    torch.cuda.synchronize()

    print(">>> CUDA memory freed.")


# =============================================================================
# Plotting helpers
# =============================================================================

# 定义分箱函数


def split_data(data, col_nme, wgt_nme, n_bins=10):
    # 避免修改原始数据帧，先创建排序后的副本
    data_sorted = data.sort_values(by=col_nme, ascending=True).copy()
    data_sorted['cum_weight'] = data_sorted[wgt_nme].cumsum()
    w_sum = data_sorted[wgt_nme].sum()
    if w_sum <= EPS:
        data_sorted.loc[:, 'bins'] = 0
    else:
        data_sorted.loc[:, 'bins'] = np.floor(
            data_sorted['cum_weight'] * float(n_bins) / w_sum
        )
        data_sorted.loc[(data_sorted['bins'] == n_bins), 'bins'] = n_bins - 1
    return data_sorted.groupby(['bins'], observed=True).sum(numeric_only=True)

# 定义提纯曲线（Lift）绘制函数


def plot_lift_list(pred_model, w_pred_list, w_act_list,
                   weight_list, tgt_nme, n_bins=10,
                   fig_nme='Lift Chart'):
    lift_data = pd.DataFrame()
    lift_data.loc[:, 'pred'] = pred_model
    lift_data.loc[:, 'w_pred'] = w_pred_list
    lift_data.loc[:, 'act'] = w_act_list
    lift_data.loc[:, 'weight'] = weight_list
    plot_data = split_data(lift_data, 'pred', 'weight', n_bins)
    plot_data['exp_v'] = plot_data['w_pred'] / plot_data['weight']
    plot_data['act_v'] = plot_data['act'] / plot_data['weight']
    plot_data.reset_index(inplace=True)
    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111)
    ax.plot(plot_data.index, plot_data['act_v'],
            label='Actual', color='red')
    ax.plot(plot_data.index, plot_data['exp_v'],
            label='Predicted', color='blue')
    ax.set_title(
        'Lift Chart of %s' % tgt_nme, fontsize=8)
    plt.xticks(plot_data.index,
               plot_data.index,
               rotation=90, fontsize=6)
    plt.yticks(fontsize=6)
    plt.legend(loc='upper left',
               fontsize=5, frameon=False)
    plt.margins(0.05)
    ax2 = ax.twinx()
    ax2.bar(plot_data.index, plot_data['weight'],
            alpha=0.5, color='seagreen',
            label='Earned Exposure')
    plt.yticks(fontsize=6)
    plt.legend(loc='upper right',
               fontsize=5, frameon=False)
    plt.subplots_adjust(wspace=0.3)
    save_path = os.path.join(
        os.getcwd(), 'plot', f'05_{tgt_nme}_{fig_nme}.png')
    ensure_parent_dir(save_path)
    plt.savefig(save_path, dpi=300)
    plt.close(fig)

# 定义双提纯曲线绘制函数


def plot_dlift_list(pred_model_1, pred_model_2,
                    model_nme_1, model_nme_2,
                    tgt_nme,
                    w_list, w_act_list, n_bins=10,
                    fig_nme='Double Lift Chart'):
    lift_data = pd.DataFrame()
    lift_data.loc[:, 'pred1'] = pred_model_1
    lift_data.loc[:, 'pred2'] = pred_model_2
    lift_data.loc[:, 'diff_ly'] = lift_data['pred1'] / lift_data['pred2']
    lift_data.loc[:, 'act'] = w_act_list
    lift_data.loc[:, 'weight'] = w_list
    lift_data.loc[:, 'w_pred1'] = lift_data['pred1'] * lift_data['weight']
    lift_data.loc[:, 'w_pred2'] = lift_data['pred2'] * lift_data['weight']
    plot_data = split_data(lift_data, 'diff_ly', 'weight', n_bins)
    plot_data['exp_v1'] = plot_data['w_pred1'] / plot_data['act']
    plot_data['exp_v2'] = plot_data['w_pred2'] / plot_data['act']
    plot_data['act_v'] = plot_data['act']/plot_data['act']
    plot_data.reset_index(inplace=True)
    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111)
    ax.plot(plot_data.index, plot_data['act_v'],
            label='Actual', color='red')
    ax.plot(plot_data.index, plot_data['exp_v1'],
            label=model_nme_1, color='blue')
    ax.plot(plot_data.index, plot_data['exp_v2'],
            label=model_nme_2, color='black')
    ax.set_title(
        'Double Lift Chart of %s' % tgt_nme, fontsize=8)
    plt.xticks(plot_data.index,
               plot_data.index,
               rotation=90, fontsize=6)
    plt.xlabel('%s / %s' % (model_nme_1, model_nme_2), fontsize=6)
    plt.yticks(fontsize=6)
    plt.legend(loc='upper left',
               fontsize=5, frameon=False)
    plt.margins(0.1)
    plt.subplots_adjust(bottom=0.25, top=0.95, right=0.8)
    ax2 = ax.twinx()
    ax2.bar(plot_data.index, plot_data['weight'],
            alpha=0.5, color='seagreen',
            label='Earned Exposure')
    plt.yticks(fontsize=6)
    plt.legend(loc='upper right',
               fontsize=5, frameon=False)
    plt.subplots_adjust(wspace=0.3)
    save_path = os.path.join(
        os.getcwd(), 'plot', f'06_{tgt_nme}_{fig_nme}.png')
    ensure_parent_dir(save_path)
    plt.savefig(save_path, dpi=300)
    plt.close(fig)


# =============================================================================
# ResNet model & sklearn-style wrapper
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
                 residual_scale: float = 0.1):
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
        self.net.add_module('softplus', nn.Softplus())

    def forward(self, x):
        return self.net(x)

# 定义ResNet模型的Scikit-Learn接口类


class ResNetSklearn(nn.Module):
    def __init__(self, model_nme: str, input_dim: int, hidden_dim: int = 64,
                 block_num: int = 2, batch_num: int = 100, epochs: int = 100,
                 tweedie_power: float = 1.5, learning_rate: float = 0.01, patience: int = 10,
                 use_layernorm: bool = True, dropout: float = 0.1,
                 residual_scale: float = 0.1):
        super(ResNetSklearn, self).__init__()

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.block_num = block_num
        self.batch_num = batch_num
        self.epochs = epochs
        self.model_nme = model_nme
        self.learning_rate = learning_rate
        self.patience = patience
        self.use_layernorm = use_layernorm
        self.dropout = dropout
        self.residual_scale = residual_scale

        # 设备选择：cuda > mps > cpu
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            self.device = torch.device('mps')
        else:
            self.device = torch.device('cpu')

        # Tweedie 幂指数设定
        if 'f' in self.model_nme:
            self.tw_power = 1
        elif 's' in self.model_nme:
            self.tw_power = 2
        else:
            self.tw_power = tweedie_power

        # 搭建网络
        self.resnet = ResNetSequential(
            self.input_dim,
            self.hidden_dim,
            self.block_num,
            use_layernorm=self.use_layernorm,
            dropout=self.dropout,
            residual_scale=self.residual_scale
        ).to(self.device)

    def forward(self, x):
        # 重写 forward 方法以处理 SHAP 的输入
        # SHAP (KernelExplainer) 会传入一个 NumPy 数组
        if isinstance(x, np.ndarray):
            # 1. 从 NumPy 数组创建张量
            x_tensor = torch.tensor(x, dtype=torch.float32)
        else:
            # 2. 保持对现有张量输入的兼容
            x_tensor = x

        # 3. 确保输入张量在正确的设备上
        x_tensor = x_tensor.to(self.device)

        # 4. 通过底层 ResNet 模型进行预测
        # self.resnet 已经在初始化时被 .to(self.device)
        y_pred = self.resnet(x_tensor)
        return y_pred

    def fit(self, X_train, y_train, w_train=None,
            X_val=None, y_val=None, w_val=None):

        # === 1. 训练集：先留在 CPU，交给 DataLoader 批量搬运到 GPU ===
        # 注意：从 pandas DataFrame 转 tensor 时要复制数据，避免后续视图修改
        X_tensor = torch.tensor(X_train.values, dtype=torch.float32)
        y_tensor = torch.tensor(
            y_train.values, dtype=torch.float32).view(-1, 1)
        if w_train is not None:
            w_tensor = torch.tensor(
                w_train.values, dtype=torch.float32).view(-1, 1)
        else:
            w_tensor = torch.ones_like(y_tensor)

        # === 2. 验证集：先在 CPU 上构造，后续一次性搬到目标设备 ===
        has_val = X_val is not None and y_val is not None
        if has_val:
            X_val_tensor = torch.tensor(X_val.values, dtype=torch.float32)
            y_val_tensor = torch.tensor(
                y_val.values, dtype=torch.float32).view(-1, 1)
            if w_val is not None:
                w_val_tensor = torch.tensor(
                    w_val.values, dtype=torch.float32).view(-1, 1)
            else:
                w_val_tensor = torch.ones_like(y_val_tensor)
        else:
            X_val_tensor = y_val_tensor = w_val_tensor = None

        # === 3. 构建 DataLoader ===
        dataset = TensorDataset(X_tensor, y_tensor, w_tensor)
        batch_size = compute_batch_size(
            data_size=len(dataset),
            learning_rate=self.learning_rate,
            batch_num=self.batch_num,
            minimum=64
        )

        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=1,  # 表格数据通常 0~1 个线程即可
            pin_memory=(self.device.type == 'cuda')
        )

        # === 4. 优化器与 AMP ===
        # 建议使用 Adam + AMP 主要是为了稳定损失，同时保持 GPU 性能
        self.optimizer = torch.optim.Adam(
            self.resnet.parameters(), lr=self.learning_rate)
        self.scaler = GradScaler(enabled=(self.device.type == 'cuda'))

        # === 5. 早停机制 ===
        best_loss, patience_counter = float('inf'), 0
        best_model_state = None

        # 若存在验证集则一次性搬到目标设备
        if has_val:
            X_val_dev = X_val_tensor.to(self.device, non_blocking=True)
            y_val_dev = y_val_tensor.to(self.device, non_blocking=True)
            w_val_dev = w_val_tensor.to(self.device, non_blocking=True)

        # === 6. 训练循环 ===
        for epoch in range(1, self.epochs + 1):
            self.resnet.train()
            for X_batch, y_batch, w_batch in dataloader:
                self.optimizer.zero_grad()

                X_batch = X_batch.to(self.device, non_blocking=True)
                y_batch = y_batch.to(self.device, non_blocking=True)
                w_batch = w_batch.to(self.device, non_blocking=True)

                with autocast(enabled=(self.device.type == 'cuda')):
                    y_pred = self.resnet(X_batch)
                    y_pred = torch.clamp(y_pred, min=1e-6)

                    losses = tweedie_loss(
                        y_pred, y_batch, p=self.tw_power).view(-1)
                    weighted_loss = (losses * w_batch.view(-1)
                                     ).sum() / torch.clamp(w_batch.sum(), min=EPS)

                self.scaler.scale(weighted_loss).backward()

                if self.device.type == 'cuda':
                    self.scaler.unscale_(self.optimizer)
                    clip_grad_norm_(self.resnet.parameters(), max_norm=1.0)

                self.scaler.step(self.optimizer)
                self.scaler.update()

            # === 7. 验证损失与早停判断 ===
            if has_val:
                self.resnet.eval()
                with torch.no_grad(), autocast(enabled=(self.device.type == 'cuda')):
                    y_val_pred = self.resnet(X_val_dev)
                    y_val_pred = torch.clamp(y_val_pred, min=1e-6)

                    val_loss_values = tweedie_loss(
                        y_val_pred, y_val_dev, p=self.tw_power
                    ).view(-1)
                    val_weighted_loss = (
                        val_loss_values * w_val_dev.view(-1)
                    ).sum() / torch.clamp(w_val_dev.sum(), min=EPS)

                if val_weighted_loss < best_loss:
                    best_loss = val_weighted_loss
                    patience_counter = 0
                    best_model_state = copy.deepcopy(self.resnet.state_dict())
                else:
                    patience_counter += 1

                if patience_counter >= self.patience and best_model_state is not None:
                    self.resnet.load_state_dict(best_model_state)
                    break
        if has_val and best_model_state is not None:
            self.resnet.load_state_dict(best_model_state)

    # ---------------- 预测 ----------------

    def predict(self, X_test):
        self.resnet.eval()
        # 如果输入是 DataFrame，先转为 NumPy 数组
        if isinstance(X_test, pd.DataFrame):
            X_np = X_test.values.astype(np.float32)
        else:
            X_np = X_test

        with torch.no_grad():
            # 直接调用 self (即 ResNetSklearn 实例)，这将触发 forward 方法
            y_pred = self(X_np).cpu().numpy()
        y_pred = np.clip(y_pred, 1e-6, None)
        return y_pred.flatten()

    # ---------------- 设置参数 ----------------

    def set_params(self, params):
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Parameter {key} not found in model.")

# =============================================================================
# FT-Transformer model & sklearn-style wrapper
# =============================================================================
# 开始定义FT Transformer模型结构


class FeatureTokenizer(nn.Module):
    # 将数值与类别特征映射为 token，输出形状 (batch, token 数, d_model)
    # 设定：
    #   - X_num 表示数值特征，形状 (batch, num_numeric)
    #   - X_cat 表示类别特征，形状 (batch, num_categorical)，每列为编码后的整数标签 [0, card-1]

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
            # 数值特征映射为单个 token
            num_token = self.num_linear(X_num)          # 形状 (batch, d_model)
            tokens.append(num_token)

        # 每个类别特征生成一个嵌入 token
        for i, emb in enumerate(self.embeddings):
            tok = emb(X_cat[:, i])                     # 形状 (batch, d_model)
            tokens.append(tok)

        # 最终堆叠为 (batch, token 数, d_model)
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
    # 最小可用版本的 FT-Transformer：
    #   - FeatureTokenizer：将数值与类别特征转换为 token
    #   - TransformerEncoder：捕捉特征之间的交互
    #   - 池化 + MLP + Softplus：保证输出为正值（适配 Tweedie/Gamma）

    def __init__(self, num_numeric: int, cat_cardinalities, d_model: int = 64,
                 n_heads: int = 8, n_layers: int = 4, dropout: float = 0.1,
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

        self.head = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Linear(d_model, d_model),
            nn.GELU(),
            # nn.ReLU(),
            nn.Linear(d_model, 1),
            nn.Softplus()  # 保证输出为正,适合 Tweedie / Gamma
        )

    def forward(self, X_num, X_cat):

        # X_num: (batch, 数值特征数)，float32
        # X_cat: (batch, 类别特征数)，long

        tokens = self.tokenizer(X_num, X_cat)  # 形状 (batch, token 数, d_model)
        x = self.encoder(tokens)               # 形状 (batch, token 数, d_model)

        # 对 token 做平均池化
        x = x.mean(dim=1)                      # 形状 (batch, d_model)

        out = self.head(x)                     # 形状 (batch, 1)，Softplus 保证为正
        return out

# 定义TabularDataset类


class TabularDataset(Dataset):
    def __init__(self, X_num, X_cat, y, w):

        # X_num: torch.float32, 形状 (N, 数值特征数)
        # X_cat: torch.long,    形状 (N, 类别特征数)
        # y:     torch.float32, 形状 (N, 1)
        # w:     torch.float32, 形状 (N, 1)

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


class FTTransformerSklearn(nn.Module):

    # sklearn 风格包装：
    #   - num_cols：数值特征列名列表
    #   - cat_cols：类别特征列名列表（需提前做标签编码，取值 [0, n_classes-1]）

    def __init__(self, model_nme: str, num_cols, cat_cols, d_model: int = 64, n_heads: int = 8,
                 n_layers: int = 4, dropout: float = 0.1, batch_num: int = 100, epochs: int = 100,
                 tweedie_power: float = 1.5, learning_rate: float = 1e-3, patience: int = 10,
                 ):
        super().__init__()

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
        self.patience = patience
        if 'f' in self.model_nme:
            self.tw_power = 1.0
        elif 's' in self.model_nme:
            self.tw_power = 2.0
        else:
            self.tw_power = tweedie_power
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")
        self.cat_cardinalities = None
        self.cat_categories = {}
        self.ft = None

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

        self.ft = FTTransformerCore(
            num_numeric=num_numeric,
            cat_cardinalities=cat_cardinalities,
            d_model=self.d_model,
            n_heads=self.n_heads,
            n_layers=self.n_layers,
            dropout=self.dropout,
        ).to(self.device)

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

    def fit(self, X_train, y_train, w_train=None,
            X_val=None, y_val=None, w_val=None):

        # 首次拟合时需要构建底层模型结构
        if self.ft is None:
            self._build_model(X_train)

        # --- 构建训练张量（全部先放在 CPU，后续按批搬运） ---
        # 复制数据确保与原 DataFrame 脱钩，这样标准化或采样不会污染原始数据
        X_num_train = X_train[self.num_cols].to_numpy(
            dtype=np.float32, copy=True)
        X_num_train = torch.tensor(
            X_num_train,
            dtype=torch.float32
        )

        if self.cat_cols:
            X_cat_train_np = self._encode_cats(X_train)
            X_cat_train = torch.tensor(X_cat_train_np, dtype=torch.long)
        else:
            X_cat_train = torch.zeros(
                (X_num_train.shape[0], 0), dtype=torch.long)

        y_tensor = torch.tensor(
            y_train.values,
            dtype=torch.float32
        ).view(-1, 1)

        if w_train is not None:
            w_tensor = torch.tensor(
                w_train.values,
                dtype=torch.float32
            ).view(-1, 1)
        else:
            w_tensor = torch.ones_like(y_tensor)

        # --- 验证集张量（一次性搬到目标设备） ---
        has_val = X_val is not None and y_val is not None
        if has_val:
            # ---------- 数值特征 ----------
            X_num_val_np = X_val[self.num_cols].to_numpy(
                dtype=np.float32, copy=True)
            X_num_val = torch.tensor(X_num_val_np, dtype=torch.float32)

            # ---------- 类别特征 ----------
            if self.cat_cols:
                X_cat_val_np = self._encode_cats(X_val)
                X_cat_val = torch.tensor(X_cat_val_np, dtype=torch.long)
            else:
                X_cat_val = torch.zeros(
                    (X_num_val.shape[0], 0), dtype=torch.long)

            # ---------- 目标 & 权重 ----------
            y_val_np = y_val.values.astype(np.float32, copy=True)
            y_val_tensor = torch.tensor(
                y_val_np, dtype=torch.float32).view(-1, 1)

            if w_val is not None:
                w_val_np = w_val.values.astype(np.float32, copy=True)
                w_val_tensor = torch.tensor(
                    w_val_np, dtype=torch.float32).view(-1, 1)
            else:
                w_val_tensor = torch.ones_like(y_val_tensor)

        else:
            X_num_val = X_cat_val = y_val_tensor = w_val_tensor = None

        # --- 构建 DataLoader ---
        dataset = TabularDataset(
            X_num_train, X_cat_train, y_tensor, w_tensor
        )

        batch_size = compute_batch_size(
            data_size=len(dataset),
            learning_rate=self.learning_rate,
            batch_num=self.batch_num,
            minimum=64
        )

        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=1,
            pin_memory=(self.device.type == 'cuda')
        )

        # --- 优化器与 AMP ---
        # 这部分与 ResNet 一致，仍建议使用 Adam + AMP 来避免数值不稳定
        optimizer = torch.optim.Adam(
            self.ft.parameters(),
            lr=self.learning_rate
        )
        scaler = GradScaler(enabled=(self.device.type == 'cuda'))

        # --- 早停机制 ---
        best_loss = float('inf')
        patience_counter = 0
        best_model_state = None

        # 若存在验证集则整体迁移到目标设备
        if has_val:
            X_num_val_dev = X_num_val.to(self.device, non_blocking=True)
            X_cat_val_dev = X_cat_val.to(self.device, non_blocking=True)
            y_val_dev = y_val_tensor.to(self.device, non_blocking=True)
            w_val_dev = w_val_tensor.to(self.device, non_blocking=True)

        # --- 训练循环 ---
        for epoch in range(1, self.epochs + 1):
            self.ft.train()
            for X_num_b, X_cat_b, y_b, w_b in dataloader:
                optimizer.zero_grad()

                X_num_b = X_num_b.to(self.device, non_blocking=True)
                X_cat_b = X_cat_b.to(self.device, non_blocking=True)
                y_b = y_b.to(self.device, non_blocking=True)
                w_b = w_b.to(self.device, non_blocking=True)

                with autocast(enabled=(self.device.type == 'cuda')):
                    y_pred = self.ft(X_num_b, X_cat_b)
                    y_pred = torch.clamp(y_pred, min=1e-6)

                    losses = tweedie_loss(
                        y_pred, y_b, p=self.tw_power
                    ).view(-1)

                    weighted_loss = (losses * w_b.view(-1)).sum() / \
                        torch.clamp(w_b.sum(), min=EPS)

                scaler.scale(weighted_loss).backward()

                if self.device.type == 'cuda':
                    scaler.unscale_(optimizer)
                    clip_grad_norm_(self.ft.parameters(), max_norm=1.0)

                scaler.step(optimizer)
                scaler.update()

            # --- 验证阶段与早停判断 ---
            if has_val:
                self.ft.eval()
                with torch.no_grad(), autocast(enabled=(self.device.type == 'cuda')):
                    y_val_pred = self.ft(X_num_val_dev, X_cat_val_dev)
                    y_val_pred = torch.clamp(y_val_pred, min=1e-6)

                    val_losses = tweedie_loss(
                        y_val_pred, y_val_dev, p=self.tw_power
                    ).view(-1)

                    val_weighted_loss = (
                        val_losses * w_val_dev.view(-1)
                    ).sum() / torch.clamp(w_val_dev.sum(), min=EPS)

                if val_weighted_loss < best_loss:
                    best_loss = val_weighted_loss
                    patience_counter = 0
                    best_model_state = copy.deepcopy(self.ft.state_dict())
                else:
                    patience_counter += 1

                if patience_counter >= self.patience and best_model_state is not None:
                    self.ft.load_state_dict(best_model_state)
                    break
        if has_val and best_model_state is not None:
            self.ft.load_state_dict(best_model_state)

    def predict(self, X_test):
        # X_test 需要包含所有数值列与类别列

        self.ft.eval()
        X_num = X_test[self.num_cols].to_numpy(dtype=np.float32, copy=True)
        X_num = torch.tensor(
            X_num,
            dtype=torch.float32
        )
        if self.cat_cols:
            X_cat_np = self._encode_cats(X_test)
            X_cat = torch.tensor(X_cat_np, dtype=torch.long)
        else:
            X_cat = torch.zeros((X_num.size(0), 0), dtype=torch.long)

        with torch.no_grad():
            X_num = X_num.to(self.device, non_blocking=True)
            X_cat = X_cat.to(self.device, non_blocking=True)
            y_pred = self.ft(X_num, X_cat).cpu().numpy()

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
# Config, preprocessing, and trainer base
# =============================================================================
@dataclass
class BayesOptConfig:
    model_nme: str
    resp_nme: str
    weight_nme: str
    factor_nmes: List[str]
    cate_list: Optional[List[str]] = None
    prop_test: float = 0.25
    rand_seed: Optional[int] = None
    epochs: int = 100
    use_gpu: bool = True


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
# Trainers
# =============================================================================


class TrainerBase:
    def __init__(self, context: "BayesOptModel", label: str) -> None:
        self.ctx = context
        self.label = label

    @property
    def config(self) -> BayesOptConfig:
        return self.ctx.config

    @property
    def output(self) -> OutputManager:
        return self.ctx.output_manager

    def tune(self, max_evals: int) -> None:  # pragma: no cover 子类会覆盖
        raise NotImplementedError

    def train(self) -> None:  # pragma: no cover 子类会覆盖
        raise NotImplementedError

    def save(self) -> None:
        pass

    def load(self) -> None:
        pass


class XGBTrainer(TrainerBase):
    def __init__(self, context: "BayesOptModel") -> None:
        super().__init__(context, 'Xgboost')
        self.model: Optional[xgb.XGBRegressor] = None
        self.best_params: Optional[Dict[str, Any]] = None
        self.best_trial = None

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

    def tune(self, max_evals: int = 100) -> None:
        study = optuna.create_study(
            direction='minimize',
            sampler=optuna.samplers.TPESampler(seed=self.ctx.rand_seed)
        )
        study.optimize(self.cross_val, n_trials=max_evals)
        self.best_params = study.best_params
        self.best_trial = study.best_trial
        params_path = self.output.result_path(
            f'{self.ctx.model_nme}_bestparams_xgb.csv'
        )
        pd.DataFrame(self.best_params, index=[0]).to_csv(params_path)

    def train(self) -> None:
        if not self.best_params:
            raise RuntimeError('请先运行 tune() 以获得 XGB 最优参数。')
        self.model = self._build_estimator()
        self.model.set_params(**self.best_params)
        self.model.fit(self.ctx.train_data[self.ctx.factor_nmes],
                       self.ctx.train_data[self.ctx.resp_nme].values,
                       **self.ctx.fit_params)
        self.ctx.model_label += [self.label]
        self.ctx.train_data['pred_xgb'] = self.model.predict(
            self.ctx.train_data[self.ctx.factor_nmes])
        self.ctx.test_data['pred_xgb'] = self.model.predict(
            self.ctx.test_data[self.ctx.factor_nmes])
        self.ctx.train_data.loc[:, 'w_pred_xgb'] = self.ctx.train_data['pred_xgb'] * \
            self.ctx.train_data[self.ctx.weight_nme]
        self.ctx.test_data.loc[:, 'w_pred_xgb'] = self.ctx.test_data['pred_xgb'] * \
            self.ctx.test_data[self.ctx.weight_nme]
        self.ctx.xgb_best = self.model

    def save(self) -> None:
        if self.model is not None:
            joblib.dump(self.model, self.output.model_path(
                f'01_{self.ctx.model_nme}_Xgboost.pkl'))

    def load(self) -> None:
        path = self.output.model_path(
            f'01_{self.ctx.model_nme}_Xgboost.pkl')
        if os.path.exists(path):
            self.model = joblib.load(path)
            self.ctx.xgb_best = self.model
        else:
            print(f"[load_model] Warning: 未找到 Xgboost 模型文件：{path}")


class ResNetTrainer(TrainerBase):
    def __init__(self, context: "BayesOptModel") -> None:
        super().__init__(context, 'ResNet')
        self.model: Optional[ResNetSklearn] = None
        self.best_params: Optional[Dict[str, Any]] = None
        self.best_trial = None

    # ========= 交叉验证（BayesOpt 用） =========
    def cross_val(self, trial: optuna.trial.Trial) -> float:
        """
        对 ResNet 做交叉验证。
        为了防止显存 OOM：
          - 每个 fold 独立创建一个 ResNetSklearn
          - fold 结束就把模型挪到 CPU + 删除 + gc + empty_cache
          - 可选：BayesOpt 阶段只用训练集子样本
        """

        # 1. 超参空间（基本沿用你之前的设定）
        learning_rate = trial.suggest_float(
            'learning_rate', 1e-6, 1e-2, log=True
        )
        # hidden_dim = trial.suggest_int('hidden_dim', 32, 256, step=32) # 不宜过大
        hidden_dim = trial.suggest_int('hidden_dim', 8, 32, step=2)
        block_num = trial.suggest_int('block_num', 2, 10)
        batch_num = trial.suggest_int(
            'batch_num',
            10 if self.ctx.obj == 'reg:gamma' else 100,
            100 if self.ctx.obj == 'reg:gamma' else 1000,
            step=10 if self.ctx.obj == 'reg:gamma' else 100
        )

        if self.ctx.obj == 'reg:tweedie':
            tw_power = trial.suggest_float('tw_power', 1.0, 2.0)
        elif self.ctx.obj == 'count:poisson':
            tw_power = 1.0
        elif self.ctx.obj == 'reg:gamma':
            tw_power = 2.0
        else:
            tw_power = 1.5

        loss = 0.0

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

        for fold, (train_idx, val_idx) in enumerate(cv_local.split(X_all)):
            X_train_fold = X_all.iloc[train_idx]
            y_train_fold = y_all.iloc[train_idx]
            w_train_fold = w_all.iloc[train_idx]

            X_val_fold = X_all.iloc[val_idx]
            y_val_fold = y_all.iloc[val_idx]
            w_val_fold = w_all.iloc[val_idx]

            # 3. 每个 fold 创建一个临时 ResNet 模型
            cv_net = ResNetSklearn(
                model_nme=self.ctx.model_nme,
                input_dim=X_all.shape[1],
                hidden_dim=hidden_dim,
                block_num=block_num,
                batch_num=batch_num,
                epochs=self.ctx.epochs,
                tweedie_power=tw_power,
                learning_rate=learning_rate,
                patience=5
            )

            try:
                # 4. 训练（内部仍然用你自己的 tweedie_loss）
                cv_net.fit(
                    X_train_fold,
                    y_train_fold,
                    w_train_fold,
                    X_val_fold,
                    y_val_fold,
                    w_val_fold
                )

                # 5. 验证集预测
                y_pred_fold = cv_net.predict(X_val_fold)

                # 6. 评估：Tweedie deviance（评估用，训练 loss 不动）
                loss += mean_tweedie_deviance(
                    y_val_fold,
                    y_pred_fold,
                    sample_weight=w_val_fold,
                    power=tw_power
                )

            finally:
                # 7. ★ 每个 fold 结束后释放 GPU 资源 ★
                try:
                    if hasattr(cv_net, "resnet"):
                        cv_net.resnet.to("cpu")
                except Exception:
                    pass
                del cv_net
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

        return loss / int(1 / self.ctx.prop_test)

    # ========= Optuna 调参 =========
    def tune(self, max_evals: int = 50) -> None:
        """
        使用 Optuna 对 ResNet 做贝叶斯优化。
        每个 trial 完成以后再做一次全局的显存清理。
        """
        def objective(trial: optuna.trial.Trial) -> float:
            result = self.cross_val(trial)
            # trial 级别兜底清理
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return result

        study = optuna.create_study(
            direction='minimize',
            sampler=optuna.samplers.TPESampler(seed=self.ctx.rand_seed)
        )
        study.optimize(objective, n_trials=max_evals)

        self.best_params = study.best_params
        self.best_trial = study.best_trial

        params_path = self.output.result_path(
            f'{self.ctx.model_nme}_bestparams_resn.csv'
        )
        pd.DataFrame(self.best_params, index=[0]).to_csv(params_path)

    # ========= 用最优超参训练最终 ResNet =========
    def train(self) -> None:
        if not self.best_params:
            raise RuntimeError('请先运行 tune() 以获得 ResNet 最优参数。')

        self.model = ResNetSklearn(
            model_nme=self.ctx.model_nme,
            input_dim=self.ctx.train_oht_scl_data[self.ctx.var_nmes].shape[1]
        )
        self.model.set_params(self.best_params)

        # 在全量 one-hot + 标准化数据上训练最终模型
        self.model.fit(
            self.ctx.train_oht_scl_data[self.ctx.var_nmes],
            self.ctx.train_oht_scl_data[self.ctx.resp_nme],
            self.ctx.train_oht_scl_data[self.ctx.weight_nme]
        )

        # 记录标签
        self.ctx.model_label += [self.label]

        # 训练集 / 测试集预测
        self.ctx.train_data['pred_resn'] = self.model.predict(
            self.ctx.train_oht_scl_data[self.ctx.var_nmes]
        )
        self.ctx.test_data['pred_resn'] = self.model.predict(
            self.ctx.test_oht_scl_data[self.ctx.var_nmes]
        )

        # 加权赔付
        self.ctx.train_data.loc[:, 'w_pred_resn'] = (
            self.ctx.train_data['pred_resn'] *
            self.ctx.train_data[self.ctx.weight_nme]
        )
        self.ctx.test_data.loc[:, 'w_pred_resn'] = (
            self.ctx.test_data['pred_resn'] *
            self.ctx.test_data[self.ctx.weight_nme]
        )

        # 方便外部调用
        self.ctx.resn_best = self.model

    # ========= 保存 / 加载 =========
    def save(self) -> None:
        """
        只保存 ResNet 的 state_dict（轻量，不含优化器）。
        """
        if self.model is not None:
            path = self.output.model_path(
                f'01_{self.ctx.model_nme}_ResNet.pth'
            )
            torch.save(self.model.resnet.state_dict(), path)

    def load(self) -> None:
        """
        从文件加载 ResNet 模型到合适的 device。
        """
        path = self.output.model_path(
            f'01_{self.ctx.model_nme}_ResNet.pth'
        )
        if os.path.exists(path):
            resn_loaded = ResNetSklearn(
                model_nme=self.ctx.model_nme,
                input_dim=self.ctx.train_oht_scl_data[self.ctx.var_nmes].shape[1]
            )
            state_dict = torch.load(path, map_location='cpu')
            resn_loaded.resnet.load_state_dict(state_dict)

            # 根据当前环境设置 device
            if torch.cuda.is_available():
                resn_loaded.device = torch.device('cuda')
            elif torch.backends.mps.is_available():
                resn_loaded.device = torch.device('mps')
            else:
                resn_loaded.device = torch.device('cpu')

            resn_loaded.resnet.to(resn_loaded.device)
            self.model = resn_loaded
            self.ctx.resn_best = self.model
        else:
            print(f"[ResNetTrainer.load] 未找到模型文件：{path}")


class FTTrainer(TrainerBase):
    def __init__(self, context: "BayesOptModel") -> None:
        super().__init__(context, 'FTTransformer')
        self.model: Optional[FTTransformerSklearn] = None
        self.best_params: Optional[Dict[str, Any]] = None
        self.best_trial = None

    def cross_val(self, trial: optuna.trial.Trial) -> float:
        """
        对 FT-Transformer 做交叉验证。
        这里是显存最容易爆的地方，所以加入了：
          - 较保守的超参搜索空间
          - 每个 fold 结束后强制释放 GPU 显存
        """
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
        batch_num = trial.suggest_int(
            'batch_num',
            5 if self.ctx.obj == 'reg:gamma' else 10,
            10 if self.ctx.obj == 'reg:gamma' else 50,
            step=1 if self.ctx.obj == 'reg:gamma' else 10
        )

        if self.ctx.obj == 'reg:tweedie':
            tw_power = trial.suggest_float('tw_power', 1.0, 2.0)
        elif self.ctx.obj == 'count:poisson':
            tw_power = 1.0
        elif self.ctx.obj == 'reg:gamma':
            tw_power = 2.0
        else:
            tw_power = 1.5

        loss = 0.0

        # 👉 可选：只在子样本上做 BO，避免大数据直接压垮显存
        data_for_cv = self.ctx.train_data
        max_rows_for_ft_bo = min(1000000, int(
            len(data_for_cv)/2))   # 你可以根据显存情况调小或调大
        if len(data_for_cv) > max_rows_for_ft_bo:
            data_for_cv = data_for_cv.sample(
                max_rows_for_ft_bo,
                random_state=self.ctx.rand_seed
            )

        for _, (train_idx, test_idx) in enumerate(
            self.ctx.cv.split(data_for_cv[self.ctx.factor_nmes])
        ):
            X_train_fold = data_for_cv.iloc[train_idx][self.ctx.factor_nmes]
            y_train_fold = data_for_cv.iloc[train_idx][self.ctx.resp_nme]
            w_train_fold = data_for_cv.iloc[train_idx][self.ctx.weight_nme]
            X_val_fold = data_for_cv.iloc[test_idx][self.ctx.factor_nmes]
            y_val_fold = data_for_cv.iloc[test_idx][self.ctx.resp_nme]
            w_val_fold = data_for_cv.iloc[test_idx][self.ctx.weight_nme]

            cv_ft = FTTransformerSklearn(
                model_nme=self.ctx.model_nme,
                num_cols=self.ctx.num_features,
                cat_cols=self.ctx.cate_list,
                d_model=d_model,
                n_heads=n_heads,
                n_layers=n_layers,
                dropout=dropout,
                batch_num=batch_num,
                epochs=self.ctx.epochs,
                tweedie_power=tw_power,
                learning_rate=learning_rate,
                patience=5
            )

            try:
                cv_ft.fit(
                    X_train_fold, y_train_fold, w_train_fold,
                    X_val_fold, y_val_fold, w_val_fold
                )
                y_pred_fold = cv_ft.predict(X_val_fold)
                loss += mean_tweedie_deviance(
                    y_val_fold,
                    y_pred_fold,
                    sample_weight=w_val_fold,
                    power=tw_power
                )
            finally:
                # 🧹 每个 fold 用完就立即释放 GPU 资源
                try:
                    # 如果模型在 GPU 上，先挪回 CPU
                    if hasattr(cv_ft, "ft"):
                        cv_ft.ft.to("cpu")
                except Exception:
                    pass
                del cv_ft
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

        return loss / int(1 / self.ctx.prop_test)

    def tune(self, max_evals: int = 50) -> None:
        """
        用 Optuna 做超参搜索。
        在每个 trial 结束后再做一次显存清理，避免 trial 间显存碎片堆积。
        """
        def objective(trial: optuna.trial.Trial) -> float:
            result = self.cross_val(trial)
            # trial 级别的兜底清理
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return result

        study = optuna.create_study(
            direction='minimize',
            sampler=optuna.samplers.TPESampler(seed=self.ctx.rand_seed)
        )
        study.optimize(objective, n_trials=max_evals)
        self.best_params = study.best_params
        self.best_trial = study.best_trial
        params_path = self.output.result_path(
            f'{self.ctx.model_nme}_bestparams_ft.csv'
        )
        pd.DataFrame(self.best_params, index=[0]).to_csv(params_path)

    def train(self) -> None:
        if not self.best_params:
            raise RuntimeError('请先运行 tune() 以获得 FT-Transformer 最优参数。')
        self.model = FTTransformerSklearn(
            model_nme=self.ctx.model_nme,
            num_cols=self.ctx.num_features,
            cat_cols=self.ctx.cate_list
        )
        self.model.set_params(self.best_params)
        self.model.fit(
            self.ctx.train_data[self.ctx.factor_nmes],
            self.ctx.train_data[self.ctx.resp_nme],
            self.ctx.train_data[self.ctx.weight_nme]
        )
        self.ctx.model_label += [self.label]
        self.ctx.train_data['pred_ft'] = self.model.predict(
            self.ctx.train_data[self.ctx.factor_nmes]
        )
        self.ctx.test_data['pred_ft'] = self.model.predict(
            self.ctx.test_data[self.ctx.factor_nmes]
        )
        self.ctx.train_data.loc[:, 'w_pred_ft'] = (
            self.ctx.train_data['pred_ft'] *
            self.ctx.train_data[self.ctx.weight_nme]
        )
        self.ctx.test_data.loc[:, 'w_pred_ft'] = (
            self.ctx.test_data['pred_ft'] *
            self.ctx.test_data[self.ctx.weight_nme]
        )
        self.ctx.ft_best = self.model

    def save(self) -> None:
        if self.model is not None:
            torch.save(
                self.model,
                self.output.model_path(
                    f'01_{self.ctx.model_nme}_FTTransformer.pth')
            )

    def load(self) -> None:
        path = self.output.model_path(
            f'01_{self.ctx.model_nme}_FTTransformer.pth')
        if os.path.exists(path):
            ft_loaded = torch.load(path, map_location='cpu')
            if torch.cuda.is_available():
                ft_loaded.device = torch.device('cuda')
            elif torch.backends.mps.is_available():
                ft_loaded.device = torch.device('mps')
            else:
                ft_loaded.device = torch.device('cpu')
            ft_loaded.ft.to(ft_loaded.device)
            self.model = ft_loaded
            self.ctx.ft_best = self.model
        else:
            print(f"[load_model] Warning: 未找到 FT-Transformer 模型文件：{path}")


# =============================================================================
# BayesOpt orchestration & SHAP utilities
# =============================================================================
class BayesOptModel:
    def __init__(self, train_data, test_data,
                 model_nme, resp_nme, weight_nme, factor_nmes,
                 cate_list=None, prop_test=0.25, rand_seed=None,
                 epochs=100, use_gpu=True):
        cfg = BayesOptConfig(
            model_nme=model_nme,
            resp_nme=resp_nme,
            weight_nme=weight_nme,
            factor_nmes=list(factor_nmes),
            cate_list=list(cate_list) if cate_list else None,
            prop_test=prop_test,
            rand_seed=rand_seed,
            epochs=epochs,
            use_gpu=use_gpu
        )
        self.config = cfg
        self.model_nme = cfg.model_nme
        self.resp_nme = cfg.resp_nme
        self.weight_nme = cfg.weight_nme
        self.factor_nmes = cfg.factor_nmes
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
        if self.model_nme.find('f') != -1:
            self.obj = 'count:poisson'
        elif self.model_nme.find('s') != -1:
            self.obj = 'reg:gamma'
        elif self.model_nme.find('bc') != -1:
            self.obj = 'reg:tweedie'
        else:
            self.obj = 'reg:tweedie'
        self.fit_params = {
            'sample_weight': self.train_data[self.weight_nme].values
        }
        self.model_label: List[str] = []

        # 记录各模型训练器，后续统一通过标签访问，方便扩展新模型
        self.trainers: Dict[str, TrainerBase] = {
            'xgb': XGBTrainer(self),
            'resn': ResNetTrainer(self),
            'ft': FTTrainer(self)
        }
        self.xgb_best = None
        self.resn_best = None
        self.ft_best = None
        self.best_xgb_params = None
        self.best_resn_params = None
        self.best_ft_params = None
        self.best_xgb_trial = None
        self.best_resn_trial = None
        self.best_ft_trial = None
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

    # 定义Xgboost贝叶斯优化函数
    def bayesopt_xgb(self, max_evals=100):
        trainer = self.trainers['xgb']
        trainer.tune(max_evals)
        trainer.train()
        self.xgb_best = trainer.model
        # 记录最优参数及 trial 以便排查或复现结果
        self.best_xgb_params = trainer.best_params
        self.best_xgb_trial = trainer.best_trial

    # 定义ResNet贝叶斯优化函数
    def bayesopt_resnet(self, max_evals=100):
        trainer = self.trainers['resn']
        trainer.tune(max_evals)
        trainer.train()
        self.resn_best = trainer.model
        # 保存最优 trial 相关信息，方便后续调参分析
        self.best_resn_params = trainer.best_params
        self.best_resn_trial = trainer.best_trial

    # 定义 FT-Transformer 贝叶斯优化函数
    def bayesopt_ft(self, max_evals=50):
        trainer = self.trainers['ft']
        trainer.tune(max_evals)
        trainer.train()
        self.ft_best = trainer.model
        # FT-Transformer 参数较多，留存配置信息尤其重要
        self.best_ft_params = trainer.best_params
        self.best_ft_trial = trainer.best_trial

    # 定义分箱函数

    def _split_data(self, data, col_nme, wgt_nme, n_bins=10):
        # 先按得分排序再按累计权重等分，能保证每个分箱曝光量接近
        sorted_data = data.sort_values(by=col_nme, ascending=True).copy()
        sorted_data['cum_weight'] = sorted_data[wgt_nme].cumsum()
        w_sum = sorted_data[wgt_nme].sum()
        if w_sum <= EPS:
            sorted_data.loc[:, 'bins'] = 0
        else:
            sorted_data.loc[:, 'bins'] = np.floor(
                sorted_data['cum_weight'] * float(n_bins) / w_sum
            )
            sorted_data.loc[(sorted_data['bins'] == n_bins),
                            'bins'] = n_bins - 1
        return sorted_data.groupby(['bins'], observed=True).sum(numeric_only=True)

    # 构建提纯曲线所需的数据
    def _plot_data_lift(self,
                        pred_list, w_pred_list,
                        w_act_list, weight_list, n_bins=10):
        lift_data = pd.DataFrame()
        lift_data.loc[:, 'pred'] = pred_list
        lift_data.loc[:, 'w_pred'] = w_pred_list
        lift_data.loc[:, 'act'] = w_act_list
        lift_data.loc[:, 'weight'] = weight_list
        plot_data = self._split_data(
            lift_data, 'pred', 'weight', n_bins)
        denom = np.maximum(plot_data['weight'], EPS)
        plot_data['exp_v'] = plot_data['w_pred'] / denom
        plot_data['act_v'] = plot_data['act'] / denom
        plot_data.reset_index(inplace=True)
        return plot_data

    # 绘制提纯曲线
    def plot_lift(self, model_label, pred_nme, n_bins=10):
        # 绘制建模集上结果
        figpos_list = [121, 122]
        plot_dict = {
            121: self.train_data,
            122: self.test_data
        }
        name_list = {
            121: 'Train Data',
            122: 'Test Data'
        }
        if model_label == 'Xgboost':
            pred_nme = 'pred_xgb'
        elif model_label == 'ResNet':
            pred_nme = 'pred_resn'
        elif model_label == 'FTTransformer':
            pred_nme = 'pred_ft'
        # pred_nme 映射保证后续取列统一，否则新模型加入时需同步更新

        fig = plt.figure(figsize=(11, 5))
        for figpos in figpos_list:
            plot_data = self._plot_data_lift(
                plot_dict[figpos][pred_nme].values,
                plot_dict[figpos]['w_'+pred_nme].values,
                plot_dict[figpos]['w_act'].values,
                plot_dict[figpos][self.weight_nme].values,
                n_bins)
            ax = fig.add_subplot(figpos)
            ax.plot(plot_data.index, plot_data['act_v'],
                    label='Actual', color='red')
            ax.plot(plot_data.index, plot_data['exp_v'],
                    label='Predicted', color='blue')
            ax.set_title(
                'Lift Chart on %s' % name_list[figpos], fontsize=8)
            plt.xticks(plot_data.index,
                       plot_data.index,
                       rotation=90, fontsize=6)
            plt.yticks(fontsize=6)
            plt.legend(loc='upper left',
                       fontsize=5, frameon=False)
            plt.margins(0.05)
            ax2 = ax.twinx()
            ax2.bar(plot_data.index, plot_data['weight'],
                    alpha=0.5, color='seagreen',
                    label='Earned Exposure')
            plt.yticks(fontsize=6)
            plt.legend(loc='upper right',
                       fontsize=5, frameon=False)
            plt.subplots_adjust(wspace=0.3)
            save_path = self.output_manager.plot_path(
                f'01_{self.model_nme}_{model_label}_lift.png')
            plt.savefig(save_path, dpi=300)
        plt.show()
        plt.close(fig)

    # 构建双提纯曲线所需的数据
    def _plot_data_dlift(self,
                         pred_list_model1, pred_list_model2,
                         w_list, w_act_list, n_bins=10):
        lift_data = pd.DataFrame()
        lift_data.loc[:, 'pred1'] = pred_list_model1
        lift_data.loc[:, 'pred2'] = pred_list_model2
        lift_data.loc[:, 'diff_ly'] = lift_data['pred1'] / lift_data['pred2']
        lift_data.loc[:, 'act'] = w_act_list
        lift_data.loc[:, 'weight'] = w_list
        plot_data = self._split_data(lift_data, 'diff_ly', 'weight', n_bins)
        denom = np.maximum(plot_data['act'], EPS)
        plot_data['exp_v1'] = plot_data['pred1'] / denom
        plot_data['exp_v2'] = plot_data['pred2'] / denom
        plot_data['act_v'] = plot_data['act'] / denom
        plot_data.reset_index(inplace=True)
        return plot_data

    # 绘制双提纯曲线
    def plot_dlift(self, model_comp: List[str] = ['xgb', 'resn'], n_bins: int = 10) -> None:
        """
        绘制双提纯曲线，对比两个模型的预测效果。

        Args:
            model_comp: 包含两个模型简称的列表，例如 ['xgb', 'resn']。
                        支持 'xgb', 'resn', 'ft'。
            n_bins: 分箱数量。
        """
        if len(model_comp) != 2:
            raise ValueError("`model_comp` 必须包含两个模型进行对比。")

        model_name_map = {
            'xgb': 'Xgboost',
            'resn': 'ResNet',
            'ft': 'FTTransformer'
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

            plot_data = self._plot_data_dlift(
                data[pred1_col].values,
                data[pred2_col].values,
                data[self.weight_nme].values,
                data['w_act'].values,
                n_bins
            )

            label1 = model_name_map[name1]
            label2 = model_name_map[name2]

            ax.plot(plot_data.index,
                    plot_data['act_v'], label='Actual', color='red')
            ax.plot(plot_data.index,
                    plot_data['exp_v1'], label=label1, color='blue')
            ax.plot(plot_data.index,
                    plot_data['exp_v2'], label=label2, color='black')

            ax.set_title(f'Double Lift Chart on {data_name}', fontsize=8)
            ax.set_xticks(plot_data.index)
            ax.set_xticklabels(plot_data.index, rotation=90, fontsize=6)
            ax.set_xlabel(f'{label1} / {label2}', fontsize=6)
            ax.tick_params(axis='y', labelsize=6)
            ax.legend(loc='upper left', fontsize=5, frameon=False)
            ax.margins(0.1)

            ax2 = ax.twinx()
            ax2.bar(plot_data.index, plot_data['weight'],
                    alpha=0.5, color='seagreen', label='Earned Exposure')
            ax2.tick_params(axis='y', labelsize=6)
            ax2.legend(loc='upper right', fontsize=5, frameon=False)

        plt.subplots_adjust(bottom=0.25, top=0.95, right=0.8, wspace=0.3)
        save_path = self.output_manager.plot_path(
            f'02_{self.model_nme}_dlift_{name1}_vs_{name2}.png')
        plt.savefig(save_path, dpi=300)
        plt.show()
        plt.close(fig)

    # 保存模型

    def save_model(self, model_name=None):

        # model_name 可以是:
        #   - None: 保存全部可用模型
        #   - 'xgb': 只保存 Xgboost
        #   - 'resn': 只保存 ResNet
        #   - 'ft': 只保存 FT-Transformer
        if model_name in (None, 'xgb'):
            trainer = self.trainers['xgb']
            if trainer.model is not None:
                trainer.save()
            else:
                print("[save_model] Warning: xgb_best 不存在,未保存 Xgboost 模型。")

        if model_name in (None, 'resn'):
            trainer = self.trainers['resn']
            if trainer.model is not None:
                trainer.save()
            else:
                print("[save_model] Warning: resn_best 不存在,未保存 ResNet 模型。")

        if model_name in (None, 'ft'):
            trainer = self.trainers['ft']
            if trainer.model is not None:
                trainer.save()
            else:
                print("[save_model] Warning: ft_best 不存在,未保存 FT-Transformer 模型。")

    def load_model(self, model_name=None):
        # model_name 可以是:
        #   - None: 加载全部能找到的模型
        #   - 'xgb': 只加载 Xgboost
        #   - 'resn': 只加载 ResNet
        #   - 'ft': 只加载 FT-Transformer

        if model_name in (None, 'xgb'):
            trainer = self.trainers['xgb']
            trainer.load()
            self.xgb_best = trainer.model
            self.xgb_load = trainer.model

        if model_name in (None, 'resn'):
            trainer = self.trainers['resn']
            trainer.load()
            self.resn_best = trainer.model
            self.resn_load = trainer.model

        if model_name in (None, 'ft'):
            trainer = self.trainers['ft']
            trainer.load()
            self.ft_best = trainer.model
            self.ft_load = trainer.model

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

    # ========= XGBoost SHAP =========

    def compute_shap_xgb(self, n_background: int = 500,
                         n_samples: int = 200,
                         on_train: bool = True):
        # 使用 KernelExplainer 计算 XGBoost 的 SHAP 值（黑盒方式）。
        #
        # - 对 SHAP：输入是一份纯数值矩阵：
        #     * 数值特征：float64
        #     * 类别特征：用 _build_ft_shap_matrix 编码后的整数 code（float64）
        # - 对模型：仍然用原始 DataFrame + xgb_best.predict(...)

        if not hasattr(self, "xgb_best"):
            raise RuntimeError("请先运行 bayesopt_xgb() 训练好 self.xgb_best")

        # 1) 选择数据源：训练集 or 测试集（原始特征空间）
        data = self.train_data if on_train else self.test_data
        X_raw = data[self.factor_nmes]

        # 2) 构造背景矩阵（用和 FT 一样的数值编码）
        background_raw = X_raw.sample(
            min(len(X_raw), n_background),
            random_state=self.rand_seed
        )
        # KernelExplainer 计算量极大，务必控制背景样本规模，否则会拖慢调试
        background_mat = self._build_ft_shap_matrix(
            background_raw
        ).astype(np.float64, copy=True)

        # 3) 定义黑盒预测函数：数值矩阵 -> DataFrame -> xgb_best.predict
        def f_predict(x_mat: np.ndarray) -> np.ndarray:
            # 把编码矩阵还原成原始 DataFrame（数值+类别）
            df_input = self._decode_ft_shap_matrix_to_df(x_mat)
            # 注意：这里用的是 self.xgb_best.predict，和你训练/预测时一致
            y_pred = self.xgb_best.predict(df_input)
            return y_pred

        explainer = shap.KernelExplainer(f_predict, background_mat)

        # 4) 要解释的样本：原始特征 + 数值编码
        X_explain_raw = X_raw.sample(
            min(len(X_raw), n_samples),
            random_state=self.rand_seed
        )
        X_explain_mat = self._build_ft_shap_matrix(
            X_explain_raw
        ).astype(np.float64, copy=True)

        # 5) 计算 SHAP 值（注意用 nsamples='auto' 控制复杂度）
        shap_values = explainer.shap_values(X_explain_mat, nsamples="auto")

        # 6) 保存结果：
        #   - shap_values：数值编码空间，对应 factor_nmes 的每一列
        #   - X_explain_raw：原始 DataFrame，方便画图时显示真实类别名
        self.shap_xgb = {
            "explainer": explainer,
            "X_explain": X_explain_raw,
            "shap_values": shap_values,
            "base_value": explainer.expected_value,
        }
        return self.shap_xgb
    # ========= ResNet SHAP =========

    def _resn_predict_wrapper(self, X_np):
        # 保证走 CPU
        model = self.resn_best.resnet.to("cpu")
        with torch.no_grad():
            # 不要 .to(self.device)
            X_tensor = torch.tensor(X_np, dtype=torch.float32)
            y_pred = model(X_tensor).cpu().numpy()
        y_pred = np.clip(y_pred, 1e-6, None)
        return y_pred.reshape(-1)

    def compute_shap_resn(self, n_background: int = 500,
                          n_samples: int = 200,
                          on_train: bool = True):

        # 使用 KernelExplainer 计算 ResNet 的 SHAP 值。
        # 解释空间：已 one-hot & 标准化后的特征 self.var_nmes。

        if not hasattr(self, 'resn_best'):
            raise RuntimeError("请先运行 bayesopt_resnet() 训练好 resn_best")

        self.resn_best.device = torch.device("cpu")  # 强制走 CPU
        self.resn_best.resnet.to("cpu")
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # 选择数据集（已 one-hot & 标准化）
        data = self.train_oht_scl_data if on_train else self.test_oht_scl_data
        X = data[self.var_nmes]
        if len(X) == 0:
            raise ValueError(
                "compute_shap_resn: 选择的数据集为空（len(X)==0），无法计算 SHAP。")

        # 背景样本：float64 numpy
        background_df = X.sample(
            min(len(X), n_background),
            random_state=self.rand_seed
        )
        background_np = background_df.to_numpy(dtype=np.float64, copy=True)

        # 黑盒预测函数
        def f_predict(x):
            y = self._resn_predict_wrapper(x)
            # 保证是一维数组
            y = np.asarray(y, dtype=np.float64).reshape(-1)
            return y

        explainer = shap.KernelExplainer(f_predict, background_np)

        # 要解释的样本
        X_explain_df = X.sample(
            min(len(X), n_samples),
            random_state=self.rand_seed
        )
        X_explain_np = X_explain_df.to_numpy(dtype=np.float64, copy=True)

        max_nsamples = 300
        min_needed = X_explain_np.shape[1] + 2
        nsample_eff = max(min_needed, min(max_nsamples,
                                          X_explain_np.shape[0] * X_explain_np.shape[1]))
        shap_values = explainer.shap_values(X_explain_np, nsamples=nsample_eff)
        # 手动计算 base_value，避免 NotOneValueFound
        bg_pred = f_predict(background_np)
        if bg_pred.size == 0:
            raise ValueError("compute_shap_resn: 背景样本预测结果为空，无法计算 base_value。")
        base_value = float(bg_pred.mean())

        self.shap_resn = {
            "explainer": explainer,
            "X_explain": X_explain_df,     # DataFrame: 用于画图（有列名）
            "shap_values": shap_values,    # numpy: (n_samples, n_features)
            # "base_value": explainer.expected_value,
            "base_value": base_value,
        }
        return self.shap_resn

    # ========= FT-Transformer SHAP =========

    def _ft_shap_predict_wrapper(self, X_mat: np.ndarray) -> np.ndarray:

        # SHAP 的预测包装：
        # 数值矩阵 -> 还原为原始特征 DataFrame -> 调用 ft_best.predict

        df_input = self._decode_ft_shap_matrix_to_df(X_mat)
        y_pred = self.ft_best.predict(df_input)
        return np.asarray(y_pred, dtype=np.float64).reshape(-1)

    def compute_shap_ft(self, n_background: int = 500,
                        n_samples: int = 200,
                        on_train: bool = True):

        # 使用 KernelExplainer 计算 FT-Transformer 的 SHAP 值。
        # 解释空间：数值+类别code 的混合数值矩阵（float64），
        # 但对外展示时仍使用原始特征名/取值（X_explain）。

        if not hasattr(self, "ft_best"):
            raise RuntimeError("请先运行 bayesopt_ft() 训练好 ft_best")

        self.ft_best.device = torch.device("cpu")  # 强制走 CPU
        self.ft_best.ft.to("cpu")
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # 选择数据源（原始特征空间）
        data = self.train_data if on_train else self.test_data
        X_raw = data[self.factor_nmes]

        # 背景矩阵
        background_raw = X_raw.sample(
            min(len(X_raw), n_background),
            random_state=self.rand_seed
        )
        background_mat = self._build_ft_shap_matrix(
            background_raw
        ).astype(np.float64, copy=True)

        # 黑盒预测函数（数值矩阵 → DataFrame → FT 模型）
        def f_predict(x):
            return self._ft_shap_predict_wrapper(x)

        explainer = shap.KernelExplainer(f_predict, background_mat)

        # 要解释的样本（原始特征空间）
        X_explain_raw = X_raw.sample(
            min(len(X_raw), n_samples),
            random_state=self.rand_seed
        )
        X_explain_mat = self._build_ft_shap_matrix(
            X_explain_raw
        ).astype(np.float64, copy=True)

        max_nsamples = 300
        min_needed = X_explain_mat.shape[1] + 2
        nsample_eff = max(min_needed, min(max_nsamples,
                                          X_explain_mat.shape[0] * X_explain_mat.shape[1]))
        shap_values = explainer.shap_values(
            X_explain_mat, nsamples=nsample_eff)
        bg_pred = self._ft_shap_predict_wrapper(background_mat)
        bg_pred = np.asarray(bg_pred, dtype=np.float64).reshape(-1)
        base_value = float(bg_pred.mean())

        self.shap_ft = {
            "explainer": explainer,
            "X_explain": X_explain_raw,   # 原始特征 DataFrame，用来画图
            "shap_values": shap_values,   # numpy: (n_samples, n_features)
            # "base_value": explainer.expected_value,
            "base_value": base_value,
        }
        return self.shap_ft
