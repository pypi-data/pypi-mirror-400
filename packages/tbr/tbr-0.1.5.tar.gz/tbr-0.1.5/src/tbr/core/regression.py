"""
TBR Regression Analysis Module.

This module provides the core mathematical implementations for TBR regression operations,
including linear regression model fitting, variance calculations, and statistical
parameter extraction. These are the foundational implementations that other modules
build upon.

The module focuses on:
- Linear regression model fitting for TBR analysis
- Variance calculations for model and prediction uncertainty
- Statistical parameter extraction and validation
- Core mathematical utilities for TBR methodology

All functions are independent implementations that do not depend on other TBR modules,
following clean architecture principles.

Examples
--------
>>> from tbr.core.regression import fit_regression_model, calculate_variances
>>> import pandas as pd
>>> import numpy as np
>>>
>>> # Prepare learning data
>>> learning_data = pd.DataFrame({
...     'control': np.random.normal(1000, 50, 30),
...     'test': np.random.normal(1020, 55, 30)
... })
>>>
>>> # Fit regression model
>>> model_params = fit_regression_model(learning_data, 'control', 'test')
>>> print(f"Beta coefficient: {model_params['beta']:.3f}")
>>>
>>> # Calculate variances
>>> x_values = np.array([1000, 1010, 1020])
>>> model_vars, pred_vars = calculate_variances(
...     x_values, model_params['pretest_x_mean'], model_params['sigma'],
...     model_params['n_pretest'], 100.0  # pretest_sum_x_squared_deviations
... )
"""

from typing import Dict, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm

from tbr.utils.preprocessing import extract_regression_arrays, prepare_regression_arrays
from tbr.utils.validation import (
    validate_array_not_empty,
    validate_learning_set,
    validate_sample_size,
)


def fit_regression_model(
    learning_data: pd.DataFrame,
    control_col: str,
    test_col: str,
) -> Dict[str, float]:
    """
    Fit TBR regression model using OLS on pretest period.

    This function fits a linear regression model of the form:
    test = α + β * control + ε

    The model is trained exclusively on the pretest period to avoid
    contamination from treatment effects.

    Parameters
    ----------
    learning_data : pd.DataFrame
        Learning set data used for training the regression model
    control_col : str
        Name of the control group metric column
    test_col : str
        Name of the test group metric column

    Returns
    -------
    Dict[str, float]
        Dictionary containing regression parameters:
        - 'alpha': Intercept (α)
        - 'beta': Slope coefficient (β)
        - 'sigma': Residual standard deviation (σ)
        - 'var_alpha': Variance of intercept estimate
        - 'var_beta': Variance of slope estimate
        - 'cov_alpha_beta': Covariance between α and β estimates
        - 'degrees_freedom': Residual degrees of freedom
        - 'n_pretest': Number of pretest observations
        - 'pretest_x_mean': Mean of control values from pretest period (x̄)

    Raises
    ------
    ValueError
        If insufficient data, constant control values, or invalid regression results

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> # Example with learning data
    >>> learning_data = pd.DataFrame({
    ...     'control': np.random.normal(1000, 50, 30),
    ...     'test': np.random.normal(1020, 55, 30)
    ... })
    >>> model = fit_regression_model(learning_data, 'control', 'test')
    >>> print(f"Beta coefficient: {model['beta']:.3f}")
    """
    # Validate learning set
    validate_learning_set(learning_data, control_col, test_col)

    # Extract x (control) and y (test) for regression
    x, y = extract_regression_arrays(learning_data, control_col, test_col)
    n = len(x)

    # Validation of regression inputs
    validate_array_not_empty(x, "control values")
    validate_array_not_empty(y, "test values")
    validate_sample_size(n, min_size=3, param_name="learning set size")

    # Check for constant control values
    if np.var(x) == 0:
        raise ValueError(
            "Control group values are constant in pretest period - cannot fit regression"
        )

    # Prepare data (add constant for intercept)
    X = prepare_regression_arrays(x, add_constant=True)

    # Fit OLS regression
    model = sm.OLS(y, X).fit()

    # Extract all parameters from fitted model
    alpha = model.params[0]  # Intercept
    beta = model.params[1]  # Slope

    # Extract variances from standard errors
    var_alpha = model.bse[0] ** 2  # Variance of intercept
    var_beta = model.bse[1] ** 2  # Variance of slope

    # Extract covariance from covariance matrix
    cov_matrix = model.cov_params()
    cov_alpha_beta = cov_matrix[0, 1]  # Covariance between intercept and slope

    # Extract other statistics
    sigma = np.sqrt(model.scale)  # Residual standard deviation
    degrees_freedom = int(model.df_resid)  # Degrees of freedom

    # Compute additional statistics needed for TBR
    pretest_x_mean = np.mean(x)

    # Validation of computed statistics
    if not np.isfinite([alpha, beta, sigma, var_alpha, var_beta, cov_alpha_beta]).all():
        raise ValueError("Computed regression parameters contain invalid values")

    if sigma <= 0:
        raise ValueError(f"Invalid residual standard deviation: {sigma}")

    if var_alpha <= 0 or var_beta <= 0:
        raise ValueError("Computed coefficient variances are non-positive")

    # Return all parameters as a simple dictionary
    return {
        "alpha": float(alpha),
        "beta": float(beta),
        "sigma": float(sigma),
        "var_alpha": float(var_alpha),
        "var_beta": float(var_beta),
        "cov_alpha_beta": float(cov_alpha_beta),
        "degrees_freedom": int(degrees_freedom),
        "n_pretest": int(n),
        "pretest_x_mean": float(pretest_x_mean),
    }


def calculate_model_variance(
    x_values: np.ndarray,
    pretest_x_mean: float,
    sigma: float,
    n_pretest: int,
    pretest_sum_x_squared_deviations: float,
) -> np.ndarray:
    """
    Calculate model variance for fitted values using TBR formula.

    Implements the TBR model variance formula for MODEL UNCERTAINTY ONLY:
    V[ŷ*] = σ² · (1/n + (x* - x̄)²/Σ(xi - x̄)²)

    This captures only the uncertainty in the fitted model, not the residual noise.
    For prediction variance which includes residual noise, use calculate_prediction_variance().

    Parameters
    ----------
    x_values : np.ndarray
        Control values (predictor variable x) from the test period (prediction targets)
    pretest_x_mean : float
        Mean of control values from pretest period (x̄)
    sigma : float
        Residual standard deviation from the model prediction over the pretest period (σ)
    n_pretest : int
        Number of observations in pretest period
    pretest_sum_x_squared_deviations : float
        Sum of squared deviations from pretest period: Σ(xi - x̄)²

    Returns
    -------
    np.ndarray
        Model variances for each x value (model uncertainty only)

    Examples
    --------
    >>> import numpy as np
    >>> # Calculate sum of squared deviations directly for maximum precision
    >>> x_vals = np.array([100, 110, 120])
    >>> sum_sq_dev = calculate_sum_squared_deviations(x_vals)
    >>> variances = calculate_model_variance(
    ...     x_vals, pretest_x_mean=110, sigma=10, n_pretest=30,
    ...     pretest_sum_x_squared_deviations=sum_sq_dev
    ... )
    >>> print(f"Model variances: {variances}")
    """
    # Apply TBR model variance formula (MODEL UNCERTAINTY ONLY)
    # V[ŷ*] = σ² · (1/n + (x* - x̄)²/Σ(xi - x̄)²)
    x_deviations_squared = (x_values - pretest_x_mean) ** 2

    model_variances = sigma**2 * (
        1.0 / n_pretest + x_deviations_squared / pretest_sum_x_squared_deviations
    )

    return model_variances


def calculate_prediction_variance(
    model_variances: np.ndarray,
    sigma: float,
) -> np.ndarray:
    """
    Calculate prediction variance by adding residual noise to model uncertainty.

    Implements the TBR prediction variance formula:
    V[y*] = σ² + V[ŷ*]

    This function adds the residual variance (σ²) to the model variances
    to get the total prediction variance including both model uncertainty
    and residual noise.

    Parameters
    ----------
    model_variances : np.ndarray
        Model variances from calculate_model_variance() (model uncertainty only)
    sigma : float
        Residual standard deviation from the model prediction over the learning set (σ)

    Returns
    -------
    np.ndarray
        Prediction variances (model uncertainty + residual noise)

    Examples
    --------
    >>> import numpy as np
    >>> # First calculate model variances
    >>> x_vals = np.array([1000, 1010, 1020])
    >>> model_vars = calculate_model_variance(
    ...     x_vals, pretest_x_mean=1005, sigma=25, n_pretest=30,
    ...     pretest_sum_x_squared_deviations=15000
    ... )
    >>> # Then calculate prediction variances
    >>> pred_vars = calculate_prediction_variance(model_vars, sigma=25)
    >>> print(f"Prediction uncertainties: {pred_vars}")
    """
    # Add residual variance: V[y*] = σ² + V[ŷ*]
    prediction_variances = sigma**2 + model_variances

    return prediction_variances


def calculate_variances(
    x_values: np.ndarray,
    pretest_x_mean: float,
    sigma: float,
    n_pretest: int,
    pretest_sum_x_squared_deviations: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate model and prediction variances for given x values.

    This function provides a convenient interface to calculate both model
    variances (uncertainty in fitted values) and prediction variances
    (total uncertainty including residual noise) in a single call.

    Parameters
    ----------
    x_values : np.ndarray
        Control values (predictor variable x) from the test period (prediction targets)
    pretest_x_mean : float
        Mean of control values from pretest period (x̄)
    sigma : float
        Residual standard deviation from the model prediction over the pretest period (σ)
    n_pretest : int
        Number of observations in pretest period
    pretest_sum_x_squared_deviations : float
        Sum of squared deviations from pretest period: Σ(xi - x̄)²

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        (model_variances, prediction_variances) where:
        - model_variances: Uncertainty in fitted values only
        - prediction_variances: Total uncertainty including residual noise

    Examples
    --------
    >>> import numpy as np
    >>> x_vals = np.array([1000, 1010, 1020])
    >>> model_vars, pred_vars = calculate_variances(
    ...     x_vals, pretest_x_mean=1005, sigma=25, n_pretest=30,
    ...     pretest_sum_x_squared_deviations=15000
    ... )
    >>> print(f"Model uncertainties: {model_vars}")
    >>> print(f"Prediction uncertainties: {pred_vars}")
    """
    # Calculate model variances (fitted value uncertainty only)
    model_variances = calculate_model_variance(
        x_values=x_values,
        pretest_x_mean=pretest_x_mean,
        sigma=sigma,
        n_pretest=n_pretest,
        pretest_sum_x_squared_deviations=pretest_sum_x_squared_deviations,
    )

    # Calculate prediction variances (total uncertainty)
    prediction_variances = calculate_prediction_variance(
        model_variances=model_variances,
        sigma=sigma,
    )

    return model_variances, prediction_variances


def calculate_sum_squared_deviations(x: np.ndarray) -> float:
    """
    Calculate sum of squared deviations from the mean.

    Computes Σ(xi - x̄)² where x̄ is the sample mean. Uses the mathematical
    definition for maximum numerical precision.

    Parameters
    ----------
    x : np.ndarray
        Input array of values

    Returns
    -------
    float
        Sum of squared deviations from the mean: Σ(xi - x̄)²

    Examples
    --------
    >>> import numpy as np
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> ssd = calculate_sum_squared_deviations(x)
    >>> print(f"Sum squared deviations: {ssd}")
    10.0
    """
    x_mean = np.mean(x)
    return float(np.sum((x - x_mean) ** 2))


def extract_sum_squared_deviations_from_model(var_beta: float, sigma: float) -> float:
    """
    Extract sum of squared deviations from regression model parameters.

    This function provides access to the mathematical relationship for
    extracting sum of squared deviations when original data is not available.

    Parameters
    ----------
    var_beta : float
        Variance of the slope coefficient (β) from regression model
    sigma : float
        Residual standard deviation from regression model

    Returns
    -------
    float
        Sum of squared deviations: Σ(xi - x̄)²

    Examples
    --------
    >>> # Extract from model parameters when original data unavailable
    >>> ssd = extract_sum_squared_deviations_from_model(var_beta=0.001, sigma=25.0)
    >>> print(f"Extracted sum squared deviations: {ssd}")
    """
    return sigma**2 / var_beta


def convert_to_integer(value: float, param_name: str) -> int:
    """
    Safely convert float to int with validation for statistical parameters.

    This function converts floating-point values that should be integers
    (like degrees of freedom) to actual integers, with validation to catch
    potential statistical calculation errors. Uses a 1% tolerance to handle
    floating-point precision issues.

    Parameters
    ----------
    value : float
        Value to convert (should be very close to an integer)
    param_name : str
        Parameter name for error messages

    Returns
    -------
    int
        Rounded integer value

    Raises
    ------
    ValueError
        If value is not close to an integer (tolerance > 0.01)

    Examples
    --------
    >>> degrees_freedom = convert_to_integer(43.0, "degrees_freedom")
    >>> print(f"Degrees of freedom: {degrees_freedom}")
    43
    >>> convert_to_integer(43.999999999999, "degrees_freedom")
    44
    >>> convert_to_integer(43.5, "degrees_freedom")  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ValueError: degrees_freedom should be an integer, got 43.5...
    """
    rounded_value = round(value)

    # Validate that the original was actually close to an integer
    if abs(value - rounded_value) > 0.01:  # 1% tolerance
        raise ValueError(
            f"{param_name} should be an integer, got {value}. "
            f"This indicates a potential issue with the statistical calculation."
        )

    return rounded_value


# Export list for clean imports
__all__ = [
    "fit_regression_model",
    "calculate_model_variance",
    "calculate_prediction_variance",
    "calculate_variances",
    "calculate_sum_squared_deviations",
    "extract_sum_squared_deviations_from_model",
    "convert_to_integer",
]
