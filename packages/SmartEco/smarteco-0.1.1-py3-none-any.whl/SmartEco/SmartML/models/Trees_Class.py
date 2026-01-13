from __future__ import annotations
import numpy as np

from .base import BaseModel

from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
)


try:
    import lightgbm as lgb

    class LightGBMClassifierModel(BaseModel):
        name = "LightGBMClassifier"
        task_type = "classification"

        def __init__(self):
            self.model = lgb.LGBMClassifier(
                n_estimators=100,
                n_jobs=-1,
                random_state=42,
                verbosity=-1,
            )

        def fit(self, X, y):
            self.model.fit(np.asarray(X), np.asarray(y))

        def predict(self, X):
            return self.model.predict(np.asarray(X))

        def warmup(self, X):
            _ = self.predict(X[:1])

except ImportError:
    LightGBMClassifierModel = None

try:
    import xgboost as xgb

    class XGBoostClassifierModel(BaseModel):
        name = "XGBoostClassifier"
        task_type = "classification"

        def __init__(self):
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                n_jobs=-1,
                random_state=42,
                verbosity=0,
                tree_method="hist",
            )

        def fit(self, X, y):
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)

        def warmup(self, X):
            _ = self.predict(X[:1])

except ImportError:
    XGBoostClassifierModel = None


try:
    from catboost import CatBoostClassifier

    class CatBoostClassifierModel(BaseModel):
        name = "CatBoostClassifier"
        task_type = "classification"

        def __init__(self):
            self.model = CatBoostClassifier(
                iterations=100,
                verbose=False,
                random_seed=42,
            )

        def fit(self, X, y):
            self.model.fit(X, y)

        def predict(self, X):
            return self.model.predict(X)

        def warmup(self, X):
            _ = self.predict(X[:1])

except ImportError:
    CatBoostClassifierModel = None

class RandomForestClassifierModel(BaseModel):
    name = "RandomForestClassifier"
    task_type = "classification"

    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            n_jobs=-1,
            random_state=42,
        )

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def warmup(self, X):
        _ = self.predict(X[:1])


# ============================================================
# ExtraTrees
# ============================================================

class ExtraTreesClassifierModel(BaseModel):
    name = "ExtraTreesClassifier"
    task_type = "classification"

    def __init__(self):
        self.model = ExtraTreesClassifier(
            n_estimators=100,
            n_jobs=-1,
            random_state=42,
        )

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def warmup(self, X):
        _ = self.predict(X[:1])
