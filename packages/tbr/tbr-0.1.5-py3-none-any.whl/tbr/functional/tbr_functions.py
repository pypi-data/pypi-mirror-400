"""
Time-Based Regression (TBR) Analysis for Causal Inference.

This module provides a comprehensive implementation of Time-Based Regression
methodology for measuring causal effects in treatment/control experiments.
TBR enables rigorous statistical analysis of intervention effects in time
series data with proper uncertainty quantification and credible intervals.

The implementation is domain-agnostic and suitable for any field requiring
causal inference from time series experiments: marketing campaigns, medical
trials, product launches, policy interventions, and A/B testing.

Key Features
------------
- Causal inference: Measure treatment effects with statistical rigor
- Domain-agnostic: Works with any time series treatment/control data
- Uncertainty quantification: Proper variance estimation and credible intervals
- Flexible time handling: Supports datetime, integer, and float time columns
- Complete methodology: Full mathematical implementation of TBR formulas

Examples
--------
>>> import pandas as pd
>>> import numpy as np
>>> from tbr.functional.tbr_functions import perform_tbr_analysis
>>>
>>> # Create time series data (control vs test groups)
>>> data = pd.DataFrame({
...     'date': pd.date_range('2023-01-01', periods=90),
...     'control': np.random.normal(1000, 50, 90),  # Control group metric
...     'test': np.random.normal(1020, 55, 90)      # Test group metric
... })
>>>
>>> # Analyze treatment effect
>>> results, summaries = perform_tbr_analysis(
...     data=data,
...     time_col='date',
...     control_col='control',
...     test_col='test',
...     pretest_start=pd.Timestamp('2023-01-01'),
...     test_start=pd.Timestamp('2023-02-15'),
...     test_end=pd.Timestamp('2023-03-01'),
...     level=0.80,
...     threshold=0.0
... )
>>>
>>> # Get treatment effect and credible interval
>>> final_summary = summaries.iloc[-1]
>>> print(f"Effect: {final_summary['estimate']:.2f}")
>>> print(f"80% CI: [{final_summary['lower']:.2f}, {final_summary['upper']:.2f}]")

Notes
-----
TBR fits a linear model on pre-treatment data: test = alpha + beta * control + epsilon
Then generates counterfactual predictions for the treatment period to estimate
causal effects with proper statistical uncertainty.

See perform_tbr_analysis() for detailed usage and additional examples.
"""

from typing import Dict, Union

import numpy as np
import pandas as pd

from tbr.core.results import TBRResults
from tbr.utils.preprocessing import split_time_series_by_periods
from tbr.utils.validation import (
    validate_column_distinctness,
    validate_metric_columns,
    validate_no_nulls,
    validate_no_reserved_column_conflicts,
    validate_period_data,
    validate_required_columns,
    validate_time_boundaries_type,
    validate_time_column_type,
    validate_time_periods,
)

# Export list for clean imports
__all__ = [
    "perform_tbr_analysis",
    "safe_int_conversion",
    "fit_tbr_regression_model",
    "calculate_sum_x_squared_deviations",
    "extract_sum_x_squared_deviations",
    "calculate_model_variance",
    "calculate_prediction_variance",
    "generate_counterfactual_predictions",
    "calculate_cumulative_standard_deviation",
    "compute_interval_estimate_and_ci",
    "create_tbr_summary",
    "create_incremental_tbr_summaries",
]


def calculate_sum_x_squared_deviations(x: np.ndarray) -> float:
    """
    Calculate sum of squared deviations from the mean.

    This function provides a wrapper around the core mathematical implementation
    for calculating sum of squared deviations, maintaining backward compatibility
    while following clean architecture principles.

    Parameters
    ----------
    x : np.ndarray
        Input array of values

    Returns
    -------
    float
        Sum of squared deviations from the mean

    Examples
    --------
    >>> import numpy as np
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> calculate_sum_x_squared_deviations(x)
    10.0
    """
    from tbr.core.regression import calculate_sum_squared_deviations

    return calculate_sum_squared_deviations(x)


def extract_sum_x_squared_deviations(var_beta: float, sigma: float) -> float:
    """
    Extract sum of squared deviations from regression variance parameters.

    This function provides a wrapper around the core mathematical implementation
    for extracting sum of squared deviations from model parameters, maintaining
    backward compatibility while following clean architecture principles.

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
    """
    from tbr.core.regression import extract_sum_squared_deviations_from_model

    return extract_sum_squared_deviations_from_model(var_beta, sigma)


def safe_int_conversion(value: float, param_name: str) -> int:
    """
    Safely convert float to int with validation for statistical parameters.

    This function provides a wrapper around the core mathematical implementation
    for safe integer conversion, maintaining backward compatibility while
    following clean architecture principles.

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
    >>> safe_int_conversion(43.0, "degrees_freedom")
    43
    >>> safe_int_conversion(43.999999999999, "degrees_freedom")
    44
    >>> safe_int_conversion(43.5, "degrees_freedom")  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ValueError: degrees_freedom should be an integer, got 43.5...
    """
    from tbr.core.regression import convert_to_integer

    return convert_to_integer(value, param_name)


def fit_tbr_regression_model(
    learning_data: pd.DataFrame,
    control_col: str,
    test_col: str,
) -> Dict[str, float]:
    """
    Fit TBR regression model using OLS on pretest period.

    This function provides a wrapper around the core regression implementation,
    maintaining backward compatibility while following clean architecture principles.
    The model is trained exclusively on the pretest period to avoid contamination
    from treatment effects.

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
    >>> model = fit_tbr_regression_model(learning_data, 'control', 'test')
    >>> print(f"Beta coefficient: {model['beta']:.3f}")
    """
    from tbr.core.regression import fit_regression_model

    return fit_regression_model(learning_data, control_col, test_col)


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
    >>> sum_sq_dev = calculate_sum_x_squared_deviations(x_vals)
    >>> variances = calculate_model_variance(
    ...     x_vals, pretest_x_mean=110, sigma=10, n_pretest=30,
    ...     pretest_sum_x_squared_deviations=sum_sq_dev
    ... )
    >>> print(f"Model variances: {variances}")
    """
    from tbr.core.regression import (
        calculate_model_variance as _calculate_model_variance,
    )

    return _calculate_model_variance(
        x_values=x_values,
        pretest_x_mean=pretest_x_mean,
        sigma=sigma,
        n_pretest=n_pretest,
        pretest_sum_x_squared_deviations=pretest_sum_x_squared_deviations,
    )


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
    >>> model_vars = calculate_model_variance(
    ...     np.array([100, 110, 120]), x_mean=105, sigma=10,
    ...     n_pretest=30, var_beta=0.001
    ... )
    >>> # Then add residual variance
    >>> pred_vars = calculate_prediction_variance(model_vars, sigma=10)
    >>> print(f"Prediction variances: {pred_vars}")
    """
    from tbr.core.regression import (
        calculate_prediction_variance as _calculate_prediction_variance,
    )

    return _calculate_prediction_variance(
        model_variances=model_variances,
        sigma=sigma,
    )


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

    This function provides a wrapper around the core prediction implementation,
    maintaining backward compatibility while following clean architecture principles.
    Creates counterfactual predictions using the fitted regression model and calculates
    their prediction standard deviations.

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
        Must be calculated from the same pretest data used to fit the regression model.
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
    >>> # Calculate sum_x_squared_deviations from pretest data
    >>> pretest_control = np.random.normal(1000, 50, 45)
    >>> sum_sq_dev = calculate_sum_x_squared_deviations(pretest_control)
    >>> predictions = generate_counterfactual_predictions(
    ...     alpha=50, beta=0.95, sigma=25, pretest_x_mean=1000, n_pretest=45,
    ...     pretest_sum_x_squared_deviations=sum_sq_dev,
    ...     test_period_data=test_data, control_col='control', time_col='date'
    ... )
    >>> print(f"Predictions shape: {predictions.shape}")
    """
    from tbr.core.prediction import (
        generate_counterfactual_predictions as _generate_counterfactual_predictions,
    )

    return _generate_counterfactual_predictions(
        alpha=alpha,
        beta=beta,
        sigma=sigma,
        pretest_x_mean=pretest_x_mean,
        n_pretest=n_pretest,
        pretest_sum_x_squared_deviations=pretest_sum_x_squared_deviations,
        test_period_data=test_period_data,
        control_col=control_col,
        time_col=time_col,
    )


def calculate_cumulative_standard_deviation(
    test_x_values: np.ndarray,
    sigma: float,
    var_alpha: float,
    var_beta: float,
    cov_alpha_beta: float,
) -> np.ndarray:
    """
    Calculate standard deviation of cumulative causal effect for TBR test period.

    Implements the TBR formula for cumulative effect variance:
    V[Δr(T)] = T · σ² + T² · v
    where v = Var(α̂) + 2·x̄_T·Cov(α̂,β̂) + x̄_T²·Var(β̂)

    This calculates the uncertainty in cumulative treatment effects as they
    accumulate over time during the test period.

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
    >>> x_vals = np.array([1000, 1020, 1010, 1030])
    >>> cumsd = calculate_cumulative_standard_deviation(
    ...     x_vals, sigma=25, var_alpha=100, var_beta=0.001,
    ...     cov_alpha_beta=-0.05
    ... )
    >>> print(f"Cumulative std devs: {cumsd}")
    """
    from tbr.core.prediction import (
        calculate_cumulative_standard_deviation as _calculate_cumulative_standard_deviation,
    )

    return _calculate_cumulative_standard_deviation(
        test_x_values=test_x_values,
        sigma=sigma,
        var_alpha=var_alpha,
        var_beta=var_beta,
        cov_alpha_beta=cov_alpha_beta,
    )


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
    """
    from tbr.core.prediction import (
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

    Raises
    ------
    ValueError
        If input validation fails or required data is missing

    Examples
    --------
    >>> summary = create_tbr_summary(
    ...     tbr_results, alpha=50, beta=0.95, sigma=25,
    ...     var_alpha=100, var_beta=0.001, cov_alpha_beta=-0.05,
    ...     degrees_freedom=43, level=0.80, threshold=0.0,
    ...     model_name='experiment_analysis'
    ... )
    >>> print(f"Effect estimate: {summary['estimate'].iloc[0]:.2f}")
    """
    from tbr.core.effects import create_tbr_summary as _create_tbr_summary

    return _create_tbr_summary(
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

    Raises
    ------
    ValueError
        If input validation fails or no test period data is found

    Examples
    --------
    >>> incremental_summaries = create_incremental_tbr_summaries(
    ...     tbr_results, alpha=50, beta=0.95, sigma=25,
    ...     var_alpha=100, var_beta=0.001, cov_alpha_beta=-0.05,
    ...     degrees_freedom=43, level=0.80, threshold=0.0
    ... )
    >>> print(f"Day 1 effect: {incremental_summaries.iloc[0]['estimate']:.2f}")
    """
    from tbr.core.effects import (
        create_incremental_tbr_summaries as _create_incremental_tbr_summaries,
    )

    return _create_incremental_tbr_summaries(
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


def perform_tbr_analysis(
    data: pd.DataFrame,
    time_col: str,
    control_col: str,
    test_col: str,
    pretest_start: Union[pd.Timestamp, int, float],
    test_start: Union[pd.Timestamp, int, float],
    test_end: Union[pd.Timestamp, int, float],
    level: float,
    threshold: float,
    test_end_inclusive: bool = False,
) -> TBRResults:
    """
    Execute complete TBR analysis pipeline for domain-agnostic time series data.

    This is the main function that orchestrates the entire TBR analysis process
    for any treatment/control time series experiment. The input should be
    pre-aggregated time series data with control and test group metrics.

    Parameters
    ----------
    data : pd.DataFrame
        Time series data with time, control, and test columns.
        Should contain pre-aggregated metrics for control and test groups.
        Time column must be one of the supported types (see time_col parameter).
    time_col : str
        Name of the time column. Supported pandas native dtypes only:
        - datetime64[ns]: Pandas native datetime (use pd.to_datetime())
        - datetime64[ns, timezone]: Timezone-aware variants (any timezone)
        - int64: Epochs, hours, days since start, etc.
        - float64: Fractional time units, decimal hours, etc.

        Note: Object dtypes are not supported (including Python date/datetime objects).
        Convert all date/time data using pd.to_datetime() first.
    control_col : str
        Name of control column
    test_col : str
        Name of test column
    pretest_start : Union[pd.Timestamp, int, float]
        Start time of pretest period (always inclusive)
    test_start : Union[pd.Timestamp, int, float]
        Start time of test period (always inclusive)
    test_end : Union[pd.Timestamp, int, float]
        End time of test period
    test_end_inclusive : bool, default False
        Whether to include the test_end boundary in the test period.

        - False (default): Exclusive end boundary (data < test_end)
        - True: Inclusive end boundary (data <= test_end)

        Examples for test_end_inclusive:
        - For same-day analysis: set test_end_inclusive=True
        - For precise time ranges: set test_end_inclusive=False

        Note: This parameter works consistently across all time column types
        (datetime64[ns], int64, float64).
    level : float
        Credibility level for credible intervals (e.g., 0.80 for 80% credible interval)
    threshold : float
        Threshold for probability calculation (typically 0.0 for positive effect testing)
    test_end_inclusive : bool, default False
        Whether to include test_end date in the analysis period

    Returns
    -------
    TBRResults
        Comprehensive result object with all analysis outputs accessible via
        properties and methods, with complete separation of inputs and outputs.

        Key properties:
        - estimate: Final cumulative effect
        - conf_int_lower, conf_int_upper: Credible interval bounds
        - pvalue: Posterior probability
        - cumulative_effect, effects: Time-indexed Series
        - summary(): Daily incremental summary statistics
        - tbr_dataframe(): Get comprehensive TBR dataframe

    Raises
    ------
    ValueError
        If input validation fails, column names conflict with reserved names,
        or insufficient data for analysis

    Examples
    --------
    Basic usage with marketing campaign data:

    >>> import pandas as pd
    >>> import numpy as np
    >>>
    >>> # Create sample time series data with datetime64[ns] (pandas native)
    >>> dates = pd.date_range('2023-01-01', periods=90)
    >>> data = pd.DataFrame({
    ...     'date': dates,
    ...     'control': np.random.normal(1000, 50, 90),
    ...     'test': np.random.normal(1020, 55, 90)
    ... })
    >>>
    >>> # Run TBR analysis - returns TBRResults object
    >>> results = perform_tbr_analysis(
    ...     data=data,
    ...     time_col='date',
    ...     control_col='control',
    ...     test_col='test',
    ...     pretest_start=pd.Timestamp('2023-01-01'),
    ...     test_start=pd.Timestamp('2023-02-15'),
    ...     test_end=pd.Timestamp('2023-03-01'),
    ...     test_end_inclusive=False,  # Exclusive: up to but not including 2023-03-01
    ...     level=0.80,
    ...     threshold=0.0
    ... )
    >>>
    >>> # Access results via clean property interface
    >>> print(f"Effect: {results.estimate:.2f}")
    >>> print(f"80% CI: [{results.conf_int_lower:.2f}, {results.conf_int_upper:.2f}]")
    >>> print(f"P-value: {results.pvalue:.3f}")
    >>>
    >>> # Check significance
    >>> is_significant = results.conf_int_lower > 0
    >>> print(f"Significant Positive Effect: {is_significant}")
    >>>
    >>> # Access time series (all indexed by date)
    >>> results.cumulative_effect.plot(title='Cumulative Treatment Effect')
    >>> print(results.effects.describe())
    >>>
    >>> # Get daily summary table
    >>> daily_summary = results.summary()
    >>> print(daily_summary.tail())
    >>>
    >>> # Get comprehensive TBR dataframe
    >>> tbr_df = results.tbr_dataframe()
    >>> tbr_df.to_csv('tbr_results.csv', index=False)

    Integer time example (hours since start):

    >>> # Integer time column example
    >>> hourly_data = pd.DataFrame({
    ...     'hour': range(1, 49),  # Hours 1-48
    ...     'control': np.random.normal(500, 25, 48),
    ...     'test': np.random.normal(520, 30, 48)
    ... })
    >>>
    >>> results = perform_tbr_analysis(
    ...     data=hourly_data,
    ...     time_col='hour',
    ...     control_col='control',
    ...     test_col='test',
    ...     pretest_start=1,
    ...     test_start=25,
    ...     test_end=25,  # Same-hour analysis
    ...     test_end_inclusive=True,  # Include hour 25
    ...     level=0.80,
    ...     threshold=0.0
    ... )
    >>> print(f"Hourly effect: {results.estimate:.2f}")

    Medical trial example:

    >>> # Medical trial data with integer time (days since start)
    >>> medical_data = pd.DataFrame({
    ...     'day': range(1, 121),  # Days 1-120
    ...     'control_recovery_rate': np.random.normal(0.75, 0.05, 120),
    ...     'treatment_recovery_rate': np.random.normal(0.82, 0.06, 120)
    ... })
    >>>
    >>> results = perform_tbr_analysis(
    ...     data=medical_data,
    ...     time_col='day',
    ...     control_col='control_recovery_rate',
    ...     test_col='treatment_recovery_rate',
    ...     pretest_start=1,
    ...     test_start=60,
    ...     test_end=90,
    ...     test_end_inclusive=False,  # Days 60-89 (exclusive end)
    ...     level=0.95,
    ...     threshold=0.05  # 5% improvement threshold
    ... )
    >>> print(f"Treatment improvement: {results.estimate:.3f}")
    """
    # Input validation
    if data.empty:
        raise ValueError("Input data cannot be empty")

    required_cols = [time_col, control_col, test_col]
    validate_required_columns(data, required_cols, "data")

    # NEW: Validate column distinctness (prevent same column used for multiple purposes)
    validate_column_distinctness(time_col, control_col, test_col)

    # NEW: Validate no conflicts with reserved output column names
    validate_no_reserved_column_conflicts(data, time_col, control_col, test_col)

    validate_time_column_type(data, time_col, "data")

    validate_time_boundaries_type(
        pretest_start, test_start, test_end, data[time_col].dtype
    )

    validate_time_periods(pretest_start, test_start, test_end, test_end_inclusive)

    validate_no_nulls(data, required_cols, "data")

    validate_metric_columns(data, control_col, test_col)

    # Step 1: Split data by periods
    (
        baseline_data,
        pretest_data,
        test_data,
        cooldown_data,
    ) = split_time_series_by_periods(
        aggregated_data=data,
        time_col=time_col,
        pretest_start=pretest_start,
        test_start=test_start,
        test_end=test_end,
        test_end_inclusive=test_end_inclusive,
    )

    validate_period_data(pretest_data, test_data)

    # Step 2: Fit the TBR regression model on learning data
    model_params = fit_tbr_regression_model(
        learning_data=pretest_data,
        control_col=control_col,
        test_col=test_col,
    )

    # Step 3: Create and return TBRResults object
    # TBRResults encapsulates all analysis outputs with clean property-based access
    return TBRResults(
        _data=data,
        time_col=time_col,
        control_col=control_col,
        test_col=test_col,
        model_params=model_params,
        periods={
            "baseline": baseline_data,
            "pretest": pretest_data,
            "test": test_data,
            "cooldown": cooldown_data,
        },
        level=level,
        threshold=threshold,
    )
