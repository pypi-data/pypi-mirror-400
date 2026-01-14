"""
Incremental Analysis Example.

==============================

This example demonstrates how to analyze the progression of treatment effects
over time using incremental summaries and subinterval analysis.

Use Case: Understanding how effects evolve, finding optimal intervention windows,
         and tracking cumulative impact over time.
"""

import numpy as np
import pandas as pd

from tbr import TBRAnalysis

np.random.seed(42)

# Generate sample data with ramping effect
dates = pd.date_range("2024-01-01", periods=120)
control = np.random.normal(1000, 50, 120)

# Test group: gradual ramping effect that grows over time
test = control.copy()
# Days 1-60: pretest (no effect)
# Days 61-120: test period with ramping effect (0% → 10%)
for i in range(60, 120):
    days_into_test = i - 60
    ramp_factor = 1.0 + (0.10 * days_into_test / 60)  # Linearly ramp to 10%
    test[i] = test[i] * ramp_factor + np.random.normal(0, 10)

data = pd.DataFrame({"date": dates, "control": control, "test": test})

print("=" * 80)
print("INCREMENTAL ANALYSIS EXAMPLE")
print("=" * 80)
print("Scenario: Treatment effect ramps from 0% to 10% over 60-day test period")
print()

# =============================================================================
# 1. Fit the Model
# =============================================================================

model = TBRAnalysis(level=0.80)
model.fit(
    data=data,
    time_col="date",
    control_col="control",
    test_col="test",
    pretest_start="2024-01-01",
    test_start="2024-03-01",  # Day 61
    test_end="2024-04-29",  # Day 120
)

print("Pretest period: 60 days")
print("Test period: 60 days")
print()

# =============================================================================
# 2. Get Incremental Summaries
# =============================================================================

print("=" * 80)
print("INCREMENTAL SUMMARIES")
print("=" * 80)

incremental = model.summarize_incremental()

# Show progression at key points
print("Cumulative effect progression:")
print()

checkpoints = [1, 7, 14, 21, 30, 45, 60]
for day in checkpoints:
    if day <= len(incremental):
        row = incremental.iloc[day - 1]
        print(
            f"Day {day:2d}: Effect = {row['estimate']:8.2f}, "
            f"SE = {row['se']:6.2f}, "
            f"CI = [{row['lower']:8.2f}, {row['upper']:8.2f}], "
            f"P(>0) = {row['prob']:.3f}"
        )

print()

# =============================================================================
# 3. Weekly Subinterval Analysis
# =============================================================================

print("=" * 80)
print("WEEKLY SUBINTERVAL ANALYSIS")
print("=" * 80)

weeks = []
for week_num in range(1, 9):
    start_day = (week_num - 1) * 7 + 1
    end_day = min(week_num * 7, 60)

    if start_day <= 60:
        result = model.analyze_subinterval(start_day, end_day)
        weeks.append(
            {
                "week": week_num,
                "days": f"{start_day}-{end_day}",
                "effect": result.estimate,
                "lower": result.lower,
                "upper": result.upper,
                "significant": result.is_positive(),
            }
        )

weeks_df = pd.DataFrame(weeks)
print("\nWeekly effects:")
print(weeks_df.to_string(index=False))
print()

# =============================================================================
# 4. Period Comparison
# =============================================================================

print("=" * 80)
print("PERIOD COMPARISON")
print("=" * 80)

# Compare early, middle, and late periods
periods = [
    ("Early (Days 1-20)", 1, 20),
    ("Middle (Days 21-40)", 21, 40),
    ("Late (Days 41-60)", 41, 60),
]

print("\nComparing different phases:")
for name, start, end in periods:
    result = model.analyze_subinterval(start, end)
    print(f"\n{name}:")
    print(f"  Effect: {result.estimate:.2f}")
    print(f"  CI: [{result.lower:.2f}, {result.upper:.2f}]")
    print(f"  Positive: {result.is_positive()}")

print()

# =============================================================================
# 5. Finding Optimal Window
# =============================================================================

print("=" * 80)
print("FINDING OPTIMAL INTERVENTION WINDOW")
print("=" * 80)

# Analyze all possible 14-day windows
window_size = 14
windows = []

for start in range(1, 60 - window_size + 2):
    end = start + window_size - 1
    result = model.analyze_subinterval(start, end)
    windows.append(
        {
            "start_day": start,
            "end_day": end,
            "effect": result.estimate,
            "significant": result.is_positive(),
        }
    )

windows_df = pd.DataFrame(windows)

# Find window with largest effect
best_window = windows_df.loc[windows_df["effect"].idxmax()]
print("\nBest 14-day window:")
print(f"  Days {best_window['start_day']:.0f}-{best_window['end_day']:.0f}")
print(f"  Effect: {best_window['effect']:.2f}")
print(f"  Significant: {bool(best_window['significant'])}")
print()

# =============================================================================
# 6. Cumulative Growth Analysis
# =============================================================================

print("=" * 80)
print("CUMULATIVE GROWTH ANALYSIS")
print("=" * 80)

# Show how cumulative effect grows
print("\nCumulative effect growth every 10 days:")
for day in range(10, 61, 10):
    row = incremental.iloc[day - 1]
    # Calculate average daily effect
    avg_daily = row["estimate"] / day
    print(
        f"Day {day:2d}: Total = {row['estimate']:8.2f}, " f"Avg/day = {avg_daily:6.2f}"
    )

print()

# =============================================================================
# 7. Confidence Evolution
# =============================================================================

print("=" * 80)
print("CONFIDENCE EVOLUTION")
print("=" * 80)

# Show how confidence (precision) improves over time
print("\nConfidence interval width over time:")
checkpoints = [1, 7, 14, 30, 45, 60]
for day in checkpoints:
    if day <= len(incremental):
        row = incremental.iloc[day - 1]
        ci_width = row["upper"] - row["lower"]
        print(
            f"Day {day:2d}: Width = {ci_width:8.2f}, "
            f"Precision = {row['precision']:8.2f}"
        )

print()

# =============================================================================
# 8. Early Stopping Decision
# =============================================================================

print("=" * 80)
print("EARLY STOPPING DECISION")
print("=" * 80)

# Determine when effect becomes statistically significant
print("\nDetecting when effect becomes significant:")

significant_day = None
for day in range(1, len(incremental) + 1):
    row = incremental.iloc[day - 1]
    if row["lower"] > 0:  # Significant
        significant_day = day
        break

if significant_day:
    result = model.analyze_subinterval(1, significant_day)
    print(f"\nEffect becomes significant on Day {significant_day}")
    print(f"  Cumulative effect: {result.estimate:.2f}")
    print(f"  CI: [{result.lower:.2f}, {result.upper:.2f}]")
    print(f"  Could stop testing early and save {60 - significant_day} days")
else:
    print("\nEffect not yet significant")

print()

# =============================================================================
# 9. Incremental Summary Export
# =============================================================================

print("=" * 80)
print("EXPORT INCREMENTAL RESULTS")
print("=" * 80)

# Export incremental summaries
incremental.to_csv("incremental_summaries.csv", index=False)
print("✓ Incremental summaries exported to 'incremental_summaries.csv'")

# Export weekly analysis
weeks_df.to_csv("weekly_analysis.csv", index=False)
print("✓ Weekly analysis exported to 'weekly_analysis.csv'")

print()
print("=" * 80)
print("INCREMENTAL ANALYSIS COMPLETE")
print("=" * 80)
print()
print("Key Insights:")
print("• Effect ramped from early to late period as expected")
print(
    f"• Best 14-day window: Days {best_window['start_day']:.0f}-{best_window['end_day']:.0f}"
)
if significant_day:
    print(f"• Significance detected on Day {significant_day} (could stop early)")
print("• Later weeks show stronger effects due to ramping")
print("• Confidence improves over time (narrower CI, higher precision)")
