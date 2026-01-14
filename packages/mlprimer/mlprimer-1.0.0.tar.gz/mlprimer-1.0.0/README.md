# MLPrimer

[![PyPI version](https://badge.fury.io/py/mlprimer.svg)](https://pypi.org/project/mlprimer/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**MLPrimer** is a comprehensive, all-in-one Python package for fast ML model deployment. It automates the complete machine learning pipeline from exploratory data analysis through hyperparameter tuning, enabling rapid model selection and deployment.

##  Overview

MLPrimer orchestrates the entire ML workflow in a single function call:

\\\python
from mlprimer.bootstrap import run_pipeline

result = run_pipeline(df, target_var="target")
best_model = result.get_best_tuned_model()[1]
predictions = best_model.predict(X_new)
\\\

**Pipeline Stages:**
1.  **Statistics** - Feature analysis, normality testing, distribution profiling
2.  **Correlation** - Association testing (Pearson, Spearman, Chi-Square, ANOVA, t-tests)
3.  **Preprocessing** - Task-aware splitting, class balancing (SMOTE), target transforms
4.  **Model Selection** - 27+ models tested, automatic ranking
5.  **Tuning** - Hyperparameter optimization for top 5 models

##  Key Features

### Data Analysis
- **Comprehensive Statistics**: Mean, median, std, normality tests, outlier detection
- **Association Testing**: Pearson, Spearman, Chi-Square, Point-Biserial, ANOVA correlations
- **Target Type Detection**: Automatically infers binary, multiclass, regression, or count targets

### Preprocessing
- **Smart Splitting**: Stratified/grouped/time-series aware data splitting
- **Class Balancing**: SMOTE, under-sampling, class weighting
- **Target Transforms**: Yeo-Johnson, Box-Cox, log1p for skewed distributions
- **Sample Weighting**: Automatic weighting for imbalanced/regression tasks

### Model Selection (27+ Models)
- **Classification**: Logistic Regression, Random Forest, SVC, XGBoost, LightGBM, CatBoost, etc.
- **Regression**: ElasticNet, Ridge, Lasso, SVR, Random Forest, XGBoost, LightGBM, CatBoost, etc.
- **Robust Models**: Huber, RANSAC, Theil-Sen regressors
- **Neural Networks**: MLP Classifier/Regressor

### Hyperparameter Tuning
- **Multiple Search Methods**: GridSearch, RandomizedSearch, Successive Halving, Bayesian Optimization
- **Task-Aware CV**: StratifiedKFold for classification, KFold for regression, GroupKFold, TimeSeriesSplit
- **Multi-Metric Support**: Optimize one metric while tracking others
- **Predefined Grids**: Ready-to-use parameter grids for all models

### Export & Deployment
- **Model Export**: Save best model with metadata
- **Auto-Generated Scripts**: Fine-tuning, inference, comparison scripts
- **Results Export**: Feature importance, associations, model rankings

##  Installation

### From PyPI (Recommended)
\\\ash
pip install mlprimer
\\\

### From Source
\\\ash
git clone https://github.com/emrec/mlprimer.git
cd mlprimer
pip install -e .
\\\

### Optional Dependencies
For advanced features:
\\\ash
# For Bayesian optimization
pip install mlprimer[bayesian]

# For all boosting models (CatBoost, LightGBM, XGBoost)
pip install mlprimer[advanced]

# For everything
pip install mlprimer[all]
\\\

##  Quick Start

### Complete Pipeline
\\\python
import pandas as pd
from mlprimer.bootstrap import run_pipeline

# Load your data
df = pd.read_csv("data.csv")

# Run the complete pipeline
result = run_pipeline(
    df, 
    target_var="target",
    tune_top_n=5,
    verbose=2
)

# Get results
best_model_name, best_model = result.get_best_tuned_model()
top_5_models = result.get_top_models(n=5)

# Make predictions
predictions = best_model.predict(X_test)
\\\

### Step-by-Step Workflow
\\\python
import pandas as pd
from mlprimer.statistics import calculate_summary
from mlprimer.correlation import check_association
from mlprimer.preprocessing import infer_target_type, split_data, apply_smote_classification
from mlprimer.model_selection import run_full_model_selection
from mlprimer.tuning import tune_random

# 1. Analyze
df = pd.read_csv("data.csv")
feature_summary = calculate_summary(df)
associations = check_association(df, target_var="target")

# 2. Preprocess
target_type = infer_target_type(df["target"])
X_train, X_test, y_train, y_test = split_data(
    df.drop("target", axis=1), df["target"],
    task="classification"
)
X_train, y_train = apply_smote_classification(X_train, y_train)

# 3. Select Models
results = run_full_model_selection(
    X_train, y_train, X_test, y_test,
    target_type=target_type
)

# 4. Tune Best Model
best_model = results['best_model']
param_grid = {"n_estimators": [100, 200], "max_depth": [10, 20]}
tuned = tune_random(best_model, X_train, y_train, param_grid, task="binary")
\\\

### Export Models for Production
\\\python
from mlprimer.bootstrap import export_best_model, export_models, create_inference_script

# Export best model
export_best_model(result, "best_model.pkl")

# Export top 5 models
export_models(result, "saved_models/", include_top_n=5)

# Generate inference script
create_inference_script(result, "inference.py")
\\\

##  Documentation

### Core Modules

#### \statistics.py\
- \calculate_summary(df)\ - Comprehensive feature statistics
- \check_normal(x)\ - Normality testing

#### \correlation.py\
- \check_association(df, target_var)\ - Task-aware correlation testing
- \nalyze_associations(df, target_var)\ - Complete association workflow

#### \preprocessing.py\
- \infer_target_type(y)\ - Detect task type
- \eport_target_distribution(y, task)\ - Distribution profiling
- \split_data(X, y, task, stratify)\ - Task-aware splitting
- \pply_smote_classification(X, y)\ - SMOTE with categorical support
- \pply_target_transform(y, method)\ - Yeo-Johnson/Box-Cox transforms
- \make_sample_weights_regression(y)\ - Importance weighting

#### \model_selection.py\
- \un_full_model_selection(X_train, y_train, ...)\ - Complete model selection
- \suggest_models(target_type, ...)\ - Smart model recommendations
- \	rain_models(X_train, y_train, task)\ - Multi-model training
- \evaluate_models(models, X_test, y_test, task)\ - Task-aware evaluation

#### \	uning.py\
- \	une_grid(model, X, y, param_grid, task)\ - Exhaustive grid search
- \	une_random(model, X, y, param_distributions, task)\ - Randomized search
- \	une_halving_grid()\ - Efficient successive halving grid search
- \	une_halving_random()\ - Efficient successive halving random search
- \	une_bayesian()\ - Bayesian optimization (optional)
- \	une_with_calibration()\ - Probability calibration for classification

#### \ootstrap.py\
- \un_pipeline(df, target_var)\ - **Main entry point**
- \export_results()\ - Export all analysis results
- \export_best_model()\ - Save best model
- \export_models()\ - Save top N models
- \create_fine_tuning_script()\ - Generate tuning script
- \create_inference_script()\ - Generate inference script
- \create_comparison_script()\ - Generate model comparison script

##  Examples

### Binary Classification with Imbalanced Data
\\\python
from mlprimer.bootstrap import run_pipeline, print_pipeline_report

result = run_pipeline(
    df, 
    target_var="target",
    apply_preprocessing=True,  # Auto-applies SMOTE
    tune_method="random",
    tune_n_iter=50
)

print_pipeline_report(result)
best_model = result.get_best_tuned_model()[1]
\\\

### Regression with Skewed Target
\\\python
result = run_pipeline(
    df,
    target_var="price",
    apply_preprocessing=True,  # Auto-applies target transforms
    include_advanced_models=True,  # XGBoost, LightGBM, CatBoost
)
\\\

### Multiclass Classification
\\\python
result = run_pipeline(
    df,
    target_var="category",
    tune_top_n=5,
    verbose=2
)
\\\

##  Supported Tasks

| Task | Target Type | Models | Metrics |
|------|-------------|--------|---------|
| Binary Classification | 2 classes | 15+ | F1, AUC, Precision, Recall |
| Multiclass | 3+ classes | 15+ | F1-weighted, Balanced Accuracy |
| Regression | Continuous | 14+ | MAE, RMSE, R² |
| Count | Non-negative integers | 14+ | MAE, RMSE, Zero-inflation |

##  Advanced Features

### Custom Hyperparameter Grids
\\\python
from mlprimer.tuning import tune_random

custom_grid = {
    "n_estimators": [100, 200, 500],
    "max_depth": [10, 20, None],
    "learning_rate": [0.01, 0.05, 0.1],
}

result = tune_random(model, X_train, y_train, custom_grid, task="binary")
\\\

### Grouped Data
\\\python
from mlprimer.preprocessing import split_data

X_train, X_test, y_train, y_test = split_data(
    X, y,
    task="classification",
    groups=df["group_column"]
)
\\\

### Time Series
\\\python
X_train, X_test, y_train, y_test = split_data(
    X, y,
    task="regression",
    time_series=True
)
\\\

##  Architecture

\\\
Bootstrap.py (Orchestrator)
     statistics.py (EDA)
     correlation.py (Association Testing)
     preprocessing.py (Data Preparation)
     model_selection.py (Model Training & Ranking)
     tuning.py (Hyperparameter Optimization)
\\\

##  Requirements

- Python  3.8
- pandas  1.0
- numpy  1.18
- scikit-learn  0.24
- scipy  1.5
- imbalanced-learn  0.8

**Optional (for advanced features):**
- xgboost  1.0
- lightgbm  3.0
- catboost  1.0
- scikit-optimize (for Bayesian tuning)

##  Contributing

Contributions are welcome! Please open an issue or submit a pull request.

##  License

MIT License - see LICENSE file for details

##  Author

Emre Can Konca

##  Acknowledgments

Built on top of scikit-learn, XGBoost, LightGBM, CatBoost, and other excellent open-source ML libraries.
