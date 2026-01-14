# TBR API Reference

Complete reference documentation for the Time-Based Regression (TBR) Python package.

## Table of Contents

- [TBRAnalysis](#tbranalysis)
  - [Initialization](#initialization)
  - [Methods](#methods)
  - [Properties](#properties)
- [Result Objects](#result-objects)
  - [TBRSummaryResult](#tbrsummaryresult)
  - [TBRPredictionResult](#tbrpredictionresult)
  - [TBRSubintervalResult](#tbrsubintervalresult)
- [Functional API](#functional-api)
- [Utility Functions](#utility-functions)

---

## TBRAnalysis

The main class for performing Time-Based Regression analysis.

### Initialization

```python
TBRAnalysis(level=0.80, threshold=0.0, test_end_inclusive=False)
```

**Parameters:**

- **level** (*float*, default=0.80): Credibility level for credible intervals
  - Must be between 0 and 1 (exclusive)
  - Common values: 0.80 (80%), 0.90 (90%), 0.95 (95%)

- **threshold** (*float*, default=0.0): Threshold for probability calculations
  - Typically 0.0 for testing positive effects
  - Can be any finite float value

- **test_end_inclusive** (*bool*, default=False): Whether to include test_end boundary
  - False: Exclusive end (data < test_end)
  - True: Inclusive end (data <= test_end)

**Example:**

```python
from tbr import TBRAnalysis

# Default configuration
model = TBRAnalysis()

# Custom configuration
model = TBRAnalysis(level=0.95, threshold=5.0, test_end_inclusive=True)
```

---

### Methods

#### fit()

Fit the TBR model to data.

```python
model.fit(data, time_col, control_col, test_col,
          pretest_start, test_start, test_end)
```

**Parameters:**

- **data** (*pd.DataFrame*): Time series data
- **time_col** (*str*): Name of time column (datetime64[ns], int64, or float64)
- **control_col** (*str*): Name of control group metric column
- **test_col** (*str*): Name of test group metric column
- **pretest_start** (*Timestamp/int/float*): Start of pretest period (inclusive)
- **test_start** (*Timestamp/int/float*): Start of test period (inclusive)
- **test_end** (*Timestamp/int/float*): End of test period

**Returns:** `self` (for method chaining)

**Example:**

```python
model.fit(
    data=df,
    time_col='date',
    control_col='control_sales',
    test_col='test_sales',
    pretest_start='2024-01-01',
    test_start='2024-02-15',
    test_end='2024-03-31'
)
```

---

#### predict()

Generate counterfactual predictions.

```python
model.predict(control_values=None)
```

**Parameters:**

- **control_values** (*array-like*, optional): Control values for predictions
  - If None: Uses test period control values from fitted data
  - Accepts: numpy array, pandas Series, or Python list

**Returns:** `TBRPredictionResult` object

**Example:**

```python
# Use fitted test period data
result = model.predict()

# Custom control values
custom_control = [1000, 1050, 1100]
result = model.predict(control_values=custom_control)

# Access predictions
print(result.predictions)  # DataFrame with pred and predsd columns
print(f"Mean prediction: {result.mean_pred:.2f}")
```

---

#### summarize()

Get final cumulative summary.

```python
model.summarize()
```

**Returns:** `TBRSummaryResult` object with final treatment effect

**Example:**

```python
summary = model.summarize()
print(f"Effect: {summary.estimate:.2f}")
print(f"CI: [{summary.lower:.2f}, {summary.upper:.2f}]")
print(f"Significant: {summary.is_significant()}")
```

---

#### summarize_incremental()

Get day-by-day incremental summaries.

```python
model.summarize_incremental()
```

**Returns:** `pd.DataFrame` with cumulative summaries for each test day

**Example:**

```python
incremental = model.summarize_incremental()
print(incremental[['test_day', 'estimate', 'lower', 'upper']])

# Plot progression
import matplotlib.pyplot as plt
plt.plot(incremental['test_day'], incremental['estimate'])
plt.fill_between(incremental['test_day'],
                 incremental['lower'], incremental['upper'], alpha=0.3)
```

---

#### analyze_subinterval()

Analyze effect for a custom time window.

```python
model.analyze_subinterval(start_day, end_day, ci_level=None)
```

**Parameters:**

- **start_day** (*int*): Starting day (1-indexed, inclusive)
- **end_day** (*int*): Ending day (1-indexed, inclusive)
- **ci_level** (*float*, optional): Credibility level (uses model's level if None)

**Returns:** `TBRSubintervalResult` object

**Example:**

```python
# Analyze first week
week1 = model.analyze_subinterval(start_day=1, end_day=7)
print(f"Week 1 effect: {week1.estimate:.2f}")
print(f"Significant: {week1.is_positive()}")

# Analyze with custom confidence level
week2 = model.analyze_subinterval(start_day=8, end_day=14, ci_level=0.95)
```

---

#### get_params()

Get model configuration parameters.

```python
model.get_params(deep=True)
```

**Parameters:**

- **deep** (*bool*, default=True): For sklearn compatibility (no effect)

**Returns:** `dict` with configuration parameters

**Example:**

```python
params = model.get_params()
print(params)
# {'level': 0.80, 'threshold': 0.0, 'test_end_inclusive': False}
```

---

#### set_params()

Update model configuration.

```python
model.set_params(**params)
```

**Parameters:**

- ****params**: Configuration parameters to update

**Returns:** `self` (for method chaining)

**Example:**

```python
# Update configuration
model.set_params(level=0.95, threshold=10.0)

# Method chaining
summary = (model
           .set_params(level=0.90)
           .fit(data, ...)
           .summarize())
```

---

#### copy()

Create a deep copy of the estimator.

```python
model.copy()
```

**Returns:** New `TBRAnalysis` instance with same configuration

**Example:**

```python
model1 = TBRAnalysis(level=0.80)
model2 = model1.copy()
model2.set_params(level=0.95)  # Doesn't affect model1
```

---

#### fit_predict()

Fit model and immediately return predictions (convenience method).

```python
model.fit_predict(data, time_col, control_col, test_col,
                  pretest_start, test_start, test_end,
                  control_values=None)
```

**Parameters:** Same as `fit()` plus optional `control_values`

**Returns:** `TBRPredictionResult` object

**Example:**

```python
# One-line fit and predict
predictions = model.fit_predict(data, 'date', 'control', 'test', ...)
print(f"Mean prediction: {predictions.mean_pred:.2f}")
```

---

#### fit_summarize()

Fit model and immediately return final summary (convenience method).

```python
model.fit_summarize(data, time_col, control_col, test_col,
                    pretest_start, test_start, test_end)
```

**Parameters:** Same as `fit()`

**Returns:** `TBRSummaryResult` object

**Example:**

```python
# One-line analysis
summary = TBRAnalysis(level=0.95).fit_summarize(
    data, 'date', 'control', 'test',
    pretest_start='2024-01-01',
    test_start='2024-02-15',
    test_end='2024-03-31'
)
print(f"Effect: {summary.estimate:.2f}")
```

---

### Properties

#### fitted_

Whether the model has been fitted.

```python
model.fitted_  # Returns: bool
```

---

#### results_

Complete TBR DataFrame with predictions and effects.

```python
model.results_  # Returns: pd.DataFrame
```

**Columns:**
- Original data columns
- `period`: 0=pretest, 1=test, 3=cooldown
- `pred`: Counterfactual predictions
- `predsd`: Prediction standard deviations
- `dif`: Daily effects (test - pred)
- `cumdif`: Cumulative effects
- `cumsd`: Cumulative standard deviations
- `estsd`: Effect standard deviations

**Example:**

```python
results = model.results_
test_period = results[results['period'] == 1]
print(test_period[['date', 'control', 'test', 'pred', 'dif']])
```

---

#### summaries_

Incremental summaries for each test day.

```python
model.summaries_  # Returns: pd.DataFrame
```

**Example:**

```python
summaries = model.summaries_
final_effect = summaries.iloc[-1]['estimate']
```

---

#### params_

Fitted regression model parameters.

```python
model.params_  # Returns: dict
```

**Keys:**
- `alpha`: Intercept
- `beta`: Slope
- `sigma`: Residual std error
- `var_alpha`: Variance of alpha
- `var_beta`: Variance of beta
- `cov_alpha_beta`: Covariance
- `degrees_freedom`: t-distribution df
- `pretest_x_mean`: Pretest control mean
- `pretest_sum_x_squared_deviations`: Sum squared deviations

---

#### final_summary

Final summary result (convenience property).

```python
model.final_summary  # Returns: TBRSummaryResult
```

Equivalent to `model.summarize()`.

---

#### final_effect

Final cumulative effect estimate (convenience property).

```python
model.final_effect  # Returns: float
```

Equivalent to `model.summarize().estimate`.

---

## Result Objects

### TBRSummaryResult

Immutable result object for TBR summary statistics.

**Attributes:**

- **estimate** (*float*): Cumulative treatment effect
- **lower** (*float*): Lower bound of credible interval
- **upper** (*float*): Upper bound of credible interval
- **se** (*float*): Standard error
- **prob** (*float*): Posterior probability (effect > threshold)
- **precision** (*float*): 1/variance
- **level** (*float*): Credibility level used
- **threshold** (*float*): Threshold used
- **alpha**, **beta**, **sigma**: Regression parameters
- **var_alpha**, **var_beta**, **cov_alpha_beta**: Parameter variances/covariances
- **degrees_freedom** (*int*): Degrees of freedom

**Methods:**

```python
summary.is_significant()     # Returns: bool (lower > 0)
summary.to_dict()           # Returns: dict
summary.to_dataframe()      # Returns: pd.DataFrame (single row)
summary.to_json(filepath)   # Export to JSON
summary.to_csv(filepath)    # Export to CSV
```

**Example:**

```python
summary = model.summarize()

# Check significance
if summary.is_significant():
    print(f"Significant effect: {summary.estimate:.2f}")
else:
    print("Effect not significant")

# Export
summary.to_json('results.json')
summary.to_csv('results.csv')
```

---

### TBRPredictionResult

Immutable result object for counterfactual predictions.

**Attributes:**

- **predictions** (*pd.DataFrame*): Predictions with `pred` and `predsd` columns
- **n_predictions** (*int*): Number of predictions
- **model_params** (*dict*): Model parameters used
- **control_values** (*np.ndarray*): Control values used

**Properties:**

- **mean_pred** (*float*): Average prediction
- **mean_uncertainty** (*float*): Average prediction std deviation

**Methods:**

```python
result.to_dict()           # Returns: dict
result.to_dataframe()      # Returns: pd.DataFrame
result.to_json(filepath)   # Export to JSON
result.to_csv(filepath)    # Export to CSV
```

**Example:**

```python
predictions = model.predict()

print(f"Mean prediction: {predictions.mean_pred:.2f}")
print(f"Mean uncertainty: {predictions.mean_uncertainty:.2f}")

# Access predictions
preds_df = predictions.predictions
print(preds_df.head())
```

---

### TBRSubintervalResult

Immutable result object for subinterval analysis.

**Attributes:**

- **estimate** (*float*): Subinterval treatment effect
- **lower** (*float*): Lower CI bound
- **upper** (*float*): Upper CI bound
- **se** (*float*): Standard error
- **ci_level** (*float*): Credibility level used
- **start_day**, **end_day**, **n_days** (*int*): Interval specification

**Methods:**

```python
result.contains_zero()    # Returns: bool (0 in CI)
result.is_positive()      # Returns: bool (lower > 0)
result.is_negative()      # Returns: bool (upper < 0)
result.to_dict()         # Returns: dict
result.to_json(filepath) # Export to JSON
result.to_csv(filepath)  # Export to CSV
```

**Example:**

```python
week1 = model.analyze_subinterval(1, 7)

if week1.is_positive():
    print(f"Positive effect in week 1: {week1.estimate:.2f}")
elif week1.contains_zero():
    print("Week 1 effect not significant")
```

---

## Functional API

For users who prefer a functional programming style:

```python
from tbr import perform_tbr_analysis

results = perform_tbr_analysis(
    data=df,
    time_col='date',
    control_col='control',
    test_col='test',
    pretest_start='2024-01-01',
    test_start='2024-02-15',
    test_end='2024-03-31',
    level=0.80,
    threshold=0.0
)

# Access results
tbr_df = results.tbr_dataframe()
summary_df = results.summary()
```

---

## Utility Functions

### Export Functions

```python
from tbr.utils import export_to_json, export_to_csv, load_json

# Export any result object
export_to_json(result, 'output.json', include_metadata=True)
export_to_csv(result, 'output.csv')

# Load JSON
data = load_json('output.json', extract_data=True)
```

### Constants

```python
from tbr import CONTROL_VAL, TEST_VAL

# Period indicators
CONTROL_VAL  # 0
TEST_VAL     # 1
```

---

## See Also

- **[Quick Start](quickstart.md)** - Getting started guide
- **[Examples](../../examples/)** - Domain-specific examples
- **[Common Patterns](patterns.md)** - Best practices
- **[Result Objects](results.md)** - Detailed result documentation
