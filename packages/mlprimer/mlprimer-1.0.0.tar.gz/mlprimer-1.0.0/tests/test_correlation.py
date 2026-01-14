import pandas as pd
from mlprimer.correlation import check_correlation

def test_check_correlation_numeric():
    df = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'target': [0, 1, 0, 1, 0]
    })
    result = check_correlation(df, target_var='target')
    assert 'feature1' in result.index
    assert result.loc['feature1', 'test_method'] == 'pointbiserialr'

def test_check_correlation_categorical():
    df = pd.DataFrame({
        'feature2': ['a', 'b', 'a', 'b', 'c'],
        'target': [0, 1, 0, 1, 0]
    })
    result = check_correlation(df, target_var='target')
    assert 'feature2' in result.index
    assert result.loc['feature2', 'test_method'] == 'chi2'
