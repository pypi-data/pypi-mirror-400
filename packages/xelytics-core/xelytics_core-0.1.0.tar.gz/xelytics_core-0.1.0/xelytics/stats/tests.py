"""Statistical tests implementation.

Pure statistical functions without backend dependencies.
Uses scipy and statsmodels for computations.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from scipy import stats as scipy_stats

from xelytics.schemas.outputs import (
    StatisticalTestResult,
    TestType,
    EffectSize,
    AssumptionCheck,
)


def run_t_test(
    group1: np.ndarray,
    group2: np.ndarray,
    paired: bool = False,
    alpha: float = 0.05,
) -> StatisticalTestResult:
    """Run t-test between two groups.
    
    Args:
        group1: First group data
        group2: Second group data
        paired: If True, run paired t-test
        alpha: Significance level
        
    Returns:
        StatisticalTestResult with test results
    """
    # Remove NaN values
    g1 = np.array(group1)[~np.isnan(group1)]
    g2 = np.array(group2)[~np.isnan(group2)]
    
    if len(g1) < 2 or len(g2) < 2:
        raise ValueError("Each group must have at least 2 non-NaN values")
    
    if paired:
        if len(g1) != len(g2):
            raise ValueError("Paired t-test requires equal group sizes")
        statistic, p_value = scipy_stats.ttest_rel(g1, g2)
        test_type = TestType.T_TEST_PAIRED
        test_name = "Paired t-test"
    else:
        statistic, p_value = scipy_stats.ttest_ind(g1, g2)
        test_type = TestType.T_TEST_INDEPENDENT
        test_name = "Independent t-test"
    
    significant = p_value < alpha
    
    # Calculate Cohen's d
    cohens_d = _calculate_cohens_d(g1, g2)
    effect_size = EffectSize(
        measure_type="cohens_d",
        value=cohens_d,
        interpretation=_interpret_cohens_d(cohens_d),
    )
    
    # Interpretation
    if significant:
        interpretation = f"Significant difference between groups (p={p_value:.4f}, d={cohens_d:.2f})"
    else:
        interpretation = f"No significant difference between groups (p={p_value:.4f})"
    
    return StatisticalTestResult(
        test_name=test_name,
        test_type=test_type,
        statistic=float(statistic),
        p_value=float(p_value),
        significant=significant,
        interpretation=interpretation,
        effect_size=effect_size,
    )


def run_anova(
    data: pd.DataFrame,
    dependent_var: str,
    independent_var: str,
    alpha: float = 0.05,
) -> StatisticalTestResult:
    """Run one-way ANOVA.
    
    Args:
        data: DataFrame with data
        dependent_var: Name of dependent variable column
        independent_var: Name of independent variable (grouping) column
        alpha: Significance level
        
    Returns:
        StatisticalTestResult with test results
    """
    # Get groups
    groups = []
    group_names = []
    for name, group in data.groupby(independent_var):
        values = group[dependent_var].dropna().values
        if len(values) >= 2:
            groups.append(values)
            group_names.append(str(name))
    
    if len(groups) < 2:
        raise ValueError("ANOVA requires at least 2 groups with sufficient data")
    
    # Run ANOVA
    statistic, p_value = scipy_stats.f_oneway(*groups)
    significant = p_value < alpha
    
    # Calculate effect size (eta-squared)
    all_values = np.concatenate(groups)
    grand_mean = np.mean(all_values)
    ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups)
    ss_total = np.sum((all_values - grand_mean) ** 2)
    eta_squared = ss_between / ss_total if ss_total > 0 else 0.0
    
    effect_size = EffectSize(
        measure_type="eta_squared",
        value=float(eta_squared),
        interpretation=_interpret_eta_squared(eta_squared),
    )
    
    if significant:
        interpretation = f"Significant difference between groups (F={statistic:.2f}, p={p_value:.4f}, η²={eta_squared:.3f})"
    else:
        interpretation = f"No significant difference between groups (F={statistic:.2f}, p={p_value:.4f})"
    
    return StatisticalTestResult(
        test_name="One-way ANOVA",
        test_type=TestType.ANOVA_ONE_WAY,
        statistic=float(statistic),
        p_value=float(p_value),
        significant=significant,
        interpretation=interpretation,
        effect_size=effect_size,
        columns=[dependent_var, independent_var],
    )


def run_chi_square(
    data: pd.DataFrame,
    col1: str,
    col2: str,
    alpha: float = 0.05,
) -> StatisticalTestResult:
    """Run chi-square test of independence.
    
    Args:
        data: DataFrame with data
        col1: First categorical column
        col2: Second categorical column
        alpha: Significance level
        
    Returns:
        StatisticalTestResult with test results
    """
    # Create contingency table
    contingency = pd.crosstab(data[col1], data[col2])
    
    if contingency.shape[0] < 2 or contingency.shape[1] < 2:
        raise ValueError("Chi-square requires at least 2x2 contingency table")
    
    # Run chi-square test
    chi2, p_value, dof, expected = scipy_stats.chi2_contingency(contingency)
    significant = p_value < alpha
    
    # Calculate Cramér's V
    n = contingency.sum().sum()
    min_dim = min(contingency.shape[0] - 1, contingency.shape[1] - 1)
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if n * min_dim > 0 else 0.0
    
    effect_size = EffectSize(
        measure_type="cramers_v",
        value=float(cramers_v),
        interpretation=_interpret_cramers_v(cramers_v),
    )
    
    if significant:
        interpretation = f"Significant association between variables (χ²={chi2:.2f}, p={p_value:.4f}, V={cramers_v:.3f})"
    else:
        interpretation = f"No significant association between variables (χ²={chi2:.2f}, p={p_value:.4f})"
    
    return StatisticalTestResult(
        test_name="Chi-square test",
        test_type=TestType.CHI_SQUARE,
        statistic=float(chi2),
        p_value=float(p_value),
        significant=significant,
        interpretation=interpretation,
        effect_size=effect_size,
        columns=[col1, col2],
    )


def run_correlation(
    x: np.ndarray,
    y: np.ndarray,
    method: str = "pearson",
    alpha: float = 0.05,
) -> StatisticalTestResult:
    """Run correlation test.
    
    Args:
        x: First variable
        y: Second variable
        method: "pearson" or "spearman"
        alpha: Significance level
        
    Returns:
        StatisticalTestResult with test results
    """
    # Remove pairs with NaN
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]
    
    if len(x_clean) < 3:
        raise ValueError("Correlation requires at least 3 valid pairs")
    
    if method == "spearman":
        statistic, p_value = scipy_stats.spearmanr(x_clean, y_clean)
        test_type = TestType.CORRELATION_SPEARMAN
        test_name = "Spearman correlation"
    else:
        statistic, p_value = scipy_stats.pearsonr(x_clean, y_clean)
        test_type = TestType.CORRELATION_PEARSON
        test_name = "Pearson correlation"
    
    significant = p_value < alpha
    
    effect_size = EffectSize(
        measure_type="r_squared",
        value=float(statistic ** 2),
        interpretation=_interpret_r(statistic),
    )
    
    if significant:
        direction = "positive" if statistic > 0 else "negative"
        interpretation = f"Significant {direction} correlation (r={statistic:.3f}, p={p_value:.4f})"
    else:
        interpretation = f"No significant correlation (r={statistic:.3f}, p={p_value:.4f})"
    
    return StatisticalTestResult(
        test_name=test_name,
        test_type=test_type,
        statistic=float(statistic),
        p_value=float(p_value),
        significant=significant,
        interpretation=interpretation,
        effect_size=effect_size,
    )


def run_normality_test(
    data: np.ndarray,
    method: str = "shapiro",
    alpha: float = 0.05,
) -> StatisticalTestResult:
    """Run normality test.
    
    Args:
        data: Data to test
        method: "shapiro" or "ks"
        alpha: Significance level
        
    Returns:
        StatisticalTestResult with test results
    """
    # Remove NaN
    clean_data = data[~np.isnan(data)]
    
    if len(clean_data) < 3:
        raise ValueError("Normality test requires at least 3 values")
    
    if method == "ks":
        # Kolmogorov-Smirnov test
        statistic, p_value = scipy_stats.kstest(
            clean_data,
            'norm',
            args=(np.mean(clean_data), np.std(clean_data)),
        )
        test_type = TestType.NORMALITY_KS
        test_name = "Kolmogorov-Smirnov normality test"
    else:
        # Shapiro-Wilk test (limited to 5000 samples)
        if len(clean_data) > 5000:
            clean_data = np.random.choice(clean_data, 5000, replace=False)
        statistic, p_value = scipy_stats.shapiro(clean_data)
        test_type = TestType.NORMALITY_SHAPIRO
        test_name = "Shapiro-Wilk normality test"
    
    # For normality tests, significant p means NOT normal
    is_normal = p_value >= alpha
    
    if is_normal:
        interpretation = f"Data appears normally distributed (p={p_value:.4f})"
    else:
        interpretation = f"Data does not appear normally distributed (p={p_value:.4f})"
    
    return StatisticalTestResult(
        test_name=test_name,
        test_type=test_type,
        statistic=float(statistic),
        p_value=float(p_value),
        significant=not is_normal,  # Significant means NOT normal
        interpretation=interpretation,
    )


# Effect size interpretation helpers

def _calculate_cohens_d(g1: np.ndarray, g2: np.ndarray) -> float:
    """Calculate Cohen's d effect size."""
    n1, n2 = len(g1), len(g2)
    var1, var2 = np.var(g1, ddof=1), np.var(g2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return float((np.mean(g1) - np.mean(g2)) / pooled_std)


def _interpret_cohens_d(d: float) -> str:
    """Interpret Cohen's d effect size."""
    d = abs(d)
    if d < 0.2:
        return "negligible"
    elif d < 0.5:
        return "small"
    elif d < 0.8:
        return "medium"
    else:
        return "large"


def _interpret_eta_squared(eta_sq: float) -> str:
    """Interpret eta-squared effect size."""
    if eta_sq < 0.01:
        return "negligible"
    elif eta_sq < 0.06:
        return "small"
    elif eta_sq < 0.14:
        return "medium"
    else:
        return "large"


def _interpret_cramers_v(v: float) -> str:
    """Interpret Cramér's V effect size."""
    if v < 0.1:
        return "negligible"
    elif v < 0.3:
        return "small"
    elif v < 0.5:
        return "medium"
    else:
        return "large"


def _interpret_r(r: float) -> str:
    """Interpret correlation coefficient."""
    r = abs(r)
    if r < 0.1:
        return "negligible"
    elif r < 0.3:
        return "weak"
    elif r < 0.5:
        return "moderate"
    elif r < 0.7:
        return "strong"
    else:
        return "very strong"
