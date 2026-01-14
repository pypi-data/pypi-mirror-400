from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import (
    pointbiserialr,
    pearsonr,
    spearmanr,
    chi2_contingency,
    f_oneway,
)
from typing import Literal, Dict, Any, Optional


TargetType = Literal["binary", "categorical", "continuous"]
VarType = Literal["binary", "categorical", "continuous"]


def _is_bool_like(s: pd.Series) -> bool:
    """Check if series is boolean-like (bool dtype or {0,1} values)."""
    if pd.api.types.is_bool_dtype(s):
        return True
    # handle {0,1} with possible NaNs
    x = pd.to_numeric(s.dropna(), errors="coerce")
    if x.empty:
        return False
    u = set(np.unique(x))
    return u.issubset({0, 1}) and len(u) <= 2


def _infer_var_type(s: pd.Series, *, max_categories: int = 20) -> VarType:
    """
    Heuristic inference of variable type.
    
    - binary: bool or {0,1} or 2 unique values
    - categorical: object/category OR low-cardinality ints
    - continuous: numeric otherwise
    """
    s_nonnull = s.dropna()

    if s_nonnull.empty:
        # default to categorical; tests will mark unsupported later
        return "categorical"

    nunique = s_nonnull.nunique(dropna=True)

    if _is_bool_like(s):
        return "binary"

    if nunique == 2:
        # could be binary encoded as strings or 2-level category
        return "binary"

    if pd.api.types.is_categorical_dtype(s) or pd.api.types.is_object_dtype(s):
        return "categorical"

    if pd.api.types.is_numeric_dtype(s):
        # treat low-cardinality integer-ish as categorical
        if pd.api.types.is_integer_dtype(s) and nunique <= max_categories:
            return "categorical"
        return "continuous"

    return "categorical"


def _safe_numeric(s: pd.Series) -> pd.Series:
    """Safely convert series to numeric, coercing errors to NaN."""
    return pd.to_numeric(s, errors="coerce")


def _cramers_v(contingency: pd.DataFrame) -> float:
    """
    Calculate bias-corrected Cramér's V from a contingency table.
    Provides standardized effect size (0-1) for categorical associations.
    """
    chi2, _, _, _ = chi2_contingency(contingency)
    n = contingency.to_numpy().sum()
    if n == 0:
        return np.nan
    r, k = contingency.shape
    phi2 = chi2 / n
    phi2corr = max(0.0, phi2 - ((k - 1) * (r - 1)) / max(n - 1, 1))
    rcorr = r - ((r - 1) ** 2) / max(n - 1, 1)
    kcorr = k - ((k - 1) ** 2) / max(n - 1, 1)
    denom = min((kcorr - 1), (rcorr - 1))
    if denom <= 0:
        return np.nan
    return np.sqrt(phi2corr / denom)


def check_association(
    data: pd.DataFrame,
    target_var: str,
    *,
    alpha: float = 0.05,
    max_categories: int = 20,
    corr_method_cont_cont: Literal["pearson", "spearman", "auto"] = "auto",
    normality_data: Optional[pd.DataFrame] = None,
    dropna: bool = True,
) -> pd.DataFrame:
    """
    Auto-selects an appropriate statistical test based on inferred variable types and normality.

    Supported scenarios:
      - continuous ~ continuous: Pearson (if normal) or Spearman (if non-normal)
      - continuous ~ binary: point-biserial (effect is r), p from pointbiserialr
      - continuous ~ categorical(k>2): one-way ANOVA (f_oneway)
      - categorical ~ categorical: chi-squared + Cramér's V
      - binary ~ categorical: chi-squared + Cramér's V (same as categorical-categorical)
      - binary ~ binary: chi-squared + phi (Cramér's V reduces to phi)

    Returns per-feature:
      test_method, statistic, p_value, effect_size, significant, feature_type, target_type, notes
    
    Parameters
    ----------
    data : pd.DataFrame
        Input data
    target_var : str
        Name of target column
    alpha : float, default 0.05
        Significance level for determining statistical significance
    max_categories : int, default 20
        Threshold above which numeric columns are treated as continuous rather than categorical
    corr_method_cont_cont : {"pearson", "spearman", "auto"}, default "auto"
        Correlation method for continuous-continuous pairs.
        If "auto", uses Pearson for normal data and Spearman for non-normal data.
        Requires normality_data if "auto" is selected.
    normality_data : pd.DataFrame, optional
        Output from calculate_summary() containing 'normal' column for normality test results.
        Used to auto-select between Pearson and Spearman when corr_method_cont_cont="auto".
    dropna : bool, default True
        Whether to drop NaNs pairwise before testing
        
    Returns
    -------
    pd.DataFrame
        Results sorted by significance (descending) and p-value (ascending)
    """
    if target_var not in data.columns:
        raise KeyError(f"target_var '{target_var}' not in dataframe columns")

    t = data[target_var]
    target_type: TargetType = _infer_var_type(t, max_categories=max_categories)  # type: ignore

    results: Dict[str, Dict[str, Any]] = {}

    for col in data.columns:
        if col == target_var:
            continue

        x = data[col]

        feature_type: VarType = _infer_var_type(x, max_categories=max_categories)

        # Align and optionally drop missing pairwise
        pair = pd.concat([t, x], axis=1)
        pair.columns = ["target", "feature"]
        if dropna:
            pair = pair.dropna()

        out: Dict[str, Any] = {
            "feature_type": feature_type,
            "target_type": target_type,
            "test_method": None,
            "statistic": np.nan,
            "p_value": np.nan,
            "effect_size": np.nan,
            "significant": False,
            "notes": "",
        }

        if pair.empty or pair["feature"].nunique() < 2 or pair["target"].nunique() < 2:
            out["test_method"] = "unsupported"
            out["notes"] = "insufficient variation or all NaN after alignment"
            results[col] = out
            continue

        # ---- continuous target ----
        if target_type == "continuous":
            y = _safe_numeric(pair["target"])
            if feature_type == "continuous":
                fx = _safe_numeric(pair["feature"])
                
                # Determine which correlation method to use
                use_spearman = False
                method_note = ""
                
                if corr_method_cont_cont == "auto" and normality_data is not None:
                    # Check normality of both variables
                    target_normal = normality_data.loc[target_var, "normal"] if target_var in normality_data.index else None
                    feature_normal = normality_data.loc[col, "normal"] if col in normality_data.index else None
                    
                    # Use Spearman if either variable is non-normal
                    use_spearman = (target_normal is False) or (feature_normal is False)
                    
                    if use_spearman:
                        method_note = "Used Spearman (non-normal distribution detected)"
                    else:
                        method_note = "Used Pearson (normal distributions)"
                elif corr_method_cont_cont == "spearman":
                    use_spearman = True
                
                if use_spearman:
                    stat, p = spearmanr(y, fx, nan_policy="omit")
                    out["test_method"] = "spearmanr"
                    out["statistic"] = stat
                    out["p_value"] = p
                    out["effect_size"] = stat
                    out["notes"] = method_note
                else:
                    stat, p = pearsonr(y, fx)
                    out["test_method"] = "pearsonr"
                    out["statistic"] = stat
                    out["p_value"] = p
                    out["effect_size"] = stat
                    out["notes"] = method_note

            elif feature_type == "binary":
                fx = pair["feature"]
                # ensure 0/1 coding for point-biserial expectations (binary)
                # pointbiserialr expects binary in one argument and continuous in the other
                # We'll encode feature to 0/1
                codes = pd.Series(pd.Categorical(fx)).cat.codes
                stat, p = pointbiserialr(codes, y)
                out["test_method"] = "pointbiserialr"
                out["statistic"] = stat
                out["p_value"] = p
                out["effect_size"] = stat

            else:  # categorical feature (k>2)
                groups = []
                for _, g in pair.groupby("feature", observed=True):
                    vals = _safe_numeric(g["target"]).dropna().to_numpy()
                    if len(vals) > 0:
                        groups.append(vals)
                if len(groups) >= 2:
                    stat, p = f_oneway(*groups)
                    out["test_method"] = "anova_oneway"
                    out["statistic"] = stat
                    out["p_value"] = p
                    out["effect_size"] = np.nan  # could add eta-squared if desired
                else:
                    out["test_method"] = "unsupported"
                    out["notes"] = "not enough non-empty groups for ANOVA"

        # ---- binary target ----
        elif target_type == "binary":
            y = pair["target"]
            # encode target to 0/1 for numeric tests
            y01 = pd.Series(pd.Categorical(y)).cat.codes

            if feature_type == "continuous":
                fx = _safe_numeric(pair["feature"])
                stat, p = pointbiserialr(y01, fx)
                out["test_method"] = "pointbiserialr"
                out["statistic"] = stat
                out["p_value"] = p
                out["effect_size"] = stat

            elif feature_type == "binary":
                contingency = pd.crosstab(y, pair["feature"])
                chi2, p, _, _ = chi2_contingency(contingency)
                v = _cramers_v(contingency)  # equals phi for 2x2
                out["test_method"] = "chi2"
                out["statistic"] = chi2
                out["p_value"] = p
                out["effect_size"] = v

            else:  # categorical feature
                contingency = pd.crosstab(y, pair["feature"])
                chi2, p, _, _ = chi2_contingency(contingency)
                v = _cramers_v(contingency)
                out["test_method"] = "chi2"
                out["statistic"] = chi2
                out["p_value"] = p
                out["effect_size"] = v

        # ---- categorical (k>2) target ----
        else:  # target_type == "categorical"
            y = pair["target"]

            if feature_type in ("categorical", "binary"):
                contingency = pd.crosstab(y, pair["feature"])
                chi2, p, _, _ = chi2_contingency(contingency)
                v = _cramers_v(contingency)
                out["test_method"] = "chi2"
                out["statistic"] = chi2
                out["p_value"] = p
                out["effect_size"] = v

            else:  # continuous feature vs categorical target => one-way ANOVA
                groups = []
                for _, g in pair.groupby("target", observed=True):
                    vals = _safe_numeric(g["feature"]).dropna().to_numpy()
                    if len(vals) > 0:
                        groups.append(vals)
                if len(groups) >= 2:
                    stat, p = f_oneway(*groups)
                    out["test_method"] = "anova_oneway"
                    out["statistic"] = stat
                    out["p_value"] = p
                    out["effect_size"] = np.nan  # could add eta-squared if desired
                else:
                    out["test_method"] = "unsupported"
                    out["notes"] = "not enough non-empty groups for ANOVA"

        out["significant"] = bool(pd.notna(out["p_value"]) and out["p_value"] < alpha)
        results[col] = out

    return pd.DataFrame.from_dict(results, orient="index").sort_values(
        by=["significant", "p_value"], ascending=[False, True]
    )


def analyze_associations(
    data: pd.DataFrame,
    target_var: str,
    **kwargs
) -> tuple:
    """
    Complete workflow: descriptive statistics → normality check → correlation analysis.
    
    This is a convenience function that ties together calculate_summary() and 
    check_association() to provide an integrated analysis pipeline where normality 
    test results automatically inform test selection.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input data
    target_var : str
        Name of target column
    **kwargs
        Additional keyword arguments passed to check_association()
        (e.g., alpha, max_categories, corr_method_cont_cont)
        
    Returns
    -------
    tuple
        - summary_df: Descriptive statistics from calculate_summary()
        - association_df: Association test results from check_association()
        
    Examples
    --------
    >>> from statistics import calculate_summary
    >>> from correlation import analyze_associations
    >>> summary, assoc = analyze_associations(df, target_var='target')
    >>> print(summary[['type', 'normal']])  # See normality results
    >>> print(assoc[['test_method', 'statistic', 'p_value']])  # See test results
    """
    # Import here to avoid circular imports
    from . import statistics
    
    summary = statistics.calculate_summary(data)
    associations = check_association(
        data, target_var, normality_data=summary, **kwargs
    )
    return summary, associations
