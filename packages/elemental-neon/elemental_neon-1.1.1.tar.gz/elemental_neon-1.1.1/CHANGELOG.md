# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2026-01-07

### Changed - Internal Code Quality Improvements

**Refactored for improved maintainability** - No API changes, all existing code works exactly the same.

- **Eliminated code duplication:**
  - Extracted `_assess_risk()` helper function in `inspect.py` (eliminates 3 duplicate risk assessment blocks)
  - Extracted `_dtype_comparison_key()` helper function in `inspect.py` (eliminates complex lambda)
  - Added `validate_equal_length()` to `_validation.py` (eliminates 4 duplicate length validation blocks)

- **Replaced magic numbers with named constants in `inspect.py`:**
  - `DENORMAL_THRESHOLD = 2.225073858507201e-308`
  - `RISK_THRESHOLD_PERCENT = 0.05`
  - `RISK_LEVEL_SCORE = {"HIGH": 2, "MEDIUM": 1, "LOW": 0}`

- **Improved validation consistency:**
  - `safe.div_many()` and `safe.pow_many()` now use centralized length validation
  - `ulp.diff_many()` and `ulp.within_many()` now use centralized length validation
  - Error messages are now consistent across all batch operations

### Fixed

- **PyPI author metadata:** Author now correctly displays as "Marco Zaccaria Di Fraia, Neon Contributors"

### Technical Details

- **Test coverage:** 95.89% (225 tests passing, same as v1.1.0)
- **Zero new dependencies:** Still pure stdlib
- **No API changes:** 100% backward compatible with v1.1.0
- **Code quality improvement:** Reduced code duplication from ~40 lines to 0

## [1.1.0] - 2026-01-05

### Added - Production Float Debugging & Low-Precision Validation

**New Module: `neon.inspect`** - Production debugging tools for floating-point issues

- **Quick Health Checks:**
  - `check(x)` - Returns warning string if value has issues (NaN, Inf, denormal), None if safe
  - `check_many(values)` - Batch health summary with risk assessment (LOW/MEDIUM/HIGH)

- **Debug Helpers:**
  - `compare_debug(a, b)` - Explains why two floats differ with ULP distance and recommendations
  - `div_debug(a, b)` - Debugs division issues (zero denominator, denormals, overflow)
  - `analyze(values)` - Comprehensive analysis with categorization and recommendations
  - `precision_loss(got, expected)` - Detects when precision loss caused unexpected results

- **Low-Precision Dtype Validation (FP8/FP16/BF16):**
  - `safe_for_dtype(x, target)` - Check if value is safe for target dtype conversion
  - `analyze_for_dtype(values, target)` - Batch analysis for dtype compatibility
  - `compare_dtypes(values, targets)` - Compare safety across multiple dtypes
  - Supported dtypes: `fp32`, `fp16`, `bf16`, `fp8_e4m3`, `fp8_e5m2`

**Use Case:** Validate model weights before FP8 quantization for H100/H200 GPU deployment

**Batch Operations Added** - Convenience functions for processing collections:

- `neon.safe`: `div_many()`, `sqrt_many()`, `log_many()`, `pow_many()`
- `neon.compare`: `near_zero_many()`, `is_integer_many()`
- `neon.clamp`: `to_int_many()`, `to_range_many()`
- `neon.ulp`: `of_many()`, `diff_many()`, `within_many()`

Note: Batch operations use Python loops for simplicity. For performance-critical array operations, use NumPy.

### Changed

- Version bumped to 1.1.0
- Added `inspect` module to `__all__` exports

### Technical Details

- **Code added:** ~650 lines production code, ~550 lines tests
- **Test coverage:** 93.19% (183 tests passing, exceeds 90% requirement)
- **Dependencies:** Zero new dependencies (still pure stdlib)
- **Package size:** Remains <100KB

### Documentation

- `neon.inspect` module provides actionable debugging output, not just technical data
- All functions return clear recommendations for fixing issues
- Examples target real-world scenarios (debugging NaN in production, validating FP8 conversion)

## [1.0.0] - 2026-01-04

### Production release - Stable API

This v1.0.0 release commits to API stability following semver. No breaking changes will occur in the 1.x series without a major version bump.

**Features:**

- **Comparison module** (`neon.compare`): Approximate equality with tolerance
  - `near()`, `near_rel()`, `near_abs()`, `near_zero()`, `is_integer()`
  - `compare()`, `less_or_near()`, `greater_or_near()`
  - `all_near()`, `near_many()` batch operations
- **Clamping module** (`neon.clamp`): Value snapping and range constraints
  - `to_zero()`, `to_int()`, `to_value()`, `to_range()`, `to_values()`
  - `to_zero_many()` batch operation
- **Safe arithmetic** (`neon.safe`): Graceful edge case handling
  - `div()`, `div_or_zero()`, `div_or_inf()` safe division
  - `mod()`, `sqrt()`, `log()`, `pow()` safe operations
  - `sum_exact()`, `mean_exact()` with `math.fsum()` for precision
- **ULP operations** (`neon.ulp`): Unit-in-last-place precision control
  - `of()`, `diff()`, `within()` ULP analysis
  - `next()`, `prev()`, `add()` ULP manipulation
- **Exception hierarchy**: `NeonError`, `InvalidValueError`, `EmptyInputError`
- **Type safety**: Full mypy strict compliance with explicit `__all__` exports
- **Zero dependencies**: Pure Python standard library only

**Testing & Quality:**

- 118 unit tests covering all API functions (100% pass rate)
- Property-based tests with Hypothesis for mathematical correctness
- 91% code coverage (exceeds 90% requirement)
- Tested on Python 3.9, 3.10, 3.11, 3.12, 3.13
- Type checking with mypy --strict
- Linting with ruff
- Pre-commit hooks configured
- Performance benchmarking suite

**Quality Improvements:**

- Better default tolerances: `abs_tol=1e-9` instead of 0.0 (more practical)
- Performance: O(1) ULP diff using IEEE 754 bit manipulation (~1M operations/sec)
- Type consistency: `to_int()` always returns `float` (no runtime type switching)
- Convenience functions: `near_rel()` and `near_abs()` for common patterns
- Comprehensive documentation with cookbook examples
- Interactive Jupyter notebook demo
- Benchmarked performance claims verified

**Breaking Changes from beta (0.1.0):**

- Renamed `ulp.near()` → `ulp.within()` for API clarity
- Changed `to_int()` return type from `Union[float, int]` to `float` for consistency
- Changed default `abs_tol` from `0.0` to `1e-9` (better defaults for 95% of use cases)
- Replaced Python Kahan summation with C `math.fsum()` (~10x faster)

**Known Limitations (documented):**

- Uses Python `float` (IEEE 754 double precision, ~15-17 significant digits)
- Not suitable for arbitrary-precision arithmetic (use `decimal.Decimal` instead)
- Not optimized for vectorized operations on millions of floats (use NumPy instead)
- `math.fsum()` cannot recover from catastrophic cancellation

**API Stability Guarantee:**

All public APIs in `neon.compare`, `neon.clamp`, `neon.safe`, and `neon.ulp` are **stable**. No breaking changes will occur in the 1.x series without a major version bump to 2.0.0.
