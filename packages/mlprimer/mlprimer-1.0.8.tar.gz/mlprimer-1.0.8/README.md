# MLPrimer

[![PyPI version](https://badge.fury.io/py/mlprimer.svg)](https://pypi.org/project/mlprimer/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**MLPrimer** is an all-in-one Python package for rapid machine learning experimentation and deployment.  
It automates the full ML workflow—from exploratory data analysis to model selection and hyperparameter tuning—behind a consistent, task-aware API.

---

## Overview

MLPrimer orchestrates the complete ML pipeline with a single function call.

```python
from mlprimer.bootstrap import run_pipeline

result = run_pipeline(df, target_var="target")
best_model_name, best_model = result.get_best_tuned_model()
predictions = best_model.predict(X_new)
```

### Pipeline Stages

1. **Statistics** – Feature profiling, normality testing, distribution analysis  
2. **Correlation** – Association testing (Pearson, Spearman, Chi-Square, ANOVA, t-tests)  
3. **Preprocessing** – Task-aware splitting, class balancing (SMOTE), target transforms  
4. **Model Selection** – 25+ models trained and ranked automatically  
5. **Tuning** – Hyperparameter optimization for the top-N models  

---

## Key Features

### Data Analysis
- Comprehensive statistics: mean, median, std, skewness, normality tests
- Association testing: Pearson, Spearman, Chi-Square, Point-Biserial, ANOVA
- Automatic target type inference (binary, multiclass, regression, count)

### Preprocessing
- Task-aware splitting (stratified, grouped, time-series)
- Class balancing: SMOTE, under-sampling, class weights
- Target transformations: Yeo-Johnson, Box-Cox, log1p
- Sample weighting for imbalanced or heteroscedastic targets

### Model Selection (25+ Models)
- **Classification**: Logistic Regression, Random Forest, SVC, XGBoost, LightGBM, CatBoost, MLP
- **Regression**: ElasticNet, Ridge, Lasso, SVR, Random Forest, XGBoost, LightGBM, CatBoost
- **Robust Models**: Huber, RANSAC, Theil-Sen
- **Neural Networks**: MLP Classifier / Regressor

### Hyperparameter Tuning
- Grid Search, Randomized Search, Successive Halving, Bayesian Optimization
- Task-aware cross-validation
- Multi-metric tracking
- Predefined parameter grids for supported models

### Export & Deployment
- Persist best or top-N models with metadata
- Auto-generated inference and tuning scripts
- Export feature importance, associations, and rankings

---

## Installation

### From PyPI (recommended)

```bash
pip install mlprimer
```

### From Source

```bash
git clone https://github.com/emrec/mlprimer.git
cd mlprimer
pip install -e .
```

### Optional Dependencies

```bash
# Bayesian optimization
pip install mlprimer[bayesian]

# Boosting models (XGBoost, LightGBM, CatBoost)
pip install mlprimer[advanced]

# All optional features
pip install mlprimer[all]
```

---

## Quick Start

### Complete Pipeline

```python
import pandas as pd
from mlprimer.bootstrap import run_pipeline

df = pd.read_csv("data.csv")

result = run_pipeline(
    df,
    target_var="target",
    tune_top_n=5,
    verbose=2
)

best_model_name, best_model = result.get_best_tuned_model()
predictions = best_model.predict(X_test)
```

### Step-by-Step Workflow

```python
from mlprimer.statistics import calculate_summary
from mlprimer.correlation import check_association
from mlprimer.preprocessing import infer_target_type, split_data, apply_smote_classification
from mlprimer.model_selection import run_full_model_selection
from mlprimer.tuning import tune_random

feature_summary = calculate_summary(df)
associations = check_association(df, target_var="target")

target_type = infer_target_type(df["target"])
X_train, X_test, y_train, y_test = split_data(
    df.drop("target", axis=1),
    df["target"],
    task="classification"
)

X_train, y_train = apply_smote_classification(X_train, y_train)

results = run_full_model_selection(
    X_train, y_train, X_test, y_test, target_type=target_type
)

best_model = results["best_model"]
tuned = tune_random(
    best_model,
    X_train,
    y_train,
    {"n_estimators": [100, 200], "max_depth": [10, 20]},
    task="binary"
)
```

---

## Exporting Models

```python
from mlprimer.bootstrap import (
    export_best_model,
    export_models,
    create_inference_script
)

export_best_model(result, "best_model.pkl")
export_models(result, "models/", include_top_n=5)
create_inference_script(result, "inference.py")
```

---

## Core Modules

### `statistics.py`
- `calculate_summary(df)`
- `check_normal(x)`

### `correlation.py`
- `check_association(df, target_var)`
- `analyze_associations(df, target_var)`

### `preprocessing.py`
- `infer_target_type(y)`
- `export_target_distribution(y, task)`
- `split_data(X, y, task, stratify=None, groups=None, time_series=False)`
- `apply_smote_classification(X, y)`
- `apply_target_transform(y, method)`
- `make_sample_weights_regression(y)`

### `model_selection.py`
- `run_full_model_selection(...)`
- `suggest_models(target_type)`
- `train_models(X_train, y_train, task)`
- `evaluate_models(models, X_test, y_test, task)`

### `tuning.py`
- `tune_grid`
- `tune_random`
- `tune_halving_grid`
- `tune_halving_random`
- `tune_bayesian`
- `tune_with_calibration`

### `bootstrap.py`
- `run_pipeline`
- `export_results`
- `export_best_model`
- `export_models`
- `create_fine_tuning_script`
- `create_inference_script`
- `create_comparison_script`

---

## Supported Tasks

| Task | Target Type | Models | Metrics |
|-----|------------|--------|---------|
| Binary Classification | 2 classes | 15+ | F1, AUC, Precision, Recall |
| Multiclass | 3+ classes | 15+ | F1-weighted, Balanced Accuracy |
| Regression | Continuous | 14+ | MAE, RMSE, R² |
| Count | Non-negative ints | 14+ | MAE, RMSE |

---

## Architecture

```text
bootstrap.py
 ├─ statistics.py
 ├─ correlation.py
 ├─ preprocessing.py
 ├─ model_selection.py
 └─ tuning.py
```

---

## Requirements

- Python ≥ 3.8  
- pandas ≥ 1.0  
- numpy ≥ 1.18  
- scikit-learn ≥ 0.24  
- scipy ≥ 1.5  
- imbalanced-learn ≥ 0.8  

**Optional**
- xgboost  
- lightgbm  
- catboost  
- scikit-optimize  

---

## License

MIT License

---

## Author

**Emre Can Konca**

---

## Acknowledgments

Built on top of scikit-learn, XGBoost, LightGBM, CatBoost, and the broader open-source ML ecosystem.
