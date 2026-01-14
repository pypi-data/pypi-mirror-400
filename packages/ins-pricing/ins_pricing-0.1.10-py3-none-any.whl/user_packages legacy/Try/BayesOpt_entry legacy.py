"""
CLI entry point generated from BayesOpt_AutoPricing.ipynb so the workflow can
run non‑interactively (e.g., via torchrun).

Example:
    torchrun --standalone --nproc_per_node=2 \\
        python BayesOpt_entry.py \\
        --config-json config.json \\
        --model-key ft --max-evals 50 --use-ft-ddp
"""

from __future__ import annotations

import argparse
import json
import os
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

import BayesOpt as ropt

PLOT_MODEL_LABELS: Dict[str, Tuple[str, str]] = {
    "glm": ("GLM", "pred_glm"),
    "xgb": ("Xgboost", "pred_xgb"),
    "resn": ("ResNet", "pred_resn"),
    "ft": ("FTTransformer", "pred_ft"),
    "gnn": ("GNN", "pred_gnn"),
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch trainer generated from BayesOpt_AutoPricing notebook."
    )
    parser.add_argument(
        "--config-json",
        required=True,
        help="Path to the JSON config describing datasets and feature columns.",
    )
    parser.add_argument(
        "--model-keys",
        nargs="+",
        default=["ft"],
        choices=["glm", "xgb", "resn", "ft", "gnn", "all"],
        help="Space-separated list of trainers to run (e.g., --model-keys glm xgb). Include 'all' to run every trainer.",
    )
    parser.add_argument(
        "--max-evals",
        type=int,
        default=50,
        help="Optuna trial count per dataset.",
    )
    parser.add_argument(
        "--use-resn-ddp",
        action="store_true",
        help="Force ResNet trainer to use DistributedDataParallel.",
    )
    parser.add_argument(
        "--use-ft-ddp",
        action="store_true",
        help="Force FT-Transformer trainer to use DistributedDataParallel.",
    )
    parser.add_argument(
        "--use-resn-dp",
        action="store_true",
        help="Enable ResNet DataParallel fall-back regardless of config.",
    )
    parser.add_argument(
        "--use-ft-dp",
        action="store_true",
        help="Enable FT-Transformer DataParallel fall-back regardless of config.",
    )
    parser.add_argument(
        "--use-gnn-dp",
        action="store_true",
        help="Enable GNN DataParallel fall-back regardless of config.",
    )
    parser.add_argument(
        "--use-gnn-ddp",
        action="store_true",
        help="Force GNN trainer to use DistributedDataParallel.",
    )
    parser.add_argument(
        "--use-gnn-faiss",
        action="store_true",
        help="Force GNN to build graphs with FAISS ANN (CPU/GPU depending on availability).",
    )
    parser.add_argument(
        "--gnn-faiss-cpu",
        action="store_true",
        help="Force FAISS ANN to run on CPU even if GPUs are visible.",
    )
    return parser.parse_args()


def _load_config(path: Path) -> Dict:
    # JSON 配置中包含数据集路径、特征/标签字段以及绘图开关。
    cfg = json.loads(path.read_text(encoding="utf-8"))
    required = [
        "data_dir",
        "model_list",
        "model_categories",
        "target",
        "weight",
        "feature_list",
        "categorical_features",
    ]
    missing = [key for key in required if key not in cfg]
    if missing:
        raise ValueError(f"Missing required keys in {path}: {missing}")
    return cfg


def _set_env(env_overrides: Dict[str, str]) -> None:
    # 仅在环境变量未设置时进行填充。
    for key, value in env_overrides.items():
        os.environ.setdefault(key, str(value))


def _build_model_names(prefixes: List[str], suffixes: List[str]) -> List[str]:
    # 生成基础模型名与类别的笛卡尔积（如 prod/gl/）。
    names: List[str] = []
    for suffix in suffixes:
        names.extend(f"{prefix}_{suffix}" for prefix in prefixes)
    return names


def _dedupe_preserve_order(items: List[str]) -> List[str]:
    # 去重但保留首个出现顺序。
    seen = set()
    unique_items: List[str] = []
    for item in items:
        if item not in seen:
            unique_items.append(item)
            seen.add(item)
    return unique_items


def _parse_model_pairs(raw_pairs: List) -> List[Tuple[str, str]]:
    # 兼容 [["glm","xgb"]] 或 "glm,xgb" 两种格式。
    pairs: List[Tuple[str, str]] = []
    for pair in raw_pairs:
        if isinstance(pair, (list, tuple)) and len(pair) == 2:
            pairs.append((str(pair[0]), str(pair[1])))
        elif isinstance(pair, str):
            parts = [p.strip() for p in pair.split(",") if p.strip()]
            if len(parts) == 2:
                pairs.append((parts[0], parts[1]))
    return pairs


def _plot_curves_for_model(model: ropt.BayesOptModel, trained_keys: List[str], cfg: Dict) -> None:
    plot_cfg = cfg.get("plot", {})
    legacy_lift_flags = {
        "glm": cfg.get("plot_lift_glm", False),
        "xgb": cfg.get("plot_lift_xgb", False),
        "resn": cfg.get("plot_lift_resn", False),
        "ft": cfg.get("plot_lift_ft", False),
    }
    plot_enabled = plot_cfg.get("enable", any(legacy_lift_flags.values()))
    if not plot_enabled:
        return

    n_bins = int(plot_cfg.get("n_bins", 10))
    oneway_enabled = plot_cfg.get("oneway", True)

    available_models = _dedupe_preserve_order(
        [m for m in trained_keys if m in PLOT_MODEL_LABELS]
    )

    if oneway_enabled:
        model.plot_oneway(n_bins=n_bins)

    if not available_models:
        return

    lift_models = plot_cfg.get("lift_models")
    if lift_models is None:
        lift_models = [
            m for m, enabled in legacy_lift_flags.items() if enabled]
        if not lift_models:
            lift_models = available_models
    lift_models = _dedupe_preserve_order(
        [m for m in lift_models if m in available_models]
    )

    for model_key in lift_models:
        label, pred_nme = PLOT_MODEL_LABELS[model_key]
        model.plot_lift(model_label=label, pred_nme=pred_nme, n_bins=n_bins)

    if not plot_cfg.get("double_lift", True) or len(available_models) < 2:
        return

    raw_pairs = plot_cfg.get("double_lift_pairs")
    if raw_pairs:
        pairs = [
            (a, b)
            for a, b in _parse_model_pairs(raw_pairs)
            if a in available_models and b in available_models and a != b
        ]
    else:
        pairs = list(combinations(available_models, 2))

    for first, second in pairs:
        model.plot_dlift([first, second], n_bins=n_bins)


def train_from_config(args: argparse.Namespace) -> None:
    cfg = _load_config(Path(args.config_json))

    _set_env(cfg.get("env", {}))

    data_dir = Path(cfg["data_dir"]).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    prop_test = cfg.get("prop_test", 0.25)
    rand_seed = cfg.get("rand_seed", 13)
    epochs = cfg.get("epochs", 50)

    model_names = _build_model_names(
        cfg["model_list"], cfg["model_categories"])
    if not model_names:
        raise ValueError(
            "No model names generated from model_list/model_categories.")

    results: Dict[str, ropt.BayesOptModel] = {}
    trained_keys_by_model: Dict[str, List[str]] = {}

    for model_name in model_names:
        # 针对每个数据集的训练循环：加载数据、划分训练测试、按请求训练模型。
        csv_path = data_dir / f"{model_name}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing dataset: {csv_path}")

        print(f"\n=== Processing model {model_name} ===")
        raw = pd.read_csv(csv_path, low_memory=False)
        raw.fillna(0, inplace=True)

        train_df, test_df = train_test_split(
            raw, test_size=prop_test, random_state=rand_seed
        )

        use_resn_dp = args.use_resn_dp or cfg.get(
            "use_resn_data_parallel", False)
        use_ft_dp = args.use_ft_dp or cfg.get("use_ft_data_parallel", True)
        use_resn_ddp = args.use_resn_ddp or cfg.get("use_resn_ddp", False)
        use_ft_ddp = args.use_ft_ddp or cfg.get("use_ft_ddp", False)
        use_gnn_dp = args.use_gnn_dp or cfg.get("use_gnn_data_parallel", False)
        use_gnn_ddp = args.use_gnn_ddp or cfg.get("use_gnn_ddp", False)
        use_gnn_faiss = args.use_gnn_faiss or cfg.get("use_gnn_faiss", False)
        use_gnn_faiss_gpu = cfg.get(
            "use_gnn_faiss_gpu", True) and (not args.gnn_faiss_cpu)

        model = ropt.BayesOptModel(
            train_df,
            test_df,
            model_name,
            cfg["target"],
            cfg["weight"],
            cfg["feature_list"],
            cate_list=cfg["categorical_features"],
            prop_test=prop_test,
            rand_seed=rand_seed,
            epochs=epochs,
            use_resn_data_parallel=use_resn_dp,
            use_ft_data_parallel=use_ft_dp,
            use_resn_ddp=use_resn_ddp,
            use_ft_ddp=use_ft_ddp,
            use_gnn_data_parallel=use_gnn_dp,
            use_gnn_ddp=use_gnn_ddp,
            use_gnn_faiss=use_gnn_faiss,
            use_gnn_faiss_gpu=use_gnn_faiss_gpu,
        )

        if "all" in args.model_keys:
            requested_keys = ["glm", "xgb", "resn", "ft", "gnn"]
        else:
            requested_keys = args.model_keys
        requested_keys = _dedupe_preserve_order(requested_keys)
        missing = [key for key in requested_keys if key not in model.trainers]
        if missing:
            raise ValueError(
                f"Trainer(s) {missing} not available for {model_name}")

        for key in requested_keys:
            print(
                f"Optimizing {key} for {model_name} (max_evals={args.max_evals})")
            model.optimize_model(key, max_evals=args.max_evals)
            model.trainers[key].save()
            ropt.free_cuda()

        results[model_name] = model
        trained_keys_by_model[model_name] = requested_keys

    for name, model in results.items():
        _plot_curves_for_model(
            model,
            trained_keys_by_model.get(name, []),
            cfg,
        )


def main() -> None:
    args = _parse_args()
    train_from_config(args)


if __name__ == "__main__":
    main()
