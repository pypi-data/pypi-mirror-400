"""
High-level performance diagnostics for TBR analysis workflows.

This module provides TBR-specific performance analysis tools that integrate
with the core performance diagnostics framework. It offers specialized
performance analysis for TBR workflows, including data size optimization,
computational bottleneck identification, and efficiency recommendations
tailored to time-based regression analysis.

The module includes:
- TBR workflow performance analysis
- Data size optimization recommendations
- Computational bottleneck identification for TBR operations
- Performance comparison between different TBR configurations
- Efficiency metrics specific to regression and prediction operations
- Integration with existing TBR diagnostic framework

Examples
--------
>>> from tbr.analysis.performance import TBRPerformanceAnalyzer
>>>
>>> # Analyze TBR workflow performance
>>> analyzer = TBRPerformanceAnalyzer()
>>> performance_report = analyzer.analyze_tbr_performance(
...     data=data,
...     time_col='date',
...     control_col='control',
...     test_col='test',
...     pretest_start='2023-01-01',
...     test_start='2023-02-15',
...     test_end='2023-03-01'
... )
>>>
>>> # Get optimization recommendations
>>> recommendations = analyzer.get_optimization_recommendations(performance_report)
>>> print(recommendations.summary())
"""

from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from tbr.functional.tbr_functions import perform_tbr_analysis
from tbr.utils.performance import (
    EfficiencyMetrics,
    PerformanceMonitor,
    PerformanceProfiler,
)


class TBRPerformanceAnalyzer:
    """
    Specialized performance analyzer for TBR analysis workflows.

    Provides comprehensive performance analysis tailored specifically for
    time-based regression workflows, including data size optimization,
    computational bottleneck identification, and efficiency recommendations.

    Examples
    --------
    >>> analyzer = TBRPerformanceAnalyzer()
    >>>
    >>> # Analyze complete TBR workflow performance
    >>> report = analyzer.analyze_tbr_performance(
    ...     data=data, time_col='date', control_col='control', test_col='test',
    ...     pretest_start='2023-01-01', test_start='2023-02-15', test_end='2023-03-01'
    ... )
    >>>
    >>> # Get detailed recommendations
    >>> recommendations = analyzer.get_optimization_recommendations(report)
    >>> analyzer.print_performance_summary(report)
    """

    def __init__(self) -> None:
        """Initialize the TBR performance analyzer."""
        self.profiler = PerformanceProfiler()
        self.efficiency_metrics = EfficiencyMetrics()
        self.monitor = PerformanceMonitor()
        self.baseline_metrics: Dict[str, Any] = {}

    def analyze_tbr_performance(
        self,
        data: pd.DataFrame,
        time_col: str,
        control_col: str,
        test_col: str,
        pretest_start: Union[pd.Timestamp, int, float],
        test_start: Union[pd.Timestamp, int, float],
        test_end: Union[pd.Timestamp, int, float],
        level: float = 0.80,
        threshold: float = 0.0,
        test_end_inclusive: bool = False,
        enable_monitoring: bool = True,
    ) -> Dict[str, Any]:
        """
        Analyze performance of a complete TBR analysis workflow.

        Parameters
        ----------
        data : pd.DataFrame
            Time series data for TBR analysis
        time_col : str
            Name of time column
        control_col : str
            Name of control column
        test_col : str
            Name of test column
        pretest_start : Union[pd.Timestamp, int, float]
            Start of pretest period
        test_start : Union[pd.Timestamp, int, float]
            Start of test period
        test_end : Union[pd.Timestamp, int, float]
            End of test period
        level : float, default 0.80
            Credibility level for analysis
        threshold : float, default 0.0
            Threshold for significance testing
        test_end_inclusive : bool, default False
            Whether test_end is inclusive
        enable_monitoring : bool, default True
            Whether to enable real-time monitoring

        Returns
        -------
        Dict[str, Any]
            Comprehensive performance analysis report
        """
        # Start monitoring if enabled
        if enable_monitoring:
            self.monitor.start_monitoring()

        # Profile the complete TBR workflow
        with self.profiler.profile_context("tbr_complete_workflow") as workflow_metrics:
            # Profile data validation phase
            with self.profiler.profile_context("data_validation"):
                data_size = len(data)
                data_memory = data.memory_usage(deep=True).sum() / 1024 / 1024  # MB

            # Profile TBR analysis execution
            with self.profiler.profile_context("tbr_analysis_execution"):
                results = perform_tbr_analysis(
                    data=data,
                    time_col=time_col,
                    control_col=control_col,
                    test_col=test_col,
                    pretest_start=pretest_start,
                    test_start=test_start,
                    test_end=test_end,
                    level=level,
                    threshold=threshold,
                    test_end_inclusive=test_end_inclusive,
                )

            # Profile results processing
            with self.profiler.profile_context("results_processing"):
                tbr_results = results.tbr_dataframe()
                tbr_summaries = results.summary()
                results_size = len(tbr_results) + len(tbr_summaries)
                results_memory = (
                    (
                        tbr_results.memory_usage(deep=True).sum()
                        + tbr_summaries.memory_usage(deep=True).sum()
                    )
                    / 1024
                    / 1024
                )  # MB

        # Stop monitoring
        if enable_monitoring:
            self.monitor.stop_monitoring()
            monitoring_report = self.monitor.get_monitoring_report()
        else:
            monitoring_report = None

        # Get all performance metrics
        all_metrics = self.profiler.get_metrics()

        # Analyze efficiency
        efficiency_report = self.efficiency_metrics.analyze_workflow_efficiency(
            data_size=data_size,
            operation_metrics=all_metrics,  # type: ignore[arg-type]
            operation_name="tbr_workflow",
        )

        # Compile comprehensive report
        performance_report = {
            "workflow_metrics": workflow_metrics,
            "operation_metrics": all_metrics,
            "efficiency_report": efficiency_report,
            "monitoring_report": monitoring_report,
            "data_characteristics": {
                "data_size": data_size,
                "data_memory_mb": data_memory,
                "results_size": results_size,
                "results_memory_mb": results_memory,
                "pretest_period_length": self._calculate_period_length(
                    data, time_col, pretest_start, test_start
                ),
                "test_period_length": self._calculate_period_length(
                    data, time_col, test_start, test_end, test_end_inclusive
                ),
            },
            "tbr_results": tbr_results,
            "tbr_summaries": tbr_summaries,
        }

        return performance_report

    def analyze_data_size_scaling(
        self,
        base_data: pd.DataFrame,
        time_col: str,
        control_col: str,
        test_col: str,
        pretest_start: Union[pd.Timestamp, int, float],
        test_start: Union[pd.Timestamp, int, float],
        test_end: Union[pd.Timestamp, int, float],
        size_multipliers: Optional[List[float]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Analyze how TBR performance scales with different data sizes.

        Parameters
        ----------
        base_data : pd.DataFrame
            Base dataset to scale
        time_col : str
            Name of time column
        control_col : str
            Name of control column
        test_col : str
            Name of test column
        pretest_start : Union[pd.Timestamp, int, float]
            Start of pretest period
        test_start : Union[pd.Timestamp, int, float]
            Start of test period
        test_end : Union[pd.Timestamp, int, float]
            End of test period
        size_multipliers : List[float], default [0.5, 1.0, 2.0, 5.0]
            Multipliers to apply to base data size
        **kwargs : dict
            Additional arguments for TBR analysis

        Returns
        -------
        Dict[str, Any]
            Scaling analysis results with performance characteristics
        """
        if size_multipliers is None:
            size_multipliers = [0.5, 1.0, 2.0, 5.0]

        scaling_results = []

        for multiplier in size_multipliers:
            # Create scaled dataset
            target_size = int(len(base_data) * multiplier)
            if target_size > len(base_data):
                # Upsample by replicating data with noise
                scaled_data = self._upsample_data(
                    base_data, target_size, control_col, test_col
                )
            else:
                # Downsample by random sampling
                scaled_data = base_data.sample(
                    n=target_size, random_state=42
                ).sort_values(time_col)

            # Analyze performance for this data size
            try:
                performance_report = self.analyze_tbr_performance(
                    data=scaled_data,
                    time_col=time_col,
                    control_col=control_col,
                    test_col=test_col,
                    pretest_start=pretest_start,
                    test_start=test_start,
                    test_end=test_end,
                    enable_monitoring=False,  # Disable monitoring for scaling tests
                    **kwargs,
                )

                scaling_results.append(
                    {
                        "size_multiplier": multiplier,
                        "data_size": target_size,
                        "total_duration": performance_report[
                            "workflow_metrics"
                        ].duration,
                        "memory_peak_mb": performance_report[
                            "workflow_metrics"
                        ].memory_peak
                        or 0,
                        "efficiency_score": performance_report[
                            "efficiency_report"
                        ].efficiency_score,
                        "success": True,
                    }
                )
            except Exception as e:
                scaling_results.append(
                    {
                        "size_multiplier": multiplier,
                        "data_size": target_size,
                        "error": str(e),
                        "success": False,
                    }
                )

        # Analyze scaling patterns
        successful_results = [r for r in scaling_results if r["success"]]
        if len(successful_results) >= 2:
            scaling_analysis = self._analyze_scaling_patterns(successful_results)
        else:
            scaling_analysis = {
                "error": "Insufficient successful runs for scaling analysis"
            }

        return {
            "scaling_results": scaling_results,
            "scaling_analysis": scaling_analysis,
            "recommendations": self._generate_scaling_recommendations(scaling_results),
        }

    def compare_tbr_configurations(
        self,
        data: pd.DataFrame,
        configurations: List[Dict[str, Any]],
        base_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Compare performance across different TBR analysis configurations.

        Parameters
        ----------
        data : pd.DataFrame
            Dataset for comparison
        configurations : List[Dict[str, Any]]
            List of TBR configuration dictionaries to compare
        base_config : Dict[str, Any]
            Base configuration for comparison

        Returns
        -------
        Dict[str, Any]
            Configuration comparison results with performance metrics
        """
        comparison_results = []

        # Analyze base configuration
        base_performance = self.analyze_tbr_performance(data=data, **base_config)
        base_duration = base_performance["workflow_metrics"].duration

        comparison_results.append(
            {
                "config_name": "baseline",
                "config": base_config,
                "performance": base_performance,
                "duration_ratio": 1.0,
                "efficiency_ratio": 1.0,
            }
        )

        # Analyze each configuration
        for i, config in enumerate(configurations):
            try:
                config_performance = self.analyze_tbr_performance(data=data, **config)
                config_duration = config_performance["workflow_metrics"].duration

                comparison_results.append(
                    {
                        "config_name": f"config_{i+1}",
                        "config": config,
                        "performance": config_performance,
                        "duration_ratio": config_duration / base_duration,
                        "efficiency_ratio": (
                            config_performance["efficiency_report"].efficiency_score
                            / base_performance["efficiency_report"].efficiency_score
                        ),
                    }
                )
            except Exception as e:
                comparison_results.append(
                    {
                        "config_name": f"config_{i+1}",
                        "config": config,
                        "error": str(e),
                        "success": False,
                    }
                )

        # Generate comparison summary
        successful_configs = [r for r in comparison_results if "error" not in r]
        if len(successful_configs) > 1:
            best_config = min(successful_configs, key=lambda x: float(x["duration_ratio"]))  # type: ignore[arg-type]
            worst_config = max(successful_configs, key=lambda x: float(x["duration_ratio"]))  # type: ignore[arg-type]

            # Type cast the dict values to float (we know they exist from min/max keys)
            best_ratio = float(best_config["duration_ratio"])  # type: ignore[arg-type]
            worst_ratio = float(worst_config["duration_ratio"])  # type: ignore[arg-type]

            comparison_summary = {
                "best_config": best_config["config_name"],
                "best_speedup": 1.0 / best_ratio,
                "worst_config": worst_config["config_name"],
                "worst_slowdown": worst_ratio,
                "performance_range": worst_ratio / best_ratio,
            }
        else:
            comparison_summary = {
                "error": "Insufficient successful configurations for comparison"
            }

        return {
            "comparison_results": comparison_results,
            "comparison_summary": comparison_summary,
            "recommendations": self._generate_configuration_recommendations(
                comparison_results
            ),
        }

    def get_optimization_recommendations(
        self, performance_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate optimization recommendations based on performance analysis.

        Parameters
        ----------
        performance_report : Dict[str, Any]
            Performance report from analyze_tbr_performance

        Returns
        -------
        Dict[str, Any]
            Optimization recommendations with specific actions
        """
        recommendations: Dict[str, List[str]] = {
            "priority_actions": [],
            "data_optimization": [],
            "computational_optimization": [],
            "memory_optimization": [],
            "general_recommendations": [],
        }

        # Extract key metrics
        workflow_metrics = performance_report["workflow_metrics"]
        efficiency_report = performance_report["efficiency_report"]
        data_chars = performance_report["data_characteristics"]

        # Priority actions based on efficiency score
        if efficiency_report.efficiency_score < 3.0:
            recommendations["priority_actions"].append(
                "Critical: Overall efficiency is very low. Focus on major optimizations."
            )
        elif efficiency_report.efficiency_score < 6.0:
            recommendations["priority_actions"].append(
                "Important: Efficiency can be significantly improved."
            )

        # Data optimization recommendations
        if data_chars["data_size"] > 100000:
            recommendations["data_optimization"].append(
                "Consider data sampling or chunked processing for large datasets"
            )

        if data_chars["data_memory_mb"] > 1000:
            recommendations["data_optimization"].append(
                "Use memory-efficient data types (e.g., category for strings, float32 for numbers)"
            )

        # Computational optimization
        total_duration = workflow_metrics.duration
        if total_duration > 60:  # More than 1 minute
            recommendations["computational_optimization"].append(
                "Analysis is taking significant time. Consider parallel processing or algorithm optimization."
            )

        # Memory optimization
        peak_memory = workflow_metrics.memory_peak or 0
        if peak_memory > 2000:  # More than 2GB
            recommendations["memory_optimization"].append(
                "High memory usage detected. Consider processing data in chunks."
            )

        # Bottleneck-specific recommendations
        for bottleneck in efficiency_report.bottlenecks:
            if "regression" in bottleneck.lower():
                recommendations["computational_optimization"].append(
                    "Regression fitting is a bottleneck. Consider using optimized BLAS libraries."
                )
            elif "validation" in bottleneck.lower():
                recommendations["data_optimization"].append(
                    "Data validation is slow. Consider pre-validating data or caching validation results."
                )

        # General recommendations from efficiency report
        recommendations["general_recommendations"].extend(
            efficiency_report.recommendations
        )

        return recommendations

    def set_performance_baseline(
        self, baseline_name: str, performance_report: Dict[str, Any]
    ) -> None:
        """
        Set a performance baseline for future comparisons.

        Parameters
        ----------
        baseline_name : str
            Name for the baseline
        performance_report : Dict[str, Any]
            Performance report to use as baseline
        """
        self.baseline_metrics[baseline_name] = {
            "workflow_duration": performance_report["workflow_metrics"].duration,
            "efficiency_score": performance_report[
                "efficiency_report"
            ].efficiency_score,
            "data_size": performance_report["data_characteristics"]["data_size"],
            "memory_peak": performance_report["workflow_metrics"].memory_peak or 0,
        }

        # Set baseline in efficiency metrics
        self.efficiency_metrics.set_baseline(
            baseline_name, performance_report["operation_metrics"]
        )

    def compare_to_baseline(
        self, performance_report: Dict[str, Any], baseline_name: str
    ) -> Dict[str, Any]:
        """
        Compare current performance to a stored baseline.

        Parameters
        ----------
        performance_report : Dict[str, Any]
            Current performance report
        baseline_name : str
            Name of baseline to compare against

        Returns
        -------
        Dict[str, Any]
            Comparison results with regression/improvement analysis
        """
        if baseline_name not in self.baseline_metrics:
            return {"error": f'Baseline "{baseline_name}" not found'}

        baseline = self.baseline_metrics[baseline_name]
        current = {
            "workflow_duration": performance_report["workflow_metrics"].duration,
            "efficiency_score": performance_report[
                "efficiency_report"
            ].efficiency_score,
            "data_size": performance_report["data_characteristics"]["data_size"],
            "memory_peak": performance_report["workflow_metrics"].memory_peak or 0,
        }

        # Calculate ratios (accounting for different data sizes)
        size_ratio = current["data_size"] / baseline["data_size"]
        duration_ratio = current["workflow_duration"] / baseline["workflow_duration"]
        efficiency_ratio = current["efficiency_score"] / baseline["efficiency_score"]
        memory_ratio = (
            current["memory_peak"] / baseline["memory_peak"]
            if baseline["memory_peak"] > 0
            else 1.0
        )

        # Normalize for data size (assuming linear scaling)
        normalized_duration_ratio = duration_ratio / size_ratio
        normalized_memory_ratio = memory_ratio / size_ratio

        comparison = {
            "baseline_name": baseline_name,
            "size_ratio": size_ratio,
            "duration_ratio": duration_ratio,
            "normalized_duration_ratio": normalized_duration_ratio,
            "efficiency_ratio": efficiency_ratio,
            "memory_ratio": memory_ratio,
            "normalized_memory_ratio": normalized_memory_ratio,
            "performance_regression": normalized_duration_ratio > 1.1,  # 10% slower
            "performance_improvement": normalized_duration_ratio < 0.9,  # 10% faster
            "efficiency_regression": efficiency_ratio < 0.9,
            "efficiency_improvement": efficiency_ratio > 1.1,
        }

        return comparison

    def print_performance_summary(
        self, performance_report: Dict[str, Any], include_recommendations: bool = True
    ) -> None:
        """
        Print a formatted summary of performance analysis results.

        Parameters
        ----------
        performance_report : Dict[str, Any]
            Performance report to summarize
        include_recommendations : bool, default True
            Whether to include optimization recommendations
        """
        print("\n" + "=" * 70)
        print("TBR PERFORMANCE ANALYSIS SUMMARY")
        print("=" * 70)

        # Workflow overview
        workflow_metrics = performance_report["workflow_metrics"]
        data_chars = performance_report["data_characteristics"]
        efficiency_report = performance_report["efficiency_report"]

        print("\nWorkflow Performance:")
        print(f"  Total Duration: {workflow_metrics.duration:.3f} seconds")
        print(f"  Data Size: {data_chars['data_size']:,} rows")
        print(f"  Data Memory: {data_chars['data_memory_mb']:.1f} MB")

        if workflow_metrics.memory_peak:
            print(f"  Peak Memory: {workflow_metrics.memory_peak:.1f} MB")

        print("\nEfficiency Analysis:")
        print(f"  Efficiency Score: {efficiency_report.efficiency_score:.1f}/10.0")
        print(
            f"  Computational Complexity: {efficiency_report.computational_complexity}"
        )

        if efficiency_report.bottlenecks:
            print(f"  Bottlenecks: {', '.join(efficiency_report.bottlenecks[:3])}")

        # Monitoring report if available
        monitoring_report = performance_report.get("monitoring_report")
        if monitoring_report and "error" not in monitoring_report:
            print("\nResource Utilization:")
            print(f"  Average CPU: {monitoring_report['cpu_stats']['mean']:.1f}%")
            print(f"  Peak CPU: {monitoring_report['cpu_stats']['max']:.1f}%")
            print(
                f"  Average Memory: {monitoring_report['memory_stats']['mean_mb']:.1f} MB"
            )
            print(
                f"  Peak Memory: {monitoring_report['memory_stats']['max_mb']:.1f} MB"
            )

            if monitoring_report["alerts"]:
                print(f"  Alerts: {', '.join(monitoring_report['alerts'])}")

        # Recommendations
        if include_recommendations:
            recommendations = self.get_optimization_recommendations(performance_report)

            if recommendations["priority_actions"]:
                print("\nPriority Actions:")
                for action in recommendations["priority_actions"]:
                    print(f"  • {action}")

            if recommendations["computational_optimization"]:
                print("\nComputational Optimizations:")
                for opt in recommendations["computational_optimization"][:3]:
                    print(f"  • {opt}")

            if recommendations["memory_optimization"]:
                print("\nMemory Optimizations:")
                for opt in recommendations["memory_optimization"][:3]:
                    print(f"  • {opt}")

        print("=" * 70)

    def _calculate_period_length(
        self,
        data: pd.DataFrame,
        time_col: str,
        start: Union[pd.Timestamp, int, float],
        end: Union[pd.Timestamp, int, float],
        inclusive: bool = False,
    ) -> int:
        """Calculate the length of a time period in the data."""
        if inclusive:
            period_data = data[(data[time_col] >= start) & (data[time_col] <= end)]
        else:
            period_data = data[(data[time_col] >= start) & (data[time_col] < end)]
        return len(period_data)

    def _upsample_data(
        self,
        data: pd.DataFrame,
        target_size: int,
        control_col: str,
        test_col: str,
        noise_factor: float = 0.01,
    ) -> pd.DataFrame:
        """Upsample data by replication with added noise."""
        if target_size <= len(data):
            return data

        # Calculate how many times to replicate
        replication_factor = int(np.ceil(target_size / len(data)))

        # Replicate data
        replicated_data = pd.concat([data] * replication_factor, ignore_index=True)

        # Add small amount of noise to avoid perfect duplicates
        if noise_factor > 0:
            control_std = data[control_col].std()
            test_std = data[test_col].std()

            replicated_data[control_col] += np.random.normal(
                0, control_std * noise_factor, len(replicated_data)
            )
            replicated_data[test_col] += np.random.normal(
                0, test_std * noise_factor, len(replicated_data)
            )

        # Trim to exact target size
        return replicated_data.iloc[:target_size].reset_index(drop=True)

    def _analyze_scaling_patterns(
        self, scaling_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze scaling patterns from scaling test results."""
        sizes = np.array([r["data_size"] for r in scaling_results])
        durations = np.array([r["total_duration"] for r in scaling_results])

        # Calculate scaling efficiency
        if len(sizes) >= 2:
            # Linear fit to estimate complexity
            log_sizes = np.log(sizes)
            log_durations = np.log(durations)

            try:
                slope, intercept = np.polyfit(log_sizes, log_durations, 1)
                r_squared = np.corrcoef(log_sizes, log_durations)[0, 1] ** 2

                # Interpret slope
                if slope < 0.5:
                    complexity_estimate = "Better than linear (very efficient)"
                elif slope < 1.2:
                    complexity_estimate = "Approximately linear (good scaling)"
                elif slope < 2.0:
                    complexity_estimate = (
                        "Between linear and quadratic (moderate scaling)"
                    )
                else:
                    complexity_estimate = "Quadratic or worse (poor scaling)"

                return {
                    "complexity_slope": slope,
                    "complexity_r_squared": r_squared,
                    "complexity_estimate": complexity_estimate,
                    "scaling_efficiency": max(0, 2.0 - slope),  # 0-2 scale
                }
            except Exception:
                return {"error": "Could not fit scaling model"}

        return {"error": "Insufficient data for scaling analysis"}

    def _generate_scaling_recommendations(
        self, scaling_results: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on scaling analysis."""
        recommendations = []

        successful_results = [r for r in scaling_results if r["success"]]
        if len(successful_results) < 2:
            recommendations.append("Insufficient scaling data for recommendations")
            return recommendations

        # Check for performance degradation at larger sizes
        largest_result = max(successful_results, key=lambda x: x["data_size"])
        smallest_result = min(successful_results, key=lambda x: x["data_size"])

        size_ratio = largest_result["data_size"] / smallest_result["data_size"]
        time_ratio = (
            largest_result["total_duration"] / smallest_result["total_duration"]
        )

        if time_ratio > size_ratio * 2:
            recommendations.append(
                "Performance degrades significantly with larger datasets. Consider chunked processing."
            )

        # Check memory scaling
        if (
            "memory_peak_mb" in largest_result
            and largest_result["memory_peak_mb"] > 1000
        ):
            recommendations.append(
                "Memory usage grows substantially with data size. Consider memory optimization."
            )

        # Check efficiency trends
        efficiency_scores = [r.get("efficiency_score", 5.0) for r in successful_results]
        if (
            len(efficiency_scores) >= 2
            and efficiency_scores[-1] < efficiency_scores[0] * 0.8
        ):
            recommendations.append(
                "Efficiency decreases with larger datasets. Review algorithm complexity."
            )

        if not recommendations:
            recommendations.append(
                "Scaling behavior appears reasonable for tested data sizes."
            )

        return recommendations

    def _generate_configuration_recommendations(
        self, comparison_results: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on configuration comparison."""
        recommendations = []

        successful_results = [r for r in comparison_results if "error" not in r]
        if len(successful_results) < 2:
            recommendations.append(
                "Insufficient configuration data for recommendations"
            )
            return recommendations

        # Find best and worst configurations
        best_config = min(successful_results, key=lambda x: x["duration_ratio"])
        worst_config = max(successful_results, key=lambda x: x["duration_ratio"])

        if best_config["duration_ratio"] < 0.8:  # 20% faster than baseline
            recommendations.append(
                f"Configuration '{best_config['config_name']}' shows significant performance improvement."
            )

        if worst_config["duration_ratio"] > 1.5:  # 50% slower than baseline
            recommendations.append(
                f"Avoid configuration '{worst_config['config_name']}' due to poor performance."
            )

        # Analyze configuration parameters if available
        # This could be extended to analyze specific parameter effects

        return recommendations


# Convenience functions for common TBR performance analysis tasks


def quick_performance_check(
    data: pd.DataFrame,
    time_col: str,
    control_col: str,
    test_col: str,
    pretest_start: Union[pd.Timestamp, int, float],
    test_start: Union[pd.Timestamp, int, float],
    test_end: Union[pd.Timestamp, int, float],
    **kwargs: Any,
) -> None:
    """
    Perform a quick performance check of TBR analysis.

    Parameters
    ----------
    data : pd.DataFrame
        Time series data for TBR analysis
    time_col : str
        Name of time column
    control_col : str
        Name of control column
    test_col : str
        Name of test column
    pretest_start : Union[pd.Timestamp, int, float]
        Start of pretest period
    test_start : Union[pd.Timestamp, int, float]
        Start of test period
    test_end : Union[pd.Timestamp, int, float]
        End of test period
    **kwargs : dict
        Additional arguments for TBR analysis
    """
    analyzer = TBRPerformanceAnalyzer()

    print("Running TBR performance analysis...")
    performance_report = analyzer.analyze_tbr_performance(
        data=data,
        time_col=time_col,
        control_col=control_col,
        test_col=test_col,
        pretest_start=pretest_start,
        test_start=test_start,
        test_end=test_end,
        **kwargs,
    )

    analyzer.print_performance_summary(performance_report)


def optimize_tbr_data_size(
    data: pd.DataFrame,
    time_col: str,
    control_col: str,
    test_col: str,
    pretest_start: Union[pd.Timestamp, int, float],
    test_start: Union[pd.Timestamp, int, float],
    test_end: Union[pd.Timestamp, int, float],
    target_duration: float = 30.0,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Find optimal data size for TBR analysis based on target duration.

    Parameters
    ----------
    data : pd.DataFrame
        Time series data for TBR analysis
    time_col : str
        Name of time column
    control_col : str
        Name of control column
    test_col : str
        Name of test column
    pretest_start : Union[pd.Timestamp, int, float]
        Start of pretest period
    test_start : Union[pd.Timestamp, int, float]
        Start of test period
    test_end : Union[pd.Timestamp, int, float]
        End of test period
    target_duration : float, default 30.0
        Target analysis duration in seconds
    **kwargs : dict
        Additional arguments for TBR analysis

    Returns
    -------
    Dict[str, Any]
        Optimization results with recommended data size
    """
    analyzer = TBRPerformanceAnalyzer()

    # Use provided size_multipliers or default ones
    default_size_multipliers = [0.1, 0.25, 0.5, 1.0, 2.0]
    size_multipliers = kwargs.pop("size_multipliers", default_size_multipliers)

    scaling_analysis = analyzer.analyze_data_size_scaling(
        base_data=data,
        time_col=time_col,
        control_col=control_col,
        test_col=test_col,
        pretest_start=pretest_start,
        test_start=test_start,
        test_end=test_end,
        size_multipliers=size_multipliers,
        **kwargs,
    )

    # Find optimal size based on target duration
    successful_results = [
        r for r in scaling_analysis["scaling_results"] if r["success"]
    ]

    if not successful_results:
        return {"error": "No successful scaling tests"}

    # Find size closest to target duration
    best_result = min(
        successful_results, key=lambda x: abs(x["total_duration"] - target_duration)
    )

    return {
        "recommended_size": best_result["data_size"],
        "recommended_multiplier": best_result["size_multiplier"],
        "expected_duration": best_result["total_duration"],
        "scaling_analysis": scaling_analysis,
    }
