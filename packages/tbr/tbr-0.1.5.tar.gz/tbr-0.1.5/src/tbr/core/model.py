"""
Object-oriented interface for Time-Based Regression analysis.

This module provides the TBRAnalysis class, which wraps the functional API
with a stateful interface for storing configuration, fitted parameters, and
analysis results.

Examples
--------
>>> from tbr.core.model import TBRAnalysis
>>> import pandas as pd
>>> import numpy as np
>>>
>>> # Create sample data
>>> data = pd.DataFrame({
...     'date': pd.date_range('2023-01-01', periods=90),
...     'control': np.random.normal(1000, 50, 90),
...     'test': np.random.normal(1020, 55, 90)
... })
>>>
>>> # Initialize and fit model
>>> model = TBRAnalysis(level=0.80, threshold=0.0)
>>> model.fit(
...     data=data,
...     time_col='date',
...     control_col='control',
...     test_col='test',
...     pretest_start='2023-01-01',
...     test_start='2023-02-15',
...     test_end='2023-03-01'
... )
>>>
>>> # Access results
>>> final_effect = model.summaries_.iloc[-1]['estimate']
>>> print(f"Treatment Effect: {final_effect:.2f}")

Notes
-----
Configuration parameters are stored in __init__. Analysis is performed via
the fit() method. Fitted results are accessed via underscore-suffixed
attributes (results_, summaries_, params_), which validate fitted state
before access.
"""

from typing import Any, Dict, Optional, Union

import numpy as np
import pandas as pd

from tbr.core.results import TBRPredictionResult, TBRSubintervalResult, TBRSummaryResult


class TBRAnalysis:
    """
    Time-Based Regression Analysis with stateful interface.

    Wraps the functional TBR API to store configuration, fitted parameters,
    and analysis results.

    Parameters
    ----------
    level : float, default=0.80
        Credibility level for credible intervals (e.g., 0.80 for 80% credible interval).
        Must be between 0 and 1 exclusive.
    threshold : float, default=0.0
        Threshold for probability calculation. Typically 0.0 for testing
        positive effects. Can be any finite float value.
    test_end_inclusive : bool, default=False
        Whether to include the test_end boundary in the test period.

        - False (default): Exclusive end boundary (data < test_end)
        - True: Inclusive end boundary (data <= test_end)

    Attributes
    ----------
    level : float
        Credibility level for credible intervals.
    threshold : float
        Threshold for probability calculation.
    test_end_inclusive : bool
        Whether test_end is inclusive.
    fitted_ : bool
        Whether the model has been fitted.
    results_ : pd.DataFrame
        TBR DataFrame with predictions, effects, and uncertainties.
        Available after calling fit().
    summaries_ : pd.DataFrame
        Incremental summaries with daily progression of effects.
        Available after calling fit().
    params_ : dict
        Regression model parameters (alpha, beta, sigma, variances, etc.).
        Available after calling fit().

    Examples
    --------
    Basic workflow:

    >>> model = TBRAnalysis(level=0.80, threshold=0.0)
    >>> model.fit(data, 'date', 'control', 'test',
    ...           pretest_start='2023-01-01',
    ...           test_start='2023-02-15',
    ...           test_end='2023-03-01')
    >>> print(model.summaries_.iloc[-1])

    Custom configuration:

    >>> model = TBRAnalysis(level=0.95, threshold=5.0, test_end_inclusive=True)
    >>> model.fit(data, 'date', 'control', 'test',
    ...           pretest_start='2023-01-01',
    ...           test_start='2023-02-15',
    ...           test_end='2023-02-15')  # Same-day analysis

    Notes
    -----
    Configuration parameters are stored in __init__. Call fit() to perform
    analysis. Access fitted results via underscore-suffixed attributes
    (results_, summaries_, params_), which validate fitted state before access.

    See Also
    --------
    tbr.functional.perform_tbr_analysis : Functional API for TBR analysis
    """

    def __init__(
        self,
        level: float = 0.80,
        threshold: float = 0.0,
        test_end_inclusive: bool = False,
    ) -> None:
        """
        Initialize TBR analysis with configuration parameters.

        Parameters
        ----------
        level : float, default=0.80
            Credibility level for credible intervals.
        threshold : float, default=0.0
            Threshold for probability calculation.
        test_end_inclusive : bool, default=False
            Whether to include test_end boundary in analysis.

        Raises
        ------
        ValueError
            If level is not between 0 and 1 exclusive.
        TypeError
            If parameters have incorrect types.
        """
        # Validate configuration parameters
        if not isinstance(level, (int, float)):
            raise TypeError(f"level must be numeric, got {type(level).__name__}")

        if not (0 < level < 1):
            raise ValueError(f"level must be between 0 and 1 exclusive, got {level}")

        if not isinstance(threshold, (int, float)):
            raise TypeError(
                f"threshold must be numeric, got {type(threshold).__name__}"
            )

        if not isinstance(test_end_inclusive, bool):
            raise TypeError(
                f"test_end_inclusive must be bool, got {type(test_end_inclusive).__name__}"
            )

        # Store configuration
        self.level = float(level)
        self.threshold = float(threshold)
        self.test_end_inclusive = test_end_inclusive

        # Initialize state (will be set by fit())
        self._fitted = False
        self._results: Optional[pd.DataFrame] = None
        self._summaries: Optional[pd.DataFrame] = None
        self._params: Optional[Dict[str, Any]] = None
        self._fit_info: Optional[Dict[str, Any]] = None

    def fit(
        self,
        data: pd.DataFrame,
        time_col: str,
        control_col: str,
        test_col: str,
        pretest_start: Union[pd.Timestamp, int, float],
        test_start: Union[pd.Timestamp, int, float],
        test_end: Union[pd.Timestamp, int, float],
    ) -> "TBRAnalysis":
        """
        Fit TBR model to data and store results.

        Performs Time-Based Regression analysis using the functional API,
        storing results and fitted parameters for later access via properties.

        Parameters
        ----------
        data : pd.DataFrame
            Time series data with time, control, and test columns.
        time_col : str
            Name of the time column (datetime64[ns], int64, or float64).
        control_col : str
            Name of control group metric column.
        test_col : str
            Name of test group metric column.
        pretest_start : Union[pd.Timestamp, int, float]
            Start time of pretest period (inclusive).
        test_start : Union[pd.Timestamp, int, float]
            Start time of test period (inclusive).
        test_end : Union[pd.Timestamp, int, float]
            End time of test period (inclusive/exclusive based on test_end_inclusive).

        Returns
        -------
        TBRAnalysis
            Returns self for method chaining.

        Raises
        ------
        TypeError
            If input types are invalid.
        ValueError
            If input validation fails or insufficient data for analysis.

        Examples
        --------
        Basic fitting:

        >>> model = TBRAnalysis(level=0.80, threshold=0.0)
        >>> model.fit(data, 'date', 'control', 'test',
        ...           pretest_start='2023-01-01',
        ...           test_start='2023-02-15',
        ...           test_end='2023-03-01')
        >>> print(f"Final effect: {model.summaries_.iloc[-1]['estimate']:.2f}")

        Method chaining:

        >>> results = (TBRAnalysis(level=0.95)
        ...            .fit(data, 'date', 'control', 'test',
        ...                 pretest_start='2023-01-01',
        ...                 test_start='2023-02-15',
        ...                 test_end='2023-03-01')
        ...            .results_)

        Notes
        -----
        Uses the stored configuration (level, threshold, test_end_inclusive)
        from initialization. Call fit() to perform analysis before accessing
        results_, summaries_, or params_ properties.
        """
        # Lazy imports to minimize loading overhead
        from tbr.functional import perform_tbr_analysis
        from tbr.utils.preprocessing import split_time_series_by_periods
        from tbr.utils.validation import (
            validate_dataframe_not_empty,
            validate_metric_columns,
            validate_no_nulls,
            validate_required_columns,
            validate_time_boundaries_type,
            validate_time_column_type,
            validate_time_periods,
        )

        # ===== Input Validation =====
        # Validate DataFrame type and not empty
        if not isinstance(data, pd.DataFrame):
            raise TypeError(
                f"data must be a pandas DataFrame, got {type(data).__name__}"
            )

        validate_dataframe_not_empty(data, "data")

        # Validate column name types
        if not isinstance(time_col, str):
            raise TypeError(f"time_col must be a string, got {type(time_col).__name__}")
        if not isinstance(control_col, str):
            raise TypeError(
                f"control_col must be a string, got {type(control_col).__name__}"
            )
        if not isinstance(test_col, str):
            raise TypeError(f"test_col must be a string, got {type(test_col).__name__}")

        # Validate required columns exist
        validate_required_columns(data, [time_col, control_col, test_col], "data")

        # Validate time column type
        validate_time_column_type(data, time_col, "data")

        # Validate metric columns are numeric
        validate_metric_columns(data, control_col, test_col)

        # Validate no nulls in required columns
        validate_no_nulls(data, [time_col, control_col, test_col], "data")

        # Validate time boundaries type consistency
        validate_time_boundaries_type(
            pretest_start, test_start, test_end, data[time_col].dtype
        )

        # Validate time periods ordering
        validate_time_periods(
            pretest_start, test_start, test_end, self.test_end_inclusive
        )

        # Perform TBR analysis using functional API with stored configuration
        tbr_results = perform_tbr_analysis(
            data=data,
            time_col=time_col,
            control_col=control_col,
            test_col=test_col,
            pretest_start=pretest_start,
            test_start=test_start,
            test_end=test_end,
            level=self.level,
            threshold=self.threshold,
            test_end_inclusive=self.test_end_inclusive,
        )

        # Extract DataFrames from TBRResults
        tbr_dataframe = tbr_results.tbr_dataframe()
        tbr_summaries = tbr_results.summary()

        # Extract model parameters from summaries (all rows have same parameters)
        summary_row = tbr_summaries.iloc[0]

        # Extract pretest data to calculate pretest_sum_x_squared_deviations
        _, pretest_df, test_df, _ = split_time_series_by_periods(
            aggregated_data=data,
            time_col=time_col,
            pretest_start=pretest_start,
            test_start=test_start,
            test_end=test_end,
            test_end_inclusive=self.test_end_inclusive,
        )

        # Calculate pretest_sum_x_squared_deviations from pretest control values
        pretest_control = pretest_df[control_col].values
        pretest_x_mean = float(np.mean(pretest_control))
        pretest_sum_x_squared_deviations = float(
            np.sum((pretest_control - pretest_x_mean) ** 2)
        )

        # Store results
        self._results = tbr_dataframe
        self._summaries = tbr_summaries

        # Store parameters dictionary
        self._params = {
            "alpha": float(summary_row["alpha"]),
            "beta": float(summary_row["beta"]),
            "sigma": float(summary_row["sigma"]),
            "var_alpha": float(summary_row["var_alpha"]),
            "var_beta": float(summary_row["var_beta"]),
            "cov_alpha_beta": float(summary_row["alpha_beta_cov"]),
            "degrees_freedom": int(summary_row["t_dist_df"]),
            "pretest_x_mean": pretest_x_mean,
            "pretest_sum_x_squared_deviations": pretest_sum_x_squared_deviations,
        }

        # Store fit information
        self._fit_info = {
            "time_col": time_col,
            "control_col": control_col,
            "test_col": test_col,
            "pretest_start": pretest_start,
            "test_start": test_start,
            "test_end": test_end,
            "n_pretest": len(pretest_df),
            "n_test": len(test_df),
        }

        # Mark as fitted
        self._fitted = True

        # Return self for method chaining
        return self

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        """
        Get configuration parameters for this estimator.

        Parameters
        ----------
        deep : bool, default=True
            If True, will return parameters for this estimator.
            Parameter is included for sklearn compatibility but has no effect
            since TBRAnalysis has no nested estimators.

        Returns
        -------
        dict
            Configuration parameters.

        Examples
        --------
        >>> model = TBRAnalysis(level=0.90, threshold=5.0)
        >>> params = model.get_params()
        >>> print(params)
        {'level': 0.90, 'threshold': 5.0, 'test_end_inclusive': False}

        See Also
        --------
        set_params : Set configuration parameters.
        """
        # Note: 'deep' parameter is for sklearn compatibility
        # TBRAnalysis has no nested estimators, so it has no effect
        _ = deep  # Acknowledge parameter for vulture
        return {
            "level": self.level,
            "threshold": self.threshold,
            "test_end_inclusive": self.test_end_inclusive,
        }

    def set_params(self, **params: Any) -> "TBRAnalysis":
        """
        Set configuration parameters for this estimator.

        Parameters are validated and stored. If the model was previously fitted,
        it will need to be re-fitted with the new parameters.

        Parameters
        ----------
        **params : dict
            Configuration parameters to set. Valid parameters are:
            - level : float between 0 and 1 exclusive
            - threshold : numeric value
            - test_end_inclusive : bool

        Returns
        -------
        TBRAnalysis
            Returns self for method chaining.

        Raises
        ------
        ValueError
            If invalid parameter names or values are provided.
        TypeError
            If parameter types are invalid.

        Examples
        --------
        Update configuration:

        >>> model = TBRAnalysis()
        >>> model.set_params(level=0.95, threshold=10.0)
        >>> print(model.get_params())
        {'level': 0.95, 'threshold': 10.0, 'test_end_inclusive': False}

        Method chaining:

        >>> summary = (TBRAnalysis()
        ...            .set_params(level=0.95)
        ...            .fit(data, 'date', 'control', 'test', ...)
        ...            .summarize())

        See Also
        --------
        get_params : Get configuration parameters.

        Notes
        -----
        If the model was previously fitted, changing parameters requires
        re-fitting the model. The fitted state is reset when parameters change.
        """
        valid_params = {"level", "threshold", "test_end_inclusive"}

        # Check for invalid parameter names
        invalid_params = set(params.keys()) - valid_params
        if invalid_params:
            raise ValueError(
                f"Invalid parameter(s): {invalid_params}. "
                f"Valid parameters are: {valid_params}"
            )

        # Track if any parameter changed
        params_changed = False

        # Update parameters with validation
        if "level" in params:
            new_level = params["level"]
            if not isinstance(new_level, (int, float)):
                raise TypeError(
                    f"level must be numeric, got {type(new_level).__name__}"
                )
            if not (0 < new_level < 1):
                raise ValueError(
                    f"level must be between 0 and 1 exclusive, got {new_level}"
                )
            if self.level != float(new_level):
                self.level = float(new_level)
                params_changed = True

        if "threshold" in params:
            new_threshold = params["threshold"]
            if not isinstance(new_threshold, (int, float)):
                raise TypeError(
                    f"threshold must be numeric, got {type(new_threshold).__name__}"
                )
            if self.threshold != float(new_threshold):
                self.threshold = float(new_threshold)
                params_changed = True

        if "test_end_inclusive" in params:
            new_test_end_inclusive = params["test_end_inclusive"]
            if not isinstance(new_test_end_inclusive, bool):
                raise TypeError(
                    f"test_end_inclusive must be bool, got {type(new_test_end_inclusive).__name__}"
                )
            if self.test_end_inclusive != new_test_end_inclusive:
                self.test_end_inclusive = new_test_end_inclusive
                params_changed = True

        # Reset fitted state if parameters changed
        if params_changed and self._fitted:
            self._fitted = False
            self._results = None
            self._summaries = None
            self._params = None
            self._fit_info = None

        return self

    def copy(self) -> "TBRAnalysis":
        """
        Create a deep copy of this estimator.

        Returns a new TBRAnalysis instance with the same configuration but
        without fitted state. This is useful for creating multiple models
        with the same configuration.

        Returns
        -------
        TBRAnalysis
            New instance with same configuration parameters.

        Examples
        --------
        Create a copy with same configuration:

        >>> model1 = TBRAnalysis(level=0.90, threshold=5.0)
        >>> model2 = model1.copy()
        >>> print(model2.get_params())
        {'level': 0.90, 'threshold': 5.0, 'test_end_inclusive': False}

        Copy for comparison:

        >>> model1 = TBRAnalysis(level=0.80)
        >>> model1.fit(data1, ...)
        >>> model2 = model1.copy()
        >>> model2.set_params(level=0.95)
        >>> model2.fit(data2, ...)

        Notes
        -----
        The copy will not include any fitted state. Only configuration
        parameters (level, threshold, test_end_inclusive) are copied.
        """
        return TBRAnalysis(
            level=self.level,
            threshold=self.threshold,
            test_end_inclusive=self.test_end_inclusive,
        )

    def fit_predict(
        self,
        data: pd.DataFrame,
        time_col: str,
        control_col: str,
        test_col: str,
        pretest_start: Union[pd.Timestamp, int, float],
        test_start: Union[pd.Timestamp, int, float],
        test_end: Union[pd.Timestamp, int, float],
        control_values: Optional[Union[pd.Series, np.ndarray]] = None,
    ) -> TBRPredictionResult:
        """
        Fit model and immediately return predictions (convenience method).

        Combines fit() and predict() into a single method call for streamlined
        workflows. This is particularly useful for quick analysis without needing
        to store the model state.

        Parameters
        ----------
        data : pd.DataFrame
            Time series data with time, control, and test columns.
        time_col : str
            Name of the time column.
        control_col : str
            Name of control group metric column.
        test_col : str
            Name of test group metric column.
        pretest_start : Union[pd.Timestamp, int, float]
            Start time of pretest period (inclusive).
        test_start : Union[pd.Timestamp, int, float]
            Start time of test period (inclusive).
        test_end : Union[pd.Timestamp, int, float]
            End time of test period (inclusive/exclusive based on test_end_inclusive).
        control_values : Union[pd.Series, np.ndarray, list], optional
            Control group values to generate predictions for. If None, uses
            control values from the test period.

        Returns
        -------
        TBRPredictionResult
            Prediction result object with predictions and metadata.

        Examples
        --------
        One-line prediction without storing model:

        >>> predictions = TBRAnalysis().fit_predict(
        ...     data, 'date', 'control', 'test',
        ...     pretest_start='2023-01-01',
        ...     test_start='2023-02-15',
        ...     test_end='2023-03-01'
        ... )
        >>> print(f"Mean prediction: {predictions.mean_pred:.2f}")

        Notes
        -----
        This is equivalent to calling `fit()` followed by `predict()`, but
        more concise for workflows where only predictions are needed.
        """
        self.fit(
            data, time_col, control_col, test_col, pretest_start, test_start, test_end
        )
        return self.predict(control_values)

    def fit_summarize(
        self,
        data: pd.DataFrame,
        time_col: str,
        control_col: str,
        test_col: str,
        pretest_start: Union[pd.Timestamp, int, float],
        test_start: Union[pd.Timestamp, int, float],
        test_end: Union[pd.Timestamp, int, float],
    ) -> TBRSummaryResult:
        """
        Fit model and immediately return final summary (convenience method).

        Combines fit() and summarize() into a single method call for streamlined
        workflows. This is particularly useful for quick analysis when only the
        final summary statistics are needed.

        Parameters
        ----------
        data : pd.DataFrame
            Time series data with time, control, and test columns.
        time_col : str
            Name of the time column.
        control_col : str
            Name of control group metric column.
        test_col : str
            Name of test group metric column.
        pretest_start : Union[pd.Timestamp, int, float]
            Start time of pretest period (inclusive).
        test_start : Union[pd.Timestamp, int, float]
            Start time of test period (inclusive).
        test_end : Union[pd.Timestamp, int, float]
            End time of test period (inclusive/exclusive based on test_end_inclusive).

        Returns
        -------
        TBRSummaryResult
            Final summary result object with all statistics.

        Examples
        --------
        One-line summary without storing model:

        >>> summary = TBRAnalysis(level=0.95).fit_summarize(
        ...     data, 'date', 'control', 'test',
        ...     pretest_start='2023-01-01',
        ...     test_start='2023-02-15',
        ...     test_end='2023-03-01'
        ... )
        >>> print(f"Effect: {summary.estimate:.2f}")
        >>> print(f"Significant: {summary.is_significant()}")

        Quick analysis with method chaining:

        >>> effect = (TBRAnalysis()
        ...           .set_params(level=0.90, threshold=5.0)
        ...           .fit_summarize(data, 'date', 'control', 'test', ...)
        ...           .estimate)

        Notes
        -----
        This is equivalent to calling `fit()` followed by `summarize()`, but
        more concise for workflows where only the final summary is needed.
        """
        self.fit(
            data, time_col, control_col, test_col, pretest_start, test_start, test_end
        )
        return self.summarize()

    def predict(
        self,
        control_values: Optional[Union[pd.Series, np.ndarray]] = None,
    ) -> TBRPredictionResult:
        """
        Generate counterfactual predictions using the fitted TBR model.

        Predicts what the test group values would have been without treatment,
        using the regression relationship learned from the pretest period.

        Parameters
        ----------
        control_values : Union[pd.Series, np.ndarray, list], optional
            Control group values to generate predictions for. If None (default),
            uses control values from the test period of the fitted data.
            Can be a numpy array, pandas Series, or Python list.

        Returns
        -------
        TBRPredictionResult
            Result object containing:
            - predictions: DataFrame with pred and predsd columns
            - n_predictions: Number of predictions generated
            - model_params: Model parameters used
            - control_values: Control values used for predictions

        Raises
        ------
        AttributeError
            If the model has not been fitted yet.
        TypeError
            If control_values has invalid type.
        ValueError
            If control_values has invalid shape, is empty, or contains non-finite values.

        Examples
        --------
        Predict using fitted test period data:

        >>> model = TBRAnalysis(level=0.80)
        >>> model.fit(data, 'date', 'control', 'test', ...)
        >>> result = model.predict()
        >>> print(result.predictions.head())
        >>> print(f"Generated {result.n_predictions} predictions")

        Predict for new control values:

        >>> new_control = np.array([1000, 1050, 1100])
        >>> result = model.predict(control_values=new_control)
        >>> print(f"Mean prediction: {result.predictions['pred'].mean():.2f}")

        Access underlying data:

        >>> predictions_df = result.predictions
        >>> result_dict = result.to_dict()

        Notes
        -----
        Predictions are generated using the fitted regression model:
        pred = alpha + beta * control_value

        Prediction standard deviation includes both model and residual uncertainty:
        predsd = sqrt(sigma^2 * (1 + 1/n + (x* - x̄)^2 / Σ(xi - x̄)^2))
        """
        # Check if model is fitted
        if not self._fitted:
            raise AttributeError(
                "This TBRAnalysis instance is not fitted yet. "
                "Call 'fit' with appropriate arguments before using predict()."
            )

        # Lazy imports
        from tbr.core.prediction import generate_counterfactual_predictions

        assert self._results is not None
        assert self._params is not None

        # Use test period control values if not provided
        if control_values is None:
            test_period = self._results[self._results["period"] == 1]
            control_values = test_period["x"].values
        else:
            # Convert to numpy array if needed
            if isinstance(control_values, pd.Series):
                control_values = control_values.values
            elif isinstance(control_values, list):
                control_values = np.array(control_values)
            elif not isinstance(control_values, np.ndarray):
                try:
                    control_values = np.array(control_values)
                except (ValueError, TypeError) as e:
                    raise TypeError(
                        f"control_values must be array-like (numpy array, pandas Series, or list), "
                        f"got {type(control_values).__name__}"
                    ) from e

        # Validate control values type and dimensions
        if not np.issubdtype(control_values.dtype, np.number):
            raise TypeError(
                f"control_values must contain numeric values, "
                f"got dtype '{control_values.dtype}'"
            )

        if control_values.ndim != 1:
            raise ValueError(
                f"control_values must be 1-dimensional, got {control_values.ndim}-dimensional "
                f"array with shape {control_values.shape}"
            )

        if len(control_values) == 0:
            raise ValueError("control_values cannot be empty")

        if not np.all(np.isfinite(control_values)):
            n_invalid = np.sum(~np.isfinite(control_values))
            raise ValueError(
                f"control_values must contain only finite values, "
                f"found {n_invalid} non-finite value(s)"
            )

        # Create test period DataFrame for predictions
        assert self._fit_info is not None
        test_period_data = pd.DataFrame(
            {
                self._fit_info["time_col"]: range(len(control_values)),
                self._fit_info["control_col"]: control_values,
            }
        )

        # Generate predictions using core functionality
        predictions = generate_counterfactual_predictions(
            alpha=self._params["alpha"],
            beta=self._params["beta"],
            sigma=self._params["sigma"],
            n_pretest=self._params["degrees_freedom"] + 2,
            pretest_x_mean=self._params["pretest_x_mean"],
            pretest_sum_x_squared_deviations=self._params[
                "pretest_sum_x_squared_deviations"
            ],
            test_period_data=test_period_data,
            control_col=self._fit_info["control_col"],
            time_col=self._fit_info["time_col"],
        )

        # Create and return TBRPredictionResult
        return TBRPredictionResult(
            predictions=predictions[["pred", "predsd"]].copy(),
            n_predictions=len(control_values),
            model_params=dict(self._params),
            control_values=control_values.copy(),
        )

    def summarize(self) -> TBRSummaryResult:
        """
        Get final cumulative summary statistics from the TBR analysis.

        Returns the final (cumulative) treatment effect summary with credible
        intervals, posterior probabilities, and model parameters.

        Returns
        -------
        TBRSummaryResult
            Result object containing:
            - estimate, lower, upper: Effect estimate and credible interval
            - se, prob, precision: Standard error, probability, precision
            - level, threshold: Configuration parameters
            - Model parameters (alpha, beta, sigma, variances, etc.)

        Raises
        ------
        AttributeError
            If the model has not been fitted yet.

        Examples
        --------
        Get final summary:

        >>> model = TBRAnalysis(level=0.80, threshold=0.0)
        >>> model.fit(data, 'date', 'control', 'test', ...)
        >>> result = model.summarize()
        >>> print(f"Effect: {result.estimate:.2f}")
        >>> print(f"CI: [{result.lower:.2f}, {result.upper:.2f}]")
        >>> print(f"Significant: {result.is_significant()}")

        Access summary as DataFrame or dict:

        >>> summary_df = result.to_dataframe()
        >>> summary_dict = result.to_dict()

        See Also
        --------
        summarize_incremental : Get day-by-day incremental summaries

        Notes
        -----
        The summary statistics are computed from the incremental summaries
        stored during fit(). This returns the last row of the incremental
        summaries as a structured result object.
        """
        # Check if model is fitted
        if not self._fitted:
            raise AttributeError(
                "This TBRAnalysis instance is not fitted yet. "
                "Call 'fit' with appropriate arguments before using summarize()."
            )

        assert self._summaries is not None

        # Extract final summary (last row) as TBRSummaryResult
        final_row = self._summaries.iloc[-1]
        return TBRSummaryResult(
            estimate=float(final_row["estimate"]),
            lower=float(final_row["lower"]),
            upper=float(final_row["upper"]),
            se=float(final_row["se"]),
            prob=float(final_row["prob"]),
            precision=float(final_row["precision"]),
            level=float(final_row["level"]),
            threshold=float(final_row["thres"]),
            alpha=float(final_row["alpha"]),
            beta=float(final_row["beta"]),
            sigma=float(final_row["sigma"]),
            var_alpha=float(final_row["var_alpha"]),
            var_beta=float(final_row["var_beta"]),
            cov_alpha_beta=float(
                final_row["alpha_beta_cov"]
            ),  # DataFrame column is alpha_beta_cov
            degrees_freedom=int(
                final_row["t_dist_df"]
            ),  # DataFrame column is t_dist_df
        )

    def summarize_incremental(self) -> pd.DataFrame:
        """
        Get day-by-day incremental summaries for the test period.

        Returns incremental summaries showing the progression of cumulative
        treatment effects as each day of the test period is added.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
            - test_day: Day number in test period
            - estimate: Cumulative treatment effect
            - precision: 1/variance of the estimate
            - lower, upper: Credible interval bounds
            - se: Standard error of the estimate
            - level: Credibility level used
            - thres: Threshold used for probability calculation
            - prob: Posterior probability of exceeding threshold
            - Model parameters (alpha, beta, sigma, variances, covariances)

        Raises
        ------
        AttributeError
            If the model has not been fitted yet.

        Examples
        --------
        Get incremental summaries:

        >>> model = TBRAnalysis(level=0.90, threshold=0.0)
        >>> model.fit(data, 'date', 'control', 'test', ...)
        >>> incremental = model.summarize_incremental()
        >>> print(incremental[['test_day', 'estimate', 'lower', 'upper']])

        Plot progression over time:

        >>> import matplotlib.pyplot as plt
        >>> plt.plot(incremental['test_day'], incremental['estimate'])
        >>> plt.fill_between(incremental['test_day'],
        ...                  incremental['lower'], incremental['upper'], alpha=0.3)

        See Also
        --------
        summarize : Get final cumulative summary as result object

        Notes
        -----
        Each row represents the cumulative effect from the start of the test
        period through that day. The last row matches the final summary
        returned by summarize().
        """
        # Check if model is fitted
        if not self._fitted:
            raise AttributeError(
                "This TBRAnalysis instance is not fitted yet. "
                "Call 'fit' with appropriate arguments before using summarize_incremental()."
            )

        assert self._summaries is not None

        return self._summaries.copy()

    def analyze_subinterval(
        self,
        start_day: int,
        end_day: int,
        ci_level: Optional[float] = None,
    ) -> TBRSubintervalResult:
        """
        Analyze treatment effect for a custom subinterval of the test period.

        Computes the treatment effect estimate and credible interval for a
        specific range of days within the test period.

        Parameters
        ----------
        start_day : int
            Starting day of the subinterval (1-indexed, inclusive).
            Day 1 is the first day of the test period.
        end_day : int
            Ending day of the subinterval (1-indexed, inclusive).
        ci_level : float, optional
            Credibility level for credible interval (must be between 0 and 1).
            If None, uses the level specified during initialization.

        Returns
        -------
        TBRSubintervalResult
            Result object containing:
            - estimate: Treatment effect for the subinterval
            - lower, upper: Credible interval bounds
            - se: Standard error of the estimate
            - ci_level: Credibility level used
            - start_day, end_day, n_days: Interval specification

        Raises
        ------
        AttributeError
            If the model has not been fitted yet.
        TypeError
            If start_day, end_day, or ci_level have invalid types.
        ValueError
            If start_day or end_day are invalid, start_day > end_day, days exceed
            test period, or ci_level is not between 0 and 1.

        Examples
        --------
        Analyze first week of test period:

        >>> model = TBRAnalysis(level=0.80)
        >>> model.fit(data, 'date', 'control', 'test', ...)
        >>> result = model.analyze_subinterval(start_day=1, end_day=7)
        >>> print(f"Week 1 effect: {result.estimate:.2f}")
        >>> print(f"Week 1 CI: [{result.lower:.2f}, {result.upper:.2f}]")
        >>> print(f"Significant: {result.is_positive()}")

        Analyze with custom credibility level:

        >>> result = model.analyze_subinterval(start_day=8, end_day=14, ci_level=0.95)
        >>> if result.contains_zero():
        ...     print("Effect not significant")

        Access underlying data:

        >>> result_dict = result.to_dict()

        Notes
        -----
        Subinterval analysis uses the compute_interval_estimate_and_ci function
        from the analysis module to calculate effects for specific day ranges
        with proper variance calculations.
        """
        # Check if model is fitted
        if not self._fitted:
            raise AttributeError(
                "This TBRAnalysis instance is not fitted yet. "
                "Call 'fit' with appropriate arguments before using analyze_subinterval()."
            )

        # Lazy imports
        from tbr.analysis.subinterval import compute_interval_estimate_and_ci
        from tbr.utils.validation import validate_probability_level

        assert self._results is not None
        assert self._params is not None

        # Validate day parameter types
        if not isinstance(start_day, (int, np.integer)):
            raise TypeError(
                f"start_day must be an integer, got {type(start_day).__name__}"
            )

        if not isinstance(end_day, (int, np.integer)):
            raise TypeError(f"end_day must be an integer, got {type(end_day).__name__}")

        # Convert numpy integers to Python int
        start_day = int(start_day)
        end_day = int(end_day)

        # Validate day parameter values
        if start_day < 1:
            raise ValueError(
                f"start_day must be a positive integer (>= 1), got {start_day}"
            )

        if end_day < 1:
            raise ValueError(
                f"end_day must be a positive integer (>= 1), got {end_day}"
            )

        if start_day > end_day:
            raise ValueError(f"start_day ({start_day}) must be <= end_day ({end_day})")

        # Check if days are within test period
        n_test_days = len(self._results[self._results["period"] == 1])

        if start_day > n_test_days:
            raise ValueError(
                f"start_day ({start_day}) exceeds test period length ({n_test_days} days)"
            )

        if end_day > n_test_days:
            raise ValueError(
                f"end_day ({end_day}) exceeds test period length ({n_test_days} days)"
            )

        # Use model's level if not provided, otherwise validate ci_level
        if ci_level is None:
            ci_level = self.level
        else:
            if not isinstance(ci_level, (int, float)):
                raise TypeError(
                    f"ci_level must be numeric, got {type(ci_level).__name__}"
                )
            validate_probability_level(ci_level, "ci_level")

        # Compute subinterval estimate
        result = compute_interval_estimate_and_ci(
            tbr_df=self._results,
            tbr_summary=self._summaries,
            start_day=start_day,
            end_day=end_day,
            ci_level=ci_level,
        )

        # Calculate standard error from precision (half-width of CI)
        se = result["precision"]

        # Create and return TBRSubintervalResult
        return TBRSubintervalResult(
            estimate=result["estimate"],
            lower=result["lower"],
            upper=result["upper"],
            se=se,
            ci_level=ci_level,
            start_day=start_day,
            end_day=end_day,
            n_days=end_day - start_day + 1,
        )

    @property
    def final_summary(self) -> TBRSummaryResult:
        """
        Get final summary as a result object (convenience property).

        Equivalent to `summarize()` but more concise.

        Returns
        -------
        TBRSummaryResult
            Final cumulative summary with all statistics.

        Raises
        ------
        AttributeError
            If the model has not been fitted yet.

        Examples
        --------
        >>> model = TBRAnalysis()
        >>> model.fit(data, 'date', 'control', 'test', ...)
        >>> summary = model.final_summary
        >>> print(f"Effect: {summary.estimate:.2f}")
        """
        return self.summarize()

    @property
    def final_effect(self) -> float:
        """
        Get final cumulative treatment effect estimate (convenience property).

        Returns
        -------
        float
            Final cumulative treatment effect.

        Raises
        ------
        AttributeError
            If the model has not been fitted yet.

        Examples
        --------
        >>> model = TBRAnalysis()
        >>> model.fit(data, 'date', 'control', 'test', ...)
        >>> print(f"Treatment effect: {model.final_effect:.2f}")
        """
        return self.final_summary.estimate

    @property
    def fitted_(self) -> bool:
        """
        Whether the model has been fitted.

        Returns
        -------
        bool
            True if fit() has been called successfully, False otherwise.
        """
        return self._fitted

    @property
    def results_(self) -> pd.DataFrame:
        """
        TBR DataFrame with predictions, effects, and uncertainties.

        This DataFrame contains the complete time series with all TBR calculations:
        - Original data (time, control, test values)
        - Period indicators (pretest=0, test=1, cooldown=3)
        - Counterfactual predictions (pred, predsd)
        - Effects (dif, cumdif, cumsd, estsd)

        Returns
        -------
        pd.DataFrame
            Complete TBR analysis results DataFrame.

        Raises
        ------
        AttributeError
            If the model has not been fitted yet.

        Examples
        --------
        >>> model = TBRAnalysis()
        >>> model.fit(data, 'date', 'control', 'test', ...)
        >>> results = model.results_
        >>> test_period_results = results[results['period'] == 1]
        """
        if not self._fitted:
            raise AttributeError(
                "This TBRAnalysis instance is not fitted yet. "
                "Call 'fit' with appropriate arguments before accessing results_."
            )
        assert self._results is not None  # Guaranteed by _fitted check
        return self._results

    @property
    def summaries_(self) -> pd.DataFrame:
        """
        Incremental summaries with daily progression of cumulative effects.

        This DataFrame contains day-by-day summaries for the test period:
        - estimate: Cumulative treatment effect
        - precision: 1/variance of the estimate
        - lower, upper: Credible interval bounds
        - se: Standard error of the estimate
        - level: Credibility level used
        - threshold: Threshold used for probability calculation
        - prob: Posterior probability of exceeding threshold
        - Model parameters (alpha, beta, sigma, variances, covariances)

        Returns
        -------
        pd.DataFrame
            Incremental summaries for each day of the test period.

        Raises
        ------
        AttributeError
            If the model has not been fitted yet.

        Examples
        --------
        >>> model = TBRAnalysis()
        >>> model.fit(data, 'date', 'control', 'test', ...)
        >>> summaries = model.summaries_
        >>> final_effect = summaries.iloc[-1]['estimate']
        >>> is_significant = summaries.iloc[-1]['lower'] > 0
        """
        if not self._fitted:
            raise AttributeError(
                "This TBRAnalysis instance is not fitted yet. "
                "Call 'fit' with appropriate arguments before accessing summaries_."
            )
        assert self._summaries is not None  # Guaranteed by _fitted check
        return self._summaries

    @property
    def params_(self) -> Dict[str, Any]:
        """
        Regression model parameters from TBR analysis.

        Returns
        -------
        dict
            Dictionary containing regression parameters:
            - alpha: Intercept coefficient
            - beta: Slope coefficient
            - sigma: Residual standard error
            - var_alpha: Variance of alpha
            - var_beta: Variance of beta
            - cov_alpha_beta: Covariance between alpha and beta
            - degrees_freedom: Degrees of freedom for t-distribution
            - pretest_x_mean: Mean of control in pretest period
            - pretest_sum_x_squared_deviations: Sum of squared deviations

        Raises
        ------
        AttributeError
            If the model has not been fitted yet.

        Examples
        --------
        >>> model = TBRAnalysis()
        >>> model.fit(data, 'date', 'control', 'test', ...)
        >>> params = model.params_
        >>> print(f"Beta coefficient: {params['beta']:.4f}")
        >>> print(f"Residual std error: {params['sigma']:.4f}")
        """
        if not self._fitted:
            raise AttributeError(
                "This TBRAnalysis instance is not fitted yet. "
                "Call 'fit' with appropriate arguments before accessing params_."
            )
        assert self._params is not None  # Guaranteed by _fitted check
        return self._params

    def __repr__(self) -> str:
        """
        Return string representation of TBRAnalysis instance.

        Returns
        -------
        str
            String representation showing configuration and fitted status.
        """
        fitted_str = "fitted" if self._fitted else "not fitted"
        return (
            f"TBRAnalysis(level={self.level}, threshold={self.threshold}, "
            f"test_end_inclusive={self.test_end_inclusive}, {fitted_str})"
        )

    def __str__(self) -> str:
        """
        Return user-friendly string representation.

        Returns
        -------
        str
            Human-readable string with key information.
        """
        if not self._fitted:
            return f"TBRAnalysis (not fitted)\n  level={self.level}\n  threshold={self.threshold}"

        assert self._summaries is not None  # Guaranteed by _fitted check
        n_test_days = len(self._summaries)
        final_effect = self._summaries.iloc[-1]["estimate"]
        final_lower = self._summaries.iloc[-1]["lower"]
        final_upper = self._summaries.iloc[-1]["upper"]

        return (
            f"TBRAnalysis (fitted)\n"
            f"  Configuration:\n"
            f"    level={self.level}\n"
            f"    threshold={self.threshold}\n"
            f"  Results:\n"
            f"    Test period days: {n_test_days}\n"
            f"    Final effect estimate: {final_effect:.2f}\n"
            f"    {int(self.level*100)}% CI: [{final_lower:.2f}, {final_upper:.2f}]"
        )
