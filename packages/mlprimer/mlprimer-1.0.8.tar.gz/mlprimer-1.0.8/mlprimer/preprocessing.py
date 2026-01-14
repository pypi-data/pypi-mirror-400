from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import skew, kurtosis
from sklearn.model_selection import (
    train_test_split,
    TimeSeriesSplit,
    GroupShuffleSplit,
    StratifiedKFold,
)
from sklearn.preprocessing import PowerTransformer, RobustScaler
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE, SMOTENC, BorderlineSMOTE
from imblearn.under_sampling import RandomUnderSampler, TomekLinks
from imblearn.pipeline import Pipeline as ImbPipeline
from typing import Literal, Dict, Any, Optional, Tuple


# ============================================================================
# PHASE 1: Target Type Detection & Classification-focused Preprocessing
# ============================================================================

def infer_target_type(
    y: pd.Series,
    *,
    max_categories: int = 20,
    ordinal_threshold: int = 15,
) -> Literal["binary", "multiclass", "ordinal", "continuous", "count", "unknown"]:
    """
    Infer the type of target variable for task-specific preprocessing.
    
    Parameters
    ----------
    y : pd.Series
        Target variable
    max_categories : int, default 20
        Threshold for distinguishing multiclass from count targets
    ordinal_threshold : int, default 15
        Max unique values to detect as ordinal (e.g., 1-9 scale)
        
    Returns
    -------
    str
        One of: "binary", "multiclass", "ordinal", "continuous", "count", "unknown"
        
    Notes
    -----
    - binary: exactly 2 unique values (numeric or categorical)
    - ordinal: consecutive integers with small range (e.g., 1-9, 1-10 scales)
    - multiclass: >2 unique values, numeric or categorical (< max_categories)
    - count: non-negative integers with >max_categories unique values
    - continuous: floating-point or large-range numeric
    - unknown: empty or unrecognizable
    """
    s = y.dropna()
    
    if s.empty:
        return "unknown"
    
    nunique = s.nunique()
    
    # Check if numeric
    if pd.api.types.is_numeric_dtype(s):
        # Check if integer and non-negative (potential count data)
        if (s >= 0).all() and np.all(np.equal(np.mod(s, 1), 0)):
            if nunique <= 2:
                return "binary"
            # Detect ordinal: consecutive integers in small range
            elif nunique <= ordinal_threshold:
                unique_vals = sorted(s.unique())
                # Check if values are consecutive or nearly consecutive
                if unique_vals[-1] - unique_vals[0] == nunique - 1:
                    # Consecutive integers - likely ordinal scale
                    return "ordinal"
                else:
                    return "multiclass"
            else:
                return "count"
        # Otherwise continuous (float or wide range)
        return "continuous"
    
    # Categorical/object dtype
    if nunique == 2:
        return "binary"
    elif nunique <= max_categories:
        return "multiclass"
    else:
        return "unknown"


def report_target_distribution(
    y: pd.Series,
    task: Literal["classification", "regression", "count"] = "classification",
) -> Dict[str, Any]:
    """
    Generate a comprehensive distribution report for the target variable.
    
    Parameters
    ----------
    y : pd.Series
        Target variable
    task : {"classification", "regression", "count"}, default "classification"
        Task type to tailor the report
        
    Returns
    -------
    dict
        Task-specific statistics and diagnostics
    """
    s = y.dropna()
    report = {
        "count": len(s),
        "missing": y.isnull().sum(),
        "missing_rate": y.isnull().sum() / len(y),
        "nunique": s.nunique(),
    }
    
    if task == "classification":
        counts = s.value_counts()
        proportions = s.value_counts(normalize=True)
        
        report.update({
            "class_counts": counts.to_dict(),
            "class_proportions": proportions.to_dict(),
            "minority_class_rate": proportions.min(),
            "majority_class_rate": proportions.max(),
            "imbalance_ratio": proportions.max() / proportions.min(),
            "entropy": -np.sum(proportions * np.log2(proportions + 1e-10)),
        })
        
    elif task == "regression":
        numeric_y = pd.to_numeric(s, errors="coerce").dropna()
        
        report.update({
            "mean": numeric_y.mean(),
            "median": numeric_y.median(),
            "std": numeric_y.std(),
            "min": numeric_y.min(),
            "max": numeric_y.max(),
            "q25": numeric_y.quantile(0.25),
            "q75": numeric_y.quantile(0.75),
            "skewness": skew(numeric_y),
            "kurtosis": kurtosis(numeric_y),
            "outlier_rate": (
                ((numeric_y < numeric_y.quantile(0.25) - 1.5 * (numeric_y.quantile(0.75) - numeric_y.quantile(0.25)))
                 | (numeric_y > numeric_y.quantile(0.75) + 1.5 * (numeric_y.quantile(0.75) - numeric_y.quantile(0.25))))
                .sum() / len(numeric_y)
            ),
        })
        
    elif task == "count":
        numeric_y = pd.to_numeric(s, errors="coerce").dropna()
        
        zero_count = (numeric_y == 0).sum()
        nonzero_y = numeric_y[numeric_y > 0]
        
        report.update({
            "zero_count": zero_count,
            "zero_fraction": zero_count / len(numeric_y),
            "mean": numeric_y.mean(),
            "variance": numeric_y.var(),
            "overdispersion_ratio": numeric_y.var() / (numeric_y.mean() + 1e-10),
            "nonzero_mean": nonzero_y.mean() if len(nonzero_y) > 0 else np.nan,
            "nonzero_variance": nonzero_y.var() if len(nonzero_y) > 0 else np.nan,
        })
    
    return report


def split_data(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    task: Literal["classification", "regression", "time_series"] = "classification",
    test_size: float = 0.2,
    stratify: bool = True,
    groups: Optional[pd.Series] = None,
    time_order: Optional[pd.Series] = None,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split data into train/test sets with task-aware stratification and grouping.
    
    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix
    y : pd.Series
        Target variable
    task : {"classification", "regression", "time_series"}, default "classification"
        - classification: stratifies by y to preserve class distribution
        - regression: random split (no stratification)
        - time_series: respects temporal order, no shuffling
    test_size : float, default 0.2
        Test set proportion
    stratify : bool, default True
        For classification: whether to stratify (ignored for regression/time_series)
    groups : pd.Series, optional
        Group labels for GroupShuffleSplit. If provided, splits respecting groups.
    time_order : pd.Series, optional
        Time indices for time_series task. If None, uses X index.
    random_state : int, default 42
        Random seed for reproducibility
        
    Returns
    -------
    tuple
        (X_train, X_test, y_train, y_test)
    """
    if len(X) != len(y):
        raise ValueError(f"X and y must have same length: {len(X)} vs {len(y)}")
    
    if task == "time_series":
        # Time series split: no shuffling, respects temporal order
        if time_order is None:
            time_order = np.arange(len(X))
        
        split_point = int(len(X) * (1 - test_size))
        
        train_idx = time_order[:split_point]
        test_idx = time_order[split_point:]
        
        return (
            X.iloc[train_idx].reset_index(drop=True),
            X.iloc[test_idx].reset_index(drop=True),
            y.iloc[train_idx].reset_index(drop=True),
            y.iloc[test_idx].reset_index(drop=True),
        )
    
    elif groups is not None:
        # Grouped split: maintains group integrity
        splitter = GroupShuffleSplit(
            n_splits=1,
            test_size=test_size,
            random_state=random_state
        )
        train_idx, test_idx = next(splitter.split(X, y, groups=groups))
        
        return (
            X.iloc[train_idx].reset_index(drop=True),
            X.iloc[test_idx].reset_index(drop=True),
            y.iloc[train_idx].reset_index(drop=True),
            y.iloc[test_idx].reset_index(drop=True),
        )
    
    else:  # classification or regression
        stratify_arg = None
        if task == "classification" and stratify:
            stratify_arg = y
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            stratify=stratify_arg,
            random_state=random_state,
        )
        
        return X_train.reset_index(drop=True), X_test.reset_index(drop=True), y_train.reset_index(drop=True), y_test.reset_index(drop=True)


def compute_class_weights(
    y: pd.Series,
    weight_strategy: Literal["balanced", "log_balanced"] = "balanced",
) -> Dict[Any, float]:
    """
    Compute sample weights for imbalanced classification.
    
    Parameters
    ----------
    y : pd.Series
        Target variable with class labels
    weight_strategy : {"balanced", "log_balanced"}, default "balanced"
        - balanced: weight inversely proportional to class frequency
        - log_balanced: log-transformed weighting (softer than balanced)
        
    Returns
    -------
    dict
        Mapping of class labels to their weights
    """
    classes = np.unique(y.dropna())
    weights = compute_class_weight(
        class_weight=weight_strategy,
        classes=classes,
        y=y.dropna(),
    )
    return dict(zip(classes, weights))


def apply_smote_classification(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    categorical_cols: Optional[list] = None,
    smote_variant: Literal["standard", "borderline", "svm"] = "standard",
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Apply SMOTE (or variant) for binary/multiclass classification resampling.
    
    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix (numeric features only; encode categorical first)
    y : pd.Series
        Target variable
    categorical_cols : list, optional
        List of column names that are categorical. If provided, uses SMOTENC.
        Otherwise uses standard SMOTE (requires all numeric features).
    smote_variant : {"standard", "borderline", "svm"}, default "standard"
        - standard: SMOTE
        - borderline: BorderlineSMOTE (focuses on borderline cases)
        - svm: SVMSMOTE (uses SVM decision boundary)
    random_state : int, default 42
        Random seed
        
    Returns
    -------
    tuple
        (X_resampled, y_resampled)
        
    Raises
    ------
    ValueError
        If X contains non-numeric features and categorical_cols not specified
    """
    # Select SMOTE variant
    if categorical_cols is not None:
        # Determine categorical feature indices
        cat_indices = [X.columns.get_loc(col) for col in categorical_cols if col in X.columns]
        
        if smote_variant == "standard":
            sampler = SMOTENC(categorical_features=cat_indices, random_state=random_state)
        elif smote_variant == "borderline":
            # BorderlineSMOTE doesn't support categorical; fallback to SMOTENC
            sampler = SMOTENC(categorical_features=cat_indices, random_state=random_state)
        else:
            sampler = SMOTENC(categorical_features=cat_indices, random_state=random_state)
    else:
        if smote_variant == "standard":
            sampler = SMOTE(random_state=random_state)
        elif smote_variant == "borderline":
            sampler = BorderlineSMOTE(random_state=random_state)
        else:
            sampler = SMOTE(random_state=random_state)
    
    X_resampled, y_resampled = sampler.fit_resample(X, y)
    
    return pd.DataFrame(X_resampled, columns=X.columns), pd.Series(y_resampled, name=y.name)


def apply_under_sampling(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    strategy: Literal["random", "tomek"] = "random",
    sampling_strategy: float = 0.5,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Apply under-sampling to reduce majority class.
    
    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix
    y : pd.Series
        Target variable
    strategy : {"random", "tomek"}, default "random"
        - random: randomly remove majority samples
        - tomek: remove Tomek links (noisy samples on decision boundary)
    sampling_strategy : float, default 0.5
        Target ratio of minority to majority class (0 < ratio <= 1)
    random_state : int, default 42
        Random seed
        
    Returns
    -------
    tuple
        (X_undersampled, y_undersampled)
    """
    if strategy == "random":
        sampler = RandomUnderSampler(
            sampling_strategy=sampling_strategy,
            random_state=random_state
        )
    elif strategy == "tomek":
        sampler = TomekLinks(sampling_strategy=sampling_strategy)
    else:
        sampler = RandomUnderSampler(
            sampling_strategy=sampling_strategy,
            random_state=random_state
        )
    
    X_undersampled, y_undersampled = sampler.fit_resample(X, y)
    
    return pd.DataFrame(X_undersampled, columns=X.columns), pd.Series(y_undersampled, name=y.name)


# ============================================================================
# PHASE 2: Regression-specific Preprocessing
# ============================================================================

def apply_target_transform(
    y: pd.Series,
    method: Literal["yeo-johnson", "box-cox", "log1p", "none"] = "yeo-johnson",
) -> Tuple[pd.Series, PowerTransformer | None]:
    """
    Apply power transformation to target for regression to handle skewness.
    
    Parameters
    ----------
    y : pd.Series
        Target variable
    method : {"yeo-johnson", "box-cox", "log1p", "none"}, default "yeo-johnson"
        - yeo-johnson: handles negative/zero values, more robust
        - box-cox: classic power transform (requires positive values)
        - log1p: log(1 + y), simple and interpretable
        - none: no transformation
        
    Returns
    -------
    tuple
        (y_transformed, transformer)
        transformer is None for method="none" or "log1p"; otherwise PowerTransformer
    """
    y_clean = y.dropna().to_numpy().reshape(-1, 1)
    
    if method == "none":
        return y, None
    
    elif method == "log1p":
        return np.log1p(y), None
    
    elif method == "box-cox":
        # Box-Cox requires positive values
        if (y_clean <= 0).any():
            raise ValueError("Box-Cox transform requires positive values; use yeo-johnson instead")
        transformer = PowerTransformer(method="box-cox", standardize=True)
        y_transformed = transformer.fit_transform(y_clean)
        return pd.Series(y_transformed.ravel(), index=y.index, name=y.name), transformer
    
    else:  # yeo-johnson
        transformer = PowerTransformer(method="yeo-johnson", standardize=True)
        y_transformed = transformer.fit_transform(y_clean)
        return pd.Series(y_transformed.ravel(), index=y.index, name=y.name), transformer


def make_sample_weights_regression(
    y: pd.Series,
    method: Literal["quantile", "density"] = "quantile",
) -> np.ndarray:
    """
    Create sample weights for imbalanced regression (rare extreme values).
    
    Parameters
    ----------
    y : pd.Series
        Target variable
    method : {"quantile", "density"}, default "quantile"
        - quantile: weights inversely proportional to local quantile density
        - density: kernel density estimation-based weighting
        
    Returns
    -------
    np.ndarray
        Sample weights for weighted regression
    """
    y_clean = y.dropna().values
    
    if method == "quantile":
        # Weight samples based on how extreme/rare they are
        quantiles = stats.rankdata(y_clean) / len(y_clean)
        # Inverse relationship: extreme values get higher weight
        weights = 1.0 / (np.minimum(quantiles, 1 - quantiles) + 1e-6)
        weights /= weights.sum()
        
    else:  # density
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(y_clean)
        density = kde(y_clean)
        # Lower density (rarer values) get higher weight
        weights = 1.0 / (density + 1e-6)
        weights /= weights.sum()
    
    return weights


def count_target_diagnostics(y: pd.Series) -> Dict[str, Any]:
    """
    Diagnose count target data for potential zero-inflation and overdispersion.
    
    Parameters
    ----------
    y : pd.Series
        Count target (non-negative integers)
        
    Returns
    -------
    dict
        Diagnostics including zero rate and overdispersion metrics
    """
    y_clean = y.dropna().values
    
    zero_count = (y_clean == 0).sum()
    zero_fraction = zero_count / len(y_clean)
    nonzero_y = y_clean[y_clean > 0]
    
    return {
        "zero_count": int(zero_count),
        "zero_fraction": float(zero_fraction),
        "is_zero_inflated": zero_fraction > 0.2,
        "mean": float(y_clean.mean()),
        "variance": float(y_clean.var()),
        "overdispersion_ratio": float(y_clean.var() / (y_clean.mean() + 1e-10)),
        "is_overdispersed": (y_clean.var() / (y_clean.mean() + 1e-10)) > 1.5,
        "nonzero_mean": float(nonzero_y.mean()) if len(nonzero_y) > 0 else np.nan,
        "nonzero_variance": float(nonzero_y.var()) if len(nonzero_y) > 0 else np.nan,
    }


# ============================================================================
# Backward Compatibility Wrappers (Legacy API)
# ============================================================================

def imbalance_check(X: pd.DataFrame, y: pd.Series) -> None:
    """
    [DEPRECATED] Legacy function. Use report_target_distribution() instead.
    Print class distribution statistics.
    """
    report = report_target_distribution(y, task="classification")
    print("\n=== Class Distribution Report ===")
    print(f"Class counts:\n{report.get('class_counts', {})}")
    print(f"\nClass proportions:\n{report.get('class_proportions', {})}")
    print(f"Imbalance ratio: {report.get('imbalance_ratio', np.nan):.2f}")
    print(f"Entropy: {report.get('entropy', np.nan):.2f}")


def apply_smote(
    X: pd.DataFrame,
    y: pd.Series,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    [DEPRECATED] Legacy function. Use apply_smote_classification() instead.
    Apply SMOTE to balance the target variable.
    """
    return apply_smote_classification(X, y, random_state=random_state)
