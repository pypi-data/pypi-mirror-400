import pandas as pd
import numpy as np

from SmartEco.SmartML.model_splitting import split_classification, split_regression

def test_split_classification():
    X = pd.DataFrame(np.random.randn(100, 3))
    y = pd.Series([0, 1] * 50)

    Xtr, Xte, ytr, yte = split_classification(X, y, test_size=0.2)

    assert len(Xtr) + len(Xte) == 100
    assert set(Xtr.index).isdisjoint(set(Xte.index))

def test_split_regression():
    X = pd.DataFrame(np.random.randn(100, 3))
    y = pd.Series(np.random.randn(100))

    Xtr, Xte, ytr, yte = split_regression(X, y)

    assert len(Xtr) + len(Xte) == 100
