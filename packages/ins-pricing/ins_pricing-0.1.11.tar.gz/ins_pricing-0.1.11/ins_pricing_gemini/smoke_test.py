
import sys
import os
from pathlib import Path

# Add current dir to sys.path to simulate running from root without install (if needed)
sys.path.insert(0, os.getcwd())

print("Testing direct import from modelling folder (simulated root usage)...")
try:
    from modelling.core import BayesOptModel
    print("SUCCESS: from modelling.core import BayesOptModel")
except ImportError as e:
    print(f"FAILURE: from modelling.core import BayesOptModel: {e}")

print("\nTesting ins_pricing.modelling namespace import (requires install or setup.py magic)...")
try:
    from ins_pricing.modelling.core import BayesOptModel
    print("SUCCESS: from ins_pricing.modelling.core import BayesOptModel")
except ImportError as e:
    print(f"FAILURE: from ins_pricing.modelling.core import BayesOptModel: {e}")

print("\nTesting plotting import...")
try:
    from modelling.plotting import curves
    print("SUCCESS: from modelling.plotting import curves")
except ImportError as e:
    print(f"FAILURE: from modelling.plotting import curves: {e}")
