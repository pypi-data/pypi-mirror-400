from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator

class DataConfig(BaseModel):
    resp_nme: str
    weight_nme: str
    factor_nmes: List[str]
    cate_list: Optional[List[str]] = None
    binary_resp_nme: Optional[str] = None
    task_type: str = 'regression'
    prop_test: float = 0.25
    rand_seed: Optional[int] = None

class DistributedConfig(BaseModel):
    use_gpu: bool = True
    use_resn_data_parallel: bool = False
    use_ft_data_parallel: bool = False
    use_gnn_data_parallel: bool = False
    use_resn_ddp: bool = False
    use_ft_ddp: bool = False
    use_gnn_ddp: bool = False
    # DDP Timeout settings can be passed via env, but good to have here if needed
    
class GNNConfig(BaseModel):
    use_approx_knn: bool = True
    approx_knn_threshold: int = 50000
    graph_cache: Optional[str] = None
    max_gpu_knn_nodes: Optional[int] = 200000
    knn_gpu_mem_ratio: float = 0.9
    knn_gpu_mem_overhead: float = 2.0
    
class RegionConfig(BaseModel):
    province_col: Optional[str] = None
    city_col: Optional[str] = None
    effect_alpha: float = 50.0

class GeoTokenConfig(BaseModel):
    feature_nmes: Optional[List[str]] = None
    hidden_dim: int = 32
    layers: int = 2
    dropout: float = 0.1
    k_neighbors: int = 10
    learning_rate: float = 1e-3
    epochs: int = 50

class OptunaConfig(BaseModel):
    storage: Optional[str] = None
    study_prefix: Optional[str] = None
    best_params_files: Optional[Dict[str, str]] = None
    reuse_best_params: bool = False

class FTConfig(BaseModel):
    role: str = "model" # "model", "embedding", "unsupervised_embedding"
    feature_prefix: str = "ft_emb"
    num_numeric_tokens: Optional[int] = None

class BayesOptConfig(BaseModel):
    # Core Data & Task
    data: DataConfig
    
    # Model Names & Meta
    model_nme: str
    
    # Training Hyperparameters
    epochs: int = 100
    xgb_max_depth_max: int = 25
    xgb_n_estimators_max: int = 500
    resn_weight_decay: float = 1e-4
    
    # Sub-component Configs
    dist: DistributedConfig = Field(default_factory=DistributedConfig)
    gnn: GNNConfig = Field(default_factory=GNNConfig)
    region: RegionConfig = Field(default_factory=RegionConfig)
    geo: GeoTokenConfig = Field(default_factory=GeoTokenConfig)
    optuna: OptunaConfig = Field(default_factory=OptunaConfig)
    ft: FTConfig = Field(default_factory=FTConfig)
    
    # Ensemble & output
    output_dir: Optional[str] = None
    final_ensemble: bool = False
    final_ensemble_k: int = 3
    final_refit: bool = True

    # Flattened accessors for backward compatibility
    @property
    def resp_nme(self): return self.data.resp_nme
    @property
    def weight_nme(self): return self.data.weight_nme
    @property
    def factor_nmes(self): return self.data.factor_nmes
    @property
    def task_type(self): return self.data.task_type
    @property
    def cate_list(self): return self.data.cate_list
    @property
    def binary_resp_nme(self): return self.data.binary_resp_nme
    @property
    def prop_test(self): return self.data.prop_test
    @property
    def rand_seed(self): return self.data.rand_seed
    
    @property
    def use_gpu(self): return self.dist.use_gpu
    @property
    def use_resn_data_parallel(self): return self.dist.use_resn_data_parallel
    @property
    def use_ft_data_parallel(self): return self.dist.use_ft_data_parallel
    @property
    def use_gnn_data_parallel(self): return self.dist.use_gnn_data_parallel
    @property
    def use_resn_ddp(self): return self.dist.use_resn_ddp
    @property
    def use_ft_ddp(self): return self.dist.use_ft_ddp
    @property
    def use_gnn_ddp(self): return self.dist.use_gnn_ddp
    
    @property
    def gnn_use_approx_knn(self): return self.gnn.use_approx_knn
    @property
    def gnn_approx_knn_threshold(self): return self.gnn.approx_knn_threshold
    @property
    def gnn_graph_cache(self): return self.gnn.graph_cache
    @property
    def gnn_max_gpu_knn_nodes(self): return self.gnn.max_gpu_knn_nodes
    @property
    def gnn_knn_gpu_mem_ratio(self): return self.gnn.knn_gpu_mem_ratio
    @property
    def gnn_knn_gpu_mem_overhead(self): return self.gnn.knn_gpu_mem_overhead
    
    @property
    def region_province_col(self): return self.region.province_col
    @property
    def region_city_col(self): return self.region.city_col
    @property
    def region_effect_alpha(self): return self.region.effect_alpha
    
    @property
    def geo_feature_nmes(self): return self.geo.feature_nmes
    @property
    def geo_token_hidden_dim(self): return self.geo.hidden_dim
    @property
    def geo_token_layers(self): return self.geo.layers
    @property
    def geo_token_dropout(self): return self.geo.dropout
    @property
    def geo_token_k_neighbors(self): return self.geo.k_neighbors
    @property
    def geo_token_learning_rate(self): return self.geo.learning_rate
    @property
    def geo_token_epochs(self): return self.geo.epochs

    @property
    def optuna_storage(self): return self.optuna.storage
    @property
    def optuna_study_prefix(self): return self.optuna.study_prefix
    @property
    def best_params_files(self): return self.optuna.best_params_files
    @property
    def reuse_best_params(self): return self.optuna.reuse_best_params

    @property
    def ft_role(self): return self.ft.role
    @property
    def ft_feature_prefix(self): return self.ft.feature_prefix
    @property
    def ft_num_numeric_tokens(self): return self.ft.num_numeric_tokens

    @classmethod
    def from_legacy_dict(cls, d: Dict[str, Any]) -> 'BayesOptConfig':
        """Map flat dictionary to nested Pydantic structure."""
        data = DataConfig(
            resp_nme=d.get('resp_nme'),
            weight_nme=d.get('weight_nme'),
            factor_nmes=d.get('factor_nmes', []),
            cate_list=d.get('cate_list'),
            binary_resp_nme=d.get('binary_resp_nme'),
            task_type=d.get('task_type', 'regression'),
            prop_test=d.get('prop_test', 0.25),
            rand_seed=d.get('rand_seed')
        )
        
        dist = DistributedConfig(
            use_gpu=d.get('use_gpu', True),
            use_resn_data_parallel=d.get('use_resn_data_parallel', False),
            use_ft_data_parallel=d.get('use_ft_data_parallel', False),
            use_gnn_data_parallel=d.get('use_gnn_data_parallel', False),
            use_resn_ddp=d.get('use_resn_ddp', False),
            use_ft_ddp=d.get('use_ft_ddp', False),
            use_gnn_ddp=d.get('use_gnn_ddp', False),
        )

        gnn = GNNConfig(
            use_approx_knn=d.get('gnn_use_approx_knn', True),
            approx_knn_threshold=d.get('gnn_approx_knn_threshold', 50000),
            graph_cache=d.get('gnn_graph_cache'),
            max_gpu_knn_nodes=d.get('gnn_max_gpu_knn_nodes', 200000),
            knn_gpu_mem_ratio=d.get('gnn_knn_gpu_mem_ratio', 0.9),
            knn_gpu_mem_overhead=d.get('gnn_knn_gpu_mem_overhead', 2.0),
        )
        
        region = RegionConfig(
            province_col=d.get('region_province_col'),
            city_col=d.get('region_city_col'),
            effect_alpha=d.get('region_effect_alpha', 50.0)
        )
        
        geo = GeoTokenConfig(
            feature_nmes=d.get('geo_feature_nmes'),
            hidden_dim=d.get('geo_token_hidden_dim', 32),
            layers=d.get('geo_token_layers', 2),
            dropout=d.get('geo_token_dropout', 0.1),
            k_neighbors=d.get('geo_token_k_neighbors', 10),
            learning_rate=d.get('geo_token_learning_rate', 1e-3),
            epochs=d.get('geo_token_epochs', 50)
        )
        
        optuna = OptunaConfig(
            storage=d.get('optuna_storage'),
            study_prefix=d.get('optuna_study_prefix'),
            best_params_files=d.get('best_params_files'),
            reuse_best_params=d.get('reuse_best_params', False)
        )
        
        ft = FTConfig(
            role=d.get('ft_role', 'model'),
            feature_prefix=d.get('ft_feature_prefix', 'ft_emb'),
            num_numeric_tokens=d.get('ft_num_numeric_tokens')
        )
        
        return cls(
            data=data,
            model_nme=d.get('model_nme', 'model'),
            epochs=d.get('epochs', 100),
            xgb_max_depth_max=d.get('xgb_max_depth_max', 25),
            xgb_n_estimators_max=d.get('xgb_n_estimators_max', 500),
            resn_weight_decay=d.get('resn_weight_decay', 1e-4),
            dist=dist,
            gnn=gnn,
            region=region,
            geo=geo,
            optuna=optuna,
            ft=ft,
            output_dir=d.get('output_dir'),
            final_ensemble=d.get('final_ensemble', False),
            final_ensemble_k=d.get('final_ensemble_k', 3),
            final_refit=d.get('final_refit', True)
        )
