from random import sample
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import os
import optuna

# from hyperopt import plotting, fmin, hp, tpe, Trials, STATUS_OK # 0.2.7
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import KFold, train_test_split
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_tweedie_deviance

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
            avg_loss = total_loss / total_weight
            # print(f"total weigiht: {total_weight:.4f}")
            # print(f"Epoch {epoch}/{self.epochs}, Training Loss: {avg_loss:.4f}")       
            
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
    def __init__(self, basic_data, model_nme, 
                 resp_nme, weight_nme, factor_nmes,
                 int_p_list=['hidden_dim', 'block_num', 'batch_size'],
                 cate_list=[], prop_test=0.25, rand_seed=None, epochs=100):
        # 初始化数据
        # basic基础数据 格式需为DataFrame
        # model_nme: 模型名称
        # resp_nme: 因变量名称, weight_nme: 权重名称
        # factor_nmes: 因子名称列表
        # int_p_list: 整数参数列表, cate_list: 类别变量列表
        # prop_test: 测试集比例, rand_seed
        self.basic_data = basic_data
        self.resp_nme = resp_nme
        self.weight_nme = weight_nme
        self.factor_nmes = factor_nmes
        self.cate_list = cate_list
        self.num_features = [nme for nme in self.factor_nmes if nme not in self.cate_list]
        self.basic_data.loc[:, 'w_act'] = self.basic_data[self.resp_nme] * \
            self.basic_data[self.weight_nme]
        self.proc_data = self.basic_data[self.factor_nmes +\
                                         [self.weight_nme]+[self.resp_nme]].copy()
        self.proc_data = pd.get_dummies(self.proc_data, columns=self.cate_list,
                                         drop_first=True, dtype=np.int8)
        train_data, test_data = train_test_split(
            self.proc_data, test_size=prop_test, random_state=rand_seed)
        for num_chr in self.num_features:
            scaler = StandardScaler()
            train_data[num_chr] = scaler.fit_transform(
                train_data[num_chr].values.reshape(-1, 1))
            test_data[num_chr] = scaler.transform(
                test_data[num_chr].values.reshape(-1, 1))
        self.X_train = train_data.drop([self.weight_nme, self.resp_nme],
                                       axis=1).copy()
        self.y_train = train_data[resp_nme].copy()
        self.w_train = train_data[weight_nme].copy()
        self.X_test = test_data.drop([self.weight_nme, self.resp_nme],
                                     axis=1).copy()
        self.y_test = test_data[resp_nme].copy()
        self.w_test = test_data[weight_nme].copy()
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

    def cross_val_func(self, trial):
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
        for fold, (train_idx, test_idx) in enumerate(kf.split(self.X_train)):
            # 创建模型
            cv_net = ResNetScikitLearn(
                model_nme=self.model_nme,
                input_dim= self.X_train.shape[1],
                epochs=self.epochs,
                learning_rate=learning_rate,
                hidden_dim=hidden_dim,
                block_num=block_num,
                batch_size=int(batch_size),
                tweedie_power=tw_power)
            # 训练模型
            cv_net.fit(self.X_train.iloc[train_idx], 
                       self.y_train.iloc[train_idx],
                       self.w_train.iloc[train_idx])
            # 预测
            y_pred_fold = cv_net.predict(self.X_train.iloc[test_idx])
            # 计算损失
            loss += mean_tweedie_deviance(self.y_train.iloc[test_idx],
                                          y_pred_fold,
                                          sample_weight=self.w_train.iloc[test_idx],
                                          power=tw_power) 
        return loss / fold_num

    def bayesopt(self, max_evals=100):
        study = optuna.create_study(
            direction='minimize',
            sampler=optuna.samplers.TPESampler(seed=self.rand_seed))
        study.optimize(self.cross_val_func, n_trials=max_evals)
        self.best_params = study.best_params
        self.best_trial = study.best_trial
        self.ResNet_best = ResNetScikitLearn(
            model_nme=self.model_nme,
            input_dim= self.X_train.shape[1])
        self.ResNet_best.set_params(self.best_params)
        self.ResNet_best.fit(self.X_train, self.y_train, self.w_train)