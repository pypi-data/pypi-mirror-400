from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np


class BaseModel(ABC):

    name: str = "BaseModel"
    task_type: str  

    def __init__(self):
        self.model = None

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray):
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        pass

    def warmup(self, X: np.ndarray):
        
        if X is None or len(X) == 0:
            return
        _ = self.predict(X[:1])
