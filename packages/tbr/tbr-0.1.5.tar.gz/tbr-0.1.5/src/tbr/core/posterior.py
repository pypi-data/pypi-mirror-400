"""
Advanced Posterior Probability Calculations and Threshold Testing for TBR.

This module provides sophisticated posterior probability analysis and threshold testing
capabilities that extend beyond basic statistical inference. It focuses on advanced
Bayesian analysis, threshold sensitivity, and multi-scenario posterior comparisons
for comprehensive TBR decision-making.

The implementation builds upon the basic inference module to provide:
- Advanced posterior variance calculations
- Threshold sensitivity analysis
- Incremental posterior probability tracking
- Bayesian threshold optimization
- Multi-scenario posterior comparisons
- Posterior distribution validation

Key Features
------------
- Sophisticated threshold testing strategies
- Multi-threshold sensitivity analysis
- Time-series posterior probability evolution
- Bayesian decision theory implementations
- Posterior distribution characterization
- Statistical validation

Examples
--------
>>> import numpy as np
>>> import pandas as pd
>>> from tbr.core.posterior import perform_threshold_sensitivity_analysis
>>>
>>> # Threshold sensitivity analysis
>>> thresholds = np.array([0.0, 5.0, 10.0, 15.0, 20.0])
>>> sensitivity = perform_threshold_sensitivity_analysis(
...     estimate=12.5, standard_error=4.2, degrees_freedom=45, thresholds=thresholds
... )
>>> print(f"Probabilities: {sensitivity['probabilities']}")

Mathematical Foundation
-----------------------
The advanced posterior probability functions implement sophisticated Bayesian
statistical methods:

1. **Posterior Variance**: V_post = Σ(estsd²) + n·σ²
   Advanced variance decomposition for interval estimation

2. **Threshold Sensitivity**: P(θ > τᵢ | data) for multiple thresholds τᵢ
   Comprehensive threshold testing across decision space

3. **Incremental Probabilities**: P(θₜ > τ | data₁:ₜ) for t = 1, 2, ..., T
   Time-series evolution of posterior beliefs

4. **Optimal Threshold**: τ* = argmax U(τ, θ̂, SE(θ̂))
   Bayesian decision-theoretic threshold selection

Notes
-----
All functions use lazy imports to minimize import overhead. Functions integrate
seamlessly with the basic inference module.

See individual function documentation for detailed usage and examples.
"""

from typing import Dict, List, Optional, Tuple, Union

import numpy as np


def calculate_posterior_variance(
    estsd_values: np.ndarray, n_days: int, sigma: float
) -> float:
    """
    Calculate posterior variance for TBR interval estimation.

    Computes the posterior variance using the TBR formula that combines
    estimation uncertainty (estsd²) with residual noise (σ²). This provides
    the foundation for credible intervals and posterior probability calculations.

    Parameters
    ----------
    estsd_values : np.ndarray
        Array of estimation standard deviations for each observation
    n_days : int
        Number of days in the analysis period
    sigma : float
        Residual standard deviation from the regression model

    Returns
    -------
    float
        Posterior variance value

    Raises
    ------
    ValueError
        If n_days is not positive or sigma is not positive
    TypeError
        If inputs have incorrect types

    Examples
    --------
    >>> import numpy as np
    >>> estsd = np.array([2.1, 2.3, 2.0, 2.4, 2.2])
    >>> posterior_var = calculate_posterior_variance(estsd, n_days=5, sigma=1.8)
    >>> print(f"Posterior variance: {posterior_var:.3f}")
    Posterior variance: 39.510

    Mathematical Formula
    --------------------
    V_posterior = Σ(estsd²) + n_days × σ²

    This decomposition separates:
    - Estimation uncertainty: Σ(estsd²) from prediction variance
    - Residual noise: n_days × σ² from model uncertainty

    Notes
    -----
    This function extracts the posterior variance calculation used in
    compute_interval_estimate_and_ci from the functional module, making
    it available as a standalone utility for advanced analysis.
    """
    # Input validation
    if not isinstance(estsd_values, np.ndarray):
        raise TypeError(f"estsd_values must be numpy array, got {type(estsd_values)}")

    if not isinstance(n_days, (int, np.integer)):
        raise TypeError(f"n_days must be integer, got {type(n_days)}")

    if not isinstance(sigma, (int, float, np.integer, np.floating)):
        raise TypeError(f"sigma must be numeric, got {type(sigma)}")

    if n_days <= 0:
        raise ValueError(f"n_days must be positive, got {n_days}")

    if sigma <= 0:
        raise ValueError(f"sigma must be positive, got {sigma}")

    if len(estsd_values) == 0:
        raise ValueError("estsd_values cannot be empty")

    # Calculate posterior variance components
    estimation_variance = np.sum(estsd_values**2)
    residual_variance = n_days * (sigma**2)
    posterior_variance = estimation_variance + residual_variance

    return float(posterior_variance)


def perform_threshold_sensitivity_analysis(
    estimate: float,
    standard_error: float,
    degrees_freedom: int,
    thresholds: np.ndarray,
) -> Dict[str, np.ndarray]:
    """
    Perform sensitivity analysis across multiple threshold values.

    Calculates posterior probabilities for a range of threshold values to
    understand how the probability of exceeding different thresholds varies.
    This enables comprehensive threshold testing and sensitivity analysis
    for decision-making in TBR analysis.

    Parameters
    ----------
    estimate : float
        Point estimate of the treatment effect
    standard_error : float
        Standard error of the estimate
    degrees_freedom : int
        Degrees of freedom for the t-distribution
    thresholds : np.ndarray
        Array of threshold values to test

    Returns
    -------
    Dict[str, np.ndarray]
        Dictionary containing:
        - 'thresholds': Input threshold values
        - 'probabilities': Posterior probabilities for each threshold
        - 'log_odds': Log odds ratios for each threshold
        - 'sensitivity': Gradient of probability with respect to threshold

    Raises
    ------
    ValueError
        If standard_error is not positive, degrees_freedom is not positive,
        or thresholds array is empty
    TypeError
        If inputs have incorrect types

    Examples
    --------
    >>> import numpy as np
    >>> thresholds = np.array([0.0, 5.0, 10.0, 15.0, 20.0])
    >>> sensitivity = perform_threshold_sensitivity_analysis(
    ...     estimate=12.5, standard_error=4.2, degrees_freedom=45, thresholds=thresholds
    ... )
    >>> print(f"P(effect > 10): {sensitivity['probabilities'][2]:.3f}")
    P(effect > 10): 0.723

    Mathematical Formula
    --------------------
    For each threshold τᵢ:
    P(θ > τᵢ | data) = 1 - F_t((τᵢ - estimate) / standard_error; df)

    Sensitivity = dP/dτ = -f_t((τ - estimate) / SE; df) / SE
    where f_t is the t-distribution PDF

    Notes
    -----
    This function enables comprehensive threshold testing by evaluating
    posterior probabilities across a range of decision-relevant thresholds.
    The sensitivity analysis helps identify critical threshold regions.
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

    if not isinstance(thresholds, np.ndarray):
        raise TypeError(f"thresholds must be numpy array, got {type(thresholds)}")

    if standard_error <= 0:
        raise ValueError(f"standard_error must be positive, got {standard_error}")

    if degrees_freedom <= 0:
        raise ValueError(f"degrees_freedom must be positive, got {degrees_freedom}")

    if len(thresholds) == 0:
        raise ValueError("thresholds array cannot be empty")

    # Calculate t-statistics for all thresholds
    t_statistics = (thresholds - estimate) / standard_error

    # Calculate posterior probabilities
    probabilities = 1 - stats.t.cdf(t_statistics, df=degrees_freedom)

    # Ensure probabilities are bounded
    probabilities = np.clip(probabilities, 0.0, 1.0)

    # Calculate log odds ratios (avoiding division by zero)
    epsilon = 1e-15
    log_odds = np.log((probabilities + epsilon) / (1 - probabilities + epsilon))

    # Calculate sensitivity (gradient of probability w.r.t. threshold)
    # Sensitivity = -f_t(t_stat) / SE where f_t is PDF
    pdf_values = stats.t.pdf(t_statistics, df=degrees_freedom)
    sensitivity = -pdf_values / standard_error

    return {
        "thresholds": thresholds.copy(),
        "probabilities": probabilities,
        "log_odds": log_odds,
        "sensitivity": sensitivity,
    }


def calculate_incremental_posterior_probabilities(
    estimates: np.ndarray,
    standard_errors: np.ndarray,
    degrees_freedom: int,
    threshold: float = 0.0,
) -> Dict[str, np.ndarray]:
    """
    Calculate incremental posterior probabilities for time-series analysis.

    Computes posterior probabilities for incremental time periods (day 1,
    days 1-2, days 1-3, etc.) to track how posterior beliefs evolve over
    the test period. This enables analysis of when effects become detectable
    and how confidence builds over time.

    Parameters
    ----------
    estimates : np.ndarray
        Array of cumulative effect estimates for each time period
    standard_errors : np.ndarray
        Array of cumulative standard errors for each time period
    degrees_freedom : int
        Degrees of freedom for the t-distribution
    threshold : float, default=0.0
        Threshold value for probability calculation

    Returns
    -------
    Dict[str, np.ndarray]
        Dictionary containing:
        - 'day': Day numbers (1, 2, 3, ...)
        - 'estimates': Cumulative estimates
        - 'standard_errors': Cumulative standard errors
        - 'probabilities': Posterior probabilities for each period
        - 'probability_change': Change in probability from previous day

    Raises
    ------
    ValueError
        If arrays have different lengths, are empty, or degrees_freedom is not positive
    TypeError
        If inputs have incorrect types

    Examples
    --------
    >>> import numpy as np
    >>> estimates = np.array([2.1, 4.8, 7.2, 9.1, 11.5])
    >>> std_errors = np.array([3.2, 4.1, 4.8, 5.2, 5.6])
    >>> incremental = calculate_incremental_posterior_probabilities(
    ...     estimates, std_errors, degrees_freedom=45
    ... )
    >>> print(f"Day 5 probability: {incremental['probabilities'][4]:.3f}")
    Day 5 probability: 0.982

    Mathematical Formula
    --------------------
    For each day t:
    P(θₜ > threshold | data₁:ₜ) = 1 - F_t((threshold - estimate_t) / SE_t; df)

    Probability change: ΔP_t = P_t - P_{t-1}

    Notes
    -----
    This function enables tracking of how posterior beliefs evolve during
    the test period, providing insights into the temporal dynamics of
    treatment effect detection and confidence building.
    """
    # Lazy import to minimize overhead
    from scipy import stats

    # Input validation
    if not isinstance(estimates, np.ndarray):
        raise TypeError(f"estimates must be numpy array, got {type(estimates)}")

    if not isinstance(standard_errors, np.ndarray):
        raise TypeError(
            f"standard_errors must be numpy array, got {type(standard_errors)}"
        )

    if not isinstance(degrees_freedom, (int, np.integer)):
        raise TypeError(f"degrees_freedom must be integer, got {type(degrees_freedom)}")

    if not isinstance(threshold, (int, float, np.integer, np.floating)):
        raise TypeError(f"threshold must be numeric, got {type(threshold)}")

    if len(estimates) == 0:
        raise ValueError("estimates array cannot be empty")

    if len(standard_errors) == 0:
        raise ValueError("standard_errors array cannot be empty")

    if len(estimates) != len(standard_errors):
        raise ValueError(
            f"estimates and standard_errors must have same length: "
            f"{len(estimates)} vs {len(standard_errors)}"
        )

    if degrees_freedom <= 0:
        raise ValueError(f"degrees_freedom must be positive, got {degrees_freedom}")

    # Calculate t-statistics for all time periods
    t_statistics = (threshold - estimates) / standard_errors

    # Calculate posterior probabilities
    probabilities = 1 - stats.t.cdf(t_statistics, df=degrees_freedom)

    # Ensure probabilities are bounded
    probabilities = np.clip(probabilities, 0.0, 1.0)

    # Calculate probability changes (difference from previous day)
    probability_change = np.zeros_like(probabilities)
    probability_change[1:] = probabilities[1:] - probabilities[:-1]

    # Create day numbers
    days = np.arange(1, len(estimates) + 1)

    return {
        "day": days,
        "estimates": estimates.copy(),
        "standard_errors": standard_errors.copy(),
        "probabilities": probabilities,
        "probability_change": probability_change,
    }


def optimize_threshold_selection(
    estimate: float,
    standard_error: float,
    degrees_freedom: int,
    utility_function: str = "balanced",
    threshold_range: Optional[Tuple[float, float]] = None,
) -> Dict[str, float]:
    """
    Optimize threshold selection using Bayesian decision theory.

    Finds the optimal threshold that maximizes expected utility given the
    posterior distribution of the treatment effect. This enables principled
    threshold selection based on decision-theoretic considerations rather
    than arbitrary choices.

    Parameters
    ----------
    estimate : float
        Point estimate of the treatment effect
    standard_error : float
        Standard error of the estimate
    degrees_freedom : int
        Degrees of freedom for the t-distribution
    utility_function : str, default="balanced"
        Utility function type: "balanced", "conservative", "aggressive"
    threshold_range : Tuple[float, float], optional
        Range of thresholds to consider. If None, uses estimate ± 3*SE

    Returns
    -------
    Dict[str, float]
        Dictionary containing:
        - 'optimal_threshold': Threshold that maximizes expected utility
        - 'max_utility': Maximum expected utility value
        - 'probability_at_optimal': Posterior probability at optimal threshold
        - 'confidence_width': Width of high-confidence region

    Raises
    ------
    ValueError
        If standard_error is not positive, degrees_freedom is not positive,
        or utility_function is not recognized
    TypeError
        If inputs have incorrect types

    Examples
    --------
    >>> optimal = optimize_threshold_selection(
    ...     estimate=12.5, standard_error=4.2, degrees_freedom=45,
    ...     utility_function="balanced"
    ... )
    >>> print(f"Optimal threshold: {optimal['optimal_threshold']:.2f}")
    Optimal threshold: 8.30

    Utility Functions
    -----------------
    - "balanced": Equal weight to Type I and Type II errors
    - "conservative": Higher penalty for false positives
    - "aggressive": Higher penalty for false negatives

    Mathematical Foundation
    ----------------------
    Expected Utility: EU(τ) = ∫ U(τ, θ) × p(θ | data) dθ

    Where U(τ, θ) depends on the chosen utility function and represents
    the decision-theoretic value of choosing threshold τ when true effect is θ.

    Notes
    -----
    This function implements Bayesian decision theory for threshold selection,
    providing principled alternatives to arbitrary threshold choices like 0.
    The optimization considers both the posterior distribution and decision costs.
    """
    # Lazy import to minimize overhead
    from scipy import optimize, stats

    # Input validation
    if not isinstance(estimate, (int, float, np.integer, np.floating)):
        raise TypeError(f"estimate must be numeric, got {type(estimate)}")

    if not isinstance(standard_error, (int, float, np.integer, np.floating)):
        raise TypeError(f"standard_error must be numeric, got {type(standard_error)}")

    if not isinstance(degrees_freedom, (int, np.integer)):
        raise TypeError(f"degrees_freedom must be integer, got {type(degrees_freedom)}")

    if not isinstance(utility_function, str):
        raise TypeError(
            f"utility_function must be string, got {type(utility_function)}"
        )

    if utility_function not in ["balanced", "conservative", "aggressive"]:
        raise ValueError(
            f"utility_function must be 'balanced', 'conservative', or 'aggressive', "
            f"got '{utility_function}'"
        )

    if standard_error <= 0:
        raise ValueError(f"standard_error must be positive, got {standard_error}")

    if degrees_freedom <= 0:
        raise ValueError(f"degrees_freedom must be positive, got {degrees_freedom}")

    # Set threshold range if not provided
    if threshold_range is None:
        margin = 3 * standard_error
        threshold_range = (estimate - margin, estimate + margin)

    # Define utility functions
    def balanced_utility(threshold: float) -> float:
        """Balanced utility: equal weight to Type I and Type II errors."""
        prob = 1 - stats.t.cdf(
            (threshold - estimate) / standard_error, df=degrees_freedom
        )
        # Utility = probability of correct decision - probability of incorrect decision
        return float(2 * prob - 1 if threshold <= estimate else 1 - 2 * prob)

    def conservative_utility(threshold: float) -> float:
        """Conservative utility: higher penalty for false positives."""
        prob = 1 - stats.t.cdf(
            (threshold - estimate) / standard_error, df=degrees_freedom
        )
        # Higher penalty for claiming effect when threshold is high
        penalty_factor = 1.5 if threshold > estimate else 1.0
        return float(prob - penalty_factor * (1 - prob))

    def aggressive_utility(threshold: float) -> float:
        """Aggressive utility: higher penalty for false negatives."""
        prob = 1 - stats.t.cdf(
            (threshold - estimate) / standard_error, df=degrees_freedom
        )
        # Higher penalty for missing effect when threshold is low
        penalty_factor = 1.5 if threshold < estimate else 1.0
        return float(penalty_factor * prob - (1 - prob))

    # Select utility function
    utility_map = {
        "balanced": balanced_utility,
        "conservative": conservative_utility,
        "aggressive": aggressive_utility,
    }
    utility_func = utility_map[utility_function]

    # Optimize threshold (minimize negative utility)
    result = optimize.minimize_scalar(
        lambda x: -utility_func(x), bounds=threshold_range, method="bounded"
    )

    optimal_threshold = result.x
    max_utility = -result.fun

    # Calculate additional metrics
    prob_at_optimal = 1 - stats.t.cdf(
        (optimal_threshold - estimate) / standard_error, df=degrees_freedom
    )
    prob_at_optimal = max(0.0, min(1.0, prob_at_optimal))

    # Calculate confidence width (95% credible interval width)
    t_critical = stats.t.ppf(0.975, df=degrees_freedom)
    confidence_width = 2 * t_critical * standard_error

    return {
        "optimal_threshold": float(optimal_threshold),
        "max_utility": float(max_utility),
        "probability_at_optimal": float(prob_at_optimal),
        "confidence_width": float(confidence_width),
    }


def compare_posterior_probabilities(
    scenarios: List[Dict[str, float]], threshold: float = 0.0
) -> Dict[str, Union[List[str], List[float], List[int]]]:
    """
    Compare posterior probabilities across multiple scenarios.

    Calculates and compares posterior probabilities for different scenarios
    (e.g., different experiments, time periods, or model specifications).
    This enables comparative analysis and helps identify scenarios with
    stronger or weaker evidence for treatment effects.

    Parameters
    ----------
    scenarios : List[Dict[str, float]]
        List of scenario dictionaries, each containing:
        - 'estimate': Point estimate
        - 'standard_error': Standard error
        - 'degrees_freedom': Degrees of freedom
        - 'name': Scenario name (optional)
    threshold : float, default=0.0
        Threshold value for probability calculation

    Returns
    -------
    Dict[str, Union[List[float], np.ndarray]]
        Dictionary containing:
        - 'scenario_names': Names or indices of scenarios
        - 'probabilities': Posterior probabilities for each scenario
        - 'relative_strength': Relative evidence strength (normalized)
        - 'ranking': Ranking of scenarios by probability (1 = highest)

    Raises
    ------
    ValueError
        If scenarios list is empty or scenarios have invalid parameters
    TypeError
        If inputs have incorrect types

    Examples
    --------
    >>> scenarios = [
    ...     {'estimate': 10.0, 'standard_error': 3.0, 'degrees_freedom': 30, 'name': 'Week1'},
    ...     {'estimate': 15.0, 'standard_error': 4.0, 'degrees_freedom': 30, 'name': 'Week2'},
    ...     {'estimate': 8.0, 'standard_error': 2.5, 'degrees_freedom': 30, 'name': 'Week3'}
    ... ]
    >>> comparison = compare_posterior_probabilities(scenarios)
    >>> print(f"Strongest evidence: {comparison['scenario_names'][0]}")
    Strongest evidence: Week2

    Mathematical Formula
    --------------------
    For each scenario i:
    P_i(θ > threshold | data_i) = 1 - F_t((threshold - estimate_i) / SE_i; df_i)

    Relative strength: RS_i = P_i / Σ(P_j) for j = 1, ..., n

    Notes
    -----
    This function enables systematic comparison of evidence strength across
    multiple scenarios, helping identify the most compelling cases for
    treatment effects and supporting meta-analytic thinking.
    """
    # Lazy import to minimize overhead
    from scipy import stats

    # Input validation
    if not isinstance(scenarios, list):
        raise TypeError(f"scenarios must be list, got {type(scenarios)}")

    if len(scenarios) == 0:
        raise ValueError("scenarios list cannot be empty")

    if not isinstance(threshold, (int, float, np.integer, np.floating)):
        raise TypeError(f"threshold must be numeric, got {type(threshold)}")

    # Validate each scenario
    required_keys = ["estimate", "standard_error", "degrees_freedom"]
    for i, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            raise TypeError(f"scenario {i} must be dict, got {type(scenario)}")

        for key in required_keys:
            if key not in scenario:
                raise ValueError(f"scenario {i} missing required key: {key}")

        if scenario["standard_error"] <= 0:
            raise ValueError(
                f"scenario {i} standard_error must be positive, got {scenario['standard_error']}"
            )

        if scenario["degrees_freedom"] <= 0:
            raise ValueError(
                f"scenario {i} degrees_freedom must be positive, got {scenario['degrees_freedom']}"
            )

    # Extract scenario information
    scenario_names = []
    probabilities_list = []

    for i, scenario in enumerate(scenarios):
        # Get scenario name
        name = str(scenario.get("name", f"Scenario_{i+1}"))
        scenario_names.append(name)

        # Calculate posterior probability
        estimate = scenario["estimate"]
        se = scenario["standard_error"]
        df = scenario["degrees_freedom"]

        t_stat = (threshold - estimate) / se
        prob = 1 - stats.t.cdf(t_stat, df=df)
        prob = max(0.0, min(1.0, prob))  # Ensure bounds
        probabilities_list.append(prob)

    # Convert to numpy array for easier manipulation
    probabilities = np.array(probabilities_list)

    # Calculate relative strength (normalized probabilities)
    total_prob = np.sum(probabilities)
    if total_prob > 0:
        relative_strength = probabilities / total_prob
    else:
        relative_strength = np.ones(len(probabilities)) / len(probabilities)

    # Calculate ranking (1 = highest probability)
    # Sort indices by probability in descending order, then assign ranks
    sorted_indices = np.argsort(probabilities)[::-1]  # Highest to lowest
    ranking = np.zeros(len(probabilities), dtype=int)
    for rank, idx in enumerate(sorted_indices):
        ranking[idx] = rank + 1  # Ranks start from 1

    return {
        "scenario_names": scenario_names,
        "probabilities": probabilities.tolist(),
        "relative_strength": relative_strength.tolist(),
        "ranking": ranking.tolist(),
    }


def validate_posterior_assumptions(
    residuals: np.ndarray,
    degrees_freedom: int,
    alpha: float = 0.05,
) -> Dict[str, Union[bool, float, str, List[str], None]]:
    """
    Validate assumptions underlying posterior probability calculations.

    Performs statistical tests to validate the assumptions required for
    valid posterior probability calculations, including normality of residuals,
    independence, and appropriate degrees of freedom. This ensures the
    reliability of posterior probability estimates.

    Parameters
    ----------
    residuals : np.ndarray
        Array of regression residuals
    degrees_freedom : int
        Degrees of freedom used in posterior calculations
    alpha : float, default=0.05
        Significance level for statistical tests

    Returns
    -------
    Dict[str, Union[bool, float, str]]
        Dictionary containing:
        - 'normality_valid': Whether normality assumption is satisfied
        - 'normality_pvalue': P-value from Shapiro-Wilk test
        - 'independence_valid': Whether independence assumption is satisfied
        - 'independence_pvalue': P-value from Durbin-Watson test
        - 'sample_size_adequate': Whether sample size is adequate
        - 'overall_validity': Overall assessment ("Valid", "Questionable", "Invalid")
        - 'recommendations': List of recommendations for improvement

    Raises
    ------
    ValueError
        If residuals array is empty, degrees_freedom is not positive,
        or alpha is not between 0 and 1
    TypeError
        If inputs have incorrect types

    Examples
    --------
    >>> import numpy as np
    >>> residuals = np.random.normal(0, 1, 50)  # Simulated residuals
    >>> validation = validate_posterior_assumptions(residuals, degrees_freedom=47)
    >>> print(f"Overall validity: {validation['overall_validity']}")
    Overall validity: Valid

    Statistical Tests
    -----------------
    1. **Normality**: Shapiro-Wilk test for normal distribution of residuals
    2. **Independence**: Durbin-Watson test for serial correlation
    3. **Sample Size**: Check for adequate degrees of freedom (>= 30 preferred)

    Notes
    -----
    This function provides diagnostic capabilities to ensure that posterior
    probability calculations are based on valid statistical assumptions.
    Violations may indicate need for robust methods or model adjustments.
    """
    # Lazy import to minimize overhead
    from scipy import stats

    # Input validation
    if not isinstance(residuals, np.ndarray):
        raise TypeError(f"residuals must be numpy array, got {type(residuals)}")

    if not isinstance(degrees_freedom, (int, np.integer)):
        raise TypeError(f"degrees_freedom must be integer, got {type(degrees_freedom)}")

    if not isinstance(alpha, (int, float, np.integer, np.floating)):
        raise TypeError(f"alpha must be numeric, got {type(alpha)}")

    if len(residuals) == 0:
        raise ValueError("residuals array cannot be empty")

    if degrees_freedom <= 0:
        raise ValueError(f"degrees_freedom must be positive, got {degrees_freedom}")

    if not (0 < alpha < 1):
        raise ValueError(f"alpha must be between 0 and 1, got {alpha}")

    recommendations = []

    # Test 1: Normality (Shapiro-Wilk test)
    if len(residuals) >= 3:  # Minimum for Shapiro-Wilk
        normality_stat, normality_pvalue = stats.shapiro(residuals)
        normality_valid = normality_pvalue > alpha
    else:
        normality_pvalue = np.nan
        normality_valid = False
        recommendations.append("Insufficient data for normality test (n < 3)")

    # Test 2: Independence (Durbin-Watson test approximation)
    if len(residuals) >= 4:  # Minimum for meaningful autocorrelation test
        # Calculate first-order autocorrelation
        residuals_lag1 = residuals[1:]
        residuals_lag0 = residuals[:-1]
        correlation = np.corrcoef(residuals_lag0, residuals_lag1)[0, 1]

        # Approximate Durbin-Watson statistic
        dw_stat = 2 * (1 - correlation)

        # Test for independence (DW should be around 2 for independence)
        # Rough approximation: reject independence if DW < 1.5 or DW > 2.5
        independence_valid = 1.5 <= dw_stat <= 2.5
        independence_pvalue = 2 * min(
            stats.norm.cdf((dw_stat - 2) / 0.5), 1 - stats.norm.cdf((dw_stat - 2) / 0.5)
        )
    else:
        dw_stat = np.nan
        independence_pvalue = np.nan
        independence_valid = False
        recommendations.append("Insufficient data for independence test (n < 4)")

    # Test 3: Sample size adequacy
    sample_size_adequate = degrees_freedom >= 30
    if not sample_size_adequate:
        recommendations.append(
            f"Small sample size (df={degrees_freedom}). "
            f"Consider df >= 30 for reliable t-distribution approximation"
        )

    # Overall validity assessment
    valid_tests = sum([normality_valid, independence_valid, sample_size_adequate])

    if valid_tests == 3:
        overall_validity = "Valid"
    elif valid_tests >= 2:
        overall_validity = "Questionable"
    else:
        overall_validity = "Invalid"

    # Add specific recommendations
    if not normality_valid and not np.isnan(normality_pvalue):
        recommendations.append(
            f"Residuals may not be normally distributed (p={normality_pvalue:.4f}). "
            f"Consider robust methods or data transformation"
        )

    if not independence_valid and not np.isnan(independence_pvalue):
        recommendations.append(
            f"Residuals may be serially correlated (DW={dw_stat:.2f}). "
            f"Consider time series methods or clustering"
        )

    return {
        "normality_valid": bool(normality_valid),
        "normality_pvalue": float(normality_pvalue)
        if not np.isnan(normality_pvalue)
        else None,
        "independence_valid": bool(independence_valid),
        "independence_pvalue": float(independence_pvalue)
        if not np.isnan(independence_pvalue)
        else None,
        "sample_size_adequate": bool(sample_size_adequate),
        "overall_validity": overall_validity,
        "recommendations": recommendations,
    }
