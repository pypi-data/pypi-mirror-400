# neon.inspect - Production Float Debugging

**Target User:** Developer debugging a production issue at 2am
**Goal:** Answer "Why is my calculation returning NaN/wrong values?" in <30 seconds

---

## Design Principle: Actionable, Not Educational

**Bad (Educational):**
```python
info = inspect.analyze_float(x)
print(f"Mantissa: {info.mantissa_hex}")  # Who cares?
```

**Good (Actionable):**
```python
issues = inspect.check(x)
if issues:
    print(issues)  # "Value is denormal - precision loss likely"
```

---

## API Design (Production-Focused)

### 1. Quick Health Check

```python
from neon import inspect as ni

# Single value check - returns issues or None
issues = ni.check(my_value)
if issues:
    print(f"Warning: {issues}")
    # "Value 1e-400 is denormal - will lose precision in arithmetic"
    # "Value is NaN - check for division by zero or log of negative"
    # "Value is Inf - check for overflow in multiplication"

# Batch check - returns summary
summary = ni.check_many(my_list)
print(summary)
# "Found 15 denormals (3%), 2 NaNs, 0 Infs - precision risk: MEDIUM"
```

### 2. Comparison Debugging

```python
# Why aren't these equal?
a = 0.1 + 0.2
b = 0.3
result = ni.compare_debug(a, b)
print(result)
# "Values differ by 5.551115e-17 (0.000000018%)
#  ULP distance: 1
#  Recommendation: Use neon.compare.near() with default tolerances"

# Why is this division failing?
result = ni.div_debug(numerator, denominator)
print(result)
# "Division 1.0 / 1e-320 would overflow to Inf
#  Denominator is denormal - precision loss
#  Recommendation: Use neon.safe.div() with appropriate default"
```

### 3. Collection Analysis

```python
# Analyze array/list for issues
report = ni.analyze(weights)
print(report)
# Analysis of 10,000 values:
#   Normal: 9,750 (97.5%)
#   Denormal: 245 (2.45%) ⚠️
#   Zero: 5 (0.05%)
#   NaN: 0
#   Inf: 0
#
#   ULP spread: 2.2e-16 to 1.8e-12
#   Precision risk: LOW
#
#   Issues:
#   - 2.45% denormals may cause precision loss
#
#   Recommendations:
#   - Use neon.clamp.to_zero(x, abs_tol=1e-300) to clean denormals
```

### 4. Precision Loss Detection

```python
# Did this operation lose precision?
original = [0.1] * 10
summed = sum(original)  # Naive sum
exact = neon.safe.sum_exact(original)

loss = ni.precision_loss(summed, exact)
print(loss)
# "Precision loss detected:
#  Expected: 1.0
#  Got: 0.9999999999999999
#  Error: 1.1e-16 (1 ULP)
#  Recommendation: Use neon.safe.sum_exact() for better precision"
```

---

## Implementation (Simplified, Production-Ready)

### Core Functions

```python
"""Float debugging for production systems."""

import math
from typing import Optional, List, Literal
from dataclasses import dataclass

__all__ = [
    "check",
    "check_many",
    "compare_debug",
    "div_debug",
    "analyze",
    "precision_loss",
]

# Simple categorization (internal helper)
def _categorize(x: float) -> Literal['zero', 'denormal', 'normal', 'nan', 'inf']:
    """Categorize float for internal use."""
    if math.isnan(x):
        return 'nan'
    if math.isinf(x):
        return 'inf'
    if x == 0.0:
        return 'zero'
    # Denormals are smaller than ~2.2e-308 (minimum normal)
    if abs(x) < 2.225073858507201e-308:
        return 'denormal'
    return 'normal'


def check(x: float) -> Optional[str]:
    """Quick health check - returns warning message or None.

    Use this in production to catch problematic floats.

    Returns:
        Warning message if issue found, None if value is safe

    Examples:
        >>> check(1.0)

        >>> check(1e-400)
        'Value 1e-400 is denormal - will lose precision in arithmetic'

        >>> check(float('nan'))
        'Value is NaN - check for division by zero or invalid operation'
    """
    cat = _categorize(x)

    if cat == 'nan':
        return "Value is NaN - check for division by zero or invalid operation"

    if cat == 'inf':
        sign = "+" if x > 0 else "-"
        return f"Value is {sign}Inf - check for overflow or division by zero"

    if cat == 'denormal':
        return f"Value {x:.2e} is denormal - will lose precision in arithmetic"

    # Normal and zero are fine
    return None


def check_many(values: List[float]) -> str:
    """Batch health check - returns summary string.

    Use this to quickly scan collections for issues.

    Examples:
        >>> check_many([1.0, 2.0, 3.0])
        'All 3 values are normal - no issues detected'

        >>> check_many([1.0, 1e-400, float('nan')])
        'Found 1 denormal (33%), 1 NaN - precision risk: HIGH'
    """
    counts = {'normal': 0, 'denormal': 0, 'zero': 0, 'nan': 0, 'inf': 0}

    for x in values:
        counts[_categorize(x)] += 1

    total = len(values)

    # All good?
    if counts['nan'] == 0 and counts['inf'] == 0 and counts['denormal'] == 0:
        return f"All {total} values are normal - no issues detected"

    # Build issue summary
    issues = []
    if counts['denormal'] > 0:
        pct = (counts['denormal'] / total) * 100
        issues.append(f"{counts['denormal']} denormal ({pct:.1f}%)")

    if counts['nan'] > 0:
        issues.append(f"{counts['nan']} NaN")

    if counts['inf'] > 0:
        issues.append(f"{counts['inf']} Inf")

    # Risk assessment
    risk = "LOW"
    if counts['nan'] > 0 or counts['inf'] > 0:
        risk = "HIGH"
    elif (counts['denormal'] / total) > 0.05:  # >5% denormals
        risk = "MEDIUM"

    return f"Found {', '.join(issues)} - precision risk: {risk}"


def compare_debug(a: float, b: float) -> str:
    """Debug why two floats aren't equal.

    Use this when a == b fails but you think they should be equal.

    Examples:
        >>> compare_debug(0.1 + 0.2, 0.3)
        'Values differ by 5.551115e-17 (0.000000018%)\\nULP distance: 1\\nRecommendation: Use neon.compare.near() with default tolerances'
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
    from neon import ulp
    try:
        ulp_dist = ulp.diff(a, b)
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

    Use this when a / b fails or gives unexpected results.

    Examples:
        >>> div_debug(1.0, 0.0)
        'Division by zero detected\\nRecommendation: Use neon.safe.div() with appropriate default'

        >>> div_debug(1.0, 1e-320)
        'Denominator 1e-320 is denormal - precision loss\\nResult would overflow to Inf\\nRecommendation: Use neon.safe.div() with default=0.0'
    """
    issues = []

    # Check denominator
    b_issue = check(b)
    if b_issue:
        issues.append(f"Denominator issue: {b_issue}")

    # Check for zero
    if b == 0:
        issues.append("Division by zero detected")
        return "\n".join(issues) + "\nRecommendation: Use neon.safe.div() with appropriate default"

    # Try division
    try:
        result = a / b
        result_issue = check(result)
        if result_issue:
            issues.append(f"Result issue: {result_issue}")
    except Exception as e:
        issues.append(f"Division failed: {e}")

    if issues:
        return "\n".join(issues) + "\nRecommendation: Use neon.safe.div() with appropriate default"

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
    precision_risk: Literal['LOW', 'MEDIUM', 'HIGH']
    issues: List[str]
    recommendations: List[str]

    def __str__(self) -> str:
        lines = [
            f"Analysis of {self.total} values:",
            f"  Normal: {self.normal} ({self.normal/self.total*100:.2f}%)",
            f"  Denormal: {self.denormal} ({self.denormal/self.total*100:.2f}%)" + (" ⚠️" if self.denormal > 0 else ""),
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


def analyze(values: List[float]) -> AnalysisReport:
    """Comprehensive analysis for production debugging.

    Use this to understand what's wrong with a collection of floats.

    Examples:
        >>> report = analyze([1.0, 1e-400, 2.0, float('nan')])
        >>> print(report)
        Analysis of 4 values:
          Normal: 2 (50.00%)
          Denormal: 1 (25.00%) ⚠️
          Zero: 0 (0.00%)
          NaN: 1 ❌
          Inf: 0

          Precision risk: HIGH

          Issues:
          - 25.00% of values are denormal
          - 1 NaN value detected

          Recommendations:
          - Use neon.clamp.to_zero() to clean denormals
          - Check for invalid operations causing NaN
    """
    counts = {'normal': 0, 'denormal': 0, 'zero': 0, 'nan': 0, 'inf': 0}

    for x in values:
        counts[_categorize(x)] += 1

    total = len(values)

    # Assess risk
    risk = "LOW"
    if counts['nan'] > 0 or counts['inf'] > 0:
        risk = "HIGH"
    elif (counts['denormal'] / total) > 0.05:  # >5%
        risk = "MEDIUM"

    # Identify issues
    issues = []
    if counts['denormal'] > 0:
        pct = (counts['denormal'] / total) * 100
        issues.append(f"{pct:.2f}% of values are denormal")

    if counts['nan'] > 0:
        issues.append(f"{counts['nan']} NaN value(s) detected")

    if counts['inf'] > 0:
        issues.append(f"{counts['inf']} Inf value(s) detected")

    # Generate recommendations
    recommendations = []
    if counts['denormal'] > 0:
        recommendations.append("Use neon.clamp.to_zero() to clean denormals")

    if counts['nan'] > 0:
        recommendations.append("Check for invalid operations causing NaN (division by zero, log of negative, etc)")

    if counts['inf'] > 0:
        recommendations.append("Check for overflow in multiplication or division by near-zero")

    return AnalysisReport(
        total=total,
        normal=counts['normal'],
        denormal=counts['denormal'],
        zero=counts['zero'],
        nan=counts['nan'],
        inf=counts['inf'],
        precision_risk=risk,
        issues=issues,
        recommendations=recommendations
    )


def precision_loss(got: float, expected: float) -> Optional[str]:
    """Detect if an operation lost precision.

    Use this to check if your calculation is accurate.

    Returns:
        Warning message if precision loss detected, None if acceptable

    Examples:
        >>> precision_loss(sum([0.1] * 10), 1.0)
        'Precision loss detected:\\n  Expected: 1.0\\n  Got: 0.9999999999999999\\n  Error: 1.11e-16 (1 ULP)\\n  Recommendation: Use neon.safe.sum_exact() for better precision'
    """
    if got == expected:
        return None

    error = abs(got - expected)

    # Get ULP distance
    from neon import ulp
    try:
        ulp_dist = ulp.diff(got, expected)
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
```

---

## Usage in Production

### Scenario 1: "Why is my calculation returning NaN?"

```python
from neon import inspect as ni

def calculate_metric(values):
    result = sum(values) / len(values)

    # Quick check
    issue = ni.check(result)
    if issue:
        logger.error(f"Calculation failed: {issue}")
        logger.error(f"Input analysis: {ni.check_many(values)}")
        return None

    return result
```

### Scenario 2: "Why aren't these values equal?"

```python
from neon import inspect as ni

a = expensive_calculation()
b = reference_value

if a != b:
    logger.warning(ni.compare_debug(a, b))
```

### Scenario 3: "Why did my division fail?"

```python
from neon import inspect as ni, safe

result = numerator / denominator  # ZeroDivisionError!

# Debug what went wrong
logger.error(ni.div_debug(numerator, denominator))

# Fix with safe division
result = safe.div(numerator, denominator, default=0.0)
```

### Scenario 4: "Are my ML weights corrupted?"

```python
from neon import inspect as ni

weights = model.get_weights()
report = ni.analyze(weights)

if report.precision_risk != 'LOW':
    logger.warning(f"Weight health check:\n{report}")
    # Maybe reload checkpoint or re-initialize
```

---

## Tests (Production-Focused)

```python
class TestCheck:
    def test_normal_values_ok(self):
        assert ni.check(1.0) is None
        assert ni.check(42.5) is None

    def test_denormal_warning(self):
        result = ni.check(1e-400)
        assert "denormal" in result.lower()
        assert "precision" in result.lower()

    def test_nan_warning(self):
        result = ni.check(float('nan'))
        assert "NaN" in result
        assert "invalid" in result.lower()

class TestCheckMany:
    def test_all_normal(self):
        result = ni.check_many([1.0, 2.0, 3.0])
        assert "no issues" in result.lower()

    def test_with_issues(self):
        result = ni.check_many([1.0, 1e-400, float('nan')])
        assert "denormal" in result.lower()
        assert "NaN" in result
        assert "HIGH" in result

class TestCompareDebug:
    def test_float_precision_issue(self):
        result = ni.compare_debug(0.1 + 0.2, 0.3)
        assert "differ" in result.lower()
        assert "near()" in result  # Recommends neon.compare.near()

    def test_exact_equal(self):
        result = ni.compare_debug(1.0, 1.0)
        assert "exactly equal" in result.lower()
```

---

## Documentation (Production-Focused)

### README snippet

```markdown
### Float Debugging (v1.1+)

When things go wrong in production, `neon.inspect` helps you debug quickly:

```python
from neon import inspect as ni

# Quick health check
if issue := ni.check(my_value):
    logger.error(f"Float issue: {issue}")

# Why aren't these equal?
print(ni.compare_debug(a, b))

# Analyze collection for issues
report = ni.analyze(weights)
if report.precision_risk == 'HIGH':
    logger.warning(report)
```

**Use cases:**
- Debugging NaN/Inf in production
- Validating ML model weights
- Understanding float comparison failures
- Detecting precision loss in calculations
```

---

**This is way more useful than teaching IEEE 754 structure!**
