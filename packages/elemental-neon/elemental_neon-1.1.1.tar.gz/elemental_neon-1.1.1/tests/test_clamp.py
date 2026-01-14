"""Tests for clamp module."""

import math

from neon import clamp


class TestToZero:
    """Tests for to_zero() function."""

    def test_snap_to_zero(self) -> None:
        assert clamp.to_zero(1e-15) == 0.0
        assert clamp.to_zero(-1e-15) == 0.0

    def test_preserve_non_zero(self) -> None:
        assert clamp.to_zero(0.1) == 0.1
        assert clamp.to_zero(-0.1) == -0.1

    def test_custom_tolerance(self) -> None:
        assert clamp.to_zero(1e-15, abs_tol=1e-14) == 0.0
        assert clamp.to_zero(1e-15, abs_tol=1e-16) == 1e-15

    def test_nan_passthrough(self) -> None:
        result = clamp.to_zero(float("nan"))
        assert math.isnan(result)


class TestToInt:
    """Tests for to_int() function."""

    def test_exact_integers(self) -> None:
        assert clamp.to_int(3.0) == 3.0
        assert clamp.to_int(-5.0) == -5.0
        assert clamp.to_int(0.0) == 0.0

    def test_near_integers(self) -> None:
        assert clamp.to_int(2.9999999999) == 3.0
        assert clamp.to_int(3.0000000001) == 3.0
        assert clamp.to_int(-3.0000000001) == -3.0

    def test_preserve_non_integers(self) -> None:
        assert clamp.to_int(2.5) == 2.5
        assert clamp.to_int(3.1) == 3.1

    def test_nan_and_inf_passthrough(self) -> None:
        result = clamp.to_int(float("nan"))
        assert math.isnan(result)
        assert clamp.to_int(float("inf")) == float("inf")


class TestToValue:
    """Tests for to_value() function."""

    def test_snap_to_target(self) -> None:
        result = clamp.to_value(0.333333333, 1 / 3)
        assert result == 1 / 3

    def test_preserve_distant_value(self) -> None:
        assert clamp.to_value(0.5, 1 / 3) == 0.5

    def test_custom_tolerance(self) -> None:
        assert clamp.to_value(0.33, 1 / 3, abs_tol=0.01) == 1 / 3
        assert clamp.to_value(0.33, 1 / 3, abs_tol=0.001) == 0.33


class TestToRange:
    """Tests for to_range() function."""

    def test_within_range(self) -> None:
        assert clamp.to_range(5, 0, 10) == 5

    def test_below_range(self) -> None:
        assert clamp.to_range(-5, 0, 10) == 0

    def test_above_range(self) -> None:
        assert clamp.to_range(15, 0, 10) == 10

    def test_at_boundaries(self) -> None:
        assert clamp.to_range(0, 0, 10) == 0
        assert clamp.to_range(10, 0, 10) == 10

    def test_nan_passthrough(self) -> None:
        result = clamp.to_range(float("nan"), 0, 10)
        assert math.isnan(result)


class TestToValues:
    """Tests for to_values() function."""

    def test_snap_to_nearest_target(self) -> None:
        assert clamp.to_values(0.5000000001, [0.0, 0.5, 1.0]) == 0.5
        assert clamp.to_values(1.0000000001, [0.0, 0.5, 1.0]) == 1.0

    def test_preserve_distant_value(self) -> None:
        assert clamp.to_values(0.3, [0.0, 0.5, 1.0]) == 0.3
        assert clamp.to_values(0.7, [0.0, 0.5, 1.0]) == 0.7

    def test_empty_targets(self) -> None:
        assert clamp.to_values(0.5, []) == 0.5


class TestToZeroMany:
    """Tests for to_zero_many() batch function."""

    def test_batch_snap(self) -> None:
        result = clamp.to_zero_many([1e-15, 0.1, -1e-15])
        assert result == [0.0, 0.1, 0.0]

    def test_empty_list(self) -> None:
        assert clamp.to_zero_many([]) == []


class TestToIntMany:
    """Tests for to_int_many() batch function."""

    def test_batch_snap_to_int(self) -> None:
        result = clamp.to_int_many([2.99999999999, 3.1, 5.0, 7.00000000001])
        assert result == [3.0, 3.1, 5.0, 7.0]

    def test_with_custom_tolerance(self) -> None:
        result = clamp.to_int_many([2.01, 2.001], abs_tol=1e-2)
        assert result == [2.0, 2.0]

    def test_empty_list(self) -> None:
        assert clamp.to_int_many([]) == []

    def test_nan_and_inf_passthrough(self) -> None:
        import math
        result = clamp.to_int_many([3.0, float('nan'), float('inf')])
        assert result[0] == 3.0
        assert math.isnan(result[1])
        assert math.isinf(result[2])


class TestToRangeMany:
    """Tests for to_range_many() batch function."""

    def test_batch_clamp_to_range(self) -> None:
        result = clamp.to_range_many([5, -5, 15, 7], 0, 10)
        assert result == [5, 0, 10, 7]

    def test_all_within_range(self) -> None:
        result = clamp.to_range_many([1, 2, 3], 0, 10)
        assert result == [1, 2, 3]

    def test_all_outside_range(self) -> None:
        result = clamp.to_range_many([-10, -5, 15], 0, 10)
        assert result == [0, 0, 10]

    def test_empty_list(self) -> None:
        assert clamp.to_range_many([], 0, 10) == []

    def test_nan_passthrough(self) -> None:
        import math
        result = clamp.to_range_many([5, float('nan'), 15], 0, 10)
        assert result[0] == 5
        assert math.isnan(result[1])
        assert result[2] == 10
