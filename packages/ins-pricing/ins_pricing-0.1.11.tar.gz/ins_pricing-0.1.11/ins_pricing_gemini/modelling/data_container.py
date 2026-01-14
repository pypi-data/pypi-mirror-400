from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import pandas as pd

@dataclass
class DataContainer:
    """Encapsulates all data structures used during training."""
    
    # Raw Data
    train_data: pd.DataFrame
    test_data: pd.DataFrame
    
    # Preprocessed Views
    train_oht_data: Optional[pd.DataFrame] = None
    test_oht_data: Optional[pd.DataFrame] = None
    
    # Scaled Views (for Neural Nets)
    train_oht_scl_data: Optional[pd.DataFrame] = None
    test_oht_scl_data: Optional[pd.DataFrame] = None
    
    # Special Features
    train_geo_tokens: Optional[pd.DataFrame] = None
    test_geo_tokens: Optional[pd.DataFrame] = None
    geo_token_cols: List[str] = field(default_factory=list)
    
    # Metadata
    var_nmes: List[str] = field(default_factory=list)
    num_features: List[str] = field(default_factory=list)
    cat_categories_for_shap: Dict[str, List[Any]] = field(default_factory=dict)
    
    def set_preprocessed_data(self, preprocessor: 'DatasetPreprocessor') -> None:
        """Populate from a run DatasetPreprocessor."""
        self.train_data = preprocessor.train_data
        self.test_data = preprocessor.test_data
        self.train_oht_data = preprocessor.train_oht_data
        self.test_oht_data = preprocessor.test_oht_data
        self.train_oht_scl_data = preprocessor.train_oht_scl_data
        self.test_oht_scl_data = preprocessor.test_oht_scl_data
        self.var_nmes = preprocessor.var_nmes
        self.num_features = preprocessor.num_features
        self.cat_categories_for_shap = preprocessor.cat_categories_for_shap
