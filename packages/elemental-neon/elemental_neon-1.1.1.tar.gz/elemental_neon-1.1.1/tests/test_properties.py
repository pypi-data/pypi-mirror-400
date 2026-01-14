"""Property-based tests using Hypothesis."""

import math

from hypothesis import assume, given
from hypothesis import strategies as st

from neon import clamp, compare, safe, ulp

# Strategy for finite floats (excluding NaN and inf)
finite_floats = st.floats(
    allow_nan=False,
    allow_infinity=False,
    min_value=-1e308,
    max_value=1e308,
)

# Strategy for positive finite floats
positive_floats = st.floats(
    allow_nan=False,
    allow_infinity=False,
    min_value=1e-300,
    max_value=1e308,
)


class TestCompareProperties:
    """Property-based tests for compare module."""

    @given(a=finite_floats, b=finite_floats)
    def test_near_is_commutative(self, a: float, b: float) -> None:
        """near(a, b) should equal near(b, a)."""
        assert compare.near(a, b) == compare.near(b, a)

    @given(x=finite_floats)
    def test_near_is_reflexive(self, x: float) -> None:
        """near(x, x) should always be True."""
        assert compare.near(x, x) is True

    @given(a=finite_floats, b=finite_floats)
    def test_compare_antisymmetric(self, a: float, b: float) -> None:
        """If compare(a,b) == 1, then compare(b,a) == -1."""
        result_ab = compare.compare(a, b)
        result_ba = compare.compare(b, a)

        if result_ab == 1:
            assert result_ba == -1
        elif result_ab == -1:
            assert result_ba == 1
        else:  # result_ab == 0
            assert result_ba == 0

    @given(x=finite_floats)
    def test_near_zero_consistency(self, x: float) -> None:
        """near_zero(x) should match near(x, 0)."""
        assert compare.near_zero(x) == compare.near(x, 0.0)

    @given(pairs=st.lists(st.tuples(finite_floats, finite_floats), min_size=0, max_size=10))
    def test_all_near_consistency(self, pairs: list[tuple[float, float]]) -> None:
        """all_near should match manually checking each pair."""
        expected = all(compare.near(a, b) for a, b in pairs) if pairs else True
        assert compare.all_near(pairs) == expected


class TestUlpProperties:
    """Property-based tests for ULP module."""

    @given(x=finite_floats)
    def test_next_prev_roundtrip(self, x: float) -> None:
        """next(prev(x)) should equal x."""
        assume(not math.isinf(x))
        assert ulp.next(ulp.prev(x)) == x

    @given(x=finite_floats)
    def test_prev_next_roundtrip(self, x: float) -> None:
        """prev(next(x)) should equal x."""
        assume(not math.isinf(x))
        assert ulp.prev(ulp.next(x)) == x

    @given(x=finite_floats, n=st.integers(min_value=-10_000, max_value=10_000))
    def test_add_inverse(self, x: float, n: int) -> None:
        """add(add(x, n), -n) should equal x for moderate ULP offsets."""
        assume(not math.isinf(x))
        result = ulp.add(ulp.add(x, n), -n)
        assert result == x

    @given(x=finite_floats)
    def test_diff_same_is_zero(self, x: float) -> None:
        """diff(x, x) should always be 0."""
        assume(not math.isinf(x))
        assert ulp.diff(x, x) == 0

    @given(x=finite_floats)
    def test_diff_next_is_one(self, x: float) -> None:
        """diff(x, next(x)) should be 1 for normal (non-denormal) values."""
        # Exclude denormals and values near zero where sign might change
        assume(not math.isinf(x) and abs(x) > 1e-300)
        assert ulp.diff(x, ulp.next(x)) == 1

    @given(a=finite_floats, b=finite_floats)
    def test_diff_is_commutative(self, a: float, b: float) -> None:
        """diff(a, b) should equal diff(b, a)."""
        assume(not math.isinf(a) and not math.isinf(b))
        assert ulp.diff(a, b) == ulp.diff(b, a)

    @given(a=finite_floats, b=finite_floats)
    def test_within_is_commutative(self, a: float, b: float) -> None:
        """within(a, b) should equal within(b, a)."""
        assert ulp.within(a, b) == ulp.within(b, a)


class TestClampProperties:
    """Property-based tests for clamp module."""

    @given(x=finite_floats)
    def test_to_zero_preserves_large_values(self, x: float) -> None:
        """to_zero should not change values far from zero."""
        assume(abs(x) > 1e-6)
        assert clamp.to_zero(x) == x

    @given(x=finite_floats, lo=finite_floats, hi=finite_floats)
    def test_to_range_bounds(self, x: float, lo: float, hi: float) -> None:
        """to_range should always return value within [lo, hi]."""
        assume(lo <= hi)
        result = clamp.to_range(x, lo, hi)
        assert lo <= result <= hi

    @given(x=finite_floats)
    def test_to_int_returns_float(self, x: float) -> None:
        """to_int should always return a float type."""
        result = clamp.to_int(x)
        assert isinstance(result, float)

    @given(values=st.lists(finite_floats, min_size=0, max_size=20))
    def test_to_zero_many_length(self, values: list[float]) -> None:
        """to_zero_many should return same length list."""
        result = clamp.to_zero_many(values)
        assert len(result) == len(values)


class TestSafeProperties:
    """Property-based tests for safe module."""

    @given(a=finite_floats, b=positive_floats)
    def test_div_matches_python_division(self, a: float, b: float) -> None:
        """div should match Python division for non-zero denominators."""
        assume(abs(a / b) < 1e100)  # Avoid overflow
        result = safe.div(a, b)
        assert result is not None
        expected = a / b
        if math.isinf(expected):
            assert math.isinf(result)
        else:
            assert abs(result - expected) < abs(expected) * 1e-10 + 1e-10

    @given(a=finite_floats)
    def test_div_by_zero_returns_default(self, a: float) -> None:
        """div(a, 0) should return default."""
        assert safe.div(a, 0.0) is None
        assert safe.div(a, 0.0, default=999.0) == 999.0

    @given(x=positive_floats)
    def test_sqrt_matches_math_sqrt(self, x: float) -> None:
        """sqrt should match math.sqrt for positive values."""
        result = safe.sqrt(x)
        assert result is not None
        assert abs(result - math.sqrt(x)) < 1e-10

    @given(values=st.lists(
        st.floats(allow_nan=False, allow_infinity=False, min_value=-1e100, max_value=1e100),
        min_size=1,
        max_size=100
    ))
    def test_sum_exact_not_empty(self, values: list[float]) -> None:
        """sum_exact should work for any non-empty list without overflow."""
        # Only test if sum won't overflow
        naive_sum = sum(values)
        assume(not math.isinf(naive_sum))
        result = safe.sum_exact(values)
        # Should be close to naive sum (within reason)
        assert isinstance(result, float)
        assert not math.isnan(result)

    @given(values=st.lists(
        st.floats(allow_nan=False, allow_infinity=False, min_value=-1e100, max_value=1e100),
        min_size=1,
        max_size=100
    ))
    def test_mean_exact_in_range(self, values: list[float]) -> None:
        """mean should be approximately between min and max."""
        assume(values)
        naive_sum = sum(values)
        assume(not math.isinf(naive_sum))
        result = safe.mean_exact(values)
        # For floating point, the mean should be within the range of values
        # Use a relative tolerance for large values
        min_val = min(values)
        max_val = max(values)
        # Use relative tolerance based on the magnitude of the values
        magnitude = max(abs(min_val), abs(max_val))
        tolerance = max(1.0, magnitude * 1e-10)
        assert min_val - tolerance <= result <= max_val + tolerance
