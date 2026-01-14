import pandas as pd
import numpy as np
import pytest
from mlprimer.statistics import calculate_summary

def test_calculate_summary_numeric():
    df = pd.DataFrame({
        'a': [1, 2, 3, 4, 5],
        'b': [5.0, 6.2, 7.1, 8.3, 9.7]
    })
    summary = calculate_summary(df)

    assert 'a' in summary.index
    assert 'mean' in summary.columns
    assert np.isclose(summary.loc['a', 'mean'], 3.0)
    assert summary.loc['b', 'dtype'] == 'float64'

def test_calculate_summary_object():
    df = pd.DataFrame({
        'cat': ['yes', 'no', 'yes', 'no', 'maybe']
    })
    summary = calculate_summary(df)

    assert 'cat' in summary.index
    assert summary.loc['cat', 'dtype'] == 'object'
    assert summary.loc['cat', 'len_unique'] == 3
