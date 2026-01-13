from __future__ import annotations

import logging
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split

TEST_SIZE = 0.2
RANDOM_STATE = 42


logger = logging.getLogger("SmartML.Split")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(levelname)s] %(name)s :: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _as_series(y) -> pd.Series:
    if isinstance(y, pd.Series):
        return y
    if isinstance(y, np.ndarray):
        return pd.Series(y)
    raise TypeError("y must be a pandas Series or numpy array")


def _can_stratify(y: pd.Series) -> bool:
    vc = y.value_counts(dropna=False)
    return vc.min() >= 2


def split_classification(
    X: pd.DataFrame,
    y,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
):
    if not isinstance(X, pd.DataFrame):
        raise TypeError("X must be a pandas DataFrame")

    y = _as_series(y)

    stratify = y if _can_stratify(y) else None
    if stratify is None:
        logger.warning(
            "Stratified split disabled (some classes have <2 samples)"
        )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        stratify=stratify,
        random_state=random_state,
        shuffle=True,
    )

    logger.info(
        f"Classification split: "
        f"train={len(X_train)} test={len(X_test)} "
        f"test_size={test_size}"
    )

    if stratify is not None:
        logger.info(
            f"Train class distribution:\n{y_train.value_counts(normalize=True)}"
        )

    return X_train, X_test, y_train, y_test


def split_regression(
    X: pd.DataFrame,
    y,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
):
    if not isinstance(X, pd.DataFrame):
        raise TypeError("X must be a pandas DataFrame")

    y = _as_series(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        shuffle=True,
    )

    logger.info(
        f"Regression split: "
        f"train={len(X_train)} test={len(X_test)} "
        f"test_size={test_size}"
    )

    return X_train, X_test, y_train, y_test


def split_info(X_train, X_test) -> dict:
    n_total = len(X_train) + len(X_test)

    info = {
        "n_total": n_total,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "train_ratio": len(X_train) / n_total,
        "test_ratio": len(X_test) / n_total,
    }

    logger.info(f"Split info: {info}")
    return info
