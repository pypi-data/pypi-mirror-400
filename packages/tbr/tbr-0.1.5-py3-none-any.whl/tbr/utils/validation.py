"""Input validation utilities for TBR analysis."""

from typing import Dict, List, Union

import numpy as np
import pandas as pd


def validate_array_not_empty(arr: np.ndarray, param_name: str) -> None:
    """
    Validate that array is not empty.

    Parameters
    ----------
    arr : np.ndarray
        Array to validate
    param_name : str
        Parameter name for error messages

    Raises
    ------
    ValueError
        If array is empty
    """
    if len(arr) == 0:
        raise ValueError(f"{param_name} cannot be empty")


def validate_sample_size(
    n: int, min_size: int, param_name: str = "sample size"
) -> None:
    """
    Validate sample size for statistical operations.

    Parameters
    ----------
    n : int
        Sample size to validate
    min_size : int
        Minimum required sample size
    param_name : str, default "sample size"
        Parameter name for error messages

    Raises
    ------
    ValueError
        If sample size is insufficient
    """
    if n < 0:
        raise ValueError(f"{param_name} cannot be negative, got {n}")
    if n < min_size:
        raise ValueError(
            f"Insufficient {param_name}: {n} observations. Need at least {min_size}."
        )


# =============================================================================
# Core DataFrame Validation Functions
# =============================================================================


def validate_required_columns(
    df: pd.DataFrame, required_cols: List[str], df_name: str
) -> None:
    """
    Validate that DataFrame contains all required columns.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate
    required_cols : List[str]
        List of required column names
    df_name : str
        Name of the DataFrame for error messages

    Raises
    ------
    ValueError
        If any required columns are missing

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    >>> validate_required_columns(df, ['a', 'b'], 'test_data')  # No error
    >>> validate_required_columns(df, ['a', 'c'], 'test_data')  # Raises ValueError
    """
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in {df_name}: {missing_cols}")


def validate_no_nulls(df: pd.DataFrame, cols: List[str], df_name: str) -> None:
    """
    Validate that specified columns contain no null values.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate
    cols : List[str]
        List of column names to check for nulls
    df_name : str
        Name of the DataFrame for error messages

    Raises
    ------
    ValueError
        If null values are found in any specified columns

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    >>> validate_no_nulls(df, ['a', 'b'], 'clean_data')  # No error
    >>> df_with_nulls = pd.DataFrame({'a': [1, np.nan], 'b': [3, 4]})
    >>> validate_no_nulls(df_with_nulls, ['a'], 'dirty_data')  # Raises ValueError
    """
    null_counts = df[cols].isnull().sum()
    if null_counts.any():
        null_cols = null_counts[null_counts > 0].to_dict()
        raise ValueError(f"Null values found in {df_name}: {null_cols}")


def validate_metric_columns(
    data: pd.DataFrame,
    control_col: str,
    test_col: str,
) -> None:
    """
    Validate that metric columns are numeric for TBR analysis.

    Parameters
    ----------
    data : pd.DataFrame
        Dataset containing the metric columns
    control_col : str
        Name of the control group metric column
    test_col : str
        Name of the test group metric column

    Raises
    ------
    ValueError
        If control or test columns are not numeric

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'control': [100, 110, 120],
    ...     'test': [105, 115, 125]
    ... })
    >>> validate_metric_columns(df, 'control', 'test')  # No error
    >>> df_bad = pd.DataFrame({
    ...     'control': ['low', 'medium', 'high'],
    ...     'test': [105, 115, 125]
    ... })
    >>> validate_metric_columns(df_bad, 'control', 'test')  # Raises ValueError
    """
    if not pd.api.types.is_numeric_dtype(data[control_col]):
        raise ValueError(f"Control column '{control_col}' must be numeric")
    if not pd.api.types.is_numeric_dtype(data[test_col]):
        raise ValueError(f"Test column '{test_col}' must be numeric")


# =============================================================================
# Time-Related Validation Functions
# =============================================================================


def validate_time_column_type(
    data: pd.DataFrame, time_col: str, df_name: str = "data"
) -> None:
    """Validate time column contains supported data types for TBR analysis.

    Ensures the time column uses pandas native dtypes only: datetime64[ns],
    int64, or float64. Object dtypes are not supported and must be converted
    using pd.to_datetime() before analysis.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing the time column to validate
    time_col : str
        Name of the time column to validate
    df_name : str, default "data"
        Name of the DataFrame for error messages

    Raises
    ------
    ValueError
        If time column is missing, empty, or has unsupported dtype

    Examples
    --------
    >>> import pandas as pd
    >>> # Valid datetime column
    >>> df = pd.DataFrame({
    ...     'date': pd.date_range('2023-01-01', periods=5),
    ...     'values': range(5)
    ... })
    >>> validate_time_column_type(df, 'date')

    >>> # Valid integer time column
    >>> df_int = pd.DataFrame({'hour': range(24), 'values': range(24)})
    >>> validate_time_column_type(df_int, 'hour')

    Notes
    -----
    Supported dtypes: datetime64[ns] (timezone-aware or naive), int64, float64.
    Object dtypes must be converted: df['date'] = pd.to_datetime(df['date'])
    """
    if time_col not in data.columns:
        raise ValueError(f"Time column '{time_col}' not found in {df_name}")

    time_series = data[time_col]

    # Check for empty column
    if time_series.empty:
        raise ValueError(f"Time column '{time_col}' in {df_name} is empty")

    # Check for all null values
    if time_series.isnull().all():
        raise ValueError(
            f"Time column '{time_col}' in {df_name} contains only null values"
        )

    # Get the actual data type
    dtype = time_series.dtype
    dtype_str = str(dtype)

    # Check supported dtypes: datetime64 variants, int64, float64
    if (
        dtype_str.startswith("datetime64")
        or dtype.name == "int64"
        or dtype.name == "float64"
    ):
        return

    # Raise error for unsupported dtypes
    raise ValueError(
        f"Unsupported dtype '{dtype}' for time column '{time_col}'. "
        f"Supported dtypes: datetime64[ns], int64, float64. "
        f"Use pd.to_datetime() for datetime columns or .astype() for numeric columns."
    )


def validate_time_boundaries_type(
    pretest_start: Union[pd.Timestamp, int, float],
    test_start: Union[pd.Timestamp, int, float],
    test_end: Union[pd.Timestamp, int, float],
    time_column_dtype: np.dtype,
) -> None:
    """
    Validate that time boundary types are consistent and match time column dtype.

    Ensures all time boundaries use the same type and are compatible with the
    time column's data type. This prevents type mismatches that could cause
    incorrect period splitting in TBR analysis.

    Parameters
    ----------
    pretest_start : Union[pd.Timestamp, int, float]
        Start time of pretest period
    test_start : Union[pd.Timestamp, int, float]
        Start time of test period
    test_end : Union[pd.Timestamp, int, float]
        End time of test period
    time_column_dtype : np.dtype
        The dtype of the time column from the DataFrame

    Raises
    ------
    ValueError
        If boundary types are inconsistent or don't match time column dtype.
        Specific cases:
        - Mixed boundary types (e.g., mixing pd.Timestamp and int)
        - Type mismatch with column (e.g., int boundaries with datetime64 column)
        - Unsupported dtype combinations

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> # Valid: datetime boundaries with datetime column
    >>> validate_time_boundaries_type(
    ...     pd.Timestamp('2023-01-01'),
    ...     pd.Timestamp('2023-02-01'),
    ...     pd.Timestamp('2023-02-15'),
    ...     np.dtype('datetime64[ns]')
    ... )

    >>> # Valid: integer boundaries with int64 column
    >>> validate_time_boundaries_type(1, 10, 20, np.dtype('int64'))

    Notes
    -----
    Supported type combinations:
    - pd.Timestamp boundaries with datetime64[ns] columns
    - int boundaries with int64 columns
    - float boundaries with float64 columns
    """
    # Check that all boundaries have the same type
    pretest_type = type(pretest_start)
    test_start_type = type(test_start)
    test_end_type = type(test_end)

    if not (pretest_type == test_start_type == test_end_type):
        raise ValueError(
            f"All time boundaries must have the same type. Got: "
            f"pretest_start: {pretest_type.__name__}, "
            f"test_start: {test_start_type.__name__}, "
            f"test_end: {test_end_type.__name__}"
        )

    # Check that boundary type matches time column dtype
    boundary_type = pretest_type
    dtype_str = str(time_column_dtype)

    if dtype_str.startswith("datetime64"):
        if boundary_type != pd.Timestamp:
            raise ValueError(
                f"Time column has dtype '{time_column_dtype}' but boundaries are {boundary_type.__name__}. "
                f"Use pd.Timestamp for datetime columns."
            )
    elif time_column_dtype.name == "int64":
        if boundary_type not in (int, np.int64):
            raise ValueError(
                f"Time column has dtype '{time_column_dtype}' but boundaries are {boundary_type.__name__}. "
                f"Use int for integer time columns."
            )
    elif time_column_dtype.name == "float64":
        if boundary_type not in (float, np.float64):
            raise ValueError(
                f"Time column has dtype '{time_column_dtype}' but boundaries are {boundary_type.__name__}. "
                f"Use float for float time columns."
            )
    else:
        raise ValueError(
            f"Boundary type {boundary_type.__name__} does not match time column dtype '{time_column_dtype}'. "
            f"Supported combinations: pd.Timestamp for datetime64, int for int64, float for float64."
        )


def validate_time_periods(
    pretest_start: Union[pd.Timestamp, int, float],
    test_start: Union[pd.Timestamp, int, float],
    test_end: Union[pd.Timestamp, int, float],
    test_end_inclusive: bool = False,
) -> None:
    """
    Validate time period parameters for TBR analysis.

    Parameters
    ----------
    pretest_start : Union[pd.Timestamp, int, float]
        Start time of pretest period
    test_start : Union[pd.Timestamp, int, float]
        Start time of test period
    test_end : Union[pd.Timestamp, int, float]
        End time of test period
    test_end_inclusive : bool, default False
        Whether to include the test_end boundary in the test period

    Raises
    ------
    ValueError
        If time periods are logically inconsistent

    Examples
    --------
    >>> import pandas as pd
    >>> # Valid time periods
    >>> validate_time_periods(
    ...     pd.Timestamp('2023-01-01'),
    ...     pd.Timestamp('2023-02-01'),
    ...     pd.Timestamp('2023-02-15')
    ... )

    >>> # Valid with inclusive end
    >>> validate_time_periods(
    ...     pd.Timestamp('2023-01-01'),
    ...     pd.Timestamp('2023-02-15'),
    ...     pd.Timestamp('2023-02-15'),
    ...     test_end_inclusive=True
    ... )
    """
    # Boundary validation
    if not (pretest_start < test_start):
        raise ValueError(
            f"pretest_start must be before test_start: {pretest_start} >= {test_start}"
        )

    # Validate test period boundaries based on inclusive/exclusive setting
    if test_end_inclusive:
        if not (test_start <= test_end):
            raise ValueError(
                f"test_start must be <= test_end when test_end_inclusive=True: {test_start} > {test_end}"
            )
    else:
        if not (test_start < test_end):
            raise ValueError(
                f"test_start must be < test_end when test_end_inclusive=False: {test_start} >= {test_end}"
            )


# =============================================================================
# Data Quality Validation Functions
# =============================================================================


def validate_period_data(
    pretest_data: pd.DataFrame,
    test_data: pd.DataFrame,
) -> None:
    """
    Validate that period data contains observations after splitting.

    Parameters
    ----------
    pretest_data : pd.DataFrame
        Pretest period data
    test_data : pd.DataFrame
        Test period data

    Raises
    ------
    ValueError
        If pretest or test data is empty

    Examples
    --------
    >>> import pandas as pd
    >>> pretest = pd.DataFrame({'date': [1, 2], 'control': [100, 110]})
    >>> test = pd.DataFrame({'date': [3, 4], 'control': [120, 130]})
    >>> validate_period_data(pretest, test)  # No error

    >>> empty_df = pd.DataFrame()
    >>> validate_period_data(empty_df, test)  # Raises ValueError
    """
    if pretest_data.empty:
        raise ValueError("No pretest data found - check pretest period dates")

    if test_data.empty:
        raise ValueError("No test data found - check test period dates")


def validate_learning_set(
    learning_df: pd.DataFrame,
    control_col: str,
    test_col: str,
) -> None:
    """
    Validate learning set for TBR regression model training.

    Parameters
    ----------
    learning_df : pd.DataFrame
        Learning data used for training the regression model
    control_col : str
        Name of the control group metric column
    test_col : str
        Name of the test group metric column

    Raises
    ------
    ValueError
        If learning data is insufficient, contains nulls, or has invalid values

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> # Valid learning data
    >>> df = pd.DataFrame({
    ...     'control': [100, 110, 120, 130],
    ...     'test': [105, 115, 125, 135]
    ... })
    >>> validate_learning_set(df, 'control', 'test')  # No error

    >>> # Insufficient data
    >>> small_df = pd.DataFrame({'control': [100], 'test': [105]})
    >>> validate_learning_set(small_df, 'control', 'test')  # Raises ValueError
    """
    # Check minimum data requirements for regression
    if len(learning_df) < 3:
        raise ValueError(
            f"Insufficient learning data: {len(learning_df)} observations. Need at least 3."
        )

    # Check for missing values
    if learning_df[[control_col, test_col]].isnull().any().any():
        raise ValueError("Learning data contains null values")

    # Check for invalid values (infinite or NaN)
    if not np.isfinite(learning_df[[control_col, test_col]]).all().all():
        raise ValueError("Learning data contains infinite or NaN values")


# =============================================================================
# Statistical Parameter Validation Functions
# =============================================================================


def validate_probability_level(
    level: float, param_name: str = "probability level"
) -> None:
    """
    Validate probability level parameter for statistical inference.

    Generic validator for probability levels used in interval estimation.
    In TBR context, this validates credibility levels for Bayesian credible intervals.

    Parameters
    ----------
    level : float
        Probability level to validate (should be between 0 and 1 exclusive)
    param_name : str, default "probability level"
        Parameter name for error messages

    Raises
    ------
    ValueError
        If level is not between 0 and 1 (exclusive)

    Examples
    --------
    >>> validate_probability_level(0.80)  # No error
    >>> validate_probability_level(0.95, "probability level")  # No error
    >>> validate_probability_level(1.2)  # Raises ValueError
    >>> validate_probability_level(-0.1)  # Raises ValueError

    Notes
    -----
    This function provides a statistically neutral validation that works for
    any probability parameter requiring values in (0, 1).
    """
    if not (0 < level < 1):
        raise ValueError(
            f"{param_name} must be between 0 and 1 (exclusive), got {level}"
        )


def validate_threshold_parameter(
    threshold: float, param_name: str = "threshold"
) -> None:
    """
    Validate threshold parameter for statistical testing.

    Parameters
    ----------
    threshold : float
        Threshold value to validate
    param_name : str, default "threshold"
        Parameter name for error messages

    Raises
    ------
    ValueError
        If threshold is not finite

    Examples
    --------
    >>> validate_threshold_parameter(0.0)  # No error
    >>> validate_threshold_parameter(5.5, "effect threshold")  # No error
    >>> validate_threshold_parameter(float('inf'))  # Raises ValueError
    >>> validate_threshold_parameter(float('nan'))  # Raises ValueError
    """
    if not np.isfinite(threshold):
        raise ValueError(f"{param_name} must be finite, got {threshold}")


def validate_degrees_freedom(df: int, param_name: str = "degrees of freedom") -> None:
    """
    Validate degrees of freedom parameter for statistical inference.

    Parameters
    ----------
    df : int
        Degrees of freedom to validate
    param_name : str, default "degrees of freedom"
        Parameter name for error messages

    Raises
    ------
    ValueError
        If degrees of freedom is not positive

    Examples
    --------
    >>> validate_degrees_freedom(10)  # No error
    >>> validate_degrees_freedom(1, "residual df")  # No error
    >>> validate_degrees_freedom(0)  # Raises ValueError
    >>> validate_degrees_freedom(-5)  # Raises ValueError
    """
    if df <= 0:
        raise ValueError(f"{param_name} must be positive, got {df}")


def validate_variance_parameters(**variances: float) -> None:
    """
    Validate variance parameters are non-negative and finite.

    Parameters
    ----------
    **variances
        Keyword arguments containing variance parameters to validate

    Raises
    ------
    ValueError
        If any variance is negative or not finite

    Examples
    --------
    >>> validate_variance_parameters(var_alpha=0.01, var_beta=0.005)  # No error
    >>> validate_variance_parameters(sigma_squared=100.0)  # No error
    >>> validate_variance_parameters(var_alpha=-0.01)  # Raises ValueError
    >>> validate_variance_parameters(var_beta=float('nan'))  # Raises ValueError
    """
    for param_name, variance in variances.items():
        if not np.isfinite(variance):
            raise ValueError(f"{param_name} must be finite, got {variance}")
        if variance < 0:
            raise ValueError(f"{param_name} must be non-negative, got {variance}")


# =============================================================================
# Enhanced Data Quality Validation Functions
# =============================================================================


def validate_dataframe_not_empty(df: pd.DataFrame, df_name: str) -> None:
    """
    Validate that DataFrame is not empty.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate
    df_name : str
        Name of the DataFrame for error messages

    Raises
    ------
    ValueError
        If DataFrame is empty

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'a': [1, 2, 3]})
    >>> validate_dataframe_not_empty(df, 'test_data')  # No error
    >>> empty_df = pd.DataFrame()
    >>> validate_dataframe_not_empty(empty_df, 'empty_data')  # Raises ValueError
    """
    if df.empty:
        raise ValueError(f"{df_name} cannot be empty")


def validate_column_types(df: pd.DataFrame, column_types: Dict[str, str]) -> None:
    """
    Validate that DataFrame columns have expected data types.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate
    column_types : Dict[str, str]
        Dictionary mapping column names to expected dtype names

    Raises
    ------
    ValueError
        If any column has unexpected dtype

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'date': pd.date_range('2023-01-01', periods=3),
    ...     'value': [1.0, 2.0, 3.0]
    ... })
    >>> validate_column_types(df, {'value': 'float64'})  # No error
    >>> validate_column_types(df, {'value': 'int64'})  # May raise ValueError
    """
    for col, expected_type in column_types.items():
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame")

        actual_type = str(df[col].dtype)
        if actual_type != expected_type:
            raise ValueError(
                f"Column '{col}' has dtype '{actual_type}', expected '{expected_type}'"
            )


def validate_time_series_continuity(df: pd.DataFrame, time_col: str) -> None:
    """
    Validate that time series has reasonable continuity (no major gaps).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing time series data
    time_col : str
        Name of the time column

    Raises
    ------
    ValueError
        If time series has major discontinuities or is not sorted

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'date': pd.date_range('2023-01-01', periods=5),
    ...     'value': [1, 2, 3, 4, 5]
    ... })
    >>> validate_time_series_continuity(df, 'date')  # No error
    """
    if df.empty:
        return

    time_series = df[time_col].copy()

    # Check if time series is sorted
    if not time_series.is_monotonic_increasing:
        raise ValueError(
            f"Time series in column '{time_col}' must be sorted in ascending order"
        )

    # For datetime columns, check for reasonable gaps
    if pd.api.types.is_datetime64_any_dtype(time_series):
        if len(time_series) > 1:
            time_diffs = time_series.diff().dropna()
            median_diff = time_diffs.median()
            max_diff = time_diffs.max()

            # Flag if any gap is more than 10x the median gap
            if max_diff > median_diff * 10:
                raise ValueError(
                    f"Time series in column '{time_col}' has large gaps. "
                    f"Median gap: {median_diff}, Max gap: {max_diff}"
                )


# =============================================================================
# Column Name Validation for API Design
# =============================================================================


def validate_column_distinctness(
    time_col: str,
    control_col: str,
    test_col: str,
) -> None:
    """
    Validate that time_col, control_col, and test_col are distinct column names.

    This validation prevents logical errors where the same column is used for
    multiple purposes in TBR analysis (e.g., using the same column as both
    control and test groups).

    Parameters
    ----------
    time_col : str
        Name of the time column
    control_col : str
        Name of the control group column
    test_col : str
        Name of the test group column

    Raises
    ------
    ValueError
        If any two column names are identical

    Examples
    --------
    >>> validate_column_distinctness('date', 'control', 'test')  # OK
    >>> validate_column_distinctness('date', 'metric', 'metric')  # Raises ValueError
    Traceback (most recent call last):
        ...
    ValueError: control_col and test_col must be different columns. Both are set to 'metric'

    Notes
    -----
    Catches user errors early with clear, actionable error messages.
    """
    if time_col == control_col:
        raise ValueError(
            f"time_col and control_col must be different columns. "
            f"Both are set to '{time_col}'"
        )

    if time_col == test_col:
        raise ValueError(
            f"time_col and test_col must be different columns. "
            f"Both are set to '{time_col}'"
        )

    if control_col == test_col:
        raise ValueError(
            f"control_col and test_col must be different columns. "
            f"Both are set to '{control_col}'"
        )


# Reserved column names used in TBR output DataFrames
# These are used when converting results to DataFrame format
_RESERVED_OUTPUT_COLUMNS = frozenset(
    [
        "period",  # Period indicator (-1=baseline, 0=pretest, 1=test, 3=cooldown)
        "y",  # Test group values
        "x",  # Control group values
        "pred",  # Predicted/fitted values
        "predsd",  # Prediction standard deviations
        "dif",  # Residuals/effects (y - pred)
        "cumdif",  # Cumulative effects
        "cumsd",  # Cumulative standard deviations
        "estsd",  # Fitted value standard deviations
    ]
)


def validate_no_reserved_column_conflicts(
    _data: pd.DataFrame,
    time_col: str,
    control_col: str,
    test_col: str,
) -> None:
    """
    Validate that user column names don't conflict with TBR output column names.

    TBR analysis generates output DataFrames with specific column names. If the
    user's input data already contains columns with these names, it could cause
    confusion or data loss when results are exported to DataFrame format.

    This validation prevents such conflicts by checking user-specified column names
    against the reserved output column names used by TBR.

    Parameters
    ----------
    data : pd.DataFrame
        Input DataFrame containing the time series data
    time_col : str
        Name of the time column
    control_col : str
        Name of the control group column
    test_col : str
        Name of the test group column

    Raises
    ------
    ValueError
        If any user-specified column name conflicts with reserved TBR output columns

    Examples
    --------
    >>> import pandas as pd
    >>> data = pd.DataFrame({
    ...     'date': [1, 2, 3],
    ...     'control': [100, 110, 120],
    ...     'test': [102, 112, 122]
    ... })
    >>> validate_no_reserved_column_conflicts(data, 'date', 'control', 'test')  # OK

    >>> data_conflict = pd.DataFrame({
    ...     'date': [1, 2, 3],
    ...     'control': [100, 110, 120],
    ...     'pred': [102, 112, 122]  # 'pred' is reserved!
    ... })
    >>> validate_no_reserved_column_conflicts(data_conflict, 'date', 'control', 'pred')
    Traceback (most recent call last):
        ...
    ValueError: Column name(s) {'pred'} are reserved for TBR output...

    Notes
    -----
    Reserved column names: period, y, x, pred, predsd, dif, cumdif, cumsd, estsd

    Prevents column name conflicts between user-specified columns and reserved
    TBR output column names, providing clear, actionable error messages to users.
    """
    # Check user-specified columns against reserved names
    user_columns = {time_col, control_col, test_col}
    conflicts = user_columns & _RESERVED_OUTPUT_COLUMNS

    if conflicts:
        raise ValueError(
            f"Column name(s) {conflicts} are reserved for TBR output columns. "
            f"Please rename these columns in your input data.\n"
            f"Reserved column names: {sorted(_RESERVED_OUTPUT_COLUMNS)}"
        )
