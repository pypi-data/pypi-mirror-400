from __future__ import annotations

import pandas as pd
import numpy as np
from scipy.stats import shapiro
from typing import Optional


def calculate_summary(data: pd.DataFrame) -> pd.DataFrame:
    """
    Generate comprehensive descriptive statistics for all variables.
    
    For numeric variables: includes mean, median, std, min, max, normality test
    For categorical variables: includes unique value count and top value
    
    The 'normal' column (numeric only) is used by correlation.py to select appropriate tests.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input data
        
    Returns
    -------
    pd.DataFrame
        Descriptive statistics indexed by column name.
        Numeric columns include 'normal' (bool or None if insufficient data)
    """
    desc_stat = {}
    
    for variable in data.columns:
        variable_data = data[variable]
        variable_dict = {}
        
        if pd.api.types.is_numeric_dtype(variable_data):
            x_clean = variable_data.dropna()
            
            # Shapiro test requires at least 3 observations
            is_normal: Optional[bool] = None
            if len(x_clean) >= 3:
                is_normal = shapiro(x_clean).pvalue >= 0.05
            
            variable_dict = {
                "dtype": str(variable_data.dtype),
                "type": "numeric",
                "count": len(variable_data),
                "missing": variable_data.isnull().sum(),
                "unique": variable_data.nunique(),
                "mean": variable_data.mean(),
                "median": variable_data.median(),
                "std": variable_data.std(),
                "min": variable_data.min(),
                "max": variable_data.max(),
                "normal": is_normal,
            }
        else:
            # Categorical or object dtype
            top_value = None
            if len(variable_data) > 0:
                value_counts = variable_data.value_counts()
                if len(value_counts) > 0:
                    top_value = value_counts.index[0]
            
            variable_dict = {
                "dtype": str(variable_data.dtype),
                "type": "categorical",
                "count": len(variable_data),
                "missing": variable_data.isnull().sum(),
                "unique": variable_data.nunique(),
                "top_value": top_value,
            }
        
        desc_stat[variable] = variable_dict
    
    return pd.DataFrame(desc_stat).T
