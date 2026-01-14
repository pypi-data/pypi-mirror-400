"""
Method Chaining and Fluent API Example.

========================================

This example demonstrates the fluent API and method chaining capabilities
of the TBR package, allowing for concise and readable analysis workflows.

Use Case: Quick analysis, configuration comparison, and one-liner workflows.
"""

import numpy as np
import pandas as pd

from tbr import TBRAnalysis

np.random.seed(42)

# Generate sample data
dates = pd.date_range("2024-01-01", periods=90)
control = np.random.normal(1000, 50, 90)
test = control * 1.03 + np.random.normal(0, 10, 90)  # 3% lift

data = pd.DataFrame({"date": dates, "control": control, "test": test})

print("=" * 80)
print("METHOD CHAINING EXAMPLES")
print("=" * 80)
print()

# =============================================================================
# 1. One-Liner Analysis
# =============================================================================

print("1. ONE-LINER ANALYSIS")
print("-" * 40)

# Complete analysis in one line
summary = TBRAnalysis().fit_summarize(
    data,
    "date",
    "control",
    "test",
    pretest_start="2024-01-01",
    test_start="2024-02-15",
    test_end="2024-03-31",
)

print(f"Effect: {summary.estimate:.2f}")
print(f"CI: [{summary.lower:.2f}, {summary.upper:.2f}]")
print(f"Significant: {summary.is_significant()}")
print()

# =============================================================================
# 2. Configuration and Fit Chaining
# =============================================================================

print("2. CONFIGURATION AND FIT CHAINING")
print("-" * 40)

# Chain configuration, fitting, and access
final_effect = (
    TBRAnalysis()
    .set_params(level=0.90, threshold=5.0)
    .fit(
        data,
        "date",
        "control",
        "test",
        pretest_start="2024-01-01",
        test_start="2024-02-15",
        test_end="2024-03-31",
    )
    .final_effect
)

print(f"Final effect (90% CI, threshold=5.0): {final_effect:.2f}")
print()

# =============================================================================
# 3. Copy, Configure, and Analyze
# =============================================================================

print("3. COPY, CONFIGURE, AND ANALYZE")
print("-" * 40)

# Base model
base_model = TBRAnalysis(level=0.80, threshold=0.0)

# Create variant with different configuration
variant_summary = (
    base_model.copy()
    .set_params(level=0.95)
    .fit_summarize(
        data,
        "date",
        "control",
        "test",
        pretest_start="2024-01-01",
        test_start="2024-02-15",
        test_end="2024-03-31",
    )
)

print(f"Variant (95% CI): {variant_summary.estimate:.2f}")
print(f"CI: [{variant_summary.lower:.2f}, {variant_summary.upper:.2f}]")
print()

# =============================================================================
# 4. Fit and Predict Chain
# =============================================================================

print("4. FIT AND PREDICT CHAIN")
print("-" * 40)

# Fit and predict in one statement
predictions = (
    TBRAnalysis()
    .fit(
        data,
        "date",
        "control",
        "test",
        pretest_start="2024-01-01",
        test_start="2024-02-15",
        test_end="2024-03-31",
    )
    .predict()
)

print(f"Mean prediction: {predictions.mean_pred:.2f}")
print(f"Mean uncertainty: {predictions.mean_uncertainty:.2f}")
print()

# =============================================================================
# 5. Comprehensive Chaining Workflow
# =============================================================================

print("5. COMPREHENSIVE CHAINING WORKFLOW")
print("-" * 40)

# Complete workflow with chaining
model = (
    TBRAnalysis()
    .set_params(level=0.90, threshold=0.0)
    .fit(
        data,
        "date",
        "control",
        "test",
        pretest_start="2024-01-01",
        test_start="2024-02-15",
        test_end="2024-03-31",
    )
)

# Now access different results
summary = model.summarize()
predictions = model.predict()
week1 = model.analyze_subinterval(1, 7)

print(f"Overall effect: {summary.estimate:.2f}")
print(f"Week 1 effect: {week1.estimate:.2f}")
print(f"Mean prediction: {predictions.mean_pred:.2f}")
print()

# =============================================================================
# 6. Comparing Multiple Configurations
# =============================================================================

print("6. COMPARING MULTIPLE CONFIGURATIONS")
print("-" * 40)

# Compare different confidence levels
levels = [0.80, 0.90, 0.95, 0.99]
results = []

for level in levels:
    effect = (
        TBRAnalysis()
        .set_params(level=level)
        .fit_summarize(
            data,
            "date",
            "control",
            "test",
            pretest_start="2024-01-01",
            test_start="2024-02-15",
            test_end="2024-03-31",
        )
    )
    results.append(
        {
            "level": level,
            "estimate": effect.estimate,
            "lower": effect.lower,
            "upper": effect.upper,
            "significant": effect.is_significant(),
        }
    )

comparison_df = pd.DataFrame(results)
print(comparison_df.to_string(index=False))
print()

# =============================================================================
# 7. Parameter Inspection
# =============================================================================

print("7. PARAMETER INSPECTION")
print("-" * 40)

model = TBRAnalysis(level=0.90, threshold=10.0)
print("Initial parameters:", model.get_params())

# Update and inspect
model.set_params(level=0.95)
print("After update:", model.get_params())
print()

# =============================================================================
# 8. Sklearn-Style Workflow
# =============================================================================

print("8. SKLEARN-STYLE WORKFLOW")
print("-" * 40)

# Use sklearn-compatible get_params/set_params
estimator = TBRAnalysis()
params = estimator.get_params()
print(f"Default params: {params}")

# Clone with different params
estimator_clone = estimator.copy()
estimator_clone.set_params(level=0.95, threshold=5.0)

print(f"Clone params: {estimator_clone.get_params()}")
print(f"Original params (unchanged): {estimator.get_params()}")
print()

# =============================================================================
# 9. Property Access Chaining
# =============================================================================

print("9. PROPERTY ACCESS CHAINING")
print("-" * 40)

# Chain fit and access convenience properties
model = TBRAnalysis().fit(
    data,
    "date",
    "control",
    "test",
    pretest_start="2024-01-01",
    test_start="2024-02-15",
    test_end="2024-03-31",
)

# Access different properties
print(f"Final effect: {model.final_effect:.2f}")
print(f"Fitted: {model.fitted_}")
print(f"Test days: {len(model.summaries_)}")
print()

# =============================================================================
# 10. One-Liner with Export
# =============================================================================

print("10. ONE-LINER WITH EXPORT")
print("-" * 40)

# Analyze and export in minimal code
summary = TBRAnalysis().fit_summarize(
    data,
    "date",
    "control",
    "test",
    pretest_start="2024-01-01",
    test_start="2024-02-15",
    test_end="2024-03-31",
)
summary.to_json("quick_analysis.json")

print(f"Quick analysis: {summary.estimate:.2f} (saved to JSON)")
print()

print("=" * 80)
print("METHOD CHAINING COMPLETE")
print("=" * 80)
print()
print("Key Takeaways:")
print("• Use fit_summarize() for one-liner analysis")
print("• Chain set_params() → fit() → summarize() for custom configs")
print("• Use copy() to create independent model variants")
print("• Access final_effect and final_summary for quick results")
print("• Compatible with sklearn-style get_params/set_params")
