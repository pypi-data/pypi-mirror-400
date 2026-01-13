from __future__ import annotations
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

from .base import BaseModel

class _ScaledModel:
    def _fit_scaler(self, X):
        self.scaler = StandardScaler()
        return self.scaler.fit_transform(X)

    def _transform(self, X):
        return self.scaler.transform(X)


class LogisticModel(BaseModel, _ScaledModel):
    name = "LogisticRegression"
    task_type = "classification"

    def fit(self, X, y):
        Xs = self._fit_scaler(X)
        self.model = LogisticRegression(
            max_iter=1000,
            n_jobs=-1,
        )
        self.model.fit(Xs, y)

    def predict(self, X):
        return self.model.predict(self._transform(X))


class SVCModel(BaseModel, _ScaledModel):
    name = "SVC"
    task_type = "classification"

    def fit(self, X, y):
        Xs = self._fit_scaler(X)
        self.model = SVC()  
        self.model.fit(Xs, y)

    def predict(self, X):
        return self.model.predict(self._transform(X))


class KNNClassifierModel(BaseModel, _ScaledModel):
    name = "KNNClassifier"
    task_type = "classification"

    def fit(self, X, y):
        Xs = self._fit_scaler(X)
        self.model = KNeighborsClassifier(n_neighbors=5)
        self.model.fit(Xs, y)

    def predict(self, X):
        return self.model.predict(self._transform(X))


class NaiveBayesModel(BaseModel):
    name = "NaiveBayes"
    task_type = "classification"

    def fit(self, X, y):
        self.model = GaussianNB()
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)
