"""
TBR Package Exception Classes.

This module defines custom exceptions for the TBR package, providing
specialized error handling for statistical and computational scenarios.

The design philosophy emphasizes:
- Minimal hierarchy with only essential custom exceptions
- Inheritance from built-in exceptions for compatibility
- Domain-agnostic naming suitable for any statistical application
- Clear, descriptive error messages for debugging

Most validation errors use built-in exceptions (ValueError, TypeError)
as these provide appropriate semantics for parameter and data validation.
"""

from typing import Optional


class TBRError(Exception):
    """
    Base exception class for TBR package-specific errors.

    This serves as the root exception for all custom TBR exceptions,
    allowing users to catch all package-specific errors with a single
    except clause while maintaining compatibility with built-in exceptions.

    Examples
    --------
    >>> try:
    ...     # TBR analysis code
    ...     pass
    ... except TBRError as e:
    ...     print(f"TBR-specific error: {e}")
    ... except ValueError as e:
    ...     print(f"General validation error: {e}")
    """


class ConvergenceError(TBRError, RuntimeError):
    """
    Raised when iterative algorithms fail to converge.

    This exception is raised when numerical algorithms (such as optimization
    routines or iterative solvers) fail to reach convergence within the
    specified tolerance or maximum number of iterations.

    Inherits from both TBRError and RuntimeError to maintain compatibility
    with standard exception handling patterns.

    Parameters
    ----------
    message : str
        Description of the convergence failure
    iterations : int, optional
        Number of iterations attempted before failure
    tolerance : float, optional
        Convergence tolerance that could not be achieved

    Examples
    --------
    >>> try:
    ...     # Model fitting that may fail to converge
    ...     pass
    ... except ConvergenceError as e:
    ...     print(f"Algorithm failed to converge: {e}")

    Notes
    -----
    This exception provides specific information about algorithmic failures
    that are distinct from general computational errors, enabling precise
    error handling for convergence-related issues.
    """

    def __init__(
        self,
        message: str,
        iterations: Optional[int] = None,
        tolerance: Optional[float] = None,
    ) -> None:
        super().__init__(message)
        self.iterations = iterations
        self.tolerance = tolerance


class NumericalInstabilityError(TBRError, RuntimeError):
    """
    Raised when numerical computations become unstable or invalid.

    This exception is raised when mathematical operations produce results
    that are numerically unstable, such as singular matrices, extreme
    values, or computations that violate mathematical assumptions.

    Inherits from both TBRError and RuntimeError to indicate that the
    error is related to computational execution rather than input validation.

    Examples
    --------
    >>> try:
    ...     # Matrix operations that may become singular
    ...     pass
    ... except NumericalInstabilityError as e:
    ...     print(f"Numerical computation failed: {e}")

    Notes
    -----
    This exception covers scenarios where computations are mathematically
    valid but numerically problematic, such as:
    - Singular or near-singular covariance matrices
    - Extreme values causing overflow/underflow
    - Loss of numerical precision in statistical calculations
    """


class InsufficientDataError(TBRError, ValueError):
    """
    Raised when data is insufficient for reliable statistical analysis.

    This exception is raised when the available data does not meet the
    minimum requirements for performing reliable statistical inference,
    such as insufficient sample sizes or inadequate time periods.

    Inherits from both TBRError and ValueError to indicate that while
    the data format may be correct, the quantity or quality is inadequate
    for the requested analysis.

    Parameters
    ----------
    message : str
        Description of the data insufficiency
    required : int, optional
        Minimum required sample size or observations
    available : int, optional
        Actual number of observations available

    Examples
    --------
    >>> try:
    ...     # Statistical analysis requiring minimum sample size
    ...     pass
    ... except InsufficientDataError as e:
    ...     print(f"Insufficient data for analysis: {e}")

    Notes
    -----
    This exception is more specific than a generic ValueError for cases
    where the data structure and types are correct, but the statistical
    requirements for reliable inference are not met.
    """

    def __init__(
        self,
        message: str,
        required: Optional[int] = None,
        available: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.required = required
        self.available = available
