from __future__ import annotations

import warnings
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Optional,
    Union,
    List,
    Literal,
    Tuple,
)

from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    StratifiedKFold,
    KFold,
    GroupKFold,
    StratifiedGroupKFold,
    TimeSeriesSplit,
    cross_val_predict,
)
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV

# Phase 2: Successive halving (sklearn 1.0+)
try:
    from sklearn.model_selection import HalvingGridSearchCV, HalvingRandomSearchCV
    HALVING_AVAILABLE = True
except ImportError:
    HALVING_AVAILABLE = False

# Phase 3: Bayesian optimization (optional)
try:
    from skopt import BayesSearchCV
    BAYES_AVAILABLE = True
except ImportError:
    BAYES_AVAILABLE = False

warnings.filterwarnings("ignore")


# ============================================================================
# CONFIGURATION & DEFAULTS
# ============================================================================

TASK_SCORING_DEFAULTS = {
    "binary": {
        "default": "f1",
        "multi": ["f1", "roc_auc", "precision", "recall", "balanced_accuracy"],
    },
    "multiclass": {
        "default": "f1_weighted",
        "multi": ["f1_weighted", "f1_macro", "balanced_accuracy"],
    },
    "regression": {
        "default": "neg_mean_absolute_error",
        "multi": ["neg_mean_absolute_error", "r2", "neg_root_mean_squared_error"],
    },
    "count": {
        "default": "neg_mean_absolute_error",
        "multi": ["neg_mean_absolute_error", "r2"],
    },
}

# Task-optimized parameter grids for common models
PARAM_GRIDS = {
    "LogisticRegression": {
        "balanced": {
            "C": [0.001, 0.01, 0.1, 1, 10, 100],
            "solver": ["lbfgs", "liblinear"],
            "max_iter": [1000, 2000],
        },
        "small": {
            "C": [0.1, 1, 10],
            "solver": ["lbfgs"],
        },
    },
    "RandomForest": {
        "balanced": {
            "n_estimators": [100, 200, 500],
            "max_depth": [10, 20, None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
        },
        "small": {
            "n_estimators": [100, 200],
            "max_depth": [10, 20],
        },
    },
    "LightGBM": {
        "balanced": {
            "num_leaves": [31, 63, 127],
            "learning_rate": [0.01, 0.05, 0.1],
            "max_depth": [5, 10, 15],
            "subsample": [0.6, 0.8, 1.0],
        },
        "small": {
            "num_leaves": [31, 63],
            "learning_rate": [0.05, 0.1],
        },
    },
    "XGBoost": {
        "balanced": {
            "n_estimators": [100, 200],
            "max_depth": [3, 5, 7],
            "learning_rate": [0.01, 0.05, 0.1],
            "subsample": [0.6, 0.8, 1.0],
            "colsample_bytree": [0.6, 0.8, 1.0],
        },
        "small": {
            "max_depth": [3, 5],
            "learning_rate": [0.05, 0.1],
        },
    },
    "SVC": {
        "balanced": {
            "C": [0.1, 1, 10, 100],
            "kernel": ["linear", "rbf"],
            "gamma": ["scale", "auto"],
        },
        "small": {
            "C": [1, 10],
            "kernel": ["rbf"],
        },
    },
    "SVR": {
        "balanced": {
            "C": [0.1, 1, 10, 100],
            "epsilon": [0.01, 0.1, 1],
            "kernel": ["linear", "rbf"],
        },
        "small": {
            "C": [1, 10],
            "epsilon": [0.1, 1],
        },
    },
    "Ridge": {
        "balanced": {
            "alpha": [0.001, 0.01, 0.1, 1, 10, 100],
        },
        "small": {
            "alpha": [0.1, 1, 10],
        },
    },
    "Lasso": {
        "balanced": {
            "alpha": [0.0001, 0.001, 0.01, 0.1, 1],
            "max_iter": [1000, 5000],
        },
        "small": {
            "alpha": [0.001, 0.01, 0.1],
        },
    },
    "ElasticNet": {
        "balanced": {
            "alpha": [0.0001, 0.001, 0.01, 0.1, 1],
            "l1_ratio": [0.1, 0.5, 0.9],
        },
        "small": {
            "alpha": [0.001, 0.01, 0.1],
            "l1_ratio": [0.5],
        },
    },
}

Scoring = Union[str, Dict[str, Any], None]


# ============================================================================
# PHASE 1: SEARCH RESULT & CV ROUTING
# ============================================================================

@dataclass
class SearchResult:
    """Structured container for hyperparameter search results."""
    
    search: Any
    best_estimator: Any
    best_params: Dict[str, Any]
    best_score: float
    cv_results: pd.DataFrame
    task: str
    scoring: Scoring
    
    def summary(self, top_n: int = 5) -> pd.DataFrame:
        """
        Get top N results summary.
        
        Parameters
        ----------
        top_n : int, default 5
            Number of top results to return
            
        Returns
        -------
        pd.DataFrame
            Top results with mean test score and std
        """
        results = self.cv_results.head(top_n).copy()
        
        # Select relevant columns
        param_cols = [col for col in results.columns if col.startswith("param_")]
        score_cols = [col for col in results.columns if "test_" in col and "mean" in col]
        
        return results[param_cols + score_cols + ["mean_test_score", "std_test_score"]]
    
    def get_params_importance(self) -> Dict[str, float]:
        """
        Estimate parameter importance based on score variance across params.
        
        Returns
        -------
        dict
            Parameter name -> importance score
        """
        param_cols = [col for col in self.cv_results.columns if col.startswith("param_")]
        importance = {}
        
        for param in param_cols:
            param_name = param.replace("param_", "")
            grouped = self.cv_results.groupby(param)["mean_test_score"].std()
            importance[param_name] = float(grouped.mean()) if len(grouped) > 0 else 0.0
        
        return {k: v for k, v in sorted(importance.items(), key=lambda x: x[1], reverse=True)}


def _validate_scoring(
    scoring: Scoring,
    task: Literal["binary", "multiclass", "regression", "count"],
) -> Scoring:
    """
    Validate and set defaults for scoring metric(s).
    
    Parameters
    ----------
    scoring : str, dict, or None
        Scoring metric(s)
    task : str
        Task type
        
    Returns
    -------
    str, dict, or None
        Validated scoring
    """
    if scoring is None:
        return TASK_SCORING_DEFAULTS[task]["default"]
    
    if isinstance(scoring, str):
        # Validate string is appropriate for task
        valid = set(TASK_SCORING_DEFAULTS[task]["multi"])
        if scoring not in valid:
            warnings.warn(
                f"Scoring '{scoring}' may not be ideal for task '{task}'. "
                f"Consider: {valid}",
                UserWarning
            )
    
    elif isinstance(scoring, dict):
        # Dict of metrics is fine; will refit on first key
        pass
    
    return scoring


def _make_cv(
    task: Literal["binary", "multiclass", "regression", "count"],
    cv: int = 5,
    *,
    shuffle: bool = True,
    random_state: int = 42,
    groups: Optional[np.ndarray] = None,
    time_series: bool = False,
    y: Optional[np.ndarray] = None,
) -> Any:
    """
    Create task-appropriate CV splitter.
    
    Parameters
    ----------
    task : str
        Classification or regression
    cv : int, default 5
        Number of splits
    shuffle : bool, default True
        Whether to shuffle
    random_state : int, default 42
        Random seed
    groups : np.ndarray, optional
        Group labels for grouped CV
    time_series : bool, default False
        Use TimeSeriesSplit
    y : np.ndarray, optional
        Target (needed for StratifiedGroupKFold)
        
    Returns
    -------
    sklearn CV splitter
    """
    if time_series:
        return TimeSeriesSplit(n_splits=cv)
    
    if groups is not None:
        if task in ("binary", "multiclass"):
            return StratifiedGroupKFold(
                n_splits=cv,
                shuffle=shuffle,
                random_state=random_state,
            )
        else:
            return GroupKFold(n_splits=cv)
    
    if task in ("binary", "multiclass"):
        return StratifiedKFold(
            n_splits=cv,
            shuffle=shuffle,
            random_state=random_state,
        )
    
    return KFold(n_splits=cv, shuffle=shuffle, random_state=random_state)


# ============================================================================
# PHASE 1: CORE TUNING FUNCTIONS
# ============================================================================

def tune_grid(
    model: Any,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    param_grid: Dict[str, Any],
    *,
    task: Literal["binary", "multiclass", "regression", "count"] = "binary",
    scoring: Scoring = None,
    refit: Union[bool, str] = True,
    cv: int = 5,
    groups: Optional[np.ndarray] = None,
    time_series: bool = False,
    random_state: int = 42,
    n_jobs: int = -1,
    verbose: int = 1,
    error_score: float = np.nan,
    return_train_score: bool = True,
    fit_params: Optional[Dict[str, Any]] = None,
    pre_dispatch: Union[int, str] = "2*n_jobs",
) -> SearchResult:
    """
    Exhaustive grid search with task-aware CV and scoring.
    
    Parameters
    ----------
    model : sklearn estimator
        Model to tune
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    param_grid : dict
        Parameter grid: name -> list of values
    task : str, default "binary"
        Task type for CV strategy and scoring defaults
    scoring : str, dict, or None, default None
        Metric(s) to optimize. None uses task default.
    refit : bool or str, default True
        Refit on best params. If dict scoring, use metric name.
    cv : int, default 5
        Number of CV folds
    groups : np.ndarray, optional
        Group labels for grouped CV
    time_series : bool, default False
        Use TimeSeriesSplit
    random_state : int, default 42
        Random seed
    n_jobs : int, default -1
        Parallel jobs (-1 = all cores)
    verbose : int, default 1
        Verbosity
    error_score : float, default np.nan
        Score if estimator raises exception
    return_train_score : bool, default True
        Include train scores in results
    fit_params : dict, optional
        Fit parameters (e.g., sample_weight, groups)
    pre_dispatch : int or str, default "2*n_jobs"
        Pre-dispatch parameter for parallelization
        
    Returns
    -------
    SearchResult
        Structured search results
    """
    fit_params = fit_params or {}
    scoring = _validate_scoring(scoring, task)
    
    cv_splitter = _make_cv(
        task=task,
        cv=cv,
        random_state=random_state,
        groups=groups,
        time_series=time_series,
        y=y_train.values if y_train is not None else None,
    )
    
    search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        scoring=scoring,
        refit=refit,
        cv=cv_splitter,
        n_jobs=n_jobs,
        verbose=verbose,
        error_score=error_score,
        return_train_score=return_train_score,
        pre_dispatch=pre_dispatch,
    )
    
    if groups is not None:
        search.fit(X_train, y_train, groups=groups, **fit_params)
    else:
        search.fit(X_train, y_train, **fit_params)
    
    cv_results_df = pd.DataFrame(search.cv_results_).sort_values(
        by="rank_test_score" if "rank_test_score" in search.cv_results_ else "mean_test_score"
    )
    
    return SearchResult(
        search=search,
        best_estimator=search.best_estimator_,
        best_params=search.best_params_,
        best_score=float(search.best_score_),
        cv_results=cv_results_df,
        task=task,
        scoring=scoring,
    )


def tune_random(
    model: Any,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    param_distributions: Dict[str, Any],
    *,
    n_iter: int = 30,
    task: Literal["binary", "multiclass", "regression", "count"] = "binary",
    scoring: Scoring = None,
    refit: Union[bool, str] = True,
    cv: int = 5,
    groups: Optional[np.ndarray] = None,
    time_series: bool = False,
    random_state: int = 42,
    n_jobs: int = -1,
    verbose: int = 1,
    error_score: float = np.nan,
    return_train_score: bool = True,
    fit_params: Optional[Dict[str, Any]] = None,
    pre_dispatch: Union[int, str] = "2*n_jobs",
) -> SearchResult:
    """
    Randomized search with task-aware CV and scoring.
    
    Parameters
    ----------
    model : sklearn estimator
        Model to tune
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    param_distributions : dict
        Parameter distributions for sampling
    n_iter : int, default 30
        Number of parameter combinations to sample
    task : str, default "binary"
        Task type for CV strategy and scoring defaults
    scoring : str, dict, or None, default None
        Metric(s) to optimize. None uses task default.
    refit : bool or str, default True
        Refit on best params
    cv : int, default 5
        Number of CV folds
    groups : np.ndarray, optional
        Group labels for grouped CV
    time_series : bool, default False
        Use TimeSeriesSplit
    random_state : int, default 42
        Random seed
    n_jobs : int, default -1
        Parallel jobs
    verbose : int, default 1
        Verbosity
    error_score : float, default np.nan
        Score if estimator raises exception
    return_train_score : bool, default True
        Include train scores
    fit_params : dict, optional
        Fit parameters (e.g., sample_weight)
    pre_dispatch : int or str, default "2*n_jobs"
        Pre-dispatch parameter
        
    Returns
    -------
    SearchResult
        Structured search results
    """
    fit_params = fit_params or {}
    scoring = _validate_scoring(scoring, task)
    
    cv_splitter = _make_cv(
        task=task,
        cv=cv,
        random_state=random_state,
        groups=groups,
        time_series=time_series,
        y=y_train.values if y_train is not None else None,
    )
    
    search = RandomizedSearchCV(
        estimator=model,
        param_distributions=param_distributions,
        n_iter=n_iter,
        scoring=scoring,
        refit=refit,
        cv=cv_splitter,
        random_state=random_state,
        n_jobs=n_jobs,
        verbose=verbose,
        error_score=error_score,
        return_train_score=return_train_score,
        pre_dispatch=pre_dispatch,
    )
    
    if groups is not None:
        search.fit(X_train, y_train, groups=groups, **fit_params)
    else:
        search.fit(X_train, y_train, **fit_params)
    
    cv_results_df = pd.DataFrame(search.cv_results_).sort_values(
        by="rank_test_score" if "rank_test_score" in search.cv_results_ else "mean_test_score"
    )
    
    return SearchResult(
        search=search,
        best_estimator=search.best_estimator_,
        best_params=search.best_params_,
        best_score=float(search.best_score_),
        cv_results=cv_results_df,
        task=task,
        scoring=scoring,
    )


# ============================================================================
# PHASE 2: SUCCESSIVE HALVING & EFFICIENCY
# ============================================================================

def tune_halving_grid(
    model: Any,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    param_grid: Dict[str, Any],
    *,
    task: Literal["binary", "multiclass", "regression", "count"] = "binary",
    scoring: Scoring = None,
    refit: Union[bool, str] = True,
    cv: int = 5,
    groups: Optional[np.ndarray] = None,
    random_state: int = 42,
    n_jobs: int = -1,
    verbose: int = 1,
    error_score: float = np.nan,
    return_train_score: bool = True,
    fit_params: Optional[Dict[str, Any]] = None,
    min_resources: Optional[int] = None,
    resource: str = "n_samples",
) -> SearchResult:
    """
    Successive halving grid search (more efficient than exhaustive grid).
    
    Only available in sklearn 1.0+. Falls back to standard GridSearchCV if unavailable.
    
    Parameters
    ----------
    model : sklearn estimator
        Model to tune
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    param_grid : dict
        Parameter grid
    task : str, default "binary"
        Task type
    scoring : str, dict, or None, default None
        Metric(s)
    refit : bool or str, default True
        Refit on best params
    cv : int, default 5
        CV folds
    groups : np.ndarray, optional
        Group labels
    random_state : int, default 42
        Random seed
    n_jobs : int, default -1
        Parallel jobs
    verbose : int, default 1
        Verbosity
    error_score : float, default np.nan
        Error score
    return_train_score : bool, default True
        Return train scores
    fit_params : dict, optional
        Fit parameters
    min_resources : int, optional
        Minimum resources (samples) per iteration
    resource : str, default "n_samples"
        Resource to halve (n_samples or other)
        
    Returns
    -------
    SearchResult
        Structured search results
    """
    if not HALVING_AVAILABLE:
        warnings.warn(
            "HalvingGridSearchCV not available (requires sklearn 1.0+). "
            "Falling back to standard GridSearchCV.",
            UserWarning
        )
        return tune_grid(
            model, X_train, y_train, param_grid,
            task=task, scoring=scoring, refit=refit, cv=cv,
            groups=groups, random_state=random_state, n_jobs=n_jobs,
            verbose=verbose, error_score=error_score,
            return_train_score=return_train_score, fit_params=fit_params,
        )
    
    fit_params = fit_params or {}
    scoring = _validate_scoring(scoring, task)
    
    cv_splitter = _make_cv(
        task=task,
        cv=cv,
        random_state=random_state,
        groups=groups,
        y=y_train.values if y_train is not None else None,
    )
    
    search = HalvingGridSearchCV(
        estimator=model,
        param_grid=param_grid,
        scoring=scoring,
        refit=refit,
        cv=cv_splitter,
        random_state=random_state,
        n_jobs=n_jobs,
        verbose=verbose,
        error_score=error_score,
        return_train_score=return_train_score,
        min_resources=min_resources,
        resource=resource,
    )
    
    if groups is not None:
        search.fit(X_train, y_train, groups=groups, **fit_params)
    else:
        search.fit(X_train, y_train, **fit_params)
    
    cv_results_df = pd.DataFrame(search.cv_results_).sort_values(
        by="rank_test_score" if "rank_test_score" in search.cv_results_ else "mean_test_score"
    )
    
    return SearchResult(
        search=search,
        best_estimator=search.best_estimator_,
        best_params=search.best_params_,
        best_score=float(search.best_score_),
        cv_results=cv_results_df,
        task=task,
        scoring=scoring,
    )


def tune_halving_random(
    model: Any,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    param_distributions: Dict[str, Any],
    *,
    n_candidates: Optional[int] = None,
    task: Literal["binary", "multiclass", "regression", "count"] = "binary",
    scoring: Scoring = None,
    refit: Union[bool, str] = True,
    cv: int = 5,
    groups: Optional[np.ndarray] = None,
    random_state: int = 42,
    n_jobs: int = -1,
    verbose: int = 1,
    error_score: float = np.nan,
    return_train_score: bool = True,
    fit_params: Optional[Dict[str, Any]] = None,
    min_resources: Optional[int] = None,
) -> SearchResult:
    """
    Successive halving randomized search (more efficient for large spaces).
    
    Only available in sklearn 1.0+. Falls back to RandomizedSearchCV if unavailable.
    
    Parameters
    ----------
    model : sklearn estimator
        Model to tune
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    param_distributions : dict
        Parameter distributions
    n_candidates : int, optional
        Number of parameter combinations to try. Auto-computed if None.
    task : str, default "binary"
        Task type
    scoring : str, dict, or None, default None
        Metric(s)
    refit : bool or str, default True
        Refit on best params
    cv : int, default 5
        CV folds
    groups : np.ndarray, optional
        Group labels
    random_state : int, default 42
        Random seed
    n_jobs : int, default -1
        Parallel jobs
    verbose : int, default 1
        Verbosity
    error_score : float, default np.nan
        Error score
    return_train_score : bool, default True
        Return train scores
    fit_params : dict, optional
        Fit parameters
    min_resources : int, optional
        Minimum resources per iteration
        
    Returns
    -------
    SearchResult
        Structured search results
    """
    if not HALVING_AVAILABLE:
        warnings.warn(
            "HalvingRandomSearchCV not available (requires sklearn 1.0+). "
            "Falling back to standard RandomizedSearchCV.",
            UserWarning
        )
        return tune_random(
            model, X_train, y_train, param_distributions,
            n_iter=20, task=task, scoring=scoring, refit=refit, cv=cv,
            groups=groups, random_state=random_state, n_jobs=n_jobs,
            verbose=verbose, error_score=error_score,
            return_train_score=return_train_score, fit_params=fit_params,
        )
    
    fit_params = fit_params or {}
    scoring = _validate_scoring(scoring, task)
    
    cv_splitter = _make_cv(
        task=task,
        cv=cv,
        random_state=random_state,
        groups=groups,
        y=y_train.values if y_train is not None else None,
    )
    
    search = HalvingRandomSearchCV(
        estimator=model,
        param_distributions=param_distributions,
        n_candidates=n_candidates,
        scoring=scoring,
        refit=refit,
        cv=cv_splitter,
        random_state=random_state,
        n_jobs=n_jobs,
        verbose=verbose,
        error_score=error_score,
        return_train_score=return_train_score,
        min_resources=min_resources,
    )
    
    if groups is not None:
        search.fit(X_train, y_train, groups=groups, **fit_params)
    else:
        search.fit(X_train, y_train, **fit_params)
    
    cv_results_df = pd.DataFrame(search.cv_results_).sort_values(
        by="rank_test_score" if "rank_test_score" in search.cv_results_ else "mean_test_score"
    )
    
    return SearchResult(
        search=search,
        best_estimator=search.best_estimator_,
        best_params=search.best_params_,
        best_score=float(search.best_score_),
        cv_results=cv_results_df,
        task=task,
        scoring=scoring,
    )


# ============================================================================
# PHASE 3: BAYESIAN OPTIMIZATION & ADVANCED TUNING
# ============================================================================

def tune_bayesian(
    model: Any,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    param_distributions: Dict[str, Any],
    *,
    n_calls: int = 50,
    task: Literal["binary", "multiclass", "regression", "count"] = "binary",
    scoring: Scoring = None,
    refit: Union[bool, str] = True,
    cv: int = 5,
    groups: Optional[np.ndarray] = None,
    random_state: int = 42,
    n_jobs: int = -1,
    verbose: int = 1,
    error_score: float = np.nan,
    fit_params: Optional[Dict[str, Any]] = None,
) -> SearchResult:
    """
    Bayesian optimization-based hyperparameter search.
    
    More efficient than grid/random search for continuous spaces.
    Requires scikit-optimize: pip install scikit-optimize
    
    Parameters
    ----------
    model : sklearn estimator
        Model to tune
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    param_distributions : dict
        Parameter space (use skopt.space types)
    n_calls : int, default 50
        Number of iterations
    task : str, default "binary"
        Task type
    scoring : str, dict, or None, default None
        Metric(s)
    refit : bool or str, default True
        Refit on best params
    cv : int, default 5
        CV folds
    groups : np.ndarray, optional
        Group labels
    random_state : int, default 42
        Random seed
    n_jobs : int, default -1
        Parallel jobs
    verbose : int, default 1
        Verbosity
    error_score : float, default np.nan
        Error score
    fit_params : dict, optional
        Fit parameters
        
    Returns
    -------
    SearchResult
        Structured search results
        
    Raises
    ------
    ImportError
        If scikit-optimize is not installed
    """
    if not BAYES_AVAILABLE:
        raise ImportError(
            "BayesSearchCV requires scikit-optimize. Install with: pip install scikit-optimize"
        )
    
    fit_params = fit_params or {}
    scoring = _validate_scoring(scoring, task)
    
    cv_splitter = _make_cv(
        task=task,
        cv=cv,
        random_state=random_state,
        groups=groups,
        y=y_train.values if y_train is not None else None,
    )
    
    search = BayesSearchCV(
        estimator=model,
        search_spaces=param_distributions,
        n_calls=n_calls,
        scoring=scoring,
        refit=refit,
        cv=cv_splitter,
        random_state=random_state,
        n_jobs=n_jobs,
        verbose=verbose,
        error_score=error_score,
    )
    
    if groups is not None:
        search.fit(X_train, y_train, groups=groups, **fit_params)
    else:
        search.fit(X_train, y_train, **fit_params)
    
    cv_results_df = pd.DataFrame(search.cv_results_).sort_values(
        by="rank_test_score" if "rank_test_score" in search.cv_results_ else "mean_test_score"
    )
    
    return SearchResult(
        search=search,
        best_estimator=search.best_estimator_,
        best_params=search.best_params_,
        best_score=float(search.best_score_),
        cv_results=cv_results_df,
        task=task,
        scoring=scoring,
    )


def tune_with_calibration(
    model: Any,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    method: Literal["sigmoid", "isotonic"] = "sigmoid",
) -> Tuple[CalibratedClassifierCV, float]:
    """
    Calibrate binary classifier for probability estimates.
    
    Use after tuning to improve probability calibration, especially for imbalanced data.
    
    Parameters
    ----------
    model : sklearn estimator
        Fitted classifier
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    X_val : pd.DataFrame
        Validation features for calibration
    y_val : pd.Series
        Validation target
    method : {"sigmoid", "isotonic"}, default "sigmoid"
        Calibration method
        
    Returns
    -------
    tuple
        (calibrated_model, calibration_score)
    """
    calibrated_model = CalibratedClassifierCV(
        estimator=model,
        method=method,
        cv="prefit",
    )
    
    calibrated_model.fit(X_val, y_val)
    
    y_proba_cal = calibrated_model.predict_proba(X_val)[:, 1]
    from sklearn.metrics import brier_score_loss
    calibration_score = 1.0 - brier_score_loss(y_val, y_proba_cal)
    
    return calibrated_model, calibration_score


def get_param_grid(
    model_name: str,
    search_space: Literal["small", "balanced", "large"] = "balanced",
) -> Optional[Dict[str, Any]]:
    """
    Get predefined parameter grid for a model.
    
    Parameters
    ----------
    model_name : str
        Name of model (e.g., "RandomForest", "LightGBM")
    search_space : {"small", "balanced", "large"}, default "balanced"
        Size of search space
        
    Returns
    -------
    dict or None
        Parameter grid, or None if not found
    """
    if model_name not in PARAM_GRIDS:
        return None
    
    grids = PARAM_GRIDS[model_name]
    
    if search_space not in grids:
        return grids.get("balanced", None)
    
    return grids[search_space]


# ============================================================================
# UTILITIES & ANALYSIS
# ============================================================================

def compare_search_results(*results: SearchResult) -> pd.DataFrame:
    """
    Compare multiple search results side-by-side.
    
    Parameters
    ----------
    *results : SearchResult
        Multiple search result objects
        
    Returns
    -------
    pd.DataFrame
        Comparison table with best scores from each search
    """
    comparison_rows = []
    
    for i, result in enumerate(results):
        row = {
            "search": i,
            "best_score": result.best_score,
            "best_params": str(result.best_params),
            "n_evals": len(result.cv_results),
            "scoring": str(result.scoring),
        }
        comparison_rows.append(row)
    
    return pd.DataFrame(comparison_rows)


def extract_best_params_for_pipeline(
    search_result: SearchResult,
    model_name: str,
) -> Dict[str, Any]:
    """
    Transform best params for use in sklearn Pipeline.
    
    Parameters
    ----------
    search_result : SearchResult
        Tuning results
    model_name : str
        Pipeline step name (e.g., "model")
        
    Returns
    -------
    dict
        Parameters prefixed for pipeline (e.g., "model__C" -> "C")
    """
    pipeline_params = {}
    
    for param, value in search_result.best_params.items():
        prefixed_param = f"{model_name}__{param}"
        pipeline_params[prefixed_param] = value
    
    return pipeline_params


# ============================================================================
# Backward Compatibility Wrappers (Legacy API)
# ============================================================================

def grid_search(
    model: Any,
    param_grid: Dict[str, Any],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    scoring: str = "accuracy",
    cv: int = 3,
) -> GridSearchCV:
    """[DEPRECATED] Legacy function. Use tune_grid() instead."""
    warnings.warn(
        "grid_search() is deprecated. Use tune_grid() for task-aware tuning.",
        DeprecationWarning,
        stacklevel=2
    )
    
    search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=cv,
        scoring=scoring,
        n_jobs=-1,
        verbose=1,
    )
    search.fit(X_train, y_train)
    return search


def randomized_search(
    model: Any,
    param_distributions: Dict[str, Any],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_iter: int = 20,
    scoring: str = "accuracy",
    cv: int = 3,
    random_state: int = 42,
) -> RandomizedSearchCV:
    """[DEPRECATED] Legacy function. Use tune_random() instead."""
    warnings.warn(
        "randomized_search() is deprecated. Use tune_random() for task-aware tuning.",
        DeprecationWarning,
        stacklevel=2
    )
    
    search = RandomizedSearchCV(
        estimator=model,
        param_distributions=param_distributions,
        n_iter=n_iter,
        cv=cv,
        scoring=scoring,
        random_state=random_state,
        n_jobs=-1,
        verbose=1,
    )
    search.fit(X_train, y_train)
    return search
