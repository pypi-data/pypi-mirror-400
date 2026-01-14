# Design: neon.numpy - Vectorized Safe Operations

**Status:** Proposed for v1.1.0
**Author:** Neon Contributors
**Date:** 2026-01-04

## Overview

Extend Neon to support NumPy array operations while maintaining the same safety guarantees as scalar operations. This is the foundation for PyTorch/JAX support.

---

## Goals

1. **Vectorized Performance:** Match hand-written NumPy code performance (no Python loops)
2. **Broadcasting Support:** Follow NumPy broadcasting semantics
3. **Type Safety:** Full type hints with proper array shape annotations
4. **Zero Dependencies (Core):** NumPy is an optional dependency via extras
5. **API Consistency:** Mirror scalar API from `neon.safe`, `neon.compare`, `neon.clamp`

---

## Non-Goals

- Custom C extensions (start with pure NumPy/Python)
- GPU acceleration (that's for PyTorch/JAX)
- In-place operations (keep immutable/functional)
- Multi-dimensional tolerances (use scalar tolerances applied element-wise)

---

## API Design

### Module Structure

```
neon/
├── numpy/
│   ├── __init__.py          # Public API
│   ├── _safe.py             # Safe arithmetic (div, sqrt, log, etc.)
│   ├── _compare.py          # Comparisons (near, near_zero, etc.)
│   ├── _clamp.py            # Clamping (to_zero, to_range, etc.)
│   └── _utils.py            # Shared utilities
```

### Import Strategy

```python
# Option 1: Explicit import (recommended for clarity)
import neon.numpy as nnp
result = nnp.div_safe(a, b, default=0.0)

# Option 2: Submodule import
from neon.numpy import div_safe
result = div_safe(a, b, default=0.0)

# Option 3: Works with scalar neon too
import neon
scalar_result = neon.div(1.0, 0.0, default=0.0)      # Scalar
array_result = neon.numpy.div_safe(arr, 0.0, default=0.0)  # Array
```

---

## Detailed API

### 1. Safe Arithmetic (`neon.numpy._safe`)

#### `div_safe(a, b, *, default=None, zero_tol=0.0)`

Vectorized safe division.

**Signature:**
```python
def div_safe(
    a: ArrayLike,
    b: ArrayLike,
    *,
    default: Optional[float | ArrayLike] = None,
    zero_tol: float = 0.0
) -> np.ndarray:
    """Safely divide arrays element-wise.

    Args:
        a: Numerator (scalar or array)
        b: Denominator (scalar or array)
        default: Value for division by zero (scalar or array)
        zero_tol: Tolerance for considering denominator as zero

    Returns:
        Array of same shape as broadcast(a, b)

    Examples:
        >>> a = np.array([1.0, 2.0, 3.0])
        >>> b = np.array([2.0, 0.0, 4.0])
        >>> div_safe(a, b, default=0.0)
        array([0.5, 0.0, 0.75])

        >>> div_safe(a, b, default=np.nan)
        array([0.5, nan, 0.75])
    """
```

**Implementation Strategy:**
```python
def div_safe(a, b, *, default=None, zero_tol=0.0):
    a = np.asarray(a)
    b = np.asarray(b)

    # Check for near-zero using vectorized comparison
    if zero_tol > 0:
        is_zero = np.abs(b) <= zero_tol
    else:
        is_zero = (b == 0)

    # Use np.where for vectorized conditional
    if default is None:
        # Return masked array or set to nan
        result = np.where(is_zero, np.nan, a / np.where(is_zero, 1.0, b))
    else:
        result = np.where(is_zero, default, a / np.where(is_zero, 1.0, b))

    return result
```

**Edge Cases:**
- `div_safe(np.array([nan]), 1.0)` → `array([nan])` (preserve input NaN)
- `div_safe(np.array([inf]), np.array([inf]))` → `array([nan])` (inf/inf = nan)
- `div_safe(0.0, 0.0, default=None)` → `array([nan])` (0/0 = nan)

---

#### Other Safe Operations

```python
def sqrt_safe(x: ArrayLike, *, default: Optional[float | ArrayLike] = None) -> np.ndarray:
    """Safe element-wise square root (handles negative values)."""

def log_safe(
    x: ArrayLike,
    *,
    base: Optional[float] = None,
    default: Optional[float | ArrayLike] = None
) -> np.ndarray:
    """Safe element-wise logarithm (handles non-positive values)."""

def pow_safe(
    base: ArrayLike,
    exp: ArrayLike,
    *,
    default: Optional[float | ArrayLike] = None
) -> np.ndarray:
    """Safe element-wise power (handles overflow/underflow)."""

def sanitize(
    x: ArrayLike,
    *,
    nan_value: Optional[float] = 0.0,
    inf_value: Optional[float] = None,
    neginf_value: Optional[float] = None
) -> np.ndarray:
    """Replace NaN/Inf values in array.

    Examples:
        >>> x = np.array([1.0, np.nan, np.inf, -np.inf, 2.0])
        >>> sanitize(x, nan_value=0.0, inf_value=1e10, neginf_value=-1e10)
        array([1.0, 0.0, 1e10, -1e10, 2.0])
    """
```

---

### 2. Comparisons (`neon.numpy._compare`)

#### `near(a, b, *, rel_tol=1e-9, abs_tol=1e-9)`

Vectorized approximate equality.

**Signature:**
```python
def near(
    a: ArrayLike,
    b: ArrayLike,
    *,
    rel_tol: float = 1e-9,
    abs_tol: float = 1e-9
) -> np.ndarray:
    """Element-wise approximate equality check.

    Returns:
        Boolean array of same shape as broadcast(a, b)

    Examples:
        >>> a = np.array([0.1 + 0.2, 1.0, 2.0])
        >>> b = np.array([0.3, 1.0 + 1e-10, 2.1])
        >>> near(a, b)
        array([True, True, False])
    """
```

**Implementation:**
```python
def near(a, b, *, rel_tol=1e-9, abs_tol=1e-9):
    a = np.asarray(a)
    b = np.asarray(b)

    # Use np.isclose (built-in vectorized version)
    # But handle NaN differently (NaN != NaN in our semantics)
    return np.isclose(a, b, rtol=rel_tol, atol=abs_tol, equal_nan=False)
```

---

#### Other Comparisons

```python
def near_zero(x: ArrayLike, *, abs_tol: float = 1e-9) -> np.ndarray:
    """Element-wise near-zero check (returns bool array)."""

def all_near(a: ArrayLike, b: ArrayLike, *, rel_tol=1e-9, abs_tol=1e-9) -> bool:
    """Check if ALL elements are near (returns single bool)."""

def any_near(a: ArrayLike, b: ArrayLike, *, rel_tol=1e-9, abs_tol=1e-9) -> bool:
    """Check if ANY elements are near (returns single bool)."""

def count_near(a: ArrayLike, b: ArrayLike, *, rel_tol=1e-9, abs_tol=1e-9) -> int:
    """Count how many elements are near."""

def fraction_near(a: ArrayLike, b: ArrayLike, *, rel_tol=1e-9, abs_tol=1e-9) -> float:
    """Fraction of elements that are near (useful for metrics).

    Examples:
        >>> a = np.array([1.0, 2.0, 3.0, 4.0])
        >>> b = np.array([1.0, 2.1, 3.0, 4.1])
        >>> fraction_near(a, b, abs_tol=0.05)
        0.5  # 50% of elements are near
    """
```

---

### 3. Clamping (`neon.numpy._clamp`)

#### `to_zero(x, *, abs_tol=1e-9)`

Snap near-zero values to exactly zero.

**Signature:**
```python
def to_zero(x: ArrayLike, *, abs_tol: float = 1e-9) -> np.ndarray:
    """Replace near-zero values with exactly 0.0.

    Examples:
        >>> x = np.array([1e-15, 0.1, -1e-16, 1.0])
        >>> to_zero(x, abs_tol=1e-9)
        array([0.0, 0.1, 0.0, 1.0])
    """
```

**Implementation:**
```python
def to_zero(x, *, abs_tol=1e-9):
    x = np.asarray(x)
    return np.where(np.abs(x) <= abs_tol, 0.0, x)
```

---

#### Other Clamping

```python
def to_range(x: ArrayLike, lo: float, hi: float) -> np.ndarray:
    """Clamp values to [lo, hi] range."""
    # Use np.clip for efficiency
    return np.clip(x, lo, hi)

def to_int(x: ArrayLike, *, abs_tol: float = 1e-9) -> np.ndarray:
    """Snap to nearest integer if near it (returns float array)."""
```

---

## Performance Considerations

### Benchmarks (Target)

```python
import numpy as np
import neon.numpy as nnp

# Setup
a = np.random.randn(1_000_000)
b = np.random.randn(1_000_000)
b[b == 0] = 1e-10  # Avoid exact zeros

# Benchmark 1: Safe division
%timeit nnp.div_safe(a, b, default=0.0)
# Target: <1ms (similar to hand-written np.where)

# Benchmark 2: Near comparison
%timeit nnp.near(a, b)
# Target: <2ms (similar to np.isclose)

# Benchmark 3: Sanitize
x = a.copy()
x[::100] = np.nan
%timeit nnp.sanitize(x, nan_value=0.0)
# Target: <1ms
```

### Optimization Strategy

1. **Use NumPy primitives:** `np.where`, `np.clip`, `np.isclose` are C-optimized
2. **Avoid Python loops:** Everything must be vectorized
3. **Minimize copies:** Use views when possible
4. **Benchmark against baseline:** Must be within 2x of naive NumPy code

---

## Type Safety

### Type Hints

```python
from typing import Union, Optional
import numpy as np
from numpy.typing import ArrayLike, NDArray

def div_safe(
    a: ArrayLike,
    b: ArrayLike,
    *,
    default: Optional[Union[float, ArrayLike]] = None,
    zero_tol: float = 0.0
) -> NDArray[np.floating]:
    ...
```

### Runtime Validation

```python
def div_safe(a, b, *, default=None, zero_tol=0.0):
    # Convert to arrays (validates input)
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    # Validate tolerance
    if zero_tol < 0:
        raise ValueError(f"zero_tol must be non-negative, got {zero_tol}")

    # ... rest of implementation
```

---

## Testing Strategy

### 1. Unit Tests (`tests/test_numpy_safe.py`)

```python
import numpy as np
import pytest
from neon.numpy import div_safe

class TestDivSafe:
    def test_normal_division(self):
        a = np.array([6.0, 4.0])
        b = np.array([3.0, 2.0])
        result = div_safe(a, b)
        np.testing.assert_array_equal(result, [2.0, 2.0])

    def test_division_by_zero_with_default(self):
        a = np.array([1.0, 2.0])
        b = np.array([0.0, 2.0])
        result = div_safe(a, b, default=0.0)
        np.testing.assert_array_equal(result, [0.0, 1.0])

    def test_broadcasting(self):
        a = np.array([[1.0, 2.0], [3.0, 4.0]])
        b = np.array([2.0, 0.0])
        result = div_safe(a, b, default=0.0)
        expected = np.array([[0.5, 0.0], [1.5, 0.0]])
        np.testing.assert_array_almost_equal(result, expected)

    def test_scalar_inputs(self):
        result = div_safe(6.0, 3.0)
        assert result == 2.0
```

### 2. Property-Based Tests

```python
from hypothesis import given, assume
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays
import numpy as np
from neon.numpy import div_safe

@given(
    a=arrays(dtype=np.float64, shape=st.integers(1, 100)),
    b=arrays(dtype=np.float64, shape=st.integers(1, 100))
)
def test_div_safe_never_raises(a, b):
    """div_safe should never raise, even with zeros/nans/infs."""
    result = div_safe(a, b, default=0.0)
    assert result.shape == np.broadcast_shapes(a.shape, b.shape)
```

### 3. Performance Regression Tests

```python
import numpy as np
import pytest
from neon.numpy import div_safe

@pytest.mark.benchmark
def test_div_safe_performance(benchmark):
    a = np.random.randn(1_000_000)
    b = np.random.randn(1_000_000)

    def run():
        return div_safe(a, b, default=0.0)

    result = benchmark(run)
    # Should complete in <2ms on modern hardware
```

---

## Documentation

### Docstring Format

```python
def div_safe(a, b, *, default=None, zero_tol=0.0):
    """Safely divide arrays element-wise with zero handling.

    Performs vectorized division with configurable behavior for
    division by zero or near-zero values.

    Parameters
    ----------
    a : array_like
        Numerator. If not an ndarray, converted to float64 array.
    b : array_like
        Denominator. If not an ndarray, converted to float64 array.
    default : float or array_like, optional
        Value to use when b is zero/near-zero. If None, uses NaN.
    zero_tol : float, default=0.0
        Tolerance for considering b as zero. If zero_tol > 0,
        treats |b| <= zero_tol as zero.

    Returns
    -------
    ndarray
        Array of same shape as broadcast(a, b) containing division
        results with safe zero handling.

    See Also
    --------
    neon.safe.div : Scalar version
    numpy.divide : Unsafe division (raises on zero)

    Notes
    -----
    This function uses NumPy's broadcasting rules. The output shape
    is determined by np.broadcast_shapes(a.shape, b.shape).

    Examples
    --------
    Basic usage:

    >>> import numpy as np
    >>> from neon.numpy import div_safe
    >>> a = np.array([1.0, 2.0, 3.0])
    >>> b = np.array([2.0, 0.0, 4.0])
    >>> div_safe(a, b, default=0.0)
    array([0.5, 0.0, 0.75])

    Broadcasting:

    >>> a = np.array([[1, 2], [3, 4]])
    >>> b = np.array([2, 0])
    >>> div_safe(a, b, default=-1)
    array([[0.5, -1.0], [1.5, -1.0]])

    Near-zero tolerance:

    >>> div_safe(1.0, 1e-15, zero_tol=1e-10, default=0.0)
    0.0  # Treated as division by zero
    """
```

---

## Migration Path

### v1.0.0 (Current) - Scalar Only
```python
from neon import safe
result = safe.div(1.0, 0.0, default=0.0)  # Works
```

### v1.1.0 - Add NumPy Support (Non-Breaking)
```python
# Scalar API unchanged
from neon import safe
result = safe.div(1.0, 0.0, default=0.0)  # Still works

# New array API
import neon.numpy as nnp
result = nnp.div_safe(np.array([1, 2]), np.array([0, 2]), default=0.0)  # New!
```

### Naming Convention
- Scalar: `neon.safe.div()` (existing)
- Array: `neon.numpy.div_safe()` (new, uses `_safe` suffix for clarity)

**Rationale:** The `_safe` suffix makes it clear this is the "safe" version when used in NumPy-heavy code alongside `np.divide()`.

---

## Open Questions

### Q1: Should `default` support per-element defaults?

```python
# Should this work?
a = np.array([1, 2, 3])
b = np.array([0, 2, 0])
defaults = np.array([10, 20, 30])
result = div_safe(a, b, default=defaults)
# → array([10, 1, 30]) ?
```

**Answer:** Yes, support array defaults (allows advanced use cases).

### Q2: Should we return masked arrays when default=None?

```python
result = div_safe(a, b, default=None)
# Option A: Return regular array with NaN
# Option B: Return np.ma.MaskedArray
```

**Answer:** Return regular array with NaN (simpler, more compatible).

### Q3: How to handle mixed scalar/array inputs?

```python
# All these should work via broadcasting
div_safe(np.array([1, 2]), 2.0, default=0.0)  # array / scalar
div_safe(1.0, np.array([2, 0]), default=0.0)  # scalar / array
div_safe(1.0, 2.0, default=0.0)              # scalar / scalar
```

**Answer:** Use `np.asarray()` to handle all cases uniformly.

---

## Implementation Checklist

- [ ] Create `neon/numpy/` directory
- [ ] Implement `div_safe()` with full tests
- [ ] Implement `sqrt_safe()`, `log_safe()`, `pow_safe()`
- [ ] Implement `sanitize()`
- [ ] Implement `near()`, `near_zero()`, `all_near()`, `count_near()`
- [ ] Implement `to_zero()`, `to_range()`, `to_int()`
- [ ] Add type hints with `numpy.typing`
- [ ] Write comprehensive unit tests (>95% coverage)
- [ ] Write property-based tests with Hypothesis
- [ ] Add performance benchmarks
- [ ] Write user guide in README
- [ ] Update pyproject.toml with optional numpy dependency
- [ ] Create migration guide for v1.0 → v1.1

---

**Next Step:** Implement `neon.numpy.div_safe()` as proof of concept.
