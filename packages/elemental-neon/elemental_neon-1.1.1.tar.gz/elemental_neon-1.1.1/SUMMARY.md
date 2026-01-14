# Neon - Development Summary

## Overview
**elemental-neon** is a zero-dependency Python library for near-equality and tolerance arithmetic for floating-point numbers.

## Project Structure
```
neon/
├── src/neon/               # Source code
│   ├── __init__.py         # Package entry point
│   ├── compare.py          # Approximate equality comparisons
│   ├── clamp.py            # Value snapping and clamping
│   ├── safe.py             # Safe arithmetic operations
│   ├── ulp.py              # ULP-based operations
│   ├── exceptions.py       # Exception hierarchy
│   └── _validation.py      # Internal validation utilities
├── tests/                  # Test suite
│   ├── test_compare.py     # 48 tests
│   ├── test_clamp.py       # 21 tests
│   ├── test_safe.py        # 15 tests
│   └── test_ulp.py         # 16 tests
├── README.md               # Documentation
├── CHANGELOG.md            # Version history
├── LICENSE                 # MIT License
├── pyproject.toml          # Project configuration
└── .gitignore              # Git ignore patterns
```

## Test Coverage
- **Total Tests**: 92 (all passing)
- **Coverage**: 91% (exceeds 90% requirement)
- **Modules**:
  - compare.py: 100%
  - clamp.py: 94%
  - safe.py: 96%
  - ulp.py: 94%
  - exceptions.py: 100%

## Key Features

### 1. `neon.compare` - Approximate Equality
- `near()` - Check if floats are approximately equal
- `near_zero()` - Check if near zero
- `is_integer()` - Check if near an integer
- `compare()` - Spaceship operator with tolerance
- Batch operations: `all_near()`, `near_many()`

### 2. `neon.clamp` - Value Snapping
- `to_zero()` - Snap near-zero to exactly zero
- `to_int()` - Snap to nearest integer
- `to_value()` - Snap to target value
- `to_range()` - Clamp to range
- `to_values()` - Snap to nearest from list

### 3. `neon.safe` - Safe Arithmetic
- `div()` - Safe division with default
- `div_or_zero()` - Returns 0 on division by zero
- `div_or_inf()` - Returns ±inf on division by zero
- `sqrt()`, `log()`, `pow()`, `mod()` - Safe math ops
- `sum_exact()`, `mean_exact()` - Kahan summation

### 4. `neon.ulp` - ULP Operations
- `of()` - Get ULP of a float
- `diff()` - ULP distance between floats
- `near()` - Check if within N ULPs
- `next()`, `prev()` - Adjacent floats
- `add()` - Move N ULPs

## Implementation Details

### Python Version
- Requires Python 3.9+ (uses `math.nextafter()`)
- Uses `typing.Union` and `typing.Optional` for 3.9 compatibility
- No use of `|` union syntax to maintain compatibility

### Dependencies
- **Zero dependencies** - stdlib only
- `math` module for core operations
- `typing` for type hints

### Design Principles
1. Pure functions - no state
2. Explicit tolerances - no magic defaults
3. IEEE 754 aware - proper NaN, inf handling
4. Fail loudly - raise exceptions for invalid inputs
5. Type hints throughout

## Next Steps (Not Implemented)
- [ ] Publish to PyPI
- [ ] Add CI/CD workflow
- [ ] Create demonstration Jupyter notebook
- [ ] Add CONTRIBUTING.md guidelines
- [ ] Add benchmark suite
- [ ] Property-based testing with Hypothesis

## Quick Start
```python
from neon import compare, clamp, safe, ulp

# Compare floats with tolerance
compare.near(0.1 + 0.2, 0.3)  # → True

# Snap near-zero values
clamp.to_zero(1e-15)  # → 0.0

# Safe division
safe.div(1, 0, default=0.0)  # → 0.0

# ULP operations
ulp.of(1.0)  # → 2.220446049250313e-16
```

## License
MIT License - See LICENSE file

## Authors
- Marco Zaccaria Di Fraia
- Neon Contributors
