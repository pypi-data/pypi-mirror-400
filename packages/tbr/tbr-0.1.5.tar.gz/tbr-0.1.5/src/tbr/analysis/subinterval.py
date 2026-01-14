"""
TBR Subinterval Analysis Module.

This module provides specialized functionality for custom time window analysis
in Time-Based Regression (TBR), enabling flexible analysis of treatment effects
over specific subintervals within the test period.

The subinterval analysis approach allows researchers to:
- Analyze treatment effects for specific time ranges
- Compare effects across different time windows
- Identify when effects become significant during the test period
- Perform detailed temporal analysis of treatment impact
- Validate effect consistency across different intervals

Functions
---------
compute_interval_estimate_and_ci : Compute subinterval effect estimate and credible interval
analyze_multiple_subintervals : Analyze multiple time windows simultaneously
create_subinterval_summary : Create comprehensive subinterval analysis summary
validate_subinterval_parameters : Validate subinterval analysis parameters

Examples
--------
>>> from tbr.analysis.subinterval import compute_interval_estimate_and_ci
>>> result = compute_interval_estimate_and_ci(
...     tbr_results, tbr_summary, start_day=5, end_day=10, ci_level=0.80
... )
>>> print(f"Days 5-10 effect: {result['estimate']:.2f}")
>>> print(f"80% CI: [{result['lower']:.2f}, {result['upper']:.2f}]")

Analyze multiple subintervals:

>>> from tbr.analysis.subinterval import analyze_multiple_subintervals
>>> intervals = [(1, 7), (8, 14), (1, 14)]  # Week 1, Week 2, Full period
>>> results = analyze_multiple_subintervals(
...     tbr_results, tbr_summary, intervals, ci_level=0.80
... )
>>> for i, result in enumerate(results):
...     start, end = intervals[i]
...     print(f"Days {start}-{end}: {result['estimate']:.2f} "
...           f"[{result['lower']:.2f}, {result['upper']:.2f}]")

Create comprehensive summary:

>>> from tbr.analysis.subinterval import create_subinterval_summary
>>> summary = create_subinterval_summary(
...     tbr_results, tbr_summary, intervals=[(1, 7), (8, 14)], ci_level=0.80
... )
>>> print(summary[['interval', 'estimate', 'lower', 'upper', 'significant']])
"""

from typing import Dict, List, Tuple

import pandas as pd

# Import core functionality for wrapping
from tbr.core.effects import compute_interval_estimate_and_ci as core_compute_interval


def compute_interval_estimate_and_ci(
    tbr_df: pd.DataFrame,
    tbr_summary: pd.DataFrame,
    start_day: int,
    end_day: int,
    ci_level: float,
) -> Dict[str, float]:
    r"""
    Compute cumulative treatment effect estimate and credible interval for a subinterval.

    This function calculates the cumulative treatment effect over a specified
    subinterval within the test period, along with its credible interval using
    t-distribution. This enables analysis of treatment effects for specific time
    ranges rather than the entire test period, providing flexible temporal analysis
    capabilities for TBR experiments.

    Parameters
    ----------
    tbr_df : pd.DataFrame
        TBR daily output with columns 'y', 'pred', 'period', 'estsd'.
        Must contain test period data (period == 1).
    tbr_summary : pd.DataFrame
        TBR summary containing 'sigma' and 't_dist_df' (degrees of freedom) parameters.
        Used for credible interval calculations.
    start_day : int
        Start day of subinterval (1-indexed within test period).
        Must be >= 1 and <= end_day.
    end_day : int
        End day of subinterval (inclusive, 1-indexed within test period).
        Must be >= start_day and <= total test days.
    ci_level : float
        Credible interval level (e.g., 0.80 for 80% interval).
        Must be between 0 and 1.

    Returns
    -------
    Dict[str, float]
        Dictionary containing subinterval analysis results:

        - 'estimate' : float
            Cumulative treatment effect for the subinterval
        - 'precision' : float
            Half-width of credible interval (margin of error)
        - 'lower' : float
            Lower bound of credible interval
        - 'upper' : float
            Upper bound of credible interval

    Raises
    ------
    ValueError
        If start_day > end_day, or if days are outside valid range
        If ci_level is not between 0 and 1
        If required columns are missing from input DataFrames
        If no test period data is found

    Notes
    -----
    The subinterval analysis uses the same mathematical foundation as the full
    TBR analysis, with credible intervals calculated using the t-distribution:

    .. math::
        CI = estimate ± t_{α/2,df} × se

    where the standard error combines model uncertainty and residual noise:

    .. math::
        se = \\sqrt{\\sum_{i=start}^{end} estsd_i^2 + n_{days} × σ^2}

    The posterior variance accounts for both prediction uncertainty (estsd²)
    and residual noise (σ²) over the subinterval period.

    Mathematical Foundation
    -----------------------
    The subinterval estimate is calculated as:

    .. math::
        estimate = \\sum_{i=start}^{end} (y_i - pred_i)

    where y_i is the observed value and pred_i is the counterfactual prediction
    for day i within the subinterval.

    Examples
    --------
    Analyze effect for days 5-10 of test period:

    >>> result = compute_interval_estimate_and_ci(
    ...     tbr_results, tbr_summary, start_day=5, end_day=10, ci_level=0.80
    ... )
    >>> print(f"Days 5-10 effect: {result['estimate']:.2f}")
    >>> print(f"80% CI: [{result['lower']:.2f}, {result['upper']:.2f}]")
    >>> print(f"Precision: ±{result['precision']:.2f}")

    Analyze single day effect:

    >>> day_7_result = compute_interval_estimate_and_ci(
    ...     tbr_results, tbr_summary, start_day=7, end_day=7, ci_level=0.95
    ... )
    >>> print(f"Day 7 effect: {day_7_result['estimate']:.2f}")

    Compare different credibility levels:

    >>> result_80 = compute_interval_estimate_and_ci(
    ...     tbr_results, tbr_summary, start_day=1, end_day=14, ci_level=0.80
    ... )
    >>> result_95 = compute_interval_estimate_and_ci(
    ...     tbr_results, tbr_summary, start_day=1, end_day=14, ci_level=0.95
    ... )
    >>> print(f"80% CI width: {result_80['upper'] - result_80['lower']:.2f}")
    >>> print(f"95% CI width: {result_95['upper'] - result_95['lower']:.2f}")
    """
    return core_compute_interval(
        tbr_df=tbr_df,
        tbr_summary=tbr_summary,
        start_day=start_day,
        end_day=end_day,
        ci_level=ci_level,
    )


def analyze_multiple_subintervals(
    tbr_df: pd.DataFrame,
    tbr_summary: pd.DataFrame,
    intervals: List[Tuple[int, int]],
    ci_level: float = 0.80,
) -> List[Dict[str, float]]:
    """
    Analyze multiple subintervals simultaneously for comparative analysis.

    This function performs subinterval analysis for multiple time windows within
    the test period, enabling comparative analysis of treatment effects across
    different temporal segments. This is particularly useful for understanding
    how treatment effects evolve over time and identifying periods of strongest
    or weakest impact.

    Parameters
    ----------
    tbr_df : pd.DataFrame
        TBR daily output with columns 'y', 'pred', 'period', 'estsd'.
        Must contain test period data (period == 1).
    tbr_summary : pd.DataFrame
        TBR summary containing 'sigma' and 't_dist_df' parameters.
    intervals : List[Tuple[int, int]]
        List of (start_day, end_day) tuples defining subintervals to analyze.
        Each tuple should contain 1-indexed day numbers within the test period.
    ci_level : float, default=0.80
        Credible interval level for all subintervals.
        Must be between 0 and 1.

    Returns
    -------
    List[Dict[str, float]]
        List of analysis results, one for each subinterval.
        Each dictionary contains the same keys as compute_interval_estimate_and_ci():
        'estimate', 'precision', 'lower', 'upper'.

    Raises
    ------
    ValueError
        If any interval has start_day > end_day
        If any day is outside the valid test period range
        If ci_level is not between 0 and 1
        If intervals list is empty

    Notes
    -----
    This function is equivalent to calling compute_interval_estimate_and_ci()
    for each interval individually, but provides a convenient interface for
    batch analysis and ensures consistent parameter validation.

    The results maintain the same mathematical rigor as individual subinterval
    analyses, with each interval analyzed independently using the full TBR
    statistical framework.

    Examples
    --------
    Compare weekly effects during a 2-week test:

    >>> intervals = [(1, 7), (8, 14)]  # Week 1, Week 2
    >>> results = analyze_multiple_subintervals(
    ...     tbr_results, tbr_summary, intervals, ci_level=0.80
    ... )
    >>> for i, result in enumerate(results, 1):
    ...     print(f"Week {i}: {result['estimate']:.2f} "
    ...           f"[{result['lower']:.2f}, {result['upper']:.2f}]")

    Analyze overlapping intervals:

    >>> intervals = [(1, 7), (4, 10), (7, 14)]  # Overlapping windows
    >>> results = analyze_multiple_subintervals(
    ...     tbr_results, tbr_summary, intervals, ci_level=0.90
    ... )
    >>> for i, (start, end) in enumerate(intervals):
    ...     result = results[i]
    ...     print(f"Days {start}-{end}: {result['estimate']:.2f}")

    Compare different interval lengths:

    >>> intervals = [(1, 3), (1, 7), (1, 14)]  # 3-day, 1-week, 2-week
    >>> results = analyze_multiple_subintervals(
    ...     tbr_results, tbr_summary, intervals
    ... )
    >>> for i, (start, end) in enumerate(intervals):
    ...     days = end - start + 1
    ...     avg_daily = results[i]['estimate'] / days
    ...     print(f"{days}-day period: {avg_daily:.2f} per day")
    """
    # Validate inputs
    if not intervals:
        raise ValueError("Intervals list cannot be empty")

    if not (0 < ci_level < 1):
        raise ValueError(f"ci_level must be between 0 and 1, got: {ci_level}")

    # Validate each interval
    for i, (start_day, end_day) in enumerate(intervals):
        if start_day > end_day:
            raise ValueError(
                f"Interval {i}: start_day ({start_day}) cannot be greater than "
                f"end_day ({end_day})"
            )
        if start_day < 1:
            raise ValueError(f"Interval {i}: start_day must be >= 1, got: {start_day}")

    # Analyze each interval
    results = []
    for start_day, end_day in intervals:
        result = compute_interval_estimate_and_ci(
            tbr_df=tbr_df,
            tbr_summary=tbr_summary,
            start_day=start_day,
            end_day=end_day,
            ci_level=ci_level,
        )
        results.append(result)

    return results


def create_subinterval_summary(
    tbr_df: pd.DataFrame,
    tbr_summary: pd.DataFrame,
    intervals: List[Tuple[int, int]],
    ci_level: float = 0.80,
    significance_threshold: float = 0.0,
) -> pd.DataFrame:
    """
    Create comprehensive summary DataFrame for multiple subinterval analyses.

    This function generates a structured summary of subinterval analyses,
    providing a tabular view of treatment effects across multiple time windows.
    The summary includes effect estimates, credible intervals, and significance
    indicators, making it easy to compare and interpret results across different
    temporal segments.

    Parameters
    ----------
    tbr_df : pd.DataFrame
        TBR daily output with columns 'y', 'pred', 'period', 'estsd'.
    tbr_summary : pd.DataFrame
        TBR summary containing 'sigma' and 't_dist_df' parameters.
    intervals : List[Tuple[int, int]]
        List of (start_day, end_day) tuples defining subintervals to analyze.
    ci_level : float, default=0.80
        Credible interval level for all analyses.
    significance_threshold : float, default=0.0
        Threshold for determining statistical significance.
        An interval is considered significant if its credible interval
        does not include this threshold value.

    Returns
    -------
    pd.DataFrame
        Summary DataFrame with columns:

        - 'interval' : str
            String representation of the interval (e.g., "Days 1-7")
        - 'start_day' : int
            Start day of the interval
        - 'end_day' : int
            End day of the interval
        - 'days' : int
            Number of days in the interval
        - 'estimate' : float
            Cumulative treatment effect estimate
        - 'precision' : float
            Half-width of credible interval
        - 'lower' : float
            Lower bound of credible interval
        - 'upper' : float
            Upper bound of credible interval
        - 'significant' : bool
            Whether the effect is statistically significant
        - 'avg_daily_effect' : float
            Average daily effect (estimate / days)
        - 'ci_level' : float
            Credible interval level used

    Notes
    -----
    Statistical significance is determined by whether the credible interval
    excludes the significance threshold. This provides a conservative test
    of treatment effect significance.

    The average daily effect is calculated as the total interval effect
    divided by the number of days, providing a normalized comparison
    metric across intervals of different lengths.

    Examples
    --------
    Create summary for weekly analysis:

    >>> intervals = [(1, 7), (8, 14), (1, 14)]
    >>> summary = create_subinterval_summary(
    ...     tbr_results, tbr_summary, intervals, ci_level=0.80
    ... )
    >>> print(summary[['interval', 'estimate', 'significant']])

    Analyze with custom significance threshold:

    >>> summary = create_subinterval_summary(
    ...     tbr_results, tbr_summary, intervals,
    ...     significance_threshold=10.0  # Effect must be > 10
    ... )
    >>> significant_intervals = summary[summary['significant']]
    >>> print(f"Significant intervals: {len(significant_intervals)}")

    Compare average daily effects:

    >>> summary = create_subinterval_summary(
    ...     tbr_results, tbr_summary, [(1, 3), (1, 7), (1, 14)]
    ... )
    >>> print(summary[['interval', 'avg_daily_effect']].sort_values('avg_daily_effect'))
    """
    # Analyze all intervals
    results = analyze_multiple_subintervals(
        tbr_df=tbr_df,
        tbr_summary=tbr_summary,
        intervals=intervals,
        ci_level=ci_level,
    )

    # Create summary DataFrame
    summary_data = []
    for _i, ((start_day, end_day), result) in enumerate(zip(intervals, results)):
        days = end_day - start_day + 1

        # Check significance (CI excludes threshold)
        significant = (
            result["lower"] > significance_threshold
            or result["upper"] < significance_threshold
        )

        summary_data.append(
            {
                "interval": f"Days {start_day}-{end_day}",
                "start_day": start_day,
                "end_day": end_day,
                "days": days,
                "estimate": result["estimate"],
                "precision": result["precision"],
                "lower": result["lower"],
                "upper": result["upper"],
                "significant": significant,
                "avg_daily_effect": result["estimate"] / days,
                "ci_level": ci_level,
            }
        )

    return pd.DataFrame(summary_data)


def validate_subinterval_parameters(
    tbr_df: pd.DataFrame,
    tbr_summary: pd.DataFrame,
    start_day: int,
    end_day: int,
    ci_level: float,
) -> None:
    """
    Validate parameters for subinterval analysis.

    This function performs comprehensive validation of input parameters for
    subinterval analysis, ensuring that all inputs are valid and consistent
    before performing the analysis. It provides clear error messages for
    invalid inputs.

    Parameters
    ----------
    tbr_df : pd.DataFrame
        TBR daily output DataFrame to validate.
    tbr_summary : pd.DataFrame
        TBR summary DataFrame to validate.
    start_day : int
        Start day of subinterval to validate.
    end_day : int
        End day of subinterval to validate.
    ci_level : float
        Credible interval level to validate.

    Raises
    ------
    ValueError
        If any parameter is invalid, with specific error message describing
        the validation failure.
    TypeError
        If parameters have incorrect types.

    Notes
    -----
    This function is called internally by other subinterval analysis functions
    but can also be used directly for parameter validation before analysis.

    The validation checks include:
    - DataFrame structure and required columns
    - Day range validity and logical consistency
    - Credibility level bounds
    - Test period data availability

    Examples
    --------
    Validate parameters before analysis:

    >>> try:
    ...     validate_subinterval_parameters(
    ...         tbr_results, tbr_summary, start_day=5, end_day=10, ci_level=0.80
    ...     )
    ...     print("Parameters are valid")
    ... except ValueError as e:
    ...     print(f"Validation error: {e}")
    """
    # Validate DataFrame types
    if not isinstance(tbr_df, pd.DataFrame):
        raise TypeError("tbr_df must be a pandas DataFrame")

    if not isinstance(tbr_summary, pd.DataFrame):
        raise TypeError("tbr_summary must be a pandas DataFrame")

    # Validate DataFrame structure
    required_tbr_cols = ["y", "pred", "period", "estsd"]
    missing_tbr_cols = [col for col in required_tbr_cols if col not in tbr_df.columns]
    if missing_tbr_cols:
        raise ValueError(f"tbr_df missing required columns: {missing_tbr_cols}")

    required_summary_cols = ["sigma", "t_dist_df"]
    missing_summary_cols = [
        col for col in required_summary_cols if col not in tbr_summary.columns
    ]
    if missing_summary_cols:
        raise ValueError(
            f"tbr_summary missing required columns: {missing_summary_cols}"
        )

    # Validate test period data exists
    test_data = tbr_df[tbr_df["period"] == 1]
    if test_data.empty:
        raise ValueError("No test period data found (period == 1)")

    # Validate day parameters
    if not isinstance(start_day, int) or not isinstance(end_day, int):
        raise TypeError("start_day and end_day must be integers")

    if start_day < 1:
        raise ValueError(f"start_day must be >= 1, got: {start_day}")

    if end_day < start_day:
        raise ValueError(f"end_day ({end_day}) must be >= start_day ({start_day})")

    max_test_day = len(test_data)
    if end_day > max_test_day:
        raise ValueError(
            f"end_day ({end_day}) exceeds available test days ({max_test_day})"
        )

    # Validate credibility level
    if not isinstance(ci_level, (int, float)):
        raise TypeError("ci_level must be a number")

    if not (0 < ci_level < 1):
        raise ValueError(f"ci_level must be between 0 and 1, got: {ci_level}")
