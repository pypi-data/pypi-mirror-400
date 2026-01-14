"""Clamping and snapping functions."""

import math
from collections.abc import Sequence

from .compare import near, near_zero

__all__ = [
    "to_zero",
    "to_int",
    "to_value",
    "to_range",
    "to_values",
    # Batch operations
    "to_zero_many",
    "to_int_many",
    "to_range_many",
]


def to_zero(x: float, *, abs_tol: float = 1e-9) -> float:
    """Snap to 0.0 if near zero, otherwise return x unchanged.

    Args:
        x: Value to check
        abs_tol: Absolute tolerance (default 1e-9)

    Returns:
        0.0 if x is near zero, otherwise x

    Examples:
        >>> to_zero(1e-15)
        0.0
        >>> to_zero(0.1)
        0.1
        >>> to_zero(-1e-15)
        0.0
    """
    # NaN passes through unchanged
    if math.isnan(x):
        return x

    return 0.0 if near_zero(x, abs_tol=abs_tol) else x


def to_int(x: float, *, abs_tol: float = 1e-9) -> float:
    """Snap to nearest integer value if near it, otherwise return x unchanged.

    IMPORTANT: Always returns a float type (e.g., 3.0, not 3) for consistent typing,
    even when snapping to an integer value. The name "to_int" refers to snapping to
    an integer VALUE, not converting to the int TYPE.

    If you need an actual int type for indexing, use int(result) after calling this.

    Args:
        x: Value to check
        abs_tol: Absolute tolerance (default 1e-9)

    Returns:
        Float value, snapped to nearest integer if within tolerance

    Examples:
        >>> to_int(3.0)
        3.0
        >>> to_int(2.9999999999)
        3.0
        >>> to_int(2.5)
        2.5
        >>> to_int(-3.0000000001)
        -3.0
        >>> int(to_int(2.9999999999))  # For list indexing
        3
    """
    # NaN and inf pass through unchanged
    if math.isnan(x) or math.isinf(x):
        return x

    rounded = round(x)
    if abs(x - rounded) <= abs_tol:
        return float(rounded)
    return x


def to_value(x: float, target: float, *, rel_tol: float = 1e-9, abs_tol: float = 1e-9) -> float:
    """Snap to target if near it, otherwise return x unchanged.

    Args:
        x: Value to check
        target: Target value to snap to
        rel_tol: Relative tolerance (default 1e-9)
        abs_tol: Absolute tolerance (default 0.0)

    Returns:
        target if x is near target, otherwise x

    Examples:
        >>> to_value(0.333333333, 1/3)
        0.3333333333333333
        >>> to_value(0.5, 1/3)
        0.5
    """
    # NaN passes through unchanged
    if math.isnan(x):
        return x

    return target if near(x, target, rel_tol=rel_tol, abs_tol=abs_tol) else x


def to_range(x: float, lo: float, hi: float) -> float:
    """Clamp x to the range [lo, hi].

    Args:
        x: Value to clamp
        lo: Lower bound
        hi: Upper bound

    Returns:
        x clamped to [lo, hi]

    Examples:
        >>> to_range(5, 0, 10)
        5
        >>> to_range(-5, 0, 10)
        0
        >>> to_range(15, 0, 10)
        10
    """
    # NaN passes through unchanged
    if math.isnan(x):
        return x

    return max(lo, min(x, hi))


def to_values(
    x: float, targets: Sequence[float], *, rel_tol: float = 1e-9, abs_tol: float = 1e-9
) -> float:
    """Snap to nearest target if near any, otherwise return x unchanged.

    Args:
        x: Value to check
        targets: Sequence of target values
        rel_tol: Relative tolerance (default 1e-9)
        abs_tol: Absolute tolerance (default 0.0)

    Returns:
        Nearest target if x is near any target, otherwise x

    Examples:
        >>> to_values(0.499999999, [0.0, 0.5, 1.0])
        0.5
        >>> to_values(0.3, [0.0, 0.5, 1.0])
        0.3
    """
    # NaN passes through unchanged
    if math.isnan(x):
        return x

    # Find nearest target that x is near
    for target in targets:
        if near(x, target, rel_tol=rel_tol, abs_tol=abs_tol):
            return target

    return x


def to_zero_many(values: Sequence[float], *, abs_tol: float = 1e-9) -> list[float]:
    """Batch snap to zero.

    Args:
        values: Sequence of values
        abs_tol: Absolute tolerance (default 1e-9)

    Returns:
        List of values snapped to zero where applicable

    Examples:
        >>> to_zero_many([1e-15, 0.1, -1e-15])
        [0.0, 0.1, 0.0]
    """
    return [to_zero(x, abs_tol=abs_tol) for x in values]


def to_int_many(values: Sequence[float], *, abs_tol: float = 1e-9) -> list[float]:
    """Batch snap to nearest integer.

    Args:
        values: Sequence of values
        abs_tol: Absolute tolerance (default 1e-9)

    Returns:
        List of values snapped to integers where applicable

    Examples:
        >>> to_int_many([2.9999999, 3.1, 5.0])
        [3.0, 3.1, 5.0]
    """
    return [to_int(x, abs_tol=abs_tol) for x in values]


def to_range_many(values: Sequence[float], lo: float, hi: float) -> list[float]:
    """Batch clamp to range.

    Args:
        values: Sequence of values
        lo: Lower bound
        hi: Upper bound

    Returns:
        List of values clamped to [lo, hi]

    Examples:
        >>> to_range_many([5, -5, 15], 0, 10)
        [5, 0, 10]
    """
    return [to_range(x, lo, hi) for x in values]
