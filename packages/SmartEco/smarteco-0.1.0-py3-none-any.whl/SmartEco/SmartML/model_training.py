from __future__ import annotations


import warnings

warnings.filterwarnings(
    "ignore",
    message="X does not have valid feature names",
    category=UserWarning,
)

warnings.filterwarnings("ignore", category=FutureWarning)


import time
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split

from .smarteco_encoding import encode_features, encode_target
from .model_evaluation import evaluate_model
from .models.registry import get_model, list_models


SEED = 42
TEST_SIZE = 0.2

np.random.seed(SEED)



logger = logging.getLogger("SmartML.Runner")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(levelname)s] %(name)s :: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _can_stratify(y: pd.Series) -> bool:
    return y.value_counts(dropna=False).min() >= 2


def load_dataset(
    *,
    csv_path: str | None = None,
    openml_id: int | None = None,
    target: str,
    subset: int | None = None,
):
    if csv_path:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded CSV dataset: {csv_path}")

    elif openml_id is not None:
        import openml
        ds = openml.datasets.get_dataset(openml_id)
        df, *_ = ds.get_data(dataset_format="dataframe")
        logger.info(f"Loaded OpenML dataset id={openml_id}")

        if target is None:
            target = ds.default_target_attribute

    else:
        raise ValueError("Provide either csv_path or openml_id")

    if target not in df.columns:
        raise KeyError(f"Target column '{target}' not found")

    if subset and len(df) > subset:
        df = df.sample(
            n=subset,
            random_state=SEED,
            replace=False,
        ).reset_index(drop=True)
        logger.info(f"Subsampled dataset to {subset} rows")

    X = df.drop(columns=[target])
    y = df[target]

    logger.info(f"Dataset shape: X={X.shape}, y={y.shape}")
    return X, y



def run_training(
    *,
    X_df: pd.DataFrame,
    y_ser: pd.Series,
    task: str,
    models: list[str] | None = None,
    exclude: list[str] | None = None,
    output_csv: str | None = None,
):
    if task not in {"classification", "regression"}:
        raise ValueError(f"Invalid task: {task}")

    stratify = y_ser if task == "classification" and _can_stratify(y_ser) else None
    if task == "classification" and stratify is None:
        logger.warning("Stratified split disabled (class imbalance / small classes)")

    idx = np.arange(len(X_df))

    train_idx, test_idx = train_test_split(
        idx,
        test_size=TEST_SIZE,
        random_state=SEED,
        stratify=stratify,
        shuffle=True,
    )

    X_train_df = X_df.iloc[train_idx]
    X_test_df = X_df.iloc[test_idx]
    y_train_ser = y_ser.iloc[train_idx]
    y_test_ser = y_ser.iloc[test_idx]

    logger.info(f"Split: train={len(X_train_df)} test={len(X_test_df)}")

 
    encoder, X_train_np, X_test_np = encode_features(
        X_train_df,
        X_test_df,
        y_train_ser,
    )

    y_train_np, y_test_np = encode_target(
        y_train_ser,
        y_test_ser,
        task=task,
    )

    logger.info(
        f"Encoded shapes: X_train={X_train_np.shape}, X_test={X_test_np.shape}"
    )


    del X_df, y_ser, X_train_df, X_test_df, y_train_ser, y_test_ser

    model_names = list_models(task) if models is None else models

    if exclude:
        model_names = [m for m in model_names if m not in exclude]

    if not model_names:
        raise RuntimeError("No models selected for run")

    logger.info(f"Models selected ({len(model_names)}): {model_names}")

    rows = []

    for model_name in model_names:
        logger.info(f"Running model: {model_name}")

        model = get_model(task, model_name)

        t0 = time.perf_counter()
        model.fit(X_train_np, y_train_np)
        train_time = time.perf_counter() - t0

        if hasattr(model, "warmup"):
            model.warmup(X_train_np)

        metrics = evaluate_model(
            model=model,
            X_test=X_test_np,
            y_test=y_test_np,
            task=task,
            train_time_s=train_time,
        )

        rows.append({"model": model_name, **metrics})

    results_df = pd.DataFrame(rows)

 
    if output_csv:
        out = Path(output_csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        results_df.to_csv(out, index=False)
        logger.info(f"Results saved to {out}")

    return results_df


if __name__ == "__main__":
    X, y = load_dataset(
        csv_path="data/dataset.csv",
        target="label",
    )

    results = run_training(
        X_df=X,
        y_ser=y,
        task="classification",
        exclude=["svr"],
        output_csv="results/benchmark.csv",
    )

    sort_col = "macro_f1" if "macro_f1" in results.columns else "r2"
    print(
    results
    .sort_values(sort_col, ascending=False)
    .reset_index(drop=True)
)

