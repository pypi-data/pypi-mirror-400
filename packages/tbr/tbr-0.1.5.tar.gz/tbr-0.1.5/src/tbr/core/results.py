"""
Result object structures for TBR analysis outputs.

This module provides structured result containers for TBR analysis methods.
User input data is kept separate from computed outputs, eliminating the
possibility of column name conflicts.

Result objects provide:
- Type-safe attribute access
- Rich string representations
- Conversion methods (to_dict, to_dataframe)
- Comprehensive metadata
- Time-indexed Series for temporal alignment
- Clean separation of user data from computed outputs

Examples
--------
Basic usage with functional API:

>>> from tbr.functional import perform_tbr_analysis
>>> import pandas as pd
>>> import numpy as np
>>>
>>> data = pd.DataFrame({
...     'date': pd.date_range('2023-01-01', periods=90),
...     'control': np.random.normal(1000, 50, 90),
...     'test': np.random.normal(1020, 55, 90)
... })
>>>
>>> # Run analysis - returns TBRResults object
>>> results = perform_tbr_analysis(
...     data, 'date', 'control', 'test',
...     pretest_start='2023-01-01',
...     test_start='2023-02-15',
...     test_end='2023-03-01',
...     level=0.80, threshold=0.0
... )
>>>
>>> # Access scalar summary
>>> print(f"Effect: {results.estimate:.2f}")
>>> print(f"CI: [{results.conf_int_lower:.2f}, {results.conf_int_upper:.2f}]")
>>>
>>> # Access time series (all indexed by time)
>>> results.cumulative_effect.plot()
>>> results.effects.head()
>>>
>>> # Get daily summary table
>>> summary_df = results.summary()
>>>
>>> # Get comprehensive TBR dataframe
>>> tbr_df = results.tbr_dataframe()

Object-oriented API:

>>> from tbr import TBRAnalysis
>>> model = TBRAnalysis(level=0.80)
>>> model.fit(data, 'date', 'control', 'test', ...)
>>>
>>> # Access prediction results
>>> predictions = model.predict()
>>> print(predictions.predictions.head())  # DataFrame
>>> print(f"Mean prediction: {predictions.predictions['pred'].mean():.2f}")
>>>
>>> # Access summary results
>>> summary = model.summarize()
>>> print(f"Effect: {summary.estimate:.2f}")
>>> print(f"CI: [{summary.lower:.2f}, {summary.upper:.2f}]")
>>> print(f"Probability: {summary.prob:.3f}")
>>>
>>> # Access subinterval results
>>> week1 = model.analyze_subinterval(1, 7)
>>> print(f"Week 1 effect: {week1.estimate:.2f} ± {week1.se:.2f}")

Notes
-----
User input data is kept separate from computed outputs, eliminating any
possibility of column name conflicts. All time series outputs are pd.Series
indexed by the time column values (datetime64[ns], int64, or float64).
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class TBRPredictionResult:
    """
    Result container for TBR counterfactual predictions.

    Contains predictions with uncertainty estimates and metadata about
    the model used to generate them.

    Attributes
    ----------
    predictions : pd.DataFrame
        DataFrame with columns:
        - pred: Predicted counterfactual values
        - predsd: Prediction standard deviations (uncertainty)
    n_predictions : int
        Number of predictions generated
    model_params : Dict[str, float]
        Model parameters used (alpha, beta, sigma, etc.)
    control_values : np.ndarray
        Control values used for predictions

    Examples
    --------
    >>> result = model.predict()
    >>> print(result.predictions.head())
    >>> print(f"Generated {result.n_predictions} predictions")
    >>> print(f"Model alpha: {result.model_params['alpha']:.3f}")
    """

    predictions: pd.DataFrame
    n_predictions: int
    model_params: Dict[str, float]
    control_values: np.ndarray

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary format.

        Returns
        -------
        dict
            Dictionary with all result attributes
        """
        return {
            "predictions": self.predictions,
            "n_predictions": self.n_predictions,
            "model_params": self.model_params,
            "control_values": self.control_values,
        }

    def to_json(self, filepath: str, **kwargs: Any) -> None:
        """
        Export result to JSON file.

        Parameters
        ----------
        filepath : str
            Path to output JSON file
        **kwargs : any
            Additional arguments passed to export_to_json()

        Examples
        --------
        >>> result = model.predict()
        >>> result.to_json('predictions.json')
        """
        from tbr.utils.export import export_to_json

        export_to_json(self, filepath, **kwargs)

    def to_csv(self, filepath: str, **kwargs: Any) -> None:
        """
        Export predictions DataFrame to CSV file.

        Parameters
        ----------
        filepath : str
            Path to output CSV file
        **kwargs : any
            Additional arguments passed to export_to_csv()

        Examples
        --------
        >>> result = model.predict()
        >>> result.to_csv('predictions.csv', index=False)
        """
        from tbr.utils.export import export_to_csv

        export_to_csv(self.predictions, filepath, **kwargs)

    @property
    def mean_pred(self) -> float:
        """
        Mean of predicted values.

        Returns
        -------
        float
            Average of counterfactual predictions
        """
        return float(self.predictions["pred"].mean())

    @property
    def mean_uncertainty(self) -> float:
        """
        Mean prediction uncertainty.

        Returns
        -------
        float
            Average of prediction standard deviations
        """
        return float(self.predictions["predsd"].mean())

    def __repr__(self) -> str:
        """Generate string representation."""
        return (
            f"TBRPredictionResult(\n"
            f"  n_predictions={self.n_predictions},\n"
            f"  mean_pred={self.mean_pred:.3f},\n"
            f"  mean_uncertainty={self.mean_uncertainty:.3f}\n"
            f")"
        )


@dataclass(frozen=True)
class TBRSummaryResult:
    """
    Result container for TBR summary statistics.

    Contains comprehensive summary statistics for TBR analysis including
    effect estimates, credible intervals, and model parameters.

    Attributes
    ----------
    estimate : float
        Cumulative treatment effect estimate
    lower : float
        Lower bound of credible interval
    upper : float
        Upper bound of credible interval
    se : float
        Standard error of the estimate
    prob : float
        Posterior probability of exceeding threshold
    precision : float
        Precision (half-width of credible interval)
    level : float
        Credibility level used
    threshold : float
        Threshold used for probability calculation
    alpha : float
        Regression intercept coefficient
    beta : float
        Regression slope coefficient
    sigma : float
        Residual standard deviation
    var_alpha : float
        Variance of intercept estimate
    var_beta : float
        Variance of slope estimate
    cov_alpha_beta : float
        Covariance between intercept and slope
    degrees_freedom : int
        Degrees of freedom

    Examples
    --------
    >>> result = model.summarize()
    >>> print(f"Effect: {result.estimate:.2f}")
    >>> print(f"95% CI: [{result.lower:.2f}, {result.upper:.2f}]")
    >>> print(f"Significant: {result.prob > 0.95}")
    """

    estimate: float
    lower: float
    upper: float
    se: float
    prob: float
    precision: float
    level: float
    threshold: float
    alpha: float
    beta: float
    sigma: float
    var_alpha: float
    var_beta: float
    cov_alpha_beta: float
    degrees_freedom: int

    def to_dict(self) -> Dict[str, float]:
        """
        Convert result to dictionary format.

        Returns
        -------
        dict
            Dictionary with all summary statistics
        """
        return {
            "estimate": self.estimate,
            "lower": self.lower,
            "upper": self.upper,
            "se": self.se,
            "prob": self.prob,
            "precision": self.precision,
            "level": self.level,
            "threshold": self.threshold,
            "alpha": self.alpha,
            "beta": self.beta,
            "sigma": self.sigma,
            "var_alpha": self.var_alpha,
            "var_beta": self.var_beta,
            "cov_alpha_beta": self.cov_alpha_beta,
            "degrees_freedom": self.degrees_freedom,
        }

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert result to single-row DataFrame format.

        Returns
        -------
        pd.DataFrame
            Single-row DataFrame with all summary statistics
        """
        return pd.DataFrame([self.to_dict()])

    def to_json(self, filepath: str, **kwargs: Any) -> None:
        """
        Export result to JSON file.

        Parameters
        ----------
        filepath : str
            Path to output JSON file
        **kwargs : any
            Additional arguments passed to export_to_json()

        Examples
        --------
        >>> summary = model.summarize()
        >>> summary.to_json('summary.json')
        """
        from tbr.utils.export import export_to_json

        export_to_json(self, filepath, **kwargs)

    def to_csv(self, filepath: str, **kwargs: Any) -> None:
        """
        Export result to CSV file.

        Parameters
        ----------
        filepath : str
            Path to output CSV file
        **kwargs : any
            Additional arguments passed to export_to_csv()

        Examples
        --------
        >>> summary = model.summarize()
        >>> summary.to_csv('summary.csv', index=False)
        """
        from tbr.utils.export import export_to_csv

        export_to_csv(self, filepath, **kwargs)

    def is_significant(self, probability_threshold: float = 0.95) -> bool:
        """
        Check if effect is statistically significant.

        Parameters
        ----------
        probability_threshold : float, default=0.95
            Probability threshold for significance

        Returns
        -------
        bool
            True if posterior probability exceeds threshold
        """
        return self.prob >= probability_threshold

    def __repr__(self) -> str:
        """Generate string representation."""
        return (
            f"TBRSummaryResult(\n"
            f"  estimate={self.estimate:.3f},\n"
            f"  CI=[{self.lower:.3f}, {self.upper:.3f}] (level={self.level}),\n"
            f"  se={self.se:.3f},\n"
            f"  prob={self.prob:.3f}\n"
            f")"
        )


@dataclass(frozen=True)
class TBRSubintervalResult:
    """
    Result container for TBR subinterval analysis.

    Contains treatment effect estimates for a specific time window within
    the test period, with credible intervals and metadata.

    Attributes
    ----------
    estimate : float
        Treatment effect estimate for the subinterval
    lower : float
        Lower bound of credible interval
    upper : float
        Upper bound of credible interval
    se : float
        Standard error of the estimate
    ci_level : float
        Credibility level used for interval
    start_day : int
        Starting day of subinterval (1-indexed)
    end_day : int
        Ending day of subinterval (1-indexed)
    n_days : int
        Number of days in the subinterval

    Examples
    --------
    >>> result = model.analyze_subinterval(1, 7)
    >>> print(f"Week 1 effect: {result.estimate:.2f}")
    >>> print(f"CI: [{result.lower:.2f}, {result.upper:.2f}]")
    >>> print(f"Days: {result.start_day}-{result.end_day} ({result.n_days} days)")
    >>> if result.contains_zero():
    ...     print("Effect not significant (CI contains zero)")
    """

    estimate: float
    lower: float
    upper: float
    se: float
    ci_level: float
    start_day: int
    end_day: int
    n_days: int

    def to_dict(self) -> Dict[str, float]:
        """
        Convert result to dictionary format.

        Returns
        -------
        dict
            Dictionary with all subinterval statistics
        """
        return {
            "estimate": self.estimate,
            "lower": self.lower,
            "upper": self.upper,
            "se": self.se,
            "ci_level": self.ci_level,
            "start_day": self.start_day,
            "end_day": self.end_day,
            "n_days": self.n_days,
        }

    def to_json(self, filepath: str, **kwargs: Any) -> None:
        """
        Export result to JSON file.

        Parameters
        ----------
        filepath : str
            Path to output JSON file
        **kwargs : any
            Additional arguments passed to export_to_json()

        Examples
        --------
        >>> result = model.analyze_subinterval(1, 7)
        >>> result.to_json('week1_results.json')
        """
        from tbr.utils.export import export_to_json

        export_to_json(self, filepath, **kwargs)

    def to_csv(self, filepath: str, **kwargs: Any) -> None:
        """
        Export result to CSV file as single-row DataFrame.

        Parameters
        ----------
        filepath : str
            Path to output CSV file
        **kwargs : any
            Additional arguments passed to pandas.DataFrame.to_csv()

        Examples
        --------
        >>> result = model.analyze_subinterval(1, 7)
        >>> result.to_csv('week1_results.csv', index=False)
        """
        df = pd.DataFrame([self.to_dict()])
        df.to_csv(filepath, **kwargs)

    def contains_zero(self) -> bool:
        """
        Check if credible interval contains zero.

        Returns
        -------
        bool
            True if interval contains zero (effect not significant)
        """
        return self.lower <= 0 <= self.upper

    def is_positive(self) -> bool:
        """
        Check if entire credible interval is positive.

        Returns
        -------
        bool
            True if lower bound > 0 (positive effect with high confidence)
        """
        return self.lower > 0

    def is_negative(self) -> bool:
        """
        Check if entire credible interval is negative.

        Returns
        -------
        bool
            True if upper bound < 0 (negative effect with high confidence)
        """
        return self.upper < 0

    def __repr__(self) -> str:
        """Generate string representation."""
        return (
            f"TBRSubintervalResult(\n"
            f"  days={self.start_day}-{self.end_day} (n={self.n_days}),\n"
            f"  estimate={self.estimate:.3f},\n"
            f"  CI=[{self.lower:.3f}, {self.upper:.3f}] (level={self.ci_level}),\n"
            f"  se={self.se:.3f}\n"
            f")"
        )


class TBRResults:
    """
    Comprehensive results from Time-Based Regression analysis.

    All computed outputs are accessible via properties and methods, with
    complete separation from user input data. This design eliminates any
    possibility of column name conflicts.

    All time series outputs are returned as pandas Series indexed by the time
    column values from the input data, preserving temporal alignment for
    plotting, merging, and further analysis.

    Parameters
    ----------
    data : pd.DataFrame
        Original input DataFrame (stored for reference, not modified)
    time_col : str
        Name of the time column in input data
    control_col : str
        Name of the control group column
    test_col : str
        Name of the test group column
    model_params : Dict[str, float]
        Regression model parameters from fit_regression_model
    periods : Dict[str, pd.DataFrame]
        DataFrames for each period (baseline, pretest, test, cooldown)
    level : float
        Credibility level for confidence intervals
    threshold : float
        Threshold for probability calculations

    Attributes (Properties)
    ------------------------
    Time Series (pd.Series indexed by time):
        control : Control group values
        test : Test group values
        fittedvalues : Fitted values from regression (pretest period)
        predictions : Counterfactual predictions (test period)
        resid : Residuals (pretest: observed - fitted)
        effects : Treatment effects (test: observed - predicted)
        cumulative_effect : Cumulative treatment effects over time
        prediction_se : Prediction standard errors (test period)
        cumulative_se : Cumulative effect standard errors (test period)

    Scalars:
        estimate : Final cumulative treatment effect
        conf_int_lower : Lower bound of credible interval
        conf_int_upper : Upper bound of credible interval
        pvalue : Posterior probability of exceeding threshold
        n_pretest : Number of pretest observations
        n_test : Number of test observations
        n_test_days : Number of days in test period

    Model Parameters:
        alpha : Regression intercept
        beta : Regression slope
        sigma : Residual standard deviation
        model_params : Complete dict of all model parameters

    Methods
    -------
    summary() : Generate daily incremental summary DataFrame
    to_dataframe() : Export all results to comprehensive DataFrame
    conf_int() : Get confidence interval as DataFrame

    Examples
    --------
    >>> from tbr.functional import perform_tbr_analysis
    >>> results = perform_tbr_analysis(data, 'date', 'control', 'test', ...)
    >>>
    >>> # Access scalar summary
    >>> print(f"Effect: {results.estimate:.2f}")
    >>> print(f"CI: [{results.conf_int_lower:.2f}, {results.conf_int_upper:.2f}]")
    >>> print(f"P-value: {results.pvalue:.3f}")
    >>>
    >>> # Access time series (all indexed by time)
    >>> results.cumulative_effect.plot(title='Cumulative Treatment Effect')
    >>> results.effects.describe()
    >>>
    >>> # Get daily summary table
    >>> daily_summary = results.summary()
    >>> print(daily_summary.tail())
    >>>
    >>> # Get comprehensive TBR dataframe
    >>> tbr_df = results.tbr_dataframe()

    Notes
    -----
    Input data and computed outputs are kept separate, with all results
    accessible via properties. Time alignment is preserved through pandas
    Series indexing, working seamlessly with datetime, integer, or float
    time columns.

    See Also
    --------
    perform_tbr_analysis : Functional API that returns TBRResults
    TBRAnalysis : Object-oriented API wrapper
    """

    def __init__(
        self,
        _data: pd.DataFrame,
        time_col: str,
        control_col: str,
        test_col: str,
        model_params: Dict[str, float],
        periods: Dict[str, pd.DataFrame],
        level: float,
        threshold: float,
    ):
        """Initialize TBRResults with analysis outputs."""
        # Store metadata
        self._time_col = time_col
        self._control_col = control_col
        self._test_col = test_col
        self._model_params = model_params
        self._level = level
        self._threshold = threshold

        # Store period data
        self._baseline_data = periods.get("baseline", pd.DataFrame())
        self._pretest_data = periods["pretest"]
        self._test_data = periods["test"]
        self._cooldown_data = periods.get("cooldown", pd.DataFrame())

        # Compute all results during initialization
        self._compute_results()

    def _compute_results(self) -> None:
        """
        Compute all TBR analysis results.

        This internal method performs the complete TBR analysis pipeline,
        computing fitted values, predictions, effects, and uncertainties
        for all periods. Results are stored as internal Series indexed by time.
        """
        # Import here to avoid circular imports
        from tbr.functional.tbr_functions import (
            calculate_cumulative_standard_deviation,
            calculate_model_variance,
            calculate_sum_x_squared_deviations,
            create_incremental_tbr_summaries,
            generate_counterfactual_predictions,
            safe_int_conversion,
        )

        # Extract time indices for each period
        self._baseline_time = (
            self._baseline_data[self._time_col].values
            if not self._baseline_data.empty
            else np.array([])
        )
        self._pretest_time = self._pretest_data[self._time_col].values
        self._test_time = self._test_data[self._time_col].values
        self._all_time = np.concatenate([self._pretest_time, self._test_time])

        # Extract control and test values
        pretest_control = self._pretest_data[self._control_col].values
        pretest_test = self._pretest_data[self._test_col].values
        test_control = self._test_data[self._control_col].values
        test_test = self._test_data[self._test_col].values

        # Store input data as Series (indexed by time)
        self._control_series = pd.Series(
            np.concatenate([pretest_control, test_control]),
            index=self._all_time,
            name="control",
        )
        self._test_series = pd.Series(
            np.concatenate([pretest_test, test_test]),
            index=self._all_time,
            name="test",
        )

        # Compute pretest statistics
        pretest_x_mean = float(np.mean(pretest_control))
        pretest_sum_x_squared_deviations = calculate_sum_x_squared_deviations(
            pretest_control
        )
        n_pretest = safe_int_conversion(self._model_params["n_pretest"], "n_pretest")

        # Compute fitted values for pretest period
        fitted_vals = (
            self._model_params["alpha"] + self._model_params["beta"] * pretest_control
        )
        self._fittedvalues = pd.Series(
            fitted_vals, index=self._pretest_time, name="fittedvalues"
        )

        # Compute fitted value uncertainties (model variance only)
        fitted_variances = calculate_model_variance(
            x_values=pretest_control,
            pretest_x_mean=pretest_x_mean,
            sigma=self._model_params["sigma"],
            n_pretest=n_pretest,
            pretest_sum_x_squared_deviations=pretest_sum_x_squared_deviations,
        )
        self._fitted_se = pd.Series(
            np.sqrt(fitted_variances), index=self._pretest_time, name="fitted_se"
        )

        # Compute residuals for pretest period
        self._resid = pd.Series(
            pretest_test - fitted_vals, index=self._pretest_time, name="resid"
        )

        # Generate counterfactual predictions for test period
        test_predictions = generate_counterfactual_predictions(
            alpha=self._model_params["alpha"],
            beta=self._model_params["beta"],
            sigma=self._model_params["sigma"],
            pretest_x_mean=pretest_x_mean,
            n_pretest=n_pretest,
            pretest_sum_x_squared_deviations=pretest_sum_x_squared_deviations,
            test_period_data=self._test_data,
            control_col=self._control_col,
            time_col=self._time_col,
        )

        # Store predictions and uncertainties
        self._predictions = pd.Series(
            test_predictions["pred"].values, index=self._test_time, name="predictions"
        )
        self._prediction_se = pd.Series(
            test_predictions["predsd"].values,
            index=self._test_time,
            name="prediction_se",
        )

        # Compute treatment effects
        self._effects = pd.Series(
            test_test - test_predictions["pred"].values,
            index=self._test_time,
            name="effects",
        )

        # Compute cumulative effects
        self._cumulative_effect = pd.Series(
            self._effects.cumsum().values,
            index=self._test_time,
            name="cumulative_effect",
        )

        # Compute cumulative standard deviations
        cumsd_values = calculate_cumulative_standard_deviation(
            test_control,
            self._model_params["sigma"],
            self._model_params["var_alpha"],
            self._model_params["var_beta"],
            self._model_params["cov_alpha_beta"],
        )
        self._cumulative_se = pd.Series(
            cumsd_values, index=self._test_time, name="cumulative_se"
        )

        # Create comprehensive DataFrame for summary computation
        # This is internal and uses standard column names
        self._internal_df = self._build_internal_dataframe()

        # Compute incremental daily summaries
        self._summary_df = create_incremental_tbr_summaries(
            tbr_dataframe=self._internal_df,
            alpha=self._model_params["alpha"],
            beta=self._model_params["beta"],
            sigma=self._model_params["sigma"],
            var_alpha=self._model_params["var_alpha"],
            var_beta=self._model_params["var_beta"],
            cov_alpha_beta=self._model_params["cov_alpha_beta"],
            degrees_freedom=safe_int_conversion(
                self._model_params["degrees_freedom"], "degrees_freedom"
            ),
            level=self._level,
            threshold=self._threshold,
        )

    def _build_internal_dataframe(self) -> pd.DataFrame:
        """
        Build internal DataFrame for computations.

        This creates a DataFrame with standard column names for internal use.
        Not exposed to users - they use property-based access instead.
        """
        dataframes_to_combine = []

        # Process baseline period if it exists
        if not self._baseline_data.empty:
            baseline_df = self._baseline_data.copy()
            baseline_df["period"] = -1
            baseline_df["y"] = baseline_df[self._test_col]
            baseline_df["x"] = baseline_df[self._control_col]
            baseline_df["pred"] = np.nan
            baseline_df["predsd"] = np.nan
            baseline_df["dif"] = np.nan
            baseline_df["cumdif"] = np.nan
            baseline_df["cumsd"] = np.nan
            baseline_df["estsd"] = np.nan
            dataframes_to_combine.append(baseline_df)

        # Process pretest period
        pretest_df = self._pretest_data.copy()
        pretest_df["period"] = 0
        pretest_df["y"] = pretest_df[self._test_col]
        pretest_df["x"] = pretest_df[self._control_col]
        pretest_df["pred"] = self._fittedvalues.values
        pretest_df["predsd"] = 0.0
        pretest_df["dif"] = self._resid.values
        pretest_df["cumdif"] = np.nan
        pretest_df["cumsd"] = 0.0
        pretest_df["estsd"] = self._fitted_se.values
        dataframes_to_combine.append(pretest_df)

        # Process test period
        test_df = self._test_data.copy()
        test_df["period"] = 1
        test_df["y"] = test_df[self._test_col]
        test_df["x"] = test_df[self._control_col]
        test_df["pred"] = self._predictions.values
        test_df["predsd"] = self._prediction_se.values
        test_df["dif"] = self._effects.values
        test_df["cumdif"] = self._cumulative_effect.values
        test_df["cumsd"] = self._cumulative_se.values
        test_df["estsd"] = np.nan
        dataframes_to_combine.append(test_df)

        return pd.concat(dataframes_to_combine, ignore_index=True)

    # =========================================================================
    # Properties: Time Series (all indexed by time)
    # =========================================================================

    @property
    def control(self) -> pd.Series:
        """
        Control group values indexed by time.

        Returns
        -------
        pd.Series
            Control group metric values for pretest and test periods,
            indexed by time column values (datetime/int/float).
        """
        return self._control_series

    @property
    def test(self) -> pd.Series:
        """
        Test group values indexed by time.

        Returns
        -------
        pd.Series
            Test group metric values for pretest and test periods,
            indexed by time column values (datetime/int/float).
        """
        return self._test_series

    @property
    def fittedvalues(self) -> pd.Series:
        """
        Fitted values from regression model (pretest period only).

        Returns
        -------
        pd.Series
            Fitted values: α + β * control, indexed by pretest time values.
        """
        return self._fittedvalues

    @property
    def predictions(self) -> pd.Series:
        """
        Counterfactual predictions for test period.

        Returns
        -------
        pd.Series
            Predicted values for test group based on control group,
            indexed by test period time values.
        """
        return self._predictions

    @property
    def resid(self) -> pd.Series:
        """
        Residuals for pretest period (observed - fitted).

        Returns
        -------
        pd.Series
            Residuals from regression fit, indexed by pretest time values.
        """
        return self._resid

    @property
    def effects(self) -> pd.Series:
        """
        Treatment effects for test period (observed - predicted).

        Returns
        -------
        pd.Series
            Daily treatment effects, indexed by test period time values.
        """
        return self._effects

    @property
    def cumulative_effect(self) -> pd.Series:
        """
        Cumulative treatment effects over test period.

        Returns
        -------
        pd.Series
            Running sum of treatment effects, indexed by test period time.
        """
        return self._cumulative_effect

    @property
    def prediction_se(self) -> pd.Series:
        """
        Prediction standard errors for test period.

        Returns
        -------
        pd.Series
            Standard errors of counterfactual predictions, indexed by test time.
        """
        return self._prediction_se

    @property
    def cumulative_se(self) -> pd.Series:
        """
        Cumulative effect standard errors over test period.

        Returns
        -------
        pd.Series
            Standard errors of cumulative effects, indexed by test time.
        """
        return self._cumulative_se

    # =========================================================================
    # Properties: Scalars
    # =========================================================================

    @property
    def estimate(self) -> float:
        """
        Final cumulative treatment effect estimate.

        Returns
        -------
        float
            Total cumulative effect at end of test period.
        """
        return float(self._cumulative_effect.iloc[-1])

    @property
    def conf_int_lower(self) -> float:
        """
        Lower bound of credible interval for final estimate.

        Returns
        -------
        float
            Lower confidence bound at specified level.
        """
        return float(self._summary_df.iloc[-1]["lower"])

    @property
    def conf_int_upper(self) -> float:
        """
        Upper bound of credible interval for final estimate.

        Returns
        -------
        float
            Upper confidence bound at specified level.
        """
        return float(self._summary_df.iloc[-1]["upper"])

    @property
    def pvalue(self) -> float:
        """
        Posterior probability of effect exceeding threshold.

        Returns
        -------
        float
            Probability that true effect > threshold.
        """
        return float(self._summary_df.iloc[-1]["prob"])

    @property
    def n_pretest(self) -> int:
        """
        Number of observations in pretest period.

        Returns
        -------
        int
            Count of pretest observations.
        """
        return len(self._pretest_data)

    @property
    def n_test(self) -> int:
        """
        Number of observations in test period.

        Returns
        -------
        int
            Count of test observations.
        """
        return len(self._test_data)

    @property
    def n_test_days(self) -> int:
        """
        Number of days (time points) in test period.

        Returns
        -------
        int
            Length of test period.
        """
        return len(self._test_data)

    # =========================================================================
    # Properties: Model Parameters
    # =========================================================================

    @property
    def alpha(self) -> float:
        """
        Regression intercept coefficient.

        Returns
        -------
        float
            Intercept from regression: test = alpha + beta * control.
        """
        return float(self._model_params["alpha"])

    @property
    def beta(self) -> float:
        """
        Regression slope coefficient.

        Returns
        -------
        float
            Slope from regression: test = alpha + beta * control.
        """
        return float(self._model_params["beta"])

    @property
    def sigma(self) -> float:
        """
        Residual standard deviation from regression.

        Returns
        -------
        float
            Standard deviation of residuals from pretest fit.
        """
        return float(self._model_params["sigma"])

    @property
    def model_params(self) -> Dict[str, float]:
        """
        Complete dictionary of regression model parameters.

        Returns
        -------
        dict
            All model parameters including alpha, beta, sigma, variances,
            covariances, degrees of freedom, etc.
        """
        return self._model_params.copy()

    # =========================================================================
    # Methods
    # =========================================================================

    def summary(self) -> pd.DataFrame:
        """
        Generate daily incremental summary statistics.

        Creates a DataFrame with one row per test day, showing cumulative
        effects and confidence intervals as they accumulate over time.

        Returns
        -------
        pd.DataFrame
            Daily summary with columns: estimate, lower, upper, precision,
            prob, and other statistics. Each row represents cumulative
            results through that day of the test period.

        Examples
        --------
        >>> results = perform_tbr_analysis(...)
        >>> summary = results.summary()
        >>> print(summary.tail())  # Last 5 days
        >>> summary.plot(x='test_day', y=['estimate', 'lower', 'upper'])
        """
        return self._summary_df.copy()

    def tbr_dataframe(self) -> pd.DataFrame:
        """
        Get the comprehensive TBR analysis dataframe.

        Returns the complete TBR dataframe combining all periods (baseline,
        pretest, test, cooldown) with all computed statistics using standard
        column names. This is the main results dataframe from the analysis.

        Returns
        -------
        pd.DataFrame
            Complete TBR results dataframe with columns:
            - time column (user's original name)
            - period: -1=baseline, 0=pretest, 1=test, 3=cooldown
            - y, x: test and control values
            - pred: fitted/predicted values
            - predsd: prediction standard deviations
            - dif: residuals/effects
            - cumdif: cumulative effects
            - cumsd: cumulative standard deviations
            - estsd: fitted value standard deviations

        Examples
        --------
        >>> results = perform_tbr_analysis(...)
        >>> tbr_df = results.tbr_dataframe()
        >>> tbr_df.to_csv('tbr_results.csv', index=False)
        >>>
        >>> # Filter to test period only
        >>> test_period = tbr_df[tbr_df['period'] == 1]

        Notes
        -----
        This returns a copy of the internal dataframe to prevent accidental
        modifications. For time-indexed Series access, use the property
        accessors (e.g., `results.cumulative_effect`).

        See Also
        --------
        summary : Get daily incremental summary statistics
        """
        return self._internal_df.copy()

    def conf_int(self, level: Optional[float] = None) -> pd.DataFrame:
        """
        Get confidence interval bounds for final estimate.

        Parameters
        ----------
        level : float, optional
            Confidence level (e.g., 0.80, 0.95). If not specified,
            uses the level from analysis initialization.

        Returns
        -------
        pd.DataFrame
            Single-row DataFrame with 'lower' and 'upper' columns.

        Examples
        --------
        >>> results = perform_tbr_analysis(..., level=0.80)
        >>> ci = results.conf_int()  # Uses 0.80
        >>> ci_95 = results.conf_int(level=0.95)  # Override to 0.95
        """
        if level is None:
            level = self._level

        # Recompute confidence interval if different level requested
        if level != self._level:
            final_effect = self.estimate
            final_se = float(self._cumulative_se.iloc[-1])
            df = self._model_params["degrees_freedom"]
            t_crit = stats.t.ppf((1 + level) / 2, df)
            precision = t_crit * final_se
            lower = final_effect - precision
            upper = final_effect + precision
        else:
            lower = self.conf_int_lower
            upper = self.conf_int_upper

        return pd.DataFrame({"lower": [lower], "upper": [upper]})

    def __repr__(self) -> str:
        """
        Generate string representation.

        Returns
        -------
        str
            Multi-line summary of key results.
        """
        return (
            f"<TBRResults>\n"
            f"Cumulative Effect: {self.estimate:.2f}\n"
            f"{self._level*100:.0f}% CI: [{self.conf_int_lower:.2f}, {self.conf_int_upper:.2f}]\n"
            f"Probability > {self._threshold}: {self.pvalue:.3f}\n"
            f"Test Period: {self.n_test_days} observations\n"
            f"Model: α = {self.alpha:.3f}, β = {self.beta:.3f}, σ = {self.sigma:.3f}"
        )

    def __str__(self) -> str:
        """Generate user-friendly string representation."""
        return self.__repr__()
