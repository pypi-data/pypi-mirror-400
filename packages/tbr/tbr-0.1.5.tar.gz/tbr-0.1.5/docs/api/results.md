# TBR Result Objects

Comprehensive guide to understanding and working with TBR result objects.

## Overview

The TBR package uses immutable result objects (frozen dataclasses) to return analysis results. This design ensures:

- **Type Safety**: Clear return types with IDE autocomplete support
- **Immutability**: Results cannot be accidentally modified
- **Rich Functionality**: Helper methods for common operations
- **Easy Export**: Built-in JSON/CSV export capabilities

## Result Object Types

### 1. TBRSummaryResult

Returned by: `summarize()`, `fit_summarize()`, `final_summary`

**Description**: Contains cumulative treatment effect statistics for the entire test period.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `estimate` | float | Cumulative treatment effect |
| `lower` | float | Lower bound of credible interval |
| `upper` | float | Upper bound of credible interval |
| `se` | float | Standard error |
| `prob` | float | Posterior probability (effect > threshold) |
| `precision` | float | Half-width of credible interval (margin of error) |
| `level` | float | Credibility level used |
| `threshold` | float | Threshold used for probability |
| `alpha` | float | Regression intercept |
| `beta` | float | Regression slope |
| `sigma` | float | Residual standard error |
| `var_alpha` | float | Variance of alpha |
| `var_beta` | float | Variance of beta |
| `cov_alpha_beta` | float | Covariance of alpha and beta |
| `degrees_freedom` | int | Degrees of freedom for t-distribution |

#### Methods

```python
# Check if effect is significant (lower > 0)
is_significant = summary.is_significant()  # Returns: bool

# Convert to dictionary
data_dict = summary.to_dict()  # Returns: dict

# Convert to DataFrame (single row)
df = summary.to_dataframe()  # Returns: pd.DataFrame

# Export to JSON
summary.to_json('results.json')

# Export to CSV
summary.to_csv('results.csv')
```

#### Example Usage

```python
summary = model.summarize()

# Basic information
print(f"Effect: {summary.estimate:.2f}")
print(f"CI: [{summary.lower:.2f}, {summary.upper:.2f}]")
print(f"P(effect > 0): {summary.prob:.3f}")

# Check significance
if summary.is_significant():
    print("✓ Statistically significant effect detected")
else:
    print("✗ Effect not statistically significant")

# Regression diagnostics
print(f"Model: y = {summary.alpha:.2f} + {summary.beta:.4f}x")
print(f"Residual SE: {summary.sigma:.2f}")
print(f"Degrees of freedom: {summary.degrees_freedom}")

# Export
summary.to_json('analysis_results.json')
```

---

### 2. TBRPredictionResult

Returned by: `predict()`, `fit_predict()`

**Description**: Contains counterfactual predictions and uncertainty estimates.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `predictions` | pd.DataFrame | Predictions with `pred` and `predsd` columns |
| `n_predictions` | int | Number of predictions |
| `model_params` | dict | Model parameters used |
| `control_values` | np.ndarray | Control values used |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `mean_pred` | float | Average prediction |
| `mean_uncertainty` | float | Average prediction std deviation |

#### Methods

```python
# Convert to dictionary
data_dict = result.to_dict()

# Convert to DataFrame
df = result.to_dataframe()

# Export to JSON
result.to_json('predictions.json')

# Export to CSV
result.to_csv('predictions.csv')
```

#### Example Usage

```python
predictions = model.predict()

# Summary statistics
print(f"Number of predictions: {predictions.n_predictions}")
print(f"Mean prediction: {predictions.mean_pred:.2f}")
print(f"Mean uncertainty: {predictions.mean_uncertainty:.2f}")

# Access predictions DataFrame
preds_df = predictions.predictions
print("\nFirst 5 predictions:")
print(preds_df.head())

# Plot predictions with uncertainty
import matplotlib.pyplot as plt
plt.plot(preds_df.index, preds_df['pred'], label='Prediction')
plt.fill_between(preds_df.index,
                 preds_df['pred'] - preds_df['predsd'],
                 preds_df['pred'] + preds_df['predsd'],
                 alpha=0.3, label='±1 SD')
plt.legend()

# Export
predictions.to_csv('counterfactual_predictions.csv')
```

---

### 3. TBRSubintervalResult

Returned by: `analyze_subinterval()`

**Description**: Contains treatment effect estimates for a specific time window within the test period.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `estimate` | float | Subinterval treatment effect |
| `lower` | float | Lower CI bound |
| `upper` | float | Upper CI bound |
| `se` | float | Standard error |
| `ci_level` | float | Credibility level used |
| `start_day` | int | Starting day (1-indexed) |
| `end_day` | int | Ending day (1-indexed) |
| `n_days` | int | Number of days in interval |

#### Methods

```python
# Check if interval contains zero
contains_zero = result.contains_zero()  # Returns: bool

# Check if effect is positive (lower > 0)
is_positive = result.is_positive()  # Returns: bool

# Check if effect is negative (upper < 0)
is_negative = result.is_negative()  # Returns: bool

# Convert to dictionary
data_dict = result.to_dict()

# Export to JSON
result.to_json('subinterval.json')

# Export to CSV
result.to_csv('subinterval.csv')
```

#### Example Usage

```python
# Analyze first week
week1 = model.analyze_subinterval(start_day=1, end_day=7)

# Basic information
print(f"Week 1 (Days {week1.start_day}-{week1.end_day}):")
print(f"  Effect: {week1.estimate:.2f}")
print(f"  CI ({week1.ci_level*100:.0f}%): [{week1.lower:.2f}, {week1.upper:.2f}]")
print(f"  SE: {week1.se:.2f}")

# Interpretation
if week1.is_positive():
    print("  ✓ Positive effect detected")
elif week1.is_negative():
    print("  ✓ Negative effect detected")
else:
    print("  ✗ Effect not significant (interval contains zero)")

# Compare multiple intervals
week2 = model.analyze_subinterval(start_day=8, end_day=14)

if week2.estimate > week1.estimate:
    improvement = ((week2.estimate - week1.estimate) / week1.estimate) * 100
    print(f"\nWeek 2 shows {improvement:.1f}% stronger effect than Week 1")

# Export
week1.to_json('week1_analysis.json')
```

---

## Common Patterns

### Pattern 1: Quick Summary Check

```python
summary = model.summarize()

if summary.is_significant() and summary.prob > 0.95:
    print(f"Strong evidence of positive effect: {summary.estimate:.2f}")
elif summary.is_significant():
    print(f"Moderate evidence of positive effect: {summary.estimate:.2f}")
else:
    print("No significant effect detected")
```

### Pattern 2: Comparing Subintervals

```python
# Analyze multiple periods
early = model.analyze_subinterval(1, 15)
late = model.analyze_subinterval(16, 30)

# Compare
periods = pd.DataFrame({
    'Period': ['Early (1-15)', 'Late (16-30)'],
    'Effect': [early.estimate, late.estimate],
    'Lower': [early.lower, late.lower],
    'Upper': [early.upper, late.upper],
    'Significant': [early.is_positive(), late.is_positive()]
})

print(periods)
```

### Pattern 3: Exporting All Results

```python
# Fit model
model.fit(...)

# Export everything
model.summarize().to_json('summary.json')
model.predict().to_csv('predictions.csv')

# Export subintervals
for week in range(1, 5):
    start = (week - 1) * 7 + 1
    end = week * 7
    result = model.analyze_subinterval(start, end)
    result.to_json(f'week_{week}.json')
```

### Pattern 4: Result DataFrame Conversion

```python
# Convert all result types to DataFrames
summary_df = model.summarize().to_dataframe()
predictions_df = model.predict().to_dataframe()

# Subinterval to dict then DataFrame
week1_dict = model.analyze_subinterval(1, 7).to_dict()
week1_df = pd.DataFrame([week1_dict])
```

### Pattern 5: Accessing Model Parameters

```python
summary = model.summarize()

# Regression equation
print(f"Model: test = {summary.alpha:.2f} + {summary.beta:.4f} × control")

# Parameter uncertainty
print(f"α variance: {summary.var_alpha:.4f}")
print(f"β variance: {summary.var_beta:.4f}")
print(f"Covariance: {summary.cov_alpha_beta:.4f}")

# Model quality
print(f"Residual SE: {summary.sigma:.2f}")
print(f"Degrees of freedom: {summary.degrees_freedom}")
```

---

## Result Object Comparison

| Feature | TBRSummaryResult | TBRPredictionResult | TBRSubintervalResult |
|---------|------------------|---------------------|----------------------|
| **Scope** | Full test period | Test period predictions | Custom time window |
| **Primary Use** | Overall effect | Counterfactuals | Temporal analysis |
| **Key Attribute** | `estimate` | `predictions` (DataFrame) | `estimate` |
| **Statistical Info** | Comprehensive | Limited | Moderate |
| **Helper Methods** | `is_significant()` | `mean_pred`, `mean_uncertainty` | `is_positive()`, `is_negative()`, `contains_zero()` |
| **Export Options** | JSON, CSV | JSON, CSV | JSON, CSV |

---

## Tips and Best Practices

### 1. Result Immutability

Result objects are **frozen** (immutable). This is intentional and prevents accidental modification:

```python
summary = model.summarize()

# This will raise an error:
# summary.estimate = 100  # FrozenInstanceError

# Instead, create a new analysis:
model.set_params(level=0.95).fit(...)
new_summary = model.summarize()
```

### 2. Type Hints and IDE Support

All result objects have complete type hints for excellent IDE support:

```python
from tbr import TBRAnalysis
from tbr.core.results import TBRSummaryResult

def analyze_data(model: TBRAnalysis) -> TBRSummaryResult:
    return model.fit(...).summarize()

# IDE will autocomplete all attributes and methods
```

### 3. Converting to Other Formats

All result objects support conversion to common formats:

```python
# To dictionary
data_dict = result.to_dict()

# To DataFrame (preserves structure)
df = result.to_dataframe()

# To JSON (with metadata)
result.to_json('output.json', include_metadata=True)

# To CSV (flattens structure)
result.to_csv('output.csv')
```

### 4. Accessing Raw Data

For advanced use cases, access the underlying data:

```python
# Summary: all attributes accessible
summary = model.summarize()
effect = summary.estimate
ci_lower = summary.lower

# Predictions: DataFrame is the main data
predictions = model.predict()
pred_values = predictions.predictions['pred'].values
control_used = predictions.control_values

# Subinterval: effect and bounds
interval = model.analyze_subinterval(1, 7)
interval_effect = interval.estimate
interval_days = interval.n_days
```

### 5. Combining Results

Create comprehensive reports by combining multiple result types:

```python
# Collect all results
results = {
    'summary': model.summarize().to_dict(),
    'predictions': model.predict().to_dict(),
    'week1': model.analyze_subinterval(1, 7).to_dict(),
    'week2': model.analyze_subinterval(8, 14).to_dict(),
}

# Export as single JSON
import json
with open('complete_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)
```

---

## See Also

- **[API Reference](api_reference.md)** - Complete API documentation
- **[Quick Start](quickstart.md)** - Getting started guide
- **[Examples](../../examples/)** - Practical examples
- **[Common Patterns](patterns.md)** - Best practices
