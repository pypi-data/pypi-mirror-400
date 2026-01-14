"""
Date/Time Handling Utilities for TBR Analysis.

This module provides essential date/time handling functions for time series
analysis. These utilities are designed to work with the existing validation
infrastructure and support all time column types (datetime64[ns], int64, float64).

The functions complement the comprehensive validation utilities already available
in the validation module and provide common time series operations needed for
TBR analysis.

Examples
--------
>>> import pandas as pd
>>> import numpy as np
>>> from tbr.utils.datetime_utils import sort_dataframe_by_time
>>>
>>> # Create sample time series data
>>> data = pd.DataFrame({
...     'date': pd.date_range('2023-03-01', periods=5),
...     'control': [100, 110, 105, 120, 115],
...     'test': [102, 112, 107, 122, 117]
... })
>>>
>>> # Sort by time column
>>> sorted_data = sort_dataframe_by_time(data, 'date')
>>> print(sorted_data.head())
"""

from typing import Union

import pandas as pd

from .validation import validate_time_column_type


def sort_dataframe_by_time(
    df: pd.DataFrame,
    time_col: str,
    validate_column: bool = True,
) -> pd.DataFrame:
    """
    Sort DataFrame by time column and reset index.

    This function extracts the sorting pattern from the functional TBR
    implementation (lines 1184-1185) and provides a reusable utility
    for ensuring time series data is properly ordered.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to sort
    time_col : str
        Name of the time column to sort by
    validate_column : bool, default True
        Whether to validate the time column type before sorting

    Returns
    -------
    pd.DataFrame
        DataFrame sorted by time column with reset index

    Raises
    ------
    ValueError
        If time column validation fails (when validate_column=True)

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> # Unsorted time series data
    >>> data = pd.DataFrame({
    ...     'date': pd.to_datetime(['2023-01-03', '2023-01-01', '2023-01-02']),
    ...     'value': [30, 10, 20]
    ... })
    >>> sorted_data = sort_dataframe_by_time(data, 'date')
    >>> print(sorted_data['value'].tolist())  # [10, 20, 30]

    >>> # Integer time column
    >>> hourly_data = pd.DataFrame({
    ...     'hour': [3, 1, 2],
    ...     'metric': [300, 100, 200]
    ... })
    >>> sorted_hourly = sort_dataframe_by_time(hourly_data, 'hour')
    >>> print(sorted_hourly['metric'].tolist())  # [100, 200, 300]

    Notes
    -----
    This function leverages existing validation infrastructure from the
    validation module to ensure the time column is properly formatted
    before sorting. It supports all time column types: datetime64[ns],
    int64, and float64.
    """
    if validate_column:
        validate_time_column_type(df, time_col, "input DataFrame")

    # Apply the sorting pattern from functional implementation
    sorted_df = df.sort_values(time_col).reset_index(drop=True)

    return sorted_df


def process_time_column(
    data: pd.DataFrame,
    time_col: str,
) -> pd.DataFrame:
    """
    Process time column ensuring it's validated and sorted.

    This is a convenience function that combines time column validation
    and sorting into a single operation, providing a clean interface
    for preparing time series data for TBR analysis.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing time series data
    time_col : str
        Name of the time column to process

    Returns
    -------
    pd.DataFrame
        DataFrame with validated and sorted time column

    Raises
    ------
    ValueError
        If time column validation fails

    Examples
    --------
    >>> import pandas as pd
    >>> # Mixed order time series
    >>> data = pd.DataFrame({
    ...     'timestamp': pd.to_datetime(['2023-01-15', '2023-01-10', '2023-01-20']),
    ...     'control': [150, 100, 200],
    ...     'test': [155, 105, 205]
    ... })
    >>> processed = process_time_column(data, 'timestamp')
    >>> print(processed['control'].tolist())  # [100, 150, 200]

    Notes
    -----
    This function is particularly useful as a preprocessing step before
    TBR analysis to ensure data quality and proper ordering.
    """
    # Validate time column (includes comprehensive checks)
    validate_time_column_type(data, time_col, "input data")

    # Sort by time column
    processed_data = sort_dataframe_by_time(data, time_col, validate_column=False)

    return processed_data


def create_time_range_mask(
    time_series: pd.Series,
    start: Union[pd.Timestamp, int, float],
    end: Union[pd.Timestamp, int, float],
    inclusive_end: bool = False,
) -> pd.Series:
    """
    Create boolean mask for filtering time series within a range.

    This function provides a clean interface for creating time range masks,
    which is a common operation in time series analysis and period splitting.

    Parameters
    ----------
    time_series : pd.Series
        Time series to create mask for
    start : Union[pd.Timestamp, int, float]
        Start of time range (inclusive)
    end : Union[pd.Timestamp, int, float]
        End of time range
    inclusive_end : bool, default False
        Whether to include the end boundary in the range

    Returns
    -------
    pd.Series
        Boolean mask where True indicates values within the time range

    Examples
    --------
    >>> import pandas as pd
    >>> # Datetime time series
    >>> dates = pd.date_range('2023-01-01', periods=10)
    >>> mask = create_time_range_mask(
    ...     dates,
    ...     pd.Timestamp('2023-01-03'),
    ...     pd.Timestamp('2023-01-07')
    ... )
    >>> print(dates[mask].tolist()[:2])  # First 2 dates in range

    >>> # Integer time series
    >>> hours = pd.Series(range(1, 25))  # Hours 1-24
    >>> mask = create_time_range_mask(hours, 8, 17, inclusive_end=True)
    >>> print(hours[mask].tolist())  # [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

    Notes
    -----
    This function complements the existing split_time_series_by_periods()
    function by providing a lower-level utility for time range operations.
    """
    if inclusive_end:
        mask = (time_series >= start) & (time_series <= end)
    else:
        mask = (time_series >= start) & (time_series < end)

    return mask


# Export list for clean imports
__all__ = [
    "sort_dataframe_by_time",
    "process_time_column",
    "create_time_range_mask",
]
