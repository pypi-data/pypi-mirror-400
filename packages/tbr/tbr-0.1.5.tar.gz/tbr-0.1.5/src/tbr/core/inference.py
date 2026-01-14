"""
Statistical inference and credible intervals for Time-Based Regression (TBR).

This module provides comprehensive statistical inference capabilities for TBR analysis,
including t-statistics, p-values, credible intervals, and posterior probability calculations.
All functions are designed to work with TBR model outputs and provide rigorous statistical
conclusions for treatment effect analysis.

The implementation provides proper error handling, numerical stability,
and comprehensive documentation.

Key Features
------------
- T-statistic calculation for hypothesis testing
- P-value computation using t-distribution
- Credible interval estimation with configurable credibility levels
- Posterior probability calculation for threshold exceedance
- Critical value computation for statistical testing
- Input validation and error handling

Examples
--------
>>> import numpy as np
>>> from tbr.core.inference import calculate_t_statistic, calculate_credible_interval
>>>
>>> # Calculate t-statistic for effect estimate
>>> t_stat = calculate_t_statistic(estimate=25.5, standard_error=8.2, null_value=0.0)
>>> print(f"T-statistic: {t_stat:.3f}")
T-statistic: 3.110
>>>
>>> # Calculate 95% credible interval
>>> ci = calculate_credible_interval(
...     estimate=25.5, standard_error=8.2, degrees_freedom=45, confidence_level=0.95
... )
>>> print(f"95% CI: [{ci['lower']:.2f}, {ci['upper']:.2f}]")
95% CI: [8.95, 42.05]

Mathematical Foundation
-----------------------
The statistical inference functions implement standard frequentist and Bayesian
statistical methods:

1. **T-statistic**: t = (θ̂ - θ₀) / SE(θ̂)
   where θ̂ is the estimate, θ₀ is the null value, SE is standard error

2. **P-value**: P(T ≥ |t|) = 2 × [1 - F_t(|t|; df)]
   where F_t is the cumulative t-distribution function

3. **Credible Interval**: θ̂ ± t_α/2,df × SE(θ̂)
   where t_α/2,df is the critical value from t-distribution

4. **Posterior Probability**: P(θ > τ | data) = 1 - F_t((τ - θ̂) / SE(θ̂); df)
   where τ is the threshold of interest

Notes
-----
All functions use lazy imports to minimize import overhead.

See individual function documentation for detailed usage and examples.
"""

from typing import Dict

import numpy as np


def calculate_t_statistic(
    estimate: float, standard_error: float, null_value: float = 0.0
) -> float:
    """
    Calculate t-statistic for hypothesis testing.

    Computes the t-statistic for testing whether an estimate differs significantly
    from a null hypothesis value. This is fundamental for statistical inference
    in TBR analysis, enabling hypothesis testing of treatment effects.

    Parameters
    ----------
    estimate : float
        The point estimate (e.g., treatment effect estimate)
    standard_error : float
        Standard error of the estimate
    null_value : float, default=0.0
        Null hypothesis value to test against

    Returns
    -------
    float
        T-statistic value

    Raises
    ------
    ValueError
        If standard_error is not positive
    TypeError
        If inputs are not numeric

    Examples
    --------
    >>> # Test if treatment effect differs from zero
    >>> t_stat = calculate_t_statistic(estimate=15.2, standard_error=4.8)
    >>> print(f"T-statistic: {t_stat:.3f}")
    T-statistic: 3.167

    >>> # Test if effect differs from a specific value
    >>> t_stat = calculate_t_statistic(
    ...     estimate=22.5, standard_error=6.1, null_value=20.0
    ... )
    >>> print(f"T-statistic: {t_stat:.3f}")
    T-statistic: 0.410

    Mathematical Formula
    --------------------
    t = (estimate - null_value) / standard_error

    Notes
    -----
    The t-statistic follows a t-distribution under the null hypothesis,
    with degrees of freedom determined by the underlying regression model.
    """
    # Input validation
    if not isinstance(estimate, (int, float, np.integer, np.floating)):
        raise TypeError(f"estimate must be numeric, got {type(estimate)}")

    if not isinstance(standard_error, (int, float, np.integer, np.floating)):
        raise TypeError(f"standard_error must be numeric, got {type(standard_error)}")

    if not isinstance(null_value, (int, float, np.integer, np.floating)):
        raise TypeError(f"null_value must be numeric, got {type(null_value)}")

    if standard_error <= 0:
        raise ValueError(f"standard_error must be positive, got {standard_error}")

    # Calculate t-statistic
    t_statistic = (estimate - null_value) / standard_error

    return float(t_statistic)


def calculate_p_value(
    t_statistic: float, degrees_freedom: int, two_tailed: bool = True
) -> float:
    """
    Calculate p-value from t-statistic using t-distribution.

    Computes the probability of observing a t-statistic as extreme or more extreme
    than the observed value, under the null hypothesis. This provides the
    statistical significance level for hypothesis testing.

    Parameters
    ----------
    t_statistic : float
        The computed t-statistic
    degrees_freedom : int
        Degrees of freedom for the t-distribution
    two_tailed : bool, default=True
        Whether to compute two-tailed (True) or one-tailed (False) p-value

    Returns
    -------
    float
        P-value between 0 and 1

    Raises
    ------
    ValueError
        If degrees_freedom is not positive
    TypeError
        If inputs have incorrect types

    Examples
    --------
    >>> # Two-tailed p-value
    >>> p_val = calculate_p_value(t_statistic=2.58, degrees_freedom=45)
    >>> print(f"Two-tailed p-value: {p_val:.4f}")
    Two-tailed p-value: 0.0132

    >>> # One-tailed p-value
    >>> p_val = calculate_p_value(
    ...     t_statistic=1.96, degrees_freedom=100, two_tailed=False
    ... )
    >>> print(f"One-tailed p-value: {p_val:.4f}")
    One-tailed p-value: 0.0262

    Mathematical Formula
    --------------------
    Two-tailed: P = 2 × [1 - F_t(|t|; df)]
    One-tailed: P = 1 - F_t(t; df) for t > 0, F_t(t; df) for t < 0

    where F_t is the cumulative t-distribution function.

    Notes
    -----
    Uses lazy import to minimize import overhead.
    The p-value represents the probability of Type I error under the null hypothesis.
    """
    # Lazy import to minimize overhead
    from scipy import stats

    # Input validation
    if not isinstance(t_statistic, (int, float, np.integer, np.floating)):
        raise TypeError(f"t_statistic must be numeric, got {type(t_statistic)}")

    if not isinstance(degrees_freedom, (int, np.integer)):
        raise TypeError(f"degrees_freedom must be integer, got {type(degrees_freedom)}")

    if not isinstance(two_tailed, bool):
        raise TypeError(f"two_tailed must be boolean, got {type(two_tailed)}")

    if degrees_freedom <= 0:
        raise ValueError(f"degrees_freedom must be positive, got {degrees_freedom}")

    # Calculate p-value
    if two_tailed:
        # Two-tailed test: P(|T| >= |t|)
        p_value = 2 * (1 - stats.t.cdf(abs(t_statistic), df=degrees_freedom))
    else:
        # One-tailed test: P(T >= t) for positive t, P(T <= t) for negative t
        if t_statistic >= 0:
            p_value = 1 - stats.t.cdf(t_statistic, df=degrees_freedom)
        else:
            p_value = stats.t.cdf(t_statistic, df=degrees_freedom)

    # Ensure p-value is between 0 and 1
    p_value = max(0.0, min(1.0, p_value))

    return float(p_value)


def calculate_posterior_probability(
    estimate: float,
    standard_error: float,
    degrees_freedom: int,
    threshold: float = 0.0,
) -> float:
    """
    Calculate posterior probability that true effect exceeds threshold.

    Computes the Bayesian posterior probability that the true treatment effect
    is greater than a specified threshold, given the observed data and assuming
    a non-informative prior. This is particularly useful for decision-making
    in TBR analysis.

    Parameters
    ----------
    estimate : float
        Point estimate of the treatment effect
    standard_error : float
        Standard error of the estimate
    degrees_freedom : int
        Degrees of freedom for the t-distribution
    threshold : float, default=0.0
        Threshold value for probability calculation

    Returns
    -------
    float
        Posterior probability between 0 and 1

    Raises
    ------
    ValueError
        If standard_error is not positive or degrees_freedom is not positive
    TypeError
        If inputs have incorrect types

    Examples
    --------
    >>> # Probability that effect is positive
    >>> prob = calculate_posterior_probability(
    ...     estimate=12.5, standard_error=4.2, degrees_freedom=48
    ... )
    >>> print(f"P(effect > 0): {prob:.3f}")
    P(effect > 0): 0.997

    >>> # Probability that effect exceeds minimum desired level
    >>> prob = calculate_posterior_probability(
    ...     estimate=12.5, standard_error=4.2, degrees_freedom=48, threshold=5.0
    ... )
    >>> print(f"P(effect > 5): {prob:.3f}")
    P(effect > 5): 0.963

    Mathematical Formula
    --------------------
    P(θ > τ | data) = 1 - F_t((τ - estimate) / standard_error; df)

    where F_t is the cumulative t-distribution function, θ is the true effect,
    and τ is the threshold.

    Notes
    -----
    This probability assumes a non-informative prior and uses the t-distribution
    to account for uncertainty in the variance estimate. The result represents
    the probability that the true effect exceeds the threshold, given the data.
    """
    # Lazy import to minimize overhead
    from scipy import stats

    # Input validation
    if not isinstance(estimate, (int, float, np.integer, np.floating)):
        raise TypeError(f"estimate must be numeric, got {type(estimate)}")

    if not isinstance(standard_error, (int, float, np.integer, np.floating)):
        raise TypeError(f"standard_error must be numeric, got {type(standard_error)}")

    if not isinstance(degrees_freedom, (int, np.integer)):
        raise TypeError(f"degrees_freedom must be integer, got {type(degrees_freedom)}")

    if not isinstance(threshold, (int, float, np.integer, np.floating)):
        raise TypeError(f"threshold must be numeric, got {type(threshold)}")

    if standard_error < 0:
        raise ValueError(f"standard_error must be non-negative, got {standard_error}")

    if degrees_freedom <= 0:
        raise ValueError(f"degrees_freedom must be positive, got {degrees_freedom}")

    # Calculate standardized threshold
    if standard_error > 0:
        t_stat = (threshold - estimate) / standard_error
        # P(θ > threshold) = 1 - P(T <= t_stat)
        probability = 1 - stats.t.cdf(t_stat, df=degrees_freedom)
    else:
        # If standard error is zero, probability is deterministic
        probability = 1.0 if estimate > threshold else 0.0

    # Ensure probability is between 0 and 1
    probability = max(0.0, min(1.0, probability))

    return float(probability)


def calculate_credible_interval(
    estimate: float,
    standard_error: float,
    degrees_freedom: int,
    confidence_level: float = 0.95,
) -> Dict[str, float]:
    """
    Calculate credible interval using t-distribution.

    Computes the credible interval for a parameter estimate using the t-distribution.
    This provides a range of plausible values for the true parameter given the
    observed data and specified credibility level.

    Parameters
    ----------
    estimate : float
        Point estimate of the parameter
    standard_error : float
        Standard error of the estimate
    degrees_freedom : int
        Degrees of freedom for the t-distribution
    confidence_level : float, default=0.95
        Credibility level between 0 and 1 (e.g., 0.95 for 95% credible interval)

    Returns
    -------
    Dict[str, float]
        Dictionary containing:
        - 'lower': Lower bound of credible interval
        - 'upper': Upper bound of credible interval
        - 'margin_of_error': Half-width of the interval
        - 'critical_value': T-critical value used

    Raises
    ------
    ValueError
        If standard_error is not positive, degrees_freedom is not positive,
        or confidence_level is not between 0 and 1
    TypeError
        If inputs have incorrect types

    Examples
    --------
    >>> # 95% credible interval
    >>> ci = calculate_credible_interval(
    ...     estimate=18.7, standard_error=5.2, degrees_freedom=42
    ... )
    >>> print(f"95% CI: [{ci['lower']:.2f}, {ci['upper']:.2f}]")
    95% CI: [8.22, 29.18]

    >>> # 80% credible interval
    >>> ci = calculate_credible_interval(
    ...     estimate=18.7, standard_error=5.2, degrees_freedom=42,
    ...     confidence_level=0.80
    ... )
    >>> print(f"80% CI: [{ci['lower']:.2f}, {ci['upper']:.2f}]")
    80% CI: [11.98, 25.42]

    Mathematical Formula
    --------------------
    CI = estimate ± t_{α/2,df} × standard_error

    where t_{α/2,df} is the critical value from t-distribution with α = 1 - confidence_level.

    Notes
    -----
    The credible interval represents the range of values that are consistent
    with the observed data at the specified credibility level. In the Bayesian
    interpretation used by TBR, there is a 95% posterior probability that the
    true parameter value lies within the 95% credible interval.
    """
    # Lazy import to minimize overhead
    from scipy import stats

    # Input validation
    if not isinstance(estimate, (int, float, np.integer, np.floating)):
        raise TypeError(f"estimate must be numeric, got {type(estimate)}")

    if not isinstance(standard_error, (int, float, np.integer, np.floating)):
        raise TypeError(f"standard_error must be numeric, got {type(standard_error)}")

    if not isinstance(degrees_freedom, (int, np.integer)):
        raise TypeError(f"degrees_freedom must be integer, got {type(degrees_freedom)}")

    if not isinstance(confidence_level, (int, float, np.integer, np.floating)):
        raise TypeError(
            f"confidence_level must be numeric, got {type(confidence_level)}"
        )

    if standard_error <= 0:
        raise ValueError(f"standard_error must be positive, got {standard_error}")

    if degrees_freedom <= 0:
        raise ValueError(f"degrees_freedom must be positive, got {degrees_freedom}")

    if not (0 < confidence_level < 1):
        raise ValueError(
            f"confidence_level must be between 0 and 1, got {confidence_level}"
        )

    # Calculate critical value
    alpha = 1 - confidence_level
    critical_value = stats.t.ppf(1 - alpha / 2, df=degrees_freedom)

    # Calculate margin of error
    margin_of_error = critical_value * standard_error

    # Calculate interval bounds
    lower = estimate - margin_of_error
    upper = estimate + margin_of_error

    return {
        "lower": float(lower),
        "upper": float(upper),
        "margin_of_error": float(margin_of_error),
        "critical_value": float(critical_value),
    }


def calculate_critical_value(
    degrees_freedom: int, confidence_level: float = 0.95, two_tailed: bool = True
) -> float:
    """
    Calculate critical value from t-distribution.

    Computes the critical value (quantile) from the t-distribution for a given
    credibility level and degrees of freedom. This is used for constructing
    credible intervals and conducting hypothesis tests.

    Parameters
    ----------
    degrees_freedom : int
        Degrees of freedom for the t-distribution
    confidence_level : float, default=0.95
        Credibility level between 0 and 1
    two_tailed : bool, default=True
        Whether to compute two-tailed (True) or one-tailed (False) critical value

    Returns
    -------
    float
        Critical value from t-distribution

    Raises
    ------
    ValueError
        If degrees_freedom is not positive or confidence_level is not between 0 and 1
    TypeError
        If inputs have incorrect types

    Examples
    --------
    >>> # Two-tailed 95% critical value
    >>> cv = calculate_critical_value(degrees_freedom=30)
    >>> print(f"t_{0.025,30} = {cv:.3f}")
    t_0.025,30 = 2.042

    >>> # One-tailed 95% critical value
    >>> cv = calculate_critical_value(
    ...     degrees_freedom=30, confidence_level=0.95, two_tailed=False
    ... )
    >>> print(f"t_{0.05,30} = {cv:.3f}")
    t_0.05,30 = 1.697

    Mathematical Formula
    --------------------
    Two-tailed: t_{α/2,df} where α = 1 - confidence_level
    One-tailed: t_{α,df} where α = 1 - confidence_level

    Notes
    -----
    Critical values are used to determine rejection regions in hypothesis testing
    and to construct credible intervals. The two-tailed version is most common
    for credible intervals, while one-tailed is used for directional tests.
    """
    # Lazy import to minimize overhead
    from scipy import stats

    # Input validation
    if not isinstance(degrees_freedom, (int, np.integer)):
        raise TypeError(f"degrees_freedom must be integer, got {type(degrees_freedom)}")

    if not isinstance(confidence_level, (int, float, np.integer, np.floating)):
        raise TypeError(
            f"confidence_level must be numeric, got {type(confidence_level)}"
        )

    if not isinstance(two_tailed, bool):
        raise TypeError(f"two_tailed must be boolean, got {type(two_tailed)}")

    if degrees_freedom <= 0:
        raise ValueError(f"degrees_freedom must be positive, got {degrees_freedom}")

    if not (0 < confidence_level < 1):
        raise ValueError(
            f"confidence_level must be between 0 and 1, got {confidence_level}"
        )

    # Calculate critical value
    alpha = 1 - confidence_level

    if two_tailed:
        # Two-tailed: use α/2
        critical_value = stats.t.ppf(1 - alpha / 2, df=degrees_freedom)
    else:
        # One-tailed: use α
        critical_value = stats.t.ppf(1 - alpha, df=degrees_freedom)

    return float(critical_value)
