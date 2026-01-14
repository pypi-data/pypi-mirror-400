"""
TBR Analysis Diagnostics Module.

This module provides comprehensive diagnostic tools for validating Time-Based
Regression (TBR) analyses, including model validation, assumption checking,
and performance diagnostics. It builds upon the robust statistical foundation
in core.diagnostics while providing high-level, TBR-specific diagnostic
interfaces for the analysis framework.

The module integrates seamlessly with TBR DataFrames and analysis workflows,
providing user-friendly diagnostic functions that work with the complete
TBR analysis pipeline including summary statistics, incremental analysis,
and subinterval analysis.

Functions
---------
validate_tbr_model : Comprehensive TBR model validation
diagnose_tbr_analysis : End-to-end diagnostic workflow for TBR analysis
check_tbr_assumptions : Statistical assumption validation for TBR models
analyze_tbr_residuals : TBR-specific residual analysis and outlier detection
assess_tbr_performance : Performance and efficiency diagnostics
create_tbr_diagnostic_report : Comprehensive diagnostic reporting

Examples
--------
>>> from tbr.analysis.diagnostics import validate_tbr_model
>>> from tbr.functional import perform_tbr_analysis
>>>
>>> # Perform TBR analysis
>>> tbr_df, summary_df = perform_tbr_analysis(
...     data, 'date', 'control', 'test',
...     pretest_start='2023-01-01', test_start='2023-02-15', test_end='2023-03-01'
... )
>>>
>>> # Validate the TBR model
>>> validation = validate_tbr_model(tbr_df, summary_df)
>>> print(f"Model valid: {validation['overall_validity']}")
>>> if validation['warnings']:
...     for warning in validation['warnings']:
...         print(f"Warning: {warning}")

Comprehensive diagnostic workflow:

>>> from tbr.analysis.diagnostics import diagnose_tbr_analysis
>>> diagnostics = diagnose_tbr_analysis(tbr_df, summary_df, learning_data)
>>> print(f"R-squared: {diagnostics['goodness_of_fit']['r_squared']:.3f}")
>>> print(f"Normality p-value: {diagnostics['assumption_tests']['normality']['p_value']:.4f}")

Performance assessment:

>>> from tbr.analysis.diagnostics import assess_tbr_performance
>>> performance = assess_tbr_performance(tbr_df, summary_df)
>>> print(f"Prediction accuracy: {performance['prediction_metrics']['mape']:.2f}%")
>>> print(f"Computational efficiency: {performance['efficiency_score']:.2f}")
"""

from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

# Import core diagnostic functions
from tbr.core.diagnostics import (
    calculate_goodness_of_fit,
    calculate_residuals,
    calculate_standardized_residuals,
    calculate_studentized_residuals,
    create_diagnostic_summary,
    validate_model_assumptions,
)

# Import core regression for model parameter extraction
# Import validation utilities
from tbr.utils.validation import validate_required_columns


def validate_tbr_model(
    tbr_df: pd.DataFrame,
    tbr_summary: pd.DataFrame,
    learning_data: Optional[pd.DataFrame] = None,
    alpha: float = 0.05,
) -> Dict[str, Union[bool, List[str], Dict]]:
    """
    Comprehensive TBR model validation with assumption checking and diagnostics.

    Performs end-to-end validation of a TBR model including statistical
    assumptions, goodness-of-fit metrics, and model diagnostics. This function
    provides a high-level interface for validating TBR analyses and identifying
    potential issues with model validity.

    Parameters
    ----------
    tbr_df : pd.DataFrame
        TBR analysis results DataFrame containing columns:
        'period', 'y', 'x', 'pred', 'predsd', 'dif', 'cumdif', 'cumsd', 'estsd'
    tbr_summary : pd.DataFrame
        TBR summary statistics DataFrame containing model parameters:
        'alpha', 'beta', 'sigma', 'var_alpha', 'var_beta', 'alpha_beta_cov', 't_dist_df'
    learning_data : pd.DataFrame, optional
        Original learning period data for residual analysis.
        If not provided, extracted from tbr_df where period == 0.
    alpha : float, default 0.05
        Significance level for statistical tests

    Returns
    -------
    Dict[str, Union[bool, List[str], Dict]]
        Comprehensive validation results containing:

        - 'overall_validity' : bool
            Whether the model passes all validation checks
        - 'warnings' : List[str]
            List of validation warnings and issues
        - 'assumption_tests' : Dict
            Results of statistical assumption tests
        - 'goodness_of_fit' : Dict
            Model fit quality metrics
        - 'residual_analysis' : Dict
            Residual diagnostics and outlier detection
        - 'prediction_quality' : Dict
            Prediction accuracy and reliability metrics

    Raises
    ------
    ValueError
        If required columns are missing from input DataFrames
        If tbr_summary is empty or contains invalid parameters
        If no learning period data is available

    Notes
    -----
    The validation performs the following checks:

    1. **Statistical Assumptions**: Tests for normality, homoscedasticity,
       and independence of residuals using appropriate statistical tests
    2. **Goodness of Fit**: Evaluates R², adjusted R², F-statistic, and
       information criteria (AIC, BIC)
    3. **Residual Analysis**: Examines residual patterns, outliers, and
       leverage points
    4. **Prediction Quality**: Assesses prediction accuracy and reliability
       for the test period

    The function integrates multiple diagnostic approaches to provide a
    comprehensive assessment of model validity and reliability.

    Examples
    --------
    Basic model validation:

    >>> validation = validate_tbr_model(tbr_df, tbr_summary)
    >>> if validation['overall_validity']:
    ...     print("Model validation passed")
    ... else:
    ...     print("Model validation issues:")
    ...     for warning in validation['warnings']:
    ...         print(f"  - {warning}")

    Detailed diagnostic review:

    >>> validation = validate_tbr_model(tbr_df, tbr_summary, learning_data)
    >>> print(f"R²: {validation['goodness_of_fit']['r_squared']:.3f}")
    >>> print(f"Normality p-value: {validation['assumption_tests']['normality']['p_value']:.4f}")
    >>> print(f"Outliers detected: {len(validation['residual_analysis']['outliers'])}")
    """
    # Validate input DataFrames
    required_tbr_cols = [
        "period",
        "y",
        "x",
        "pred",
        "predsd",
        "dif",
        "cumdif",
        "cumsd",
        "estsd",
    ]
    validate_required_columns(tbr_df, required_tbr_cols, "tbr_df")

    required_summary_cols = [
        "alpha",
        "beta",
        "sigma",
        "var_alpha",
        "var_beta",
        "alpha_beta_cov",
        "t_dist_df",
    ]
    validate_required_columns(tbr_summary, required_summary_cols, "tbr_summary")

    if tbr_summary.empty:
        raise ValueError("tbr_summary DataFrame cannot be empty")

    # Extract learning data if not provided
    if learning_data is None:
        learning_data = tbr_df[tbr_df["period"] == 0].copy()
        if learning_data.empty:
            raise ValueError(
                "No learning period data found (period == 0) and learning_data not provided"
            )

    # Extract model parameters from summary
    summary_row = tbr_summary.iloc[0]
    model_params = {
        "alpha": float(summary_row["alpha"]),
        "beta": float(summary_row["beta"]),
        "sigma": float(summary_row["sigma"]),
        "var_alpha": float(summary_row["var_alpha"]),
        "var_beta": float(summary_row["var_beta"]),
        "alpha_beta_cov": float(summary_row["alpha_beta_cov"]),
        "degrees_freedom": int(summary_row["t_dist_df"]),  # Add degrees of freedom
    }

    warnings_list = []

    # 1. Statistical Assumption Tests
    try:
        assumption_tests = validate_model_assumptions(
            learning_data, model_params, "x", "y", alpha=alpha
        )

        if not assumption_tests["normality_valid"]:
            warnings_list.append(
                "Residuals fail normality test - consider data transformation"
            )
        if not assumption_tests["homoscedasticity_valid"]:
            warnings_list.append(
                "Residuals show heteroscedasticity - variance may be non-constant"
            )
        if not assumption_tests["independence_valid"]:
            warnings_list.append(
                "Residuals show autocorrelation - independence assumption violated"
            )

    except Exception as e:
        warnings_list.append(f"Assumption testing failed: {str(e)}")
        assumption_tests = {"error": str(e)}

    # 2. Goodness of Fit Analysis
    try:
        goodness_of_fit = calculate_goodness_of_fit(
            learning_data, model_params, "x", "y"
        )

        if goodness_of_fit["r_squared"] < 0.5:
            warnings_list.append(
                f"Low R² ({goodness_of_fit['r_squared']:.3f}) - model explains little variance"
            )
        if goodness_of_fit["f_statistic_p_value"] > alpha:
            warnings_list.append(
                "F-statistic not significant - overall model may not be meaningful"
            )

    except Exception as e:
        warnings_list.append(f"Goodness of fit calculation failed: {str(e)}")
        goodness_of_fit = {
            "r_squared": 0.0,
            "adj_r_squared": 0.0,
            "f_statistic": 0.0,
            "f_statistic_p_value": 1.0,
            "mse": 0.0,
            "rmse": 0.0,
        }

    # 3. Residual Analysis
    try:
        residuals = calculate_residuals(learning_data, model_params, "x", "y")
        standardized_residuals = calculate_standardized_residuals(
            learning_data, model_params, "x", "y"
        )
        studentized_residuals = calculate_studentized_residuals(
            learning_data, model_params, "x", "y"
        )

        # Identify outliers (|studentized residual| > 2.5)
        outlier_threshold = 2.5
        outliers = np.where(np.abs(studentized_residuals) > outlier_threshold)[0]

        if len(outliers) > 0.1 * len(learning_data):  # More than 10% outliers
            warnings_list.append(
                f"High number of outliers detected ({len(outliers)}/{len(learning_data)})"
            )

        residual_analysis = {
            "residuals": residuals,
            "standardized_residuals": standardized_residuals,
            "studentized_residuals": studentized_residuals,
            "outliers": outliers.tolist(),
            "outlier_threshold": outlier_threshold,
            "outlier_percentage": len(outliers) / len(learning_data) * 100,
        }

    except Exception as e:
        warnings_list.append(f"Residual analysis failed: {str(e)}")
        residual_analysis = {"error": str(e)}

    # 4. Prediction Quality Assessment
    try:
        test_data = tbr_df[tbr_df["period"] == 1].copy()
        if not test_data.empty:
            # Calculate prediction accuracy metrics
            prediction_errors = test_data["y"] - test_data["pred"]
            mae = np.mean(np.abs(prediction_errors))
            mse = np.mean(prediction_errors**2)
            rmse = np.sqrt(mse)
            mape = np.mean(np.abs(prediction_errors / test_data["y"])) * 100

            # Check prediction interval coverage
            pred_lower = test_data["pred"] - 1.96 * test_data["predsd"]
            pred_upper = test_data["pred"] + 1.96 * test_data["predsd"]
            coverage = np.mean(
                (test_data["y"] >= pred_lower) & (test_data["y"] <= pred_upper)
            )

            if coverage < 0.90:  # Less than 90% coverage for ~95% intervals
                warnings_list.append(
                    f"Poor prediction interval coverage ({coverage:.1%}) - uncertainty may be underestimated"
                )

            prediction_quality = {
                "mae": mae,
                "mse": mse,
                "rmse": rmse,
                "mape": mape,
                "prediction_interval_coverage": coverage,
                "n_predictions": len(test_data),
            }
        else:
            prediction_quality = {"error": "No test period data available"}

    except Exception as e:
        warnings_list.append(f"Prediction quality assessment failed: {str(e)}")
        prediction_quality = {"error": str(e)}

    # Overall validity assessment
    overall_validity = len(warnings_list) == 0

    return {
        "overall_validity": overall_validity,
        "warnings": warnings_list,
        "assumption_tests": assumption_tests,
        "goodness_of_fit": goodness_of_fit,
        "residual_analysis": residual_analysis,
        "prediction_quality": prediction_quality,
    }


def diagnose_tbr_analysis(
    tbr_df: pd.DataFrame,
    tbr_summary: pd.DataFrame,
    learning_data: Optional[pd.DataFrame] = None,
    include_performance: bool = True,
) -> Dict[str, Union[Dict, List, float, Any]]:
    """
    End-to-end diagnostic workflow for comprehensive TBR analysis evaluation.

    Performs a complete diagnostic evaluation of a TBR analysis including
    model validation, assumption checking, residual analysis, and optional
    performance assessment. This function provides a one-stop diagnostic
    workflow for evaluating TBR analysis quality and reliability.

    Parameters
    ----------
    tbr_df : pd.DataFrame
        TBR analysis results DataFrame
    tbr_summary : pd.DataFrame
        TBR summary statistics DataFrame
    learning_data : pd.DataFrame, optional
        Original learning period data. If not provided, extracted from tbr_df.
    include_performance : bool, default True
        Whether to include computational performance diagnostics

    Returns
    -------
    Dict[str, Union[Dict, List, float]]
        Comprehensive diagnostic results containing:

        - 'model_validation' : Dict
            Results from validate_tbr_model()
        - 'diagnostic_summary' : Dict
            Core diagnostic summary from create_diagnostic_summary()
        - 'performance_metrics' : Dict (if include_performance=True)
            Computational performance and efficiency metrics
        - 'recommendations' : List[str]
            Actionable recommendations based on diagnostic results

    Examples
    --------
    >>> diagnostics = diagnose_tbr_analysis(tbr_df, tbr_summary)
    >>> print(f"Overall model validity: {diagnostics['model_validation']['overall_validity']}")
    >>> print("Recommendations:")
    >>> for rec in diagnostics['recommendations']:
    ...     print(f"  - {rec}")
    """
    # Extract learning data if needed
    if learning_data is None:
        learning_data = tbr_df[tbr_df["period"] == 0].copy()

    # 1. Model Validation
    model_validation = validate_tbr_model(tbr_df, tbr_summary, learning_data)

    # 2. Core Diagnostic Summary
    summary_row = tbr_summary.iloc[0]
    model_params = {
        "alpha": float(summary_row["alpha"]),
        "beta": float(summary_row["beta"]),
        "sigma": float(summary_row["sigma"]),
        "var_alpha": float(summary_row["var_alpha"]),
        "var_beta": float(summary_row["var_beta"]),
        "alpha_beta_cov": float(summary_row["alpha_beta_cov"]),
        "degrees_freedom": int(summary_row["t_dist_df"]),
    }

    try:
        diagnostic_summary = create_diagnostic_summary(
            learning_data, model_params, "x", "y"
        )
    except Exception as e:
        diagnostic_summary = {
            "goodness_of_fit": {
                "r_squared": 0.0,
                "adj_r_squared": 0.0,
                "f_statistic": 0.0,
                "f_p_value": 1.0,
                "mse": 0.0,
                "rmse": 0.0,
            },
            "information_criteria": {"aic": 0.0, "bic": 0.0},
            "normality_test": {
                "statistic": 0.0,
                "p_value": 1.0,
                "is_normal": False,
                "test_name": "error",
            },
            "homoscedasticity_test": {
                "statistic": 0.0,
                "p_value": 1.0,
                "is_homoscedastic": False,
                "test_name": "error",
            },
            "independence_test": {
                "statistic": 0.0,
                "interpretation": "error",
                "is_independent": False,
                "test_name": "error",
            },
            "overall_validity": False,
            "warnings": [f"Diagnostic summary failed: {str(e)}"],
        }

    # 3. Performance Metrics (if requested)
    performance_metrics = {}
    if include_performance:
        performance_metrics = assess_tbr_performance(tbr_df, tbr_summary)

    # 4. Generate Recommendations
    recommendations = _generate_diagnostic_recommendations(
        model_validation, performance_metrics
    )

    return {
        "model_validation": model_validation,
        "diagnostic_summary": diagnostic_summary,
        "performance_metrics": performance_metrics,
        "recommendations": recommendations,
    }


def check_tbr_assumptions(
    tbr_df: pd.DataFrame,
    tbr_summary: pd.DataFrame,
    learning_data: Optional[pd.DataFrame] = None,
    alpha: float = 0.05,
) -> Dict[str, Union[bool, float, str]]:
    """
    Statistical assumption validation specifically for TBR models.

    Performs comprehensive testing of regression assumptions required for
    valid TBR analysis, including linearity, normality, homoscedasticity,
    and independence. Provides clear pass/fail results with statistical
    test details.

    Parameters
    ----------
    tbr_df : pd.DataFrame
        TBR analysis results DataFrame
    tbr_summary : pd.DataFrame
        TBR summary statistics DataFrame
    learning_data : pd.DataFrame, optional
        Learning period data for assumption testing
    alpha : float, default 0.05
        Significance level for statistical tests

    Returns
    -------
    Dict[str, Union[bool, float, str]]
        Assumption test results with pass/fail status and test statistics

    Examples
    --------
    >>> assumptions = check_tbr_assumptions(tbr_df, tbr_summary)
    >>> print(f"All assumptions valid: {assumptions['all_assumptions_valid']}")
    >>> print(f"Normality p-value: {assumptions['normality_p_value']:.4f}")
    """
    if learning_data is None:
        learning_data = tbr_df[tbr_df["period"] == 0].copy()

    summary_row = tbr_summary.iloc[0]
    model_params = {
        "alpha": float(summary_row["alpha"]),
        "beta": float(summary_row["beta"]),
        "sigma": float(summary_row["sigma"]),
        "var_alpha": float(summary_row["var_alpha"]),
        "var_beta": float(summary_row["var_beta"]),
        "alpha_beta_cov": float(summary_row["alpha_beta_cov"]),
        "degrees_freedom": int(summary_row["t_dist_df"]),
    }

    return validate_model_assumptions(
        learning_data, model_params, "x", "y", alpha=alpha
    )


def analyze_tbr_residuals(
    tbr_df: pd.DataFrame,
    tbr_summary: pd.DataFrame,
    learning_data: Optional[pd.DataFrame] = None,
) -> Dict[str, Union[np.ndarray, List, float]]:
    """
    TBR-specific residual analysis and outlier detection.

    Performs comprehensive residual analysis for TBR models including
    calculation of raw, standardized, and studentized residuals, outlier
    detection, and residual pattern analysis.

    Parameters
    ----------
    tbr_df : pd.DataFrame
        TBR analysis results DataFrame
    tbr_summary : pd.DataFrame
        TBR summary statistics DataFrame
    learning_data : pd.DataFrame, optional
        Learning period data for residual calculation

    Returns
    -------
    Dict[str, Union[np.ndarray, List, float]]
        Residual analysis results including residuals, outliers, and diagnostics

    Examples
    --------
    >>> residuals = analyze_tbr_residuals(tbr_df, tbr_summary)
    >>> print(f"Outliers detected: {len(residuals['outliers'])}")
    >>> print(f"Residual std: {residuals['residual_std']:.3f}")
    """
    if learning_data is None:
        learning_data = tbr_df[tbr_df["period"] == 0].copy()

    summary_row = tbr_summary.iloc[0]
    model_params = {
        "alpha": float(summary_row["alpha"]),
        "beta": float(summary_row["beta"]),
        "sigma": float(summary_row["sigma"]),
        "var_alpha": float(summary_row["var_alpha"]),
        "var_beta": float(summary_row["var_beta"]),
        "alpha_beta_cov": float(summary_row["alpha_beta_cov"]),
        "degrees_freedom": int(summary_row["t_dist_df"]),
    }

    # Calculate different types of residuals
    residuals = calculate_residuals(learning_data, model_params, "x", "y")
    standardized_residuals = calculate_standardized_residuals(
        learning_data, model_params, "x", "y"
    )
    studentized_residuals = calculate_studentized_residuals(
        learning_data, model_params, "x", "y"
    )

    # Outlier detection
    outlier_threshold = 2.5
    outliers = np.where(np.abs(studentized_residuals) > outlier_threshold)[0]

    # Residual statistics
    residual_stats = {
        "mean": np.mean(residuals),
        "std": np.std(residuals),
        "min": np.min(residuals),
        "max": np.max(residuals),
        "q25": np.percentile(residuals, 25),
        "median": np.median(residuals),
        "q75": np.percentile(residuals, 75),
    }

    return {
        "residuals": residuals,
        "standardized_residuals": standardized_residuals,
        "studentized_residuals": studentized_residuals,
        "outliers": outliers.tolist(),
        "outlier_threshold": outlier_threshold,
        "outlier_percentage": len(outliers) / len(learning_data) * 100,
        "residual_stats": residual_stats,
        "residual_std": residual_stats["std"],
        "n_observations": len(residuals),
    }


def assess_tbr_performance(
    tbr_df: pd.DataFrame,
    tbr_summary: pd.DataFrame,
) -> Dict[str, Union[float, int, Dict]]:
    """
    Assess performance and efficiency for TBR analysis.

    Evaluates computational performance, prediction accuracy, and efficiency
    metrics for TBR analysis workflows. Provides insights into model
    performance and computational characteristics.

    Parameters
    ----------
    tbr_df : pd.DataFrame
        TBR analysis results DataFrame
    tbr_summary : pd.DataFrame
        TBR summary statistics DataFrame

    Returns
    -------
    Dict[str, Union[float, int, Dict]]
        Performance assessment results including accuracy and efficiency metrics

    Examples
    --------
    >>> performance = assess_tbr_performance(tbr_df, tbr_summary)
    >>> print(f"Prediction MAPE: {performance['prediction_metrics']['mape']:.2f}%")
    >>> print(f"Efficiency score: {performance['efficiency_score']:.2f}")
    """
    # Data size metrics
    total_observations = len(tbr_df)
    learning_observations = len(tbr_df[tbr_df["period"] == 0])
    test_observations = len(tbr_df[tbr_df["period"] == 1])

    # Prediction accuracy metrics (for test period)
    test_data = tbr_df[tbr_df["period"] == 1].copy()
    prediction_metrics = {}

    if not test_data.empty:
        prediction_errors = test_data["y"] - test_data["pred"]

        prediction_metrics = {
            "mae": float(np.mean(np.abs(prediction_errors))),
            "mse": float(np.mean(prediction_errors**2)),
            "rmse": float(np.sqrt(np.mean(prediction_errors**2))),
            "mape": float(np.mean(np.abs(prediction_errors / test_data["y"])) * 100),
            "mean_error": float(np.mean(prediction_errors)),
            "std_error": float(np.std(prediction_errors)),
        }

        # Prediction interval coverage
        pred_lower = test_data["pred"] - 1.96 * test_data["predsd"]
        pred_upper = test_data["pred"] + 1.96 * test_data["predsd"]
        coverage = float(
            np.mean((test_data["y"] >= pred_lower) & (test_data["y"] <= pred_upper))
        )
        prediction_metrics["interval_coverage"] = coverage

    # Model complexity metrics
    summary_row = tbr_summary.iloc[0]
    model_complexity = {
        "degrees_freedom": int(summary_row["t_dist_df"]),
        "sigma": float(summary_row["sigma"]),
        "r_squared_proxy": 1.0
        - (
            float(summary_row["sigma"]) ** 2
            / np.var(tbr_df[tbr_df["period"] == 0]["y"])
        )
        if learning_observations > 0
        else 0.0,
    }

    # Efficiency score (composite metric)
    efficiency_components = []
    if prediction_metrics:
        # Lower MAPE is better (invert and normalize)
        mape_score = max(0, 1 - prediction_metrics["mape"] / 100)
        efficiency_components.append(mape_score)

        # Good interval coverage (target ~0.95)
        coverage_score = (
            1 - abs(prediction_metrics.get("interval_coverage", 0.95) - 0.95) * 2
        )
        efficiency_components.append(max(0, coverage_score))

    # Model parsimony (prefer simpler models)
    if learning_observations > 0:
        parsimony_score = min(
            1.0, learning_observations / 50
        )  # Normalize by reasonable sample size
        efficiency_components.append(parsimony_score)

    efficiency_score = np.mean(efficiency_components) if efficiency_components else 0.0

    return {
        "data_metrics": {
            "total_observations": total_observations,
            "learning_observations": learning_observations,
            "test_observations": test_observations,
            "learning_test_ratio": learning_observations / max(test_observations, 1),
        },
        "prediction_metrics": prediction_metrics,
        "model_complexity": model_complexity,
        "efficiency_score": float(efficiency_score),
        "performance_summary": {
            "data_quality": "Good" if learning_observations >= 20 else "Limited",
            "prediction_quality": "Good"
            if prediction_metrics.get("mape", 100) < 10
            else "Moderate"
            if prediction_metrics.get("mape", 100) < 25
            else "Poor",
            "overall_performance": "Excellent"
            if efficiency_score > 0.8
            else "Good"
            if efficiency_score > 0.6
            else "Moderate"
            if efficiency_score > 0.4
            else "Poor",
        },
    }


def create_tbr_diagnostic_report(
    tbr_df: pd.DataFrame,
    tbr_summary: pd.DataFrame,
    learning_data: Optional[pd.DataFrame] = None,
    include_detailed_analysis: bool = True,
) -> Dict[str, Union[str, Dict, List]]:
    """
    Create comprehensive diagnostic report for TBR analysis.

    Generates a complete diagnostic report combining all diagnostic functions
    into a structured, interpretable format suitable for analysis review
    and documentation.

    Parameters
    ----------
    tbr_df : pd.DataFrame
        TBR analysis results DataFrame
    tbr_summary : pd.DataFrame
        TBR summary statistics DataFrame
    learning_data : pd.DataFrame, optional
        Learning period data for detailed analysis
    include_detailed_analysis : bool, default True
        Whether to include detailed residual and performance analysis

    Returns
    -------
    Dict[str, Union[str, Dict, List]]
        Comprehensive diagnostic report with summary and detailed results

    Examples
    --------
    >>> report = create_tbr_diagnostic_report(tbr_df, tbr_summary)
    >>> print(report['executive_summary'])
    >>> print("Key findings:")
    >>> for finding in report['key_findings']:
    ...     print(f"  - {finding}")
    """
    # Run comprehensive diagnostics
    diagnostics = diagnose_tbr_analysis(
        tbr_df,
        tbr_summary,
        learning_data,
        include_performance=include_detailed_analysis,
    )

    # Extract key metrics for summary
    model_validation = diagnostics["model_validation"]
    if isinstance(model_validation, dict):
        model_valid = model_validation.get("overall_validity", False)
        warnings_count = len(model_validation.get("warnings", []))
    else:
        model_valid = False
        warnings_count = 0

    # Generate executive summary
    if model_valid:
        executive_summary = "TBR model validation PASSED. The analysis meets statistical requirements and assumptions."
    else:
        executive_summary = f"TBR model validation identified {warnings_count} issue(s) requiring attention."

    # Key findings
    key_findings = []

    # Add goodness of fit findings
    if isinstance(model_validation, dict):
        gof = model_validation.get("goodness_of_fit", {})
        if isinstance(gof, dict) and "r_squared" in gof:
            key_findings.append(
                f"Model explains {gof['r_squared']:.1%} of variance (R² = {gof['r_squared']:.3f})"
            )

        # Add assumption test findings
        assumptions = model_validation.get("assumption_tests", {})
        if isinstance(assumptions, dict) and "all_assumptions_valid" in assumptions:
            if assumptions["all_assumptions_valid"]:
                key_findings.append("All statistical assumptions are satisfied")
            else:
                failed_assumptions = []
                if not assumptions.get("normality_valid", True):
                    failed_assumptions.append("normality")
                if not assumptions.get("homoscedasticity_valid", True):
                    failed_assumptions.append("homoscedasticity")
                if not assumptions.get("independence_valid", True):
                    failed_assumptions.append("independence")
                key_findings.append(
                    f"Assumption violations: {', '.join(failed_assumptions)}"
                )

    # Add performance findings
    if (
        include_detailed_analysis
        and isinstance(diagnostics["performance_metrics"], dict)
        and "prediction_metrics" in diagnostics["performance_metrics"]
    ):
        pred_metrics = diagnostics["performance_metrics"]["prediction_metrics"]
        if isinstance(pred_metrics, dict) and "mape" in pred_metrics:
            key_findings.append(
                f"Prediction accuracy: {pred_metrics['mape']:.1f}% MAPE"
            )
        if isinstance(pred_metrics, dict) and "interval_coverage" in pred_metrics:
            key_findings.append(
                f"Prediction interval coverage: {pred_metrics['interval_coverage']:.1%}"
            )

    # Compile report
    report = {
        "executive_summary": executive_summary,
        "overall_validity": model_valid,
        "warnings_count": warnings_count,
        "key_findings": key_findings,
        "recommendations": diagnostics["recommendations"],
        "detailed_results": diagnostics if include_detailed_analysis else None,
        "report_timestamp": pd.Timestamp.now().isoformat(),
    }

    return report


def _generate_diagnostic_recommendations(
    model_validation: Dict,
    performance_metrics: Dict,
) -> List[str]:
    """
    Generate actionable recommendations based on diagnostic results.

    Internal helper function that analyzes diagnostic results and generates
    specific, actionable recommendations for improving TBR analysis quality.

    Parameters
    ----------
    model_validation : Dict
        Results from validate_tbr_model()
    diagnostic_summary : Dict
        Results from create_diagnostic_summary()
    performance_metrics : Dict
        Results from assess_tbr_performance()

    Returns
    -------
    List[str]
        List of actionable recommendations
    """
    recommendations = []

    # Model validation recommendations
    if not model_validation.get("overall_validity", True):
        recommendations.append(
            "Address model validation warnings before proceeding with analysis"
        )

    # Assumption-based recommendations
    assumptions = model_validation.get("assumption_tests", {})
    if isinstance(assumptions, dict):
        if not assumptions.get("normality_valid", True):
            recommendations.append(
                "Consider data transformation (log, square root) to improve residual normality"
            )
        if not assumptions.get("homoscedasticity_valid", True):
            recommendations.append(
                "Investigate heteroscedasticity - consider weighted regression or variance stabilization"
            )
        if not assumptions.get("independence_valid", True):
            recommendations.append(
                "Check for temporal patterns in data - consider time series methods if autocorrelation persists"
            )

    # Goodness of fit recommendations
    gof = model_validation.get("goodness_of_fit", {})
    if isinstance(gof, dict) and "r_squared" in gof:
        if gof["r_squared"] < 0.3:
            recommendations.append(
                "Low model fit (R² < 0.3) - consider additional predictors or different model specification"
            )
        elif gof["r_squared"] < 0.5:
            recommendations.append(
                "Moderate model fit - investigate potential confounding variables or model improvements"
            )

    # Outlier recommendations
    residual_analysis = model_validation.get("residual_analysis", {})
    if (
        isinstance(residual_analysis, dict)
        and "outlier_percentage" in residual_analysis
    ):
        if residual_analysis["outlier_percentage"] > 10:
            recommendations.append(
                "High percentage of outliers detected - investigate data quality and consider robust regression methods"
            )

    # Performance recommendations
    if performance_metrics and "prediction_metrics" in performance_metrics:
        pred_metrics = performance_metrics["prediction_metrics"]
        if "mape" in pred_metrics and pred_metrics["mape"] > 15:
            recommendations.append(
                "High prediction error (MAPE > 15%) - consider model refinement or additional validation"
            )
        if (
            "interval_coverage" in pred_metrics
            and pred_metrics["interval_coverage"] < 0.85
        ):
            recommendations.append(
                "Poor prediction interval coverage - uncertainty estimates may be unreliable"
            )

    # Data quality recommendations
    if performance_metrics and "data_metrics" in performance_metrics:
        data_metrics = performance_metrics["data_metrics"]
        if data_metrics["learning_observations"] < 20:
            recommendations.append(
                "Limited learning period data - consider collecting more historical data for robust model fitting"
            )
        if data_metrics["learning_test_ratio"] < 2:
            recommendations.append(
                "Short learning period relative to test period - consider longer historical baseline"
            )

    # Default recommendation if no issues found
    if not recommendations:
        recommendations.append(
            "Model diagnostics look good - proceed with confidence in TBR analysis results"
        )

    return recommendations
