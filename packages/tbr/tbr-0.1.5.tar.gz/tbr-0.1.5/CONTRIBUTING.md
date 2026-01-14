# Contributing to TBR

Thank you for your interest in contributing to TBR! This document provides guidelines for contributing to the project.

## Ways to Contribute

- **Report bugs** - Open an issue describing the bug and how to reproduce it
- **Suggest features** - Open an issue describing the feature and its use case
- **Improve documentation** - Fix typos, clarify explanations, add examples
- **Submit code** - Fix bugs or implement features via pull requests

## Getting Started

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/idohi/tbr.git
cd tbr
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .[dev]
```

3. Install pre-commit hooks:
```bash
pre-commit install
```

### Running Tests

```bash
# Run all tests
make test-all

# Run with coverage
make test-cov-all

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/mathematical/  # Mathematical validation tests
pytest tests/performance/   # Performance tests
```

### Code Quality

All code must pass quality checks:

```bash
# Run linting
make lint

# Format code
make format

# Type checking
make type-check

# All checks
make check
```

## Contribution Guidelines

### Reporting Issues

When reporting bugs, please include:
- Python version and operating system
- TBR version (`import tbr; print(tbr.__version__)`)
- Minimal reproducible example
- Expected vs. actual behavior
- Full error traceback if applicable

### Submitting Pull Requests

1. **Fork the repository** and create a feature branch
2. **Write tests** for new functionality
3. **Maintain 100% test coverage** - all new code must be tested
4. **Follow code style** - use Black, isort, and pass all linting
5. **Update documentation** - include docstrings and update relevant docs
6. **Write clear commit messages** - explain what and why
7. **Reference issues** - if fixing a bug, reference the issue number

### Code Standards

- **Type hints** - all functions must have complete type annotations
- **Docstrings** - all public APIs must have comprehensive structured docstrings
- **Testing** - maintain 100% code coverage
- **Style** - follow PEP 8, enforced by Black and Ruff
- **Performance** - avoid performance regressions

### Docstring Format

Use structured docstrings with clear sections:

```python
def example_function(param1: int, param2: str) -> bool:
    """
    Brief one-line description.

    Longer description if needed, explaining the function's purpose
    and behavior in detail.

    Parameters
    ----------
    param1 : int
        Description of param1.
    param2 : str
        Description of param2.

    Returns
    -------
    bool
        Description of return value.

    Examples
    --------
    >>> example_function(42, "hello")
    True
    """
    pass
```

## Development Workflow

1. **Create an issue** - discuss the change before starting work
2. **Create a branch** - use descriptive branch names (e.g., `fix-variance-calculation`)
3. **Make changes** - write code, tests, and documentation
4. **Test locally** - ensure all tests pass and coverage is 100%
5. **Commit changes** - write clear, descriptive commit messages
6. **Push to fork** - push your branch to your forked repository
7. **Open pull request** - describe changes, reference issues, and request review
8. **Address feedback** - respond to review comments and make requested changes
9. **Merge** - maintainers will merge after approval

## Testing Guidelines

- **Unit tests** - test individual functions in isolation
- **Integration tests** - test complete workflows
- **Mathematical tests** - validate statistical accuracy
- **Performance tests** - prevent performance regressions
- **Edge cases** - test boundary conditions and error handling

## Mathematical Contributions

TBR implements rigorous statistical methodology. When contributing:

- **Validate formulas** - ensure mathematical correctness
- **Reference sources** - cite statistical literature when applicable
- **Test accuracy** - use known values and cross-validation
- **Document assumptions** - explain statistical assumptions clearly

## Questions?

- **GitHub Issues** - for bugs, features, and general questions
- **GitHub Discussions** - for broader discussions and ideas

## License

By contributing, you agree that your contributions will be licensed under the BSD-3-Clause License.

---

Thank you for contributing to TBR!
