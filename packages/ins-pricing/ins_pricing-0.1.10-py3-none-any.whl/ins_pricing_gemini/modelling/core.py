from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import os
from typing import Any, Dict, List, Optional

try:  # matplotlib is optional; avoid hard import failures in headless/minimal envs
    import matplotlib
    if os.name != "nt" and not os.environ.get("DISPLAY") and not os.environ.get("MPLBACKEND"):
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _MPL_IMPORT_ERROR: Optional[BaseException] = None
except Exception as exc:  # pragma: no cover - optional dependency
    plt = None  # type: ignore[assignment]
    _MPL_IMPORT_ERROR = exc
import numpy as np
import pandas as pd
import torch
import statsmodels.api as sm
from sklearn.model_selection import ShuffleSplit
from sklearn.preprocessing import StandardScaler

from .config import BayesOptConfig
from .config_preprocess import DatasetPreprocessor, OutputManager, VersionManager
from .data_container import DataContainer
from .model_manager import ModelManager
from .models import GraphNeuralNetSklearn
from .trainers import FTTrainer, GLMTrainer, GNNTrainer, ResNetTrainer, XGBTrainer
from .utils import EPS, PlotUtils, infer_factor_and_cate_list, set_global_seed

# Feature and Plotting modules
from .features import _add_region_effect, _prepare_geo_tokens, _build_geo_tokens
from .model_plotting import (
    plot_oneway, 
    plot_lift, 
    plot_dlift, 
    plot_conversion_lift, 
    _plot_skip
)

try:
    from .plotting import curves as plot_curves
    from .plotting import diagnostics as plot_diagnostics
    from .plotting.common import PlotStyle, finalize_figure
    from .explain import gradients as explain_gradients
    from .explain import permutation as explain_permutation
    from .explain import shap_utils as explain_shap
except Exception:  # pragma: no cover - optional for legacy imports
    try:  # best-effort for non-package imports
        from ins_pricing.modelling.plotting import curves as plot_curves
        from ins_pricing.modelling.plotting import diagnostics as plot_diagnostics
        from ins_pricing.modelling.plotting.common import PlotStyle, finalize_figure
        from ins_pricing.modelling.explain import gradients as explain_gradients
        from ins_pricing.modelling.explain import permutation as explain_permutation
        from ins_pricing.modelling.explain import shap_utils as explain_shap
    except Exception:  # pragma: no cover
        plot_curves = None
        plot_diagnostics = None
        PlotStyle = None
        finalize_figure = None
        explain_gradients = None
        explain_permutation = None
        explain_shap = None


# BayesOpt orchestration and SHAP utilities
# =============================================================================
class BayesOptModel:
    
    # Property proxies to maintain backward compatibility with Trainers
    @property
    def train_data(self): return self.data_container.train_data
    @property
    def test_data(self): return self.data_container.test_data
    @property
    def train_oht_data(self): return self.data_container.train_oht_data
    @property
    def test_oht_data(self): return self.data_container.test_oht_data
    @property
    def train_oht_scl_data(self): return self.data_container.train_oht_scl_data
    @property
    def test_oht_scl_data(self): return self.data_container.test_oht_scl_data
    @property
    def var_nmes(self): return self.data_container.var_nmes
    @property
    def num_features(self): return self.data_container.num_features
    @property
    def cat_categories_for_shap(self): return self.data_container.cat_categories_for_shap
    @property
    def train_geo_tokens(self): return self.data_container.train_geo_tokens
    @train_geo_tokens.setter
    def train_geo_tokens(self, val): self.data_container.train_geo_tokens = val
    @property
    def test_geo_tokens(self): return self.data_container.test_geo_tokens
    @test_geo_tokens.setter
    def test_geo_tokens(self, val): self.data_container.test_geo_tokens = val
    @property
    def geo_token_cols(self): return self.data_container.geo_token_cols
    @geo_token_cols.setter
    def geo_token_cols(self, val): self.data_container.geo_token_cols = val

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
                 ft_num_numeric_tokens: Optional[int] = None,
                 infer_categorical_max_unique: int = 50,
                 infer_categorical_max_ratio: float = 0.05,
                 reuse_best_params: bool = False,
                 xgb_max_depth_max: int = 25,
                 xgb_n_estimators_max: int = 500,
                 resn_weight_decay: Optional[float] = None,
                 final_ensemble: bool = False,
                 final_ensemble_k: int = 3,
                 final_refit: bool = True,
                 optuna_storage: Optional[str] = None,
                 optuna_study_prefix: Optional[str] = None,
                 best_params_files: Optional[Dict[str, str]] = None):
        """Orchestrate BayesOpt training across multiple trainers."""
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

        config_args = {
            "model_nme": model_nme,
            "task_type": task_type,
            "resp_nme": resp_nme,
            "weight_nme": weight_nme,
            "factor_nmes": list(inferred_factors),
            "binary_resp_nme": binary_resp_nme,
            "cate_list": list(inferred_cats) if inferred_cats else None,
            "prop_test": prop_test,
            "rand_seed": rand_seed,
            "epochs": epochs,
            "use_gpu": use_gpu,
            "xgb_max_depth_max": int(xgb_max_depth_max),
            "xgb_n_estimators_max": int(xgb_n_estimators_max),
            "use_resn_data_parallel": use_resn_data_parallel,
            "use_ft_data_parallel": use_ft_data_parallel,
            "use_resn_ddp": use_resn_ddp,
            "use_gnn_data_parallel": use_gnn_data_parallel,
            "use_ft_ddp": use_ft_ddp,
            "use_gnn_ddp": use_gnn_ddp,
            "gnn_use_approx_knn": gnn_use_approx_knn,
            "gnn_approx_knn_threshold": gnn_approx_knn_threshold,
            "gnn_graph_cache": gnn_graph_cache,
            "gnn_max_gpu_knn_nodes": gnn_max_gpu_knn_nodes,
            "gnn_knn_gpu_mem_ratio": gnn_knn_gpu_mem_ratio,
            "gnn_knn_gpu_mem_overhead": gnn_knn_gpu_mem_overhead,
            "output_dir": output_dir,
            "optuna_storage": optuna_storage,
            "optuna_study_prefix": optuna_study_prefix,
            "best_params_files": best_params_files,
            "ft_role": str(ft_role or "model"),
            "ft_feature_prefix": str(ft_feature_prefix or "ft_emb"),
            "ft_num_numeric_tokens": ft_num_numeric_tokens,
            "reuse_best_params": bool(reuse_best_params),
            "resn_weight_decay": float(resn_weight_decay) if resn_weight_decay is not None else 1e-4,
            "final_ensemble": bool(final_ensemble),
            "final_ensemble_k": int(final_ensemble_k),
            "final_refit": bool(final_refit),
        }
        cfg = BayesOptConfig.from_legacy_dict(config_args)
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
        
        self.data_container = DataContainer(
            train_data=preprocessor.train_data,
            test_data=preprocessor.test_data
        )
        self.data_container.set_preprocessed_data(preprocessor)

        self.geo_gnn_model: Optional[GraphNeuralNetSklearn] = None
        
        # Use extracted feature engineering logic
        _add_region_effect(self)

        self.cv = ShuffleSplit(n_splits=int(1/self.prop_test),
                               test_size=self.prop_test,
                               random_state=self.rand_seed)
        if self.task_type == 'classification':
            self.obj = 'binary:logistic'
        else:
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

        self.version_manager = VersionManager(self.output_manager)
        
        self.model_manager = ModelManager(self)
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
        return _build_geo_tokens(self, params_override)

    def _prepare_geo_tokens(self) -> None:
        return _prepare_geo_tokens(self)

    # Note: _add_region_effect was called in __init__ directly via the imported function.
    # We remove the method definition here or keep it as a wrapper if called elsewhere.
    # It seems it's only called in __init__, so we can remove strict method definition
    # unless subclasses use it. To be safe, let's keep it wrapper.
    def _add_region_effect(self) -> None:
        _add_region_effect(self)

    # Plotting wrappers
    def plot_oneway(self, n_bins=10):
        plot_oneway(self, n_bins)

    def _require_trainer(self, model_key: str) -> "TrainerBase":
        return self.model_manager.get_trainer(model_key)

    def _pred_vector_columns(self, pred_prefix: str) -> List[str]:
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
        pass

    def optimize_model(self, model_key: str, max_evals: int = 100):
        self.model_manager.optimize(model_key, max_evals)

    def add_numeric_feature_from_column(self, col_name: str) -> None:
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
                tr).astype(np.float32).reshape(-1)
            self.test_oht_scl_data[col_name] = scaler.transform(te).astype(np.float32).reshape(-1)

        if col_name not in self.var_nmes:
            self.var_nmes.append(col_name)

    def add_numeric_features_from_columns(self, col_names: List[str]) -> None:
        if not col_names:
            return
        missing = [
            col for col in col_names
            if col not in self.train_data.columns or col not in self.test_data.columns
        ]
        if missing:
            raise KeyError(
                f"Column(s) {missing} must exist in both train_data and test_data."
            )

        for col_name in col_names:
            if col_name not in self.factor_nmes:
                self.factor_nmes.append(col_name)
            if col_name not in self.config.factor_nmes:
                self.config.factor_nmes.append(col_name)
            if col_name not in self.cate_list and col_name not in self.num_features:
                self.num_features.append(col_name)
            if col_name not in self.var_nmes:
                self.var_nmes.append(col_name)

        if self.train_oht_data is not None and self.test_oht_data is not None:
            self.train_oht_data.loc[:, col_names] = self.train_data[col_names].to_numpy(copy=False)
            self.test_oht_data.loc[:, col_names] = self.test_data[col_names].to_numpy(copy=False)

        if self.train_oht_scl_data is not None and self.test_oht_scl_data is not None:
            scaler = StandardScaler()
            tr = self.train_data[col_names].to_numpy(dtype=np.float32, copy=False)
            te = self.test_data[col_names].to_numpy(dtype=np.float32, copy=False)
            self.train_oht_scl_data.loc[:, col_names] = scaler.fit_transform(tr).astype(np.float32)
            self.test_oht_scl_data.loc[:, col_names] = scaler.transform(te).astype(np.float32)

    def prepare_ft_as_feature(self, max_evals: int = 50, pred_prefix: str = "ft_feat") -> str:
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

    def bayesopt_glm(self, max_evals=50):
        self.optimize_model('glm', max_evals)

    def bayesopt_xgb(self, max_evals=100):
        self.optimize_model('xgb', max_evals)

    def bayesopt_resnet(self, max_evals=100):
        self.optimize_model('resn', max_evals)

    def bayesopt_gnn(self, max_evals=50):
        self.optimize_model('gnn', max_evals)

    def bayesopt_ft(self, max_evals=50):
        self.optimize_model('ft', max_evals)

    def plot_lift(self, model_label, pred_nme, n_bins=10):
        plot_lift(self, model_label, pred_nme, n_bins)

    def plot_dlift(self, model_comp: List[str] = ['xgb', 'resn'], n_bins: int = 10) -> None:
        plot_dlift(self, model_comp, n_bins)

    def plot_conversion_lift(self, model_pred_col: str, n_bins: int = 20):
        plot_conversion_lift(self, model_pred_col, n_bins)

    # ========= Lightweight explainability: Permutation Importance =========
    def compute_permutation_importance(self,
                                       model_key: str,
                                       on_train: bool = True,
                                       metric: Any = "auto",
                                       n_repeats: int = 5,
                                       max_rows: int = 5000,
                                       random_state: Optional[int] = None):
        if explain_permutation is None:
            raise RuntimeError("explain.permutation is not available.")

        model_key = str(model_key)
        data = self.train_data if on_train else self.test_data
        if self.resp_nme not in data.columns:
            raise RuntimeError("Missing response column for permutation importance.")
        y = data[self.resp_nme]
        w = data[self.weight_nme] if self.weight_nme in data.columns else None

        if model_key == "resn":
            if self.resn_best is None:
                raise RuntimeError("ResNet model not trained.")
            X = self.train_oht_scl_data if on_train else self.test_oht_scl_data
            if X is None:
                raise RuntimeError("Missing standardized features for ResNet.")
            X = X[self.var_nmes]
            predict_fn = lambda df: self.resn_best.predict(df)
        elif model_key == "ft":
            if self.ft_best is None:
                raise RuntimeError("FT model not trained.")
            if str(self.config.ft_role) != "model":
                raise RuntimeError("FT role is not 'model'; FT predictions unavailable.")
            X = data[self.factor_nmes]
            geo_tokens = self.train_geo_tokens if on_train else self.test_geo_tokens
            geo_np = None
            if geo_tokens is not None:
                geo_np = geo_tokens.to_numpy(dtype=np.float32, copy=False)
            predict_fn = lambda df, geo=geo_np: self.ft_best.predict(df, geo_tokens=geo)
        elif model_key == "xgb":
            if self.xgb_best is None:
                raise RuntimeError("XGB model not trained.")
            X = data[self.factor_nmes]
            predict_fn = lambda df: self.xgb_best.predict(df)
        else:
            raise ValueError("Unsupported model_key for permutation importance.")

        return explain_permutation.permutation_importance(
            predict_fn,
            X,
            y,
            sample_weight=w,
            metric=metric,
            task_type=self.task_type,
            n_repeats=n_repeats,
            random_state=random_state,
            max_rows=max_rows,
        )

    # ========= Deep explainability: Integrated Gradients =========
    def compute_integrated_gradients_resn(self,
                                          on_train: bool = True,
                                          baseline: Any = None,
                                          steps: int = 50,
                                          batch_size: int = 256,
                                          target: Optional[int] = None):
        if explain_gradients is None:
            raise RuntimeError("explain.gradients is not available.")
        if self.resn_best is None:
            raise RuntimeError("ResNet model not trained.")
        X = self.train_oht_scl_data if on_train else self.test_oht_scl_data
        if X is None:
            raise RuntimeError("Missing standardized features for ResNet.")
        X = X[self.var_nmes]
        return explain_gradients.resnet_integrated_gradients(
            self.resn_best,
            X,
            baseline=baseline,
            steps=steps,
            batch_size=batch_size,
            target=target,
        )

    def compute_integrated_gradients_ft(self,
                                        on_train: bool = True,
                                        geo_tokens: Optional[np.ndarray] = None,
                                        baseline_num: Any = None,
                                        baseline_geo: Any = None,
                                        steps: int = 50,
                                        batch_size: int = 256,
                                        target: Optional[int] = None):
        if explain_gradients is None:
            raise RuntimeError("explain.gradients is not available.")
        if self.ft_best is None:
            raise RuntimeError("FT model not trained.")
        if str(self.config.ft_role) != "model":
            raise RuntimeError("FT role is not 'model'; FT explanations unavailable.")

        data = self.train_data if on_train else self.test_data
        X = data[self.factor_nmes]

        if geo_tokens is None and getattr(self.ft_best, "num_geo", 0) > 0:
            tokens_df = self.train_geo_tokens if on_train else self.test_geo_tokens
            if tokens_df is not None:
                geo_tokens = tokens_df.to_numpy(dtype=np.float32, copy=False)

        return explain_gradients.ft_integrated_gradients(
            self.ft_best,
            X,
            geo_tokens=geo_tokens,
            baseline_num=baseline_num,
            baseline_geo=baseline_geo,
            steps=steps,
            batch_size=batch_size,
            target=target,
        )

    def save_model(self, model_name=None):
        keys = [model_name] if model_name else self.model_manager.trainers.keys()
        for key in keys:
            if key in self.model_manager.trainers:
                self.model_manager.trainers[key].save()
            else:
                if model_name:
                    print(f"[save_model] Warning: Unknown model key {key}")

    def load_model(self, model_name=None):
        keys = [model_name] if model_name else self.model_manager.trainers.keys()
        for key in keys:
            if key in self.model_manager.trainers:
                self.model_manager.trainers[key].load()
                # Restore to ctx for backward compat
                trainer = self.model_manager.trainers[key]
                if trainer.model is not None:
                    setattr(self, f"{key}_best", trainer.model)
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
        X_mat = np.concatenate(matrices, axis=1)  # Result shape (N, F)
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
        if explain_shap is None:
            raise RuntimeError("explain.shap_utils is not available.")
        return explain_shap.compute_shap_core(
            self,
            model_key,
            n_background,
            n_samples,
            on_train,
            X_df=X_df,
            prep_fn=prep_fn,
            predict_fn=predict_fn,
            cleanup_fn=cleanup_fn,
        )

    def compute_shap_glm(self, n_background: int = 500,
                         n_samples: int = 200,
                         on_train: bool = True):
        if explain_shap is None:
            raise RuntimeError("explain.shap_utils is not available.")
        self.shap_glm = explain_shap.compute_shap_glm(
            self,
            n_background=n_background,
            n_samples=n_samples,
            on_train=on_train,
        )
        return self.shap_glm

    def compute_shap_xgb(self, n_background: int = 500,
                         n_samples: int = 200,
                         on_train: bool = True):
        if explain_shap is None:
            raise RuntimeError("explain.shap_utils is not available.")
        self.shap_xgb = explain_shap.compute_shap_xgb(
            self,
            n_background=n_background,
            n_samples=n_samples,
            on_train=on_train,
        )
        return self.shap_xgb

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
        if explain_shap is None:
            raise RuntimeError("explain.shap_utils is not available.")
        self.shap_resn = explain_shap.compute_shap_resn(
            self,
            n_background=n_background,
            n_samples=n_samples,
            on_train=on_train,
        )
        return self.shap_resn

    def _ft_shap_predict_wrapper(self, X_mat: np.ndarray) -> np.ndarray:
        df_input = self._decode_ft_shap_matrix_to_df(X_mat)
        y_pred = self.ft_best.predict(df_input)
        return np.asarray(y_pred, dtype=np.float64).reshape(-1)

    def compute_shap_ft(self, n_background: int = 500,
                        n_samples: int = 200,
                        on_train: bool = True):
        if explain_shap is None:
            raise RuntimeError("explain.shap_utils is not available.")
        self.shap_ft = explain_shap.compute_shap_ft(
            self,
            n_background=n_background,
            n_samples=n_samples,
            on_train=on_train,
        )
        return self.shap_ft
