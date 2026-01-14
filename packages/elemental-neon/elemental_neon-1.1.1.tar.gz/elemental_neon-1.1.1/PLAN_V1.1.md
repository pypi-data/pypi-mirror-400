# Neon v1.1.0 Implementation Plan

**Goal:** Add diagnostic tools and complete batch operation patterns.

**Timeline:** 15-20 hours total
**Release Date:** Target within 2 weeks

---

## Overview

v1.1.0 adds two focused enhancements:

1. **`neon.inspect`** - Float health diagnostics (NEW module)
2. **Batch operations** - Complete `*_many()` pattern across all modules (EXTEND existing)

**Principles:**
- ✅ Zero new dependencies
- ✅ Works with plain Python iterables
- ✅ <300 lines of new code
- ✅ Maintains Neon's essence (educational, correct, simple)

---

## Feature 1: Float Inspection (`neon/inspect.py`)

### API Design

```python
from neon import inspect as ni

# Analyze single float - decompose IEEE 754 structure
info = ni.analyze_float(3.14159)
print(info)
# FloatInfo(
#   value=3.14159,
#   sign='+',
#   exponent=1,
#   mantissa_hex='0x921f9f01b866e',
#   category='normal',
#   ulp=4.440892098500626e-16,
#   next_float=3.1415900000000003,
#   prev_float=3.1415899999999997
# )

# Analyze collection - health report
values = [1e-320, 1.0, float('nan'), 1e308]
report = ni.analyze_many(values)
print(report)
# HealthReport(
#   count=4,
#   categories={'denormal': 1, 'normal': 1, 'nan': 1, 'overflow': 1},
#   denormal_count=1,
#   denormal_percent=25.0,
#   nan_count=1,
#   inf_count=0,
#   zero_count=0,
#   normal_count=1,
#   ulp_median=2.220446049250313e-16,
#   ulp_max=inf,
#   precision_risk='high'  # Due to denormals + NaN
# )

# Quick categorization
ni.categorize(1e-400)  # → 'denormal'
ni.categorize(1.0)     # → 'normal'
ni.categorize(float('nan'))  # → 'nan'
ni.categorize(float('inf'))  # → 'inf'
ni.categorize(0.0)     # → 'zero'

# Precision info
prec = ni.precision_info(1.0)
print(prec)
# PrecisionInfo(
#   value=1.0,
#   ulp=2.220446049250313e-16,
#   significant_bits=53,
#   decimal_precision=15,
#   safe_for_fp16=True,
#   safe_for_bfloat16=True
# )
```

### Implementation Details

**File:** `src/neon/inspect.py`

**Dependencies:** `math`, `struct` (already used in ulp.py), `dataclasses`

**Classes:**
```python
from dataclasses import dataclass
from typing import Literal

Category = Literal['zero', 'denormal', 'normal', 'inf', 'nan']

@dataclass
class FloatInfo:
    value: float
    sign: str  # '+' or '-'
    exponent: int
    mantissa_hex: str
    category: Category
    ulp: float
    next_float: float
    prev_float: float

@dataclass
class HealthReport:
    count: int
    categories: dict[Category, int]
    denormal_count: int
    denormal_percent: float
    nan_count: int
    inf_count: int
    zero_count: int
    normal_count: int
    ulp_median: float
    ulp_max: float
    precision_risk: Literal['low', 'medium', 'high']

@dataclass
class PrecisionInfo:
    value: float
    ulp: float
    significant_bits: int
    decimal_precision: int
    safe_for_fp16: bool
    safe_for_bfloat16: bool
```

**Functions:**
```python
def categorize(x: float) -> Category:
    """Categorize a float into one of: zero, denormal, normal, inf, nan."""

def analyze_float(x: float) -> FloatInfo:
    """Decompose IEEE 754 structure and analyze precision."""

def analyze_many(values: Iterable[float]) -> HealthReport:
    """Analyze collection of floats for numerical health."""

def precision_info(x: float) -> PrecisionInfo:
    """Get precision information for a float."""
```

### Tests (`tests/test_inspect.py`)

```python
import math
import pytest
from neon import inspect as ni

class TestCategorize:
    def test_zero(self):
        assert ni.categorize(0.0) == 'zero'
        assert ni.categorize(-0.0) == 'zero'

    def test_normal(self):
        assert ni.categorize(1.0) == 'normal'
        assert ni.categorize(-42.5) == 'normal'

    def test_denormal(self):
        # Smallest normal is ~2.2e-308, denormals are smaller
        assert ni.categorize(1e-320) == 'denormal'

    def test_infinity(self):
        assert ni.categorize(float('inf')) == 'inf'
        assert ni.categorize(float('-inf')) == 'inf'

    def test_nan(self):
        assert ni.categorize(float('nan')) == 'nan'

class TestAnalyzeFloat:
    def test_positive_normal(self):
        info = ni.analyze_float(1.0)
        assert info.value == 1.0
        assert info.sign == '+'
        assert info.category == 'normal'
        assert info.ulp > 0

    def test_negative(self):
        info = ni.analyze_float(-3.14)
        assert info.sign == '-'

    def test_zero(self):
        info = ni.analyze_float(0.0)
        assert info.category == 'zero'

class TestAnalyzeMany:
    def test_mixed_values(self):
        values = [1.0, 1e-400, float('nan'), 2.0]
        report = ni.analyze_many(values)

        assert report.count == 4
        assert report.normal_count == 2  # 1.0, 2.0
        assert report.denormal_count == 1  # 1e-400
        assert report.nan_count == 1

    def test_empty(self):
        report = ni.analyze_many([])
        assert report.count == 0

    def test_precision_risk_high(self):
        # Mix of denormals and NaN = high risk
        values = [1e-400, float('nan')]
        report = ni.analyze_many(values)
        assert report.precision_risk == 'high'

    def test_precision_risk_low(self):
        # All normal values = low risk
        values = [1.0, 2.0, 3.0]
        report = ni.analyze_many(values)
        assert report.precision_risk == 'low'
```

---

## Feature 2: Batch Operations

### Extend Existing Modules

#### `neon/safe.py` additions

```python
def div_many(
    a_values: Sequence[float],
    b_values: Sequence[float],
    *,
    default: Optional[float] = None,
    zero_tol: float = 0.0
) -> list[Optional[float]]:
    """Batch safe division.

    Examples:
        >>> div_many([1, 2, 3], [2, 0, 4], default=0.0)
        [0.5, 0.0, 0.75]
    """
    # Broadcast if one is scalar
    if not isinstance(a_values, Sequence):
        a_values = [a_values] * len(b_values)
    if not isinstance(b_values, Sequence):
        b_values = [b_values] * len(a_values)

    return [div(a, b, default=default, zero_tol=zero_tol)
            for a, b in zip(a_values, b_values)]

def sqrt_many(
    values: Sequence[float],
    *,
    default: Optional[float] = None
) -> list[Optional[float]]:
    """Batch safe square root.

    Examples:
        >>> sqrt_many([4, -1, 9], default=0.0)
        [2.0, 0.0, 3.0]
    """
    return [sqrt(x, default=default) for x in values]

def log_many(
    values: Sequence[float],
    *,
    base: Optional[float] = None,
    default: Optional[float] = None
) -> list[Optional[float]]:
    """Batch safe logarithm."""
    return [log(x, base=base, default=default) for x in values]

def pow_many(
    bases: Sequence[float],
    exps: Sequence[float],
    *,
    default: Optional[float] = None
) -> list[Optional[float]]:
    """Batch safe power."""
    return [pow(b, e, default=default) for b, e in zip(bases, exps)]
```

**Tests:**
```python
class TestDivMany:
    def test_basic(self):
        result = safe.div_many([6, 4], [3, 2])
        assert result == [2.0, 2.0]

    def test_with_zeros(self):
        result = safe.div_many([1, 2, 3], [0, 2, 0], default=-1)
        assert result == [-1, 1.0, -1]

    def test_broadcasting_scalar_denominator(self):
        result = safe.div_many([6, 4], 2)
        assert result == [3.0, 2.0]
```

#### `neon/compare.py` additions

```python
def near_zero_many(
    values: Sequence[float],
    *,
    abs_tol: float = 1e-9
) -> list[bool]:
    """Batch near-zero check.

    Examples:
        >>> near_zero_many([1e-15, 0.1, -1e-16])
        [True, False, True]
    """
    return [near_zero(x, abs_tol=abs_tol) for x in values]

def is_integer_many(
    values: Sequence[float],
    *,
    abs_tol: float = 1e-9
) -> list[bool]:
    """Batch integer check.

    Examples:
        >>> is_integer_many([3.0, 3.1, 2.9999999999])
        [True, False, True]
    """
    return [is_integer(x, abs_tol=abs_tol) for x in values]
```

#### `neon/clamp.py` additions

```python
def to_int_many(
    values: Sequence[float],
    *,
    abs_tol: float = 1e-9
) -> list[float]:
    """Batch snap to nearest integer.

    Examples:
        >>> to_int_many([2.9999999, 3.1, 5.0])
        [3.0, 3.1, 5.0]
    """
    return [to_int(x, abs_tol=abs_tol) for x in values]

def to_range_many(
    values: Sequence[float],
    lo: float,
    hi: float
) -> list[float]:
    """Batch clamp to range.

    Examples:
        >>> to_range_many([5, -5, 15], 0, 10)
        [5, 0, 10]
    """
    return [to_range(x, lo, hi) for x in values]
```

#### `neon/ulp.py` additions

```python
def of_many(values: Sequence[float]) -> list[float]:
    """Get ULP for each value.

    Examples:
        >>> ulps = of_many([1.0, 2.0, 0.0])
        >>> ulps[0] > 0  # 1.0 has a ULP
        True

    Raises:
        InvalidValueError: If any value is NaN
    """
    return [of(x) for x in values]

def diff_many(
    a_values: Sequence[float],
    b_values: Sequence[float]
) -> list[int]:
    """ULP distances between pairs.

    Examples:
        >>> diff_many([1.0, 2.0], [1.0001, 2.0001])
        [450, 901]

    Raises:
        InvalidValueError: If any value is NaN or inf
    """
    return [diff(a, b) for a, b in zip(a_values, b_values)]

def within_many(
    a_values: Sequence[float],
    b_values: Sequence[float],
    *,
    max_ulps: int = 4
) -> list[bool]:
    """Check if pairs are within max_ulps.

    Examples:
        >>> within_many([1.0, 2.0], [1.0 + 1e-15, 2.1])
        [True, False]
    """
    return [within(a, b, max_ulps=max_ulps) for a, b in zip(a_values, b_values)]
```

---

## Update `__init__.py`

Export new functions:

```python
# Add to imports
from . import inspect
from .safe import div_many, sqrt_many, log_many, pow_many
from .compare import near_zero_many, is_integer_many
from .clamp import to_int_many, to_range_many
from .ulp import of_many, diff_many, within_many

# Add to __all__
__all__ = [
    # ... existing exports ...

    # New in v1.1.0
    "inspect",
    "div_many",
    "sqrt_many",
    "log_many",
    "pow_many",
    "near_zero_many",
    "is_integer_many",
    "to_int_many",
    "to_range_many",
    "of_many",
    "diff_many",
    "within_many",
]
```

---

## Documentation Updates

### README.md additions

Add new section after "API Reference":

```markdown
### `neon.inspect` (v1.1+)

Float health diagnostics and IEEE 754 structure analysis.

| Function | Description |
|----------|-------------|
| `categorize(x)` | Categorize float (zero, denormal, normal, inf, nan) |
| `analyze_float(x)` | Decompose IEEE 754 structure |
| `analyze_many(values)` | Health report for collection |
| `precision_info(x)` | Precision statistics |

```python
from neon import inspect as ni

# Analyze single float
info = ni.analyze_float(3.14)
print(f"ULP: {info.ulp}, Category: {info.category}")

# Health check for collection
report = ni.analyze_many(my_array)
if report.denormal_percent > 10:
    print("Warning: High denormal count - precision loss likely")
```

### Batch Operations

All modules now support batch operations via `*_many()` functions:

```python
from neon import safe, compare, clamp, ulp

# Batch safe division
safe.div_many([1, 2, 3], [0, 2, 0], default=0.0)  # [0.0, 1.0, 0.0]

# Batch comparisons
compare.near_zero_many([1e-15, 0.1])  # [True, False]

# Batch clamping
clamp.to_range_many([5, -5, 15], 0, 10)  # [5, 0, 10]

# Batch ULP operations
ulp.diff_many([1.0, 2.0], [1.001, 2.001])  # ULP distances
```
```

---

## Testing Strategy

### Coverage Target: 95%+

1. **Unit tests** - Test each function individually
2. **Edge cases** - Test with NaN, inf, denormals, zeros
3. **Property tests** - Use Hypothesis for `*_many()` functions
4. **Integration tests** - Test `inspect` with real-world data

### Test Files

- `tests/test_inspect.py` - New file (~100 lines)
- `tests/test_safe.py` - Add batch operation tests
- `tests/test_compare.py` - Add batch operation tests
- `tests/test_clamp.py` - Add batch operation tests
- `tests/test_ulp.py` - Add batch operation tests

---

## Performance Considerations

**Batch operations are NOT optimized for performance** - they're convenience wrappers.

If users need performance, they should use NumPy:
```python
# Neon: Convenient but slow for large arrays
result = safe.div_many(a_list, b_list)  # Pure Python loop

# NumPy: Fast for large arrays
result = np.where(b != 0, a / b, 0.0)  # Vectorized
```

**This is intentional** - Neon stays dependency-free and simple.

---

## Migration Guide

v1.0.0 code works unchanged:
```python
# All v1.0.0 code continues to work
from neon import safe
safe.div(1, 0, default=0.0)  # ✅ Still works
```

New in v1.1.0:
```python
# Optional: Use new batch operations
from neon import safe
safe.div_many([1, 2], [0, 2], default=0.0)  # ✅ New!

# Optional: Use new inspection tools
from neon import inspect as ni
ni.analyze_many([1.0, 1e-400])  # ✅ New!
```

---

## Release Checklist

- [ ] Implement `neon/inspect.py` (~150 lines)
- [ ] Add batch operations to `safe.py` (~40 lines)
- [ ] Add batch operations to `compare.py` (~30 lines)
- [ ] Add batch operations to `clamp.py` (~30 lines)
- [ ] Add batch operations to `ulp.py` (~40 lines)
- [ ] Update `__init__.py` exports
- [ ] Write tests for `inspect` module (95%+ coverage)
- [ ] Write tests for batch operations (95%+ coverage)
- [ ] Update README.md with new sections
- [ ] Update CHANGELOG.md
- [ ] Bump version to 1.1.0
- [ ] Run full test suite (should be ~150+ tests)
- [ ] Build package: `python -m build`
- [ ] Check with twine: `twine check dist/*`
- [ ] Upload to PyPI: `twine upload dist/elemental_neon-1.1.0*`

---

**Estimated Timeline:**
- Implementation: 10-12 hours
- Testing: 4-5 hours
- Documentation: 2-3 hours
- **Total: 16-20 hours**

**Target Ship Date:** Within 2 weeks of starting
