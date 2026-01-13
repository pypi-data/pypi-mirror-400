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

    class TorchTabularClassifierBase(BaseModel):
        task_type = "classification"
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


    class MLPClassifierModel(TorchTabularClassifierBase):
        name = "MLPClassifier"

        def fit(self, X, y):
            _log_dl_defaults(self.name)

            data_cfg, trainer_cfg, optim_cfg = self._build_common()
            model_cfg = CategoryEmbeddingModelConfig(
                task="classification",
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


    class FTTransformerClassifierModel(TorchTabularClassifierBase):
        name = "FTTransformerClassifier"

        def fit(self, X, y):
            _log_dl_defaults(self.name)

            data_cfg, trainer_cfg, optim_cfg = self._build_common()
            model_cfg = FTTransformerConfig(
                task="classification",
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


    class TabTransformerClassifierModel(TorchTabularClassifierBase):
        name = "TabTransformerClassifier"

        def fit(self, X, y):
            _log_dl_defaults(self.name)

            data_cfg, trainer_cfg, optim_cfg = self._build_common()
            model_cfg = TabTransformerConfig(task="classification")

            self.model = TabularModel(
                data_config=data_cfg,
                model_config=model_cfg,
                trainer_config=trainer_cfg,
                optimizer_config=optim_cfg,
            )
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)


    class SAINTClassifierModel(TorchTabularClassifierBase):
        name = "SAINTClassifier"

        def fit(self, X, y):
            _log_dl_defaults(self.name)

            data_cfg, trainer_cfg, optim_cfg = self._build_common()
            model_cfg = SAINTConfig(task="classification")

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
    MLPClassifierModel = None
    FTTransformerClassifierModel = None
    TabTransformerClassifierModel = None
    SAINTClassifierModel = None


try:
    from pytorch_tabnet.tab_model import TabNetClassifier

    class TabNetClassifierModel(BaseModel):
        name = "TabNetClassifier"
        task_type = "classification"
        group = "deep_tabular"

        def fit(self, X, y):
            _log_dl_defaults(self.name)

            self.model = TabNetClassifier(
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
    TabNetClassifierModel = None


try:
    from node.models import NodeClassifier

    class NODEClassifierModel(BaseModel):
        name = "NODEClassifier"
        task_type = "classification"
        group = "deep_tabular"

        def fit(self, X, y):
            _log_dl_defaults(self.name)
            self.model = NodeClassifier()
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)

        def warmup(self, X):
            _ = self.predict(X[:1])

except ImportError:
    NODEClassifierModel = None


try:
    from interpret.glassbox import ExplainableBoostingClassifier

    class NAMClassifierModel(BaseModel):
        name = "NAMClassifier"
        task_type = "classification"
        group = "deep_tabular"

        def fit(self, X, y):
            _log_dl_defaults(self.name)
            self.model = ExplainableBoostingClassifier()
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)

        def warmup(self, X):
            _ = self.predict(X[:1])

except ImportError:
    NAMClassifierModel = None


try:
    from grownet import GrowNetClassifier

    class GrowNetClassifierModel(BaseModel):
        name = "GrowNetClassifier"
        task_type = "classification"
        group = "deep_tabular"

        def fit(self, X, y):
            _log_dl_defaults(self.name)
            self.model = GrowNetClassifier()
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)

        def warmup(self, X):
            _ = self.predict(X[:1])

except ImportError:
    GrowNetClassifierModel = None


try:
    from pynca import NCAModel

    class ModernNCAClassifierModel(BaseModel):
        name = "ModernNCA"
        task_type = "classification"
        group = "deep_tabular"

        def fit(self, X, y):
            _log_dl_defaults(self.name)
            self.model = NCAModel()
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)

        def warmup(self, X):
            _ = self.predict(X[:1])

except ImportError:
    ModernNCAClassifierModel = None
