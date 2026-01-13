from __future__ import annotations
import numpy as np

from .base import BaseModel

try:
    from smart_knn import SmartKNN
    HAS_SMARTKNN = True
except ImportError:
    HAS_SMARTKNN = False


class SmartKNNClassifierModel(BaseModel):
    name = "SmartKNNClassifier"
    task_type = "classification"

    def __init__(self):
        if not HAS_SMARTKNN:
            raise ImportError("smart_knn not installed or not in PYTHONPATH")

        self.model = SmartKNN(
            k=5,
            backend="auto",
            weight_threshold=0.0,
            force_classification=True,
        )

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def warmup(self, X: np.ndarray):
        _ = self.predict(X[:1])


class SmartKNNRegressorModel(BaseModel):
    name = "SmartKNNRegressor"
    task_type = "regression"

    def __init__(self):
        if not HAS_SMARTKNN:
            raise ImportError("smart_knn not installed or not in PYTHONPATH")

        self.model = SmartKNN(
            k=5,
            backend="auto",
            weight_threshold=0.0,
            force_classification=False,
        )

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def warmup(self, X: np.ndarray):
        _ = self.predict(X[:1])
