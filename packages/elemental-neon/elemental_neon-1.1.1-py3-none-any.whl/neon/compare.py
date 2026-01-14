"""Comparison functions for floating-point numbers."""

import math
from collections.abc import Sequence

__all__ = [
    "near",
    "near_rel",
    "near_abs",
    "near_zero",
    "is_integer",
    "compare",
    "less_or_near",
    "greater_or_near",
    "all_near",
    "near_many",
    # Batch operations
    "near_zero_many",
    "is_integer_many",
]


def near(a: float, b: float, *, rel_tol: float = 1e-9, abs_tol: float = 1e-9) -> bool:
    """Check if two floats are approximately equal.

    Uses a hybrid tolerance approach:
        abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

    Default tolerances (rel_tol=1e-9, abs_tol=1e-9) provide practical behavior
    for both large numbers (relative) and near-zero values (absolute).

    Special cases:
        - near(nan, nan) → False (NaN is not near anything)
        - near(inf, inf) → True (same infinity)
        - near(-inf, inf) → False
        - near(inf, x) → False for any finite x
        - near(0.0, -0.0) → True

    Args:
        a: First value
        b: Second value
        rel_tol: Relative tolerance (default 1e-9)
        abs_tol: Absolute tolerance (default 1e-9, better than math.isclose's 0.0)

    Returns:
        True if a and b are approximately equal

    Examples:
        >>> near(0.1 + 0.2, 0.3)
        True
        >>> near(1e-15, 0.0)  # Uses abs_tol
        True
        >>> near(1.0, 1.001, rel_tol=1e-2)
        True
        >>> near(1.0, 1.001, rel_tol=1e-4)
        False
        >>> near(float('nan'), float('nan'))
        False
        >>> near(float('inf'), float('inf'))
        True
    """
    # Handle NaN - NaN is not near anything, including itself
    if math.isnan(a) or math.isnan(b):
        return False

    # Handle infinities
    if math.isinf(a) or math.isinf(b):
        return a == b  # inf == inf, but inf != -inf and inf != finite

    # Standard relative/absolute tolerance check
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def near_rel(a: float, b: float, *, tol: float = 1e-9) -> bool:
    """Check if two floats are approximately equal using relative tolerance only.

    Purely relative comparison: abs(a - b) <= tol * max(abs(a), abs(b))

    Useful when you know both values are far from zero and want percentage-based
    comparison without absolute tolerance affecting the result.

    Args:
        a: First value
        b: Second value
        tol: Relative tolerance (default 1e-9)

    Returns:
        True if a and b are within relative tolerance

    Examples:
        >>> near_rel(1000.0, 1000.001, tol=1e-3)  # 0.1% tolerance
        True
        >>> near_rel(1000.0, 1001.0, tol=1e-3)    # 0.1% difference
        True
        >>> near_rel(1e-15, 2e-15, tol=1e-3)       # Works for small values
        True
    """
    return near(a, b, rel_tol=tol, abs_tol=0.0)


def near_abs(a: float, b: float, *, tol: float = 1e-9) -> bool:
    """Check if two floats are approximately equal using absolute tolerance only.

    Purely absolute comparison: abs(a - b) <= tol

    Useful for near-zero comparisons or when you want a fixed tolerance
    regardless of magnitude.

    Args:
        a: First value
        b: Second value
        tol: Absolute tolerance (default 1e-9)

    Returns:
        True if a and b are within absolute tolerance

    Examples:
        >>> near_abs(1e-15, 0.0)           # Default tol=1e-9
        True
        >>> near_abs(0.001, 0.002, tol=0.01)
        True
        >>> near_abs(1000.0, 1000.5, tol=1.0)
        True
    """
    return near(a, b, rel_tol=0.0, abs_tol=tol)


def near_zero(x: float, *, abs_tol: float = 1e-9) -> bool:
    """Check if a float is approximately zero.

    Args:
        x: Value to check
        abs_tol: Absolute tolerance (default 1e-9)

    Returns:
        True if x is within abs_tol of zero

    Examples:
        >>> near_zero(0.0)
        True
        >>> near_zero(-0.0)
        True
        >>> near_zero(1e-15)
        True
        >>> near_zero(1e-5)
        False
        >>> near_zero(float('nan'))
        False
    """
    if math.isnan(x):
        return False
    if math.isinf(x):
        return False
    return abs(x) <= abs_tol


def less_or_near(a: float, b: float, *, rel_tol: float = 1e-9, abs_tol: float = 1e-9) -> bool:
    """Check if a < b or a ≈ b.

    Args:
        a: First value
        b: Second value
        rel_tol: Relative tolerance (default 1e-9)
        abs_tol: Absolute tolerance (default 0.0)

    Returns:
        True if a is less than or approximately equal to b

    Examples:
        >>> less_or_near(1.0, 2.0)
        True
        >>> less_or_near(1.0, 1.0 + 1e-15)
        True
        >>> less_or_near(2.0, 1.0)
        False
    """
    return a < b or near(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def greater_or_near(
    a: float, b: float, *, rel_tol: float = 1e-9, abs_tol: float = 1e-9
) -> bool:
    """Check if a > b or a ≈ b.

    Args:
        a: First value
        b: Second value
        rel_tol: Relative tolerance (default 1e-9)
        abs_tol: Absolute tolerance (default 0.0)

    Returns:
        True if a is greater than or approximately equal to b

    Examples:
        >>> greater_or_near(2.0, 1.0)
        True
        >>> greater_or_near(1.0, 1.0 - 1e-15)
        True
        >>> greater_or_near(1.0, 2.0)
        False
    """
    return a > b or near(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def compare(a: float, b: float, *, rel_tol: float = 1e-9, abs_tol: float = 1e-9) -> int:
    """Compare two floats with tolerance (spaceship operator).

    Returns:
        -1 if a < b
         0 if a ≈ b (within tolerance)
        +1 if a > b

    Args:
        a: First value
        b: Second value
        rel_tol: Relative tolerance (default 1e-9)
        abs_tol: Absolute tolerance (default 0.0)

    Examples:
        >>> compare(1.0, 2.0)
        -1
        >>> compare(2.0, 1.0)
        1
        >>> compare(1.0, 1.0 + 1e-15)
        0
    """
    if near(a, b, rel_tol=rel_tol, abs_tol=abs_tol):
        return 0
    return -1 if a < b else 1


def all_near(
    pairs: Sequence[tuple[float, float]], *, rel_tol: float = 1e-9, abs_tol: float = 1e-9
) -> bool:
    """Check if all pairs of values are approximately equal.

    Args:
        pairs: Sequence of (a, b) tuples
        rel_tol: Relative tolerance (default 1e-9)
        abs_tol: Absolute tolerance (default 0.0)

    Returns:
        True if all pairs are approximately equal

    Examples:
        >>> all_near([(0.1 + 0.2, 0.3), (1.0, 1.0)])
        True
        >>> all_near([(1.0, 1.0), (1.0, 2.0)])
        False
    """
    return all(near(a, b, rel_tol=rel_tol, abs_tol=abs_tol) for a, b in pairs)


def is_integer(x: float, *, abs_tol: float = 1e-9) -> bool:
    """Check if a float is near an integer value.

    Args:
        x: Value to check
        abs_tol: Absolute tolerance (default 1e-9)

    Returns:
        True if x is approximately an integer

    Examples:
        >>> is_integer(3.0)
        True
        >>> is_integer(3.0000000001)
        True
        >>> is_integer(3.1)
        False
        >>> is_integer(float('inf'))
        False
        >>> is_integer(float('nan'))
        False
    """
    if math.isnan(x) or math.isinf(x):
        return False
    return abs(x - round(x)) <= abs_tol


def near_many(
    pairs: Sequence[tuple[float, float]], *, rel_tol: float = 1e-9, abs_tol: float = 1e-9
) -> list[bool]:
    """Batch comparison of pairs.

    Args:
        pairs: Sequence of (a, b) tuples
        rel_tol: Relative tolerance (default 1e-9)
        abs_tol: Absolute tolerance (default 0.0)

    Returns:
        List of boolean results for each pair

    Examples:
        >>> near_many([(0.1 + 0.2, 0.3), (1.0, 1.0), (1.0, 2.0)])
        [True, True, False]
    """
    return [near(a, b, rel_tol=rel_tol, abs_tol=abs_tol) for a, b in pairs]


def near_zero_many(values: Sequence[float], *, abs_tol: float = 1e-9) -> list[bool]:
    """Batch near-zero check.

    Args:
        values: Values to check
        abs_tol: Absolute tolerance (default 1e-9)

    Returns:
        List of boolean results

    Examples:
        >>> near_zero_many([1e-15, 0.1, -1e-16])
        [True, False, True]
    """
    return [near_zero(x, abs_tol=abs_tol) for x in values]


def is_integer_many(values: Sequence[float], *, abs_tol: float = 1e-9) -> list[bool]:
    """Batch integer check.

    Args:
        values: Values to check
        abs_tol: Absolute tolerance (default 1e-9)

    Returns:
        List of boolean results

    Examples:
        >>> is_integer_many([3.0, 3.1, 2.9999999999])
        [True, False, True]
    """
    return [is_integer(x, abs_tol=abs_tol) for x in values]
