from random import sample
import numpy as np # 1.26.2
import pandas as pd # 2.2.3
import torch
import torch.nn as nn
import torch.nn.functional as F
import os
import re
import optuna
import xgboost as xgb # 1.7.0
import joblib

from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import KFold, train_test_split, ShuffleSplit, cross_val_score # 1.2.2
from torch.utils.data import DataLoader, TensorDataset
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
        term2 = -target / pred_clamped +1
        term3 = 0
    else:
        term1 = torch.pow(target, 2 - p) / ((1 - p) * (2 - p))
        term2 = target * torch.pow(pred_clamped, 1 - p) / (1 - p)
        term3 = torch.pow(pred_clamped, 2 - p) / (2 - p)
    # Tweedie negative log-likelihood (up to a constant)
    return 2 * (term1 - term2 + term3)

class xgb_bayesopt:
    def __init__(self, train_data, test_data, 
                 model_nme, resp_nme, weight_nme, factor_nmes,
                 int_p_list=['n_estimators', 'max_depth'],
                 cate_list=[], prop_test=0.25, rand_seed=None):
        # 初始化数据
        # train_data: 训练数据, test_data: 测试数据 格式需为DataFrame
        # model_nme: 模型名称
        # resp_nme: 因变量名称, weight_nme: 权重名称
        # factor_nmes: 因子名称列表, space_params: 参数空间
        # int_p_list: 整数参数列表, cate_list: 类别变量列表
        # prop_test: 测试集比例, rand_seed

        self.train_data = train_data
        self.test_data = test_data
        self.resp_nme = resp_nme
        self.weight_nme = weight_nme
        self.factor_nmes = factor_nmes
        self.cate_list = cate_list
        self.rand_seed = rand_seed if rand_seed is not None else np.random.randint(
            1, 10000)
        if self.cate_list != []:
            for cate in self.cate_list:
                self.train_data[cate] = self.train_data[cate].astype('category')
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

        self.int_p_list = int_p_list
        self.clf = xgb.XGBRegressor(objective=self.obj,
                                    random_state=self.rand_seed,
                                    subsample=0.9,
                                    tree_method='gpu_hist',
                                    gpu_id=0,
                                    enable_categorical=True,
                                    predictor='gpu_predictor')
        self.fit_params = {
            'sample_weight': self.train_data[self.weight_nme].values
        }

    # 定义交叉验证函数
    def cross_val_xgb(self, trial):
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-1, log=True)
        gamma = trial.suggest_float('gamma', 0, 10000)
        max_depth = trial.suggest_int('max_depth', 3, 25)
        n_estimators = trial.suggest_int('n_estimators', 10, 500, step=10)
        min_child_weight = trial.suggest_float('min_child_weight', 1, 10000)
        reg_alpha = trial.suggest_float('reg_alpha', 1e-10, 1, log=True)
        reg_lambda = trial.suggest_float('reg_lambda', 1e-10, 1, log=True)
        if self.obj == 'reg:tweedie':
            tweedie_variance_power = trial.suggest_float('tweedie_variance_power', 1, 2)
        elif self.obj == 'count:poisson':
            tweedie_variance_power = 1
        elif self.obj == 'reg:gamma':
            tweedie_variance_power = 2
        params = {
            'learning_rate': learning_rate,
            'gamma': gamma,
            'max_depth': int(max_depth),
            'n_estimators': int(n_estimators),
            'min_child_weight': min_child_weight,
            'reg_alpha': reg_alpha,
            'reg_lambda': reg_lambda,
            'tweedie_variance_power': tweedie_variance_power
        }
        if self.obj != 'reg:tweedie':
            del params['tweedie_variance_power']
        self.clf.set_params(**params)
        acc = cross_val_score(self.clf,
                              self.train_data[self.factor_nmes], 
                              self.train_data[self.resp_nme].values,
                              fit_params=self.fit_params,
                              cv=self.cv,
                              scoring=make_scorer(mean_tweedie_deviance,
                                                  power=tweedie_variance_power,
                                                  greater_is_better=False),
                              error_score='raise',
                              n_jobs=int(1/self.prop_test)).mean()
        return -acc

    # 定义贝叶斯优化函数
    def bayesopt(self, max_evals=100):
        study = optuna.create_study(
            direction='minimize',
            sampler=optuna.samplers.TPESampler(seed=self.rand_seed))
        study.optimize(self.cross_val_xgb, n_trials=max_evals)
        self.best_params = study.best_params
        self.best_trial = study.best_trial
        self.clf.set_params(**self.best_params)
        self.clf.fit(self.train_data[self.factor_nmes],
                     self.train_data[self.resp_nme].values,
                     **self.fit_params))
        self.train_data['pred'] = self.clf.predict(
            self.train_data[self.factor_nmes])
        self.test_data['pred'] = self.clf.predict(
            self.test_data[self.factor_nmes])
        
# 定义ResNet模型        
        
class ResBlock(nn.Module):
    """一个简单的残差块：两层线性 + ReLU, 带跳跃连接"""
    def __init__(self, dim):
        super().__init__()
        self.block = nn.Sequential(
            nn.Linear(dim, dim),
            nn.ReLU(),
            nn.Linear(dim, dim)
        )
    
    def forward(self, x):
        # 原始输入 + 两层变换，然后再过 ReLU
        return F.relu(self.block(x) + x)
    
class ResNetSequential(nn.Module):
    """整个网络用 nn.Sequential 串联：输入 -> ResBlock*block_num -> 输出"""
    def __init__(self, input_dim, hidden_dim=64, block_num=2):
        super().__init__()
        self.net = nn.Sequential()
        self.net.add_module('fc1', nn.Linear(input_dim, hidden_dim)),
        self.net.add_module('ReLU1', nn.ReLU())
        for i in range(block_num):
            self.net.add_module('ResBlk_'+str(i+1), ResBlock(hidden_dim))  
        self.net.add_module('fc2', nn.Linear(hidden_dim, 1))
        self.net.add_module('softplus', nn.Softplus())
    
    def forward(self, x):
        return self.net(x)
    
class ResNetScikitLearn:
    """贝叶斯优化类，使用高斯过程进行超参数优化"""
    def __init__(self, model_nme, input_dim, hidden_dim=64, 
                 block_num=2, batch_size=32, epochs=100,
                 tweedie_power=1.5,learning_rate=0.01):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.block_num = block_num
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.resnet = ResNetSequential(
            self.input_dim, 
            self.hidden_dim, 
            self.block_num
            ).to(self.device)
        self.batch_size = batch_size
        self.epochs = epochs
        self.model_nme = model_nme
        if self.model_nme.find('f') != -1:
            self.tw_power = 1
        elif self.model_nme.find('s') != -1:
            self.tw_power = 2
        else:
            self.tw_power = tweedie_power 
        self.learning_rate = learning_rate     
        
    def fit(self, X_train, y_train, w_train=None):
        # 将数据转换为 PyTorch 张量
        X_tensor = torch.tensor(X_train.values, dtype=torch.float32).to(self.device)
        y_tensor = torch.tensor(y_train.values, dtype=torch.float32).view(-1, 1).to(self.device)
        w_tensor = torch.tensor(w_train.values, dtype=torch.float32).view(-1, 1).to(self.device) if w_train is not None else None
        # 创建数据集和数据加载器
        dataset = TensorDataset(X_tensor, y_tensor, w_tensor) if w_train is not None else TensorDataset(X_tensor, y_tensor)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        
        # 定义损失函数和优化器
        optimizer = torch.optim.Adam(self.resnet.parameters(), lr=self.learning_rate)
        
        # 训练模型
        for epoch in range(1, self.epochs + 1):
            self.resnet.train()
            total_loss = 0.0
            total_weight = 0.0
            for X_batch, y_batch, w_batch in dataloader:
                X_batch = X_batch.to(self.device)
                y_batch = y_batch.to(self.device)
                w_batch = w_batch.to(self.device)
                optimizer.zero_grad()
                y_pred = self.resnet(X_batch)
                loss_values = tweedie_loss(y_pred, y_batch, p=self.tw_power).view(-1)
                weighted_loss = (loss_values * w_batch.view(-1)).sum() / w_batch.sum()
                weighted_loss.backward()
                optimizer.step()
                total_loss += weighted_loss.item() * w_batch.sum().item()
                total_weight += w_batch.sum().item()  
            
    def predict(self, X_test):
        self.resnet.eval()
        with torch.no_grad():
            X_tensor = torch.tensor(X_test.values, dtype=torch.float32).to(self.device)
            y_pred = self.resnet(X_tensor).cpu().numpy()
        return y_pred.flatten()
    
    def set_params(self, params):
        # 设置模型参数
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Parameter {key} not found in model.")
            
class ResNetBayesOpt:
    def __init__(self, train_data, test_data, 
                 model_nme, resp_nme, weight_nme, factor_nmes,
                 int_p_list=['hidden_dim', 'block_num', 'batch_size'],
                 cate_list=[], prop_test=0.25, rand_seed=None, epochs=100):
        # 初始化数据
        # basic基础数据 格式需为DataFrame
        # model_nme: 模型名称
        # resp_nme: 因变量名称, weight_nme: 权重名称
        # factor_nmes: 因子名称列表
        # int_p_list: 整数参数列表, cate_list: 类别变量列表
        # prop_test: 测试集比例, rand_seed
        self.train_data = train_data
        self.test_data = test_data
        self.resp_nme = resp_nme
        self.weight_nme = weight_nme
        self.factor_nmes = factor_nmes
        self.cate_list = cate_list
        self.num_features = [nme for nme in self.factor_nmes if nme not in self.cate_list]
        self.train_oht_scl_data = self.train_data[self.factor_nmes +\
            [self.weight_nme]+[self.resp_nme]].copy()
        self.test_oht_scl_data = self.test_data[self.factor_nmes +\
            [self.weight_nme]+[self.resp_nme]].copy()
        self.train_oht_scl_data = pd.get_dummies(self.train_oht_scl_data, columns=self.cate_list,
                                                 drop_first=True, dtype=np.int8)
        self.test_oht_scl_data = pd.get_dummies(self.test_oht_scl_data, columns=self.cate_list,
                                                drop_first=True, dtype=np.int8)                                  
        for num_chr in self.num_features:
            scaler = StandardScaler()
            self.train_oht_scl_data[num_chr] = scaler.fit_transform(
                self.train_oht_scl_data[num_chr].values.reshape(-1, 1))
            self.test_oht_scl_data[num_chr] = scaler.transform(
                self.test_oht_scl_data[num_chr].values.reshape(-1, 1))
            
        self.var_nmes = [nme for nme in self.train_oht_scl_data.columns if nme not in [self.resp_nme, self.weight_nme]]
        self.rand_seed = rand_seed if rand_seed is not None else np.random.randint(
            1, 10000)
        self.prop_test = prop_test
        self.model_nme = model_nme
        if self.model_nme.find('f') != -1:
            self.obj = 'count:poisson'
        elif self.model_nme.find('s') != -1:
            self.obj = 'reg:gamma'
        elif self.model_nme.find('bc') != -1:
            self.obj = 'reg:tweedie'
        self.int_p_list = int_p_list
        self.epochs = epochs

    def cross_val_resn(self, trial):
        # 交叉验证函数
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-1, log=True)
        hidden_dim = trial.suggest_int('hidden_dim', 8, 128)
        block_num = trial.suggest_int('block_num', 2, 10)
        batch_size = trial.suggest_float('batch_size', 200, 10000, step=200)
        if self.obj == 'reg:tweedie':
            tw_power = trial.suggest_uniform('tw_power', 0, 2.0)
        elif self.obj == 'count:poisson':
            tw_power = 1
        elif self.obj == 'reg:gamma':
            tw_power = 2
        fold_num = int(1/self.prop_test)
        kf = KFold(n_splits=fold_num, shuffle=True, random_state=self.rand_seed)
        loss = 0
        for fold, (train_idx, test_idx) in enumerate(kf.split(self.train_oht_scl_data[self.var_nmes])):
            # 创建模型
            cv_net = ResNetScikitLearn(
                model_nme=self.model_nme,
                input_dim= self.train_oht_scl_data[self.var_nmes].shape[1],
                epochs=self.epochs,
                learning_rate=learning_rate,
                hidden_dim=hidden_dim,
                block_num=block_num,
                batch_size=int(batch_size),
                tweedie_power=tw_power)
            # 训练模型
            cv_net.fit(self.train_oht_scl_data[self.var_nmes].iloc[train_idx], 
                       self.train_oht_scl_data[self.resp_nme].iloc[train_idx],
                       self.train_oht_scl_data[self.weight_nme].iloc[train_idx])
            # 预测
            y_pred_fold = cv_net.predict(self.train_oht_scl_data[self.var_nmes].iloc[test_idx])
            # 计算损失
            loss += mean_tweedie_deviance(self.train_oht_scl_data[self.resp_nme].iloc[test_idx],
                                          y_pred_fold,
                                          sample_weight=self.train_oht_scl_data[self.weight_nme].iloc[test_idx],
                                          power=tw_power) 
        return loss / fold_num

    def bayesopt(self, max_evals=100):
        study = optuna.create_study(
            direction='minimize',
            sampler=optuna.samplers.TPESampler(seed=self.rand_seed))
        study.optimize(self.cross_val_resn, n_trials=max_evals)
        self.best_params = study.best_params
        self.best_trial = study.best_trial
        self.clf = ResNetScikitLearn(
            model_nme=self.model_nme,
            input_dim=self.train_oht_scl_data[self.var_nmes].shape[1])
        self.clf.set_params(self.best_params)
        self.clf.fit(self.train_oht_scl_data[self.var_nmes],
                     self.train_oht_scl_data[self.resp_nme],
                     self.train_oht_scl_data[self.weight_nme])
        self.train_data['pred'] = self.clf.predict(
            self.train_oht_scl_data[self.var_nmes])
        self.test_data['pred'] = self.clf.predict(
            self.test_oht_scl_data[self.var_nmes])