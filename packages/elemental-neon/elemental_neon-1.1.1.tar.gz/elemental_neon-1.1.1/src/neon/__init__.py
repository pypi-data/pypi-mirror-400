"""Neon - Near-equality and tolerance arithmetic for floating-point numbers.

elemental-neon is a zero-dependency library for floating-point comparison and
tolerance math. It handles approximate equality, safe division, ULP comparisons,
and numerical clamping.

Modules:
    compare: Approximate equality comparisons
    clamp: Value snapping and clamping
    safe: Safe arithmetic operations
    ulp: ULP-based operations

Example:
    >>> from neon import compare
    >>> compare.near(0.1 + 0.2, 0.3)
    True
"""

from . import clamp, compare, inspect, safe, ulp
from .clamp import to_int, to_range, to_zero

# Export most commonly used functions at top level for ergonomics
# Users can do: from neon import near, to_zero, div
from .compare import is_integer, near, near_zero
from .exceptions import (
    EmptyInputError,
    InvalidValueError,
    NeonError,
)
from .safe import div, sqrt, sum_exact
from .ulp import diff as ulp_diff
from .ulp import of as ulp_of
from .ulp import within as ulp_within

__version__ = "1.1.1"

__all__ = [
    # Modules
    "compare",
    "clamp",
    "safe",
    "ulp",
    "inspect",  # New in v1.1.0
    # Exceptions
    "NeonError",
    "InvalidValueError",
    "EmptyInputError",
    # Most commonly used functions (ergonomic top-level exports)
    "near",
    "near_zero",
    "is_integer",
    "to_zero",
    "to_int",
    "to_range",
    "div",
    "sqrt",
    "sum_exact",
    "ulp_of",
    "ulp_diff",
    "ulp_within",
]
