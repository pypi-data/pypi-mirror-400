# TBR - Time-Based Regression Analysis Package

[![PyPI version](https://badge.fury.io/py/tbr.svg)](https://badge.fury.io/py/tbr)
[![Build Status](https://github.com/idohi/tbr/workflows/CI/badge.svg)](https://github.com/idohi/tbr/actions)
[![Coverage Status](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/idohi/tbr/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Development Status](https://img.shields.io/badge/status-beta-yellow.svg)](https://pypi.org/project/tbr/)

A comprehensive Python package for Time-Based Regression (TBR) analysis. TBR combines regression techniques with time series analysis to estimate treatment effects in before-after studies. Applications span marketing effectiveness, medical research, A/B testing, policy evaluation, and more.

## Status: Beta

**TBR** is feature-complete and ready for production use with:
- Complete TBR functionality (functional + OOP APIs)
- 1,200+ tests with 100% code coverage
- Intuitive, type-safe API interfaces
- Export utilities (JSON, CSV)
- Performance validated (linear O(n) scalability)
- Cross-platform support (Python 3.8-3.12)

**Why Beta?** While comprehensively tested, we're gathering real-world feedback before declaring v1.0 stable. We encourage production use and welcome your feedback!

## Features

- **Domain-Agnostic**: Works with any treatment/control group time series data
- **Comprehensive Analysis**: Lift calculation, counterfactual predictions, statistical inference
- **Statistical Rigor**: Credible intervals, significance tests, posterior probability assessments
- **Flexible**: Temporal and cumulative analysis, subinterval analysis, incremental analysis
- **Well-Tested**: Type hints, 100% code coverage, comprehensive test suite
- **Easy to Use**: Simple, intuitive API for both quick analysis and advanced workflows

## Installation

```bash
pip install tbr
```

Optional dependencies:
```bash
pip install tbr[dev]       # Development tools
pip install tbr[docs]      # Documentation tools
pip install tbr[examples]  # Example dependencies
```

## Quick Start

```python
import pandas as pd
import numpy as np
from tbr import TBRAnalysis

# Create example time series data
np.random.seed(42)
dates = pd.date_range('2023-01-01', periods=100, freq='D')
data = pd.DataFrame({
    'date': dates,
    'control': np.random.normal(100, 10, 100),
    'test': np.random.normal(105, 10, 100)
})

# Initialize and fit model
model = TBRAnalysis(level=0.90)
model.fit(
    data=data,
    time_col='date',
    control_col='control',
    test_col='test',
    pretest_start='2023-01-01',
    test_start='2023-02-15',
    test_end='2023-04-10'
)

# Get results
summary = model.summarize()
print(f"Treatment Effect: {summary.estimate:.2f}")
print(f"95% CI: [{summary.ci_lower:.2f}, {summary.ci_upper:.2f}]")
print(f"Significant: {summary.is_significant()}")

# Additional capabilities
predictions = model.predict()
subinterval = model.analyze_subinterval(start_day=1, end_day=10)
incremental = model.summarize_incremental()
summary.to_json('results.json')
```

## Key Capabilities

- **Counterfactual Predictions**: Estimates what would have happened without treatment
- **Lift Calculations**: Treatment effect with statistical uncertainty quantification
- **Credible Intervals**: Bayesian confidence bounds using t-distribution
- **Significance Testing**: Posterior probability of positive/negative effects
- **Flexible Analysis**: Subinterval analysis, incremental tracking, custom confidence levels

## Mathematical Foundation

TBR implements statistical methods for estimating causal effects in before-after study designs:

- **Regression Modeling**: Establishes relationship between control and test groups
- **Counterfactual Prediction**: Estimates what would have occurred without intervention
- **Bayesian Inference**: Credible intervals with uncertainty quantification
- **Variance Decomposition**: Proper error propagation

## Documentation

- **Examples**: See `examples/` directory in the repository
- **Full Documentation**: Coming in v0.2.0

## Version Compatibility

- **Python**: 3.8+ (tested on 3.8, 3.9, 3.10, 3.11, 3.12)
- **pandas**: 2.0+
- **numpy**: 1.24+
- **scipy**: 1.10+
- **statsmodels**: 0.14+

## References

The mathematical framework and notation in this package are based on:

> Kerman, J., Wang, P., & Vaver, J. (2017). *Estimating Ad Effectiveness using Geo Experiments in a Time-Based Regression Framework*. Technical Report, Google, Inc. [PDF](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/45950.pdf)

This package provides a domain-agnostic Python implementation of the time-based regression methodology for any before-after intervention study.

## License

This project is licensed under the BSD-3-Clause License - see the [LICENSE](https://github.com/idohi/tbr/blob/main/LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/idohi/tbr/issues)
