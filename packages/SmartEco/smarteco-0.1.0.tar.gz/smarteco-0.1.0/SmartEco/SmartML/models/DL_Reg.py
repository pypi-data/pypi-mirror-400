from __future__ import annotations
import numpy as np
import logging

from .base import BaseModel


DEVICE = "cpu"
MAX_EPOCHS = 30        
SEED = 42

logger = logging.getLogger("SmartML.DeepModel")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(levelname)s] %(name)s :: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _log_dl_defaults(model_name: str):
    logger.info(
        f"{model_name} uses deep learning defaults | "
        f"device={DEVICE}, epochs={MAX_EPOCHS}, "
        f"deterministic=True (models are compute-heavy)"
    )



try:
    from torch_tabular import TabularModel
    from torch_tabular.config import DataConfig, TrainerConfig, OptimizerConfig
    from torch_tabular.models import (
        CategoryEmbeddingModelConfig,
        FTTransformerConfig,
        TabTransformerConfig,
        SAINTConfig,
    )

    class TorchTabularRegressorBase(BaseModel):
        task_type = "regression"
        group = "deep_tabular"

        def _build_common(self):
            return (
                DataConfig(
                    target=None,   
                    continuous_cols=None,
                    categorical_cols=None,
                ),
                TrainerConfig(
                    max_epochs=MAX_EPOCHS,
                    accelerator=DEVICE,
                    devices=1,
                    enable_progress_bar=False,
                    logger=False,
                    deterministic=True,
                ),
                OptimizerConfig(),
            )

        def warmup(self, X):
            _ = self.predict(X[:1])


    class MLPRegressorModel(TorchTabularRegressorBase):
        name = "MLPRegressor"

        def fit(self, X, y):
            _log_dl_defaults(self.name)

            data_cfg, trainer_cfg, optim_cfg = self._build_common()
            model_cfg = CategoryEmbeddingModelConfig(
                task="regression",
                layers="256-128",
                dropout=0.1,
            )

            self.model = TabularModel(
                data_config=data_cfg,
                model_config=model_cfg,
                trainer_config=trainer_cfg,
                optimizer_config=optim_cfg,
            )
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)


    class FTTransformerRegressorModel(TorchTabularRegressorBase):
        name = "FTTransformerRegressor"

        def fit(self, X, y):
            _log_dl_defaults(self.name)

            data_cfg, trainer_cfg, optim_cfg = self._build_common()
            model_cfg = FTTransformerConfig(
                task="regression",
                num_heads=8,
                hidden_dim=128,
            )

            self.model = TabularModel(
                data_config=data_cfg,
                model_config=model_cfg,
                trainer_config=trainer_cfg,
                optimizer_config=optim_cfg,
            )
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)


    class TabTransformerRegressorModel(TorchTabularRegressorBase):
        name = "TabTransformerRegressor"

        def fit(self, X, y):
            _log_dl_defaults(self.name)

            data_cfg, trainer_cfg, optim_cfg = self._build_common()
            model_cfg = TabTransformerConfig(task="regression")

            self.model = TabularModel(
                data_config=data_cfg,
                model_config=model_cfg,
                trainer_config=trainer_cfg,
                optimizer_config=optim_cfg,
            )
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)


    class SAINTRegressorModel(TorchTabularRegressorBase):
        name = "SAINTRegressor"

        def fit(self, X, y):
            _log_dl_defaults(self.name)

            data_cfg, trainer_cfg, optim_cfg = self._build_common()
            model_cfg = SAINTConfig(task="regression")

            self.model = TabularModel(
                data_config=data_cfg,
                model_config=model_cfg,
                trainer_config=trainer_cfg,
                optimizer_config=optim_cfg,
            )
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)

except ImportError:
    MLPRegressorModel = None
    FTTransformerRegressorModel = None
    TabTransformerRegressorModel = None
    SAINTRegressorModel = None


try:
    from pytorch_tabnet.tab_model import TabNetRegressor

    class TabNetRegressorModel(BaseModel):
        name = "TabNetRegressor"
        task_type = "regression"
        group = "deep_tabular"

        def fit(self, X, y):
            _log_dl_defaults(self.name)

            self.model = TabNetRegressor(
                n_steps=5,
                verbose=0,
                seed=SEED,
            )
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)

        def warmup(self, X):
            _ = self.predict(X[:1])

except ImportError:
    TabNetRegressorModel = None


try:
    from node.models import NodeRegressor

    class NODERegressorModel(BaseModel):
        name = "NODERegressor"
        task_type = "regression"
        group = "deep_tabular"

        def fit(self, X, y):
            _log_dl_defaults(self.name)
            self.model = NodeRegressor()
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)

        def warmup(self, X):
            _ = self.predict(X[:1])

except ImportError:
    NODERegressorModel = None


try:
    from interpret.glassbox import ExplainableBoostingRegressor

    class NAMRegressorModel(BaseModel):
        name = "NAMRegressor"
        task_type = "regression"
        group = "deep_tabular"

        def fit(self, X, y):
            _log_dl_defaults(self.name)
            self.model = ExplainableBoostingRegressor()
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)

        def warmup(self, X):
            _ = self.predict(X[:1])

except ImportError:
    NAMRegressorModel = None


try:
    from deepgbm import DeepGBM

    class DeepGBMRegressorModel(BaseModel):
        name = "DeepGBMRegressor"
        task_type = "regression"
        group = "deep_tabular"

        def fit(self, X, y):
            _log_dl_defaults(self.name)
            self.model = DeepGBM()
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)

        def warmup(self, X):
            _ = self.predict(X[:1])

except ImportError:
    DeepGBMRegressorModel = None


try:
    from grownet import GrowNetRegressor

    class GrowNetRegressorModel(BaseModel):
        name = "GrowNetRegressor"
        task_type = "regression"
        group = "deep_tabular"

        def fit(self, X, y):
            _log_dl_defaults(self.name)
            self.model = GrowNetRegressor()
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)

        def warmup(self, X):
            _ = self.predict(X[:1])

except ImportError:
    GrowNetRegressorModel = None
