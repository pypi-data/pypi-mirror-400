# Common Patterns and Best Practices

A comprehensive guide to common usage patterns and best practices for TBR analysis.

## Table of Contents

- [Data Preparation](#data-preparation)
- [Model Configuration](#model-configuration)
- [Analysis Patterns](#analysis-patterns)
- [Result Interpretation](#result-interpretation)
- [Performance Tips](#performance-tips)
- [Common Pitfalls](#common-pitfalls)
- [Domain-Specific Guidance](#domain-specific-guidance)

---

## Data Preparation

### Pattern 1: Preparing Time Series Data

**Best Practice**: Ensure your data has consistent time intervals and proper data types.

```python
import pandas as pd

# Load your data
data = pd.read_csv('data.csv')

# Convert date column to datetime
data['date'] = pd.to_datetime(data['date'])

# Sort by date (critical!)
data = data.sort_values('date').reset_index(drop=True)

# Check for missing values
if data[['control', 'test']].isnull().any().any():
    print("Warning: Missing values detected")
    data = data.dropna(subset=['control', 'test'])

# Verify consistent frequency
date_diff = data['date'].diff()
if not date_diff[1:].nunique() == 1:
    print("Warning: Inconsistent time intervals")
```

### Pattern 2: Handling Different Time Column Types

**Best Practice**: TBR supports datetime, integer, and float time columns.

```python
from tbr import TBRAnalysis

# Datetime (most common)
model.fit(data, time_col='date', ...,
          pretest_start='2024-01-01',
          test_start='2024-02-15',
          test_end='2024-03-31')

# Integer (e.g., day numbers)
model.fit(data, time_col='day_number', ...,
          pretest_start=1,
          test_start=45,
          test_end=90)

# Float (e.g., fractional time)
model.fit(data, time_col='time_value', ...,
          pretest_start=0.0,
          test_start=44.5,
          test_end=89.9)
```

### Pattern 3: Aggregating Data to Appropriate Granularity

**Best Practice**: Choose time granularity based on your signal-to-noise ratio.

```python
# Daily aggregation (most common)
daily = raw_data.groupby('date').agg({
    'control_metric': 'sum',
    'test_metric': 'sum'
}).reset_index()

# Weekly aggregation (for noisy data)
weekly = raw_data.resample('W', on='date').agg({
    'control_metric': 'sum',
    'test_metric': 'sum'
}).reset_index()
```

---

## Model Configuration

### Pattern 4: Choosing Credibility Level

**Best Practice**: Use confidence levels appropriate for your decision context.

```python
from tbr import TBRAnalysis

# Standard analysis (80% - balanced)
model = TBRAnalysis(level=0.80)

# High confidence needed (95% - conservative)
model = TBRAnalysis(level=0.95)

# Quick screening (90% - moderate)
model = TBRAnalysis(level=0.90)

# Very high confidence (99% - very conservative)
model = TBRAnalysis(level=0.99)
```

**Guidelines**:
- **80%**: Default, balanced for most use cases
- **90-95%**: Important business decisions
- **99%**: Critical decisions with high cost of error

### Pattern 5: Setting Threshold for Practical Significance

**Best Practice**: Set threshold based on minimum detectable/meaningful effect.

```python
# Test for any positive effect
model = TBRAnalysis(threshold=0.0)

# Test for effect exceeding minimum ROI
min_effect = 1000  # e.g., $1000 minimum lift
model = TBRAnalysis(threshold=min_effect)

# Test for effect exceeding cost
intervention_cost = 5000
model = TBRAnalysis(threshold=intervention_cost)
```

### Pattern 6: Pretest Period Length

**Best Practice**: Use at least 2x test period length for pretest.

```python
test_period_days = 30

# Minimum pretest (2x test period)
pretest_period_days = test_period_days * 2  # 60 days

# Recommended pretest (3-4x test period)
pretest_period_days = test_period_days * 3  # 90 days

# Calculate dates
test_end = pd.Timestamp('2024-03-31')
test_start = test_end - pd.Timedelta(days=test_period_days)
pretest_start = test_start - pd.Timedelta(days=pretest_period_days)
```

**Rationale**:
- More pretest data → better parameter estimates
- More pretest data → narrower confidence intervals
- Diminishing returns beyond 4-5x test period

---

## Analysis Patterns

### Pattern 7: Standard Analysis Workflow

**Best Practice**: Follow a systematic analysis workflow.

```python
from tbr import TBRAnalysis

# 1. Configure model
model = TBRAnalysis(level=0.80, threshold=0.0)

# 2. Fit model
model.fit(data, 'date', 'control', 'test',
          pretest_start='2024-01-01',
          test_start='2024-02-15',
          test_end='2024-03-31')

# 3. Get overall results
summary = model.summarize()
print(f"Effect: {summary.estimate:.2f}")
print(f"Significant: {summary.is_significant()}")

# 4. Check predictions
predictions = model.predict()
print(f"Mean prediction: {predictions.mean_pred:.2f}")

# 5. Analyze temporal patterns
incremental = model.summarize_incremental()

# 6. Export results
summary.to_json('results.json')
```

### Pattern 8: Comparing Multiple Configurations

**Best Practice**: Systematically compare different analysis configurations.

```python
configs = [
    {'level': 0.80, 'name': '80% CI'},
    {'level': 0.90, 'name': '90% CI'},
    {'level': 0.95, 'name': '95% CI'},
]

results = []
for config in configs:
    model = TBRAnalysis(level=config['level'])
    summary = model.fit_summarize(data, 'date', 'control', 'test', ...)
    results.append({
        'config': config['name'],
        'estimate': summary.estimate,
        'lower': summary.lower,
        'upper': summary.upper,
        'significant': summary.is_significant()
    })

comparison = pd.DataFrame(results)
print(comparison)
```

### Pattern 9: Subinterval Analysis

**Best Practice**: Analyze multiple subintervals to understand temporal dynamics.

```python
# Analyze by week
n_weeks = test_period_days // 7
weekly_results = []

for week in range(1, n_weeks + 1):
    start_day = (week - 1) * 7 + 1
    end_day = min(week * 7, test_period_days)

    result = model.analyze_subinterval(start_day, end_day)
    weekly_results.append({
        'week': week,
        'effect': result.estimate,
        'lower': result.lower,
        'upper': result.upper,
        'significant': result.is_positive()
    })

weekly_df = pd.DataFrame(weekly_results)
```

### Pattern 10: Early Stopping Decision

**Best Practice**: Monitor incremental results to determine optimal stopping time.

```python
incremental = model.summarize_incremental()

# Find first day effect becomes significant
for idx, row in incremental.iterrows():
    if row['lower'] > 0:  # Significant
        print(f"Effect significant by Day {row['test_day']}")
        print(f"Could stop testing early")
        break
```

---

## Result Interpretation

### Pattern 11: Statistical Significance Check

**Best Practice**: Use multiple criteria for significance.

```python
summary = model.summarize()

# Criterion 1: Confidence interval excludes zero
ci_significant = summary.is_significant()  # lower > 0

# Criterion 2: High posterior probability
prob_significant = summary.prob > 0.95  # P(effect > 0) > 95%

# Criterion 3: Effect exceeds threshold
threshold = 1000
practical_significant = summary.lower > threshold

# Combined assessment
if ci_significant and prob_significant:
    print("Strong evidence of positive effect")
elif ci_significant:
    print("Moderate evidence of positive effect")
else:
    print("Insufficient evidence of effect")
```

### Pattern 12: Effect Size Interpretation

**Best Practice**: Report both absolute and relative effects.

```python
summary = model.summarize()

# Absolute effect
print(f"Absolute effect: {summary.estimate:.2f}")

# Relative effect (percentage)
# Calculate average test value
avg_test = model.results_[model.results_['period'] == 1]['test'].mean()
avg_control = model.results_[model.results_['period'] == 1]['control'].mean()

if avg_control > 0:
    relative_effect = (summary.estimate / (avg_control * test_period_days)) * 100
    print(f"Relative effect: {relative_effect:.2f}%")
```

### Pattern 13: Uncertainty Communication

**Best Practice**: Always report uncertainty along with point estimates.

```python
summary = model.summarize()

# Point estimate with confidence interval
print(f"Effect: {summary.estimate:.2f} "
      f"[{summary.lower:.2f}, {summary.upper:.2f}] "
      f"({summary.level*100:.0f}% CI)")

# Probability interpretation
if summary.prob > 0.99:
    confidence = "very high"
elif summary.prob > 0.95:
    confidence = "high"
elif summary.prob > 0.80:
    confidence = "moderate"
else:
    confidence = "low"

print(f"Confidence in positive effect: {confidence}")
```

---

## Performance Tips

### Pattern 14: Efficient Batch Analysis

**Best Practice**: Reuse model instances for multiple analyses.

```python
# Create model once
model = TBRAnalysis(level=0.80)

# Analyze multiple periods efficiently
periods = [
    ('Q1', '2024-01-01', '2024-03-31'),
    ('Q2', '2024-04-01', '2024-06-30'),
    ('Q3', '2024-07-01', '2024-09-30'),
]

results = []
for name, start, end in periods:
    summary = model.fit_summarize(
        data[data['date'] <= end],
        'date', 'control', 'test',
        pretest_start=start,
        test_start=...,
        test_end=end
    )
    results.append({'period': name, 'effect': summary.estimate})
```

### Pattern 15: Memory-Efficient Large Dataset Analysis

**Best Practice**: Work with filtered data when possible.

```python
# Filter to relevant time window before analysis
analysis_start = '2024-01-01'
analysis_end = '2024-06-30'

filtered_data = data[
    (data['date'] >= analysis_start) &
    (data['date'] <= analysis_end)
].copy()

# Analyze filtered data
model.fit(filtered_data, ...)
```

---

## Common Pitfalls

### Pitfall 1: Insufficient Pretest Data

**Problem**: Too little pretest data leads to unstable estimates.

**Solution**:
```python
# Check pretest length
pretest_days = (test_start - pretest_start).days
test_days = (test_end - test_start).days

if pretest_days < test_days * 2:
    print(f"Warning: Pretest ({pretest_days} days) < 2x test period ({test_days} days)")
    print("Consider using more pretest data for stable estimates")
```

### Pitfall 2: Unstable Control-Test Relationship

**Problem**: Relationship between control and test groups changes in pretest.

**Solution**:
```python
# Check relationship stability in pretest
pretest_data = data[
    (data['date'] >= pretest_start) &
    (data['date'] < test_start)
]

# Split into early/late pretest
mid_pretest = pretest_start + (test_start - pretest_start) / 2
early_pretest = pretest_data[pretest_data['date'] < mid_pretest]
late_pretest = pretest_data[pretest_data['date'] >= mid_pretest]

# Compare correlations
early_corr = early_pretest[['control', 'test']].corr().iloc[0, 1]
late_corr = late_pretest[['control', 'test']].corr().iloc[0, 1]

if abs(early_corr - late_corr) > 0.1:
    print(f"Warning: Pretest relationship unstable")
    print(f"Early correlation: {early_corr:.3f}")
    print(f"Late correlation: {late_corr:.3f}")
```

### Pitfall 3: Ignoring Seasonality

**Problem**: Day-of-week or seasonal patterns not accounted for.

**Solution**:
```python
# Ensure pretest and test periods cover complete cycles
# For weekly patterns, use multiples of 7 days
test_period_days = 28  # 4 weeks
pretest_period_days = 56  # 8 weeks

# For monthly patterns, align to calendar months
pretest_start = '2024-01-01'  # Month start
test_start = '2024-03-01'      # Month start
test_end = '2024-03-31'        # Month end
```

### Pitfall 4: Multiple Testing Without Adjustment

**Problem**: Testing multiple hypotheses inflates false positive rate.

**Solution**:
```python
# When analyzing multiple subintervals, be cautious
n_tests = 10  # Number of subintervals tested

# Consider Bonferroni adjustment
adjusted_level = 1 - (1 - 0.95) / n_tests  # Adjust from 95%
model = TBRAnalysis(level=adjusted_level)

# Or report that you're conducting exploratory analysis
print(f"Note: Analyzing {n_tests} subintervals (exploratory)")
```

---

## Domain-Specific Guidance

### Marketing Campaigns

```python
# Typical setup for marketing lift measurement
model = TBRAnalysis(
    level=0.80,          # 80% CI standard for marketing
    threshold=0.0        # Test any positive lift
)

# Typical periods
pretest_days = 60  # 2 months historical
test_days = 30     # 1 month campaign

# Calculate ROI
summary = model.summarize()
campaign_cost = 10000
roi = (summary.estimate - campaign_cost) / campaign_cost
print(f"ROI: {roi*100:.1f}%")
```

### A/B Testing

```python
# A/B test with control and treatment groups
model = TBRAnalysis(
    level=0.95,          # High confidence for product decisions
    threshold=0.0
)

# Shorter test periods common in A/B tests
pretest_days = 14
test_days = 7

# Check for early stopping
incremental = model.summarize_incremental()
if incremental.iloc[2]['lower'] > 0:  # Significant by day 3
    print("Early stopping recommended")
```

### Medical Trials

```python
# Clinical trial analysis
model = TBRAnalysis(
    level=0.95,          # High confidence for medical decisions
    threshold=5.0        # Minimum clinically meaningful effect
)

# Longer observation periods
pretest_days = 180  # 6 months baseline
test_days = 90      # 3 months treatment

# Report with medical standards
summary = model.summarize()
print(f"Treatment effect: {summary.estimate:.2f}")
print(f"95% CI: [{summary.lower:.2f}, {summary.upper:.2f}]")
print(f"P(effect > {model.threshold}): {summary.prob:.3f}")
```

### Economic Analysis

```python
# Policy intervention analysis
model = TBRAnalysis(
    level=0.90,          # Standard for economic research
    threshold=0.0
)

# Quarterly or annual data common
# Adjust time units accordingly
pretest_quarters = 8   # 2 years
test_quarters = 4      # 1 year

# Report economic significance
summary = model.summarize()
if summary.is_significant():
    print(f"Statistically significant policy effect: {summary.estimate:.2f}")
```

---

## See Also

- **[API Reference](api_reference.md)** - Complete API documentation
- **[Quick Start](quickstart.md)** - Getting started guide
- **[Examples](../../examples/)** - Practical examples
- **[Result Objects](results.md)** - Understanding results
