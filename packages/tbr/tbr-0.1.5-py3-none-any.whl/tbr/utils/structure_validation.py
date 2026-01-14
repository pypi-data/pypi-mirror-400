"""
Data Structure Validation Utilities for TBR Analysis.

This module provides validation functions for complex data structures used
throughout the TBR package. These utilities complement the existing validation
functions by focusing on structured data validation patterns.

The functions are designed to validate dictionaries, tuples, and nested
structures commonly used in TBR analysis results and parameters.

Examples
--------
>>> from tbr.utils.structure_validation import validate_model_parameters_dict
>>>
>>> # Validate regression model parameters
>>> params = {
...     'alpha': 50.0,
...     'beta': 0.95,
...     'sigma': 25.0,
...     'var_alpha': 100.0,
...     'var_beta': 0.001,
...     'cov_alpha_beta': -0.05,
...     'degrees_freedom': 43,
...     'n_pretest': 45,
        ...     'pretest_x_mean': 1000.0
... }
>>> validate_model_parameters_dict(params)  # No error if valid
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd


def validate_model_parameters_dict(
    params: Dict[str, Union[float, int]], required_keys: Optional[List[str]] = None
) -> None:
    """
    Validate model parameters dictionary structure and types.

    This function validates the structure of model parameter dictionaries
    returned by regression fitting functions, ensuring all required keys
    are present and values have appropriate types.

    Parameters
    ----------
    params : Dict[str, Union[float, int]]
        Dictionary containing model parameters
    required_keys : List[str], optional
        List of required parameter keys. If None, uses default TBR model keys.

    Raises
    ------
    TypeError
        If params is not a dictionary or values have wrong types
    ValueError
        If required keys are missing or values are invalid

    Examples
    --------
    >>> params = {
    ...     'alpha': 50.0,
    ...     'beta': 0.95,
    ...     'sigma': 25.0,
    ...     'var_alpha': 100.0,
    ...     'var_beta': 0.001,
    ...     'cov_alpha_beta': -0.05,
    ...     'degrees_freedom': 43,
    ...     'n_pretest': 45,
        ...     'pretest_x_mean': 1000.0
    ... }
    >>> validate_model_parameters_dict(params)  # No error

    >>> # Missing required key
    >>> incomplete_params = {'alpha': 50.0, 'beta': 0.95}
    >>> validate_model_parameters_dict(incomplete_params)  # Raises ValueError
    """
    # Type validation
    if not isinstance(params, dict):
        raise TypeError(f"Model parameters must be a dictionary, got {type(params)}")

    # Default required keys for TBR model parameters
    if required_keys is None:
        required_keys = [
            "alpha",
            "beta",
            "sigma",
            "var_alpha",
            "var_beta",
            "cov_alpha_beta",
            "degrees_freedom",
            "n_pretest",
            "pretest_x_mean",
        ]

    # Check for missing keys
    missing_keys = [key for key in required_keys if key not in params]
    if missing_keys:
        raise ValueError(f"Missing required model parameters: {missing_keys}")

    # Validate value types and constraints
    for key, value in params.items():
        if not isinstance(value, (int, float)):
            raise TypeError(f"Parameter '{key}' must be numeric, got {type(value)}")

        # Check for non-finite values
        if (
            not pd.api.types.is_number(value)
            or not pd.notna(value)
            or not pd.api.types.is_scalar(value)
        ):
            raise ValueError(f"Parameter '{key}' must be finite, got {value}")

        # Additional check for infinity
        if math.isinf(value):
            raise ValueError(f"Parameter '{key}' must be finite, got {value}")

        # Specific constraints for known parameters
        if key in ["sigma", "var_alpha", "var_beta"] and value <= 0:
            raise ValueError(f"Parameter '{key}' must be positive, got {value}")

        if key == "degrees_freedom" and (not isinstance(value, int) or value <= 0):
            raise ValueError(
                f"Parameter '{key}' must be a positive integer, got {value}"
            )

        if key == "n_pretest" and (not isinstance(value, int) or value < 3):
            raise ValueError(f"Parameter '{key}' must be an integer >= 3, got {value}")


def validate_tbr_output_structure(
    tbr_dataframe: pd.DataFrame, required_columns: Optional[List[str]] = None
) -> None:
    """
    Validate TBR output DataFrame structure and column requirements.

    This function validates that TBR analysis output DataFrames have the
    expected structure, columns, and data types required for downstream
    processing and summary generation.

    Parameters
    ----------
    tbr_dataframe : pd.DataFrame
        TBR analysis output DataFrame to validate
    required_columns : List[str], optional
        List of required column names. If None, uses default TBR output columns.

    Raises
    ------
    TypeError
        If input is not a pandas DataFrame
    ValueError
        If required columns are missing or have invalid structure

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> # Valid TBR output structure
    >>> tbr_df = pd.DataFrame({
    ...     'period': [0, 0, 1, 1],
    ...     'y': [100, 110, 120, 130],
    ...     'x': [95, 105, 115, 125],
    ...     'pred': [98, 108, 118, 128],
    ...     'cumdif': [np.nan, np.nan, 2, 4],
    ...     'cumsd': [0, 0, 1.5, 2.1]
    ... })
    >>> validate_tbr_output_structure(tbr_df)  # No error
    """
    # Type validation
    if not isinstance(tbr_dataframe, pd.DataFrame):
        raise TypeError(
            f"TBR output must be a pandas DataFrame, got {type(tbr_dataframe)}"
        )

    # Check for empty DataFrame
    if tbr_dataframe.empty:
        raise ValueError("TBR output DataFrame cannot be empty")

    # Default required columns for TBR output
    if required_columns is None:
        required_columns = ["period", "y", "x", "pred", "cumdif", "cumsd"]

    # Check for missing columns
    missing_columns = [
        col for col in required_columns if col not in tbr_dataframe.columns
    ]
    if missing_columns:
        raise ValueError(f"Missing required columns in TBR output: {missing_columns}")

    # Validate specific column constraints
    if "period" in tbr_dataframe.columns:
        valid_periods = {-1, 0, 1, 3}  # baseline, pretest, test, cooldown
        invalid_periods = set(tbr_dataframe["period"].dropna().unique()) - valid_periods
        if invalid_periods:
            raise ValueError(
                f"Invalid period values found: {invalid_periods}. "
                f"Valid periods are: {valid_periods}"
            )

    # Check for required numeric columns
    numeric_columns = ["y", "x", "pred", "cumdif", "cumsd"]
    for col in numeric_columns:
        if col in tbr_dataframe.columns:
            if not pd.api.types.is_numeric_dtype(tbr_dataframe[col]):
                raise ValueError(
                    f"Column '{col}' must be numeric, got {tbr_dataframe[col].dtype}"
                )


def validate_analysis_results_tuple(
    results: Tuple[pd.DataFrame, pd.DataFrame], expected_length: int = 2
) -> None:
    """
    Validate analysis results tuple structure and contents.

    This function validates tuples returned by analysis functions,
    ensuring they have the expected length and contain valid DataFrames.

    Parameters
    ----------
    results : Tuple[pd.DataFrame, pd.DataFrame]
        Tuple containing analysis results (typically tbr_dataframe, tbr_summaries)
    expected_length : int, default 2
        Expected number of elements in the tuple

    Raises
    ------
    TypeError
        If results is not a tuple or contains non-DataFrame elements
    ValueError
        If tuple has wrong length or DataFrames are invalid

    Examples
    --------
    >>> import pandas as pd
    >>> # Valid results tuple
    >>> df1 = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    >>> df2 = pd.DataFrame({'c': [5, 6], 'd': [7, 8]})
    >>> results = (df1, df2)
    >>> validate_analysis_results_tuple(results)  # No error

    >>> # Invalid: wrong length
    >>> validate_analysis_results_tuple((df1,), expected_length=2)  # Raises ValueError
    """
    # Type validation
    if not isinstance(results, tuple):
        raise TypeError(f"Analysis results must be a tuple, got {type(results)}")

    # Length validation
    if len(results) != expected_length:
        raise ValueError(
            f"Expected tuple of length {expected_length}, got length {len(results)}"
        )

    # Validate each element is a DataFrame
    for i, element in enumerate(results):
        if not isinstance(element, pd.DataFrame):
            raise TypeError(
                f"Element {i} must be a pandas DataFrame, got {type(element)}"
            )

        if element.empty:
            raise ValueError(f"DataFrame at position {i} cannot be empty")


def validate_nested_dict_structure(
    data: Dict[str, Any],
    required_keys: List[str],
    value_types: Optional[Dict[str, type]] = None,
    allow_extra_keys: bool = True,
) -> None:
    """
    Validate nested dictionary structure with type checking.

    This function provides flexible validation for nested dictionaries
    commonly used in configuration, results, and parameter structures.

    Parameters
    ----------
    data : Dict[str, Any]
        Dictionary to validate
    required_keys : List[str]
        List of keys that must be present
    value_types : Dict[str, type], optional
        Dictionary mapping keys to expected value types
    allow_extra_keys : bool, default True
        Whether to allow keys not in required_keys

    Raises
    ------
    TypeError
        If data is not a dictionary or values have wrong types
    ValueError
        If required keys are missing

    Examples
    --------
    >>> # Configuration dictionary
    >>> config = {
    ...     'level': 0.80,
    ...     'threshold': 0.0,
    ...     'test_end_inclusive': False
    ... }
    >>> validate_nested_dict_structure(
    ...     config,
    ...     required_keys=['level', 'threshold'],
    ...     value_types={'level': float, 'threshold': float, 'test_end_inclusive': bool}
    ... )  # No error

    >>> # Missing required key
    >>> incomplete_config = {'level': 0.80}
    >>> validate_nested_dict_structure(
    ...     incomplete_config,
    ...     required_keys=['level', 'threshold']
    ... )  # Raises ValueError
    """
    # Type validation
    if not isinstance(data, dict):
        raise TypeError(f"Data must be a dictionary, got {type(data)}")

    # Check for missing required keys
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        raise ValueError(f"Missing required keys: {missing_keys}")

    # Check for unexpected keys if not allowed
    if not allow_extra_keys:
        extra_keys = [key for key in data.keys() if key not in required_keys]
        if extra_keys:
            raise ValueError(f"Unexpected keys found: {extra_keys}")

    # Validate value types if specified
    if value_types:
        for key, expected_type in value_types.items():
            if key in data:
                actual_value = data[key]
                if not isinstance(actual_value, expected_type):
                    raise TypeError(
                        f"Key '{key}' expected type {expected_type.__name__}, "
                        f"got {type(actual_value).__name__}"
                    )


# Export list for clean imports
__all__ = [
    "validate_model_parameters_dict",
    "validate_tbr_output_structure",
    "validate_analysis_results_tuple",
    "validate_nested_dict_structure",
]
