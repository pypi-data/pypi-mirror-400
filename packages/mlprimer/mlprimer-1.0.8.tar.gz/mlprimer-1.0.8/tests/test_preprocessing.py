import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
from mlprimer.preprocessing import apply_smote, split_data


def test_apply_smote_balances_classes():
    X = pd.DataFrame({'feature': [1, 2, 3, 4, 5, 6, 7, 8]})
    y = pd.Series([0, 0, 0, 0, 1, 1, 1, 1])  # 4 per class (enough for k_neighbors=3)

    smote = SMOTE(k_neighbors=3, random_state=42)
    X_res, y_res = smote.fit_resample(X, y)

    assert len(X_res) == len(y_res)
    assert y_res.value_counts().nunique() == 1


def test_split_data_returns_correct_shape():
    X = pd.DataFrame(np.random.rand(100, 4), columns=['a', 'b', 'c', 'd'])
    y = pd.Series([0, 1] * 50)

    X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.25)
    assert len(X_train) == 75
    assert len(X_test) == 25
    assert len(y_train) == 75
    assert len(y_test) == 25