from setuptools import setup, find_packages
import os

# Custom package discovery to map root folders to ins_pricing namespace
# Because the root folder "ins_pricing v2" has a space and handled as "."
def start_package_discovery():
    # We want 'modelling' -> 'ins_pricing.modelling'
    # 'pricing' -> 'ins_pricing.pricing'
    # etc.
    # And '.' -> 'ins_pricing'
    
    root_packages = ['modelling', 'pricing', 'production', 'governance', 'reporting', 'scripts']
    packages = ['ins_pricing']
    
    for root in root_packages:
        # Find subpackages for each root package
        found = find_packages(where='.', include=[root, f"{root}.*"])
        for pkg in found:
            packages.append(f"ins_pricing.{pkg}")
            
    return packages

setup(
    name="ins_pricing",
    version="2.0.0",
    description="Insurance Pricing Modelling Toolbox",
    # Map 'ins_pricing' package to current directory '.'
    package_dir={'ins_pricing': '.'},
    packages=start_package_discovery(),
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "statsmodels",
        "pydantic",  # Required for data validation
    ],
    extras_require={
        "full": [
            "torch",
            "xgboost",
            "optuna",
            "shap",
            "matplotlib",
        ]
    },
    entry_points={
        "console_scripts": [
            "ins-pricing-train=ins_pricing.scripts.train:main",
            "ins-pricing-incremental=ins_pricing.scripts.BayesOpt_incremental:main",
            "ins-pricing-explain=ins_pricing.scripts.Explain_entry:main",
        ]
    },
    include_package_data=True,
)
