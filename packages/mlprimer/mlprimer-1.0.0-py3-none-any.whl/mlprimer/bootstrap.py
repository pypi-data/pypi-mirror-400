from __future__ import annotations

import warnings
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from . import statistics
from . import correlation
from . import preprocessing
from . import model_selection
from . import tuning

warnings.filterwarnings("ignore")


@dataclass
class PipelineResult:
    """Complete pipeline execution result."""
    
    # Input
    X: pd.DataFrame
    y: pd.Series
    target_type: str
    
    # Analysis
    feature_summary: pd.DataFrame
    associations: pd.DataFrame
    
    # Preprocessing
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    preprocessor_info: Dict[str, Any]
    
    # Model Selection
    suggested_models: List[str]
    trained_models: Dict[str, Any]
    model_cv_results: pd.DataFrame
    model_test_results: pd.DataFrame
    best_model_name: str
    
    # Tuning (Top 5)
    tuned_models: Dict[str, tuning.SearchResult]
    
    def summary(self) -> Dict[str, Any]:
        """Get high-level summary of pipeline."""
        return {
            "n_samples": len(self.X),
            "n_features": self.X.shape[1],
            "target_type": self.target_type,
            "train_size": len(self.X_train),
            "test_size": len(self.X_test),
            "suggested_models": self.suggested_models,
            "initial_best_model": self.best_model_name,
            "tuned_models_count": len(self.tuned_models),
            "tuned_model_names": list(self.tuned_models.keys()),
        }
    
    def get_best_tuned_model(self) -> Tuple[str, Any]:
        """
        Get the best tuned model by CV score.
        
        Returns
        -------
        tuple
            (model_name, best_estimator)
        """
        if not self.tuned_models:
            return self.best_model_name, self.trained_models[self.best_model_name]
        
        # Find model with highest CV score
        best_model_name = max(
            self.tuned_models.keys(),
            key=lambda name: self.tuned_models[name].best_score
        )
        best_result = self.tuned_models[best_model_name]
        
        return best_model_name, best_result.best_estimator
    
    def get_top_models(self, n: int = 5) -> Dict[str, Any]:
        """
        Get top N tuned models sorted by score.
        
        Parameters
        ----------
        n : int, default 5
            Number of top models
            
        Returns
        -------
        dict
            {model_name: best_estimator, ...}
        """
        sorted_models = sorted(
            self.tuned_models.items(),
            key=lambda x: x[1].best_score,
            reverse=True
        )
        
        return {name: result.best_estimator for name, result in sorted_models[:n]}


def run_pipeline(
    df: pd.DataFrame,
    target_var: str,
    feature_cols: Optional[List[str]] = None,
    *,
    test_size: float = 0.2,
    cv_folds: int = 5,
    tune_top_n: int = 5,
    tune_method: str = "random",
    tune_n_iter: int = 30,
    include_advanced_models: bool = True,
    include_neural_models: bool = False,
    apply_preprocessing: bool = True,
    random_state: int = 42,
    verbose: int = 1,
) -> PipelineResult:
    """
    Run complete ML pipeline: EDA → preprocessing → model selection → tuning.
    
    This is the main entry point for fast model deployment.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input data
    target_var : str
        Name of target column
    feature_cols : list, optional
        List of feature column names. If None, uses all except target_var.
    test_size : float, default 0.2
        Test set proportion
    cv_folds : int, default 5
        Cross-validation folds
    tune_top_n : int, default 5
        Number of top models to fine-tune
    tune_method : {"random", "grid", "halving"}, default "random"
        Hyperparameter search method
    tune_n_iter : int, default 30
        Iterations for random/halving search
    include_advanced_models : bool, default True
        Include XGBoost, LightGBM, CatBoost
    include_neural_models : bool, default False
        Include MLPClassifier/MLPRegressor
    apply_preprocessing : bool, default True
        Apply SMOTE/transformations (recommended for imbalanced data)
    random_state : int, default 42
        Random seed for reproducibility
    verbose : int, default 1
        Verbosity level (0=silent, 1=normal, 2=detailed)
        
    Returns
    -------
    PipelineResult
        Complete pipeline results with tuned models
        
    Examples
    --------
    >>> result = run_pipeline(df, target_var='target')
    >>> best_model_name, best_model = result.get_best_tuned_model()
    >>> predictions = best_model.predict(X_test)
    """
    
    if verbose >= 1:
        print("=" * 80)
        print("MLPRIMER PIPELINE: Complete ML Deployment")
        print("=" * 80)
    
    # ========================================================================
    # STEP 1: DATA PREPARATION
    # ========================================================================
    if verbose >= 1:
        print("\n[STEP 1/5] Data Preparation...")
    
    if target_var not in df.columns:
        raise KeyError(f"Target variable '{target_var}' not in DataFrame")
    
    if feature_cols is None:
        feature_cols = [col for col in df.columns if col != target_var]
    
    X = df[feature_cols].copy()
    y = df[target_var].copy()
    
    if verbose >= 2:
        print(f"  - Features: {X.shape[1]} columns, {X.shape[0]} samples")
        print(f"  - Target: {y.dtype}, {y.nunique()} unique values")
    
    # ========================================================================
    # STEP 2: EXPLORATORY ANALYSIS
    # ========================================================================
    if verbose >= 1:
        print("\n[STEP 2/5] Exploratory Analysis...")
    
    # Feature statistics
    feature_summary = statistics.calculate_summary(X)
    
    # Target-feature associations
    associations = correlation.check_association(
        pd.concat([X, y.rename(target_var)], axis=1),
        target_var=target_var,
    )
    
    # Infer target type
    target_type = preprocessing.infer_target_type(y)
    
    if verbose >= 2:
        print(f"  - Target type: {target_type}")
        print(f"  - Feature summary: {feature_summary.shape[0]} features analyzed")
        print(f"  - Associations: {associations.shape[0]} features ranked")
    
    # ========================================================================
    # STEP 3: DATA PREPROCESSING & SPLITTING
    # ========================================================================
    if verbose >= 1:
        print("\n[STEP 3/5] Preprocessing & Splitting...")
    
    # Map target type to task
    task_map = {
        "binary": "classification",
        "multiclass": "classification",
        "continuous": "regression",
        "count": "count",
    }
    task = task_map.get(target_type, "classification")
    
    # Split data with stratification for classification
    X_train, X_test, y_train, y_test = preprocessing.split_data(
        X, y,
        task=task,
        test_size=test_size,
        stratify=True if task == "classification" else False,
        random_state=random_state,
    )
    
    if verbose >= 2:
        print(f"  - Train set: {len(X_train)} samples")
        print(f"  - Test set: {len(X_test)} samples")
    
    # Apply preprocessing (balancing, transforms)
    preprocessor_info = {}
    
    if apply_preprocessing:
        if target_type in ("binary", "multiclass"):
            # Check class distribution
            dist_report = preprocessing.report_target_distribution(y_train, task="classification")
            imbalance_ratio = dist_report.get("imbalance_ratio", 1.0)
            
            if imbalance_ratio > 1.5:
                if verbose >= 2:
                    print(f"  - Imbalance detected (ratio: {imbalance_ratio:.2f})")
                    print(f"  - Applying SMOTE...")
                
                X_train, y_train = preprocessing.apply_smote_classification(X_train, y_train)
                preprocessor_info["smote_applied"] = True
                
                if verbose >= 2:
                    print(f"  - After SMOTE: {len(X_train)} samples")
        
        elif target_type == "continuous":
            # Check for skewness and apply transform if needed
            dist_report = preprocessing.report_target_distribution(y_train, task="regression")
            skewness = dist_report.get("skewness", 0)
            
            if abs(skewness) > 1.0:
                if verbose >= 2:
                    print(f"  - Skewed distribution detected (skewness: {skewness:.2f})")
                    print(f"  - Applying Yeo-Johnson transform...")
                
                y_train, transformer = preprocessing.apply_target_transform(
                    y_train, method="yeo-johnson"
                )
                preprocessor_info["target_transform"] = "yeo-johnson"
                preprocessor_info["target_transformer"] = transformer
    
    if verbose >= 2:
        print(f"  - Preprocessor info: {preprocessor_info}")
    
    # ========================================================================
    # STEP 4: MODEL SELECTION & TRAINING
    # ========================================================================
    if verbose >= 1:
        print("\n[STEP 4/5] Model Selection & Initial Training...")
    
    selection_results = model_selection.run_full_model_selection(
        X_train, y_train, X_test, y_test,
        target_type=target_type,
        feature_stats=feature_summary,
        n_cv_folds=cv_folds,
        include_advanced=include_advanced_models,
        include_neural=include_neural_models,
    )
    
    suggested_models = selection_results["suggested_models"]
    trained_models = selection_results["trained_models"]
    best_model_name = selection_results["best_model_name"]
    
    if verbose >= 2:
        print(f"  - Suggested models: {len(suggested_models)}")
        print(f"  - Trained models: {len(trained_models)}")
        print(f"  - Initial best: {best_model_name}")
    
    # ========================================================================
    # STEP 5: HYPERPARAMETER TUNING (TOP MODELS)
    # ========================================================================
    if verbose >= 1:
        print(f"\n[STEP 5/5] Hyperparameter Tuning (Top {tune_top_n} Models)...")
    
    # Get test results and select top N models
    test_results = selection_results["test_results"]
    top_models_to_tune = test_results.head(tune_top_n)["model"].tolist()
    
    tuned_models = {}
    
    for i, model_name in enumerate(top_models_to_tune, 1):
        try:
            if verbose >= 2:
                print(f"  [{i}/{len(top_models_to_tune)}] Tuning {model_name}...")
            
            model = trained_models[model_name]
            
            # Get parameter grid
            param_grid = tuning.get_param_grid(model_name, search_space="balanced")
            
            if param_grid is None:
                if verbose >= 2:
                    print(f"       → No predefined grid; skipping tuning")
                continue
            
            # Select scoring
            scoring = tuning.TASK_SCORING_DEFAULTS[target_type]["default"]
            
            # Tune based on method
            if tune_method == "grid":
                result = tuning.tune_grid(
                    model, X_train, y_train, param_grid,
                    task=target_type,
                    scoring=scoring,
                    cv=cv_folds,
                    random_state=random_state,
                    verbose=0,
                )
            elif tune_method == "halving":
                result = tuning.tune_halving_random(
                    model, X_train, y_train, param_grid,
                    n_candidates=tune_n_iter,
                    task=target_type,
                    scoring=scoring,
                    cv=cv_folds,
                    random_state=random_state,
                    verbose=0,
                )
            else:  # random (default)
                result = tuning.tune_random(
                    model, X_train, y_train, param_grid,
                    n_iter=tune_n_iter,
                    task=target_type,
                    scoring=scoring,
                    cv=cv_folds,
                    random_state=random_state,
                    verbose=0,
                )
            
            tuned_models[model_name] = result
            
            if verbose >= 2:
                print(f"       → Best score: {result.best_score:.4f}")
                print(f"       → Best params: {result.best_params}")
        
        except Exception as e:
            if verbose >= 1:
                print(f"  [WARNING] Failed to tune {model_name}: {e}")
            continue
    
    if verbose >= 1:
        print(f"\n✓ Successfully tuned {len(tuned_models)} models")
    
    # ========================================================================
    # RESULTS
    # ========================================================================
    if verbose >= 1:
        print("\n" + "=" * 80)
        print("PIPELINE COMPLETE")
        print("=" * 80)
    
    return PipelineResult(
        X=X,
        y=y,
        target_type=target_type,
        feature_summary=feature_summary,
        associations=associations,
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        preprocessor_info=preprocessor_info,
        suggested_models=suggested_models,
        trained_models=trained_models,
        model_cv_results=selection_results["cv_results"],
        model_test_results=selection_results["test_results"],
        best_model_name=best_model_name,
        tuned_models=tuned_models,
    )


def quick_run(
    df: pd.DataFrame,
    target_var: str,
    **kwargs
) -> PipelineResult:
    """
    Shorthand for run_pipeline with default settings.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input data
    target_var : str
        Target column name
    **kwargs
        Additional arguments for run_pipeline
        
    Returns
    -------
    PipelineResult
        Pipeline results
    """
    return run_pipeline(df, target_var, **kwargs)


# ============================================================================
# REPORTING & EXPORT UTILITIES
# ============================================================================

# ============================================================================
# REPORTING & EXPORT UTILITIES
# ============================================================================

def print_pipeline_report(result: PipelineResult, top_n: int = 5) -> None:
    """
    Print comprehensive pipeline report.
    
    Parameters
    ----------
    result : PipelineResult
        Pipeline results
    top_n : int, default 5
        Number of top models to display
    """
    print("\n" + "=" * 80)
    print("PIPELINE REPORT")
    print("=" * 80)
    
    summary = result.summary()
    print("\n[DATA SUMMARY]")
    print(f"  Samples: {summary['n_samples']}")
    print(f"  Features: {summary['n_features']}")
    print(f"  Target Type: {summary['target_type']}")
    print(f"  Train/Test Split: {summary['train_size']} / {summary['test_size']}")
    
    print("\n[MODEL SELECTION]")
    print(f"  Suggested Models: {len(summary['suggested_models'])}")
    print(f"  Initial Best: {summary['initial_best_model']}")
    print(f"  Models Tuned: {summary['tuned_models_count']}")
    
    print("\n[TOP MODELS (by CV score)]")
    sorted_models = sorted(
        result.tuned_models.items(),
        key=lambda x: x[1].best_score,
        reverse=True
    )
    
    for i, (name, result_obj) in enumerate(sorted_models[:top_n], 1):
        print(f"  {i}. {name}: {result_obj.best_score:.4f}")
        print(f"     Params: {result_obj.best_params}")
    
    print("\n[FEATURE ASSOCIATIONS (Top 10)]")
    top_associations = result.associations.head(10)
    for col, row in top_associations.iterrows():
        print(f"  {col}: {row['test_method']} (p={row['p_value']:.4f})")
    
    print("\n" + "=" * 80)


def export_results(
    result: PipelineResult,
    output_dir: str,
) -> None:
    """
    Export complete pipeline results to directory.
    
    Exports:
    - feature_summary.csv
    - associations.csv
    - model_test_results.csv
    - model_cv_results.csv
    - tuned_models_summary.csv
    - pipeline_metadata.json
    
    Parameters
    ----------
    result : PipelineResult
        Pipeline results
    output_dir : str
        Directory to save results
        
    Examples
    --------
    >>> export_results(result, "pipeline_results/")
    """
    import os
    import json
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Export DataFrames
    result.feature_summary.to_csv(os.path.join(output_dir, "feature_summary.csv"))
    result.associations.to_csv(os.path.join(output_dir, "associations.csv"))
    result.model_test_results.to_csv(os.path.join(output_dir, "model_test_results.csv"), index=False)
    result.model_cv_results.to_csv(os.path.join(output_dir, "model_cv_results.csv"))
    
    # Export tuned models summary
    tuned_summary = []
    for model_name, search_result in sorted(
        result.tuned_models.items(),
        key=lambda x: x[1].best_score,
        reverse=True
    ):
        tuned_summary.append({
            "rank": len(tuned_summary) + 1,
            "model_name": model_name,
            "best_score": float(search_result.best_score),
            "best_params": str(search_result.best_params),
            "scoring": str(search_result.scoring),
        })
    
    pd.DataFrame(tuned_summary).to_csv(
        os.path.join(output_dir, "tuned_models_summary.csv"),
        index=False
    )
    
    # Export metadata
    metadata = {
        "target_type": result.target_type,
        "n_samples": int(result.X.shape[0]),
        "n_features": int(result.X.shape[1]),
        "n_train": int(len(result.X_train)),
        "n_test": int(len(result.X_test)),
        "feature_columns": result.X.columns.tolist(),
        "target_variable": str(result.y.name),
        "suggested_models": result.suggested_models,
        "initial_best_model": result.best_model_name,
        "n_tuned_models": len(result.tuned_models),
        "tuned_model_names": list(result.tuned_models.keys()),
        "preprocessor_info": result.preprocessor_info,
    }
    
    with open(os.path.join(output_dir, "pipeline_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Results exported to {output_dir}")
    print(f"  - feature_summary.csv")
    print(f"  - associations.csv")
    print(f"  - model_test_results.csv")
    print(f"  - model_cv_results.csv")
    print(f"  - tuned_models_summary.csv")
    print(f"  - pipeline_metadata.json")


def export_models(
    result: PipelineResult,
    output_dir: str,
    include_top_n: int = 5,
) -> None:
    """
    Export top N tuned models individually.
    
    Parameters
    ----------
    result : PipelineResult
        Pipeline results
    output_dir : str
        Directory to save models
    include_top_n : int, default 5
        Number of top models to export
        
    Examples
    --------
    >>> export_models(result, "saved_models/", include_top_n=5)
    """
    import os
    import pickle
    
    os.makedirs(output_dir, exist_ok=True)
    
    sorted_models = sorted(
        result.tuned_models.items(),
        key=lambda x: x[1].best_score,
        reverse=True
    )
    
    for i, (model_name, search_result) in enumerate(sorted_models[:include_top_n], 1):
        # Sanitize model name for filename
        safe_name = model_name.lower().replace(" ", "_")
        filepath = os.path.join(output_dir, f"{i:02d}_{safe_name}_model.pkl")
        
        model_data = {
            "rank": i,
            "model_name": model_name,
            "model": search_result.best_estimator,
            "best_params": search_result.best_params,
            "best_score": search_result.best_score,
            "scoring": search_result.scoring,
            "target_type": result.target_type,
            "feature_columns": result.X.columns.tolist(),
            "target_variable": result.y.name,
            "preprocessor_info": result.preprocessor_info,
            "cv_results": search_result.cv_results,
        }
        
        with open(filepath, "wb") as f:
            pickle.dump(model_data, f)
        
        print(f"✓ Exported ({i}/{include_top_n}): {model_name} → {filepath}")


def export_best_model(
    result: PipelineResult,
    filepath: str,
    include_preprocessor: bool = True,
) -> None:
    """
    Export best tuned model to file.
    
    Parameters
    ----------
    result : PipelineResult
        Pipeline results
    filepath : str
        Path to save model (pickle format)
    include_preprocessor : bool, default True
        Include preprocessor info in export
        
    Examples
    --------
    >>> export_best_model(result, "best_model.pkl")
    """
    import pickle
    
    model_name, best_model = result.get_best_tuned_model()
    best_result = result.tuned_models[model_name]
    
    export_data = {
        "model": best_model,
        "model_name": model_name,
        "best_params": best_result.best_params,
        "best_score": best_result.best_score,
        "target_type": result.target_type,
        "feature_columns": result.X.columns.tolist(),
        "target_variable": result.y.name,
        "preprocessor_info": result.preprocessor_info if include_preprocessor else None,
        "cv_results": best_result.cv_results if hasattr(best_result, 'cv_results') else None,
    }
    
    with open(filepath, "wb") as f:
        pickle.dump(export_data, f)
    
    print(f"✓ Best model exported: {model_name}")
    print(f"  File: {filepath}")
    print(f"  CV Score: {best_result.best_score:.4f}")


def load_model(filepath: str) -> Dict[str, Any]:
    """
    Load exported model with metadata.
    
    Parameters
    ----------
    filepath : str
        Path to saved model
        
    Returns
    -------
    dict
        Model data including:
        - model: sklearn estimator
        - model_name: str
        - best_params: dict
        - best_score: float
        - target_type: str
        - feature_columns: list
        - target_variable: str
        - preprocessor_info: dict
        - cv_results: pd.DataFrame (if available)
        
    Examples
    --------
    >>> model_data = load_model("best_model.pkl")
    >>> model = model_data['model']
    >>> predictions = model.predict(X_new)
    """
    import pickle
    
    with open(filepath, "rb") as f:
        model_data = pickle.load(f)
    
    return model_data


def get_model_comparison_df(result: PipelineResult) -> pd.DataFrame:
    """
    Get detailed comparison DataFrame of all tuned models.
    
    Parameters
    ----------
    result : PipelineResult
        Pipeline results
        
    Returns
    -------
    pd.DataFrame
        Comparison with model name, score, params, and stats
    """
    comparison_rows = []
    
    sorted_models = sorted(
        result.tuned_models.items(),
        key=lambda x: x[1].best_score,
        reverse=True
    )
    
    for rank, (model_name, search_result) in enumerate(sorted_models, 1):
        row = {
            "rank": rank,
            "model": model_name,
            "cv_score": search_result.best_score,
            "n_params": len(search_result.best_params),
            "cv_std": search_result.cv_results["std_test_score"].iloc[0] if len(search_result.cv_results) > 0 else np.nan,
            "params": str(search_result.best_params),
            "scoring": str(search_result.scoring),
        }
        comparison_rows.append(row)
    
    return pd.DataFrame(comparison_rows)


# ============================================================================
# SEPARATE SCRIPT UTILITIES
# ============================================================================

def create_fine_tuning_script(
    result: PipelineResult,
    output_filepath: str = "fine_tune_model.py",
) -> None:
    """
    Generate a standalone Python script for fine-tuning a specific model.
    
    The generated script can be run independently to continue tuning.
    
    Parameters
    ----------
    result : PipelineResult
        Pipeline results
    output_filepath : str, default "fine_tune_model.py"
        Path to save the generated script
        
    Examples
    --------
    >>> create_fine_tuning_script(result, "fine_tune.py")
    >>> # Then run: python fine_tune.py
    """
    model_name, best_model = result.get_best_tuned_model()
    
    script_template = f'''"""
Auto-generated fine-tuning script for {model_name}.

Generated from mlprimer pipeline.
Edit param_grid to customize hyperparameter search.
"""

import pandas as pd
import numpy as np
import pickle
from mlprimer.tuning import tune_random, get_param_grid

# ============================================================================
# CONFIGURATION
# ============================================================================

# Load your training data
X_train = pd.read_csv("X_train.csv")  # Replace with your data
y_train = pd.read_csv("y_train.csv").squeeze()  # Replace with your data

TARGET_TYPE = "{result.target_type}"
TUNE_METHOD = "random"  # or "grid", "halving"
N_ITERATIONS = 50
CV_FOLDS = 5
RANDOM_STATE = 42

# ============================================================================
# LOAD PREVIOUSLY TUNED MODEL
# ============================================================================

with open("best_model.pkl", "rb") as f:  # From export_best_model()
    model_data = pickle.load(f)

model = model_data["model"]
model_name = model_data["model_name"]
previous_best_params = model_data["best_params"]
previous_best_score = model_data["best_score"]

print(f"Loaded: {{model_name}}")
print(f"Previous best score: {{previous_best_score:.4f}}")
print(f"Previous best params: {{previous_best_params}}")

# ============================================================================
# DEFINE CUSTOM PARAMETER GRID
# ============================================================================

# Start with previous best params and expand search space
param_grid = {{
    # Example for RandomForest:
    # "n_estimators": [100, 200, 500, 1000],
    # "max_depth": [5, 10, 15, 20, None],
    # "min_samples_split": [2, 5, 10],
    # "min_samples_leaf": [1, 2, 4],
    
    # Modify for your model class and needs
}}

# Or use predefined grid (adjust scope as needed)
if not param_grid:
    from mlprimer.tuning import PARAM_GRIDS
    if model_name in PARAM_GRIDS:
        param_grid = PARAM_GRIDS[model_name]["balanced"]  # or "small", "large"
    else:
        print(f"Warning: No predefined grid for {{model_name}}")
        param_grid = {{}}: # Define your own

# ============================================================================
# RUN FINE-TUNING SEARCH
# ============================================================================

print("\\nStarting fine-tuning search...")
print(f"Method: {{TUNE_METHOD}}")
print(f"Iterations: {{N_ITERATIONS}}")
print(f"CV Folds: {{CV_FOLDS}}")

search_result = tune_random(
    model,
    X_train, y_train,
    param_grid,
    n_iter=N_ITERATIONS,
    task=TARGET_TYPE,
    scoring=None,  # Uses task default
    cv=CV_FOLDS,
    random_state=RANDOM_STATE,
    verbose=2,
)

# ============================================================================
# RESULTS
# ============================================================================

print("\\n" + "="*80)
print("FINE-TUNING COMPLETE")
print("="*80)

print(f"\\nNew Best Score: {{search_result.best_score:.4f}}")
print(f"Previous Score: {{previous_best_score:.4f}}")
improvement = search_result.best_score - previous_best_score
print(f"Improvement: {{improvement:+.4f}}")

print(f"\\nNew Best Parameters:")
for param, value in search_result.best_params.items():
    print(f"  {{param}}: {{value}}")

print(f"\\nTop 5 Results:")
print(search_result.summary(top_n=5))

# ============================================================================
# EXPORT FINE-TUNED MODEL
# ============================================================================

fine_tuned_data = {{
    "model": search_result.best_estimator,
    "model_name": model_name,
    "best_params": search_result.best_params,
    "best_score": search_result.best_score,
    "previous_score": previous_best_score,
    "improvement": improvement,
    "cv_results": search_result.cv_results,
}}

output_path = "fine_tuned_model.pkl"
with open(output_path, "wb") as f:
    pickle.dump(fine_tuned_data, f)

print(f"\\n✓ Fine-tuned model exported: {{output_path}}")
'''
    
    with open(output_filepath, "w") as f:
        f.write(script_template)
    
    print(f"✓ Fine-tuning script created: {output_filepath}")
    print(f"  Edit param_grid and run: python {output_filepath}")


def create_inference_script(
    result: PipelineResult,
    output_filepath: str = "inference.py",
) -> None:
    """
    Generate a standalone Python script for inference with the best model.
    
    Parameters
    ----------
    result : PipelineResult
        Pipeline results
    output_filepath : str, default "inference.py"
        Path to save the generated script
        
    Examples
    --------
    >>> create_inference_script(result, "inference.py")
    >>> # Then run: python inference.py
    """
    
    script_template = '''"""
Auto-generated inference script.

Load a trained model and make predictions on new data.
"""

import pandas as pd
import numpy as np
import pickle

# ============================================================================
# CONFIGURATION
# ============================================================================

MODEL_PATH = "best_model.pkl"  # Path to exported model
DATA_PATH = "new_data.csv"     # Path to data for prediction

# ============================================================================
# LOAD MODEL
# ============================================================================

with open(MODEL_PATH, "rb") as f:
    model_data = pickle.load(f)

model = model_data["model"]
model_name = model_data["model_name"]
feature_columns = model_data["feature_columns"]
target_type = model_data["target_type"]
preprocessor_info = model_data.get("preprocessor_info", {})

print(f"Loaded model: {model_name}")
print(f"Target type: {target_type}")
print(f"Features expected: {len(feature_columns)}")

# ============================================================================
# LOAD DATA
# ============================================================================

df = pd.read_csv(DATA_PATH)
print(f"\\nData shape: {df.shape}")

# Select feature columns
if set(feature_columns).issubset(df.columns):
    X = df[feature_columns]
    print(f"✓ All required features found")
else:
    missing = set(feature_columns) - set(df.columns)
    print(f"✗ Missing features: {missing}")
    X = df[[col for col in feature_columns if col in df.columns]]

# ============================================================================
# MAKE PREDICTIONS
# ============================================================================

print("\\nGenerating predictions...")

predictions = model.predict(X)

# For classification models with predict_proba
if hasattr(model, "predict_proba") and target_type in ["binary", "multiclass"]:
    probabilities = model.predict_proba(X)
    print(f"Probabilities shape: {probabilities.shape}")

# ============================================================================
# RESULTS
# ============================================================================

if target_type in ["binary", "multiclass"]:
    print(f"\\nPredictions (class labels):")
    print(f"  Shape: {predictions.shape}")
    print(f"  Unique classes: {np.unique(predictions)}")
    print(f"  Sample predictions: {predictions[:5]}")
    
    if hasattr(model, "predict_proba"):
        print(f"\\nPrediction probabilities:")
        print(f"  Shape: {probabilities.shape}")
        print(f"  Sample (first 3 samples):")
        print(probabilities[:3])
else:
    print(f"\\nRegression predictions:")
    print(f"  Shape: {predictions.shape}")
    print(f"  Mean: {predictions.mean():.4f}")
    print(f"  Std: {predictions.std():.4f}")
    print(f"  Min: {predictions.min():.4f}")
    print(f"  Max: {predictions.max():.4f}")
    print(f"  Sample predictions: {predictions[:5]}")

# ============================================================================
# EXPORT PREDICTIONS
# ============================================================================

output_df = pd.DataFrame({{
    "prediction": predictions,
}})

if target_type in ["binary", "multiclass"] and hasattr(model, "predict_proba"):
    classes = model.classes_
    for i, cls in enumerate(classes):
        output_df[f"prob_{cls}"] = probabilities[:, i]

output_path = "predictions.csv"
output_df.to_csv(output_path, index=False)

print(f"\\n✓ Predictions exported: {output_path}")
'''
    
    with open(output_filepath, "w") as f:
        f.write(script_template)
    
    print(f"✓ Inference script created: {output_filepath}")
    print(f"  Run: python {output_filepath}")


def create_comparison_script(
    result: PipelineResult,
    output_filepath: str = "compare_models.py",
) -> None:
    """
    Generate a standalone script to compare all tuned models.
    
    Parameters
    ----------
    result : PipelineResult
        Pipeline results
    output_filepath : str, default "compare_models.py"
        Path to save the generated script
        
    Examples
    --------
    >>> create_comparison_script(result, "compare_models.py")
    >>> # Then run: python compare_models.py
    """
    
    script_template = '''"""
Auto-generated model comparison script.

Load all tuned models and compare predictions on test data.
"""

import pandas as pd
import numpy as np
import pickle
import glob
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

MODEL_DIR = "saved_models/"  # Directory with exported models
X_TEST_PATH = "X_test.csv"   # Test features
Y_TEST_PATH = "y_test.csv"   # Test target (for evaluation)

# ============================================================================
# LOAD MODELS
# ============================================================================

print("Loading models from:", MODEL_DIR)
model_files = sorted(glob.glob(f"{MODEL_DIR}*.pkl"))

if not model_files:
    print(f"✗ No models found in {MODEL_DIR}")
    exit(1)

models = {}
for filepath in model_files:
    with open(filepath, "rb") as f:
        data = pickle.load(f)
    model_name = data["model_name"]
    models[model_name] = data
    print(f"✓ Loaded: {model_name} (score: {data['best_score']:.4f})")

# ============================================================================
# LOAD TEST DATA
# ============================================================================

X_test = pd.read_csv(X_TEST_PATH)
y_test = pd.read_csv(Y_TEST_PATH).squeeze()

print(f"\\nTest set: {X_test.shape[0]} samples, {X_test.shape[1]} features")

# ============================================================================
# COMPARE PREDICTIONS
# ============================================================================

print("\\n" + "="*80)
print("MODEL COMPARISON")
print("="*80)

comparison_results = []

for model_name, model_data in models.items():
    model = model_data["model"]
    
    # Make predictions
    predictions = model.predict(X_test)
    
    # Evaluate if regression or classification
    target_type = model_data.get("target_type", "binary")
    
    if target_type in ["binary", "multiclass"]:
        from sklearn.metrics import accuracy_score, f1_score, balanced_accuracy_score
        
        accuracy = accuracy_score(y_test, predictions)
        f1 = f1_score(y_test, predictions, average="weighted" if target_type == "multiclass" else "binary")
        balanced_acc = balanced_accuracy_score(y_test, predictions)
        
        result_row = {{
            "model": model_name,
            "cv_score": model_data["best_score"],
            "test_accuracy": accuracy,
            "test_f1": f1,
            "test_balanced_acc": balanced_acc,
        }}
    else:
        from sklearn.metrics import mean_absolute_error, r2_score
        
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        result_row = {{
            "model": model_name,
            "cv_score": model_data["best_score"],
            "test_mae": mae,
            "test_r2": r2,
        }}
    
    comparison_results.append(result_row)
    
    print(f"\\n{model_name}:")
    print(f"  CV Score: {{model_data['best_score']:.4f}}")
    for key, value in result_row.items():
        if key not in ["model", "cv_score"]:
            print(f"  {{key}}: {{value:.4f}}")

# ============================================================================
# EXPORT COMPARISON
# ============================================================================

comparison_df = pd.DataFrame(comparison_results)
comparison_df = comparison_df.sort_values(by="cv_score", ascending=False)

output_path = "model_comparison.csv"
comparison_df.to_csv(output_path, index=False)

print("\\n" + "="*80)
print(f"✓ Comparison exported: {output_path}")
print("\\nTop Model:")
print(comparison_df.iloc[0])
'''
    
    with open(output_filepath, "w") as f:
        f.write(script_template)
    
    print(f"✓ Comparison script created: {output_filepath}")
    print(f"  Run: python {output_filepath}")


def extract_tuning_report(result: PipelineResult) -> pd.DataFrame:
    """
    Extract detailed tuning report for each model.
    
    Parameters
    ----------
    result : PipelineResult
        Pipeline results
        
    Returns
    -------
    pd.DataFrame
        Detailed tuning report with all information
    """
    reports = []
    
    sorted_models = sorted(
        result.tuned_models.items(),
        key=lambda x: x[1].best_score,
        reverse=True
    )
    
    for rank, (model_name, search_result) in enumerate(sorted_models, 1):
        report = {
            "rank": rank,
            "model_name": model_name,
            "best_cv_score": search_result.best_score,
            "best_cv_std": search_result.cv_results["std_test_score"].iloc[0] if len(search_result.cv_results) > 0 else np.nan,
            "n_evals": len(search_result.cv_results),
            "n_params": len(search_result.best_params),
            "scoring_metric": str(search_result.scoring),
            "best_params_str": str(search_result.best_params),
        }
        reports.append(report)
    
    return pd.DataFrame(reports)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the complete pipeline.
    
    To run:
        from mlprimer.bootstrap import run_pipeline
        
        df = pd.read_csv("data.csv")
        result = run_pipeline(df, target_var="target", verbose=2)
        
        # Get best model
        best_model_name, best_model = result.get_best_tuned_model()
        
        # Get top 5 models
        top_5 = result.get_top_models(n=5)
        
        # Print report
        from mlprimer.bootstrap import print_pipeline_report
        print_pipeline_report(result)
        
        # Export best model
        from mlprimer.bootstrap import export_best_model
        export_best_model(result, "best_model.pkl")
    """
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                    MLPRIMER - COMPLETE ML PIPELINE                           ║
    ║                     Fast Model Selection & Deployment                        ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    
    To get started with the pipeline:
    
    1. Import and load your data:
       >>> import pandas as pd
       >>> from mlprimer.bootstrap import run_pipeline
       >>> df = pd.read_csv("your_data.csv")
    
    2. Run the complete pipeline:
       >>> result = run_pipeline(df, target_var="target", verbose=2)
    
    3. Get results:
       >>> best_model_name, best_model = result.get_best_tuned_model()
       >>> top_5_models = result.get_top_models(n=5)
    
    4. Make predictions:
       >>> predictions = best_model.predict(X_test)
       >>> probabilities = best_model.predict_proba(X_test)
    
    5. Export for production:
       >>> from mlprimer.bootstrap import export_best_model
       >>> export_best_model(result, "best_model.pkl")
    
    Pipeline stages:
    ✓ Feature Analysis (statistics)
    ✓ Association Testing (correlation)
    ✓ Data Preprocessing (splitting, balancing, transforms)
    ✓ Model Selection (27+ models tested)
    ✓ Hyperparameter Tuning (top 5 models fine-tuned)
    
    Results: Top 5 tuned models ready for deployment
    """)
