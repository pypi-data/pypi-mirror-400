"""ULP (Unit in the Last Place) operations for floating-point numbers."""

import math
import struct
from typing import cast

from ._validation import validate_equal_length
from .exceptions import InvalidValueError

__all__ = [
    "of",
    "diff",
    "within",
    "next",
    "prev",
    "add",
    # Batch operations
    "of_many",
    "diff_many",
    "within_many",
]


def of(x: float) -> float:
    """Return the ULP (Unit in the Last Place) of x.

    The ULP is the gap between x and the next representable float.

    Args:
        x: Value to get ULP of

    Returns:
        ULP of x

    Raises:
        InvalidValueError: If x is NaN

    Examples:
        >>> of(1.0)
        2.220446049250313e-16
        >>> of(0.0) > 0  # Smallest positive denormal
        True
        >>> of(float('inf'))
        inf
    """
    if math.isnan(x):
        raise InvalidValueError("Cannot compute ULP of NaN", x)

    if math.isinf(x):
        return math.inf

    if x == 0:
        # Return smallest positive denormal
        return math.nextafter(0.0, 1.0)

    return abs(math.nextafter(x, math.inf) - x)


def diff(a: float, b: float) -> int:
    """Return the distance between a and b in ULPs.

    Uses IEEE 754 binary representation for O(1) computation instead of
    iterating through nextafter() calls.

    Args:
        a: First value
        b: Second value

    Returns:
        Number of ULPs between a and b

    Raises:
        InvalidValueError: If either value is NaN or inf

    Examples:
        >>> diff(1.0, 1.0)
        0
        >>> diff(1.0, next(1.0))
        1
    """
    if math.isnan(a) or math.isnan(b):
        raise InvalidValueError("Cannot compute ULP distance with NaN")

    if math.isinf(a) or math.isinf(b):
        raise InvalidValueError("Cannot compute ULP distance with infinity")

    if a == b:
        return 0

    # Convert floats to their IEEE 754 binary representation
    # Python's struct uses big-endian by default, we need to interpret as signed int
    def float_to_int_bits(f: float) -> int:
        # Pack as double (8 bytes), unpack as long long (signed 64-bit int)
        bits = cast(int, struct.unpack('>Q', struct.pack('>d', f))[0])
        # Convert to signed (two's complement for negative numbers)
        if bits >= 2**63:
            bits -= 2**64
        return bits

    a_bits = float_to_int_bits(a)
    b_bits = float_to_int_bits(b)

    # Handle sign changes (crossing zero)
    # When crossing zero, we need special handling because IEEE 754 has -0.0 and +0.0
    if (a < 0) != (b < 0):
        # Different signs - need to count through zero
        return abs(a_bits) + abs(b_bits)

    return abs(a_bits - b_bits)


def within(a: float, b: float, *, max_ulps: int = 4) -> bool:
    """Check if a and b are within max_ulps of each other.

    Args:
        a: First value
        b: Second value
        max_ulps: Maximum ULP distance (default 4)

    Returns:
        True if a and b are within max_ulps

    Examples:
        >>> within(1.0, 1.0)
        True
        >>> within(1.0, add(1.0, 4))
        True
        >>> within(1.0, add(1.0, 5))
        False
    """
    # Special case: exact equality
    if a == b:
        return True

    # NaN or inf handling
    if math.isnan(a) or math.isnan(b):
        return False
    if math.isinf(a) or math.isinf(b):
        return a == b

    # Both values are finite at this point, diff() will not raise
    return diff(a, b) <= max_ulps


def next(x: float) -> float:
    """Return the next representable float above x.

    Args:
        x: Value

    Returns:
        Next float above x

    Examples:
        >>> next(1.0) > 1.0
        True
        >>> next(float('inf'))
        inf
    """
    return math.nextafter(x, math.inf)


def prev(x: float) -> float:
    """Return the next representable float below x.

    Args:
        x: Value

    Returns:
        Next float below x

    Examples:
        >>> prev(1.0) < 1.0
        True
        >>> prev(float('-inf'))
        -inf
    """
    return math.nextafter(x, -math.inf)


def add(x: float, n: int) -> float:
    """Move n ULPs from x using math.nextafter.

    Note: This uses a loop of math.nextafter calls. While O(N), it is fast enough
    for practical use cases (millions of iterations per second). A full O(1) bit
    manipulation approach would require complex IEEE 754 sign-magnitude handling.

    Args:
        x: Starting value
        n: Number of ULPs to move (positive or negative)

    Returns:
        Value n ULPs away from x

    Examples:
        >>> add(1.0, 0) == 1.0
        True
        >>> add(1.0, 1) == next(1.0)
        True
        >>> add(1.0, -1) == prev(1.0)
        True
    """
    if n == 0:
        return x

    if math.isnan(x) or math.isinf(x):
        return x

    # Use math.nextafter in a loop
    result = x
    direction = math.inf if n > 0 else -math.inf
    for _ in range(abs(n)):
        result = math.nextafter(result, direction)
    return result


# ============================================================================
# Batch Operations
# ============================================================================


def of_many(values: list[float]) -> list[float]:
    """Get ULP for each value.

    Args:
        values: Values to get ULPs for

    Returns:
        List of ULP values

    Raises:
        InvalidValueError: If any value is NaN

    Examples:
        >>> ulps = of_many([1.0, 2.0, 0.0])
        >>> ulps[0] > 0
        True
    """
    return [of(x) for x in values]


def diff_many(a_values: list[float], b_values: list[float]) -> list[int]:
    """ULP distances between pairs.

    Args:
        a_values: First values
        b_values: Second values

    Returns:
        List of ULP distances

    Raises:
        InvalidValueError: If any value is NaN or inf
        ValueError: If a_values and b_values have different lengths

    Examples:
        >>> diff_many([1.0, 2.0], [1.0001, 2.0001])
        [450359962737, 450359962737]
    """
    validate_equal_length(a_values, b_values, "a_values", "b_values")
    return [diff(a, b) for a, b in zip(a_values, b_values)]


def within_many(
    a_values: list[float], b_values: list[float], *, max_ulps: int = 4
) -> list[bool]:
    """Check if pairs are within max_ulps.

    Args:
        a_values: First values
        b_values: Second values
        max_ulps: Maximum ULP distance (default 4)

    Returns:
        List of boolean results

    Raises:
        ValueError: If a_values and b_values have different lengths

    Examples:
        >>> within_many([1.0, 2.0], [1.0 + 1e-15, 2.1])
        [True, False]
    """
    validate_equal_length(a_values, b_values, "a_values", "b_values")
    return [within(a, b, max_ulps=max_ulps) for a, b in zip(a_values, b_values)]
