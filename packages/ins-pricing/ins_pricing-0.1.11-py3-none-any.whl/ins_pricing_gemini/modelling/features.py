from __future__ import annotations

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Optional, Dict, Any, TYPE_CHECKING
import sys

if TYPE_CHECKING:
    from .core import BayesOptModel

def _add_region_effect(model: "BayesOptModel") -> None:
    """Partial pooling over province/city to create a smoothed region_effect feature."""
    prov_col = model.config.region_province_col
    city_col = model.config.region_city_col
    if not prov_col or not city_col:
        return
    for col in [prov_col, city_col]:
        if col not in model.train_data.columns:
            print(f"[RegionEffect] Missing column {col}; skipped.")
            return

    def safe_mean(df: pd.DataFrame) -> float:
        w = df[model.weight_nme]
        y = df[model.resp_nme]
        # EPS is imported from utils usually, but we can define local or import
        denom = max(float(w.sum()), 1e-6)
        return float((y * w).sum() / denom)

    global_mean = safe_mean(model.train_data)
    alpha = max(float(model.config.region_effect_alpha), 0.0)

    w_all = model.train_data[model.weight_nme]
    y_all = model.train_data[model.resp_nme]
    yw_all = y_all * w_all

    prov_sumw = w_all.groupby(model.train_data[prov_col]).sum()
    prov_sumyw = yw_all.groupby(model.train_data[prov_col]).sum()
    prov_mean = (prov_sumyw / prov_sumw.clip(lower=1e-6)).astype(float)
    prov_mean = prov_mean.fillna(global_mean)

    city_sumw = model.train_data.groupby([prov_col, city_col])[
        model.weight_nme].sum()
    city_sumyw = yw_all.groupby(
        [model.train_data[prov_col], model.train_data[city_col]]).sum()
    city_df = pd.DataFrame({
        "sum_w": city_sumw,
        "sum_yw": city_sumyw,
    })
    city_df["prior"] = city_df.index.get_level_values(0).map(
        prov_mean).fillna(global_mean)
    city_df["effect"] = (
        city_df["sum_yw"] + alpha * city_df["prior"]
    ) / (city_df["sum_w"] + alpha).clip(lower=1e-6)
    city_effect = city_df["effect"]

    def lookup_effect(df: pd.DataFrame) -> pd.Series:
        idx = pd.MultiIndex.from_frame(df[[prov_col, city_col]])
        effects = city_effect.reindex(idx).to_numpy(dtype=np.float64)
        prov_fallback = df[prov_col].map(
            prov_mean).fillna(global_mean).to_numpy(dtype=np.float64)
        effects = np.where(np.isfinite(effects), effects, prov_fallback)
        effects = np.where(np.isfinite(effects), effects, global_mean)
        return pd.Series(effects, index=df.index, dtype=np.float32)

    re_train = lookup_effect(model.train_data)
    re_test = lookup_effect(model.test_data)

    col_name = "region_effect"
    model.train_data[col_name] = re_train
    model.test_data[col_name] = re_test

    # Sync into one-hot and scaled variants.
    for df in [model.train_oht_data, model.test_oht_data]:
        if df is not None:
            df[col_name] = re_train if df is model.train_oht_data else re_test

    # Standardize region_effect and propagate.
    scaler = StandardScaler()
    re_train_s = scaler.fit_transform(
        re_train.values.reshape(-1, 1)).astype(np.float32).reshape(-1)
    re_test_s = scaler.transform(
        re_test.values.reshape(-1, 1)).astype(np.float32).reshape(-1)
    for df in [model.train_oht_scl_data, model.test_oht_scl_data]:
        if df is not None:
            df[col_name] = re_train_s if df is model.train_oht_scl_data else re_test_s

    # Update feature lists.
    if col_name not in model.factor_nmes:
        model.factor_nmes.append(col_name)
    if col_name not in model.num_features:
        model.num_features.append(col_name)
    if model.train_oht_scl_data is not None:
        excluded = {model.weight_nme, model.resp_nme}
        model.var_nmes = [
            col for col in model.train_oht_scl_data.columns if col not in excluded
        ]

def _build_geo_tokens(model: "BayesOptModel", params_override: Optional[Dict[str, Any]] = None):
    """Internal builder; allows trial overrides and returns None on failure."""
    from .models import GraphNeuralNetSklearn # lazy import to avoid circle if models imports core
    
    geo_cols = list(model.config.geo_feature_nmes or [])
    if not geo_cols:
        return None

    available = [c for c in geo_cols if c in model.train_data.columns]
    if not available:
        return None

    # Preprocess text/numeric: fill numeric with median, label-encode text, map unknowns.
    proc_train = {}
    proc_test = {}
    for col in available:
        s_train = model.train_data[col]
        s_test = model.test_data[col]
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

    train_geo_raw = pd.DataFrame(proc_train, index=model.train_data.index)
    test_geo_raw = pd.DataFrame(proc_test, index=model.test_data.index)

    scaler = StandardScaler()
    train_geo = pd.DataFrame(
        scaler.fit_transform(train_geo_raw),
        columns=available,
        index=model.train_data.index
    )
    test_geo = pd.DataFrame(
        scaler.transform(test_geo_raw),
        columns=available,
        index=model.test_data.index
    )

    tw_power = model.default_tweedie_power()

    cfg = params_override or {}
    try:
        geo_gnn = GraphNeuralNetSklearn(
            model_nme=f"{model.model_nme}_geo",
            input_dim=len(available),
            hidden_dim=cfg.get("geo_token_hidden_dim",
                               model.config.geo_token_hidden_dim),
            num_layers=cfg.get("geo_token_layers",
                               model.config.geo_token_layers),
            k_neighbors=cfg.get("geo_token_k_neighbors",
                                model.config.geo_token_k_neighbors),
            dropout=cfg.get("geo_token_dropout",
                            model.config.geo_token_dropout),
            learning_rate=cfg.get(
                "geo_token_learning_rate", model.config.geo_token_learning_rate),
            epochs=int(cfg.get("geo_token_epochs",
                       model.config.geo_token_epochs)),
            patience=5,
            task_type=model.task_type,
            tweedie_power=tw_power,
            use_data_parallel=False,
            use_ddp=False,
            use_approx_knn=model.config.gnn_use_approx_knn,
            approx_knn_threshold=model.config.gnn_approx_knn_threshold,
            graph_cache_path=None,
            max_gpu_knn_nodes=model.config.gnn_max_gpu_knn_nodes,
            knn_gpu_mem_ratio=model.config.gnn_knn_gpu_mem_ratio,
            knn_gpu_mem_overhead=model.config.gnn_knn_gpu_mem_overhead
        )
        geo_gnn.fit(
            train_geo,
            model.train_data[model.resp_nme],
            model.train_data[model.weight_nme]
        )
        train_embed = geo_gnn.encode(train_geo)
        test_embed = geo_gnn.encode(test_geo)
        cols = [f"geo_token_{i}" for i in range(train_embed.shape[1])]
        train_tokens = pd.DataFrame(
            train_embed, index=model.train_data.index, columns=cols)
        test_tokens = pd.DataFrame(
            test_embed, index=model.test_data.index, columns=cols)
        return train_tokens, test_tokens, cols, geo_gnn
    except Exception as exc:
        print(f"[GeoToken] Generation failed: {exc}")
        return None

def _prepare_geo_tokens(model: "BayesOptModel") -> None:
    """Build and persist geo tokens with default config values."""
    gnn_trainer = model.model_manager.trainers.get("gnn")
    if gnn_trainer is not None and hasattr(gnn_trainer, "prepare_geo_tokens"):
        try:
            gnn_trainer.prepare_geo_tokens(force=False)  # type: ignore[attr-defined]
            return
        except Exception as exc:
            print(f"[GeoToken] GNNTrainer generation failed: {exc}")

    result = _build_geo_tokens(model)
    if result is None:
        return
    train_tokens, test_tokens, cols, geo_gnn = result
    model.train_geo_tokens = train_tokens
    model.test_geo_tokens = test_tokens
    model.geo_token_cols = cols
    model.geo_gnn_model = geo_gnn
    print(f"[GeoToken] Generated {len(cols)}-dim geo tokens; injecting into FT.")
