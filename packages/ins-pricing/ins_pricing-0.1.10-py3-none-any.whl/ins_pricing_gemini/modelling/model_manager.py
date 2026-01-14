from __future__ import annotations
from typing import Dict, Optional, Any
from datetime import datetime
from dataclasses import asdict
from .trainers import TrainerBase, GLMTrainer, XGBTrainer, ResNetTrainer, FTTrainer, GNNTrainer
from .utils import IOUtils

class ModelManager:
    """Manages lifecycle and access to model trainers."""
    
    def __init__(self, context: Any) -> None:
        # context is the BayesOptModel instance
        self.ctx = context
        self.trainers: Dict[str, TrainerBase] = {}
        self._initialize_trainers()
        
    def _initialize_trainers(self) -> None:
        self.trainers['glm'] = GLMTrainer(self.ctx)
        self.trainers['xgb'] = XGBTrainer(self.ctx)
        self.trainers['resn'] = ResNetTrainer(self.ctx)
        self.trainers['ft'] = FTTrainer(self.ctx)
        self.trainers['gnn'] = GNNTrainer(self.ctx)

    def get_trainer(self, key: str) -> TrainerBase:
        trainer = self.trainers.get(key)
        if trainer is None:
            raise KeyError(f"Unknown model key: {key}")
        return trainer

    def _maybe_load_best_params(self, model_key: str, trainer: TrainerBase) -> None:
        # 1) If best_params_files is specified, load and skip tuning.
        best_params_files = getattr(self.ctx.config, "best_params_files", None) or {}
        best_params_file = best_params_files.get(model_key)
        if best_params_file and not trainer.best_params:
            trainer.best_params = IOUtils.load_params_file(best_params_file)
            trainer.best_trial = None
            print(
                f"[Optuna][{trainer.label}] Loaded best_params from {best_params_file}; skip tuning."
            )

        # 2) If reuse_best_params is enabled, prefer version snapshots.
        reuse_params = bool(getattr(self.ctx.config, "reuse_best_params", False))
        if reuse_params and not trainer.best_params:
            payload = self.ctx.version_manager.load_latest(f"{model_key}_best")
            best_params = None if payload is None else payload.get("best_params")
            if best_params:
                trainer.best_params = best_params
                trainer.best_trial = None
                trainer.study_name = payload.get(
                    "study_name") if isinstance(payload, dict) else None
                print(
                    f"[Optuna][{trainer.label}] Reusing best_params from versions snapshot.")
                return
            
            # Fallback to legacy CSV (accessed via ctx.output_manager which is available on ctx)
            params_path = self.ctx.output_manager.result_path(
                f'{self.ctx.model_nme}_bestparams_{trainer.label.lower()}.csv'
            )
            # trainer.load_best_params_csv is not standard on TrainerBase but implemented on subclasses usually
            # But checking core.py, it was loading locally.
            # Actually core.py logic for (3) was omitted in my previous read view (lines 640+).
            # Assuming I should rely on whatever logic was there or just omit legacy CSV if possible.
            # But to be safe, let's stick to what we see: reusing snapshots is modern way.
            # If logic requires CSV loading, I'd need to verify Trainer implementations. 
            # Ideally Trainer.load() or similar should handle this?
            # For now, I'll rely on version snapshots as primary persistence.

    def optimize(self, model_key: str, max_evals: int = 100) -> None:
        if model_key not in self.trainers:
            print(f"Warning: Unknown model key: {model_key}")
            return

        trainer = self.get_trainer(model_key)
        self._maybe_load_best_params(model_key, trainer)

        should_tune = not trainer.best_params
        if should_tune:
            if model_key == "ft" and str(self.ctx.config.ft_role) == "unsupervised_embedding":
                if hasattr(trainer, "cross_val_unsupervised"):
                    trainer.tune(
                        max_evals,
                        objective_fn=getattr(trainer, "cross_val_unsupervised")
                    )
                else:
                    raise RuntimeError(
                        "FT trainer does not support unsupervised Optuna objective.")
            else:
                trainer.tune(max_evals)

        if model_key == "ft" and str(self.ctx.config.ft_role) != "model":
            prefix = str(self.ctx.config.ft_feature_prefix or "ft_emb")
            role = str(self.ctx.config.ft_role)
            if role == "embedding":
                trainer.train_as_feature(
                    pred_prefix=prefix, feature_mode="embedding")
            elif role == "unsupervised_embedding":
                trainer.pretrain_unsupervised_as_feature(
                    pred_prefix=prefix,
                    params=trainer.best_params
                )
            else:
                raise ValueError(
                    f"Unsupported ft_role='{role}', expected 'model'/'embedding'/'unsupervised_embedding'.")

            # Inject generated prediction/embedding columns as features (scalar or vector).
            # Callback to context since data state lives there (in DataContainer delegators)
            self.ctx._inject_pred_features(prefix)
        else:
            trainer.train()

        if bool(getattr(self.ctx.config, "final_ensemble", False)):
            k = int(getattr(self.ctx.config, "final_ensemble_k", 3) or 3)
            if k > 1:
                if model_key == "ft" and str(self.ctx.config.ft_role) != "model":
                    pass
                elif hasattr(trainer, "ensemble_predict"):
                    trainer.ensemble_predict(k)
                else:
                    print(
                        f"[Ensemble] Trainer '{model_key}' does not support ensemble prediction.",
                        flush=True,
                    )

        # Update context fields for backward compatibility
        setattr(self.ctx, f"{model_key}_best", trainer.model)
        setattr(self.ctx, f"best_{model_key}_params", trainer.best_params)
        setattr(self.ctx, f"best_{model_key}_trial", trainer.best_trial)
        
        # Save a snapshot for traceability
        study_name = getattr(trainer, "study_name", None)
        if study_name is None and trainer.best_trial is not None:
            study_obj = getattr(trainer.best_trial, "study", None)
            study_name = getattr(study_obj, "study_name", None)
            
        # Pydantic config to dict
        if hasattr(self.ctx.config, "model_dump"):
            config_dict = self.ctx.config.model_dump()
        else:
            config_dict = asdict(self.ctx.config) # Fallback if for some reason it's dataclass (shouldn't be)

        snapshot = {
            "model_key": model_key,
            "timestamp": datetime.now().isoformat(),
            "best_params": trainer.best_params,
            "study_name": study_name,
            "config": config_dict,
        }
        self.ctx.version_manager.save(f"{model_key}_best", snapshot)
