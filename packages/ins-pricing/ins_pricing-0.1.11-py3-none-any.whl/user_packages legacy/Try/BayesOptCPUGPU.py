# 数据在CPU和GPU之间传输会带来较大开销,但可以多CUDA流同时传输数据和计算,从而实现更大数据集的操作。

import pandas as pd
import numpy as np
from random import sample
from re import X
from turtle import st
from uuid import RESERVED_FUTURE
import numpy as np  # 1.26.2
import pandas as pd  # 2.2.3
import torch  # 1.10.1+cu111
import torch.nn as nn
import torch.nn.functional as F
import optuna  # 4.3.0
import xgboost as xgb  # 1.7.0
import matplotlib.pyplot as plt
import os
import joblib
import copy
import shap
import math
import gc

from torch.utils.data import Dataset, DataLoader, TensorDataset
from torch.cuda.amp import autocast, GradScaler
from torch.nn.utils import clip_grad_norm_
from sklearn.model_selection import ShuffleSplit, cross_val_score  # 1.2.2
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import make_scorer, mean_tweedie_deviance

# 定义torch下tweedie deviance损失函数
# 参考：https://scikit-learn.org/stable/modules/model_evaluation.html#mean-poisson-gamma-and-tweedie-deviances


def tweedie_loss(pred, target, p=1.5, eps=1e-6, max_clip=1e6):
    # Ensure predictions are positive for stability
    pred_clamped = torch.clamp(pred, min=eps)
    # Compute Tweedie deviance components
    if p == 1:
        # Poisson case
        term1 = target * torch.log(target / pred_clamped + eps)
        term2 = -target + pred_clamped
        term3 = 0
    elif p == 0:
        # Gaussian case
        term1 = 0.5 * torch.pow(target - pred_clamped, 2)
        term2 = 0
        term3 = 0
    elif p == 2:
        # Gamma case
        term1 = torch.log(pred_clamped / target + eps)
        term2 = -target / pred_clamped + 1
        term3 = 0
    else:
        term1 = torch.pow(target, 2 - p) / ((1 - p) * (2 - p))
        term2 = target * torch.pow(pred_clamped, 1 - p) / (1 - p)
        term3 = torch.pow(pred_clamped, 2 - p) / (2 - p)
    # Tweedie negative log-likelihood (up to a constant)
    return torch.nan_to_num(2 * (term1 - term2 + term3), nan=eps, posinf=max_clip, neginf=-max_clip)

# 定义释放CUDA内存函数


def free_cuda():
    print(">>> Moving all models to CPU...")
    for obj in gc.get_objects():
        try:
            if hasattr(obj, "to") and callable(obj.to):
                # skip torch.device
                obj.to("cpu")
        except:
            pass

    print(">>> Deleting tensors, optimizers, dataloaders...")
    gc.collect()

    print(">>> Emptying CUDA cache...")
    torch.cuda.empty_cache()
    torch.cuda.synchronize()

    print(">>> CUDA memory freed.")


# 定义分箱函数


def split_data(data, col_nme, wgt_nme, n_bins=10):
    data.sort_values(by=col_nme, ascending=True, inplace=True)
    data['cum_weight'] = data[wgt_nme].cumsum()
    w_sum = data[wgt_nme].sum()
    data.loc[:, 'bins'] = np.floor(data['cum_weight'] * float(n_bins) / w_sum)
    data.loc[(data['bins'] == n_bins), 'bins'] = n_bins - 1
    return data.groupby(['bins'], observed=True).sum(numeric_only=True)

# 定义Lift Chart绘制函数


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
    plt.savefig(save_path, dpi=300)
    plt.close(fig)

# 定义Double Lift Chart绘制函数


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
    plt.savefig(save_path, dpi=300)
    plt.close(fig)


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
        # pre-activation
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
    # 输入: (batch, input_dim)
    # 结构:
    #   fc1 -> LN/Bn -> ReLU -> ResBlock * block_num -> fc_out -> Softplus

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

        # Tweedie power
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

    def fit(self, X_train, y_train, w_train=None,
            X_val=None, y_val=None, w_val=None):

        # === 1. 训练集：留在 CPU,交给 DataLoader 再搬到 GPU ===
        X_tensor = torch.tensor(X_train.values, dtype=torch.float32)
        y_tensor = torch.tensor(
            y_train.values, dtype=torch.float32).view(-1, 1)
        if w_train is not None:
            w_tensor = torch.tensor(
                w_train.values, dtype=torch.float32).view(-1, 1)
        else:
            w_tensor = torch.ones_like(y_tensor)

        # === 2. 验证集：先在 CPU 上建,后面一次性搬到 device ===
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

        # === 3. DataLoader ===
        dataset = TensorDataset(X_tensor, y_tensor, w_tensor)
        batch_size = max(
            4096,
            int((self.learning_rate / (1e-4)) ** 0.5 *
                (X_train.shape[0] / self.batch_num))
        )

        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=1,  # tabular: 0~1 一般够用
            pin_memory=(self.device.type == 'cuda')
        )

        # === 4. 优化器 & AMP ===
        optimizer = torch.optim.Adam(
            self.resnet.parameters(), lr=self.learning_rate)
        scaler = GradScaler(enabled=(self.device.type == 'cuda'))

        # === 5. Early stopping ===
        best_loss, patience_counter = float('inf'), 0
        best_model_state = None

        # 如果有验证集,先把它整个搬到 device,只搬一次
        if has_val:
            X_val_dev = X_val_tensor.to(self.device, non_blocking=True)
            y_val_dev = y_val_tensor.to(self.device, non_blocking=True)
            w_val_dev = w_val_tensor.to(self.device, non_blocking=True)

        # === 6. 训练循环 ===
        for epoch in range(1, self.epochs + 1):
            self.resnet.train()
            for X_batch, y_batch, w_batch in dataloader:
                optimizer.zero_grad()

                X_batch = X_batch.to(self.device, non_blocking=True)
                y_batch = y_batch.to(self.device, non_blocking=True)
                w_batch = w_batch.to(self.device, non_blocking=True)

                with autocast(enabled=(self.device.type == 'cuda')):
                    y_pred = self.resnet(X_batch)
                    y_pred = torch.clamp(y_pred, min=1e-6)

                    losses = tweedie_loss(
                        y_pred, y_batch, p=self.tw_power).view(-1)
                    weighted_loss = (losses * w_batch.view(-1)
                                     ).sum() / w_batch.sum()

                scaler.scale(weighted_loss).backward()

                if self.device.type == 'cuda':
                    scaler.unscale_(optimizer)
                    clip_grad_norm_(self.resnet.parameters(), max_norm=1.0)

                scaler.step(optimizer)
                scaler.update()

            # === 7. 验证集损失 & early stopping ===
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
                    ).sum() / w_val_dev.sum()

                if val_weighted_loss < best_loss:
                    best_loss = val_weighted_loss
                    patience_counter = 0
                    best_model_state = copy.deepcopy(self.resnet.state_dict())
                else:
                    patience_counter += 1

                if patience_counter >= self.patience and best_model_state is not None:
                    self.resnet.load_state_dict(best_model_state)
                    break

    # ---------------- predict ----------------

    def predict(self, X_test):
        self.resnet.eval()
        with torch.no_grad():
            X_tensor = torch.tensor(
                X_test.values, dtype=torch.float32).to(self.device)
            y_pred = self.resnet(X_tensor).cpu().numpy()

        y_pred = np.clip(y_pred, 1e-6, None)
        return y_pred.flatten()

    # ---------------- set_params ----------------

    def set_params(self, params):
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Parameter {key} not found in model.")

# 开始定义FT Transformer模型结构


class FeatureTokenizer(nn.Module):
    # 将数值特征 & 类别特征映射为 token (batch, n_tokens, d_model)
    # 假设:
    #   - X_num: (batch, num_numeric)
    #   - X_cat: (batch, num_categorical),每列是已编码好的整数标签 [0, card-1]

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
            # 数值特征映射为一个 token
            num_token = self.num_linear(X_num)          # (batch, d_model)
            tokens.append(num_token)

        # 每个类别特征一个 embedding token
        for i, emb in enumerate(self.embeddings):
            tok = emb(X_cat[:, i])                     # (batch, d_model)
            tokens.append(tok)

        # (batch, n_tokens, d_model)
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

        # FFN
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(dim_feedforward, d_model)

        # Norm & Dropout
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

        self.activation = nn.GELU()
        self.norm_first = norm_first

        # 残差缩放系数
        self.res_scale_attn = residual_scale_attn
        self.res_scale_ffn = residual_scale_ffn

    def forward(self, src, src_mask=None, src_key_padding_mask=None):
        """
        src: (B, T, d_model)
        """
        x = src

        if self.norm_first:
            # pre-norm
            x = x + self._sa_block(self.norm1(x), src_mask,
                                   src_key_padding_mask)
            x = x + self._ff_block(self.norm2(x))
        else:
            # post-norm（一般不用）
            x = self.norm1(
                x + self._sa_block(x, src_mask, src_key_padding_mask))
            x = self.norm2(x + self._ff_block(x))

        return x

    def _sa_block(self, x, attn_mask, key_padding_mask):
        # Self-Attention + 残差缩放
        attn_out, _ = self.self_attn(
            x, x, x,
            attn_mask=attn_mask,
            key_padding_mask=key_padding_mask,
            need_weights=False
        )
        return self.res_scale_attn * self.dropout1(attn_out)

    def _ff_block(self, x):
        # FFN + 残差缩放
        x2 = self.linear2(self.dropout(self.activation(self.linear1(x))))
        return self.res_scale_ffn * self.dropout2(x2)

# 定义FT-Transformer核心模型


class FTTransformerCore(nn.Module):
    # 一个最小可用的 FT-Transformer：
    #   - FeatureTokenizer: 数值、类别 → token
    #   - TransformerEncoder: 捕捉特征交互
    #   - 池化 + MLP + Softplus: 输出正值 (适配 Tweedie/Gamma)

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
            nn.Linear(d_model, 1),
            nn.Softplus()  # 保证输出为正,适合 Tweedie / Gamma
        )

    def forward(self, X_num, X_cat):

        # X_num: (batch, num_numeric) float32
        # X_cat: (batch, num_categorical) long

        tokens = self.tokenizer(X_num, X_cat)  # (batch, tokens, d_model)
        x = self.encoder(tokens)               # (batch, tokens, d_model)

        # 简单地对 token 取平均池化
        x = x.mean(dim=1)                      # (batch, d_model)

        out = self.head(x)                     # (batch, 1), Softplus 已做
        return out

# 定义TabularDataset类


class TabularDataset(Dataset):
    def __init__(self, X_num, X_cat, y, w):

        # X_num: torch.float32, (N, num_numeric)
        # X_cat: torch.long,    (N, num_categorical)
        # y:     torch.float32, (N, 1)
        # w:     torch.float32, (N, 1)

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
    #   - num_cols: 数值特征列名列表
    #   - cat_cols: 类别特征列名列表 (已做 label encoding,取值 [0, n_classes-1])

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
        # X: DataFrame,至少包含 self.cat_cols
        # 返回: np.ndarray, shape (N, num_categorical), dtype=int64

        if not self.cat_cols:
            return np.zeros((len(X), 0), dtype='int64')

        X_cat_list = []
        for col in self.cat_cols:
            # 使用训练时记录下来的 categories
            categories = self.cat_categories[col]
            # 用固定的 categories 构造 Categorical
            cats = pd.Categorical(X[col], categories=categories)
            codes = cats.codes.astype('int64', copy=True)   # -1 表示未知或缺失
            # 未知 / 缺失 映射到“未知类 bucket”,索引 = len(categories)
            codes[codes < 0] = len(categories)
            X_cat_list.append(codes)

        X_cat_np = np.stack(X_cat_list, axis=1)  # (N, num_categorical)
        return X_cat_np

    def fit(self, X_train, y_train, w_train=None,
            X_val=None, y_val=None, w_val=None):

        # 第一次 fit 时构建模型结构
        if self.ft is None:
            self._build_model(X_train)

        # --- 构建训练张量 (全在 CPU,后面 batch 再搬 GPU) ---
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
                (X_num_train.size(0), 0), dtype=torch.long)

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

        # --- 验证集张量 (后面一次性搬到 device) ---
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

        # --- DataLoader ---
        dataset = TabularDataset(
            X_num_train, X_cat_train, y_tensor, w_tensor
        )

        batch_size = max(
            32,
            int((self.learning_rate / 1e-4) ** 0.5 *
                (X_train.shape[0] / self.batch_num))
        )

        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=1,
            pin_memory=(self.device.type == 'cuda')
        )

        # --- 优化器 & AMP ---
        optimizer = torch.optim.Adam(
            self.ft.parameters(),
            lr=self.learning_rate
        )
        scaler = GradScaler(enabled=(self.device.type == 'cuda'))

        # --- Early stopping ---
        best_loss = float('inf')
        patience_counter = 0
        best_model_state = None

        # 验证集整体搬到 device（如果存在）
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

                    weighted_loss = (losses * w_b.view(-1)).sum() / w_b.sum()

                scaler.scale(weighted_loss).backward()

                if self.device.type == 'cuda':
                    scaler.unscale_(optimizer)
                    clip_grad_norm_(self.ft.parameters(), max_norm=1.0)

                scaler.step(optimizer)
                scaler.update()

            # --- 验证 & early stopping ---
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
                    ).sum() / w_val_dev.sum()

                if val_weighted_loss < best_loss:
                    best_loss = val_weighted_loss
                    patience_counter = 0
                    best_model_state = copy.deepcopy(self.ft.state_dict())
                else:
                    patience_counter += 1

                if patience_counter >= self.patience and best_model_state is not None:
                    self.ft.load_state_dict(best_model_state)
                    break

    def predict(self, X_test):
        # X_test: DataFrame,包含 num_cols + cat_cols

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


# 定义贝叶斯优化模型类,包含XGBoost和ResNet模型

class BayesOptModel:
    def __init__(self, train_data, test_data,
                 model_nme, resp_nme, weight_nme, factor_nmes,
                 cate_list=[], prop_test=0.25, rand_seed=None, epochs=100):
        # 初始化数据
        # train_data: 训练数据, test_data: 测试数据 格式需为DataFrame
        # model_nme: 模型名称
        # resp_nme: 因变量名称, weight_nme: 权重名称
        # factor_nmes: 因子名称列表, space_params: 参数空间
        # cate_list: 类别变量列表
        # prop_test: 测试集比例, rand_seed
        self.train_data = train_data
        self.test_data = test_data
        self.resp_nme = resp_nme
        self.weight_nme = weight_nme
        self.train_data.loc[:, 'w_act'] = self.train_data[self.resp_nme] * \
            self.train_data[self.weight_nme]
        self.test_data.loc[:, 'w_act'] = self.test_data[self.resp_nme] * \
            self.test_data[self.weight_nme]
        q99 = self.train_data[self.resp_nme].quantile(0.999)
        self.train_data[self.resp_nme] = self.train_data[self.resp_nme].clip(
            upper=q99)
        self.factor_nmes = factor_nmes
        self.cate_list = cate_list
        self.rand_seed = rand_seed if rand_seed is not None else np.random.randint(
            1, 10000)
        if self.cate_list != []:
            for cate in self.cate_list:
                self.train_data[cate] = self.train_data[cate].astype(
                    'category')
                self.test_data[cate] = self.test_data[cate].astype('category')
        self.prop_test = prop_test
        self.cv = ShuffleSplit(n_splits=int(1/self.prop_test),
                               test_size=self.prop_test,
                               random_state=self.rand_seed)
        self.model_nme = model_nme
        if self.model_nme.find('f') != -1:
            self.obj = 'count:poisson'
        elif self.model_nme.find('s') != -1:
            self.obj = 'reg:gamma'
        elif self.model_nme.find('bc') != -1:
            self.obj = 'reg:tweedie'
        self.fit_params = {
            'sample_weight': self.train_data[self.weight_nme].values
        }
        self.num_features = [
            nme for nme in self.factor_nmes if nme not in self.cate_list]
        self.train_oht_scl_data = self.train_data[self.factor_nmes +
                                                  [self.weight_nme]+[self.resp_nme]].copy()
        self.test_oht_scl_data = self.test_data[self.factor_nmes +
                                                [self.weight_nme]+[self.resp_nme]].copy()
        self.train_oht_scl_data = pd.get_dummies(
            self.train_oht_scl_data,
            columns=self.cate_list,
            drop_first=True,
            dtype=np.int8
        )
        self.test_oht_scl_data = pd.get_dummies(
            self.test_oht_scl_data,
            columns=self.cate_list,
            drop_first=True,
            dtype=np.int8
        )
        for num_chr in self.num_features:
            scaler = StandardScaler()
            self.train_oht_scl_data[num_chr] = scaler.fit_transform(
                self.train_oht_scl_data[num_chr].values.reshape(-1, 1))
            self.test_oht_scl_data[num_chr] = scaler.transform(
                self.test_oht_scl_data[num_chr].values.reshape(-1, 1))
        # 对测试集进行列对齐
        self.test_oht_scl_data = self.test_oht_scl_data.reindex(
            columns=self.train_oht_scl_data.columns,
            fill_value=0
        )
        self.var_nmes = list(
            set(list(self.train_oht_scl_data.columns)) -
            set([self.weight_nme, self.resp_nme])
        )
        self.epochs = epochs
        self.model_label = []
        self.cat_categories_for_shap = {}
        for col in self.cate_list:
            cats = self.train_data[col].astype('category')
            self.cat_categories_for_shap[col] = list(cats.cat.categories)

    # 定义单因素画图函数
    def plot_oneway(self, n_bins=10):
        for c in self.factor_nmes:
            fig = plt.figure(figsize=(7, 5))
            if c in self.cate_list:
                strs = c
            else:
                strs = c+'_bins'
                self.train_data.loc[:, strs] = pd.qcut(
                    self.train_data[c],
                    n_bins,
                    duplicates='drop'
                )
            plot_data = self.train_data.groupby(
                [strs], observed=True).sum(numeric_only=True)
            plot_data.reset_index(inplace=True)
            plot_data['act_v'] = plot_data['w_act'] / \
                plot_data[self.weight_nme]
            plot_data.head()
            ax = fig.add_subplot(111)
            ax.plot(plot_data.index, plot_data['act_v'],
                    label='Actual', color='red')
            ax.set_title(
                'Analysis of  %s : Train Data' % strs,
                fontsize=8)
            plt.xticks(plot_data.index,
                       list(plot_data[strs].astype(str)),
                       rotation=90)
            if len(list(plot_data[strs].astype(str))) > 50:
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
            save_path = os.path.join(
                os.getcwd(), 'plot',
                f'00_{self.model_nme}_{strs}_oneway.png')
            plt.savefig(save_path, dpi=300)
            plt.close(fig)

    # Xgboost交叉验证函数
    def cross_val_xgb(self, trial):
        learning_rate = trial.suggest_float(
            'learning_rate', 1e-5, 1e-1, log=True)
        gamma = trial.suggest_float(
            'gamma', 0, 10000)
        max_depth = trial.suggest_int(
            'max_depth', 3, 25)
        n_estimators = trial.suggest_int(
            'n_estimators', 10, 500, step=10)
        min_child_weight = trial.suggest_int(
            'min_child_weight', 100, 10000, step=100)
        reg_alpha = trial.suggest_float(
            'reg_alpha', 1e-10, 1, log=True)
        reg_lambda = trial.suggest_float(
            'reg_lambda', 1e-10, 1, log=True)
        if self.obj == 'reg:tweedie':
            tweedie_variance_power = trial.suggest_float(
                'tweedie_variance_power', 1, 2)
        elif self.obj == 'count:poisson':
            tweedie_variance_power = 1
        elif self.obj == 'reg:gamma':
            tweedie_variance_power = 2
        clf = xgb.XGBRegressor(
            objective=self.obj,
            random_state=self.rand_seed,
            subsample=0.9,
            tree_method='gpu_hist' if torch.cuda.is_available() else 'hist',
            gpu_id=0,
            enable_categorical=True,
            predictor='gpu_predictor' if torch.cuda.is_available() else 'cpu_predictor'
        )
        params = {
            'learning_rate': learning_rate,
            'gamma': gamma,
            'max_depth': max_depth,
            'n_estimators': n_estimators,
            'min_child_weight': min_child_weight,
            'reg_alpha': reg_alpha,
            'reg_lambda': reg_lambda
        }
        if self.obj == 'reg:tweedie':
            params['tweedie_variance_power'] = tweedie_variance_power
        clf.set_params(**params)
        acc = cross_val_score(
            clf,
            self.train_data[self.factor_nmes],
            self.train_data[self.resp_nme].values,
            fit_params=self.fit_params,
            cv=self.cv,
            scoring=make_scorer(
                mean_tweedie_deviance,
                power=tweedie_variance_power,
                greater_is_better=False),
            error_score='raise',
            n_jobs=int(1/self.prop_test)).mean()
        return -acc

    # 定义Xgboost贝叶斯优化函数
    def bayesopt_xgb(self, max_evals=100):
        study = optuna.create_study(
            direction='minimize',
            sampler=optuna.samplers.TPESampler(seed=self.rand_seed))
        study.optimize(self.cross_val_xgb, n_trials=max_evals)
        self.best_xgb_params = study.best_params
        pd.DataFrame(self.best_xgb_params, index=[0]).to_csv(
            os.getcwd() + '/Results/' + self.model_nme + '_bestparams_xgb.csv')
        self.best_xgb_trial = study.best_trial
        self.xgb_best = xgb.XGBRegressor(
            objective=self.obj,
            random_state=self.rand_seed,
            subsample=0.9,
            tree_method='gpu_hist' if torch.cuda.is_available() else 'hist',
            gpu_id=0,
            enable_categorical=True,
            predictor='gpu_predictor' if torch.cuda.is_available() else 'cpu_predictor'
        )
        self.xgb_best.set_params(**self.best_xgb_params)
        self.xgb_best.fit(self.train_data[self.factor_nmes],
                          self.train_data[self.resp_nme].values,
                          **self.fit_params)
        self.model_label += ['Xgboost']
        self.train_data['pred_xgb'] = self.xgb_best.predict(
            self.train_data[self.factor_nmes])
        self.test_data['pred_xgb'] = self.xgb_best.predict(
            self.test_data[self.factor_nmes])
        self.train_data.loc[:, 'w_pred_xgb'] = self.train_data['pred_xgb'] * \
            self.train_data[self.weight_nme]
        self.test_data.loc[:, 'w_pred_xgb'] = self.test_data['pred_xgb'] * \
            self.test_data[self.weight_nme]

    # ResNet交叉验证函数
    def cross_val_resn(self, trial):

        learning_rate = trial.suggest_float(
            'learning_rate', 1e-6, 1e-2, log=True)  # 较低learning rate为了保证不会出险梯度爆炸
        hidden_dim = trial.suggest_int(
            'hidden_dim', 32, 256, step=32)
        block_num = trial.suggest_int(
            'block_num', 2, 10)
        batch_num = trial.suggest_int(
            'batch_num',
            10 if self.obj == 'reg:gamma' else 100,
            100 if self.obj == 'reg:gamma' else 1000,
            step=10 if self.obj == 'reg:gamma' else 100)
        if self.obj == 'reg:tweedie':
            tw_power = trial.suggest_float(
                'tw_power', 1, 2.0)
        elif self.obj == 'count:poisson':
            tw_power = 1
        elif self.obj == 'reg:gamma':
            tw_power = 2
        loss = 0
        for fold, (train_idx, test_idx) in enumerate(self.cv.split(self.train_oht_scl_data[self.var_nmes])):
            # 创建模型
            cv_net = ResNetSklearn(
                model_nme=self.model_nme,
                input_dim=self.train_oht_scl_data[self.var_nmes].shape[1],
                epochs=self.epochs,
                learning_rate=learning_rate,
                hidden_dim=hidden_dim,
                block_num=block_num,
                # 保证权重方差不变
                batch_num=batch_num,
                tweedie_power=tw_power
                # 再此可以调整normlayer,dropout,residual_scale等参数
            )
            # 训练模型
            cv_net.fit(
                self.train_oht_scl_data[self.var_nmes].iloc[train_idx],
                self.train_oht_scl_data[self.resp_nme].iloc[train_idx],
                self.train_oht_scl_data[self.weight_nme].iloc[train_idx],
                self.train_oht_scl_data[self.var_nmes].iloc[test_idx],
                self.train_oht_scl_data[self.resp_nme].iloc[test_idx],
                self.train_oht_scl_data[self.weight_nme].iloc[test_idx]
            )
            # 预测
            y_pred_fold = cv_net.predict(
                self.train_oht_scl_data[self.var_nmes].iloc[test_idx]
            )
            # 计算损失
            loss += mean_tweedie_deviance(
                self.train_oht_scl_data[self.resp_nme].iloc[test_idx],
                y_pred_fold,
                sample_weight=self.train_oht_scl_data[self.weight_nme].iloc[test_idx],
                power=tw_power
            )
        return loss / int(1/self.prop_test)

    # 定义ResNet贝叶斯优化函数
    def bayesopt_resnet(self, max_evals=100):
        study = optuna.create_study(
            direction='minimize',
            sampler=optuna.samplers.TPESampler(seed=self.rand_seed))
        study.optimize(self.cross_val_resn, n_trials=max_evals)
        self.best_resn_params = study.best_params
        pd.DataFrame(self.best_resn_params, index=[0]).to_csv(
            os.getcwd() + '/Results/' + self.model_nme + '_bestparams_resn.csv')
        self.best_resn_trial = study.best_trial
        self.resn_best = ResNetSklearn(
            model_nme=self.model_nme,
            input_dim=self.train_oht_scl_data[self.var_nmes].shape[1]
        )
        self.resn_best.set_params(self.best_resn_params)
        self.resn_best.fit(self.train_oht_scl_data[self.var_nmes],
                           self.train_oht_scl_data[self.resp_nme],
                           self.train_oht_scl_data[self.weight_nme])
        self.model_label += ['ResNet']
        self.train_data['pred_resn'] = self.resn_best.predict(
            self.train_oht_scl_data[self.var_nmes])
        self.test_data['pred_resn'] = self.resn_best.predict(
            self.test_oht_scl_data[self.var_nmes])
        self.train_data.loc[:, 'w_pred_resn'] = self.train_data['pred_resn'] * \
            self.train_data[self.weight_nme]
        self.test_data.loc[:, 'w_pred_resn'] = self.test_data['pred_resn'] * \
            self.test_data[self.weight_nme]

    # FT-Transformer 交叉验证函数
    def cross_val_ft(self, trial):

        # 学习率
        learning_rate = trial.suggest_float(
            'learning_rate', 1e-6, 1e-4, log=True
        )

        # Transformer 维度与层数
        d_model = trial.suggest_int(
            'd_model', 32, 128, step=32
        )
        n_heads = trial.suggest_categorical(
            'n_heads', [2, 4, 8]
        )
        n_layers = trial.suggest_int(
            'n_layers', 2, 6
        )

        dropout = trial.suggest_float(
            'dropout', 0.0, 0.2
        )

        batch_num = trial.suggest_int(
            'batch_num',
            5 if self.obj == 'reg:gamma' else 10,
            10 if self.obj == 'reg:gamma' else 100,
            step=1 if self.obj == 'reg:gamma' else 10
        )

        # Tweedie power
        if self.obj == 'reg:tweedie':
            tw_power = trial.suggest_float('tw_power', 1.0, 2.0)
        elif self.obj == 'count:poisson':
            tw_power = 1.0
        elif self.obj == 'reg:gamma':
            tw_power = 2.0

        loss = 0.0

        # 这里注意：FT 使用的是“原始特征”（self.factor_nmes）,
        # 而不是 one-hot 之后的 self.train_oht_scl_data
        for fold, (train_idx, test_idx) in enumerate(
                self.cv.split(self.train_data[self.factor_nmes])):

            X_train_fold = self.train_data.iloc[train_idx][self.factor_nmes]
            y_train_fold = self.train_data.iloc[train_idx][self.resp_nme]
            w_train_fold = self.train_data.iloc[train_idx][self.weight_nme]

            X_val_fold = self.train_data.iloc[test_idx][self.factor_nmes]
            y_val_fold = self.train_data.iloc[test_idx][self.resp_nme]
            w_val_fold = self.train_data.iloc[test_idx][self.weight_nme]

            # 创建 FT-Transformer 模型
            cv_ft = FTTransformerSklearn(
                model_nme=self.model_nme,
                num_cols=self.num_features,   # 数值特征列表
                cat_cols=self.cate_list,      # 类别特征列表（需是编码好的整数或category）
                d_model=d_model,
                n_heads=n_heads,
                n_layers=n_layers,
                dropout=dropout,
                batch_num=batch_num,
                epochs=self.epochs,
                tweedie_power=tw_power,
                learning_rate=learning_rate,
                patience=5  # 可以根据需要调整
            )

            # 训练
            cv_ft.fit(
                X_train_fold,
                y_train_fold,
                w_train_fold,
                X_val_fold,
                y_val_fold,
                w_val_fold
            )

            # 预测
            y_pred_fold = cv_ft.predict(X_val_fold)

            # 计算损失（与 ResNet 一致：mean_tweedie_deviance）
            loss += mean_tweedie_deviance(
                y_val_fold,
                y_pred_fold,
                sample_weight=w_val_fold,
                power=tw_power
            )

        return loss / int(1 / self.prop_test)

    # 定义 FT-Transformer 贝叶斯优化函数
    def bayesopt_ft(self, max_evals=50):
        study = optuna.create_study(
            direction='minimize',
            sampler=optuna.samplers.TPESampler(seed=self.rand_seed)
        )
        study.optimize(self.cross_val_ft, n_trials=max_evals)

        self.best_ft_params = study.best_params
        pd.DataFrame(self.best_ft_params, index=[0]).to_csv(
            os.getcwd() + '/Results/' + self.model_nme + '_bestparams_ft.csv'
        )
        self.best_ft_trial = study.best_trial

        # 用最优参数重新建一个 FT 模型,在全量训练集上拟合
        self.ft_best = FTTransformerSklearn(
            model_nme=self.model_nme,
            num_cols=self.num_features,
            cat_cols=self.cate_list
        )
        # 设置最优超参
        self.ft_best.set_params(self.best_ft_params)

        # 全量训练
        self.ft_best.fit(
            self.train_data[self.factor_nmes],
            self.train_data[self.resp_nme],
            self.train_data[self.weight_nme]
        )

        # 记录模型标签
        self.model_label += ['FTTransformer']

        # 训练集预测
        self.train_data['pred_ft'] = self.ft_best.predict(
            self.train_data[self.factor_nmes]
        )
        # 测试集预测
        self.test_data['pred_ft'] = self.ft_best.predict(
            self.test_data[self.factor_nmes]
        )

        # 加权预测（和 XGB / ResNet 风格一致）
        self.train_data.loc[:, 'w_pred_ft'] = (
            self.train_data['pred_ft'] * self.train_data[self.weight_nme]
        )
        self.test_data.loc[:, 'w_pred_ft'] = (
            self.test_data['pred_ft'] * self.test_data[self.weight_nme]
        )

    # 定义分箱函数

    def _split_data(self, data, col_nme, wgt_nme, n_bins=10):
        data.sort_values(by=col_nme, ascending=True, inplace=True)
        data['cum_weight'] = data[wgt_nme].cumsum()
        w_sum = data[wgt_nme].sum()
        data.loc[:, 'bins'] = np.floor(
            data['cum_weight']*float(n_bins)/w_sum)
        data.loc[(data['bins'] == n_bins), 'bins'] = n_bins-1
        return data.groupby(['bins'], observed=True).sum(numeric_only=True)

    # 定义Lift Chart绘制数据集函数
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
        plot_data['exp_v'] = plot_data['w_pred'] / plot_data['weight']
        plot_data['act_v'] = plot_data['act'] / plot_data['weight']
        plot_data.reset_index(inplace=True)
        return plot_data

    # 定义lift曲线绘制函数
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
            save_path = os.path.join(
                os.getcwd(), 'plot', f'01_{self.model_nme}_{model_label}_lift.png')
            plt.savefig(save_path, dpi=300)
        plt.show()
        plt.close(fig)

    # 定义Double Lift Chart绘制数据集函数
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
        plot_data['exp_v1'] = plot_data['pred1'] / plot_data['act']
        plot_data['exp_v2'] = plot_data['pred2'] / plot_data['act']
        plot_data['act_v'] = plot_data['act'] / plot_data['act']
        plot_data.reset_index(inplace=True)
        return plot_data

    # 定义绘制Double Lift Chart函数
    def plot_dlift(self, model_comp=['xgb', 'resn'], n_bins=10):
        # 指标名称
        # xgb = 'Xgboost'
        # resn = 'ResNet'
        # ft = 'FTTransformer'
        figpos_list = [121, 122]
        plot_dict = {
            121: self.train_data,
            122: self.test_data
        }
        name_list = {
            121: 'Train Data',
            122: 'Test Data'
        }
        fig = plt.figure(figsize=(11, 5))
        for figpos in figpos_list:
            plot_data = self._plot_data_dlift(
                plot_dict[figpos]['w_pred_'+model_comp[0]].values,
                plot_dict[figpos]['w_pred_'+model_comp[1]].values,
                plot_dict[figpos][self.weight_nme].values,
                plot_dict[figpos]['w_act'].values,
                n_bins)
            ax = fig.add_subplot(figpos)
            tt1 = 'Xgboost'
            tt2 = 'ResNet'
            ax.plot(plot_data.index, plot_data['act_v'],
                    label='Actual', color='red')
            ax.plot(plot_data.index, plot_data['exp_v1'],
                    label=tt1, color='blue')
            ax.plot(plot_data.index, plot_data['exp_v2'],
                    label=tt2, color='black')
            ax.set_title(
                'Double Lift Chart on %s' % name_list[figpos], fontsize=8)
            plt.xticks(plot_data.index,
                       plot_data.index,
                       rotation=90, fontsize=6)
            plt.xlabel('%s / %s' % (tt1, tt2), fontsize=6)
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
                os.getcwd(), 'plot', f'02_{self.model_nme}_dlift.png')
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

        model_dir = os.path.join(os.getcwd(), 'model')
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        save_path_xgb = os.path.join(
            model_dir, f'01_{self.model_nme}_Xgboost.pkl'
        )
        save_path_resn = os.path.join(
            model_dir, f'01_{self.model_nme}_ResNet.pth'
        )
        save_path_ft = os.path.join(
            model_dir, f'01_{self.model_nme}_FTTransformer.pth'
        )

        # 保存 XGBoost
        if model_name in (None, 'xgb'):
            if hasattr(self, 'xgb_best'):
                joblib.dump(self.xgb_best, save_path_xgb)
            else:
                print("[save_model] Warning: xgb_best 不存在,未保存 Xgboost 模型。")

        # 保存 ResNet（只保存核心网络的 state_dict）
        if model_name in (None, 'resn'):
            if hasattr(self, 'resn_best'):
                torch.save(self.resn_best.resnet.state_dict(), save_path_resn)
            else:
                print("[save_model] Warning: resn_best 不存在,未保存 ResNet 模型。")

        # 保存 FT-Transformer（直接保存整个 sklearn 风格 wrapper,方便恢复结构和参数）
        if model_name in (None, 'ft'):
            if hasattr(self, 'ft_best'):
                # 这里直接保存整个对象,包含结构和参数、best 超参等
                torch.save(self.ft_best, save_path_ft)
            else:
                print("[save_model] Warning: ft_best 不存在,未保存 FT-Transformer 模型。")

    def load_model(self, model_name=None):
        # model_name 可以是:
        #   - None: 加载全部能找到的模型
        #   - 'xgb': 只加载 Xgboost
        #   - 'resn': 只加载 ResNet
        #   - 'ft': 只加载 FT-Transformer

        model_dir = os.path.join(os.getcwd(), 'model')
        save_path_xgb = os.path.join(
            model_dir, f'01_{self.model_nme}_Xgboost.pkl'
        )
        save_path_resn = os.path.join(
            model_dir, f'01_{self.model_nme}_ResNet.pth'
        )
        save_path_ft = os.path.join(
            model_dir, f'01_{self.model_nme}_FTTransformer.pth'
        )

        # 加载 XGBoost
        if model_name in (None, 'xgb'):
            if os.path.exists(save_path_xgb):
                self.xgb_load = joblib.load(save_path_xgb)
            else:
                print(
                    f"[load_model] Warning: 未找到 Xgboost 模型文件：{save_path_xgb}")

        # 加载 ResNet（重新构建 wrapper,然后加载 state_dict）
        if model_name in (None, 'resn'):
            if os.path.exists(save_path_resn):
                self.resn_load = ResNetSklearn(
                    model_nme=self.model_nme,
                    input_dim=self.train_oht_scl_data[self.var_nmes].shape[1]
                )
                state_dict = torch.load(
                    save_path_resn, map_location=self.resn_load.device)
                self.resn_load.resnet.load_state_dict(state_dict)
            else:
                print(
                    f"[load_model] Warning: 未找到 ResNet 模型文件：{save_path_resn}")

        # 加载 FT-Transformer（直接反序列化 sklearn 风格 wrapper）
        if model_name in (None, 'ft'):
            if os.path.exists(save_path_ft):
                # 统一用 CPU 先加载,再按当前环境迁移
                ft_loaded = torch.load(save_path_ft, map_location='cpu')
                # 根据当前环境设置 device,并把内部 core 模型迁到对应 device
                if torch.cuda.is_available():
                    ft_loaded.device = torch.device('cuda')
                elif torch.backends.mps.is_available():
                    ft_loaded.device = torch.device('mps')
                else:
                    ft_loaded.device = torch.device('cpu')
                ft_loaded.ft.to(ft_loaded.device)

                self.ft_load = ft_loaded
            else:
                print(
                    f"[load_model] Warning: 未找到 FT-Transformer 模型文件：{save_path_ft}")

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

    def _resn_predict_wrapper(self, X_np: np.ndarray) -> np.ndarray:
        # 用于 SHAP 的 ResNet 预测包装。
        # X_np: numpy array, shape = (N, n_features), 列顺序对应 self.var_nmes
        X_df = pd.DataFrame(X_np, columns=self.var_nmes)
        return self.resn_best.predict(X_df)

    def compute_shap_resn(self, n_background: int = 500,
                          n_samples: int = 200,
                          on_train: bool = True):

        # 使用 KernelExplainer 计算 ResNet 的 SHAP 值。
        # 解释空间：已 one-hot & 标准化后的特征 self.var_nmes。

        if not hasattr(self, 'resn_best'):
            raise RuntimeError("请先运行 bayesopt_resnet() 训练好 resn_best")

        # 选择数据集（已 one-hot & 标准化）
        data = self.train_oht_scl_data if on_train else self.test_oht_scl_data
        X = data[self.var_nmes]

        # 背景样本：float64 numpy
        background_df = X.sample(
            min(len(X), n_background),
            random_state=self.rand_seed
        )
        background_np = background_df.to_numpy(dtype=np.float64, copy=True)

        # 黑盒预测函数
        def f_predict(x):
            return self._resn_predict_wrapper(x)

        explainer = shap.KernelExplainer(f_predict, background_np)

        # 要解释的样本
        X_explain_df = X.sample(
            min(len(X), n_samples),
            random_state=self.rand_seed
        )
        X_explain_np = X_explain_df.to_numpy(dtype=np.float64, copy=True)

        shap_values = explainer.shap_values(X_explain_np, nsamples="auto")

        self.shap_resn = {
            "explainer": explainer,
            "X_explain": X_explain_df,     # DataFrame: 用于画图（有列名）
            "shap_values": shap_values,    # numpy: (n_samples, n_features)
            "base_value": explainer.expected_value,
        }
        return self.shap_resn

    # ========= FT-Transformer SHAP =========

    def _ft_shap_predict_wrapper(self, X_mat: np.ndarray) -> np.ndarray:

        # SHAP 的预测包装：
        # 数值矩阵 -> 还原为原始特征 DataFrame -> 调用 ft_best.predict

        df_input = self._decode_ft_shap_matrix_to_df(X_mat)
        y_pred = self.ft_best.predict(df_input)
        return y_pred

    def compute_shap_ft(self, n_background: int = 500,
                        n_samples: int = 200,
                        on_train: bool = True):

        # 使用 KernelExplainer 计算 FT-Transformer 的 SHAP 值。
        # 解释空间：数值+类别code 的混合数值矩阵（float64），
        # 但对外展示时仍使用原始特征名/取值（X_explain）。

        if not hasattr(self, "ft_best"):
            raise RuntimeError("请先运行 bayesopt_ft() 训练好 ft_best")

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

        shap_values = explainer.shap_values(X_explain_mat, nsamples="auto")

        self.shap_ft = {
            "explainer": explainer,
            "X_explain": X_explain_raw,   # 原始特征 DataFrame，用来画图
            "shap_values": shap_values,   # numpy: (n_samples, n_features)
            "base_value": explainer.expected_value,
        }
        return self.shap_ft
