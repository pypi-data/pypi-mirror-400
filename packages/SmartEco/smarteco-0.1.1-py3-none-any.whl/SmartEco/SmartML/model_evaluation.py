from __future__ import annotations

import time
import numpy as np

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    r2_score,
    mean_squared_error,
)


def _ensure_1d(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y)
    if y.ndim > 1:
        y = y.reshape(-1)
    return y


def _ensure_labels(y_pred: np.ndarray) -> np.ndarray:
    y_pred = np.asarray(y_pred)
    if y_pred.ndim > 1:
        return y_pred.argmax(axis=1)
    return y_pred


def evaluate_classification(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> dict:
    y_true = _ensure_1d(y_true)
    y_pred = _ensure_1d(_ensure_labels(y_pred))

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
    }


def evaluate_regression(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> dict:
    y_true = _ensure_1d(y_true)
    y_pred = _ensure_1d(y_pred)

    return {
        "r2": float(r2_score(y_true, y_pred)),
        "mse": float(mean_squared_error(y_true, y_pred)),
    }


def measure_batch_inference(model, X: np.ndarray) -> float:
    if X is None or len(X) == 0:
        return 0.0

    _ = model.predict(X[: min(8, len(X))])

    t0 = time.perf_counter()
    _ = model.predict(X)
    return time.perf_counter() - t0


def measure_single_inference(
    model,
    X: np.ndarray,
    n_runs: int = 200,
    seed: int = 42,
) -> dict:
    if X is None or len(X) == 0:
        return {
            "single_mean_ms": 0.0,
            "single_p95_ms": 0.0,
        }

    rng = np.random.default_rng(seed)
    latencies = np.empty(n_runs, dtype=np.float64)

    _ = model.predict(X[:1])

    for i in range(n_runs):
        idx = rng.integers(0, len(X))
        x = X[idx].reshape(1, -1)

        t0 = time.perf_counter()
        _ = model.predict(x)
        latencies[i] = (time.perf_counter() - t0) * 1000.0

    return {
        "single_mean_ms": float(latencies.mean()),
        "single_p95_ms": float(np.percentile(latencies, 95)),
    }


def evaluate_model(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    task: str,
    train_time_s: float,
) -> dict:

    y_pred = model.predict(X_test)

    if task == "classification":
        metrics = evaluate_classification(y_test, y_pred)
    elif task == "regression":
        metrics = evaluate_regression(y_test, y_pred)
    else:
        raise ValueError(f"Unknown task type: {task}")

    batch_time_s = measure_batch_inference(model, X_test)
    single_latency = measure_single_inference(model, X_test)

    results = {
        "train_time_s": float(train_time_s),
        "batch_inference_s": float(batch_time_s),
        "batch_samples": int(len(X_test)),
        "batch_throughput": float(len(X_test) / batch_time_s)
        if batch_time_s > 0 else np.inf,
    }

    results.update(metrics)
    results.update(single_latency)

    return results
