from __future__ import annotations

import logging
import numpy as np
import pandas as pd
import sklearn

from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

try:
    from category_encoders.target_encoder import TargetEncoder
    HAS_TARGET_ENCODER = True
except ImportError:
    HAS_TARGET_ENCODER = False


LOW_CARD_THRESHOLD = 10
MAX_OHE_CAT_COLS = 10
MAX_OHE_TOTAL_UNIQUES = 100  
NUM_IMPUTE_STRATEGY = "median"
CAT_IMPUTE_STRATEGY = "most_frequent"

logger = logging.getLogger("SmartML.Encoder")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(levelname)s] %(name)s :: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _detect_column_types(X: pd.DataFrame):
    cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    num_cols = X.select_dtypes(include=["number"]).columns.tolist()
    return num_cols, cat_cols


def _split_categorical_by_cardinality(X: pd.DataFrame, cat_cols):
    low_card, high_card = [], []

    for col in cat_cols:
        n_unique = X[col].nunique(dropna=True)
        if n_unique <= LOW_CARD_THRESHOLD:
            low_card.append(col)
        else:
            high_card.append(col)

    return low_card, high_card


def _make_one_hot_encoder():
    if sklearn.__version__ >= "1.2":
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    else:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


class TabularEncoder:
    def __init__(self):
        self.num_cols = []
        self.low_card_cols = []
        self.high_card_cols = []
        self.all_cat_cols = []
        self.label_encoder = None
        self.preprocessor = None
        self._fitted = False

    def fit(self, X: pd.DataFrame, y: pd.Series | None = None):
        if not isinstance(X, pd.DataFrame):
            raise TypeError("X must be a pandas DataFrame")

        self.num_cols, cat_cols = _detect_column_types(X)
        self.all_cat_cols = cat_cols

        logger.info(
            f"Detected {len(self.num_cols)} numeric and {len(cat_cols)} categorical columns"
        )

        transformers = []


        if self.num_cols:
            num_pipe = Pipeline([
                ("imputer", SimpleImputer(strategy=NUM_IMPUTE_STRATEGY)),
            ])
            transformers.append(("num", num_pipe, self.num_cols))


        if cat_cols:
            if not HAS_TARGET_ENCODER:
                raise ImportError(
                    "category_encoders required for categorical encoding.\n"
                    "Install via: pip install category-encoders"
                )
            if y is None:
                raise ValueError("Categorical encoding requires y during fit().")

            use_ohe = len(cat_cols) <= MAX_OHE_CAT_COLS
            self.low_card_cols, self.high_card_cols = _split_categorical_by_cardinality(X, cat_cols)

            total_low_uniques = sum(X[c].nunique(dropna=True) for c in self.low_card_cols)

            if use_ohe and total_low_uniques <= MAX_OHE_TOTAL_UNIQUES:
                if self.low_card_cols:
                    logger.info(f"Using OHE for low-cardinality columns: {self.low_card_cols}")
                    ohe = Pipeline([
                        ("imputer", SimpleImputer(strategy=CAT_IMPUTE_STRATEGY)),
                        ("ohe", _make_one_hot_encoder()),
                    ])
                    transformers.append(("low_card_cat", ohe, self.low_card_cols))

                if self.high_card_cols:
                    logger.info(f"Using TargetEncoder for high-cardinality columns: {self.high_card_cols}")
                    te = Pipeline([
                        ("imputer", SimpleImputer(strategy=CAT_IMPUTE_STRATEGY)),
                        ("te", TargetEncoder(smoothing=1.0, min_samples_leaf=1)),
                    ])
                    transformers.append(("high_card_cat", te, self.high_card_cols))
            else:
                logger.info("Using TargetEncoder for all categorical columns")
                self.low_card_cols = []
                self.high_card_cols = cat_cols

                te_all = Pipeline([
                    ("imputer", SimpleImputer(strategy=CAT_IMPUTE_STRATEGY)),
                    ("te", TargetEncoder(smoothing=1.0, min_samples_leaf=1)),
                ])
                transformers.append(("all_cat_te", te_all, cat_cols))

        self.preprocessor = ColumnTransformer(
            transformers=transformers,
            remainder="drop",
            sparse_threshold=0.0,
        )

        self.preprocessor.fit(X, y) if cat_cols else self.preprocessor.fit(X)
        self._fitted = True

        logger.info("TabularEncoder fitted successfully")
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Encoder must be fitted before transform()")
        Xt = self.preprocessor.transform(X)
        return np.asarray(Xt, dtype=np.float32)


    def fit_transform_y(self, y: pd.Series) -> np.ndarray:
        self.label_encoder = LabelEncoder()
        return self.label_encoder.fit_transform(y.astype(str))

    def transform_y(self, y: pd.Series) -> np.ndarray:
        if self.label_encoder is None:
            raise RuntimeError("LabelEncoder not fitted")
        return self.label_encoder.transform(y.astype(str))


    def get_feature_info(self) -> dict:
        return {
            "num_features": len(self.num_cols),
            "categorical_features": len(self.all_cat_cols),
            "ohe_used": bool(self.low_card_cols),
            "low_card_categorical": len(self.low_card_cols),
            "high_card_categorical": len(self.high_card_cols),
            "low_card_cols": self.low_card_cols,
            "high_card_cols": self.high_card_cols,
        }


def encode_features(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series | None = None,
):
    encoder = TabularEncoder()
    encoder.fit(X_train, y_train)

    Xtr = encoder.transform(X_train)
    Xte = encoder.transform(X_test)

    return encoder, Xtr, Xte


def encode_target(
    y_train: pd.Series,
    y_test: pd.Series,
    *,
    task: str,
):
    if task == "classification":
        le = LabelEncoder()
        y_train_np = le.fit_transform(y_train.astype(str))
        y_test_np = le.transform(y_test.astype(str))
        return y_train_np, y_test_np

    if task == "regression":
        return (
            y_train.to_numpy(dtype=np.float32),
            y_test.to_numpy(dtype=np.float32),
        )

    raise ValueError(f"Unknown task: {task}")
