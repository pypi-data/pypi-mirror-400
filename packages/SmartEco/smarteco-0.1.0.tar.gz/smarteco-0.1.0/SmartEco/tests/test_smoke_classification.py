import pandas as pd
import numpy as np

from SmartEco.SmartML.model_training import run_training

def test_smoke_classification():
    # tiny synthetic dataset
    X = pd.DataFrame({
        "a": np.random.randn(50),
        "b": np.random.randn(50),
    })
    y = pd.Series(np.random.randint(0, 2, size=50))

    results = run_training(
        X_df=X,
        y_ser=y,
        task="classification",
        models=["logistic"],
    )

    assert not results.empty
    assert "accuracy" in results.columns
