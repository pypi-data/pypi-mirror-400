"""Tests for compare module."""


from neon import compare


class TestNear:
    """Tests for near() function."""

    def test_basic_near_equality(self) -> None:
        assert compare.near(0.1 + 0.2, 0.3) is True
        assert compare.near(1.0, 1.0) is True
        assert compare.near(1.0, 2.0) is False

    def test_relative_tolerance(self) -> None:
        assert compare.near(1000.0, 1001.0, rel_tol=1e-2) is True
        assert compare.near(1000.0, 1001.0, rel_tol=1e-4) is False

    def test_absolute_tolerance(self) -> None:
        assert compare.near(1e-15, 0.0, abs_tol=1e-14) is True
        assert compare.near(1e-15, 0.0, abs_tol=1e-16) is False

    def test_nan_handling(self) -> None:
        assert compare.near(float("nan"), float("nan")) is False
        assert compare.near(float("nan"), 0.0) is False
        assert compare.near(0.0, float("nan")) is False

    def test_infinity_handling(self) -> None:
        assert compare.near(float("inf"), float("inf")) is True
        assert compare.near(float("-inf"), float("-inf")) is True
        assert compare.near(float("inf"), float("-inf")) is False
        assert compare.near(float("inf"), 1e308) is False

    def test_signed_zeros(self) -> None:
        assert compare.near(0.0, -0.0) is True


class TestNearRel:
    """Tests for near_rel() function."""

    def test_relative_comparison(self) -> None:
        # 0.1% tolerance
        assert compare.near_rel(1000.0, 1001.0, tol=1e-2) is True
        assert compare.near_rel(1000.0, 1010.0, tol=1e-2) is True
        assert compare.near_rel(1000.0, 1011.0, tol=1e-2) is False

    def test_small_values(self) -> None:
        # Relative works for small values too
        assert compare.near_rel(1e-15, 1.5e-15, tol=0.5) is True


class TestNearAbs:
    """Tests for near_abs() function."""

    def test_absolute_comparison(self) -> None:
        assert compare.near_abs(0.001, 0.002, tol=0.01) is True
        assert compare.near_abs(0.001, 0.012, tol=0.01) is False

    def test_near_zero(self) -> None:
        assert compare.near_abs(1e-15, 0.0) is True
        assert compare.near_abs(1e-8, 0.0, tol=1e-7) is True

    def test_large_values(self) -> None:
        # Fixed tolerance regardless of magnitude
        assert compare.near_abs(1000.0, 1000.5, tol=1.0) is True
        assert compare.near_abs(1000.0, 1001.5, tol=1.0) is False


class TestNearZero:
    """Tests for near_zero() function."""

    def test_zero_detection(self) -> None:
        assert compare.near_zero(0.0) is True
        assert compare.near_zero(-0.0) is True
        assert compare.near_zero(1e-15) is True
        assert compare.near_zero(1e-5) is False

    def test_custom_tolerance(self) -> None:
        assert compare.near_zero(1e-15, abs_tol=1e-14) is True
        assert compare.near_zero(1e-15, abs_tol=1e-16) is False

    def test_nan_and_inf(self) -> None:
        assert compare.near_zero(float("nan")) is False
        assert compare.near_zero(float("inf")) is False
        assert compare.near_zero(float("-inf")) is False


class TestIsInteger:
    """Tests for is_integer() function."""

    def test_exact_integers(self) -> None:
        assert compare.is_integer(3.0) is True
        assert compare.is_integer(-5.0) is True
        assert compare.is_integer(0.0) is True

    def test_near_integers(self) -> None:
        assert compare.is_integer(3.0000000001) is True
        assert compare.is_integer(2.9999999999) is True
        assert compare.is_integer(-3.0000000001) is True

    def test_non_integers(self) -> None:
        assert compare.is_integer(3.1) is False
        assert compare.is_integer(2.5) is False

    def test_special_values(self) -> None:
        assert compare.is_integer(float("inf")) is False
        assert compare.is_integer(float("nan")) is False


class TestCompare:
    """Tests for compare() spaceship operator."""

    def test_less_than(self) -> None:
        assert compare.compare(1.0, 2.0) == -1

    def test_greater_than(self) -> None:
        assert compare.compare(2.0, 1.0) == 1

    def test_near_equal(self) -> None:
        assert compare.compare(1.0, 1.0 + 1e-15) == 0
        assert compare.compare(1.0, 1.0) == 0


class TestLessOrNear:
    """Tests for less_or_near() function."""

    def test_less_than(self) -> None:
        assert compare.less_or_near(1.0, 2.0) is True

    def test_near_equal(self) -> None:
        assert compare.less_or_near(1.0, 1.0 + 1e-15) is True

    def test_greater_than(self) -> None:
        assert compare.less_or_near(2.0, 1.0) is False


class TestGreaterOrNear:
    """Tests for greater_or_near() function."""

    def test_greater_than(self) -> None:
        assert compare.greater_or_near(2.0, 1.0) is True

    def test_near_equal(self) -> None:
        assert compare.greater_or_near(1.0, 1.0 - 1e-15) is True

    def test_less_than(self) -> None:
        assert compare.greater_or_near(1.0, 2.0) is False


class TestAllNear:
    """Tests for all_near() function."""

    def test_all_near(self) -> None:
        assert compare.all_near([(0.1 + 0.2, 0.3), (1.0, 1.0)]) is True

    def test_some_not_near(self) -> None:
        assert compare.all_near([(1.0, 1.0), (1.0, 2.0)]) is False

    def test_empty_list(self) -> None:
        assert compare.all_near([]) is True


class TestNearMany:
    """Tests for near_many() batch function."""

    def test_batch_comparison(self) -> None:
        pairs = [(0.1 + 0.2, 0.3), (1.0, 1.0), (1.0, 2.0)]
        result = compare.near_many(pairs)
        assert result == [True, True, False]

    def test_empty_list(self) -> None:
        assert compare.near_many([]) == []


class TestNearZeroMany:
    """Tests for near_zero_many() batch function."""

    def test_batch_near_zero(self) -> None:
        values = [1e-15, 0.5, -1e-16, 1.0, 2e-17]
        result = compare.near_zero_many(values)
        assert result == [True, False, True, False, True]

    def test_with_custom_tolerance(self) -> None:
        values = [1e-5, 1e-10, 1e-15]
        result = compare.near_zero_many(values, abs_tol=1e-9)
        assert result == [False, True, True]

    def test_empty_list(self) -> None:
        assert compare.near_zero_many([]) == []

    def test_special_values(self) -> None:
        values = [0.0, float('nan'), float('inf')]
        result = compare.near_zero_many(values)
        assert result == [True, False, False]


class TestIsIntegerMany:
    """Tests for is_integer_many() batch function."""

    def test_batch_integer_check(self) -> None:
        values = [3.0, 2.99999999999, 3.1, 5.00000000001]
        result = compare.is_integer_many(values)
        assert result == [True, True, False, True]

    def test_with_custom_tolerance(self) -> None:
        values = [3.1, 3.001, 3.0001]
        result = compare.is_integer_many(values, abs_tol=1e-3)
        assert result == [False, True, True]

    def test_empty_list(self) -> None:
        assert compare.is_integer_many([]) == []

    def test_special_values(self) -> None:
        values = [0.0, float('nan'), float('inf')]
        result = compare.is_integer_many(values)
        assert result == [True, False, False]
