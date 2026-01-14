"""
Export utilities for TBR analysis results.

This module provides utilities for exporting TBR results to various formats
(JSON, CSV, DataFrame) with comprehensive metadata preservation.

Functions
---------
export_to_json : Export any TBR result object to JSON file
export_to_csv : Export DataFrame-compatible results to CSV file
safe_json_serialize : Convert numpy/pandas objects for JSON serialization

Examples
--------
Export functional API results to JSON:

>>> from tbr.functional import perform_tbr_analysis
>>> from tbr.utils.export import export_to_json, export_to_csv
>>> results = perform_tbr_analysis(data, ...)
>>>
>>> # Export summary to JSON
>>> export_to_json(results.summary(), 'summary.json')
>>>
>>> # Export full TBR dataframe to CSV
>>> export_to_csv(results.tbr_dataframe(), 'tbr_results.csv')

Export OOP API results:

>>> from tbr import TBRAnalysis
>>> model = TBRAnalysis()
>>> model.fit(data, ...)
>>>
>>> # Export summary result
>>> summary = model.summarize()
>>> export_to_json(summary, 'summary.json')
>>>
>>> # Export predictions
>>> predictions = model.predict()
>>> export_to_csv(predictions.predictions, 'predictions.csv')
"""

import json
from pathlib import Path
from typing import Any, Dict, Union

import numpy as np
import pandas as pd


def safe_json_serialize(obj: Any) -> Any:
    """
    Convert numpy/pandas objects to JSON-serializable types.

    Handles conversion of numpy arrays, pandas DataFrames/Series, and other
    non-JSON-serializable types to standard Python types.

    Parameters
    ----------
    obj : any
        Object to convert for JSON serialization

    Returns
    -------
    any
        JSON-serializable version of the object

    Examples
    --------
    >>> import numpy as np
    >>> arr = np.array([1, 2, 3])
    >>> safe_json_serialize(arr)
    [1, 2, 3]

    >>> import pandas as pd
    >>> df = pd.DataFrame({'a': [1, 2]})
    >>> result = safe_json_serialize(df)
    >>> isinstance(result, dict)
    True
    """
    # Handle None
    if obj is None:
        return None

    # Handle numpy scalars
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()

    # Handle pandas objects
    if isinstance(obj, pd.DataFrame):
        # Convert DataFrame to dict with proper handling of datetime indices
        return {
            "data": obj.to_dict(orient="records"),
            "columns": list(obj.columns),
            "index": (
                obj.index.tolist()
                if not isinstance(obj.index, pd.DatetimeIndex)
                else obj.index.strftime("%Y-%m-%d %H:%M:%S").tolist()
            ),
        }
    if isinstance(obj, pd.Series):
        return {
            "values": obj.values.tolist(),
            "name": obj.name,
            "index": (
                obj.index.tolist()
                if not isinstance(obj.index, pd.DatetimeIndex)
                else obj.index.strftime("%Y-%m-%d %H:%M:%S").tolist()
            ),
        }
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if isinstance(obj, pd.Index):
        # Handle all pandas Index types (DatetimeIndex, Int64Index, etc.)
        if isinstance(obj, pd.DatetimeIndex):
            return obj.strftime("%Y-%m-%d %H:%M:%S").tolist()
        return obj.tolist()

    # Handle dictionaries recursively
    if isinstance(obj, dict):
        return {key: safe_json_serialize(value) for key, value in obj.items()}

    # Handle lists/tuples recursively
    if isinstance(obj, (list, tuple)):
        return [safe_json_serialize(item) for item in obj]

    # Return as-is for JSON-safe types
    return obj


def export_to_json(
    obj: Any,
    filepath: Union[str, Path],
    include_metadata: bool = True,
    indent: int = 2,
) -> None:
    """
    Export any TBR result object to JSON file with metadata.

    Handles TBR result objects (TBRPredictionResult, TBRSummaryResult,
    TBRSubintervalResult), pandas DataFrames, and dictionaries. Automatically
    converts numpy/pandas objects for JSON compatibility.

    Parameters
    ----------
    obj : any
        Object to export (result object, DataFrame, dict, etc.)
    filepath : str or Path
        Path to output JSON file
    include_metadata : bool, default=True
        Whether to include type metadata in output
    indent : int, default=2
        JSON indentation level (None for compact output)

    Examples
    --------
    >>> from tbr import TBRAnalysis
    >>> model = TBRAnalysis()
    >>> model.fit(data, ...)
    >>> summary = model.summarize()
    >>> export_to_json(summary, 'summary.json')

    >>> # Export with compact formatting
    >>> export_to_json(summary, 'summary_compact.json', indent=None)

    Notes
    -----
    The output JSON includes metadata about the object type and structure
    when `include_metadata=True`, enabling reconstruction of the original
    object if needed.
    """
    filepath = Path(filepath)

    # Convert object to dictionary
    # Check for result objects first (they have to_dict and a specific type name)
    if isinstance(obj, pd.DataFrame):
        data = obj
        obj_type = "DataFrame"
    elif hasattr(obj, "to_dict") and not isinstance(obj, dict):
        # Result objects with to_dict method
        data = obj.to_dict()
        obj_type = type(obj).__name__
    elif isinstance(obj, dict):
        data = obj
        obj_type = "dict"
    else:
        raise TypeError(
            f"Cannot export object of type {type(obj).__name__} to JSON. "
            f"Supported types: TBR result objects, DataFrame, dict"
        )

    # Convert to JSON-serializable format
    json_data = safe_json_serialize(data)

    # Add metadata if requested
    if include_metadata:
        output = {"type": obj_type, "data": json_data}
    else:
        output = json_data

    # Write to file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=indent)


def export_to_csv(
    obj: Any,
    filepath: Union[str, Path],
    include_index: bool = True,
    **kwargs: Any,
) -> None:
    r"""
    Export DataFrame-compatible TBR results to CSV file.

    Handles pandas DataFrames and TBR result objects that have DataFrame
    representations. For result objects, calls to_dataframe() if available.

    Parameters
    ----------
    obj : any
        Object to export (DataFrame or result object with to_dataframe())
    filepath : str or Path
        Path to output CSV file
    include_index : bool, default=True
        Whether to include index in CSV output
    **kwargs : any
        Additional arguments passed to pandas.DataFrame.to_csv()

    Examples
    --------
    >>> from tbr import TBRAnalysis
    >>> model = TBRAnalysis()
    >>> model.fit(data, ...)
    >>>
    >>> # Export summary as CSV
    >>> summary = model.summarize()
    >>> export_to_csv(summary, 'summary.csv')
    >>>
    >>> # Export predictions
    >>> predictions = model.predict()
    >>> export_to_csv(predictions.predictions, 'predictions.csv', index=False)

    >>> # Export with custom separator
    >>> export_to_csv(summary, 'summary.tsv', sep='\\t')

    Notes
    -----
    For objects without a DataFrame representation, consider using
    export_to_json() instead, which can handle more complex structures.
    """
    filepath = Path(filepath)

    # Convert to DataFrame if needed
    if isinstance(obj, pd.DataFrame):
        df = obj
    elif hasattr(obj, "to_dataframe"):
        df = obj.to_dataframe()
    elif hasattr(obj, "predictions") and isinstance(obj.predictions, pd.DataFrame):
        # Handle TBRPredictionResult
        df = obj.predictions
    else:
        raise TypeError(
            f"Cannot export object of type {type(obj).__name__} to CSV. "
            f"Supported types: DataFrame, objects with to_dataframe() method"
        )

    # Export to CSV
    # Don't pass include_index if 'index' is already in kwargs
    if "index" in kwargs:
        df.to_csv(filepath, **kwargs)
    else:
        df.to_csv(filepath, index=include_index, **kwargs)


def load_json(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Load JSON file exported by export_to_json().

    Parameters
    ----------
    filepath : str or Path
        Path to JSON file

    Returns
    -------
    dict
        Loaded data (with metadata if it was included during export)

    Examples
    --------
    >>> data = load_json('summary.json')
    >>> if 'type' in data:
    ...     print(f"Object type: {data['type']}")
    ...     content = data['data']
    ... else:
    ...     content = data
    """
    filepath = Path(filepath)

    with open(filepath, encoding="utf-8") as f:
        result: Dict[str, Any] = json.load(f)
        return result
