"""
Data Preprocessing and Cleaning Utilities for TBR Analysis.

This module provides preprocessing functions extracted from the functional TBR
implementation. These utilities handle time series period splitting, data
preparation for regression analysis, and basic statistical calculations.

The functions in this module are designed to be domain-agnostic and work
across marketing, medical, economic, and other time series analysis domains.

Examples
--------
>>> import pandas as pd
>>> import numpy as np
>>> from tbr.utils.preprocessing import split_time_series_by_periods
>>>
>>> # Create sample time series data
>>> data = pd.DataFrame({
...     'date': pd.date_range('2023-01-01', periods=90),
...     'control': np.random.normal(1000, 50, 90),
...     'test': np.random.normal(1020, 55, 90)
... })
>>>
>>> # Split data into periods
>>> baseline, pretest, test, cooldown = split_time_series_by_periods(
...     data, 'date',
...     pd.Timestamp('2023-01-15'),  # pretest_start
...     pd.Timestamp('2023-02-15'),  # test_start
...     pd.Timestamp('2023-03-01')   # test_end
... )
"""

from typing import Dict, Tuple, Union

import numpy as np
import pandas as pd


def split_time_series_by_periods(
    aggregated_data: pd.DataFrame,
    time_col: str,
    pretest_start: Union[pd.Timestamp, int, float],
    test_start: Union[pd.Timestamp, int, float],
    test_end: Union[pd.Timestamp, int, float],
    test_end_inclusive: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split aggregated time series data into baseline, pretest, test and cooldown periods.

    This function is extracted from the functional TBR implementation (lines 198-252)
    and provides period splitting logic for time series analysis.

    Parameters
    ----------
    aggregated_data : pd.DataFrame
        Time series data with columns for time, control, and test metrics
    time_col : str
        Name of the time column
    pretest_start : Union[pd.Timestamp, int, float]
        Start time of pretest period (always inclusive)
    test_start : Union[pd.Timestamp, int, float]
        Start time of test period (always inclusive)
    test_end : Union[pd.Timestamp, int, float]
        End time of test period
    test_end_inclusive : bool, default False
        Whether to include the test_end boundary in the test period

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
        (baseline_data, pretest_data, test_data, cooldown_data) - DataFrames for each period

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> data = pd.DataFrame({
    ...     'date': pd.date_range('2023-01-01', periods=90),
    ...     'control': np.random.normal(1000, 50, 90),
    ...     'test': np.random.normal(1020, 55, 90)
    ... })
    >>> baseline, pretest, test, cooldown = split_time_series_by_periods(
    ...     data, 'date',
    ...     pd.Timestamp('2023-01-15'),
    ...     pd.Timestamp('2023-02-15'),
    ...     pd.Timestamp('2023-03-01')
    ... )
    >>> print(f"Pretest period: {len(pretest)} days")
    """
    data_copy = aggregated_data.copy()

    # Use boundary values directly (validation done at entry point)
    time_series = data_copy[time_col]

    # Create period masks using boundary values directly
    baseline_mask = time_series < pretest_start
    pretest_mask = (time_series >= pretest_start) & (time_series < test_start)

    # Inclusive/exclusive boundary handling
    if test_end_inclusive:
        test_mask = (time_series >= test_start) & (time_series <= test_end)
        cooldown_mask = time_series > test_end
    else:
        test_mask = (time_series >= test_start) & (time_series < test_end)
        cooldown_mask = time_series >= test_end

    baseline_data = data_copy[baseline_mask].copy()
    pretest_data = data_copy[pretest_mask].copy()
    test_data = data_copy[test_mask].copy()
    cooldown_data = data_copy[cooldown_mask].copy()

    return baseline_data, pretest_data, test_data, cooldown_data


def extract_regression_arrays(
    learning_data: pd.DataFrame,
    control_col: str,
    test_col: str,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract arrays from DataFrame for regression analysis.

    This function is extracted from the functional TBR implementation (line 313)
    and provides safe array extraction for regression fitting.

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
    Tuple[np.ndarray, np.ndarray]
        (x, y) arrays where x is control values and y is test values

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> learning_data = pd.DataFrame({
    ...     'control': np.random.normal(1000, 50, 30),
    ...     'test': np.random.normal(1020, 55, 30)
    ... })
    >>> x, y = extract_regression_arrays(learning_data, 'control', 'test')
    >>> print(f"Arrays shape: x={x.shape}, y={y.shape}")
    """
    # Extract x (control) and y (test) for regression
    x = learning_data[control_col].values
    y = learning_data[test_col].values

    return x, y


def assign_period_indicators(
    data: pd.DataFrame, test_col: str, control_col: str, period_value: int
) -> pd.DataFrame:
    """
    Assign period indicators and standardize column names for analysis DataFrame.

    This function is extracted from the functional TBR implementation
    (lines 1221-1226, 1334-1350) and provides period indicator assignment.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame to process
    test_col : str
        Name of test column
    control_col : str
        Name of control column
    period_value : int
        Period indicator value to assign

    Returns
    -------
    pd.DataFrame
        DataFrame with period indicator and standardized columns

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> data = pd.DataFrame({
    ...     'control': np.random.normal(1000, 50, 10),
    ...     'test': np.random.normal(1020, 55, 10)
    ... })
    >>> processed = assign_period_indicators(data, 'test', 'control', 1)
    >>> print(processed.columns.tolist())
    """
    processed_data = data.copy()
    processed_data["period"] = period_value
    processed_data["y"] = processed_data[test_col]
    processed_data["x"] = processed_data[control_col]

    return processed_data


def prepare_regression_arrays(x: np.ndarray, add_constant: bool = True) -> np.ndarray:
    """
    Prepare arrays for regression analysis.

    This function is extracted from the functional TBR implementation (line 329)
    and provides data preparation for regression fitting.

    Parameters
    ----------
    x : np.ndarray
        Input array (predictor variable)
    add_constant : bool, default True
        Whether to add constant term for intercept

    Returns
    -------
    np.ndarray
        Prepared array for regression analysis

    Examples
    --------
    >>> import numpy as np
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> X = prepare_regression_arrays(x, add_constant=True)
    >>> print(f"Original shape: {x.shape}, Prepared shape: {X.shape}")
    """
    if add_constant:
        # Lazy import to minimize dependencies
        import statsmodels.api as sm

        # Add constant for intercept
        X = sm.add_constant(x)
        return X
    else:
        return x


def calculate_basic_statistics(x: np.ndarray) -> Dict[str, float]:
    """
    Calculate basic statistical measures for array data.

    This function is extracted from the functional TBR implementation
    (lines 106, 351) and provides basic statistical calculations.

    Parameters
    ----------
    x : np.ndarray
        Input array

    Returns
    -------
    Dict[str, float]
        Dictionary containing basic statistics:
        - 'mean': Sample mean
        - 'sum_squared_deviations': Sum of squared deviations from mean

    Examples
    --------
    >>> import numpy as np
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> stats = calculate_basic_statistics(x)
    >>> print(f"Mean: {stats['mean']:.2f}")
    >>> print(f"Sum squared deviations: {stats['sum_squared_deviations']:.2f}")
    """
    x_mean = np.mean(x)
    sum_squared_deviations = float(np.sum((x - x_mean) ** 2))

    return {"mean": float(x_mean), "sum_squared_deviations": sum_squared_deviations}


# Export list for clean imports
__all__ = [
    "split_time_series_by_periods",
    "extract_regression_arrays",
    "assign_period_indicators",
    "prepare_regression_arrays",
    "calculate_basic_statistics",
]
