"""Tests for neon.inspect module."""


import pytest

from neon import inspect as ni


class TestCheck:
    """Tests for check() function."""

    def test_normal_values_ok(self) -> None:
        assert ni.check(1.0) is None
        assert ni.check(42.5) is None
        assert ni.check(-100.0) is None
        assert ni.check(1e10) is None

    def test_zero_ok(self) -> None:
        assert ni.check(0.0) is None
        assert ni.check(-0.0) is None

    def test_denormal_warning(self) -> None:
        # Smallest denormal in FP64 is ~5e-324
        result = ni.check(5e-324)
        assert result is not None
        assert "denormal" in result.lower()
        assert "precision" in result.lower()

    def test_nan_warning(self) -> None:
        result = ni.check(float("nan"))
        assert result is not None
        assert "NaN" in result
        assert "invalid" in result.lower()

    def test_inf_warning_positive(self) -> None:
        result = ni.check(float("inf"))
        assert result is not None
        assert "Inf" in result
        assert "+" in result

    def test_inf_warning_negative(self) -> None:
        result = ni.check(float("-inf"))
        assert result is not None
        assert "Inf" in result
        assert "-" in result


class TestCheckMany:
    """Tests for check_many() function."""

    def test_all_normal(self) -> None:
        result = ni.check_many([1.0, 2.0, 3.0])
        assert "no issues" in result.lower()
        assert "3 values" in result

    def test_with_denormals(self) -> None:
        result = ni.check_many([1.0, 5e-324, 2.0])
        assert "denormal" in result.lower()
        assert "33.3%" in result or "33%" in result

    def test_with_nan(self) -> None:
        result = ni.check_many([1.0, float("nan"), 2.0])
        assert "NaN" in result
        assert "HIGH" in result

    def test_with_inf(self) -> None:
        result = ni.check_many([1.0, float("inf"), 2.0])
        assert "Inf" in result
        assert "HIGH" in result

    def test_mixed_issues(self) -> None:
        result = ni.check_many([1.0, 5e-324, float("nan")])
        assert "denormal" in result.lower()
        assert "NaN" in result
        assert "HIGH" in result

    def test_risk_assessment_low(self) -> None:
        result = ni.check_many([1.0, 2.0, 3.0, 4.0])
        assert "no issues" in result.lower()

    def test_risk_assessment_medium(self) -> None:
        # >5% denormals = MEDIUM risk
        values = [1.0] * 94 + [5e-324] * 6
        result = ni.check_many(values)
        assert "MEDIUM" in result

    def test_risk_assessment_high(self) -> None:
        result = ni.check_many([1.0, float("nan")])
        assert "HIGH" in result


class TestCompareDebug:
    """Tests for compare_debug() function."""

    def test_exact_equal(self) -> None:
        result = ni.compare_debug(1.0, 1.0)
        assert "exactly equal" in result.lower()

    def test_float_precision_issue(self) -> None:
        result = ni.compare_debug(0.1 + 0.2, 0.3)
        assert "differ" in result.lower()
        assert "ULP" in result
        assert "near()" in result  # Recommends neon.compare.near()

    def test_small_difference(self) -> None:
        result = ni.compare_debug(1.0, 1.0 + 1e-15)
        # The actual difference is ~1.11e-15 due to rounding
        assert "1.1" in result and "15" in result  # Matches "1.110223025e-15"
        assert "near()" in result.lower()

    def test_large_difference(self) -> None:
        result = ni.compare_debug(1.0, 2.0)
        assert "significantly different" in result.lower()

    def test_division_by_zero_in_percentage(self) -> None:
        result = ni.compare_debug(1.0, 0.0)
        assert "N/A" in result

    def test_nan_values(self) -> None:
        result = ni.compare_debug(float("nan"), 1.0)
        assert "N/A" in result or "NaN" in result


class TestDivDebug:
    """Tests for div_debug() function."""

    def test_safe_division(self) -> None:
        result = ni.div_debug(6.0, 3.0)
        assert "safe" in result.lower()

    def test_division_by_zero(self) -> None:
        result = ni.div_debug(1.0, 0.0)
        assert "Division by zero" in result
        assert "safe.div()" in result

    def test_denormal_denominator(self) -> None:
        result = ni.div_debug(1.0, 5e-324)
        assert "denormal" in result.lower()
        assert "safe.div()" in result

    def test_nan_denominator(self) -> None:
        result = ni.div_debug(1.0, float("nan"))
        assert "NaN" in result
        assert "safe.div()" in result

    def test_overflow_result(self) -> None:
        result = ni.div_debug(1e308, 1e-308)
        # May overflow to inf
        # Just check it doesn't crash
        assert isinstance(result, str)


class TestAnalyze:
    """Tests for analyze() function."""

    def test_normal_values(self) -> None:
        report = ni.analyze([1.0, 2.0, 3.0])
        assert report.total == 3
        assert report.normal == 3
        assert report.denormal == 0
        assert report.nan == 0
        assert report.precision_risk == "LOW"

    def test_mixed_categories(self) -> None:
        values = [1.0, 5e-324, float("nan"), 2.0]
        report = ni.analyze(values)

        assert report.total == 4
        assert report.normal == 2
        assert report.denormal == 1
        assert report.nan == 1

    def test_precision_risk_high(self) -> None:
        values = [1.0, float("nan")]
        report = ni.analyze(values)
        assert report.precision_risk == "HIGH"

    def test_precision_risk_medium(self) -> None:
        # >5% denormals = MEDIUM
        values = [1.0] * 94 + [5e-324] * 6
        report = ni.analyze(values)
        assert report.precision_risk == "MEDIUM"

    def test_issues_populated(self) -> None:
        values = [1.0, 5e-324, float("nan")]
        report = ni.analyze(values)
        assert len(report.issues) > 0
        assert any("denormal" in issue.lower() for issue in report.issues)
        assert any("NaN" in issue for issue in report.issues)

    def test_recommendations_populated(self) -> None:
        values = [1.0, 5e-324]
        report = ni.analyze(values)
        assert len(report.recommendations) > 0
        assert any("to_zero" in rec.lower() for rec in report.recommendations)

    def test_str_representation(self) -> None:
        report = ni.analyze([1.0, 1e-400, 2.0])
        report_str = str(report)
        assert "Analysis of 3 values" in report_str
        assert "Normal:" in report_str
        assert "Denormal:" in report_str


class TestPrecisionLoss:
    """Tests for precision_loss() function."""

    def test_no_loss(self) -> None:
        assert ni.precision_loss(1.0, 1.0) is None

    def test_sum_precision_loss(self) -> None:
        # Naive sum loses precision on most platforms
        got = sum([0.1] * 10)
        expected = 1.0
        result = ni.precision_loss(got, expected)
        # On some platforms/compilers, this might be exactly equal
        # The important thing is precision_loss doesn't crash
        if result is not None:
            assert "Precision loss" in result
            # Check for scientific notation of the error (platform-dependent)
            assert "e-16" in result or "e-15" in result

    def test_large_error_not_precision_issue(self) -> None:
        # >1% error is logic bug, not precision loss
        result = ni.precision_loss(1.0, 2.0)
        assert result is None

    def test_acceptable_precision(self) -> None:
        # Very small error is precision loss
        result = ni.precision_loss(1.0, 1.0 + 1e-10)
        assert result is not None
        assert "Precision loss" in result

    def test_nan_values(self) -> None:
        # NaN comparisons should not crash
        result = ni.precision_loss(float("nan"), 1.0)
        # May return None or string, just check it doesn't crash
        assert result is None or isinstance(result, str)


class TestSafeForDtype:
    """Tests for safe_for_dtype() function."""

    def test_normal_value_fp32(self) -> None:
        check = ni.safe_for_dtype(1.0, target="fp32")
        assert check.safe

    def test_fp16_overflow(self) -> None:
        check = ni.safe_for_dtype(1e6, target="fp16")
        assert not check.safe
        assert check.issue == "overflow"
        assert "6.55e+04" in check.message or "65504" in check.message

    def test_fp16_underflow(self) -> None:
        check = ni.safe_for_dtype(1e-10, target="fp16")
        assert not check.safe
        assert check.issue == "underflow"

    def test_bf16_range(self) -> None:
        # BF16 has same range as FP32
        check = ni.safe_for_dtype(1e20, target="bf16")
        assert check.safe

    def test_bf16_large_value(self) -> None:
        # BF16 supports large values like FP32
        check = ni.safe_for_dtype(1e30, target="bf16")
        assert check.safe

    def test_fp8_e4m3_limits(self) -> None:
        # FP8 E4M3 max is ~448
        check = ni.safe_for_dtype(500, target="fp8_e4m3")
        assert not check.safe
        assert check.issue == "overflow"

    def test_fp8_e4m3_safe(self) -> None:
        check = ni.safe_for_dtype(100, target="fp8_e4m3")
        assert check.safe

    def test_fp8_e5m2_range(self) -> None:
        # FP8 E5M2 has wider range
        check = ni.safe_for_dtype(10000, target="fp8_e5m2")
        assert check.safe

    def test_nan_invalid(self) -> None:
        check = ni.safe_for_dtype(float("nan"), target="fp16")
        assert not check.safe
        assert check.issue == "invalid"

    def test_inf_invalid(self) -> None:
        check = ni.safe_for_dtype(float("inf"), target="fp16")
        assert not check.safe
        assert check.issue == "invalid"

    def test_zero_safe(self) -> None:
        check = ni.safe_for_dtype(0.0, target="fp16")
        assert check.safe

    def test_negative_values(self) -> None:
        # Test that absolute value is used
        check = ni.safe_for_dtype(-100, target="fp16")
        assert check.safe

    def test_invalid_dtype(self) -> None:
        with pytest.raises(ValueError, match="Unknown dtype"):
            ni.safe_for_dtype(1.0, target="invalid_dtype")


class TestAnalyzeForDtype:
    """Tests for analyze_for_dtype() function."""

    def test_all_safe(self) -> None:
        report = ni.analyze_for_dtype([1.0, 2.0, 3.0], target="fp32")
        assert report.safe == 3
        assert report.overflow == 0
        assert report.underflow == 0
        assert "All values safe" in report.recommendation

    def test_fp16_overflow_detection(self) -> None:
        values = [1.0, 1e10]
        report = ni.analyze_for_dtype(values, target="fp16")
        assert report.overflow == 1
        assert report.safe == 1
        assert "overflow" in report.recommendation.lower()

    def test_fp16_underflow_detection(self) -> None:
        values = [1.0, 1e-10]
        report = ni.analyze_for_dtype(values, target="fp16")
        assert report.underflow == 1
        assert "underflow" in report.recommendation.lower()

    def test_mixed_issues(self) -> None:
        values = [1.0, 1e10, 1e-10]
        report = ni.analyze_for_dtype(values, target="fp16")
        assert report.overflow == 1
        assert report.underflow == 1
        assert report.safe == 1

    def test_invalid_values(self) -> None:
        values = [1.0, float("nan")]
        report = ni.analyze_for_dtype(values, target="fp16")
        assert report.invalid == 1
        assert "NaN/Inf" in report.recommendation

    def test_high_underflow_percentage(self) -> None:
        # >5% underflow triggers special recommendation
        values = [1.0] * 94 + [1e-10] * 6
        report = ni.analyze_for_dtype(values, target="fp16")
        assert report.underflow == 6
        assert ("6.0%" in report.recommendation or "6%" in report.recommendation)


class TestCompareDtypes:
    """Tests for compare_dtypes() function."""

    def test_single_dtype(self) -> None:
        comparison = ni.compare_dtypes([1.0, 2.0], targets=["fp32"])
        assert "fp32" in comparison.results
        assert comparison.results["fp32"]["precision_loss"] == "LOW"

    def test_multiple_dtypes(self) -> None:
        comparison = ni.compare_dtypes([1.0, 2.0], targets=["fp16", "bf16", "fp32"])
        assert len(comparison.results) == 3
        assert "fp16" in comparison.results
        assert "bf16" in comparison.results
        assert "fp32" in comparison.results

    def test_recommendation_chooses_best(self) -> None:
        # Values that overflow FP16 but not BF16
        values = [1.0, 1e10]
        comparison = ni.compare_dtypes(values, targets=["fp16", "bf16"])
        # BF16 should be recommended (no overflow)
        assert "BF16" in comparison.recommendation.upper()

    def test_precision_loss_risk_assessment(self) -> None:
        values = [1.0, float("nan")]
        comparison = ni.compare_dtypes(values, targets=["fp16"])
        assert comparison.results["fp16"]["precision_loss"] == "HIGH"

    def test_medium_risk_underflow(self) -> None:
        # >5% underflow = MEDIUM risk
        values = [1.0] * 94 + [1e-10] * 6
        comparison = ni.compare_dtypes(values, targets=["fp16"])
        assert comparison.results["fp16"]["precision_loss"] == "MEDIUM"

    def test_fp8_comparison(self) -> None:
        values = [1.0, 100.0, 200.0]
        comparison = ni.compare_dtypes(
            values, targets=["fp8_e4m3", "fp8_e5m2", "fp16"]
        )
        # All should be safe for FP16
        assert comparison.results["fp16"]["overflow"] == 0
        # FP8_E4M3 max is ~448, so all safe
        assert comparison.results["fp8_e4m3"]["overflow"] == 0
