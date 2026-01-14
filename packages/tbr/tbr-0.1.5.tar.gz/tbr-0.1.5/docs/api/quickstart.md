# TBR Quick Start Guide

Welcome to the Time-Based Regression (TBR) Python package! This guide will help you get started with analyzing treatment effects in time series data.

## Installation

```bash
pip install tbr
```

## Basic Usage

### 1. Import and Prepare Data

```python
import pandas as pd
from tbr import TBRAnalysis

# Create or load your time series data
# Required columns: time, control group metric, test group metric
data = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=90),
    'control': [1000, 1020, 980, ...],  # Control group values
    'test': [1010, 1035, 995, ...]      # Test group values
})
```

### 2. Initialize the Model

```python
# Create a TBR analysis instance
model = TBRAnalysis(
    level=0.80,        # 80% credibility level
    threshold=0.0      # Test if effect > 0
)
```

### 3. Fit the Model

```python
# Fit the model to your data
model.fit(
    data=data,
    time_col='date',
    control_col='control',
    test_col='test',
    pretest_start='2024-01-01',  # Start of pretest period
    test_start='2024-02-15',     # Start of test period
    test_end='2024-03-31'        # End of test period
)
```

### 4. Get Results

```python
# Get final summary
summary = model.summarize()
print(f"Treatment Effect: {summary.estimate:.2f}")
print(f"80% CI: [{summary.lower:.2f}, {summary.upper:.2f}]")
print(f"Significant: {summary.is_significant()}")

# Access detailed results
results_df = model.results_
predictions = model.predict()
```

## Complete Example

```python
import pandas as pd
import numpy as np
from tbr import TBRAnalysis

# Generate sample data
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=90)
control = np.random.normal(1000, 50, 90)
test = control * 1.02 + np.random.normal(0, 5, 90)  # 2% treatment effect

data = pd.DataFrame({
    'date': dates,
    'control': control,
    'test': test
})

# Run TBR analysis
model = TBRAnalysis(level=0.80, threshold=0.0)
model.fit(
    data=data,
    time_col='date',
    control_col='control',
    test_col='test',
    pretest_start='2024-01-01',
    test_start='2024-02-15',
    test_end='2024-03-31'
)

# Get results
summary = model.summarize()
print(f"Effect: {summary.estimate:.2f}")
print(f"CI: [{summary.lower:.2f}, {summary.upper:.2f}]")
print(f"P(effect > 0): {summary.prob:.3f}")
```

## One-Liner Analysis

```python
# Quick analysis without storing model
summary = TBRAnalysis().fit_summarize(
    data, 'date', 'control', 'test',
    pretest_start='2024-01-01',
    test_start='2024-02-15',
    test_end='2024-03-31'
)
print(f"Effect: {summary.estimate:.2f}")
```

## Next Steps

- **[API Reference](api_reference.md)** - Complete API documentation
- **[Examples](../../examples/)** - Domain-specific examples
- **[Common Patterns](patterns.md)** - Best practices and patterns
- **[Result Objects](results.md)** - Understanding result objects

## Key Concepts

### Time Periods

- **Pretest Period**: Historical data used to learn the relationship between control and test
- **Test Period**: Period where treatment is applied
- **Counterfactual**: What the test would have been without treatment

### Configuration Parameters

- **level**: Credibility level for confidence intervals (0 < level < 1)
- **threshold**: Minimum effect size for probability calculations
- **test_end_inclusive**: Whether to include the end date in analysis

### Result Components

- **estimate**: Cumulative treatment effect
- **lower/upper**: Credible interval bounds
- **prob**: Posterior probability that effect exceeds threshold
- **precision**: Inverse of variance (higher = more certain)

## Common Use Cases

### Marketing Campaign Analysis
Measure the incremental impact of a marketing campaign on sales or conversions.

### A/B Testing
Analyze treatment effects in controlled experiments with time series data.

### Medical Trials
Evaluate treatment effects in clinical studies with temporal components.

### Economic Policy Analysis
Assess the impact of policy interventions on economic indicators.

### Feature Rollouts
Measure the impact of new product features on user metrics.

## Tips

1. **Sufficient Pretest Data**: Use at least 2x the test period length for pretest
2. **Stable Relationships**: Ensure control-test relationship is stable in pretest
3. **Check Diagnostics**: Use model diagnostics to validate assumptions
4. **Domain-Agnostic**: Works with any time series where you have control and test groups
5. **Multiple Analyses**: Re-fit the same model with different periods for comparisons

## Getting Help

- Check the [API Reference](api_reference.md) for detailed method documentation
- See [Examples](../../examples/) for domain-specific use cases
- Review [Common Patterns](patterns.md) for best practices
- Read [Result Objects](results.md) to understand output structures
