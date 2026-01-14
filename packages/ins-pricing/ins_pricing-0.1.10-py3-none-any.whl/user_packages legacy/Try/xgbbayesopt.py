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
        self.clf_init = xgb.XGBRegressor(objective=self.obj,
                                         random_state=self.rand_seed,
                                         subsample=0.9,
                                         tree_method='gpu_hist',
                                         gpu_id=0,
                                         enable_categorical=True,
                                         predictor='gpu_predictor')
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
        self.clf_init.fit(self.train_data[self.factor_nmes], 
                          self.train_data[self.resp_nme],
                          **self.fit_params)
        self.train_data.loc[:, 'pred'] = self.clf.predict(
            self.train_data[self.factor_nmes])
        self.test_data.loc[:, 'pred'] = self.clf.predict(
            self.test_data[self.factor_nmes])
        self.train_data.loc[:, 'pred_init'] = self.clf_init.predict(
            self.train_data[self.factor_nmes])
        self.test_data.loc[:, 'pred_init'] = self.clf_init.predict(
            self.test_data[self.factor_nmes])
        self.train_data.loc[:, 'w_pred'] = self.train_data['pred'] * \
            self.train_data[self.weight_nme]
        self.test_data.loc[:, 'w_pred'] = self.test_data['pred'] * \
            self.test_data[self.weight_nme]
        self.train_data.loc[:, 'w_pred_init'] = self.clf_init.predict(
            self.train_data[self.factor_nmes]) * self.train_data[self.weight_nme]
        self.test_data.loc[:, 'w_pred_init'] = self.clf_init.predict(
            self.test_data[self.factor_nmes]) * self.test_data[self.weight_nme]

    # 定义输出模型函数
    def output_model(self, model_nme='Optimization'):
        ''' 模型可在Optimization和Initial两种模式下保存 '''
        if model_nme == 'Optimization':
            joblib.dump(self.clf, os.getcwd() + '/Results/' +
                        self.model_nme + '_xgb.pkl')
        elif model_nme == 'Initial':
            joblib.dump(self.clf_init, os.getcwd() +
                        '/Results/' + self.model_nme + '_xgb.pkl')

    def pred(self, data, model_nme='Optimization'):
        # 模型可在Optimization和Initial两种模式下预测
        if model_nme == 'Optimization':
            return self.clf.predict(data[self.factor_nmes])
        elif model_nme == 'Initial':
            return self.clf_init.predict(data[self.factor_nmes])

    # 定义绘制单因素结果
    def plot_oneway(self, n_bins=10):
        for c in self.factor_nmes:
            fig = plt.figure(figsize=(7, 5))
            if c in self.cate_list:
                strs = c
            else:
                strs = c+'_bins'
                self.train_data.loc[:, strs] = pd.qcut(self.train_data[c], n_bins,
                                                       duplicates='drop')
            plot_data = self.train_data.groupby([strs], observed=True).sum(numeric_only=True)
            plot_data.reset_index(inplace=True)
            plot_data['act_v'] = plot_data['w_act'] / plot_data[self.weight_nme]
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
    def plot_lift(self, n_bins=10):
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
            plot_data = self._plot_data_lift(
                plot_dict[figpos]['pred'].values,
                plot_dict[figpos]['w_pred'].values,
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
                os.getcwd(), 'plot', f'01_{self.model_nme}_lift.png')
            plt.savefig(save_path, dpi=300)
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
                plot_dict[figpos]['w_pred'].values,
                plot_dict[figpos]['w_pred_init'].values,
                plot_dict[figpos][self.weight_nme].values,
                plot_dict[figpos]['w_act'].values,
                n_bins)
            ax = fig.add_subplot(figpos)
            tt1 = 'Modified Model'
            tt2 = 'Initial Model'
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
        plt.close(fig)

    # 绘制单因素实际与预测值对比图
    def plot_sim(self, n_bins=10):
        figpos_list = [121, 122]
        plot_dict = {
            121: self.train_data,
            122: self.test_data
        }
        name_list = {
            121: 'Train Data',
            122: 'Test Data'
        }
        for c in self.factor_nmes:
            fig = plt.figure(figsize=(11, 5))
            for figpos in figpos_list:
                plot_data = plot_dict[figpos]
                if c in self.cate_list:
                    strs = c
                else:
                    strs = c+'_bins'
                    plot_data.loc[:, strs] = pd.qcut(
                        plot_data[c], n_bins,
                        duplicates='drop')
                plot_data = plot_data.groupby(
                    [strs], observed=True).sum(numeric_only=True)
                plot_data.reset_index(inplace=True)
                plot_data['exp_v'] = plot_data['w_pred'] / \
                    plot_data[self.weight_nme]
                plot_data['act_v'] = plot_data['w_act'] / \
                    plot_data[self.weight_nme]
                ax = fig.add_subplot(figpos)
                ax.plot(plot_data.index, plot_data['act_v'],
                        label='Actual', color='red')
                ax.plot(plot_data.index, plot_data['exp_v'],
                        label='Predicted', color='blue')
                ax.set_title(
                    'Analysis of  %s : %s' % (strs, name_list[figpos]), 
                    fontsize=8)
                plt.xticks(plot_data.index,
                           list(plot_data[strs].astype(str)),
                           rotation=90, fontsize=4)
                plt.legend(loc='upper left', 
                           fontsize=5, frameon=False)
                plt.margins(0.05)
                plt.yticks(fontsize=6)
                ax2 = ax.twinx()
                ax2.bar(plot_data.index, plot_data[self.weight_nme],
                        alpha=0.5, color='seagreen', 
                        label='Earned Exposure')
                plt.legend(loc='upper right', 
                           fontsize=5, frameon=False)
                plt.yticks(fontsize=6)
                plt.subplots_adjust(wspace=0.3)
                save_path = os.path.join(
                    os.getcwd(), 'plot', f'03_{self.model_nme}_{strs}_sim.png')
                plt.savefig(save_path, dpi=300)
            plt.close(fig)

    # 绘制SHAP值图

    def plot_shap(self, n_bins=10):
        figpos_list = [121, 122]
        plot_dict = {
            121: self.train_data,
            122: self.test_data
        }
        name_list = {
            121: 'Train Data',
            122: 'Test Data'
        }
        for figpos in figpos_list:
            plot_data = plot_dict[figpos]
            explainer = shap.TreeExplainer(self.clf)
            shap_values = explainer.shap_values(plot_data[self.factor_nmes])
            shap.summary_plot(shap_values, plot_data[self.factor_nmes],
                              plot_type='bar', max_display=10)
            plt.title('SHAP Summary Plot on %s' % name_list[figpos])
            save_path = os.path.join(
                os.getcwd(), 'plot', f'04_{self.model_nme}_shap.png')
            plt.savefig(save_path, dpi=300)
            plt.close()


# 定义外部函数
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