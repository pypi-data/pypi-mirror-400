"""TBR utilities module."""

from .constants import CONTROL_VAL, TEST_VAL
from .datetime_utils import (
    create_time_range_mask,
    process_time_column,
    sort_dataframe_by_time,
)
from .exceptions import (
    ConvergenceError,
    InsufficientDataError,
    NumericalInstabilityError,
    TBRError,
)
from .export import export_to_csv, export_to_json, load_json, safe_json_serialize
from .performance import (
    EfficiencyMetrics,
    EfficiencyReport,
    PerformanceMetrics,
    PerformanceMonitor,
    PerformanceProfiler,
    benchmark_tbr_functions,
    profile_tbr_workflow,
)
from .preprocessing import (
    assign_period_indicators,
    calculate_basic_statistics,
    extract_regression_arrays,
    prepare_regression_arrays,
    split_time_series_by_periods,
)
from .structure_validation import (
    validate_analysis_results_tuple,
    validate_model_parameters_dict,
    validate_nested_dict_structure,
    validate_tbr_output_structure,
)
from .validation import (
    validate_array_not_empty,
    validate_column_types,
    validate_dataframe_not_empty,
    validate_degrees_freedom,
    validate_learning_set,
    validate_metric_columns,
    validate_no_nulls,
    validate_period_data,
    validate_probability_level,
    validate_required_columns,
    validate_sample_size,
    validate_threshold_parameter,
    validate_time_boundaries_type,
    validate_time_column_type,
    validate_time_periods,
    validate_time_series_continuity,
    validate_variance_parameters,
)

__all__ = [
    # Constants
    "CONTROL_VAL",
    "TEST_VAL",
    # Exceptions
    "TBRError",
    "ConvergenceError",
    "NumericalInstabilityError",
    "InsufficientDataError",
    # Array & Sample Validation
    "validate_array_not_empty",
    "validate_sample_size",
    # Core DataFrame Validation
    "validate_required_columns",
    "validate_no_nulls",
    "validate_metric_columns",
    # Time-Related Validation
    "validate_time_column_type",
    "validate_time_boundaries_type",
    "validate_time_periods",
    # Data Quality Validation
    "validate_period_data",
    "validate_learning_set",
    # Statistical Parameter Validation
    "validate_probability_level",
    "validate_threshold_parameter",
    "validate_degrees_freedom",
    "validate_variance_parameters",
    # Enhanced Data Quality Validation
    "validate_dataframe_not_empty",
    "validate_column_types",
    "validate_time_series_continuity",
    # Data Preprocessing Functions
    "split_time_series_by_periods",
    "extract_regression_arrays",
    "assign_period_indicators",
    "prepare_regression_arrays",
    "calculate_basic_statistics",
    # Date/Time Handling Functions
    "sort_dataframe_by_time",
    "process_time_column",
    "create_time_range_mask",
    # Data Structure Validation Functions
    "validate_model_parameters_dict",
    "validate_tbr_output_structure",
    "validate_analysis_results_tuple",
    "validate_nested_dict_structure",
    # Performance Diagnostics
    "PerformanceProfiler",
    "EfficiencyMetrics",
    "PerformanceMonitor",
    "PerformanceMetrics",
    "EfficiencyReport",
    "profile_tbr_workflow",
    "benchmark_tbr_functions",
    # Export Utilities
    "export_to_json",
    "export_to_csv",
    "load_json",
    "safe_json_serialize",
]
