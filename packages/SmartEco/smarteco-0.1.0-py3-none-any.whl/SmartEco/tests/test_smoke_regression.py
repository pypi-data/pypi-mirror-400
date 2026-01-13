import pandas as pd
import numpy as np

from SmartEco.SmartML.model_training import run_training

def test_smoke_regression():
    X = pd.DataFrame({
        "a": np.random.randn(50),
        "b": np.random.randn(50),
    })
    y = pd.Series(np.random.randn(50))

    results = run_training(
        X_df=X,
        y_ser=y,
        task="regression",
        models=["linear"],
    )

    assert not results.empty
    assert "r2" in results.columns
