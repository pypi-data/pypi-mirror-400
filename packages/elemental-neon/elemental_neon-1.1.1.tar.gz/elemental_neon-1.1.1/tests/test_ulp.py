"""Tests for ULP module."""

import pytest

from neon import ulp
from neon.exceptions import InvalidValueError


class TestOf:
    """Tests for ulp.of() function."""

    def test_normal_values(self) -> None:
        result = ulp.of(1.0)
        assert result == 2.220446049250313e-16

    def test_zero(self) -> None:
        result = ulp.of(0.0)
        assert result > 0  # Smallest positive denormal

    def test_infinity(self) -> None:
        assert ulp.of(float("inf")) == float("inf")

    def test_nan(self) -> None:
        with pytest.raises(InvalidValueError):
            ulp.of(float("nan"))


class TestDiff:
    """Tests for ulp.diff() function."""

    def test_same_value(self) -> None:
        assert ulp.diff(1.0, 1.0) == 0

    def test_adjacent_values(self) -> None:
        next_val = ulp.next(1.0)
        assert ulp.diff(1.0, next_val) == 1

    def test_nan_raises(self) -> None:
        with pytest.raises(InvalidValueError):
            ulp.diff(float("nan"), 1.0)
        with pytest.raises(InvalidValueError):
            ulp.diff(1.0, float("nan"))

    def test_infinity_raises(self) -> None:
        with pytest.raises(InvalidValueError):
            ulp.diff(float("inf"), 1.0)


class TestWithin:
    """Tests for ulp.within() function."""

    def test_exact_equality(self) -> None:
        assert ulp.within(1.0, 1.0) is True

    def test_within_tolerance(self) -> None:
        val = ulp.add(1.0, 4)
        assert ulp.within(1.0, val) is True

    def test_outside_tolerance(self) -> None:
        val = ulp.add(1.0, 5)
        assert ulp.within(1.0, val) is False

    def test_custom_max_ulps(self) -> None:
        val = ulp.add(1.0, 10)
        assert ulp.within(1.0, val, max_ulps=10) is True
        assert ulp.within(1.0, val, max_ulps=5) is False

    def test_nan_handling(self) -> None:
        assert ulp.within(float("nan"), float("nan")) is False
        assert ulp.within(float("nan"), 1.0) is False


class TestNext:
    """Tests for ulp.next() function."""

    def test_next_above(self) -> None:
        result = ulp.next(1.0)
        assert result > 1.0
        assert result == 1.0000000000000002

    def test_next_infinity(self) -> None:
        assert ulp.next(float("inf")) == float("inf")


class TestPrev:
    """Tests for ulp.prev() function."""

    def test_prev_below(self) -> None:
        result = ulp.prev(1.0)
        assert result < 1.0
        assert result == 0.9999999999999999

    def test_prev_negative_infinity(self) -> None:
        assert ulp.prev(float("-inf")) == float("-inf")


class TestAdd:
    """Tests for ulp.add() function."""

    def test_zero_ulps(self) -> None:
        assert ulp.add(1.0, 0) == 1.0

    def test_positive_ulps(self) -> None:
        assert ulp.add(1.0, 1) == ulp.next(1.0)
        result = ulp.add(1.0, 2)
        assert result == ulp.next(ulp.next(1.0))

    def test_negative_ulps(self) -> None:
        assert ulp.add(1.0, -1) == ulp.prev(1.0)

    def test_round_trip(self) -> None:
        original = 1.0
        moved = ulp.add(original, 5)
        back = ulp.add(moved, -5)
        assert back == original


class TestOfMany:
    """Tests for of_many() batch function."""

    def test_batch_ulp_calculation(self) -> None:
        values = [1.0, 10.0, 100.0]
        ulps = ulp.of_many(values)
        assert len(ulps) == 3
        assert all(u > 0 for u in ulps)
        # ULP size should increase with magnitude
        assert ulps[1] > ulps[0]
        assert ulps[2] > ulps[1]

    def test_zero_value(self) -> None:
        ulps = ulp.of_many([0.0, 1.0])
        assert ulps[0] > 0  # Smallest denormal
        assert ulps[1] > 0

    def test_empty_list(self) -> None:
        assert ulp.of_many([]) == []

    def test_raises_on_nan(self) -> None:
        from neon.exceptions import InvalidValueError
        with pytest.raises(InvalidValueError):
            ulp.of_many([1.0, float('nan')])


class TestDiffMany:
    """Tests for diff_many() batch function."""

    def test_batch_ulp_distance(self) -> None:
        a_values = [1.0, 2.0]
        b_values = [1.0, 2.0]
        result = ulp.diff_many(a_values, b_values)
        assert result == [0, 0]

    def test_adjacent_values(self) -> None:
        a_values = [1.0, 2.0]
        b_values = [ulp.next(1.0), ulp.next(2.0)]
        result = ulp.diff_many(a_values, b_values)
        assert result == [1, 1]

    def test_mismatched_lengths_raises(self) -> None:
        with pytest.raises(ValueError):
            ulp.diff_many([1.0, 2.0], [1.0])

    def test_raises_on_nan(self) -> None:
        from neon.exceptions import InvalidValueError
        with pytest.raises(InvalidValueError):
            ulp.diff_many([1.0], [float('nan')])


class TestWithinMany:
    """Tests for within_many() batch function."""

    def test_batch_ulp_comparison(self) -> None:
        a_values = [1.0, 2.0]
        b_values = [1.0, 2.1]
        result = ulp.within_many(a_values, b_values, max_ulps=4)
        assert result[0] is True   # Exact match
        assert result[1] is False  # Too far apart

    def test_custom_max_ulps(self) -> None:
        a_values = [1.0]
        b_values = [ulp.add(1.0, 10)]
        result = ulp.within_many(a_values, b_values, max_ulps=20)
        assert result == [True]

    def test_mismatched_lengths_raises(self) -> None:
        with pytest.raises(ValueError):
            ulp.within_many([1.0, 2.0], [1.0])
