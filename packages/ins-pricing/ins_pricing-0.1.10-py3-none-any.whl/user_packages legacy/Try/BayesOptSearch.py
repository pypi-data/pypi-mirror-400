from random import sample
from turtle import st
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
import torch.utils.checkpoint as cp

from torch.utils.data import DataLoader, TensorDataset
from torch.cuda.amp import autocast, GradScaler
from torch.nn.utils import clip_grad_norm_
from sklearn.model_selection import KFold, ShuffleSplit, cross_val_score  # 1.2.2
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import make_scorer, mean_tweedie_deviance

# 定义torch下tweedie deviance损失函数
# 参考：https://scikit-learn.org/stable/modules/model_evaluation.html#mean-poisson-gamma-and-tweedie-deviances


def tweedie_loss(pred, target, p=1.5):
    # Ensure predictions are positive for stability
    eps = 1e-6
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
    return 2 * (term1 - term2 + term3)

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

# 残差块：两层线性 + ReLU + 残差连接
# ResBlock 继承 nn.Module


class ResBlock(nn.Module):
    def __init__(self, dim):
        super(ResBlock, self).__init__()
        self.block = nn.Sequential(
            nn.Linear(dim, dim),
            nn.BatchNorm1d(dim),
            nn.ReLU(),
            nn.Linear(dim, dim),
            nn.BatchNorm1d(dim)
        )

    def forward(self, x):
        # 原始输入 + 两层变换，然后再过 ReLU
        # 用 checkpoint来节省内存
        # out = cp.checkpoint(self.block, x)
        return F.relu(self.block(x) + x)
        # return F.relu(out + x)

# ResNetSequential 继承 nn.Module，定义整个网络结构


class ResNetSequential(nn.Module):
    # 整个网络用 nn.Sequential 串联：输入 -> ResBlock*block_num -> 输出
    def __init__(self, input_dim, hidden_dim=64, block_num=2):
        super(ResNetSequential, self).__init__()
        self.net = nn.Sequential()
        self.net.add_module('fc1', nn.Linear(input_dim, hidden_dim))
        self.net.add_module('bn1', nn.BatchNorm1d(hidden_dim))
        self.net.add_module('ReLU1', nn.ReLU())
        for i in range(block_num):
            self.net.add_module('ResBlk_'+str(i+1), ResBlock(hidden_dim))
        self.net.add_module('fc2', nn.Linear(hidden_dim, 1))
        self.net.add_module('softplus', nn.Softplus())

    def forward(self, x):
        return self.net(x)

# 贝叶斯优化类，使用高斯过程进行超参数优化


class ResNetScikitLearn(nn.Module):
    def __init__(self, model_nme, input_dim, hidden_dim=64,
                 block_num=2, batch_num=100, epochs=100,
                 tweedie_power=1.5, learning_rate=0.01,
                 patience=10, accumulation_steps=2):
        super(ResNetScikitLearn, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.block_num = block_num
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            self.device = torch.device('mps')
        else:
            self.device = torch.device('cpu')
        self.resnet = ResNetSequential(
            self.input_dim,
            self.hidden_dim,
            self.block_num
        ).to(self.device)
        if torch.cuda.device_count() > 1:
            self.resnet = nn.DataParallel(
                self.resnet,
                device_ids=list(range(torch.cuda.device_count()))
            )
        self.batch_num = batch_num
        self.epochs = epochs
        self.model_nme = model_nme
        if self.model_nme.find('f') != -1:
            self.tw_power = 1
        elif self.model_nme.find('s') != -1:
            self.tw_power = 2
        else:
            self.tw_power = tweedie_power
        self.learning_rate = learning_rate
        self.patience = patience  # Early stopping patience
        self.accumulation_steps = accumulation_steps  # Gradient accumulation steps

    def fit(self, X_train, y_train, w_train=None, X_val=None, y_val=None, w_val=None):
        # 将数据转换为 PyTorch 张量
        X_tensor = torch.tensor(
            X_train.values, dtype=torch.float32).to(self.device)
        y_tensor = torch.tensor(
            y_train.values, dtype=torch.float32).view(-1, 1).to(self.device)
        w_tensor = torch.tensor(
            w_train.values, dtype=torch.float32).view(-1, 1).to(self.device) if w_train is not None else torch.ones_like(y_tensor)

        # 验证集张量
        if X_val is not None:
            X_val_tensor = torch.tensor(
                X_val.values, dtype=torch.float32).to(self.device)
            y_val_tensor = torch.tensor(
                y_val.values, dtype=torch.float32).view(-1, 1).to(self.device)
            w_val_tensor = torch.tensor(
                w_val.values, dtype=torch.float32).view(-1, 1).to(self.device) if w_val is not None else torch.ones_like(y_val_tensor)

        # 创建数据集和数据加载器
        dataset = TensorDataset(
            X_tensor, y_tensor, w_tensor
        )
        dataloader = DataLoader(
            dataset,
            batch_size=max(1, int((self.learning_rate/(1e-4))**0.5 *
                                  (X_train.shape[0]/self.batch_num))),
            shuffle=True
            # num_workers=4
            # pin_memory=(self.device.type == 'cuda')
        )
        # 定义损失函数和优化器
        optimizer = torch.optim.Adam(
            self.resnet.parameters(), lr=self.learning_rate)
        scaler = GradScaler(enabled=(self.device.type == 'cuda'))

        # Early stopping 参数
        best_loss, patience_counter = float('inf'), 0
        best_model_state = None  # Initialize best_model_state

        # 训练模型
        for epoch in range(1, self.epochs + 1):
            self.resnet.train()
            for X_batch, y_batch, w_batch in dataloader:
                optimizer.zero_grad()
                # 如果运行设备为 CUDA，则启用混合精度。
                with autocast(enabled=(self.device.type == 'cuda')):
                    X_batch, y_batch, w_batch = X_batch.to(self.device), y_batch.to(
                        self.device), w_batch.to(self.device)
                    y_pred = self.resnet(X_batch)
                    y_pred = torch.clamp(y_pred, min=1e-6)
                    losses = tweedie_loss(
                        y_pred, y_batch, p=self.tw_power).view(-1)
                    weighted_loss = (losses * w_batch.view(-1)
                                     ).sum() / w_batch.sum()
                scaler.scale(weighted_loss).backward()
                # gradient clipping
                # 如进行gradient clipping,需要在反向传播之前取消缩放
                if self.device.type == 'cuda':
                    scaler.unscale_(optimizer)
                    clip_grad_norm_(
                        self.resnet.parameters(),
                        max_norm=1.0
                    )
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad()

        # 验证集损失计算
            if X_val is not None and y_val is not None:
                self.resnet.eval()
                with torch.no_grad(), autocast(enabled=(self.device.type == 'cuda')):
                    y_val_pred = self.resnet(X_val_tensor)
                    val_loss_values = tweedie_loss(
                        y_val_pred, y_val_tensor, p=self.tw_power).view(-1)
                    val_weighted_loss = (
                        val_loss_values * w_val_tensor.view(-1)).sum() / w_val_tensor.sum()

                # Early stopping 检查
                if val_weighted_loss < best_loss:
                    best_loss, patience_counter = val_weighted_loss, 0
                    # 保存当前最佳模型
                    best_model_state = self.resnet.state_dict()
                else:
                    patience_counter += 1
                if patience_counter >= self.patience:
                    self.resnet.load_state_dict(best_model_state)  # 恢复最佳模型
                    break

    def predict(self, X_test):
        self.resnet.eval()
        with torch.no_grad():
            X_tensor = torch.tensor(
                X_test.values, dtype=torch.float32).to(self.device)
            y_pred = self.resnet(X_tensor).cpu().numpy()
        y_pred = np.clip(y_pred, 1e-6, None)
        return y_pred.flatten()

    def set_params(self, params):
        # 设置模型参数
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Parameter {key} not found in model.")

# 定义贝叶斯优化模型类，包含XGBoost和ResNet模型


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
            tree_method='gpu_hist',
            gpu_id=0,
            enable_categorical=True,
            predictor='gpu_predictor'
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
            predictor='gpu_predictor'
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
            'learning_rate', 1e-6, 1e-2, log=True)
        hidden_dim = trial.suggest_int(
            'hidden_dim', 32, 256, step=16)
        block_num = trial.suggest_int(
            'block_num', 3, 10)
        batch_num = trial.suggest_int(
            'batch_num',
            10 if self.obj == 'reg:gamma' else 100,
            100 if self.obj == 'reg:gamma' else 1000,
            step=10)
        if self.obj == 'reg:tweedie':
            tw_power = trial.suggest_float(
                'tw_power', 1, 2)
        elif self.obj == 'count:poisson':
            tw_power = 1
        elif self.obj == 'reg:gamma':
            tw_power = 2
        loss = 0
        for fold, (train_idx, test_idx) in enumerate(self.cv.split(self.train_oht_scl_data[self.var_nmes])):
            # 创建模型
            cv_net = ResNetScikitLearn(
                model_nme=self.model_nme,
                input_dim=self.train_oht_scl_data[self.var_nmes].shape[1],
                epochs=self.epochs,
                learning_rate=learning_rate,
                hidden_dim=hidden_dim,
                block_num=block_num,
                # 保证权重方差不变
                batch_num=batch_num,
                tweedie_power=tw_power if self.obj == 'reg:tweedie' and tw_power != 1 else tw_power+1e-6
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
        self.resn_best = ResNetScikitLearn(
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
    def plot_lift(self, model_label, n_bins=10):
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
        fig = plt.figure(figsize=(11, 5))
        if model_label == 'Xgboost':
            pred_nme = 'pred_xgb'
        elif model_label == 'ResNet':
            pred_nme = 'pred_resn'

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
    def plot_dlift(self, n_bins=10):
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
        fig = plt.figure(figsize=(11, 5))
        for figpos in figpos_list:
            plot_data = self._plot_data_dlift(
                plot_dict[figpos]['w_pred_xgb'].values,
                plot_dict[figpos]['w_pred_resn'].values,
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
        # model_name 可以是 'xgb', 'resn' 或 None
        save_path_xgb = os.path.join(
            os.getcwd(), 'model', f'01_{self.model_nme}_Xgboost.pkl')
        save_path_resn = os.path.join(
            os.getcwd(), 'model', f'01_{self.model_nme}_ResNet.pth')
        if not os.path.exists(os.path.dirname(save_path_xgb)):
            os.makedirs(os.path.dirname(save_path_xgb))
        # self.xgb_best.save_model(save_path_xgb)
        if model_name != 'resn':
            joblib.dump(self.xgb_best, save_path_xgb)
        if model_name != 'xgb':
            torch.save(self.resn_best.resnet.state_dict(), save_path_resn)

    def load_model(self, model_name=None):
        # model_name 可以是 'xgb', 'resn' 或 None
        save_path_xgb = os.path.join(
            os.getcwd(), 'model', f'01_{self.model_nme}_Xgboost.pkl')
        save_path_resn = os.path.join(
            os.getcwd(), 'model', f'01_{self.model_nme}_ResNet.pth')
        if model_name != 'resn':
            self.xgb_load = joblib.load(save_path_xgb)
        if model_name != 'xgb':
            self.resn_load = ResNetScikitLearn(
                model_nme=self.model_nme,
                input_dim=self.train_oht_scl_data[self.var_nmes].shape[1]
            )
            self.resn_load.resnet.load_state_dict(
                torch.load(save_path_resn, map_location=self.resn_load.device))
