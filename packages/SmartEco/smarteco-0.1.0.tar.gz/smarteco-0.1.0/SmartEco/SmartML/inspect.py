from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .models.registry import (
    CLASSIFICATION_MODELS,
    REGRESSION_MODELS,
)


def _format_models(models: dict) -> list[str]:

    formatted = []
    for idx, name in enumerate(sorted(models.keys()), start=1):
        formatted.append(f"{idx}. {name.upper()}")
    return formatted


def SmartML_Inspect(output: str = "smartml_inspect.json") -> None:

    report = {
        "library": "SmartML",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "models": {
            "classification": _format_models(CLASSIFICATION_MODELS),
            "regression": _format_models(REGRESSION_MODELS),
        },
        "metrics": {
            "classification": [
                "ACCURACY",
                "MACRO_F1",
            ],
            "regression": [
                "R2",
                "MSE",
            ],
            "inference": [
                "TRAIN_TIME_S",
                "BATCH_INFERENCE_S",
                "BATCH_THROUGHPUT",
                "SINGLE_MEAN_MS",
                "SINGLE_P95_MS",
            ],
        },
    }

    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
