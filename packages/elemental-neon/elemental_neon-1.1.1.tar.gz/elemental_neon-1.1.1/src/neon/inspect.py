"""Float inspection and dtype safety validation.

Internal tool for debugging float issues and validating dtype conversions.
Focuses on production use cases: post-mortem analysis and FP8/FP16 validation.
"""

import math
from dataclasses import dataclass
from typing import Literal, Optional, Union, cast

from . import ulp as neon_ulp

__all__ = [
    "check",
    "check_many",
    "compare_debug",
    "div_debug",
    "analyze",
    "precision_loss",
    "safe_for_dtype",
    "analyze_for_dtype",
    "compare_dtypes",
]

# Module-level constants
DENORMAL_THRESHOLD = 2.225073858507201e-308  # Smallest normal float64
RISK_THRESHOLD_PERCENT = 0.05  # 5% denormals triggers MEDIUM risk
RISK_LEVEL_SCORE = {"HIGH": 2, "MEDIUM": 1, "LOW": 0}  # For dtype comparison sorting

# Float format limits for dtype validation
DTYPE_LIMITS = {
    "fp32": {"min": 1.175494e-38, "max": 3.4028235e38},
    "fp16": {"min": 6.104e-5, "max": 65504.0},
    "bf16": {"min": 1.175494e-38, "max": 3.4028235e38},
    "fp8_e4m3": {"min": 0.001953125, "max": 448.0},
    "fp8_e5m2": {"min": 0.0001525878, "max": 57344.0},
}


def _categorize(x: float) -> Literal["zero", "denormal", "normal", "nan", "inf"]:
    """Categorize float for internal use."""
    if math.isnan(x):
        return "nan"
    if math.isinf(x):
        return "inf"
    if x == 0.0:
        return "zero"
    # Denormals are smaller than minimum normal FP64
    if abs(x) < DENORMAL_THRESHOLD:
        return "denormal"
    return "normal"


def _assess_risk(counts: dict[str, int], total: int) -> Literal["LOW", "MEDIUM", "HIGH"]:
    """Assess precision risk from categorized float counts.

    Args:
        counts: Dictionary with keys "nan", "inf", "denormal", etc.
        total: Total number of values

    Returns:
        Risk level: "HIGH" if NaN/Inf present, "MEDIUM" if >5% denormals, else "LOW"
    """
    if counts.get("nan", 0) > 0 or counts.get("inf", 0) > 0:
        return "HIGH"
    elif total > 0 and (counts.get("denormal", 0) / total) > RISK_THRESHOLD_PERCENT:
        return "MEDIUM"
    return "LOW"


def _dtype_comparison_key(item: tuple[str, dict[str, Union[int, str]]]) -> tuple[int, int, int, int]:
    """Key function for sorting dtype comparison results.

    Args:
        item: Tuple of (dtype_name, results_dict)

    Returns:
        Sort key prioritizing invalid, overflow, underflow, then risk level
    """
    results = item[1]
    return (
        cast(int, results["invalid"]),
        cast(int, results["overflow"]),
        cast(int, results["underflow"]),
        RISK_LEVEL_SCORE[cast(str, results["precision_loss"])],
    )


# ============================================================================
# Production Debugging API
# ============================================================================


def check(x: float) -> Optional[str]:
    """Quick health check - returns warning message or None.

    Args:
        x: Value to check

    Returns:
        Warning message if issue found, None if value is safe

    Examples:
        >>> check(1.0)
        >>> check(1e-400)
        'Value 1.00e-400 is denormal - will lose precision in arithmetic'
        >>> check(float('nan'))
        'Value is NaN - check for division by zero or invalid operation'
    """
    cat = _categorize(x)

    if cat == "nan":
        return "Value is NaN - check for division by zero or invalid operation"

    if cat == "inf":
        sign = "+" if x > 0 else "-"
        return f"Value is {sign}Inf - check for overflow or division by zero"

    if cat == "denormal":
        return f"Value {x:.2e} is denormal - will lose precision in arithmetic"

    # Normal and zero are fine
    return None


def check_many(values: list[float]) -> str:
    """Batch health check - returns summary string.

    Args:
        values: Collection to check

    Returns:
        Summary string describing any issues found

    Examples:
        >>> check_many([1.0, 2.0, 3.0])
        'All 3 values are normal - no issues detected'
        >>> check_many([1.0, 1e-400, float('nan')])
        'Found 1 denormal (33.3%), 1 NaN - precision risk: HIGH'
    """
    counts = {"normal": 0, "denormal": 0, "zero": 0, "nan": 0, "inf": 0}

    for x in values:
        counts[_categorize(x)] += 1

    total = len(values)

    # All good?
    if counts["nan"] == 0 and counts["inf"] == 0 and counts["denormal"] == 0:
        return f"All {total} values are normal - no issues detected"

    # Build issue summary
    issues = []
    if counts["denormal"] > 0:
        pct = (counts["denormal"] / total) * 100
        issues.append(f"{counts['denormal']} denormal ({pct:.1f}%)")

    if counts["nan"] > 0:
        issues.append(f"{counts['nan']} NaN")

    if counts["inf"] > 0:
        issues.append(f"{counts['inf']} Inf")

    # Risk assessment
    risk = _assess_risk(counts, total)

    return f"Found {', '.join(issues)} - precision risk: {risk}"


def compare_debug(a: float, b: float) -> str:
    """Debug why two floats aren't equal.

    Args:
        a: First value
        b: Second value

    Returns:
        Explanation with ULP distance and recommendation

    Examples:
        >>> compare_debug(0.1 + 0.2, 0.3)  # doctest: +SKIP
        'Values differ by 5.551115e-17 (0.000000018%)\\nULP distance: 1\\nRecommendation: Use neon.compare.near() with default tolerances'  # noqa: E501
    """
    if a == b:
        return "Values are exactly equal"

    diff = abs(a - b)

    # Avoid division by zero
    if b == 0:
        pct_str = "N/A (denominator is zero)"
    else:
        pct = (diff / abs(b)) * 100
        pct_str = f"{pct:.9f}%"

    # Get ULP distance
    try:
        ulp_dist = neon_ulp.diff(a, b)
        ulp_str = f"ULP distance: {ulp_dist}"
    except Exception:
        ulp_str = "ULP distance: N/A (values are NaN or Inf)"

    # Recommendation
    if diff < 1e-9:
        rec = "Recommendation: Use neon.compare.near() with default tolerances"
    elif diff < 1e-6:
        rec = "Recommendation: Use neon.compare.near() with rel_tol=1e-6"
    else:
        rec = "Values are significantly different - not a float precision issue"

    return f"Values differ by {diff:.9e} ({pct_str})\n{ulp_str}\n{rec}"


def div_debug(a: float, b: float) -> str:
    """Debug division issues.

    Args:
        a: Numerator
        b: Denominator

    Returns:
        Explanation of division issues and recommendation

    Examples:
        >>> div_debug(1.0, 0.0)  # doctest: +SKIP
        'Division by zero detected\\nRecommendation: Use neon.safe.div() with appropriate default'
        >>> div_debug(1.0, 1e-320)  # doctest: +SKIP
        'Denominator issue: Value 1.00e-320 is denormal - will lose precision in arithmetic\\nRecommendation: Use neon.safe.div() with appropriate default'  # noqa: E501
    """
    issues = []

    # Check denominator
    b_issue = check(b)
    if b_issue:
        issues.append(f"Denominator issue: {b_issue}")

    # Check for zero
    if b == 0:
        issues.append("Division by zero detected")
        return (
            "\n".join(issues)
            + "\nRecommendation: Use neon.safe.div() with appropriate default"
        )

    # Try division
    try:
        result = a / b
        result_issue = check(result)
        if result_issue:
            issues.append(f"Result issue: {result_issue}")
    except Exception as e:
        issues.append(f"Division failed: {e}")

    if issues:
        return (
            "\n".join(issues)
            + "\nRecommendation: Use neon.safe.div() with appropriate default"
        )

    return "Division appears safe - no issues detected"


@dataclass
class AnalysisReport:
    """Analysis report for production debugging."""

    total: int
    normal: int
    denormal: int
    zero: int
    nan: int
    inf: int
    precision_risk: Literal["LOW", "MEDIUM", "HIGH"]
    issues: list[str]
    recommendations: list[str]

    def __str__(self) -> str:
        lines = [
            f"Analysis of {self.total} values:",
            f"  Normal: {self.normal} ({self.normal/self.total*100:.2f}%)",
            f"  Denormal: {self.denormal} ({self.denormal/self.total*100:.2f}%)"
            + (" ⚠️" if self.denormal > 0 else ""),
            f"  Zero: {self.zero} ({self.zero/self.total*100:.2f}%)",
            f"  NaN: {self.nan}" + (" ❌" if self.nan > 0 else ""),
            f"  Inf: {self.inf}" + (" ❌" if self.inf > 0 else ""),
            "",
            f"  Precision risk: {self.precision_risk}",
        ]

        if self.issues:
            lines.append("")
            lines.append("  Issues:")
            for issue in self.issues:
                lines.append(f"  - {issue}")

        if self.recommendations:
            lines.append("")
            lines.append("  Recommendations:")
            for rec in self.recommendations:
                lines.append(f"  - {rec}")

        return "\n".join(lines)


def analyze(values: list[float]) -> AnalysisReport:
    """Comprehensive analysis for production debugging.

    Args:
        values: Collection to analyze

    Returns:
        Detailed analysis report with issues and recommendations

    Examples:
        >>> report = analyze([1.0, 1e-400, 2.0, float('nan')])
        >>> print(report.precision_risk)
        HIGH
    """
    counts = {"normal": 0, "denormal": 0, "zero": 0, "nan": 0, "inf": 0}

    for x in values:
        counts[_categorize(x)] += 1

    total = len(values)

    # Assess risk
    risk = _assess_risk(counts, total)

    # Identify issues
    issues = []
    if counts["denormal"] > 0:
        pct = (counts["denormal"] / total) * 100
        issues.append(f"{pct:.2f}% of values are denormal")

    if counts["nan"] > 0:
        issues.append(f"{counts['nan']} NaN value(s) detected")

    if counts["inf"] > 0:
        issues.append(f"{counts['inf']} Inf value(s) detected")

    # Generate recommendations
    recommendations = []
    if counts["denormal"] > 0:
        recommendations.append("Use neon.clamp.to_zero() to clean denormals")

    if counts["nan"] > 0:
        recommendations.append(
            "Check for invalid operations causing NaN (division by zero, log of negative, etc)"
        )

    if counts["inf"] > 0:
        recommendations.append(
            "Check for overflow in multiplication or division by near-zero"
        )

    return AnalysisReport(
        total=total,
        normal=counts["normal"],
        denormal=counts["denormal"],
        zero=counts["zero"],
        nan=counts["nan"],
        inf=counts["inf"],
        precision_risk=risk,
        issues=issues,
        recommendations=recommendations,
    )


def precision_loss(got: float, expected: float) -> Optional[str]:
    """Detect if an operation lost precision.

    Args:
        got: Actual result
        expected: Expected result

    Returns:
        Warning message if precision loss detected, None if acceptable

    Examples:
        >>> precision_loss(sum([0.1] * 10), 1.0)  # doctest: +SKIP
        'Precision loss detected:\\n  Expected: 1.0\\n  Got: 0.9999999999999999\\n  Error: 1.11e-16 (1 ULP)\\n  Recommendation: Use neon.safe.sum_exact() or check operation order'  # noqa: E501
    """
    if got == expected:
        return None

    error = abs(got - expected)

    # Get ULP distance
    try:
        ulp_dist = neon_ulp.diff(got, expected)
    except Exception:
        ulp_dist = None

    # Small error = precision loss
    # Large error = logic bug
    if error > abs(expected) * 0.01:  # >1% error
        return None  # Not a precision issue, likely a logic bug

    ulp_str = f" ({ulp_dist} ULP)" if ulp_dist is not None else ""

    return (
        f"Precision loss detected:\n"
        f"  Expected: {expected}\n"
        f"  Got: {got}\n"
        f"  Error: {error:.2e}{ulp_str}\n"
        f"  Recommendation: Use neon.safe.sum_exact() or check operation order"
    )


# ============================================================================
# Low-Precision Dtype Validation API
# ============================================================================


@dataclass
class SafetyCheck:
    """Result of dtype safety check."""

    safe: bool
    issue: Optional[str]
    message: str
    recommendation: Optional[str]


def safe_for_dtype(x: float, target: str) -> SafetyCheck:
    """Check if value is safe for target dtype.

    Args:
        x: Value to check
        target: Target dtype ('fp32', 'fp16', 'bf16', 'fp8_e4m3', 'fp8_e5m2')

    Returns:
        Safety check result with issue details and recommendations

    Examples:
        >>> check = safe_for_dtype(1e6, target='fp16')
        >>> check.safe
        False
        >>> check.issue
        'overflow'
    """
    if target not in DTYPE_LIMITS:
        raise ValueError(
            f"Unknown dtype '{target}'. Valid options: {list(DTYPE_LIMITS.keys())}"
        )

    limits = DTYPE_LIMITS[target]

    if math.isnan(x) or math.isinf(x):
        return SafetyCheck(
            safe=False,
            issue="invalid",
            message=f"Value is {x} (NaN/Inf not representable)",
            recommendation="Fix NaN/Inf before dtype conversion",
        )

    abs_x = abs(x)

    if abs_x > limits["max"]:
        return SafetyCheck(
            safe=False,
            issue="overflow",
            message=f"Value {x:.2e} would overflow in {target.upper()} (max={limits['max']:.2e})",
            recommendation="Rescale values or use higher-precision dtype",
        )

    if abs_x != 0 and abs_x < limits["min"]:
        return SafetyCheck(
            safe=False,
            issue="underflow",
            message=f"Value {x:.2e} would underflow to 0 in {target.upper()} (min={limits['min']:.2e})",  # noqa: E501
            recommendation="Rescale values or use higher-precision dtype",
        )

    return SafetyCheck(
        safe=True, issue=None, message="Value is safe", recommendation=None
    )


@dataclass
class DTypeReport:
    """Report of dtype conversion safety for a collection."""

    total: int
    safe: int
    overflow: int
    underflow: int
    invalid: int
    recommendation: str


def analyze_for_dtype(values: list[float], target: str) -> DTypeReport:
    """Analyze collection for dtype safety.

    Args:
        values: Collection to analyze
        target: Target dtype ('fp32', 'fp16', 'bf16', 'fp8_e4m3', 'fp8_e5m2')

    Returns:
        Report with counts and recommendations

    Examples:
        >>> report = analyze_for_dtype([1.0, 1e10], target='fp16')
        >>> report.overflow
        1
    """
    overflow = 0
    underflow = 0
    invalid = 0
    safe = 0

    for x in values:
        check = safe_for_dtype(x, target)
        if check.safe:
            safe += 1
        elif check.issue == "overflow":
            overflow += 1
        elif check.issue == "underflow":
            underflow += 1
        elif check.issue == "invalid":
            invalid += 1

    total = len(values)

    # Generate recommendation
    if invalid > 0:
        rec = f"{invalid} values ({invalid/total*100:.1f}%) are NaN/Inf - fix these before conversion"  # noqa: E501
    elif overflow > 0:
        rec = f"{overflow} values ({overflow/total*100:.1f}%) would overflow in {target.upper()}. Use higher-precision dtype or rescale."  # noqa: E501
    elif underflow > total * 0.05:  # >5% underflow
        rec = f"{underflow} values ({underflow/total*100:.1f}%) would underflow in {target.upper()}. Consider rescaling or using BF16."  # noqa: E501
    elif safe == total:
        rec = f"All values safe for {target.upper()} conversion"
    else:
        rec = f"{total - safe} values would have issues in {target.upper()}"

    return DTypeReport(
        total=total,
        safe=safe,
        overflow=overflow,
        underflow=underflow,
        invalid=invalid,
        recommendation=rec,
    )


@dataclass
class DTypeComparison:
    """Comparison of conversion safety across multiple dtypes."""

    results: dict[str, dict[str, Union[int, str]]]
    recommendation: str


def compare_dtypes(values: list[float], targets: list[str]) -> DTypeComparison:
    """Compare value safety across multiple dtypes.

    Args:
        values: Collection to analyze
        targets: List of target dtypes to compare

    Returns:
        Comparison with recommendation on best dtype

    Examples:
        >>> comparison = compare_dtypes([1.0, 1e10], targets=['fp16', 'bf16'])
        >>> 'bf16' in comparison.recommendation.lower()
        True
    """
    results: dict[str, dict[str, Union[int, str]]] = {}

    for dtype in targets:
        report = analyze_for_dtype(values, dtype)

        # Assess precision loss risk
        if report.invalid > 0 or report.overflow > 0:
            risk = "HIGH"
        elif report.underflow > len(values) * 0.05:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        results[dtype] = {
            "overflow": report.overflow,
            "underflow": report.underflow,
            "invalid": report.invalid,
            "precision_loss": risk,
        }

    # Recommend best dtype (fewest issues)
    best = min(results.items(), key=_dtype_comparison_key)

    return DTypeComparison(
        results=results, recommendation=f"Use {best[0].upper()} for best balance"
    )
