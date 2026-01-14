"""
Model Diagnostics and Assumption Testing for TBR Regression.

This module provides comprehensive diagnostic tools for validating TBR regression
models, including goodness-of-fit metrics, residual analysis, and statistical
assumption testing. These diagnostics ensure model validity and help identify
potential violations of regression assumptions.

Key Features
------------
- Goodness-of-fit metrics: R², Adjusted R², AIC, BIC, F-statistic
- Residual analysis: Raw, standardized, and studentized residuals
- Assumption testing: Normality, homoscedasticity, independence tests
- Comprehensive diagnostic summaries and reporting

Examples
--------
>>> import pandas as pd
>>> import numpy as np
>>> from tbr.core.diagnostics import calculate_goodness_of_fit, test_normality
>>> from tbr.core.regression import fit_regression_model
>>>
>>> # Fit regression model
>>> learning_data = pd.DataFrame({
...     'control': np.random.normal(1000, 50, 30),
...     'test': np.random.normal(1020, 55, 30)
... })
>>> model_params = fit_regression_model(learning_data, 'control', 'test')
>>>
>>> # Calculate goodness-of-fit metrics
>>> gof_metrics = calculate_goodness_of_fit(learning_data, model_params, 'control', 'test')
>>> print(f"R-squared: {gof_metrics['r_squared']:.3f}")
>>> print(f"AIC: {gof_metrics['aic']:.2f}")
>>>
>>> # Test normality of residuals
>>> residuals = calculate_residuals(learning_data, model_params, 'control', 'test')
>>> normality_result = test_normality(residuals)
>>> print(f"Normality p-value: {normality_result['p_value']:.4f}")

Notes
-----
All diagnostic functions provide comprehensive statistical information
for model validation and assumption checking.
"""

from typing import Dict, List, TypedDict, Union

import numpy as np
import pandas as pd

from tbr.utils.preprocessing import extract_regression_arrays, prepare_regression_arrays
from tbr.utils.validation import validate_array_not_empty, validate_sample_size


# TypedDict definitions for return types
class NormalityTestResult(TypedDict):
    """Result of normality test."""

    statistic: float
    p_value: float
    is_normal: bool
    test_name: str


class HomoscedasticityTestResult(TypedDict):
    """Result of homoscedasticity test."""

    statistic: float
    p_value: float
    is_homoscedastic: bool
    test_name: str


class IndependenceTestResult(TypedDict):
    """Result of independence test."""

    statistic: float
    interpretation: str
    is_independent: bool
    test_name: str


class DiagnosticSummary(TypedDict):
    """Comprehensive diagnostic summary result."""

    goodness_of_fit: Dict[str, float]
    information_criteria: Dict[str, float]
    normality_test: NormalityTestResult
    homoscedasticity_test: HomoscedasticityTestResult
    independence_test: IndependenceTestResult
    overall_validity: bool
    warnings: List[str]


# Export list for clean imports
__all__ = [
    "calculate_residuals",
    "calculate_standardized_residuals",
    "calculate_studentized_residuals",
    "calculate_goodness_of_fit",
    "calculate_information_criteria",
    "check_normality",
    "check_homoscedasticity",
    "check_independence",
    "create_diagnostic_summary",
    "validate_model_assumptions",
]


def calculate_residuals(
    data: pd.DataFrame,
    model_params: Dict[str, float],
    control_col: str,
    test_col: str,
) -> np.ndarray:
    """
    Calculate raw residuals from fitted TBR regression model.

    Computes residuals as: e_i = y_i - (α + β * x_i)
    where α and β are the fitted regression parameters.

    Parameters
    ----------
    data : pd.DataFrame
        Data used for regression fitting
    model_params : Dict[str, float]
        Regression parameters from fit_regression_model()
    control_col : str
        Name of the control group metric column
    test_col : str
        Name of the test group metric column

    Returns
    -------
    np.ndarray
        Array of residuals with same length as input data

    Raises
    ------
    ValueError
        If data is insufficient or model parameters are invalid

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> from tbr.core.regression import fit_regression_model
    >>>
    >>> # Create test data
    >>> data = pd.DataFrame({
    ...     'control': [100, 110, 120, 130, 140],
    ...     'test': [105, 115, 125, 135, 145]
    ... })
    >>> model_params = fit_regression_model(data, 'control', 'test')
    >>> residuals = calculate_residuals(data, model_params, 'control', 'test')
    >>> print(f"Mean residual: {np.mean(residuals):.6f}")  # Should be ~0
    """
    # Extract regression arrays
    x, y = extract_regression_arrays(data, control_col, test_col)

    # Validate inputs
    validate_array_not_empty(x, "control values")
    validate_array_not_empty(y, "test values")
    validate_sample_size(len(x), min_size=3, param_name="data size")

    # Extract model parameters
    alpha = model_params["alpha"]
    beta = model_params["beta"]

    # Calculate fitted values
    y_fitted = alpha + beta * x

    # Calculate residuals
    residuals = y - y_fitted

    return residuals


def calculate_standardized_residuals(
    data: pd.DataFrame,
    model_params: Dict[str, float],
    control_col: str,
    test_col: str,
) -> np.ndarray:
    """
    Calculate standardized residuals from fitted TBR regression model.

    Computes standardized residuals as: r_i = e_i / σ
    where e_i are raw residuals and σ is the residual standard deviation.

    Parameters
    ----------
    data : pd.DataFrame
        Data used for regression fitting
    model_params : Dict[str, float]
        Regression parameters from fit_regression_model()
    control_col : str
        Name of the control group metric column
    test_col : str
        Name of the test group metric column

    Returns
    -------
    np.ndarray
        Array of standardized residuals

    Examples
    --------
    >>> # Using same data as calculate_residuals example
    >>> std_residuals = calculate_standardized_residuals(data, model_params, 'control', 'test')
    >>> print(f"Std deviation of standardized residuals: {np.std(std_residuals):.3f}")
    """
    # Calculate raw residuals
    residuals = calculate_residuals(data, model_params, control_col, test_col)

    # Extract residual standard deviation
    sigma = model_params["sigma"]

    # Calculate standardized residuals
    standardized_residuals = residuals / sigma

    return standardized_residuals


def calculate_studentized_residuals(
    data: pd.DataFrame,
    model_params: Dict[str, float],
    control_col: str,
    test_col: str,
) -> np.ndarray:
    """
    Calculate studentized residuals from fitted TBR regression model.

    Computes studentized residuals as: t_i = e_i / (σ * √(1 - h_ii))
    where h_ii is the leverage (hat matrix diagonal element) for observation i.

    Parameters
    ----------
    data : pd.DataFrame
        Data used for regression fitting
    model_params : Dict[str, float]
        Regression parameters from fit_regression_model()
    control_col : str
        Name of the control group metric column
    test_col : str
        Name of the test group metric column

    Returns
    -------
    np.ndarray
        Array of studentized residuals

    Examples
    --------
    >>> # Using same data as previous examples
    >>> student_residuals = calculate_studentized_residuals(data, model_params, 'control', 'test')
    >>> print(f"Max absolute studentized residual: {np.max(np.abs(student_residuals)):.3f}")
    """
    # Extract regression arrays
    x, y = extract_regression_arrays(data, control_col, test_col)

    # Prepare design matrix with constant
    X = prepare_regression_arrays(x, add_constant=True)

    # Calculate hat matrix diagonal (leverage values)
    # H = X(X'X)^(-1)X', leverage = diag(H)
    XtX_inv = np.linalg.inv(X.T @ X)
    leverage = np.sum((X @ XtX_inv) * X, axis=1)

    # Calculate raw residuals
    residuals = calculate_residuals(data, model_params, control_col, test_col)

    # Extract residual standard deviation
    sigma = model_params["sigma"]

    # Calculate studentized residuals
    # Avoid division by zero for high-leverage points
    denominator = sigma * np.sqrt(np.maximum(1 - leverage, 1e-10))
    studentized_residuals = residuals / denominator

    return studentized_residuals


def calculate_goodness_of_fit(
    data: pd.DataFrame,
    model_params: Dict[str, float],
    control_col: str,
    test_col: str,
) -> Dict[str, float]:
    """
    Calculate comprehensive goodness-of-fit metrics for TBR regression model.

    Computes R², Adjusted R², F-statistic, and related metrics to assess
    how well the model fits the data.

    Parameters
    ----------
    data : pd.DataFrame
        Data used for regression fitting
    model_params : Dict[str, float]
        Regression parameters from fit_regression_model()
    control_col : str
        Name of the control group metric column
    test_col : str
        Name of the test group metric column

    Returns
    -------
    Dict[str, float]
        Dictionary containing goodness-of-fit metrics:
        - 'r_squared': Coefficient of determination (R²)
        - 'adj_r_squared': Adjusted R²
        - 'f_statistic': F-statistic for overall model significance
        - 'f_p_value': P-value for F-statistic
        - 'mse': Mean squared error
        - 'rmse': Root mean squared error

    Examples
    --------
    >>> gof = calculate_goodness_of_fit(data, model_params, 'control', 'test')
    >>> print(f"Model explains {gof['r_squared']*100:.1f}% of variance")
    >>> if gof['f_p_value'] < 0.05:
    ...     print("Model is statistically significant")
    """
    # Extract regression arrays
    x, y = extract_regression_arrays(data, control_col, test_col)
    n = len(y)

    # Calculate residuals
    residuals = calculate_residuals(data, model_params, control_col, test_col)

    # Calculate sum of squares
    ss_res = np.sum(residuals**2)  # Residual sum of squares
    ss_tot = np.sum((y - np.mean(y)) ** 2)  # Total sum of squares
    ss_reg = ss_tot - ss_res  # Regression sum of squares

    # Calculate R-squared
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    # Calculate adjusted R-squared
    # Adjusted R² = 1 - (1 - R²) * (n - 1) / (n - p - 1)
    # For simple linear regression: p = 1 (one predictor)
    df_res = model_params["degrees_freedom"]  # n - 2
    df_tot = n - 1
    adj_r_squared = 1 - (1 - r_squared) * df_tot / df_res if df_res > 0 else 0.0

    # Calculate F-statistic
    # F = (SS_reg / df_reg) / (SS_res / df_res)
    # For simple linear regression: df_reg = 1
    df_reg = 1
    mse_reg = ss_reg / df_reg if df_reg > 0 else 0.0
    mse_res = ss_res / df_res if df_res > 0 else 0.0

    f_statistic = mse_reg / mse_res if mse_res > 0 else 0.0

    # Calculate F-statistic p-value
    # Lazy import to minimize dependencies
    from scipy import stats

    f_p_value = 1 - stats.f.cdf(f_statistic, df_reg, df_res) if f_statistic > 0 else 1.0

    # Calculate error metrics
    mse = ss_res / n  # Mean squared error
    rmse = np.sqrt(mse)  # Root mean squared error

    return {
        "r_squared": float(r_squared),
        "adj_r_squared": float(adj_r_squared),
        "f_statistic": float(f_statistic),
        "f_p_value": float(f_p_value),
        "mse": float(mse),
        "rmse": float(rmse),
    }


def calculate_information_criteria(
    data: pd.DataFrame,
    model_params: Dict[str, float],
    control_col: str,
    test_col: str,
) -> Dict[str, float]:
    """
    Calculate information criteria (AIC, BIC) for model selection.

    Computes Akaike Information Criterion (AIC) and Bayesian Information
    Criterion (BIC) for comparing different models.

    Parameters
    ----------
    data : pd.DataFrame
        Data used for regression fitting
    model_params : Dict[str, float]
        Regression parameters from fit_regression_model()
    control_col : str
        Name of the control group metric column
    test_col : str
        Name of the test group metric column

    Returns
    -------
    Dict[str, float]
        Dictionary containing information criteria:
        - 'aic': Akaike Information Criterion
        - 'bic': Bayesian Information Criterion
        - 'log_likelihood': Log-likelihood of the model

    Examples
    --------
    >>> ic = calculate_information_criteria(data, model_params, 'control', 'test')
    >>> print(f"AIC: {ic['aic']:.2f}, BIC: {ic['bic']:.2f}")
    """
    # Extract regression arrays
    x, y = extract_regression_arrays(data, control_col, test_col)
    n = len(y)

    # Calculate residuals and sum of squared errors
    residuals = calculate_residuals(data, model_params, control_col, test_col)
    sse = np.sum(residuals**2)

    # Extract residual standard deviation
    sigma = model_params["sigma"]

    # Calculate log-likelihood for normal linear regression
    # L = -n/2 * ln(2π) - n/2 * ln(σ²) - SSE/(2σ²)
    log_likelihood = (
        -n / 2 * np.log(2 * np.pi) - n / 2 * np.log(sigma**2) - sse / (2 * sigma**2)
    )

    # Number of parameters: intercept + slope + variance = 3
    k = 3

    # Calculate AIC: AIC = 2k - 2*ln(L)
    aic = 2 * k - 2 * log_likelihood

    # Calculate BIC: BIC = k*ln(n) - 2*ln(L)
    bic = k * np.log(n) - 2 * log_likelihood

    return {
        "aic": float(aic),
        "bic": float(bic),
        "log_likelihood": float(log_likelihood),
    }


def check_normality(residuals: np.ndarray) -> NormalityTestResult:
    """
    Test normality of residuals using Shapiro-Wilk test.

    Performs the Shapiro-Wilk test for normality, which is appropriate
    for small to medium sample sizes (n ≤ 5000).

    Parameters
    ----------
    residuals : np.ndarray
        Array of residuals to test for normality

    Returns
    -------
    Dict[str, Union[float, bool]]
        Dictionary containing test results:
        - 'statistic': Shapiro-Wilk test statistic
        - 'p_value': P-value of the test
        - 'is_normal': Boolean indicating normality at α = 0.05
        - 'test_name': Name of the statistical test used

    Examples
    --------
    >>> residuals = np.random.normal(0, 1, 50)  # Normal residuals
    >>> result = test_normality(residuals)
    >>> print(f"Normality test p-value: {result['p_value']:.4f}")
    >>> print(f"Residuals are normal: {result['is_normal']}")
    """
    validate_array_not_empty(residuals, "residuals")

    # Perform Shapiro-Wilk test
    # Lazy import to minimize dependencies
    from scipy import stats

    statistic, p_value = stats.shapiro(residuals)

    # Determine normality at α = 0.05
    is_normal = p_value > 0.05

    return {
        "statistic": float(statistic),
        "p_value": float(p_value),
        "is_normal": bool(is_normal),
        "test_name": "Shapiro-Wilk",
    }


def check_homoscedasticity(
    data: pd.DataFrame,
    model_params: Dict[str, float],
    control_col: str,
    test_col: str,
) -> HomoscedasticityTestResult:
    """
    Test homoscedasticity using Breusch-Pagan test.

    Tests the null hypothesis that residual variance is constant
    (homoscedastic) against the alternative of heteroscedasticity.

    Parameters
    ----------
    data : pd.DataFrame
        Data used for regression fitting
    model_params : Dict[str, float]
        Regression parameters from fit_regression_model()
    control_col : str
        Name of the control group metric column
    test_col : str
        Name of the test group metric column

    Returns
    -------
    Dict[str, Union[float, bool]]
        Dictionary containing test results:
        - 'statistic': Breusch-Pagan test statistic
        - 'p_value': P-value of the test
        - 'is_homoscedastic': Boolean indicating homoscedasticity at α = 0.05
        - 'test_name': Name of the statistical test used

    Examples
    --------
    >>> result = test_homoscedasticity(data, model_params, 'control', 'test')
    >>> print(f"Homoscedasticity p-value: {result['p_value']:.4f}")
    >>> if not result['is_homoscedastic']:
    ...     print("Warning: Heteroscedasticity detected")
    """
    # Extract regression arrays
    x, y = extract_regression_arrays(data, control_col, test_col)
    n = len(x)

    # Calculate residuals
    residuals = calculate_residuals(data, model_params, control_col, test_col)

    # Calculate squared residuals
    residuals_squared = residuals**2

    # Fit auxiliary regression: e² = γ₀ + γ₁x + u
    X = prepare_regression_arrays(x, add_constant=True)
    # Lazy import to minimize dependencies
    import statsmodels.api as sm

    aux_model = sm.OLS(residuals_squared, X).fit()

    # Calculate Breusch-Pagan statistic
    # BP = n * R² from auxiliary regression
    r_squared_aux = aux_model.rsquared
    bp_statistic = n * r_squared_aux

    # Calculate p-value (chi-squared distribution with 1 df)
    # Lazy import to minimize dependencies (reuse from earlier in function)
    from scipy import stats

    p_value = 1 - stats.chi2.cdf(bp_statistic, df=1)

    # Determine homoscedasticity at α = 0.05
    is_homoscedastic = p_value > 0.05

    return {
        "statistic": float(bp_statistic),
        "p_value": float(p_value),
        "is_homoscedastic": bool(is_homoscedastic),
        "test_name": "Breusch-Pagan",
    }


def check_independence(residuals: np.ndarray) -> IndependenceTestResult:
    """
    Test independence of residuals using Durbin-Watson test.

    Tests for first-order autocorrelation in residuals. The Durbin-Watson
    statistic ranges from 0 to 4, with 2 indicating no autocorrelation.

    Parameters
    ----------
    residuals : np.ndarray
        Array of residuals in time order

    Returns
    -------
    Dict[str, Union[float, bool]]
        Dictionary containing test results:
        - 'statistic': Durbin-Watson test statistic
        - 'interpretation': Interpretation of the statistic
        - 'is_independent': Boolean indicating independence (rough guideline)
        - 'test_name': Name of the statistical test used

    Examples
    --------
    >>> # Residuals should be in time order for this test
    >>> result = test_independence(residuals)
    >>> print(f"Durbin-Watson statistic: {result['statistic']:.3f}")
    >>> print(f"Interpretation: {result['interpretation']}")
    """
    validate_array_not_empty(residuals, "residuals")
    validate_sample_size(len(residuals), min_size=3, param_name="residuals")

    # Calculate Durbin-Watson statistic
    # DW = Σ(e_t - e_{t-1})² / Σ(e_t)²
    diff_residuals = np.diff(residuals)
    dw_statistic = np.sum(diff_residuals**2) / np.sum(residuals**2)

    # Interpret the statistic (rough guidelines)
    if dw_statistic < 1.5:
        interpretation = "Positive autocorrelation likely"
        is_independent = False
    elif dw_statistic > 2.5:
        interpretation = "Negative autocorrelation likely"
        is_independent = False
    else:
        interpretation = "No strong evidence of autocorrelation"
        is_independent = True

    return {
        "statistic": float(dw_statistic),
        "interpretation": interpretation,
        "is_independent": bool(is_independent),
        "test_name": "Durbin-Watson",
    }


def create_diagnostic_summary(
    data: pd.DataFrame,
    model_params: Dict[str, float],
    control_col: str,
    test_col: str,
) -> DiagnosticSummary:
    """
    Create comprehensive diagnostic summary for TBR regression model.

    Combines all diagnostic tests and metrics into a single comprehensive
    report for model validation and assumption checking.

    Parameters
    ----------
    data : pd.DataFrame
        Data used for regression fitting
    model_params : Dict[str, float]
        Regression parameters from fit_regression_model()
    control_col : str
        Name of the control group metric column
    test_col : str
        Name of the test group metric column

    Returns
    -------
    Dict[str, Union[Dict, bool, str]]
        Comprehensive diagnostic summary containing:
        - 'goodness_of_fit': Goodness-of-fit metrics
        - 'information_criteria': AIC, BIC values
        - 'normality_test': Normality test results
        - 'homoscedasticity_test': Homoscedasticity test results
        - 'independence_test': Independence test results
        - 'overall_validity': Boolean indicating overall model validity
        - 'warnings': List of assumption violations

    Examples
    --------
    >>> summary = create_diagnostic_summary(data, model_params, 'control', 'test')
    >>> print(f"Model R²: {summary['goodness_of_fit']['r_squared']:.3f}")
    >>> print(f"Overall valid: {summary['overall_validity']}")
    >>> if summary['warnings']:
    ...     print("Warnings:", summary['warnings'])
    """
    # Calculate all diagnostic metrics
    goodness_of_fit = calculate_goodness_of_fit(
        data, model_params, control_col, test_col
    )
    information_criteria = calculate_information_criteria(
        data, model_params, control_col, test_col
    )

    # Calculate residuals for assumption tests
    residuals = calculate_residuals(data, model_params, control_col, test_col)

    # Perform assumption tests
    normality_test = check_normality(residuals)
    homoscedasticity_test = check_homoscedasticity(
        data, model_params, control_col, test_col
    )
    independence_test = check_independence(residuals)

    # Assess overall model validity
    warnings = []

    if not normality_test["is_normal"]:
        warnings.append("Normality assumption violated (Shapiro-Wilk p < 0.05)")

    if not homoscedasticity_test["is_homoscedastic"]:
        warnings.append("Homoscedasticity assumption violated (Breusch-Pagan p < 0.05)")

    if not independence_test["is_independent"]:
        warnings.append(
            f"Independence assumption questionable ({independence_test['interpretation']})"
        )

    # Overall validity: no major assumption violations
    overall_validity = len(warnings) == 0

    return {
        "goodness_of_fit": goodness_of_fit,
        "information_criteria": information_criteria,
        "normality_test": normality_test,
        "homoscedasticity_test": homoscedasticity_test,
        "independence_test": independence_test,
        "overall_validity": overall_validity,
        "warnings": warnings,
    }


def validate_model_assumptions(
    data: pd.DataFrame,
    model_params: Dict[str, float],
    control_col: str,
    test_col: str,
    alpha: float = 0.05,
) -> Dict[str, Union[bool, str, float]]:
    """
    Validate all regression assumptions with customizable significance level.

    Performs comprehensive assumption testing and returns a structured
    validation report with pass/fail status for each assumption.

    Parameters
    ----------
    data : pd.DataFrame
        Data used for regression fitting
    model_params : Dict[str, float]
        Regression parameters from fit_regression_model()
    control_col : str
        Name of the control group metric column
    test_col : str
        Name of the test group metric column
    alpha : float, default 0.05
        Significance level for hypothesis tests

    Returns
    -------
    Dict[str, Union[bool, str, float]]
        Validation results containing:
        - 'linearity_valid': Boolean for linearity assumption
        - 'normality_valid': Boolean for normality assumption
        - 'homoscedasticity_valid': Boolean for homoscedasticity assumption
        - 'independence_valid': Boolean for independence assumption
        - 'all_assumptions_valid': Boolean for overall validity
        - 'significance_level': Alpha level used for tests
        - 'validation_summary': Text summary of results

    Examples
    --------
    >>> validation = validate_model_assumptions(data, model_params, 'control', 'test')
    >>> if validation['all_assumptions_valid']:
    ...     print("All regression assumptions satisfied")
    >>> else:
    ...     print("Some assumptions violated:", validation['validation_summary'])
    """
    # Calculate residuals
    residuals = calculate_residuals(data, model_params, control_col, test_col)

    # Test assumptions
    normality_result = check_normality(residuals)
    homoscedasticity_result = check_homoscedasticity(
        data, model_params, control_col, test_col
    )
    independence_result = check_independence(residuals)

    # Validate each assumption
    normality_valid = normality_result["p_value"] > alpha
    homoscedasticity_valid = homoscedasticity_result["p_value"] > alpha
    independence_valid = independence_result["is_independent"]

    # For linearity, we assume it's valid if the model fits reasonably well
    # (This is a simplification - more sophisticated tests could be added)
    gof = calculate_goodness_of_fit(data, model_params, control_col, test_col)
    linearity_valid = gof["f_p_value"] < alpha and gof["r_squared"] > 0.1

    # Overall validity
    all_assumptions_valid = all(
        [
            linearity_valid,
            normality_valid,
            homoscedasticity_valid,
            independence_valid,
        ]
    )

    # Create validation summary
    failed_assumptions = []
    if not linearity_valid:
        failed_assumptions.append("linearity")
    if not normality_valid:
        failed_assumptions.append("normality")
    if not homoscedasticity_valid:
        failed_assumptions.append("homoscedasticity")
    if not independence_valid:
        failed_assumptions.append("independence")

    if failed_assumptions:
        validation_summary = f"Failed assumptions: {', '.join(failed_assumptions)}"
    else:
        validation_summary = "All regression assumptions satisfied"

    return {
        "linearity_valid": linearity_valid,
        "normality_valid": normality_valid,
        "homoscedasticity_valid": homoscedasticity_valid,
        "independence_valid": independence_valid,
        "all_assumptions_valid": all_assumptions_valid,
        "significance_level": alpha,
        "validation_summary": validation_summary,
    }
