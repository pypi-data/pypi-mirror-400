"""Safe arithmetic operations with edge case handling."""

import math
from collections.abc import Sequence
from typing import Optional, cast

from ._validation import validate_equal_length, validate_non_empty
from .compare import near_zero

__all__ = [
    "div",
    "div_or_zero",
    "div_or_inf",
    "mod",
    "sqrt",
    "log",
    "pow",
    "sum_exact",
    "mean_exact",
    # Batch operations
    "div_many",
    "sqrt_many",
    "log_many",
    "pow_many",
]


def div(
    a: float, b: float, *, default: Optional[float] = None, zero_tol: float = 0.0
) -> Optional[float]:
    """Safe division with configurable zero handling.

    Args:
        a: Numerator
        b: Denominator
        default: Value to return if b is zero/near-zero (default None)
        zero_tol: Tolerance for considering b as zero (default 0.0)

    Returns:
        a / b if b is not zero, otherwise default

    Examples:
        >>> div(6, 3)
        2.0
        >>> div(1, 0)
        >>> div(1, 0, default=0.0)
        0.0
        >>> div(1, 1e-15, zero_tol=1e-10)
    """
    if near_zero(b, abs_tol=zero_tol):
        return default
    return a / b


def div_or_zero(a: float, b: float, *, zero_tol: float = 0.0) -> float:
    """Safe division that returns 0.0 if denominator is zero.

    Args:
        a: Numerator
        b: Denominator
        zero_tol: Tolerance for considering b as zero (default 0.0)

    Returns:
        a / b if b is not zero, otherwise 0.0

    Examples:
        >>> div_or_zero(6, 3)
        2.0
        >>> div_or_zero(1, 0)
        0.0
    """
    result = div(a, b, default=0.0, zero_tol=zero_tol)
    return result if result is not None else 0.0


def div_or_inf(a: float, b: float, *, zero_tol: float = 0.0) -> float:
    """Safe division that returns ±inf if denominator is zero.

    Args:
        a: Numerator
        b: Denominator
        zero_tol: Tolerance for considering b as zero (default 0.0)

    Returns:
        a / b if b is not zero, otherwise ±inf (sign matches a)
        Special case: 0/0 returns NaN

    Examples:
        >>> div_or_inf(6, 3)
        2.0
        >>> div_or_inf(1, 0)
        inf
        >>> div_or_inf(-1, 0)
        -inf
        >>> import math
        >>> math.isnan(div_or_inf(0, 0))
        True
    """
    if near_zero(b, abs_tol=zero_tol):
        if near_zero(a, abs_tol=zero_tol):
            return math.nan  # 0/0 → NaN
        return math.copysign(math.inf, a)
    return a / b


def mod(
    a: float, b: float, *, default: Optional[float] = None, zero_tol: float = 0.0
) -> Optional[float]:
    """Safe modulo with zero handling using IEEE 754 semantics.

    Uses math.fmod() which matches IEEE 754 behavior (result has sign of dividend).
    This avoids wrapping small negative errors to large positive values.

    Args:
        a: Dividend
        b: Divisor
        default: Value to return if b is zero/near-zero (default None)
        zero_tol: Tolerance for considering b as zero (default 0.0)

    Returns:
        fmod(a, b) if b is not zero, otherwise default

    Examples:
        >>> mod(7, 3)
        1.0
        >>> mod(7, 0)
        >>> mod(7, 0, default=0.0)
        0.0
        >>> mod(-1e-100, 1.0)  # Preserves sign of dividend
        -1e-100
    """
    if near_zero(b, abs_tol=zero_tol):
        return default
    return math.fmod(a, b)


def sqrt(x: float, *, default: Optional[float] = None) -> Optional[float]:
    """Safe square root that handles negative inputs.

    Args:
        x: Value to take square root of
        default: Value to return if x < 0 (default None)

    Returns:
        sqrt(x) if x >= 0, otherwise default

    Examples:
        >>> sqrt(4)
        2.0
        >>> sqrt(-1)
        >>> sqrt(-1, default=0.0)
        0.0
        >>> sqrt(0)
        0.0
    """
    if x < 0:
        return default
    return math.sqrt(x)


def log(
    x: float, *, base: Optional[float] = None, default: Optional[float] = None
) -> Optional[float]:
    """Safe logarithm that handles non-positive inputs and invalid bases.

    Args:
        x: Value to take logarithm of
        base: Logarithm base (default e, natural log)
        default: Value to return if x <= 0 or base is invalid (default None)

    Returns:
        log(x) if x > 0 and base is valid, otherwise default

    Examples:
        >>> import math
        >>> abs(log(math.e) - 1.0) < 1e-10
        True
        >>> log(0)
        >>> log(-1)
        >>> log(100, base=10)
        2.0
        >>> log(10, base=1.0)  # Invalid base
        >>> log(10, base=-2.0)  # Invalid base
    """
    if x <= 0:
        return default

    try:
        if base is None:
            return math.log(x)
        return math.log(x, base)
    except (ValueError, ZeroDivisionError):
        return default


def pow(base: float, exp: float, *, default: Optional[float] = None) -> Optional[float]:
    """Safe power that handles edge cases.

    Args:
        base: Base value
        exp: Exponent
        default: Value to return on error (default None)

    Returns:
        base ** exp, or default if operation would raise an error

    Examples:
        >>> pow(2, 3)
        8.0
        >>> pow(-1, 0.5)  # Would raise error
        >>> pow(-1, 0.5, default=0.0)
        0.0
        >>> pow(0, 0)
        1.0
    """
    try:
        return cast(float, base**exp)
    except (ValueError, ZeroDivisionError, OverflowError):
        return default


def sum_exact(values: Sequence[float]) -> float:
    """Sum using math.fsum() for exact floating-point summation.

    Uses Python's built-in math.fsum() which tracks all partial sums for
    maximum precision. This is implemented in C and is faster than Python-based
    Kahan summation while providing better accuracy.

    Note: math.fsum() provides exact summation but cannot recover from
    catastrophic cancellation (e.g., [1e16, 1.0, -1e16] still loses the 1.0).

    Args:
        values: Sequence of values to sum

    Returns:
        Sum of values with maximum precision

    Raises:
        EmptyInputError: If values is empty

    Examples:
        >>> sum_exact([0.1] * 10) == 1.0
        True
        >>> # More accurate than built-in sum:
        >>> sum([0.1] * 10)  # May have rounding error
        0.9999999999999999
        >>> sum_exact([0.1] * 10)  # Exact
        1.0
    """
    validate_non_empty(values, "values")
    return math.fsum(values)


def mean_exact(values: Sequence[float]) -> float:
    """Mean using math.fsum() for improved precision.

    Args:
        values: Sequence of values

    Returns:
        Mean of values with maximum precision

    Raises:
        EmptyInputError: If values is empty

    Examples:
        >>> mean_exact([1.0, 2.0, 3.0])
        2.0
    """
    validate_non_empty(values, "values")
    return sum_exact(values) / len(values)


# ============================================================================
# Batch Operations
# ============================================================================


def div_many(
    a_values: Sequence[float],
    b_values: Sequence[float],
    *,
    default: Optional[float] = None,
    zero_tol: float = 0.0,
) -> list[Optional[float]]:
    """Batch safe division.

    Args:
        a_values: Numerators
        b_values: Denominators
        default: Value to return for zero divisions
        zero_tol: Tolerance for considering b as zero

    Returns:
        List of division results

    Raises:
        ValueError: If a_values and b_values have different lengths

    Examples:
        >>> div_many([6, 4], [3, 2])
        [2.0, 2.0]
        >>> div_many([1, 2, 3], [0, 2, 0], default=0.0)
        [0.0, 1.0, 0.0]
    """
    validate_equal_length(a_values, b_values, "a_values", "b_values")
    return [div(a, b, default=default, zero_tol=zero_tol) for a, b in zip(a_values, b_values)]


def sqrt_many(
    values: Sequence[float], *, default: Optional[float] = None
) -> list[Optional[float]]:
    """Batch safe square root.

    Args:
        values: Values to take square root of
        default: Value to return for negative inputs

    Returns:
        List of sqrt results

    Examples:
        >>> sqrt_many([4, 9, 16])
        [2.0, 3.0, 4.0]
        >>> sqrt_many([4, -1, 9], default=0.0)
        [2.0, 0.0, 3.0]
    """
    return [sqrt(x, default=default) for x in values]


def log_many(
    values: Sequence[float],
    *,
    base: Optional[float] = None,
    default: Optional[float] = None,
) -> list[Optional[float]]:
    """Batch safe logarithm.

    Args:
        values: Values to take logarithm of
        base: Logarithm base (default e)
        default: Value to return for invalid inputs

    Returns:
        List of log results

    Examples:
        >>> log_many([1, 10, 100], base=10)
        [0.0, 1.0, 2.0]
    """
    return [log(x, base=base, default=default) for x in values]


def pow_many(
    bases: Sequence[float],
    exps: Sequence[float],
    *,
    default: Optional[float] = None,
) -> list[Optional[float]]:
    """Batch safe power.

    Args:
        bases: Base values
        exps: Exponents
        default: Value to return on error

    Returns:
        List of power results

    Raises:
        ValueError: If bases and exps have different lengths

    Examples:
        >>> pow_many([2, 3, 4], [3, 2, 1])
        [8.0, 9.0, 4.0]
    """
    validate_equal_length(bases, exps, "bases", "exps")
    return [pow(b, e, default=default) for b, e in zip(bases, exps)]
