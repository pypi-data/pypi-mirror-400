# Low-Precision Float Support - Future Direction

**Based on:** NVIDIA engineer feedback (Priya Sharma)
**Target:** v1.2 or v1.3 (after v1.1 ships and we have user data)
**Rationale:** FP8 training is becoming standard for LLMs - validation tools will be needed

---

## The Opportunity

**Context:** Modern AI training uses mixed-precision:
- **FP32** (float) - 32 bits, ±3.4e38 range, ~7 decimal digits
- **FP16** (half) - 16 bits, ±65,504 range, ~3 decimal digits
- **BF16** (bfloat16) - 16 bits, ±3.4e38 range (same as FP32), ~2 decimal digits
- **FP8** (E4M3/E5M2) - 8 bits, various formats, becoming standard for LLM training

**Problem:** Converting FP32 weights to FP8 can cause:
- **Overflow** - Values > max representable value → Inf
- **Underflow** - Values < min representable value → 0 (or denormal)
- **Precision loss** - Rounding errors accumulate

**Current solution:** Trial and error, manual inspection, lots of debugging

**Neon's potential:** Validate values before conversion, predict issues

---

## Proposed API (v1.2+)

### Extend `neon.inspect` module

```python
from neon import inspect as ni

# Check if a value is safe for a target dtype
result = ni.safe_for_dtype(1e-20, target='fp16')
print(result)
# SafetyCheck(
#   safe=False,
#   issue='underflow',
#   message='Value 1e-20 would underflow to 0 in FP16 (min=6.1e-5)',
#   recommendation='Use BF16 (supports down to 1.2e-38) or rescale values'
# )

# Batch check before model conversion
weights = model.get_weights().flatten()
report = ni.analyze_for_dtype(weights, target='fp8_e4m3')
print(report)
# DTypeReport(
#   total=10000,
#   safe=9850,
#   overflow=0,
#   underflow=150,
#   precision_loss=8500,
#   recommendation='150 values (1.5%) would underflow to zero in FP8_E4M3.
#                   Consider rescaling layer outputs or using FP16 for this layer.'
# )

# Compare precision loss across dtypes
comparison = ni.compare_dtypes(weights, targets=['fp16', 'bf16', 'fp8_e4m3'])
print(comparison)
# DTypeComparison(
#   fp16={'overflow': 5, 'underflow': 200, 'precision_loss': 'HIGH'},
#   bf16={'overflow': 0, 'underflow': 150, 'precision_loss': 'MEDIUM'},
#   fp8_e4m3={'overflow': 0, 'underflow': 500, 'precision_loss': 'HIGH'},
#   recommendation='Use BF16 for best balance of range and precision'
# )
```

---

## Float Format Reference (for implementation)

### FP32 (IEEE 754 float)
- **Bits:** 1 sign, 8 exponent, 23 mantissa
- **Range:** ±3.4e38
- **Precision:** ~7 decimal digits
- **Min normal:** 1.175494e-38
- **Min denormal:** 1.401298e-45

### FP16 (IEEE 754 half)
- **Bits:** 1 sign, 5 exponent, 10 mantissa
- **Range:** ±65,504
- **Precision:** ~3 decimal digits
- **Min normal:** 6.104e-5
- **Min denormal:** 5.96e-8

### BF16 (Google Brain Float)
- **Bits:** 1 sign, 8 exponent, 7 mantissa
- **Range:** ±3.4e38 (same as FP32)
- **Precision:** ~2 decimal digits
- **Min normal:** 1.175494e-38 (same as FP32)
- **Min denormal:** 1.401298e-45 (same as FP32)

### FP8 E4M3 (NVIDIA H100/H200)
- **Bits:** 1 sign, 4 exponent, 3 mantissa
- **Range:** ±448
- **Precision:** ~1 decimal digit
- **Min normal:** ~0.0001
- **No denormals** (implementation detail)

### FP8 E5M2 (Alternative format)
- **Bits:** 1 sign, 5 exponent, 2 mantissa
- **Range:** ±57,344
- **Precision:** ~0.5 decimal digits
- **Used for gradients** (wider range, less precision)

---

## Implementation Strategy

### Phase 1: Detection (~50 lines)

```python
# Internal constants
DTYPE_LIMITS = {
    'fp32': {'min': 1.175494e-38, 'max': 3.4028235e38},
    'fp16': {'min': 6.104e-5, 'max': 65504.0},
    'bf16': {'min': 1.175494e-38, 'max': 3.4028235e38},
    'fp8_e4m3': {'min': 0.001953125, 'max': 448.0},  # Approximate
    'fp8_e5m2': {'min': 0.0001525878, 'max': 57344.0},  # Approximate
}

def safe_for_dtype(x: float, target: str) -> SafetyCheck:
    """Check if value is safe for target dtype."""
    limits = DTYPE_LIMITS[target]

    if math.isnan(x) or math.isinf(x):
        return SafetyCheck(
            safe=False,
            issue='invalid',
            message=f'Value is {x} (NaN/Inf not representable)',
            recommendation='Fix NaN/Inf before dtype conversion'
        )

    abs_x = abs(x)

    if abs_x > limits['max']:
        return SafetyCheck(
            safe=False,
            issue='overflow',
            message=f'Value {x:.2e} would overflow in {target.upper()} (max={limits["max"]:.2e})',
            recommendation=f'Rescale values or use higher-precision dtype'
        )

    if abs_x != 0 and abs_x < limits['min']:
        return SafetyCheck(
            safe=False,
            issue='underflow',
            message=f'Value {x:.2e} would underflow to 0 in {target.upper()} (min={limits["min"]:.2e})',
            recommendation=f'Rescale values or use higher-precision dtype'
        )

    return SafetyCheck(safe=True, issue=None, message='Value is safe', recommendation=None)
```

### Phase 2: Batch Analysis (~100 lines)

```python
def analyze_for_dtype(values: List[float], target: str) -> DTypeReport:
    """Analyze collection for dtype safety."""
    overflow = 0
    underflow = 0
    safe = 0

    for x in values:
        check = safe_for_dtype(x, target)
        if check.safe:
            safe += 1
        elif check.issue == 'overflow':
            overflow += 1
        elif check.issue == 'underflow':
            underflow += 1

    total = len(values)

    # Generate recommendation
    if overflow > 0:
        rec = f'{overflow} values ({overflow/total*100:.1f}%) would overflow in {target.upper()}. Use higher-precision dtype or rescale.'
    elif underflow > total * 0.05:  # >5% underflow
        rec = f'{underflow} values ({underflow/total*100:.1f}%) would underflow in {target.upper()}. Consider rescaling or using BF16.'
    elif safe == total:
        rec = f'All values safe for {target.upper()} conversion'
    else:
        rec = f'{total - safe} values would have issues in {target.upper()}'

    return DTypeReport(
        total=total,
        safe=safe,
        overflow=overflow,
        underflow=underflow,
        recommendation=rec
    )
```

### Phase 3: Cross-dtype Comparison (~50 lines)

```python
def compare_dtypes(values: List[float], targets: List[str]) -> DTypeComparison:
    """Compare value safety across multiple dtypes."""
    results = {}

    for dtype in targets:
        report = analyze_for_dtype(values, dtype)

        # Assess precision loss risk
        if report.overflow > 0:
            risk = 'HIGH'
        elif report.underflow > len(values) * 0.05:
            risk = 'MEDIUM'
        else:
            risk = 'LOW'

        results[dtype] = {
            'overflow': report.overflow,
            'underflow': report.underflow,
            'precision_loss': risk
        }

    # Recommend best dtype
    best = min(results.items(), key=lambda x: (
        x[1]['overflow'],
        x[1]['underflow'],
        {'HIGH': 2, 'MEDIUM': 1, 'LOW': 0}[x[1]['precision_loss']]
    ))

    return DTypeComparison(
        results=results,
        recommendation=f'Use {best[0].upper()} for best balance'
    )
```

---

## Real-World Use Cases

### Use Case 1: Pre-quantization Validation

```python
from neon import inspect as ni
import torch

# Before converting model to FP8 for deployment
model = torch.load('my_llm_70b.pt')

for name, param in model.named_parameters():
    weights = param.detach().cpu().numpy().flatten().tolist()

    report = ni.analyze_for_dtype(weights, target='fp8_e4m3')

    if report.overflow > 0 or report.underflow > 100:
        print(f'WARNING: Layer {name}')
        print(f'  {report}')
        print(f'  Consider keeping this layer in FP16')
```

**Output:**
```
WARNING: Layer transformer.layers.47.mlp.gate_proj
  DTypeReport(total=50000, safe=48500, overflow=0, underflow=1500)
  1500 values (3%) would underflow in FP8_E4M3.
  Consider rescaling layer outputs or using FP16 for this layer.
```

### Use Case 2: Choosing Mixed-Precision Strategy

```python
from neon import inspect as ni

activations = capture_activations(model, sample_input)

# Should we use FP16, BF16, or FP8?
comparison = ni.compare_dtypes(activations, targets=['fp16', 'bf16', 'fp8_e4m3'])
print(comparison)
```

**Output:**
```
DTypeComparison(
  fp16={'overflow': 250, 'underflow': 50, 'precision_loss': 'HIGH'},
  bf16={'overflow': 0, 'underflow': 50, 'precision_loss': 'MEDIUM'},
  fp8_e4m3={'overflow': 0, 'underflow': 500, 'precision_loss': 'HIGH'},
  recommendation='Use BF16 for best balance of range and precision'
)
```

### Use Case 3: Debugging Quantization Errors

```python
from neon import inspect as ni

# Model works in FP32, breaks in FP8 - why?
fp32_weights = load_weights('model_fp32.pt')
fp8_weights = load_weights('model_fp8.pt')  # After quantization

for i, (w32, w8) in enumerate(zip(fp32_weights, fp8_weights)):
    loss = ni.precision_loss(w8, w32)
    if loss:
        print(f'Layer {i}: {loss}')
```

**Output:**
```
Layer 47: Precision loss detected:
  Expected: 0.0001234 (FP32)
  Got: 0.0 (FP8)
  Error: 1.23e-4 (underflow)
  Recommendation: Value underflowed in FP8 - rescale this layer's weights
```

---

## Why This Is Valuable

### Problem Neon Solves

**Current workflow for FP8 conversion:**
1. Convert model to FP8
2. Run inference
3. Notice accuracy degradation
4. **Manually inspect weights** to find problematic layers
5. Trial-and-error rescaling
6. Repeat

**With Neon:**
1. **Validate before conversion** - `analyze_for_dtype(weights, 'fp8_e4m3')`
2. Identify problematic layers upfront
3. Apply targeted fixes (rescale specific layers, keep some in FP16)
4. Convert with confidence

**Time saved:** Hours/days of debugging → Minutes of validation

### Market Timing

**FP8 is exploding:**
- NVIDIA H100/H200 GPUs have native FP8 support
- Meta LLaMA 3.1 uses FP8 for some layers
- Mixtral, Gemini, Claude all experimenting with FP8
- Every AI lab is trying to reduce inference cost

**Neon's angle:** "Validate your FP8 quantization before deploying"

**Competitors:** None. This is a gap.
- PyTorch has `torch.quantization` but no validation tools
- ONNX has quantization but no pre-flight checks
- No standalone library for dtype safety analysis

---

## Implementation Plan (v1.2 or v1.3)

### Prerequisites
- ✅ v1.1.0 shipped with basic `neon.inspect`
- ✅ User feedback collected (6 months)
- ✅ Demand validated (GitHub issues requesting low-precision support)

### Scope (~200 lines, 8-10 hours)
1. Add dtype limits reference (~20 lines)
2. Implement `safe_for_dtype()` (~50 lines)
3. Implement `analyze_for_dtype()` (~50 lines)
4. Implement `compare_dtypes()` (~50 lines)
5. Add dataclasses (`SafetyCheck`, `DTypeReport`, `DTypeComparison`) (~30 lines)
6. Write tests (~100 lines)
7. Document in README (~50 lines)

### Testing
```python
class TestSafeForDtype:
    def test_fp16_overflow(self):
        check = ni.safe_for_dtype(1e6, target='fp16')
        assert not check.safe
        assert check.issue == 'overflow'

    def test_fp16_underflow(self):
        check = ni.safe_for_dtype(1e-10, target='fp16')
        assert not check.safe
        assert check.issue == 'underflow'

    def test_bf16_range(self):
        # BF16 has same range as FP32
        check = ni.safe_for_dtype(1e20, target='bf16')
        assert check.safe

    def test_fp8_limits(self):
        check = ni.safe_for_dtype(500, target='fp8_e4m3')
        assert not check.safe  # Max is 448
```

---

## Marketing Angle

### Positioning

**Headline:** "Validate FP8 quantization before you break production"

**Value Props:**
- ✅ **Prevent accuracy loss** - Identify problematic layers before deployment
- ✅ **Save debugging time** - Hours → Minutes
- ✅ **Zero dependencies** - Works without PyTorch/ONNX
- ✅ **Educational** - Learn which layers need higher precision

**Target Audience:**
- AI engineers deploying LLMs to production
- ML engineers optimizing inference cost
- Researchers experimenting with mixed-precision training
- Anyone converting models to FP8/FP16

**Testimonial We Want:**
> "Neon caught FP8 underflow in our 70B model's final layer before we deployed to prod. Saved us a week of debugging customer complaints."
> - ML Engineer at [AI Startup]

---

## Decision Point

**Should we build this for v1.2?**

**Arguments FOR:**
- ✅ Clear market need (FP8 training is growing)
- ✅ No competitors (unique positioning)
- ✅ Small scope (~200 lines, 8-10 hours)
- ✅ Stays zero-dependency (just more constants)
- ✅ Natural extension of `neon.inspect`

**Arguments AGAINST:**
- ❌ Speculative - users haven't asked for it yet
- ❌ Niche - only useful for AI deployment engineers
- ❌ Requires domain expertise (FP8 formats are evolving)
- ❌ Maintenance burden (need to track new formats like FP4)

**Recommendation:**
**WAIT.** Ship v1.1 first. If we get GitHub issues like:
- "Can Neon check if values are safe for FP16?"
- "How do I validate quantization?"
- "Add support for BF16 validation"

Then build this for v1.2. Don't build it speculatively.

---

## Appendix: Why This Is Better Than Existing Tools

### vs. PyTorch Quantization
```python
# PyTorch: Requires full model, complex API
from torch.quantization import quantize_dynamic
quantized_model = quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
# If it breaks, hard to debug why

# Neon: Simple validation, clear feedback
report = ni.analyze_for_dtype(weights, 'fp8_e4m3')
print(report.recommendation)
# Tells you exactly what's wrong and how to fix it
```

### vs. ONNX Runtime
```python
# ONNX: Need to export model, run optimizer, check metrics
import onnxruntime as ort
# Complex pipeline, opaque errors

# Neon: Direct validation
comparison = ni.compare_dtypes(weights, ['fp16', 'bf16', 'fp8_e4m3'])
# Clear recommendation on which dtype to use
```

### vs. Manual Inspection
```python
# Manual: Print statements, trial-and-error
print(f'Min: {weights.min()}, Max: {weights.max()}')
# "Hmm, is -1e-10 safe for FP16? Let me check Wikipedia..."

# Neon: Automated validation
check = ni.safe_for_dtype(weights.min(), 'fp16')
print(check.message)
# "Value -1e-10 would underflow to 0 in FP16 (min=6.1e-5)"
```

---

**Bottom line:** This is a compelling feature for v1.2+, but we should validate demand first. Ship v1.1, collect feedback, then decide.
