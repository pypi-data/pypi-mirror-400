TBR Examples
============

This directory contains practical examples demonstrating various aspects of the TBR package.

Available Examples
------------------

Basic Analysis
~~~~~~~~~~~~~~

**File:** ``plot_basic_analysis.py``

A complete walkthrough of a basic TBR analysis from data preparation to result export.

**Topics Covered:**

- Data preparation and exploration
- Model initialization and configuration
- Fitting the model
- Interpreting summary results
- Subinterval analysis
- Generating predictions
- Exporting results

**Run the example:**

.. code-block:: bash

    cd examples
    python plot_basic_analysis.py


Method Chaining
~~~~~~~~~~~~~~~

**File:** ``plot_method_chaining.py``

Demonstrates the fluent API and method chaining capabilities for concise workflows.

**Topics Covered:**

- One-liner analysis with ``fit_summarize()``
- Configuration and fit chaining
- Model copying and variants
- Fit and predict chains
- Sklearn-style parameter management
- Comparing multiple configurations
- Property access shortcuts

**Run the example:**

.. code-block:: bash

    python plot_method_chaining.py


Incremental Analysis
~~~~~~~~~~~~~~~~~~~~

**File:** ``plot_incremental_analysis.py``

Shows how to analyze treatment effects over time using incremental summaries and subintervals.

**Topics Covered:**

- Incremental summary progression
- Weekly subinterval analysis
- Period comparison (early vs. late)
- Finding optimal intervention windows
- Cumulative growth tracking
- Confidence evolution
- Early stopping decisions
- Exporting incremental results

**Run the example:**

.. code-block:: bash

    python plot_incremental_analysis.py


Example Scenarios
-----------------

All examples use synthetic data but represent real-world scenarios:

- **Marketing Campaign Analysis**: Measuring incremental lift from marketing interventions
- **A/B Testing**: Analyzing treatment effects in controlled experiments
- **Medical Trials**: Evaluating treatment effects in clinical studies
- **Economic Policy Analysis**: Assessing policy intervention impacts
- **Feature Rollouts**: Measuring new feature impacts on user metrics


Domain-Agnostic Design
----------------------

All examples are **domain-agnostic**, meaning:

- They work with any control/test group time series data
- No assumptions about data source or industry
- Applicable across marketing, medical, economic, and other domains
- Focus on statistical methodology, not domain-specific details


Running Examples
----------------

Prerequisites
~~~~~~~~~~~~~

.. code-block:: bash

    pip install tbr


Basic Execution
~~~~~~~~~~~~~~~

Each example is a standalone Python script:

.. code-block:: bash

    python plot_basic_analysis.py
    python plot_method_chaining.py
    python plot_incremental_analysis.py


Output
~~~~~~

Examples produce:

- Console output with analysis results
- JSON export files (e.g., ``tbr_summary.json``, ``tbr_predictions.json``)
- CSV export files (e.g., ``tbr_summary.csv``, ``incremental_summaries.csv``)


Customization
~~~~~~~~~~~~~

To adapt examples to your data:

1. **Replace data generation code** with your data loading:

.. code-block:: python

    # Instead of synthetic data generation
    # Use:
    data = pd.read_csv('your_data.csv')
    data['date'] = pd.to_datetime(data['date'])

2. **Update column names** to match your data:

.. code-block:: python

    model.fit(
        data=data,
        time_col='your_time_column',
        control_col='your_control_column',
        test_col='your_test_column',
        ...
    )

3. **Adjust time periods** to your analysis window:

.. code-block:: python

    pretest_start='your_pretest_start',
    test_start='your_test_start',
    test_end='your_test_end'


Learning Path
-------------

**Recommended order for beginners:**

1. **Start with** ``plot_basic_analysis.py``

   - Understand the complete workflow
   - Learn core concepts and terminology
   - See all major components in action

2. **Then explore** ``plot_method_chaining.py``

   - Learn fluent API patterns
   - Discover shortcuts and convenience methods
   - Understand model configuration

3. **Finally study** ``plot_incremental_analysis.py``

   - Master temporal analysis techniques
   - Learn subinterval analysis patterns
   - Understand effect progression


Additional Resources
--------------------

- **Quick Start Guide** (``docs/api/quickstart.md``) - Fast introduction to TBR
- **API Reference** (``docs/api/api_reference.md``) - Complete API documentation
- **Common Patterns** (``docs/api/patterns.md``) - Best practices and patterns
- **Result Objects** (``docs/api/results.md``) - Understanding result structures


Contributing Examples
---------------------

Have a great example? Consider contributing:

1. Create a new example file (e.g., ``plot_your_example.py``)
2. Follow the existing example structure
3. Include comprehensive comments
4. Add domain-agnostic synthetic data
5. Update this README


Questions or Issues?
--------------------

- Check the API Reference for detailed documentation
- Review Common Patterns for best practices
- See Quick Start for basic usage


License
-------

All examples are part of the TBR package and subject to the same license.
