"""Root package for ins_pricing."""

from __future__ import annotations
from importlib import import_module
import sys

# Root subpackages
_ROOT_SUBPACKAGES = {
    "modelling": "ins_pricing.modelling",
    "pricing": "ins_pricing.pricing",
    "production": "ins_pricing.production",
    "governance": "ins_pricing.governance",
    "reporting": "ins_pricing.reporting",
}

__all__ = sorted(list(_ROOT_SUBPACKAGES.keys()))

def __getattr__(name: str):
    if name in _ROOT_SUBPACKAGES:
        module = import_module(_ROOT_SUBPACKAGES[name])
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
