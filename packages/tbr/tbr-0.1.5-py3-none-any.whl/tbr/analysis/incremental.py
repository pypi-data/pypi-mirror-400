"""
TBR Incremental Analysis Module.

This module provides specialized functionality for incremental TBR analysis,
enabling day-by-day progression analysis of treatment effects during test periods.

The incremental analysis approach allows researchers to:
- Track treatment effect evolution over time
- Identify when effects become statistically significant
- Optimize test duration for future experiments
- Make early stopping decisions in ongoing tests
- Understand effect stability and consistency patterns

Functions
---------
create_incremental_tbr_summaries : Create day-by-day incremental summaries

Examples
--------
>>> from tbr.analysis.incremental import create_incremental_tbr_summaries
>>> incremental = create_incremental_tbr_summaries(
...     tbr_results, alpha=50.2, beta=0.95, sigma=25.3,
...     var_alpha=100.5, var_beta=0.001, cov_alpha_beta=-0.05,
...     degrees_freedom=43, level=0.80, threshold=0.0
... )
>>> print(f"Day 1 effect: {incremental.iloc[0]['estimate']:.2f}")
>>> print(f"Day 3 effect: {incremental.iloc[2]['estimate']:.2f}")

Analyze effect progression:

>>> for day in range(len(incremental)):
...     row = incremental.iloc[day]
...     print(f"Day {row['test_day']}: {row['estimate']:.2f} "
...           f"(prob={row['prob']:.3f})")

Find when effect becomes significant:

>>> significant_days = incremental[incremental['prob'] > 0.8]
>>> if not significant_days.empty:
...     first_sig_day = significant_days.iloc[0]['test_day']
...     print(f"Effect significant from day {first_sig_day}")
"""


import pandas as pd

# Import functional implementation for wrapping
from tbr.functional.tbr_functions import (
    create_incremental_tbr_summaries as functional_create_incremental_tbr_summaries,
)


def create_incremental_tbr_summaries(
    tbr_dataframe: pd.DataFrame,
    alpha: float,
    beta: float,
    sigma: float,
    var_alpha: float,
    var_beta: float,
    cov_alpha_beta: float,
    degrees_freedom: int,
    level: float,
    threshold: float,
) -> pd.DataFrame:
    """
    Create incremental TBR summary statistics for each test period day.

    This function generates summary statistics for incremental test periods,
    providing day-by-day analysis of cumulative treatment effects:
    - Day 1: Summary for first day only
    - Day 2: Summary for first two days (cumulative)
    - Day 3: Summary for first three days (cumulative)
    - ...and so on

    This enables progressive analysis of treatment effects during the test period,
    providing insights into when effects become detectable, stable, and significant.
    Each row represents the cumulative effect up to that test day.

    Parameters
    ----------
    tbr_dataframe : pd.DataFrame
        Complete TBR dataframe with all periods and statistics.
        Must contain columns: 'period', 'cumdif', 'cumsd'
    alpha : float
        Regression intercept coefficient (α) from fitted model
    beta : float
        Regression slope coefficient (β) from fitted model
    sigma : float
        Residual standard deviation from the model prediction over the learning set (σ).
        Must be positive.
    var_alpha : float
        Variance of intercept estimate (Var[α̂]) from regression model
    var_beta : float
        Variance of slope estimate (Var[β̂]) from regression model
    cov_alpha_beta : float
        Covariance between intercept and slope estimates (Cov[α̂,β̂])
    degrees_freedom : int
        Residual degrees of freedom from regression model. Must be positive.
    level : float
        Credibility level for credible intervals. Must be between 0 and 1.
        E.g., 0.80 for 80% credible intervals.
    threshold : float
        Threshold value for posterior probability calculation.
        Probability calculated as P(effect > threshold).

    Returns
    -------
    pd.DataFrame
        Multi-row DataFrame with incremental TBR summary statistics.
        Each row represents cumulative statistics up to that test day.

        Columns include all standard summary statistics plus:
        - 'test_day' : int
            Test day number (1, 2, 3, ...)
        - All columns from create_tbr_summary() for each incremental period

        The DataFrame is ordered by test_day, enabling easy analysis of
        effect progression over time.

    Raises
    ------
    ValueError
        If tbr_dataframe is empty or missing required columns
        If level is not between 0 and 1
        If degrees_freedom is not positive
        If sigma is not positive
        If no test period data found (period == 1)

    Notes
    -----
    Each row in the returned DataFrame represents the cumulative effect
    from test day 1 through the specified test day. This allows analysis
    of how treatment effects accumulate and stabilize over time.

    The incremental analysis is particularly useful for:
    - Detecting when effects become statistically significant
    - Understanding effect stability and consistency
    - Optimizing test duration for future experiments
    - Early stopping decisions in ongoing tests

    Mathematical Foundation
    -----------------------
    The incremental analysis maintains the same mathematical rigor as the
    complete TBR analysis, with each incremental period using:

    .. math::
        CI_t = estimate_t ± t_{α/2,df} × se_t

    where t represents the incremental test period (day 1, day 2, etc.).

    The posterior probability for each incremental period uses:

    .. math::
        P(effect_t > threshold) = 1 - F_t((threshold - estimate_t)/se_t, df)

    Examples
    --------
    Create incremental summaries for day-by-day analysis:

    >>> incremental = create_incremental_tbr_summaries(
    ...     tbr_results, alpha=50.2, beta=0.95, sigma=25.3,
    ...     var_alpha=100.5, var_beta=0.001, cov_alpha_beta=-0.05,
    ...     degrees_freedom=43, level=0.80, threshold=0.0
    ... )
    >>> print(f"Day 1 effect: {incremental.iloc[0]['estimate']:.2f}")
    >>> print(f"Day 3 effect: {incremental.iloc[2]['estimate']:.2f}")

    Analyze effect progression:

    >>> for day in range(len(incremental)):
    ...     row = incremental.iloc[day]
    ...     print(f"Day {row['test_day']}: {row['estimate']:.2f} "
    ...           f"(prob={row['prob']:.3f})")

    Find when effect becomes significant:

    >>> significant_days = incremental[incremental['prob'] > 0.8]
    >>> if not significant_days.empty:
    ...     first_sig_day = significant_days.iloc[0]['test_day']
    ...     print(f"Effect significant from day {first_sig_day}")

    Track effect stability:

    >>> # Calculate effect variance across days
    >>> effect_variance = incremental['estimate'].var()
    >>> print(f"Effect stability (lower=more stable): {effect_variance:.3f}")

    Optimize test duration:

    >>> # Find minimum days for desired significance
    >>> target_prob = 0.9
    >>> min_days = incremental[incremental['prob'] >= target_prob]
    >>> if not min_days.empty:
    ...     optimal_duration = min_days.iloc[0]['test_day']
    ...     print(f"Minimum test duration for 90% confidence: {optimal_duration} days")
    """
    return functional_create_incremental_tbr_summaries(
        tbr_dataframe=tbr_dataframe,
        alpha=alpha,
        beta=beta,
        sigma=sigma,
        var_alpha=var_alpha,
        var_beta=var_beta,
        cov_alpha_beta=cov_alpha_beta,
        degrees_freedom=degrees_freedom,
        level=level,
        threshold=threshold,
    )
