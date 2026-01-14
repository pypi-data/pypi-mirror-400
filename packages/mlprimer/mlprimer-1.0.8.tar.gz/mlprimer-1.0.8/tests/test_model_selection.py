import pandas as pd
import numpy as np
from mlprimer.model_selection import train_models, evaluate_models

def test_train_models_returns_all_models():
    X = pd.DataFrame(np.random.rand(100, 3), columns=['a', 'b', 'c'])
    y = pd.Series([0, 1] * 50)

    models = train_models(X, y)
    assert set(models.keys()) == {"Logistic Regression", "Decision Tree", "Random Forest", "Gradient Boosting"}

def test_evaluate_models_returns_metrics():
    X = pd.DataFrame(np.random.rand(100, 3), columns=['a', 'b', 'c'])
    y = pd.Series([0, 1] * 50)
    models = train_models(X, y)
    results = evaluate_models(models, X, y)

    assert isinstance(results, pd.DataFrame)
    assert all(metric in results.columns for metric in ["Accuracy", "Precision", "Recall", "F1 Score"])
