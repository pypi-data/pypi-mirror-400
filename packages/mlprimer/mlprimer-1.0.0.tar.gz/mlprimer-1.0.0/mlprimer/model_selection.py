from __future__ import annotations

import numpy as np
import pandas as pd
import warnings
from typing import Literal, Dict, Any, List, Tuple, Optional
from sklearn.model_selection import (
    cross_validate,
    StratifiedKFold,
    KFold,
    StratifiedGroupKFold,
    GroupKFold,
)
from sklearn.preprocessing import StandardScaler

# ============================================================================
# PHASE 1 & 2: Core Classification Models
# ============================================================================
from sklearn.linear_model import (
    LogisticRegression,
    Ridge,
    Lasso,
    ElasticNet,
)
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
)
from sklearn.svm import SVC, SVR
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor

# ============================================================================
# PHASE 3: Advanced Models
# ============================================================================
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    import catboost as cb
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.linear_model import BayesianRidge, HuberRegressor, RANSACRegressor, TheilSenRegressor
from sklearn.preprocessing import PowerTransformer

# ============================================================================
# PHASE 4: Unsupervised Models
# ============================================================================
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.covariance import EllipticEnvelope

# ============================================================================
# Metrics
# ============================================================================
from sklearn.metrics import (
    # Classification
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
    classification_report,
    balanced_accuracy_score,
    cohen_kappa_score,
    # Regression
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    mean_absolute_percentage_error,
)

warnings.filterwarnings("ignore")


# ============================================================================
# MODEL REGISTRY & CONFIGURATION
# ============================================================================

class ModelRegistry:
    """Central registry of models organized by task and family."""
    
    @staticmethod
    def get_classification_models(
        include_advanced: bool = True,
        include_neural: bool = False,
    ) -> Dict[str, Any]:
        """
        Get classification model templates.
        
        Parameters
        ----------
        include_advanced : bool, default True
            Include XGBoost, LightGBM, CatBoost
        include_neural : bool, default False
            Include MLP and neural variants
            
        Returns
        -------
        dict
            Model name -> unfitted model instance
        """
        models = {
            # Phase 1: Best-Practice Defaults
            "Logistic Regression": LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                solver="lbfgs",
                random_state=42,
            ),
            "Random Forest": RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight="balanced",
                n_jobs=-1,
                random_state=42,
            ),
            "SVC": SVC(
                kernel="rbf",
                C=1.0,
                class_weight="balanced",
                probability=True,
                random_state=42,
            ),
            # Phase 2: Extended Linear & Tree
            "LDA": LinearDiscriminantAnalysis(),
            "QDA": QuadraticDiscriminantAnalysis(),
            "Naive Bayes": GaussianNB(),
            "Decision Tree": DecisionTreeClassifier(
                max_depth=10,
                min_samples_split=5,
                class_weight="balanced",
                random_state=42,
            ),
            "Extra Trees": ExtraTreesClassifier(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                class_weight="balanced",
                n_jobs=-1,
                random_state=42,
            ),
            "Gradient Boosting": GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                subsample=0.8,
                random_state=42,
            ),
            "k-NN": KNeighborsClassifier(n_neighbors=5, n_jobs=-1),
        }
        
        # Phase 3: Advanced Boosting
        if include_advanced:
            if XGBOOST_AVAILABLE:
                models["XGBoost"] = xgb.XGBClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    subsample=0.8,
                    use_label_encoder=False,
                    eval_metric="logloss",
                    random_state=42,
                    n_jobs=-1,
                )
            
            if LIGHTGBM_AVAILABLE:
                models["LightGBM"] = lgb.LGBMClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=7,
                    num_leaves=31,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                    verbose=-1,
                )
            
            if CATBOOST_AVAILABLE:
                models["CatBoost"] = cb.CatBoostClassifier(
                    iterations=100,
                    learning_rate=0.1,
                    max_depth=6,
                    subsample=0.8,
                    auto_class_weights="balanced",
                    random_state=42,
                    verbose=0,
                    thread_count=-1,
                )
        
        # Phase 4: Neural Networks
        if include_neural:
            models["MLP"] = MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=1000,
                early_stopping=True,
                validation_fraction=0.1,
                random_state=42,
                n_jobs=-1,
            )
        
        return models
    
    @staticmethod
    def get_regression_models(
        include_advanced: bool = True,
        include_neural: bool = False,
    ) -> Dict[str, Any]:
        """
        Get regression model templates.
        
        Parameters
        ----------
        include_advanced : bool, default True
            Include XGBoost, LightGBM, CatBoost
        include_neural : bool, default False
            Include MLP and neural variants
            
        Returns
        -------
        dict
            Model name -> unfitted model instance
        """
        models = {
            # Phase 1: Best-Practice Defaults
            "ElasticNet": ElasticNet(
                alpha=0.1,
                l1_ratio=0.5,
                max_iter=2000,
                random_state=42,
            ),
            "Random Forest": RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                n_jobs=-1,
                random_state=42,
            ),
            "SVR": SVR(kernel="rbf", C=1.0, gamma="scale"),
            # Phase 2: Extended Linear & Tree
            "Ridge": Ridge(alpha=1.0),
            "Lasso": Lasso(alpha=0.1, max_iter=2000),
            "Decision Tree": DecisionTreeRegressor(
                max_depth=10,
                min_samples_split=5,
                random_state=42,
            ),
            "Extra Trees": ExtraTreesRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                n_jobs=-1,
                random_state=42,
            ),
            "Gradient Boosting": GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                subsample=0.8,
                random_state=42,
            ),
            "k-NN": KNeighborsRegressor(n_neighbors=5, n_jobs=-1),
            # Phase 2: Robust Regression
            "Bayesian Ridge": BayesianRidge(max_iter=1000),
            "Huber": HuberRegressor(epsilon=1.35, max_iter=1000),
            "RANSAC": RANSACRegressor(random_state=42, min_samples=30),
            "Theil-Sen": TheilSenRegressor(random_state=42),
        }
        
        # Phase 3: Advanced Boosting
        if include_advanced:
            if XGBOOST_AVAILABLE:
                models["XGBoost"] = xgb.XGBRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    subsample=0.8,
                    random_state=42,
                    n_jobs=-1,
                )
            
            if LIGHTGBM_AVAILABLE:
                models["LightGBM"] = lgb.LGBMRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=7,
                    num_leaves=31,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    n_jobs=-1,
                    verbose=-1,
                )
            
            if CATBOOST_AVAILABLE:
                models["CatBoost"] = cb.CatBoostRegressor(
                    iterations=100,
                    learning_rate=0.1,
                    max_depth=6,
                    subsample=0.8,
                    random_state=42,
                    verbose=0,
                    thread_count=-1,
                )
        
        # Phase 4: Neural Networks
        if include_neural:
            models["MLP"] = MLPRegressor(
                hidden_layer_sizes=(100, 50),
                max_iter=1000,
                early_stopping=True,
                validation_fraction=0.1,
                random_state=42,
                n_jobs=-1,
            )
        
        return models
    
    @staticmethod
    def get_unsupervised_models() -> Dict[str, Any]:
        """Get unsupervised models for preprocessing and diagnostics."""
        return {
            "PCA": PCA(n_components=None, random_state=42),
            "K-Means": KMeans(n_clusters=3, n_init=10, random_state=42),
            "Isolation Forest": IsolationForest(random_state=42, n_jobs=-1),
            "Elliptic Envelope": EllipticEnvelope(random_state=42),
        }


# ============================================================================
# TASK-AWARE MODEL SUGGESTION
# ============================================================================

def suggest_models(
    target_type: Literal["binary", "multiclass", "continuous", "count"],
    n_samples: int,
    n_features: int,
    feature_correlation: Optional[float] = None,
    is_normal: Optional[bool] = None,
    include_advanced: bool = True,
    include_neural: bool = False,
) -> List[str]:
    """
    Suggest appropriate models based on data characteristics.
    
    Parameters
    ----------
    target_type : str
        From infer_target_type(): "binary", "multiclass", "continuous", "count"
    n_samples : int
        Number of samples
    n_features : int
        Number of features
    feature_correlation : float, optional
        Average absolute correlation between features (0-1)
    is_normal : bool, optional
        Whether target is normally distributed
    include_advanced : bool, default True
        Include advanced boosting models
    include_neural : bool, default False
        Include neural network models
        
    Returns
    -------
    list
        Ordered list of suggested model names
    """
    suggestions = []
    
    is_small_sample = n_samples < 1000
    is_high_dim = n_features > 20
    is_collinear = feature_correlation is not None and feature_correlation > 0.7
    
    if target_type in ("binary", "multiclass"):
        # Classification suggestions
        
        # Always suggest robust baselines
        suggestions.append("Logistic Regression")
        
        if is_high_dim or is_collinear:
            suggestions.insert(1, "LDA")
        
        # Tree-based for interactions
        suggestions.append("Random Forest")
        suggestions.append("Extra Trees")
        
        # Boosting
        suggestions.append("Gradient Boosting")
        if include_advanced:
            if LIGHTGBM_AVAILABLE:
                suggestions.append("LightGBM")
            if XGBOOST_AVAILABLE:
                suggestions.append("XGBoost")
            if CATBOOST_AVAILABLE:
                suggestions.append("CatBoost")
        
        # SVM for high-dim
        if is_high_dim:
            suggestions.append("SVC")
        
        # k-NN for small samples
        if is_small_sample:
            suggestions.append("k-NN")
        
        # Neural for large samples
        if not is_small_sample and include_neural:
            suggestions.append("MLP")
    
    else:  # Regression: "continuous" or "count"
        # Regression suggestions
        
        # Linear baselines
        if is_collinear:
            suggestions.append("Ridge")
            suggestions.append("Lasso")
        suggestions.append("ElasticNet")
        
        # Robust for outliers/non-normal
        if not is_normal or is_normal is None:
            suggestions.append("Huber")
        
        # Trees for nonlinearity
        suggestions.append("Random Forest")
        suggestions.append("Extra Trees")
        
        # Boosting
        suggestions.append("Gradient Boosting")
        if include_advanced:
            if LIGHTGBM_AVAILABLE:
                suggestions.append("LightGBM")
            if XGBOOST_AVAILABLE:
                suggestions.append("XGBoost")
            if CATBOOST_AVAILABLE:
                suggestions.append("CatBoost")
        
        # SVR for smooth functions
        suggestions.append("SVR")
        
        # k-NN for small samples
        if is_small_sample:
            suggestions.append("k-NN")
        
        # Neural for large samples
        if not is_small_sample and include_neural:
            suggestions.append("MLP")
    
    return suggestions


# ============================================================================
# METRICS SELECTION
# ============================================================================

def get_metrics(
    task: Literal["binary", "multiclass", "regression", "count"],
) -> Dict[str, str]:
    """
    Get appropriate metrics for each task type.
    
    Parameters
    ----------
    task : str
        Task type: "binary", "multiclass", "regression", "count"
        
    Returns
    -------
    dict
        Metric name -> sklearn metric identifier
    """
    if task == "binary":
        return {
            "accuracy": "accuracy",
            "balanced_accuracy": "balanced_accuracy",
            "precision": "precision",
            "recall": "recall",
            "f1": "f1",
            "roc_auc": "roc_auc",
        }
    elif task == "multiclass":
        return {
            "accuracy": "accuracy",
            "balanced_accuracy": "balanced_accuracy",
            "f1_weighted": "f1_weighted",
            "f1_macro": "f1_macro",
        }
    elif task in ("regression", "count"):
        return {
            "r2": "r2",
            "neg_mean_absolute_error": "neg_mean_absolute_error",
            "neg_mean_squared_error": "neg_mean_squared_error",
            "neg_mean_absolute_percentage_error": "neg_mean_absolute_percentage_error",
        }
    else:
        return {}


def get_cv_splitter(
    task: Literal["binary", "multiclass", "regression", "count"],
    y: pd.Series,
    n_splits: int = 5,
    groups: Optional[pd.Series] = None,
    shuffle: bool = True,
    random_state: int = 42,
):
    """
    Get appropriate cross-validation splitter for task.
    
    Parameters
    ----------
    task : str
        Task type
    y : pd.Series
        Target variable
    n_splits : int, default 5
        Number of CV folds
    groups : pd.Series, optional
        Group labels for grouped CV
    shuffle : bool, default True
        Whether to shuffle before split
    random_state : int, default 42
        Random seed
        
    Returns
    -------
    sklearn CV splitter
    """
    if groups is not None:
        if task in ("binary", "multiclass"):
            return StratifiedGroupKFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)
        else:
            return GroupKFold(n_splits=n_splits)
    
    elif task in ("binary", "multiclass"):
        return StratifiedKFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)
    
    else:  # regression
        return KFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)


# ============================================================================
# MODEL TRAINING
# ============================================================================

def train_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    task: Literal["binary", "multiclass", "regression", "count"] = "binary",
    model_names: Optional[List[str]] = None,
    cv: int = 5,
    scale_features: bool = True,
    sample_weight: Optional[np.ndarray] = None,
) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """
    Train multiple models with cross-validation.
    
    Parameters
    ----------
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    task : str, default "binary"
        Task type: "binary", "multiclass", "regression", "count"
    model_names : list, optional
        Specific models to train. If None, uses all available.
    cv : int, default 5
        Number of cross-validation folds
    scale_features : bool, default True
        Whether to scale features (important for SVM, linear, KNN)
    sample_weight : np.ndarray, optional
        Sample weights for training
        
    Returns
    -------
    tuple
        (trained_models_dict, cv_results_dataframe)
    """
    # Select model registry
    if task in ("binary", "multiclass"):
        all_models = ModelRegistry.get_classification_models()
    else:
        all_models = ModelRegistry.get_regression_models()
    
    # Filter to requested models
    if model_names is not None:
        models = {name: all_models[name] for name in model_names if name in all_models}
    else:
        models = all_models
    
    # Prepare data
    X = X_train.copy()
    y = y_train.copy()
    
    if scale_features:
        scaler = StandardScaler()
        X = pd.DataFrame(
            scaler.fit_transform(X),
            columns=X.columns,
            index=X.index,
        )
    
    # Get metrics and CV splitter
    scoring = get_metrics(task)
    cv_splitter = get_cv_splitter(task, y)
    
    # Train and evaluate
    trained_models = {}
    cv_results_list = []
    
    for model_name, model in models.items():
        try:
            # Cross-validation
            cv_results = cross_validate(
                model,
                X,
                y,
                cv=cv_splitter,
                scoring=scoring,
                return_train_score=True,
                n_jobs=-1,
            )
            
            # Fit on full training set
            if sample_weight is not None and hasattr(model, "fit"):
                model.fit(X, y, sample_weight=sample_weight)
            else:
                model.fit(X, y)
            
            trained_models[model_name] = model
            
            # Aggregate CV results
            row = {"model": model_name}
            for metric, scores in cv_results.items():
                if metric.startswith("test_"):
                    metric_name = metric.replace("test_", "")
                    row[f"{metric_name}_mean"] = scores.mean()
                    row[f"{metric_name}_std"] = scores.std()
            
            cv_results_list.append(row)
        
        except Exception as e:
            print(f"Error training {model_name}: {e}")
            continue
    
    cv_results_df = pd.DataFrame(cv_results_list)
    
    return trained_models, cv_results_df


# ============================================================================
# MODEL EVALUATION
# ============================================================================

def evaluate_models(
    models: Dict[str, Any],
    X_test: pd.DataFrame,
    y_test: pd.Series,
    task: Literal["binary", "multiclass", "regression", "count"] = "binary",
    scale_features: bool = True,
    scaler: Optional[StandardScaler] = None,
) -> pd.DataFrame:
    """
    Evaluate trained models on test set.
    
    Parameters
    ----------
    models : dict
        Trained model instances
    X_test : pd.DataFrame
        Test features
    y_test : pd.Series
        Test target
    task : str, default "binary"
        Task type
    scale_features : bool, default True
        Whether to scale features
    scaler : StandardScaler, optional
        Fitted scaler from training (if not provided, creates new)
        
    Returns
    -------
    pd.DataFrame
        Evaluation results for each model
    """
    X = X_test.copy()
    
    if scale_features:
        if scaler is None:
            scaler = StandardScaler()
            X = pd.DataFrame(
                scaler.fit_transform(X),
                columns=X.columns,
                index=X.index,
            )
        else:
            X = pd.DataFrame(
                scaler.transform(X),
                columns=X.columns,
                index=X.index,
            )
    
    results = []
    
    for model_name, model in models.items():
        try:
            y_pred = model.predict(X)
            row = {"model": model_name}
            
            if task in ("binary", "multiclass"):
                # Classification metrics
                row["accuracy"] = accuracy_score(y_test, y_pred)
                row["balanced_accuracy"] = balanced_accuracy_score(y_test, y_pred)
                
                if task == "binary":
                    row["precision"] = precision_score(y_test, y_pred, zero_division=0)
                    row["recall"] = recall_score(y_test, y_pred, zero_division=0)
                    row["f1"] = f1_score(y_test, y_pred, zero_division=0)
                    
                    if hasattr(model, "predict_proba"):
                        y_proba = model.predict_proba(X)[:, 1]
                        row["roc_auc"] = roc_auc_score(y_test, y_proba)
                else:
                    row["f1_weighted"] = f1_score(y_test, y_pred, average="weighted", zero_division=0)
                    row["f1_macro"] = f1_score(y_test, y_pred, average="macro", zero_division=0)
            
            else:  # Regression
                row["r2"] = r2_score(y_test, y_pred)
                row["mae"] = mean_absolute_error(y_test, y_pred)
                row["rmse"] = np.sqrt(mean_squared_error(y_test, y_pred))
                row["mape"] = mean_absolute_percentage_error(y_test, y_pred)
            
            results.append(row)
        
        except Exception as e:
            print(f"Error evaluating {model_name}: {e}")
            continue
    
    return pd.DataFrame(results).sort_values(
        by=[col for col in results[0].keys() if col != "model"],
        ascending=False,
        key=lambda x: x.abs() if x.dtype in [float, int] else x,
    )


def get_model_feature_importance(
    model: Any,
    feature_names: List[str],
    top_n: int = 10,
) -> pd.DataFrame:
    """
    Extract feature importance from tree-based models.
    
    Parameters
    ----------
    model : sklearn model
        Trained tree-based model
    feature_names : list
        Feature column names
    top_n : int, default 10
        Top N features to return
        
    Returns
    -------
    pd.DataFrame
        Features with importance scores
    """
    if not hasattr(model, "feature_importances_"):
        return pd.DataFrame({"feature": [], "importance": []})
    
    importances = model.feature_importances_
    
    # Handle models like XGBoost with different attribute names
    if hasattr(model, "get_booster"):  # XGBoost
        importances = model.feature_importances_
    
    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": importances,
    }).sort_values("importance", ascending=False).head(top_n)
    
    return importance_df


# ============================================================================
# PIPELINE INTEGRATION
# ============================================================================

def run_full_model_selection(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    target_type: Literal["binary", "multiclass", "continuous", "count"],
    feature_stats: Optional[Dict[str, Any]] = None,
    sample_weight: Optional[np.ndarray] = None,
    n_cv_folds: int = 5,
    include_advanced: bool = True,
    include_neural: bool = False,
) -> Dict[str, Any]:
    """
    End-to-end model selection: suggest, train, evaluate, rank.
    
    This is the primary interface for the full model selection pipeline.
    
    Parameters
    ----------
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    X_test : pd.DataFrame
        Test features
    y_test : pd.Series
        Test target
    target_type : str
        From preprocessing.infer_target_type()
    feature_stats : dict, optional
        From statistics.calculate_summary()
    sample_weight : np.ndarray, optional
        Sample weights from preprocessing
    n_cv_folds : int, default 5
        Cross-validation folds
    include_advanced : bool, default True
        Include advanced boosting
    include_neural : bool, default False
        Include neural networks
        
    Returns
    -------
    dict
        Comprehensive results:
        - suggested_models: List of suggested model names
        - trained_models: Dict of trained models
        - cv_results: Cross-validation scores
        - test_results: Test set evaluation
        - best_model_name: Top performer
        - best_model: Best trained model instance
    """
    # Map target type to task
    task_map = {
        "binary": "binary",
        "multiclass": "multiclass",
        "continuous": "regression",
        "count": "count",
    }
    task = task_map.get(target_type, "binary")
    
    # Get data characteristics
    feature_correlation = None
    is_normal = None
    
    if feature_stats is not None:
        # Calculate average correlation
        numeric_cols = [col for col in X_train.columns 
                       if X_train[col].dtype in [float, int]]
        if len(numeric_cols) > 1:
            corr_matrix = X_train[numeric_cols].corr().abs()
            feature_correlation = corr_matrix.values[np.triu_indices_from(
                corr_matrix.values, k=1)].mean()
        
        # Get normality from feature stats if available
        if y_train.name in feature_stats.index:
            is_normal = feature_stats.loc[y_train.name, "normal"]
    
    # Step 1: Suggest models
    suggested_models = suggest_models(
        target_type=target_type,
        n_samples=len(X_train),
        n_features=X_train.shape[1],
        feature_correlation=feature_correlation,
        is_normal=is_normal,
        include_advanced=include_advanced,
        include_neural=include_neural,
    )
    
    print(f"Suggested models: {suggested_models}")
    
    # Step 2: Train models
    trained_models, cv_results = train_models(
        X_train, y_train,
        task=task,
        model_names=suggested_models,
        cv=n_cv_folds,
        sample_weight=sample_weight,
    )
    
    print(f"Trained {len(trained_models)} models")
    
    # Step 3: Evaluate on test set
    test_results = evaluate_models(
        trained_models,
        X_test, y_test,
        task=task,
    )
    
    print(f"Evaluation complete")
    
    # Step 4: Rank and select best
    if len(test_results) > 0:
        # Best model is first row (already sorted by metrics)
        best_model_name = test_results.iloc[0]["model"]
        best_model = trained_models[best_model_name]
    else:
        best_model_name = None
        best_model = None
    
    return {
        "target_type": target_type,
        "task": task,
        "suggested_models": suggested_models,
        "trained_models": trained_models,
        "cv_results": cv_results,
        "test_results": test_results,
        "best_model_name": best_model_name,
        "best_model": best_model,
        "feature_importance": (
            get_model_feature_importance(best_model, X_train.columns)
            if best_model is not None else None
        ),
    }


# ============================================================================
# Backward Compatibility Wrappers (Legacy API)
# ============================================================================

def train_models_legacy(X_train: pd.DataFrame, y_train: pd.Series) -> Dict[str, Any]:
    """[DEPRECATED] Legacy interface. Use train_models() instead."""
    trained_models, cv_results = train_models(
        X_train, y_train,
        task="binary",
        model_names=["Logistic Regression", "Decision Tree", "Random Forest", "Gradient Boosting"],
    )
    return trained_models


def evaluate_models_legacy(
    models: Dict[str, Any],
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> pd.DataFrame:
    """[DEPRECATED] Legacy interface. Use evaluate_models() instead."""
    return evaluate_models(models, X_test, y_test, task="binary")
