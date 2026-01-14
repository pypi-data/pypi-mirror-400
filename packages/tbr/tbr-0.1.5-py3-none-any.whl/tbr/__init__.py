"""
TBR - Time-Based Regression Analysis Package.

A comprehensive, domain-agnostic Python package for Time-Based Regression (TBR)
analysis. Perform rigorous statistical analysis of treatment/control group time
series data across any industry.

Features
--------
- Domain-agnostic treatment/control analysis
- Rigorous statistical methodology with proper variance quantification
- Comprehensive credible interval construction using t-distribution
- Support for any time series treatment/control experiment
- Full type hints and documentation

Quick Start
-----------
>>> import pandas as pd
>>> from tbr.functional import perform_tbr_analysis
>>>
>>> # Your time series data with columns: date, control, test
>>> data = pd.DataFrame({
...     'date': pd.date_range('2023-01-01', periods=100),
...     'control': np.random.normal(100, 10, 100),
...     'test': np.random.normal(105, 10, 100)
... })
>>>
>>> # Perform TBR analysis
>>> tbr_df, summary_df = perform_tbr_analysis(
...     data=data,
...     time_col='date',
...     control_col='control',
...     test_col='test',
...     pretest_start='2023-01-01',
...     test_start='2023-02-15',
...     test_end='2023-04-10'
... )

See Also
--------
- Documentation: https://tbr.readthedocs.io/
- Source Code: https://github.com/idohi/tbr
- Issues: https://github.com/idohi/tbr/issues
"""

from importlib.metadata import version as _get_version

__version__ = _get_version("tbr")
__author__ = "Ido Hirsh"
__license__ = "BSD-3-Clause"

# Lazy imports for optimal memory usage
import lazy_loader as lazy

# Lazy loading implementation - modules load only when accessed
__getattr__, __dir__, __all__ = lazy.attach(
    __name__,
    submodules=["functional", "utils", "analysis", "core"],
    submod_attrs={
        "functional": ["perform_tbr_analysis"],
        "core": ["TBRAnalysis"],
        "utils": ["CONTROL_VAL", "TEST_VAL"],
        "analysis": [
            "create_tbr_summary",
            "create_incremental_tbr_summaries",
            "compute_interval_estimate_and_ci",
            "analyze_multiple_subintervals",
            "create_subinterval_summary",
            "validate_tbr_model",
            "diagnose_tbr_analysis",
            "check_tbr_assumptions",
            "analyze_tbr_residuals",
            "assess_tbr_performance",
            "create_tbr_diagnostic_report",
        ],
    },
)

# Add package metadata to __all__
__all__ = __all__ + ["__version__", "__author__", "__license__"]
