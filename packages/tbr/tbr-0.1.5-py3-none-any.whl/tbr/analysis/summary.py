"""
TBR Analysis Summary Module.

This module provides clean, modular interfaces for creating TBR summary statistics.
It wraps the proven functional implementations with object-oriented interfaces
while maintaining 100% mathematical compatibility and performance.

The module uses lazy loading for optimal performance and provides comprehensive
input validation leveraging the existing validation infrastructure.

Functions
---------
create_tbr_summary : Create single-row TBR summary with credible intervals

Examples
--------
>>> from tbr.analysis.summary import create_tbr_summary
>>> summary = create_tbr_summary(
...     tbr_dataframe, alpha=50, beta=0.95, sigma=25,
...     var_alpha=100, var_beta=0.001, cov_alpha_beta=-0.05,
...     degrees_freedom=43, level=0.80, threshold=0.0
... )
>>> print(f"Effect estimate: {summary['estimate'].iloc[0]:.2f}")
"""


import pandas as pd

# Import functional implementation for wrapping
from tbr.functional.tbr_functions import (
    create_tbr_summary as functional_create_tbr_summary,
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
    credible intervals, and model parameters. It provides a clean modular interface
    around the proven functional implementation.

    The summary includes:
    - Cumulative treatment effect estimate with uncertainty quantification
    - Credible intervals using t-distribution with proper degrees of freedom
    - Posterior probability of exceeding specified threshold
    - Complete model parameters and metadata for reproducibility

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
        Single-row DataFrame with TBR summary statistics including:

        - 'estimate' : float
            Cumulative treatment effect (final cumdif value)
        - 'precision' : float
            Half-width of credible interval (margin of error)
        - 'lower' : float
            Lower bound of credible interval
        - 'upper' : float
            Upper bound of credible interval
        - 'se' : float
            Standard error (final cumsd value)
        - 'level' : float
            Credibility level used
        - 'thres' : float
            Threshold value used
        - 'prob' : float
            Posterior probability P(effect > threshold)
        - Model parameters: 'alpha', 'beta', 'sigma', 'var_alpha', 'var_beta',
          'alpha_beta_cov', 't_dist_df'

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
    The credible interval is calculated using the t-distribution:

    .. math::
        CI = estimate ± t_{α/2,df} × se

    where t_{α/2,df} is the critical value from t-distribution with specified
    degrees of freedom.

    The posterior probability uses the t-distribution CDF:

    .. math::
        P(effect > threshold) = 1 - F_t((threshold - estimate)/se, df)

    where F_t is the t-distribution cumulative distribution function.

    Examples
    --------
    Create summary for a TBR analysis:

    >>> summary = create_tbr_summary(
    ...     tbr_results, alpha=50.2, beta=0.95, sigma=25.3,
    ...     var_alpha=100.5, var_beta=0.001, cov_alpha_beta=-0.05,
    ...     degrees_freedom=43, level=0.80, threshold=0.0
    ... )
    >>> print(f"Effect estimate: {summary['estimate'].iloc[0]:.2f}")
    >>> print(f"80% CI: [{summary['lower'].iloc[0]:.2f}, {summary['upper'].iloc[0]:.2f}]")
    >>> print(f"P(effect > 0): {summary['prob'].iloc[0]:.3f}")

    Access model parameters:

    >>> print(f"Regression slope: {summary['beta'].iloc[0]:.3f}")
    >>> print(f"Residual std: {summary['sigma'].iloc[0]:.2f}")
    """
    return functional_create_tbr_summary(
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
