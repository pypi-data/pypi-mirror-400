"""
Basic TBR Analysis Example.

===========================

This example demonstrates a basic time-based regression analysis workflow.

Use Case: Measuring the impact of any treatment/intervention on a metric over time.
Domain: Universal (works for marketing, medical, economic, or any other domain)
"""

import numpy as np
import pandas as pd

from tbr import TBRAnalysis

# Set random seed for reproducibility
np.random.seed(42)

# =============================================================================
# 1. Generate Sample Data
# =============================================================================

# Create 90 days of daily data
dates = pd.date_range("2024-01-01", periods=90, freq="D")

# Control group: baseline behavior
control = np.random.normal(1000, 50, 90)

# Test group: same as control in pretest, then 5% lift in test period
test = control.copy()
test[45:] = test[45:] * 1.05 + np.random.normal(0, 10, 45)  # 5% lift + noise

# Create DataFrame
data = pd.DataFrame({"date": dates, "control_metric": control, "test_metric": test})

print("=" * 80)
print("DATA SUMMARY")
print("=" * 80)
print(f"Total days: {len(data)}")
print(f"Date range: {data['date'].min()} to {data['date'].max()}")
print("\nFirst 5 rows:")
print(data.head())
print()

# =============================================================================
# 2. Initialize TBR Model
# =============================================================================

# Create model with 80% credibility level
model = TBRAnalysis(
    level=0.80, threshold=0.0  # 80% credible interval  # Test if effect > 0
)

print("=" * 80)
print("MODEL CONFIGURATION")
print("=" * 80)
print(f"Credibility level: {model.level * 100:.0f}%")
print(f"Threshold: {model.threshold}")
print(f"Test end inclusive: {model.test_end_inclusive}")
print()

# =============================================================================
# 3. Fit the Model
# =============================================================================

# Define time periods
pretest_start = "2024-01-01"  # Day 1
test_start = "2024-02-15"  # Day 45 (intervention starts)
test_end = "2024-03-31"  # Day 90 (end of observation)

print("=" * 80)
print("FITTING MODEL")
print("=" * 80)
print(f"Pretest period: {pretest_start} to {test_start}")
print(f"Test period: {test_start} to {test_end}")
print()

# Fit model
model.fit(
    data=data,
    time_col="date",
    control_col="control_metric",
    test_col="test_metric",
    pretest_start=pretest_start,
    test_start=test_start,
    test_end=test_end,
)

print(f"Model fitted: {model.fitted_}")
print(f"Pretest days: {model._fit_info['n_pretest']}")
print(f"Test days: {model._fit_info['n_test']}")
print()

# =============================================================================
# 4. Get Summary Results
# =============================================================================

summary = model.summarize()

print("=" * 80)
print("ANALYSIS RESULTS")
print("=" * 80)
print(f"Treatment Effect: {summary.estimate:.2f}")
print(f"Standard Error: {summary.se:.2f}")
print(f"80% Credible Interval: [{summary.lower:.2f}, {summary.upper:.2f}]")
print(f"Probability (effect > 0): {summary.prob:.3f}")
print(f"Statistically Significant: {summary.is_significant()}")
print()

# Regression parameters
print("Regression Model:")
print(f"  Intercept (α): {summary.alpha:.2f}")
print(f"  Slope (β): {summary.beta:.4f}")
print(f"  Residual Std Error (σ): {summary.sigma:.2f}")
print()

# =============================================================================
# 5. Analyze Subintervals
# =============================================================================

print("=" * 80)
print("SUBINTERVAL ANALYSIS")
print("=" * 80)

# Analyze first week
week1 = model.analyze_subinterval(start_day=1, end_day=7)
print("Week 1 (Days 1-7):")
print(f"  Effect: {week1.estimate:.2f}")
print(f"  CI: [{week1.lower:.2f}, {week1.upper:.2f}]")
print(f"  Positive effect: {week1.is_positive()}")
print()

# Analyze second week
week2 = model.analyze_subinterval(start_day=8, end_day=14)
print("Week 2 (Days 8-14):")
print(f"  Effect: {week2.estimate:.2f}")
print(f"  CI: [{week2.lower:.2f}, {week2.upper:.2f}]")
print(f"  Positive effect: {week2.is_positive()}")
print()

# Analyze last two weeks
final_period = model.analyze_subinterval(start_day=32, end_day=45)
print("Final Period (Days 32-45):")
print(f"  Effect: {final_period.estimate:.2f}")
print(f"  CI: [{final_period.lower:.2f}, {final_period.upper:.2f}]")
print(f"  Positive effect: {final_period.is_positive()}")
print()

# =============================================================================
# 6. Generate Predictions
# =============================================================================

print("=" * 80)
print("COUNTERFACTUAL PREDICTIONS")
print("=" * 80)

# Get predictions for test period
predictions = model.predict()

print(f"Number of predictions: {predictions.n_predictions}")
print(f"Mean prediction: {predictions.mean_pred:.2f}")
print(f"Mean uncertainty: {predictions.mean_uncertainty:.2f}")
print()
print("First 5 predictions:")
print(predictions.predictions.head())
print()

# =============================================================================
# 7. Access Detailed Results
# =============================================================================

print("=" * 80)
print("DETAILED RESULTS")
print("=" * 80)

# Get full TBR DataFrame
results_df = model.results_

# Show test period results
test_period = results_df[results_df["period"] == 1]
print(f"Test period data shape: {test_period.shape}")
print()
print("Test period summary (first 5 days):")
print(
    test_period[
        ["date", "control_metric", "test_metric", "pred", "dif", "cumdif"]
    ].head()
)
print()

# =============================================================================
# 8. Export Results
# =============================================================================

print("=" * 80)
print("EXPORT OPTIONS")
print("=" * 80)

# Export summary to JSON
summary.to_json("tbr_summary.json")
print("✓ Summary exported to 'tbr_summary.json'")

# Export summary to CSV
summary.to_csv("tbr_summary.csv")
print("✓ Summary exported to 'tbr_summary.csv'")

# Export predictions
predictions.to_json("tbr_predictions.json")
print("✓ Predictions exported to 'tbr_predictions.json'")

print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
