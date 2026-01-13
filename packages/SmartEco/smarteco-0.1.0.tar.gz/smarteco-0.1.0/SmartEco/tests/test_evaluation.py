import numpy as np
from sklearn.linear_model import LogisticRegression

from SmartEco.SmartML.model_evaluation import evaluate_model

class DummyModel:
    def fit(self, X, y): pass
    def predict(self, X): return np.zeros(len(X))

def test_evaluate_classification_metrics():
    X = np.random.randn(20, 3)
    y = np.random.randint(0, 2, size=20)

    model = DummyModel()

    metrics = evaluate_model(
        model=model,
        X_test=X,
        y_test=y,
        task="classification",
        train_time_s=0.1,
    )

    assert "accuracy" in metrics
    assert "macro_f1" in metrics
    assert metrics["train_time_s"] >= 0
