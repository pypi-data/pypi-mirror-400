from __future__ import annotations
import numpy as np

from .base import BaseModel

from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
)


try:
    import lightgbm as lgb

    class LightGBMRegressorModel(BaseModel):
        name = "LightGBMRegressor"
        task_type = "regression"

        def __init__(self):
            self.model = lgb.LGBMRegressor(
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
    LightGBMRegressorModel = None


try:
    import xgboost as xgb

    class XGBoostRegressorModel(BaseModel):
        name = "XGBoostRegressor"
        task_type = "regression"

        def __init__(self):
            self.model = xgb.XGBRegressor(
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
    XGBoostRegressorModel = None


try:
    from catboost import CatBoostRegressor

    class CatBoostRegressorModel(BaseModel):
        name = "CatBoostRegressor"
        task_type = "regression"

        def __init__(self):
            self.model = CatBoostRegressor(
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
    CatBoostRegressorModel = None


class RandomForestRegressorModel(BaseModel):
    name = "RandomForestRegressor"
    task_type = "regression"

    def __init__(self):
        self.model = RandomForestRegressor(
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


class ExtraTreesRegressorModel(BaseModel):
    name = "ExtraTreesRegressor"
    task_type = "regression"

    def __init__(self):
        self.model = ExtraTreesRegressor(
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
