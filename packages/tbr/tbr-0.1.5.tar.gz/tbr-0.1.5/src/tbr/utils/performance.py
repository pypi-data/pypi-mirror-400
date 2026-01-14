"""
Performance diagnostics and computational efficiency metrics for TBR analysis.

This module provides comprehensive performance monitoring, profiling, and
efficiency metrics for TBR analysis workflows. It enables users to monitor
computational performance, identify bottlenecks, and optimize their analysis
pipelines for better efficiency.

The module includes:
- Performance profiling for individual functions and complete workflows
- Memory usage monitoring and optimization recommendations
- Computational complexity analysis and scaling behavior
- Performance regression detection and alerting
- Efficiency benchmarking against baseline implementations
- Resource utilization monitoring (CPU, memory, I/O)

Examples
--------
>>> from tbr.core.performance import PerformanceProfiler, EfficiencyMetrics
>>>
>>> # Profile a TBR analysis workflow
>>> profiler = PerformanceProfiler()
>>> with profiler.profile_context("tbr_analysis"):
...     # Run TBR analysis
...     results = perform_tbr_analysis(data, ...)
>>>
>>> # Get performance metrics
>>> metrics = profiler.get_metrics()
>>> print(f"Analysis took {metrics['tbr_analysis']['duration']:.3f} seconds")
>>>
>>> # Analyze computational efficiency
>>> efficiency = EfficiencyMetrics()
>>> report = efficiency.analyze_workflow_efficiency(data, results)
>>> print(report.summary())
"""

import gc
import os
import time
import tracemalloc
import warnings
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import psutil


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    operation_name: str
    duration: float
    memory_peak: Optional[float] = None
    memory_current: Optional[float] = None
    cpu_percent: Optional[float] = None
    function_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EfficiencyReport:
    """Container for efficiency analysis results."""

    operation_name: str
    data_size: int
    computational_complexity: str
    efficiency_score: float
    bottlenecks: List[str]
    recommendations: List[str]
    baseline_comparison: Optional[Dict[str, float]] = None
    scaling_analysis: Optional[Dict[str, Any]] = None

    def summary(self) -> str:
        """Generate a human-readable summary of the efficiency report."""
        lines = [
            f"Performance Analysis: {self.operation_name}",
            f"Data Size: {self.data_size:,} elements",
            f"Efficiency Score: {self.efficiency_score:.2f}/10.0",
            f"Computational Complexity: {self.computational_complexity}",
        ]

        if self.bottlenecks:
            lines.append(f"Bottlenecks: {', '.join(self.bottlenecks)}")

        if self.recommendations:
            lines.append("Recommendations:")
            for rec in self.recommendations:
                lines.append(f"  - {rec}")

        return "\n".join(lines)


class PerformanceProfiler:
    """
    Advanced performance profiler for TBR analysis workflows.

    Provides comprehensive performance monitoring including timing, memory usage,
    CPU utilization, and function call statistics. Supports both context manager
    and decorator patterns for flexible profiling.

    Examples
    --------
    >>> profiler = PerformanceProfiler()
    >>>
    >>> # Context manager usage
    >>> with profiler.profile_context("regression_fitting"):
    ...     model = fit_regression_model(data, "control", "test")
    >>>
    >>> # Decorator usage
    >>> @profiler.profile_function
    >>> def my_analysis_function(data):
    ...     return perform_tbr_analysis(data, ...)
    >>>
    >>> # Get detailed metrics
    >>> metrics = profiler.get_metrics()
    >>> profiler.print_summary()
    """

    def __init__(
        self, enable_memory_tracking: bool = True, enable_cpu_tracking: bool = True
    ):
        """
        Initialize the performance profiler.

        Parameters
        ----------
        enable_memory_tracking : bool, default True
            Whether to track memory usage during profiling
        enable_cpu_tracking : bool, default True
            Whether to track CPU utilization during profiling
        """
        self.enable_memory_tracking = enable_memory_tracking
        self.enable_cpu_tracking = enable_cpu_tracking
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self._active_profiles: Dict[str, Dict[str, Any]] = {}

        # Initialize system monitoring
        if self.enable_cpu_tracking:
            try:
                self.process = psutil.Process(os.getpid())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self.enable_cpu_tracking = False
                warnings.warn(
                    "CPU tracking disabled due to system limitations", stacklevel=2
                )

    @contextmanager
    def profile_context(
        self, operation_name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Generator[PerformanceMetrics, None, None]:
        """
        Context manager for profiling code blocks.

        Parameters
        ----------
        operation_name : str
            Name identifier for the operation being profiled
        metadata : dict, optional
            Additional metadata to store with the performance metrics

        Yields
        ------
        PerformanceMetrics
            The metrics object being populated during profiling
        """
        # Initialize metrics
        metrics = PerformanceMetrics(
            operation_name=operation_name, duration=0.0, metadata=metadata or {}
        )

        # Start memory tracking
        if self.enable_memory_tracking:
            tracemalloc.start()
            gc.collect()  # Clean slate for memory measurement

        # Record start state
        start_time = time.perf_counter()
        metrics.start_time = start_time

        if self.enable_cpu_tracking and hasattr(self, "process"):
            try:
                cpu_start = self.process.cpu_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                cpu_start = None
        else:
            cpu_start = None

        try:
            yield metrics
        finally:
            # Record end state
            end_time = time.perf_counter()
            metrics.end_time = end_time
            metrics.duration = end_time - start_time

            # Memory tracking
            if self.enable_memory_tracking:
                try:
                    current, peak = tracemalloc.get_traced_memory()
                    metrics.memory_current = current / 1024 / 1024  # MB
                    metrics.memory_peak = peak / 1024 / 1024  # MB
                    tracemalloc.stop()
                except Exception:
                    # Graceful fallback if memory tracking fails
                    pass

            # CPU tracking
            if cpu_start is not None:
                try:
                    cpu_end = self.process.cpu_percent()
                    metrics.cpu_percent = (cpu_start + cpu_end) / 2
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Store metrics
            self.metrics[operation_name] = metrics

    def profile_function(self, func: Callable) -> Callable:
        """
        Decorate a function to enable execution profiling.

        Parameters
        ----------
        func : Callable
            Function to be profiled

        Returns
        -------
        Callable
            Wrapped function with profiling enabled
        """

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            operation_name = f"{func.__module__}.{func.__name__}"
            with self.profile_context(operation_name) as metrics:
                metrics.function_calls = 1
                result = func(*args, **kwargs)
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    def benchmark_function(
        self,
        func: Callable,
        *args: Any,
        n_runs: int = 5,
        warmup_runs: int = 2,
        operation_name: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, float]:
        """
        Benchmark a function with statistical analysis.

        Parameters
        ----------
        func : Callable
            Function to benchmark
        *args : tuple
            Positional arguments for the function
        n_runs : int, default 5
            Number of benchmark runs for statistical analysis
        warmup_runs : int, default 2
            Number of warmup runs (excluded from statistics)
        operation_name : str, optional
            Name for the operation (defaults to function name)
        **kwargs : dict
            Keyword arguments for the function

        Returns
        -------
        Dict[str, float]
            Statistical summary of benchmark results
        """
        if operation_name is None:
            operation_name = f"{func.__module__}.{func.__name__}"

        # Warmup runs
        for _ in range(warmup_runs):
            func(*args, **kwargs)

        # Benchmark runs
        times = []
        memory_peaks = []

        for run in range(n_runs):
            with self.profile_context(f"{operation_name}_run_{run}") as metrics:
                result = func(*args, **kwargs)

            times.append(metrics.duration)
            if metrics.memory_peak is not None:
                memory_peaks.append(metrics.memory_peak)

        # Statistical analysis
        times_array = np.array(times)
        stats = {
            "mean_time": float(np.mean(times_array)),
            "std_time": float(np.std(times_array)),
            "min_time": float(np.min(times_array)),
            "max_time": float(np.max(times_array)),
            "median_time": float(np.median(times_array)),
            "n_runs": n_runs,
            "result": result,
        }

        if memory_peaks:
            memory_array = np.array(memory_peaks)
            stats.update(
                {
                    "mean_memory": float(np.mean(memory_array)),
                    "max_memory": float(np.max(memory_array)),
                    "min_memory": float(np.min(memory_array)),
                }
            )

        return stats

    def get_metrics(
        self, operation_name: Optional[str] = None
    ) -> Union[Optional[PerformanceMetrics], Dict[str, PerformanceMetrics]]:
        """
        Retrieve performance metrics.

        Parameters
        ----------
        operation_name : str, optional
            Specific operation to retrieve metrics for. If None, returns all metrics.

        Returns
        -------
        PerformanceMetrics or Dict[str, PerformanceMetrics]
            Performance metrics for the specified operation or all operations
        """
        if operation_name is not None:
            return self.metrics.get(operation_name)
        return self.metrics.copy()

    def clear_metrics(self) -> None:
        """Clear all stored performance metrics."""
        self.metrics.clear()

    def print_summary(self, operation_name: Optional[str] = None) -> None:
        """
        Print a formatted summary of performance metrics.

        Parameters
        ----------
        operation_name : str, optional
            Specific operation to print summary for. If None, prints all operations.
        """
        metrics_dict: Dict[str, Optional[PerformanceMetrics]]
        if operation_name is not None:
            metrics_dict = {operation_name: self.metrics.get(operation_name)}
        else:
            metrics_dict = dict(self.metrics.items())

        print("\n" + "=" * 60)
        print("PERFORMANCE PROFILING SUMMARY")
        print("=" * 60)

        for name, metrics in metrics_dict.items():
            if metrics is None:
                print(f"\nNo metrics found for operation: {name}")
                continue

            print(f"\nOperation: {name}")
            print(f"Duration: {metrics.duration:.4f} seconds")

            if metrics.memory_peak is not None:
                print(f"Peak Memory: {metrics.memory_peak:.2f} MB")
            if metrics.memory_current is not None:
                print(f"Current Memory: {metrics.memory_current:.2f} MB")
            if metrics.cpu_percent is not None:
                print(f"CPU Usage: {metrics.cpu_percent:.1f}%")
            if metrics.function_calls > 0:
                print(f"Function Calls: {metrics.function_calls}")

            if metrics.metadata:
                print("Metadata:")
                for key, value in metrics.metadata.items():
                    print(f"  {key}: {value}")

        print("=" * 60)


class EfficiencyMetrics:
    """
    Computational efficiency analyzer for TBR workflows.

    Analyzes computational complexity, identifies performance bottlenecks,
    and provides optimization recommendations for TBR analysis workflows.

    Examples
    --------
    >>> efficiency = EfficiencyMetrics()
    >>>
    >>> # Analyze workflow efficiency
    >>> report = efficiency.analyze_workflow_efficiency(
    ...     data_size=10000,
    ...     operation_metrics=profiler.get_metrics()
    ... )
    >>>
    >>> # Get scaling analysis
    >>> scaling = efficiency.analyze_scaling_behavior(
    ...     function=fit_regression_model,
    ...     data_sizes=[100, 500, 1000, 5000]
    ... )
    """

    def __init__(self) -> None:
        """Initialize the efficiency metrics analyzer."""
        self.baseline_metrics: Dict[str, Dict[str, float]] = {}
        self.profiler = PerformanceProfiler()

    def analyze_workflow_efficiency(
        self,
        data_size: int,
        operation_metrics: Dict[str, PerformanceMetrics],
        operation_name: str = "tbr_workflow",
    ) -> EfficiencyReport:
        """
        Analyze the computational efficiency of a TBR workflow.

        Parameters
        ----------
        data_size : int
            Size of the dataset being analyzed
        operation_metrics : Dict[str, PerformanceMetrics]
            Performance metrics from workflow execution
        operation_name : str, default "tbr_workflow"
            Name of the workflow being analyzed

        Returns
        -------
        EfficiencyReport
            Comprehensive efficiency analysis report
        """
        # Calculate total duration
        total_duration = sum(
            metrics.duration
            for metrics in operation_metrics.values()
            if metrics.duration is not None
        )

        # Analyze computational complexity
        complexity = self._estimate_computational_complexity(data_size, total_duration)

        # Calculate efficiency score (0-10 scale)
        efficiency_score = self._calculate_efficiency_score(
            data_size, total_duration, operation_metrics
        )

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(operation_metrics)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            data_size, total_duration, operation_metrics, bottlenecks
        )

        # Baseline comparison if available
        baseline_comparison = None
        if operation_name in self.baseline_metrics:
            baseline_comparison = self._compare_to_baseline(
                operation_name, total_duration, operation_metrics
            )

        return EfficiencyReport(
            operation_name=operation_name,
            data_size=data_size,
            computational_complexity=complexity,
            efficiency_score=efficiency_score,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            baseline_comparison=baseline_comparison,
        )

    def analyze_scaling_behavior(
        self, function: Callable, data_sizes: List[int], *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Analyze how a function's performance scales with data size.

        Parameters
        ----------
        function : Callable
            Function to analyze scaling behavior for
        data_sizes : List[int]
            List of data sizes to test
        *args : tuple
            Additional arguments for the function
        **kwargs : dict
            Additional keyword arguments for the function

        Returns
        -------
        Dict[str, Any]
            Scaling analysis results including complexity estimation
        """
        scaling_results = []

        for size in data_sizes:
            # Generate test data of specified size
            if hasattr(function, "__name__") and "regression" in function.__name__:
                # For regression functions, generate DataFrame
                test_data = pd.DataFrame(
                    {
                        "control": np.random.normal(1000, 100, size),
                        "test": np.random.normal(1050, 110, size),
                    }
                )
                benchmark_stats = self.profiler.benchmark_function(
                    function, test_data, *args, **kwargs
                )
            else:
                # For array functions, generate array
                test_data = np.random.normal(0, 1, size)
                benchmark_stats = self.profiler.benchmark_function(
                    function, test_data, *args, **kwargs
                )

            scaling_results.append(
                {
                    "data_size": size,
                    "mean_time": benchmark_stats["mean_time"],
                    "memory_usage": benchmark_stats.get("mean_memory", 0),
                }
            )

        # Analyze scaling pattern
        sizes = np.array([r["data_size"] for r in scaling_results])
        times = np.array([r["mean_time"] for r in scaling_results])

        # Fit different complexity models
        complexity_analysis = self._fit_complexity_models(sizes, times)

        return {
            "scaling_results": scaling_results,
            "complexity_analysis": complexity_analysis,
            "best_fit_complexity": complexity_analysis["best_fit"],
            "scaling_efficiency": self._calculate_scaling_efficiency(sizes, times),
        }

    def set_baseline(
        self, operation_name: str, metrics: Dict[str, PerformanceMetrics]
    ) -> None:
        """
        Set baseline performance metrics for comparison.

        Parameters
        ----------
        operation_name : str
            Name of the operation to set baseline for
        metrics : Dict[str, PerformanceMetrics]
            Baseline performance metrics
        """
        baseline_summary = {
            "total_duration": sum(m.duration for m in metrics.values() if m.duration),
            "peak_memory": max(
                (m.memory_peak for m in metrics.values() if m.memory_peak), default=0
            ),
            "operation_count": len(metrics),
        }
        self.baseline_metrics[operation_name] = baseline_summary

    def _estimate_computational_complexity(
        self, data_size: int, duration: float
    ) -> str:
        """Estimate computational complexity based on data size and execution time."""
        # Simple heuristic based on time per element
        time_per_element = duration / data_size if data_size > 0 else float("inf")

        if time_per_element < 1e-6:  # < 1 microsecond per element
            return "O(1) - Constant"
        elif time_per_element < 1e-5:  # < 10 microseconds per element
            return "O(log n) - Logarithmic"
        elif time_per_element < 1e-4:  # < 100 microseconds per element
            return "O(n) - Linear"
        elif time_per_element < 1e-3:  # < 1 millisecond per element
            return "O(n log n) - Linearithmic"
        else:
            return "O(n²) or higher - Polynomial/Exponential"

    def _calculate_efficiency_score(
        self,
        data_size: int,
        total_duration: float,
        operation_metrics: Dict[str, PerformanceMetrics],
    ) -> float:
        """Calculate efficiency score on a 0-10 scale."""
        # Base score on time per element (logarithmic scale)
        time_per_element = total_duration / data_size if data_size > 0 else float("inf")

        # Score based on time efficiency (0-5 points)
        if time_per_element < 1e-6:
            time_score = 5.0
        elif time_per_element < 1e-5:
            time_score = 4.0
        elif time_per_element < 1e-4:
            time_score = 3.0
        elif time_per_element < 1e-3:
            time_score = 2.0
        elif time_per_element < 1e-2:
            time_score = 1.0
        else:
            time_score = 0.0

        # Score based on memory efficiency (0-3 points)
        total_memory = sum(
            m.memory_peak
            for m in operation_metrics.values()
            if m.memory_peak is not None
        )
        memory_per_element = (
            total_memory / data_size if data_size > 0 and total_memory > 0 else 0
        )

        if memory_per_element < 1e-3:  # < 1KB per element
            memory_score = 3.0
        elif memory_per_element < 1e-2:  # < 10KB per element
            memory_score = 2.0
        elif memory_per_element < 1e-1:  # < 100KB per element
            memory_score = 1.0
        else:
            memory_score = 0.0

        # Score based on operation count (0-2 points)
        operation_count = len(operation_metrics)
        if operation_count <= 5:
            operation_score = 2.0
        elif operation_count <= 10:
            operation_score = 1.0
        else:
            operation_score = 0.0

        return min(10.0, time_score + memory_score + operation_score)

    def _identify_bottlenecks(
        self, operation_metrics: Dict[str, PerformanceMetrics]
    ) -> List[str]:
        """Identify performance bottlenecks in the workflow."""
        bottlenecks: List[str] = []

        if not operation_metrics:
            return bottlenecks

        # Find operations taking disproportionate time
        durations = [m.duration for m in operation_metrics.values() if m.duration]
        if durations:
            total_duration = sum(durations)
            mean_duration = np.mean(durations)

            for name, metrics in operation_metrics.items():
                if metrics.duration and metrics.duration > mean_duration * 2:
                    percentage = (metrics.duration / total_duration) * 100
                    bottlenecks.append(f"{name} ({percentage:.1f}% of total time)")

        # Find operations with high memory usage
        memory_peaks = [
            (name, m.memory_peak)
            for name, m in operation_metrics.items()
            if m.memory_peak is not None
        ]
        if memory_peaks:
            max_memory = max(peak for _, peak in memory_peaks)
            for name, peak in memory_peaks:
                if peak > max_memory * 0.7:  # More than 70% of max memory
                    bottlenecks.append(f"{name} (high memory usage: {peak:.1f} MB)")

        return bottlenecks

    def _generate_recommendations(
        self,
        data_size: int,
        total_duration: float,
        operation_metrics: Dict[str, PerformanceMetrics],
        bottlenecks: List[str],
    ) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []

        # Time-based recommendations
        time_per_element = total_duration / data_size if data_size > 0 else 0
        if time_per_element > 1e-3:  # > 1ms per element
            recommendations.append(
                "Consider vectorizing operations for better performance"
            )
            recommendations.append(
                "Profile individual functions to identify slow operations"
            )

        # Memory-based recommendations
        total_memory = sum(
            m.memory_peak
            for m in operation_metrics.values()
            if m.memory_peak is not None
        )
        if total_memory > 1000:  # > 1GB
            recommendations.append(
                "Consider processing data in chunks to reduce memory usage"
            )
            recommendations.append(
                "Use memory-efficient data types (e.g., float32 instead of float64)"
            )

        # Bottleneck-specific recommendations
        if bottlenecks:
            recommendations.append(
                "Focus optimization efforts on identified bottlenecks"
            )
            if any("regression" in b.lower() for b in bottlenecks):
                recommendations.append(
                    "Consider using optimized linear algebra libraries (BLAS/LAPACK)"
                )

        # General recommendations
        if len(operation_metrics) > 10:
            recommendations.append(
                "Consider combining related operations to reduce overhead"
            )

        if not recommendations:
            recommendations.append("Performance appears optimal for current data size")

        return recommendations

    def _compare_to_baseline(
        self,
        operation_name: str,
        current_duration: float,
        current_metrics: Dict[str, PerformanceMetrics],
    ) -> Dict[str, float]:
        """Compare current performance to baseline."""
        baseline = self.baseline_metrics[operation_name]

        current_memory = max(
            (m.memory_peak for m in current_metrics.values() if m.memory_peak),
            default=0,
        )

        return {
            "duration_ratio": current_duration / baseline["total_duration"],
            "memory_ratio": current_memory / baseline["peak_memory"]
            if baseline["peak_memory"] > 0
            else 1.0,
            "operation_ratio": len(current_metrics) / baseline["operation_count"],
        }

    def _fit_complexity_models(
        self, sizes: np.ndarray, times: np.ndarray
    ) -> Dict[str, Any]:
        """Fit different computational complexity models to scaling data."""
        models = {}

        # Linear model: O(n)
        try:
            linear_coeff = np.polyfit(sizes, times, 1)
            linear_pred = np.polyval(linear_coeff, sizes)
            linear_r2 = 1 - np.sum((times - linear_pred) ** 2) / np.sum(
                (times - np.mean(times)) ** 2
            )
            models["linear"] = {"r2": linear_r2, "coefficients": linear_coeff}
        except Exception:
            models["linear"] = {"r2": 0, "coefficients": [0, 0]}

        # Quadratic model: O(n²)
        try:
            quad_coeff = np.polyfit(sizes, times, 2)
            quad_pred = np.polyval(quad_coeff, sizes)
            quad_r2 = 1 - np.sum((times - quad_pred) ** 2) / np.sum(
                (times - np.mean(times)) ** 2
            )
            models["quadratic"] = {"r2": quad_r2, "coefficients": quad_coeff}
        except Exception:
            models["quadratic"] = {"r2": 0, "coefficients": [0, 0, 0]}

        # Logarithmic model: O(log n)
        try:
            log_sizes = np.log(sizes)
            log_coeff = np.polyfit(log_sizes, times, 1)
            log_pred = np.polyval(log_coeff, log_sizes)
            log_r2 = 1 - np.sum((times - log_pred) ** 2) / np.sum(
                (times - np.mean(times)) ** 2
            )
            models["logarithmic"] = {"r2": log_r2, "coefficients": log_coeff}
        except Exception:
            models["logarithmic"] = {"r2": 0, "coefficients": [0, 0]}

        # Find best fit
        best_fit = max(models.keys(), key=lambda k: models[k]["r2"])

        return {
            "models": models,
            "best_fit": best_fit,
            "best_r2": models[best_fit]["r2"],
        }

    def _calculate_scaling_efficiency(
        self, sizes: np.ndarray, times: np.ndarray
    ) -> float:
        """Calculate scaling efficiency score (0-10)."""
        if len(sizes) < 2:
            return 5.0  # Neutral score for insufficient data

        # Calculate scaling ratio
        size_ratios = sizes[1:] / sizes[:-1]
        time_ratios = times[1:] / times[:-1]

        # Ideal scaling would have time_ratio = size_ratio (linear)
        efficiency_ratios = size_ratios / time_ratios
        mean_efficiency = float(np.mean(efficiency_ratios))

        # Convert to 0-10 scale (1.0 = perfect linear scaling = 10 points)
        if mean_efficiency >= 1.0:
            return 10.0  # Better than linear
        elif mean_efficiency >= 0.8:
            return float(8.0 + 2.0 * (mean_efficiency - 0.8) / 0.2)
        elif mean_efficiency >= 0.5:
            return float(5.0 + 3.0 * (mean_efficiency - 0.5) / 0.3)
        elif mean_efficiency >= 0.2:
            return float(2.0 + 3.0 * (mean_efficiency - 0.2) / 0.3)
        else:
            return float(max(0.0, 2.0 * mean_efficiency / 0.2))


class PerformanceMonitor:
    """
    Real-time performance monitoring for TBR analysis workflows.

    Provides continuous monitoring of system resources and performance
    metrics during TBR analysis execution, with alerting capabilities
    for performance degradation or resource exhaustion.

    Examples
    --------
    >>> monitor = PerformanceMonitor()
    >>> monitor.start_monitoring()
    >>>
    >>> # Run TBR analysis
    >>> results = perform_tbr_analysis(data, ...)
    >>>
    >>> monitor.stop_monitoring()
    >>> report = monitor.get_monitoring_report()
    """

    def __init__(self, sampling_interval: float = 0.1):
        """
        Initialize the performance monitor.

        Parameters
        ----------
        sampling_interval : float, default 0.1
            Interval in seconds between performance samples
        """
        self.sampling_interval = sampling_interval
        self.monitoring = False
        self.samples: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None

        # Initialize system monitoring
        try:
            self.process = psutil.Process(os.getpid())
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            self.process = None
            warnings.warn(
                "System monitoring disabled due to access limitations", stacklevel=2
            )

    def start_monitoring(self) -> None:
        """Start real-time performance monitoring."""
        if self.process is None:
            warnings.warn(
                "Cannot start monitoring: system access unavailable", stacklevel=2
            )
            return

        self.monitoring = True
        self.start_time = time.time()
        self.samples.clear()

        # Initial sample
        self._take_sample()

    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        if self.monitoring:
            self._take_sample()  # Final sample
        self.monitoring = False

    def _take_sample(self) -> None:
        """Take a performance sample."""
        if self.process is None:
            return

        try:
            sample = {
                "timestamp": time.time() - (self.start_time or 0),
                "cpu_percent": self.process.cpu_percent(),
                "memory_mb": self.process.memory_info().rss / 1024 / 1024,
                "memory_percent": self.process.memory_percent(),
            }

            # System-wide metrics
            sample.update(
                {
                    "system_cpu_percent": psutil.cpu_percent(),
                    "system_memory_percent": psutil.virtual_memory().percent,
                }
            )

            self.samples.append(sample)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def get_monitoring_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive monitoring report.

        Returns
        -------
        Dict[str, Any]
            Monitoring report with statistics and trends
        """
        if not self.samples:
            return {"error": "No monitoring data available"}

        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(self.samples)

        report = {
            "duration": df["timestamp"].max() if len(df) > 0 else 0,
            "sample_count": len(df),
            "cpu_stats": {
                "mean": df["cpu_percent"].mean(),
                "max": df["cpu_percent"].max(),
                "min": df["cpu_percent"].min(),
                "std": df["cpu_percent"].std(),
            },
            "memory_stats": {
                "mean_mb": df["memory_mb"].mean(),
                "max_mb": df["memory_mb"].max(),
                "min_mb": df["memory_mb"].min(),
                "peak_percent": df["memory_percent"].max(),
            },
            "system_stats": {
                "cpu_mean": df["system_cpu_percent"].mean(),
                "cpu_max": df["system_cpu_percent"].max(),
                "memory_mean": df["system_memory_percent"].mean(),
                "memory_max": df["system_memory_percent"].max(),
            },
        }

        # Performance alerts
        alerts = []
        if report["cpu_stats"]["max"] > 90:
            alerts.append("High CPU usage detected (>90%)")
        if report["memory_stats"]["peak_percent"] > 85:
            alerts.append("High memory usage detected (>85%)")
        if report["system_stats"]["memory_max"] > 90:
            alerts.append("System memory pressure detected (>90%)")

        report["alerts"] = alerts

        return report


# Convenience functions for common performance analysis tasks


def profile_tbr_workflow(
    analysis_function: Callable,
    *args: Any,
    enable_monitoring: bool = True,
    **kwargs: Any,
) -> Tuple[Any, PerformanceMetrics, Optional[Dict[str, Any]]]:
    """
    Profile a complete TBR analysis workflow.

    Parameters
    ----------
    analysis_function : Callable
        TBR analysis function to profile
    *args : tuple
        Arguments for the analysis function
    enable_monitoring : bool, default True
        Whether to enable real-time monitoring
    **kwargs : dict
        Keyword arguments for the analysis function

    Returns
    -------
    Tuple[Any, PerformanceMetrics, Optional[Dict[str, Any]]]
        Analysis results, performance metrics, and monitoring report
    """
    profiler = PerformanceProfiler()
    monitor = PerformanceMonitor() if enable_monitoring else None

    if monitor:
        monitor.start_monitoring()

    with profiler.profile_context("tbr_workflow") as metrics:
        result = analysis_function(*args, **kwargs)

    if monitor:
        monitor.stop_monitoring()
        monitoring_report = monitor.get_monitoring_report()
    else:
        monitoring_report = None

    return result, metrics, monitoring_report


def benchmark_tbr_functions(
    functions: Dict[str, Callable], test_data: Any, n_runs: int = 5
) -> Dict[str, Dict[str, Union[float, str]]]:
    """
    Benchmark multiple TBR functions for performance comparison.

    Parameters
    ----------
    functions : Dict[str, Callable]
        Dictionary of function names to functions to benchmark
    test_data : Any
        Test data to use for benchmarking
    n_runs : int, default 5
        Number of benchmark runs per function

    Returns
    -------
    Dict[str, Dict[str, Union[float, str]]]
        Benchmark results for each function. Dict values are floats for successful
        benchmarks, or a dict with an 'error' key containing the error message string
        for failed benchmarks
    """
    profiler = PerformanceProfiler()
    results: Dict[str, Dict[str, Union[float, str]]] = {}

    for name, func in functions.items():
        try:
            if isinstance(test_data, (list, tuple)):
                benchmark_stats: Dict[str, float] = profiler.benchmark_function(
                    func, *test_data, n_runs=n_runs
                )
            else:
                benchmark_stats = profiler.benchmark_function(
                    func, test_data, n_runs=n_runs
                )
            # Convert Dict[str, float] to Dict[str, Union[float, str]]
            results[name] = dict(benchmark_stats.items())
        except Exception as e:
            results[name] = {"error": str(e)}

    return results
