"""
Core prediction module for Time-Based Regression (TBR) analysis.

This module provides the core mathematical implementations for TBR prediction functionality,
including counterfactual predictions, uncertainty quantification, and interval estimation
for causal inference in time series experiments. These are the foundational implementations
that other modules build upon.

The module focuses on:
- Counterfactual prediction generation with uncertainty quantification
- Cumulative effect standard deviation calculations
- Interval estimation and credible intervals for subinterval analysis
- Core mathematical utilities for TBR prediction methodology

All functions are independent implementations that do not depend on other TBR modules,
following clean architecture principles.

Functions
---------
generate_counterfactual_predictions : Generate counterfactual predictions with uncertainties
calculate_cumulative_standard_deviation : Calculate cumulative effect uncertainty
compute_interval_estimate_and_ci : Compute interval estimates and credible intervals

Examples
--------
>>> import pandas as pd
>>> import numpy as np
>>> from tbr.core.prediction import generate_counterfactual_predictions
>>>
>>> # Test period data
>>> test_data = pd.DataFrame({
...     'date': pd.date_range('2023-02-15', periods=14),
...     'control': np.random.normal(1000, 50, 14)
... })
>>>
>>> # Generate counterfactual predictions
>>> predictions = generate_counterfactual_predictions(
...     alpha=50, beta=0.95, sigma=25, pretest_x_mean=1000, n_pretest=45,
...     pretest_sum_x_squared_deviations=15000,
...     test_period_data=test_data, control_col='control', time_col='date'
... )
>>> print(f"Predictions shape: {predictions.shape}")

Notes
-----
This module contains the core mathematical implementations for TBR prediction analysis.
Other modules can import and use these functions as building blocks.
"""

from typing import Dict

import numpy as np
import pandas as pd
from scipy import stats

from .regression import calculate_model_variance, calculate_prediction_variance

# Export list for clean imports
__all__ = [
    "generate_counterfactual_predictions",
    "calculate_cumulative_standard_deviation",
    "compute_interval_estimate_and_ci",
]


def generate_counterfactual_predictions(
    alpha: float,
    beta: float,
    sigma: float,
    pretest_x_mean: float,
    n_pretest: int,
    pretest_sum_x_squared_deviations: float,
    test_period_data: pd.DataFrame,
    control_col: str,
    time_col: str,
) -> pd.DataFrame:
    """
    Generate counterfactual predictions and prediction uncertainties for TBR test period.

    Creates counterfactual predictions using the fitted regression model and calculates
    their prediction standard deviations. These predictions represent what the test
    group values would have been without treatment intervention.

    This is a clean interface to the proven functional implementation, providing
    the core prediction functionality for TBR causal inference.

    Parameters
    ----------
    alpha : float
        Regression intercept coefficient (α)
    beta : float
        Regression slope coefficient (β)
    sigma : float
        Residual standard deviation from the model prediction over the pretest period (σ)
    pretest_x_mean : float
        Mean of control values from pretest period (x̄)
    n_pretest : int
        Number of observations in pretest period
    pretest_sum_x_squared_deviations : float
        Sum of squared deviations from pretest period: Σ(xi - x̄)²
    test_period_data : pd.DataFrame
        Test period data containing control values and time column
    control_col : str
        Name of control column
    time_col : str
        Name of the time column

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: time column, control, pred, predsd where:
        - pred: counterfactual predictions (ŷ*)
        - predsd: prediction standard deviations including model uncertainty and residual noise

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> test_data = pd.DataFrame({
    ...     'date': pd.date_range('2023-02-15', periods=14),
    ...     'control': np.random.normal(1000, 50, 14)
    ... })
    >>> predictions = generate_counterfactual_predictions(
    ...     alpha=50, beta=0.95, sigma=25, pretest_x_mean=1000, n_pretest=45,
    ...     pretest_sum_x_squared_deviations=2500.0,
    ...     test_period_data=test_data, control_col='control', time_col='date'
    ... )
    >>> print(f"Predictions shape: {predictions.shape}")

    Notes
    -----
    Implements: ŷ* = α + β * x* with prediction variance V[y*] = σ² + V[ŷ*]
    where V[ŷ*] = σ² * (1/n + (x* - x̄)²/Σ(xi - x̄)²)
    """
    # Get control values for test period
    X_test = test_period_data[control_col].values

    # Calculate counterfactual predictions: ŷ* = α + β * x*
    predictions = alpha + beta * X_test

    model_variances = calculate_model_variance(
        x_values=X_test,  # Test period values (prediction targets)
        pretest_x_mean=pretest_x_mean,  # Pretest mean
        sigma=sigma,  # Pretest residual std
        n_pretest=int(n_pretest),  # Pretest sample size
        pretest_sum_x_squared_deviations=pretest_sum_x_squared_deviations,  # Pretest sum sq dev
    )

    # Calculate prediction variances
    prediction_variances = calculate_prediction_variance(
        model_variances=model_variances,
        sigma=sigma,
    )

    # Calculate prediction standard deviations
    prediction_std_devs = np.sqrt(prediction_variances)

    # Create result DataFrame
    result_df = test_period_data[[time_col, control_col]].copy()
    result_df["pred"] = predictions
    result_df["predsd"] = prediction_std_devs

    return result_df


def calculate_cumulative_standard_deviation(
    test_x_values: np.ndarray,
    sigma: float,
    var_alpha: float,
    var_beta: float,
    cov_alpha_beta: float,
) -> np.ndarray:
    """
    Calculate standard deviation of cumulative causal effect for TBR test period.

    Implements the TBR formula for cumulative effect variance to quantify uncertainty
    in cumulative treatment effects as they accumulate over time during the test period.

    This provides the uncertainty quantification component of TBR analysis, essential
    for proper statistical inference about cumulative causal effects.

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
        Array of cumulative standard deviations for each day in test period

    Examples
    --------
    >>> import numpy as np
    >>> test_x = np.array([1000, 1020, 980, 1050, 990])
    >>> cumsd = calculate_cumulative_standard_deviation(
    ...     test_x_values=test_x, sigma=25.0, var_alpha=100.0,
    ...     var_beta=0.001, cov_alpha_beta=-0.05
    ... )
    >>> print(f"Cumulative std devs: {cumsd}")

    Notes
    -----
    Implements: V[Δr(T)] = T · σ² + T² · v
    where v = Var(α̂) + 2·x̄_T·Cov(α̂,β̂) + x̄_T²·Var(β̂)
    """
    n = len(test_x_values)
    T_values = np.arange(1, n + 1)  # [1, 2, 3, ..., n]

    # Calculate cumulative means efficiently using vectorized operations
    cumsum_x = np.cumsum(test_x_values)
    x_mean_cumulative = cumsum_x / T_values

    # Vectorized calculation of v for all time points
    v_values = (
        var_alpha
        + 2 * x_mean_cumulative * cov_alpha_beta
        + (x_mean_cumulative**2) * var_beta
    )

    # Vectorized calculation of cumulative variance
    cum_variance = T_values * (sigma**2) + (T_values**2) * v_values

    # Validate mathematical constraint: variance must be non-negative
    if np.any(cum_variance < 0):
        raise ValueError(
            "Negative variance detected in TBR calculation. "
            "This occurs when the covariance term 2·x̄·Cov(α̂,β̂) is large and negative, "
            "making the total variance negative. Check regression model conditioning "
            "and parameter values."
        )

    # Vectorized square root
    return np.sqrt(cum_variance)


def compute_interval_estimate_and_ci(
    tbr_df: pd.DataFrame,
    tbr_summary: pd.DataFrame,
    start_day: int,
    end_day: int,
    ci_level: float,
) -> Dict[str, float]:
    """
    Compute cumulative treatment effect estimate and credible interval for a subinterval.

    Calculates the cumulative treatment effect over a specified subinterval within
    the test period, along with its credible interval using t-distribution. This
    enables analysis of treatment effects for specific time ranges rather than
    the entire test period.

    This provides the interval estimation component of TBR analysis, allowing
    flexible analysis of treatment effects over custom time windows.

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
    >>> result = compute_interval_estimate_and_ci(
    ...     tbr_results, tbr_summaries, start_day=5, end_day=10, ci_level=0.80
    ... )
    >>> print(f"Effect estimate: {result['estimate']:.2f}")
    >>> print(f"80% CI: [{result['lower']:.2f}, {result['upper']:.2f}]")

    Notes
    -----
    Uses t-distribution for credible intervals with degrees of freedom from the
    regression model. Posterior variance combines model uncertainty and residual noise.
    """
    # Filter for test period
    test_df = tbr_df[tbr_df["period"] == 1].reset_index(drop=True)

    # Slice the subinterval (remember start_day is 1-indexed)
    interval_df = test_df.iloc[start_day - 1 : end_day]

    # Estimate of cumulative effect (sum of differences)
    estimate = (interval_df["y"] - interval_df["pred"]).sum()

    # Posterior variance = sum of estsd^2 + n * sigma^2
    sum_estsd_sq = np.sum(interval_df["estsd"] ** 2)
    n_days = end_day - start_day + 1
    sigma = float(tbr_summary.iloc[-1]["sigma"])
    dof = int(tbr_summary.iloc[-1]["t_dist_df"])

    posterior_variance = sum_estsd_sq + n_days * sigma**2
    se = np.sqrt(posterior_variance)

    # t-multiplier
    alpha = 1 - ci_level
    t_mult = stats.t.ppf(1 - alpha / 2, dof)

    # Precision (half-width)
    precision = t_mult * se

    return {
        "estimate": estimate,
        "precision": precision,
        "lower": estimate - precision,
        "upper": estimate + precision,
    }
