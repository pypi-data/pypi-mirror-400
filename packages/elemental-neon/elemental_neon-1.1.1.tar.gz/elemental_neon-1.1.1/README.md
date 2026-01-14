# Neon

Near-equality and tolerance arithmetic for floating-point numbers.

[![PyPI version](https://img.shields.io/pypi/v/elemental-neon.svg)](https://pypi.org/project/elemental-neon/)
[![Python versions](https://img.shields.io/pypi/pyversions/elemental-neon.svg)](https://pypi.org/project/elemental-neon/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/marszdf/neon/blob/main/neon_demo.ipynb)

## The Problem

Floating-point arithmetic is broken by design. Everyone ships these bugs:

```python
# Bug: floating-point comparison
>>> 0.1 + 0.2 == 0.3
False  # Wrong! Should be True.

# Bug: near-zero comparison
>>> 1e-16 == 0
False  # Maybe should be "close enough"?

# Bug: unsafe division
>>> x / y
ZeroDivisionError  # What if y is zero or near-zero?

# Bug: naive tolerance breaks for large numbers
>>> abs(1000000.0 - 1000000.1) < 0.0001
True  # Wrong! This is a 0.00001% difference, not "near equal"
```

Neon handles these correctly:

```python
from neon import compare, safe, clamp, ulp, inspect

compare.near(0.1 + 0.2, 0.3)           # → True
compare.near_zero(1e-16)               # → True
safe.div(1, 0, default=0.0)            # → 0.0
clamp.to_zero(1e-15)                   # → 0.0
ulp.diff(1.0, ulp.next(1.0))           # → 1 (one ULP apart)
inspect.check(float('nan'))            # → "Value is NaN - invalid calculation result" ✨ v1.1.0
```

## Installation

```bash
pip install elemental-neon
```

**Zero dependencies** — uses only the Python standard library.

## When to Use Neon

**Use neon when:**
- You need correct floating-point comparisons (within tolerance)
- You're debugging NaN/Inf issues in production or validating FP8/FP16 quantization ✨ v1.1.0
- You're doing safe division that handles zero gracefully
- You want to snap near-zero values to exactly zero
- You need ULP-based comparisons for precise float arithmetic
- You're building numerical algorithms, financial calculations, or scientific computing
- You want improved summation precision with math.fsum()
- You need to process batches of floats with safe operations ✨ v1.1.0

**Don't use neon when:**
- You need arbitrary-precision arithmetic — use `decimal.Decimal`
- You need symbolic math — use `sympy`
- You need interval arithmetic — use `mpmath`
- Standard `==` comparison is actually what you want (rare for floats)

## API Reference

### `neon.inspect` ✨ New in v1.1.0

Production debugging tools for floating-point issues and low-precision dtype validation.

| Function | Description |
|----------|-------------|
| `check(x)` | Quick health check, returns warning or None |
| `check_many(values)` | Batch health summary with risk assessment |
| `compare_debug(a, b)` | Explains why floats differ + recommends fix |
| `div_debug(a, b)` | Debugs division issues |
| `analyze(values)` | Comprehensive analysis with recommendations |
| `precision_loss(got, expected)` | Detects precision loss |
| `safe_for_dtype(x, target)` | Check if value safe for target dtype |
| `analyze_for_dtype(values, target)` | Batch analysis for dtype conversion |
| `compare_dtypes(values, targets)` | Compare safety across multiple dtypes |

**Supported dtypes:** `fp32`, `fp16`, `bf16`, `fp8_e4m3`, `fp8_e5m2`

```python
from neon import inspect as ni

# Quick health check
if issue := ni.check(result):
    print(f"Problem: {issue}")
    # → "Value is NaN - invalid calculation result"

# Debug why floats differ
ni.compare_debug(0.1 + 0.2, 0.3)
# → "Values differ by 5.551115123e-17 (1 ULP). Use neon.compare.near() for tolerance comparison."

# Debug division issues
ni.div_debug(1.0, 0.0)
# → "Division by zero detected. Use neon.safe.div(a, b, default=...) to handle gracefully."

# Analyze batch of values
report = ni.analyze([1.0, 5e-324, float('nan'), 2.0])
print(report)
# → Analysis of 4 values:
#   Normal: 2 (50.0%)
#   Denormal: 1 (25.0%)
#   NaN: 1 (25.0%)
#   Precision Risk: HIGH

# Validate FP8 quantization before converting model
weights = model.get_weights().flatten().tolist()
report = ni.analyze_for_dtype(weights, target='fp8_e4m3')
if report.overflow > 0:
    print(f"WARNING: {report.recommendation}")
    # → "WARNING: 15% of values overflow FP8 range (max ±448). Consider clipping."

# Compare multiple dtypes
comparison = ni.compare_dtypes(activations, targets=['fp16', 'bf16', 'fp8_e4m3'])
print(comparison.recommendation)
# → "Use BF16 for best balance (0% overflow, LOW precision risk)"
```

**Use cases:**
- Debug NaN/Inf in production calculations
- Understand precision loss in numerical algorithms
- Validate model weights before FP8/FP16 quantization
- Post-mortem analysis of training failures

### `neon.compare`

Comparison functions for approximate equality.

| Function | Description |
|----------|-------------|
| `near(a, b, *, rel_tol=1e-9, abs_tol=1e-9)` | True if a and b are approximately equal |
| `near_zero(x, *, abs_tol=1e-9)` | True if x is approximately zero |
| `less_or_near(a, b, *, rel_tol, abs_tol)` | True if a < b or a ≈ b |
| `greater_or_near(a, b, *, rel_tol, abs_tol)` | True if a > b or a ≈ b |
| `compare(a, b, *, rel_tol, abs_tol)` | Returns -1, 0, or 1 (spaceship operator) |
| `all_near(pairs, *, rel_tol, abs_tol)` | True if all pairs are near |
| `is_integer(x, *, abs_tol=1e-9)` | True if x is near an integer |
| `near_many(pairs, *, rel_tol, abs_tol)` | Batch comparison |
| `near_zero_many(values, *, abs_tol)` | Batch near-zero check ✨ v1.1.0 |
| `is_integer_many(values, *, abs_tol)` | Batch integer check ✨ v1.1.0 |

```python
from neon import compare

compare.near(0.1 + 0.2, 0.3)           # → True
compare.near(1.0, 1.001, rel_tol=1e-2) # → True
compare.near(1.0, 1.001, rel_tol=1e-4) # → False

compare.near_zero(1e-15)               # → True
compare.near_zero(1e-5)                # → False

compare.is_integer(3.0000000001)       # → True
compare.is_integer(3.1)                # → False

compare.compare(1.0, 1.0 + 1e-12)      # → 0 (near)
compare.compare(1.0, 2.0)              # → -1 (less)
compare.compare(2.0, 1.0)              # → 1 (greater)

# Batch operations
pairs = [(0.1 + 0.2, 0.3), (1.0, 2.0)]
compare.near_many(pairs)               # → [True, False]
compare.all_near([(1.0, 1.0), (2.0, 2.0)]) # → True
```

**Special value semantics:**
- `near(nan, nan)` → `False` (NaN is not near anything, including itself)
- `near(inf, inf)` → `True` (same infinity)
- `near(-inf, inf)` → `False`
- `near(inf, 1e308)` → `False` (infinity is not near any finite number)
- `near(0.0, -0.0)` → `True`

### `neon.clamp`

Clamping and snapping functions.

| Function | Description |
|----------|-------------|
| `to_zero(x, *, abs_tol=1e-9)` | Snap to 0.0 if near zero |
| `to_int(x, *, abs_tol=1e-9)` | Snap to nearest int if near it |
| `to_value(x, target, *, rel_tol, abs_tol)` | Snap to target if near it |
| `to_range(x, lo, hi)` | Clamp x to [lo, hi] |
| `to_values(x, targets, *, rel_tol, abs_tol)` | Snap to nearest target |
| `to_zero_many(values, *, abs_tol)` | Batch snap to zero |
| `to_int_many(values, *, abs_tol)` | Batch snap to integer ✨ v1.1.0 |
| `to_range_many(values, lo, hi)` | Batch clamp to range ✨ v1.1.0 |

```python
from neon import clamp

clamp.to_zero(1e-15)           # → 0.0
clamp.to_zero(0.1)             # → 0.1

clamp.to_int(2.9999999999)     # → 3.0 (float, not int)
clamp.to_int(2.5)              # → 2.5

clamp.to_value(0.333333333, 1/3)  # → 0.3333333333333333 (exact 1/3)

clamp.to_range(5, 0, 10)       # → 5
clamp.to_range(-5, 0, 10)      # → 0
clamp.to_range(15, 0, 10)      # → 10

clamp.to_values(0.499999999, [0.0, 0.5, 1.0]) # → 0.5
clamp.to_values(0.3, [0.0, 0.5, 1.0])         # → 0.3 (not near any)
```

### `neon.safe`

Safe arithmetic with graceful edge case handling.

| Function | Description |
|----------|-------------|
| `div(a, b, *, default=None, zero_tol=0.0)` | Safe division |
| `div_or_zero(a, b, *, zero_tol=0.0)` | Safe division, returns 0.0 on zero |
| `div_or_inf(a, b, *, zero_tol=0.0)` | Safe division, returns ±inf on zero |
| `mod(a, b, *, default=None, zero_tol=0.0)` | Safe modulo |
| `sqrt(x, *, default=None)` | Safe sqrt, handles negative |
| `log(x, *, base=None, default=None)` | Safe log, handles non-positive |
| `pow(base, exp, *, default=None)` | Safe power, handles edge cases |
| `sum_exact(values)` | Precise summation using math.fsum() |
| `mean_exact(values)` | Mean using math.fsum() |
| `div_many(a_values, b_values, *, default, zero_tol)` | Batch safe division ✨ v1.1.0 |
| `sqrt_many(values, *, default)` | Batch safe sqrt ✨ v1.1.0 |
| `log_many(values, *, base, default)` | Batch safe log ✨ v1.1.0 |
| `pow_many(bases, exps, *, default)` | Batch safe power ✨ v1.1.0 |

```python
from neon import safe

safe.div(6, 3)                 # → 2.0
safe.div(1, 0)                 # → None
safe.div(1, 0, default=0.0)    # → 0.0

safe.div_or_zero(1, 0)         # → 0.0
safe.div_or_inf(1, 0)          # → inf
safe.div_or_inf(-1, 0)         # → -inf

safe.div(1, 1e-15, zero_tol=1e-10)  # → None (b is "near zero")

safe.sqrt(4)                   # → 2.0
safe.sqrt(-1)                  # → None
safe.sqrt(-1, default=0.0)     # → 0.0

safe.log(0)                    # → None
safe.log(100, base=10)         # → 2.0

# Kahan summation for precision
values = [1e16, 1.0, -1e16]
sum(values)                    # → 0.0 (wrong! lost precision)
safe.sum_exact(values)         # → 1.0 (correct)

safe.sum_exact([0.1] * 10)     # → 1.0 (precise)
```

### `neon.ulp`

ULP (Unit in the Last Place) operations — the distance between adjacent floats.

| Function | Description |
|----------|-------------|
| `of(x)` | Returns the ULP of x |
| `diff(a, b)` | Distance in ULPs between a and b |
| `within(a, b, *, max_ulps=4)` | True if within max_ulps |
| `next(x)` | Next representable float above x |
| `prev(x)` | Next representable float below x |
| `add(x, n)` | Move n ULPs from x |
| `of_many(values)` | Batch ULP calculation ✨ v1.1.0 |
| `diff_many(a_values, b_values)` | Batch ULP distance ✨ v1.1.0 |
| `within_many(a_values, b_values, *, max_ulps)` | Batch ULP comparison ✨ v1.1.0 |

```python
from neon import ulp

ulp.of(1.0)                    # → 2.220446049250313e-16
ulp.of(1e10)                   # → 1.9073486328125e-06
ulp.of(0.0)                    # → 5e-324 (smallest denormal)

ulp.diff(1.0, 1.0 + 2.2e-16)   # → 1 (one ULP)
ulp.within(1.0, 1.0 + 1e-15)   # → True (within 4 ULPs)
ulp.within(1.0, 1.0001)        # → False

ulp.next(1.0)                  # → 1.0000000000000002
ulp.prev(1.0)                  # → 0.9999999999999999
ulp.add(1.0, 10)               # → 1.0 + 10 ULPs

# Round-trip
ulp.next(ulp.prev(1.0)) == 1.0 # → True
```

### Exceptions

Neon provides a hierarchy of exceptions for precise error handling:

```python
from neon import (
    NeonError,           # Base class for all neon errors
    InvalidValueError,   # NaN or invalid input
    EmptyInputError,     # Empty input where not allowed
)

# Catch specific errors
try:
    ulp.of(float('nan'))
except InvalidValueError as e:
    print(f"Invalid: {e.value}")  # → Invalid: nan

# Or catch all neon errors
try:
    safe.sum_exact([])
except NeonError:
    print("Neon operation failed")
```

## Cookbook

### Validate user input with tolerance

```python
from neon import compare

def validate_percentage(value: float) -> bool:
    """Check if value is approximately 0-100."""
    return compare.less_or_near(0, value) and compare.less_or_near(value, 100)

validate_percentage(99.9999999999)  # → True
validate_percentage(100.0000000001) # → True
validate_percentage(100.1)          # → False
```

### Clean up near-zero values in data

```python
from neon import clamp

# Remove floating-point noise from calculations
data = [0.0, 1e-16, 0.5, -1e-15, 1.0]
cleaned = clamp.to_zero_many(data)
# → [0.0, 0.0, 0.5, 0.0, 1.0]
```

### Safe division in financial calculations

```python
from neon import safe

def calculate_roi(profit: float, investment: float) -> float | None:
    """Calculate return on investment, handling zero investment."""
    return safe.div(profit, investment, default=None)

calculate_roi(1000, 5000)  # → 0.2 (20% ROI)
calculate_roi(1000, 0)     # → None (can't divide by zero)
```

### Snap to grid values in UI

```python
from neon import clamp

def snap_to_grid(x: float, grid_values: list[float]) -> float:
    """Snap x to nearest grid line if close enough."""
    return clamp.to_values(x, grid_values, rel_tol=0.01)

snap_to_grid(0.505, [0.0, 0.5, 1.0])  # → 0.5 (snapped)
snap_to_grid(0.6, [0.0, 0.5, 1.0])    # → 0.6 (not near any grid)
```

### Precise summation for accounting

```python
from neon import safe

# Adding many small currency amounts
transactions = [0.01, 0.01, 0.01] * 100  # 300 pennies

# Naive sum loses precision
naive_total = sum(transactions)  # → 2.9999999999999982 (wrong!)

# Kahan summation preserves it
exact_total = safe.sum_exact(transactions)  # → 3.0 (correct)
```

### Check if floats are "close enough" with ULPs

```python
from neon import ulp

# Sometimes you need ULP-level precision
a = 1.0
b = ulp.add(a, 2)  # Exactly 2 ULPs away

ulp.within(a, b, max_ulps=4)  # → True
ulp.within(a, b, max_ulps=1)  # → False
```

## Why Neon?

Floating-point comparison is hard. Everyone gets it wrong:

```python
# The bug everyone ships
>>> 0.1 + 0.2 == 0.3
False  # Wrong! They're "close enough"

>>> 1e-16 == 0
False  # Maybe should be True?

>>> abs(a - b) < 0.0001
# Breaks for large numbers! 1000000 vs 1000000.1 would be "near"
```

### What Neon does differently

- **Zero dependencies** — stdlib only
- **Pure functions** — no state, easy to test
- **Explicit tolerances** — no magic defaults
- **IEEE 754 aware** — proper NaN, inf, denormal handling
- **Fail loudly** — raises exceptions for invalid inputs
- **math.fsum()** — improved precision for sums using Python's C implementation
- **ULP operations** — direct access to float representation

### Math Model

Neon uses **relative and absolute tolerance** for comparisons, following the same algorithm as Python's `math.isclose()`:

```
abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
```

- **Relative tolerance** (`rel_tol`): Scales with magnitude (good for large numbers)
- **Absolute tolerance** (`abs_tol`): Fixed threshold (good for near-zero)

For ULP operations, Neon uses `math.nextafter()` (Python 3.9+) to manipulate the actual float representation.

For summation, Neon uses **math.fsum()** (Python's C-optimized compensated summation) to reduce floating-point error accumulation.

### Use Cases

- Floating-point comparisons with tolerance
- Safe division and arithmetic
- Cleaning near-zero values from data
- Snapping values to targets (UI grids, rounding)
- ULP-based precision testing
- Improved summation precision

## Performance

Neon is designed for low-latency float operations (benchmarked on Python 3.12, M1 Mac):

- **`compare.near()`**: ~0.15µs (~6.7M ops/sec)
- **`clamp.to_zero()`**: ~0.12µs (~8.3M ops/sec)
- **`safe.div()`**: ~0.18µs (~5.6M ops/sec)
- **`ulp.of()`**: ~0.25µs (~4.0M ops/sec)

Batch operations (`*_many()` functions) provide ~100x overhead reduction for lists of 100+ values.

**Not optimized for:** Vectorized operations on millions of floats. For that, use NumPy.

## Numerical Precision

Neon uses standard Python `float` (IEEE 754 double precision):

- **Precision:** ~15-17 significant decimal digits
- **Range:** ~±1.8e308
- **Smallest positive:** ~5e-324 (denormal)

**Edge cases:**
- `NaN` and `Infinity` inputs are handled explicitly
- ULP operations work correctly near zero (denormals)
- math.fsum() reduces but doesn't eliminate all rounding errors
- Tolerances default to `rel_tol=1e-9, abs_tol=1e-9` (better than math.isclose's abs_tol=0.0)

**Not suitable for:** Applications requiring arbitrary precision or guaranteed decimal accuracy (use `decimal.Decimal`).

## What Neon Does NOT Do

To set clear expectations:

- ❌ **Arbitrary precision** — use `decimal.Decimal` or `mpmath`
- ❌ **Symbolic math** — use `sympy`
- ❌ **Interval arithmetic** — use `mpmath.iv`
- ❌ **Fast vectorized operations** — use NumPy
- ❌ **Complex numbers** — use Python's `complex` or NumPy
- ❌ **Unit handling** — use `pint` or `astropy.units`

Neon handles **tolerance arithmetic** for floats. For other numerical needs, use specialized libraries.

## License

MIT

