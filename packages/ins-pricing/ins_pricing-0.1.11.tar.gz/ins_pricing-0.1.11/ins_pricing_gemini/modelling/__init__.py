"""Modelling subpackage for ins_pricing."""

from __future__ import annotations
import types
import sys
from importlib import import_module
from pathlib import Path

# Exports
from .config import BayesOptConfig
from .config_preprocess import (
    DatasetPreprocessor,
    OutputManager,
    VersionManager,
)
from .core import BayesOptModel
from .models import (
    FeatureTokenizer,
    FTTransformerCore,
    FTTransformerSklearn,
    GraphNeuralNetSklearn,
    MaskedTabularDataset,
    ResBlock,
    ResNetSequential,
    ResNetSklearn,
    ScaledTransformerEncoderLayer,
    SimpleGraphLayer,
    SimpleGNN,
    TabularDataset,
)
from .trainers import (
    FTTrainer,
    GLMTrainer,
    GNNTrainer,
    ResNetTrainer,
    TrainerBase,
    XGBTrainer,
    _xgb_cuda_available,
)
from .utils import (
    EPS,
    DistributedUtils,
    IOUtils,
    PlotUtils,
    TorchTrainerMixin,
    TrainingUtils,
    compute_batch_size,
    csv_to_dict,
    ensure_parent_dir,
    free_cuda,
    infer_factor_and_cate_list,
    plot_dlift_list,
    plot_lift_list,
    set_global_seed,
    split_data,
    tweedie_loss,
)
try:
    import torch
except ImportError:
    torch = None

# Lazy submodules
_LAZY_SUBMODULES = {
    "plotting": "ins_pricing.modelling.plotting",
    "explain": "ins_pricing.modelling.explain",
    "cli_common": "ins_pricing.modelling.cli_common",
    "notebook_utils": "ins_pricing.modelling.notebook_utils",
}

_PACKAGE_PATHS = {
    "plotting": Path(__file__).resolve().parent / "plotting",
    "explain": Path(__file__).resolve().parent / "explain",
}

__all__ = [
    "BayesOptConfig",
    "DatasetPreprocessor",
    "OutputManager",
    "VersionManager",
    "BayesOptModel",
    "FeatureTokenizer",
    "FTTransformerCore",
    "FTTransformerSklearn",
    "GraphNeuralNetSklearn",
    "MaskedTabularDataset",
    "ResBlock",
    "ResNetSequential",
    "ResNetSklearn",
    "ScaledTransformerEncoderLayer",
    "SimpleGraphLayer",
    "SimpleGNN",
    "TabularDataset",
    "FTTrainer",
    "GLMTrainer",
    "GNNTrainer",
    "ResNetTrainer",
    "TrainerBase",
    "XGBTrainer",
    "_xgb_cuda_available",
    "EPS",
    "DistributedUtils",
    "IOUtils",
    "PlotUtils",
    "TorchTrainerMixin",
    "TrainingUtils",
    "compute_batch_size",
    "csv_to_dict",
    "ensure_parent_dir",
    "free_cuda",
    "infer_factor_and_cate_list",
    "plot_dlift_list",
    "plot_lift_list",
    "set_global_seed",
    "split_data",
    "tweedie_loss",
    "torch",
] + sorted(list(_LAZY_SUBMODULES.keys()))

def _lazy_module(name: str, target: str, package_path: Path | None = None) -> types.ModuleType:
    proxy = types.ModuleType(name)
    if package_path is not None:
        proxy.__path__ = [str(package_path)]

    def _load():
        module = import_module(target)
        sys.modules[name] = module
        return module

    def __getattr__(attr: str):
        module = _load()
        return getattr(module, attr)

    def __dir__() -> list[str]:
        module = _load()
        return sorted(set(dir(module)))

    proxy.__getattr__ = __getattr__  # type: ignore[attr-defined]
    proxy.__dir__ = __dir__  # type: ignore[attr-defined]
    return proxy

def _install_proxy(alias: str, target: str) -> None:
    module_name = f"{__name__}.{alias}"
    if module_name in sys.modules:
        return
    proxy = _lazy_module(module_name, target, _PACKAGE_PATHS.get(alias))
    sys.modules[module_name] = proxy
    globals()[alias] = proxy

for _alias, _target in _LAZY_SUBMODULES.items():
    _install_proxy(_alias, _target)
