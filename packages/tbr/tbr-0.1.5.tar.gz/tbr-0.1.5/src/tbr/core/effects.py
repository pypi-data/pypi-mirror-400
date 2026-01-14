"""TBR Effects and Lift Calculation Module.

This module provides clean interfaces for calculating treatment effects and lift
in Time-Based Regression (TBR) analysis. It wraps the functional implementations
with modular interfaces while maintaining full backward compatibility.

The effects module focuses on:
- Cumulative treatment effect calculations
- Lift measurement and uncertainty quantification
- Subinterval effect analysis
- Summary statistics generation

All functions maintain mathematical accuracy and statistical rigor while providing
clean, documented interfaces for production use.
"""

from typing import Dict

import numpy as np
import pandas as pd

# Export list for clean imports
__all__ = [
    "calculate_cumulative_standard_deviation",
    "calculate_cumulative_variance",
    "compute_interval_estimate_and_ci",
    "create_tbr_summary",
    "create_incremental_tbr_summaries",
]


def calculate_cumulative_standard_deviation(
    test_x_values: np.ndarray,
    sigma: float,
    var_alpha: float,
    var_beta: float,
    cov_alpha_beta: float,
) -> np.ndarray:
    """
    Calculate standard deviation of cumulative causal effect for TBR test period.

    This function computes the uncertainty in cumulative treatment effects as they
    accumulate over time during the test period, implementing the TBR formula for
    cumulative effect variance.

    Parameters
    ----------
    test_x_values : np.ndarray
        Control values during test period
    sigma : float
        Residual standard deviation from the model prediction over the learning set (σ)
    var_alpha : float
        Variance of intercept estimate (α)
    var_beta : float
        Variance of slope estimate (β)
    cov_alpha_beta : float
        Covariance between intercept and slope estimates

    Returns
    -------
    np.ndarray
        Cumulative standard deviations for each time point in test period

    Examples
    --------
    >>> import numpy as np
    >>> from tbr.core.effects import calculate_cumulative_standard_deviation
    >>> x_vals = np.array([1000, 1020, 1010, 1030])
    >>> cumsd = calculate_cumulative_standard_deviation(
    ...     x_vals, sigma=25, var_alpha=100, var_beta=0.001,
    ...     cov_alpha_beta=-0.05
    ... )
    >>> print(f"Cumulative std devs: {cumsd}")
    """
    from tbr.functional.tbr_functions import (
        calculate_cumulative_standard_deviation as _calculate_cumulative_standard_deviation,
    )

    return _calculate_cumulative_standard_deviation(
        test_x_values=test_x_values,
        sigma=sigma,
        var_alpha=var_alpha,
        var_beta=var_beta,
        cov_alpha_beta=cov_alpha_beta,
    )


def calculate_cumulative_variance(
    test_x_values: np.ndarray,
    sigma: float,
    var_alpha: float,
    var_beta: float,
    cov_alpha_beta: float,
) -> np.ndarray:
    """
    Calculate variance of cumulative causal effect for TBR test period.

    This function implements the TBR formula for cumulative effect variance directly,
    providing the mathematical foundation for statistical inference and credible intervals.
    The variance quantifies uncertainty in cumulative treatment effects as they
    accumulate over time during the test period.

    Mathematical Formula
    --------------------
    V[Δr(T)] = T · σ² + T² · v
    where:
    - T = time point (1, 2, 3, ..., n)
    - σ² = residual variance from regression model
    - v = Var(α̂) + 2·x̄_T·Cov(α̂,β̂) + x̄_T²·Var(β̂)
    - x̄_T = cumulative mean of control values up to time T

    This formula captures both:
    1. Residual uncertainty (T · σ²) - grows linearly with time
    2. Model parameter uncertainty (T² · v) - grows quadratically with time

    Parameters
    ----------
    test_x_values : np.ndarray
        Control values during test period
    sigma : float
        Residual standard deviation from the model prediction over the learning set (σ)
    var_alpha : float
        Variance of intercept estimate (α)
    var_beta : float
        Variance of slope estimate (β)
    cov_alpha_beta : float
        Covariance between intercept and slope estimates

    Returns
    -------
    np.ndarray
        Cumulative variances for each time point in test period

    Notes
    -----
    This function provides the variance directly, which is more efficient than
    computing standard deviation and squaring when variance is the desired output.
    For standard deviation, use calculate_cumulative_standard_deviation().

    The relationship between this function and calculate_cumulative_standard_deviation()
    is: variance = standard_deviation²

    Examples
    --------
    >>> import numpy as np
    >>> from tbr.core.effects import calculate_cumulative_variance
    >>> x_vals = np.array([1000, 1020, 1010, 1030])
    >>> cum_var = calculate_cumulative_variance(
    ...     x_vals, sigma=25, var_alpha=100, var_beta=0.001,
    ...     cov_alpha_beta=-0.05
    ... )
    >>> print(f"Cumulative variances: {cum_var}")

    References
    ----------
    .. [1] Time-Based Regression methodology for causal inference
    .. [2] Statistical inference for cumulative treatment effects
    """
    # Input validation
    if len(test_x_values) == 0:
        raise ValueError("test_x_values cannot be empty")

    n = len(test_x_values)
    T_values = np.arange(1, n + 1)  # [1, 2, 3, ..., n]

    # Calculate cumulative means efficiently using vectorized operations
    cumsum_x = np.cumsum(test_x_values)
    x_mean_cumulative = cumsum_x / T_values

    # Vectorized calculation of v for all time points
    # v = Var(α̂) + 2·x̄_T·Cov(α̂,β̂) + x̄_T²·Var(β̂)
    v_values = (
        var_alpha
        + 2 * x_mean_cumulative * cov_alpha_beta
        + (x_mean_cumulative**2) * var_beta
    )

    # Direct calculation of cumulative variance using TBR formula
    # V[Δr(T)] = T · σ² + T² · v
    cum_variance = T_values * (sigma**2) + (T_values**2) * v_values

    return cum_variance


def compute_interval_estimate_and_ci(
    tbr_df: pd.DataFrame,
    tbr_summary: pd.DataFrame,
    start_day: int,
    end_day: int,
    ci_level: float,
) -> Dict[str, float]:
    """
    Compute cumulative treatment effect estimate and credible interval for a subinterval.

    This function calculates the cumulative treatment effect over a specified
    subinterval within the test period, along with its credible interval using
    t-distribution. This enables analysis of treatment effects for specific time
    ranges rather than the entire test period.

    Parameters
    ----------
    tbr_df : pd.DataFrame
        TBR daily output with columns 'y', 'pred', 'period', 'estsd'
    tbr_summary : pd.DataFrame
        TBR summary containing 'sigma' and 't_dist_df' (degrees of freedom) parameters
    start_day : int
        Start day of subinterval (1-indexed within test period)
    end_day : int
        End day of subinterval (inclusive)
    ci_level : float
        Credible interval level (e.g., 0.80 for 80% interval)

    Returns
    -------
    Dict[str, float]
        Dictionary containing:
        - 'estimate': Cumulative treatment effect for the subinterval
        - 'precision': Half-width of credible interval
        - 'lower': Lower bound of credible interval
        - 'upper': Upper bound of credible interval

    Examples
    --------
    >>> from tbr.core.effects import compute_interval_estimate_and_ci
    >>> result = compute_interval_estimate_and_ci(
    ...     tbr_results, tbr_summaries, start_day=5, end_day=10, ci_level=0.80
    ... )
    >>> print(f"Effect estimate: {result['estimate']:.2f}")
    >>> print(f"80% CI: [{result['lower']:.2f}, {result['upper']:.2f}]")
    """
    from tbr.functional.tbr_functions import (
        compute_interval_estimate_and_ci as _compute_interval_estimate_and_ci,
    )

    return _compute_interval_estimate_and_ci(
        tbr_df=tbr_df,
        tbr_summary=tbr_summary,
        start_day=start_day,
        end_day=end_day,
        ci_level=ci_level,
    )


def create_tbr_summary(
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
    Create TBR summary statistics DataFrame with credible intervals and probabilities.

    This function generates a single-row summary DataFrame containing all key
    statistics for the TBR analysis, including the cumulative effect estimate,
    credible intervals, and model parameters.

    Parameters
    ----------
    tbr_dataframe : pd.DataFrame
        Complete TBR dataframe with all periods and statistics
    alpha : float
        Regression intercept coefficient (α)
    beta : float
        Regression slope coefficient (β)
    sigma : float
        Residual standard deviation from the model prediction over the learning set (σ)
    var_alpha : float
        Variance of intercept estimate (α)
    var_beta : float
        Variance of slope estimate (β)
    cov_alpha_beta : float
        Covariance between intercept and slope estimates
    degrees_freedom : int
        Residual degrees of freedom from regression
    level : float
        Credibility level for credible intervals
    threshold : float
        Threshold for probability calculation

    Returns
    -------
    pd.DataFrame
        Single-row DataFrame with TBR summary statistics including:
        - 'estimate': Cumulative treatment effect
        - 'precision': Half-width of credible interval
        - 'lower', 'upper': Credible interval bounds
        - 'prob': Posterior probability of exceeding threshold
        - Model parameters and metadata

    Examples
    --------
    >>> from tbr.core.effects import create_tbr_summary
    >>> summary = create_tbr_summary(
    ...     tbr_results, alpha=50, beta=0.95, sigma=25,
    ...     var_alpha=100, var_beta=0.001, cov_alpha_beta=-0.05,
    ...     degrees_freedom=43, level=0.80, threshold=0.0
    ... )
    >>> print(f"Effect estimate: {summary['estimate'].iloc[0]:.2f}")
    """
    from scipy import stats

    # Input validation
    if tbr_dataframe.empty:
        raise ValueError("TBR dataframe cannot be empty")

    required_cols = ["period", "cumdif", "cumsd"]
    missing_cols = [col for col in required_cols if col not in tbr_dataframe.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in TBR dataframe: {missing_cols}")

    if not (0 <= level <= 1):
        raise ValueError(f"Level must be between 0 and 1, got: {level}")

    if degrees_freedom <= 0:
        raise ValueError(f"Degrees of freedom must be positive, got: {degrees_freedom}")

    if sigma <= 0:
        raise ValueError(f"Sigma must be positive, got: {sigma}")

    # Extract test period data (period == 1)
    test_period_data = tbr_dataframe[tbr_dataframe["period"] == 1].copy()

    if test_period_data.empty:
        raise ValueError("No test period data found (period == 1)")

    # Calculate core summary statistics
    # estimate: Final cumulative effect from test period
    estimate = test_period_data["cumdif"].iloc[-1]

    # se: Final cumulative standard deviation from test period
    se = test_period_data["cumsd"].iloc[-1]

    # Calculate credible interval using t-distribution
    alpha_level = 1 - level  # Probability outside interval
    t_critical = stats.t.ppf(1 - alpha_level / 2, df=degrees_freedom)

    # Credible interval bounds
    margin_of_error = t_critical * se
    lower = estimate - margin_of_error
    upper = estimate + margin_of_error

    # precision: Half-width of credible interval
    precision = margin_of_error

    # prob: Posterior probability that true cumulative effect exceeds threshold
    t_stat = (threshold - estimate) / se if se > 0 else 0
    prob = 1 - stats.t.cdf(t_stat, df=degrees_freedom)

    # Ensure probability is between 0 and 1
    prob = max(0.0, min(1.0, prob))

    # Create summary dictionary
    summary_data = {
        "estimate": float(estimate),
        "precision": float(precision),
        "lower": float(lower),
        "upper": float(upper),
        "se": float(se),
        "level": float(level),
        "thres": float(threshold),
        "prob": float(prob),
        "alpha": float(alpha),
        "beta": float(beta),
        "alpha_beta_cov": float(cov_alpha_beta),
        "var_alpha": float(var_alpha),
        "var_beta": float(var_beta),
        "sigma": float(sigma),
        "t_dist_df": float(degrees_freedom),
    }

    # Create single-row DataFrame with specified dtypes
    summary_df = pd.DataFrame([summary_data])

    # Ensure correct dtypes
    dtype_mapping = {
        "estimate": "float64",
        "precision": "float64",
        "lower": "float64",
        "upper": "float64",
        "se": "float64",
        "level": "float64",
        "thres": "float64",
        "prob": "float64",
        "alpha": "float64",
        "beta": "float64",
        "alpha_beta_cov": "float64",
        "var_alpha": "float64",
        "var_beta": "float64",
        "sigma": "float64",
        "t_dist_df": "float64",
    }

    summary_df = summary_df.astype(dtype_mapping)

    return summary_df


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

    This function generates summary statistics for incremental test periods:
    - Day 1: Summary for first day only
    - Day 2: Summary for first two days (cumulative)
    - Day 3: Summary for first three days (cumulative)
    - ...and so on

    This enables day-by-day analysis of cumulative treatment effects during the
    test period, providing insights into when effects become detectable and stable.

    Parameters
    ----------
    tbr_dataframe : pd.DataFrame
        Complete TBR dataframe with all periods and statistics
    alpha : float
        Regression intercept coefficient (α)
    beta : float
        Regression slope coefficient (β)
    sigma : float
        Residual standard deviation from the model prediction over the learning set (σ)
    var_alpha : float
        Variance of intercept estimate (α)
    var_beta : float
        Variance of slope estimate (β)
    cov_alpha_beta : float
        Covariance between intercept and slope estimates
    degrees_freedom : int
        Residual degrees of freedom from regression
    level : float
        Credibility level for credible intervals
    threshold : float
        Threshold for probability calculation

    Returns
    -------
    pd.DataFrame
        Multi-row DataFrame with incremental TBR summary statistics.
        Each row represents cumulative statistics up to that test day.
        Includes an additional 'test_day' column indicating the incremental period.

    Examples
    --------
    >>> from tbr.core.effects import create_incremental_tbr_summaries
    >>> incremental_summaries = create_incremental_tbr_summaries(
    ...     tbr_results, alpha=50, beta=0.95, sigma=25,
    ...     var_alpha=100, var_beta=0.001, cov_alpha_beta=-0.05,
    ...     degrees_freedom=43, level=0.80, threshold=0.0
    ... )
    >>> print(f"Day 1 effect: {incremental_summaries.iloc[0]['estimate']:.2f}")
    """
    # Input validation
    if tbr_dataframe.empty:
        raise ValueError("TBR dataframe cannot be empty")

    required_cols = ["period", "cumdif", "cumsd"]
    missing_cols = [col for col in required_cols if col not in tbr_dataframe.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in TBR dataframe: {missing_cols}")

    if not (0 <= level <= 1):
        raise ValueError(f"Level must be between 0 and 1, got: {level}")

    if degrees_freedom <= 0:
        raise ValueError(f"Degrees of freedom must be positive, got: {degrees_freedom}")

    if sigma <= 0:
        raise ValueError(f"Sigma must be positive, got: {sigma}")

    # Extract test period data (period == 1)
    test_period_data = tbr_dataframe[tbr_dataframe["period"] == 1].copy()

    if test_period_data.empty:
        raise ValueError("No test period data found (period == 1)")

    # Get pretest data for combining with incremental test periods
    pretest_data = tbr_dataframe[tbr_dataframe["period"] == 0].copy()

    num_test_days = len(test_period_data)
    incremental_summaries = []

    # Generate summary for each incremental test period
    for day_idx in range(num_test_days):
        # Create subset of test data up to current day (inclusive)
        test_subset = test_period_data.iloc[: day_idx + 1].copy()

        # Combine pretest data with current test subset
        incremental_df = pd.concat([pretest_data, test_subset], ignore_index=True)

        # Generate summary for this incremental period
        summary = create_tbr_summary(
            tbr_dataframe=incremental_df,
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

        # Add test day identifier
        summary["test_day"] = day_idx + 1

        incremental_summaries.append(summary)

    # Combine all incremental summaries
    result_df = pd.concat(incremental_summaries, ignore_index=True)

    # Reorder columns to put test_day first for clarity
    cols = ["test_day"] + [col for col in result_df.columns if col != "test_day"]
    result_df = result_df[cols]

    return result_df
