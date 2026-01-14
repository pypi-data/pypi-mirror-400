from sklearn.model_selection import ShuffleSplit, cross_val_score # 1.2.2
from hyperopt import plotting, fmin, hp, tpe, Trials, STATUS_OK # 0.2.7
from sklearn.metrics import make_scorer, mean_tweedie_deviance # 1.2.2 

import shap # 0.44.1
import xgboost as xgb # 1.7.0
import joblib
import matplotlib.pyplot as plt
import numpy as np # 1.26.2
import pandas as pd # 2.2.3
import os
import re

class xgb_bayesopt:
    def __init__(self, train_data, test_data, 
                 model_nme, resp_nme, weight_nme,
                 factor_nmes, space_params,
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
        self.train_data.loc[:, 'w_act'] = self.train_data[self.resp_nme] * \
            self.train_data[self.weight_nme]
        self.test_data.loc[:, 'w_act'] = self.test_data[self.resp_nme] * \
            self.test_data[self.weight_nme]
        self.cate_list = cate_list
        self.space_params = space_params
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

        if self.obj != 'reg:tweedie':
            del self.space_params['tweedie_variance_power']
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
    def cross_val_xgb(self, params):
        # 将部分float参数调整为整数型
        for param_name in self.int_p_list:  # ,  'max_leaves'
            params[param_name] = int(params[param_name])
        self.clf.set_params(**params)
        if self.obj == 'reg:tweedie':
            tw_power = params['tweedie_variance_power']
        elif self.obj == 'count:poisson':
            tw_power = 1
        elif self.obj == 'reg:gamma':
            tw_power = 2
        acc = cross_val_score(self.clf, 
                              self.train_data[self.factor_nmes], 
                              self.train_data[self.resp_nme].values,
                              fit_params=self.fit_params,
                              cv=self.cv,
                              # scoring='neg_root_mean_squared_error',
                              scoring=make_scorer(mean_tweedie_deviance,
                                                  power=tw_power,
                                                  greater_is_better=False),
                              error_score='raise',
                              n_jobs=int(1/self.prop_test)).mean()
        return {'loss': -acc, 'params': params, 'status': STATUS_OK}

    # 定义贝叶斯优化函数
    def bayesopt(self, max_evals=100):
        self.trials = Trials()
        self.best = fmin(self.cross_val_xgb, self.space_params,
                         algo=tpe.suggest, 
                         max_evals=max_evals, trials=self.trials)
        for param_name in self.int_p_list:  # , 'max_leaves'
            self.best[param_name] = int(self.best[param_name])
        pd.DataFrame(self.best, index=[0]).to_csv(
            os.getcwd() + '/Results/' + self.model_nme + '_bestparams_xgb.csv')
        self.clf.set_params(**self.best)
        self.clf.fit(self.train_data[self.factor_nmes], 
                     self.train_data[self.resp_nme], 
                     **self.fit_params)

    # 定义输出模型函数
    def output_model(self):
        ''' 模型可在Optimization和Initial两种模式下保存 '''
        joblib.dump(self.clf, os.getcwd() + '/Results/' +
                    self.model_nme + '_xgb.pkl')

    def pred(self, data):
        # 模型可在Optimization和Initial两种模式下预测
        return self.clf.predict(data[self.factor_nmes])

  