from __future__ import annotations
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso,
    ElasticNet,
)
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor

from .base import BaseModel


class _ScaledModel:
    def _fit_scaler(self, X):
        self.scaler = StandardScaler()
        return self.scaler.fit_transform(X)

    def _transform(self, X):
        return self.scaler.transform(X)


class LinearRegModel(BaseModel, _ScaledModel):
    name = "LinearRegression"
    task_type = "regression"

    def fit(self, X, y):
        Xs = self._fit_scaler(X)
        self.model = LinearRegression()
        self.model.fit(Xs, y)

    def predict(self, X):
        return self.model.predict(self._transform(X))


class RidgeModel(BaseModel, _ScaledModel):
    name = "Ridge"
    task_type = "regression"

    def fit(self, X, y):
        Xs = self._fit_scaler(X)
        self.model = Ridge()
        self.model.fit(Xs, y)

    def predict(self, X):
        return self.model.predict(self._transform(X))


class LassoModel(BaseModel, _ScaledModel):
    name = "Lasso"
    task_type = "regression"

    def fit(self, X, y):
        Xs = self._fit_scaler(X)
        self.model = Lasso()
        self.model.fit(Xs, y)

    def predict(self, X):
        return self.model.predict(self._transform(X))


class ElasticNetModel(BaseModel, _ScaledModel):
    name = "ElasticNet"
    task_type = "regression"

    def fit(self, X, y):
        Xs = self._fit_scaler(X)
        self.model = ElasticNet()
        self.model.fit(Xs, y)

    def predict(self, X):
        return self.model.predict(self._transform(X))


class SVRModel(BaseModel, _ScaledModel):
    name = "SVR"
    task_type = "regression"

    def fit(self, X, y):
        Xs = self._fit_scaler(X)
        self.model = SVR()
        self.model.fit(Xs, y)

    def predict(self, X):
        return self.model.predict(self._transform(X))


class KNNRegressorModel(BaseModel, _ScaledModel):
    name = "KNNRegressor"
    task_type = "regression"

    def fit(self, X, y):
        Xs = self._fit_scaler(X)
        self.model = KNeighborsRegressor(n_neighbors=5)
        self.model.fit(Xs, y)

    def predict(self, X):
        return self.model.predict(self._transform(X))
