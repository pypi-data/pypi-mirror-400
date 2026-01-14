# Neon AI Roadmap: From CSV Tool to LLM Training Essential

**Vision:** Transform Neon from "I help you clean your CSV data" to "I stop your 70B parameter LLM training run from crashing after 2 weeks."

## The Gap

Current Neon (v1.0.0) handles scalar floating-point operations beautifully, but AI/ML teams need:
- **Vectorized operations** on millions of values at C++/CUDA speed
- **Gradient-aware logic** that doesn't break backpropagation
- **Proactive debugging** that catches instability before it becomes NaN
- **Low-precision support** for FP16/BF16/FP8 training
- **JIT compatibility** for torch.compile, jax.jit, numba

---

## Phase 1: Tensor-First Evolution (v1.1.0)

**Goal:** Make Neon work on entire arrays, not just scalars.

### 1.1 NumPy Integration (`neon.numpy`)

**The Problem:**
```python
# Current: AI teams write verbose boilerplate
mask = denominator != 0
result = np.where(mask, numerator / denominator, 0.0)
# 3 lines, creates intermediate arrays, hard to read
```

**The Neon Way:**
```python
import neon.numpy as nnp
result = nnp.div_safe(numerator, denominator, default=0.0)
# 1 line, optimized, clear intent
```

**Deliverables:**
- [ ] `neon.numpy.div_safe(a, b, *, default=None, zero_tol=0.0)` - Vectorized safe division
- [ ] `neon.numpy.near(a, b, *, rel_tol=1e-9, abs_tol=1e-9)` - Vectorized comparison (returns bool array)
- [ ] `neon.numpy.clamp_to_zero(x, *, abs_tol=1e-9)` - Vectorized zero-snapping
- [ ] `neon.numpy.sanitize(x, *, nan_value=0.0, inf_value=None)` - Replace NaN/inf in arrays
- [ ] Performance: Match or beat hand-written NumPy code (C-level speed)

**Why This Matters:**
- AI teams process millions of values per forward pass
- Python loops are 100-1000x slower than vectorized NumPy
- This becomes the foundation for PyTorch/JAX support

---

### 1.2 PyTorch Integration (`neon.torch`)

**The Problem:**
```python
# Naive masking breaks gradients
mask = (y != 0).float()
z = mask * (x / (y + 1e-10))  # Gradients are wrong!
```

**The Neon Way:**
```python
import neon.torch as ntorch
z = ntorch.div_safe(x, y, default=0.0)  # Gradients flow correctly
```

**Deliverables:**
- [ ] `neon.torch.div_safe()` - Gradient-aware safe division
- [ ] `neon.torch.clamp_safe()` - Differentiable clamping (uses `torch.where` internally)
- [ ] `neon.torch.near()` - Tolerance-based comparison (returns bool tensor)
- [ ] Full autograd support - gradients must flow correctly through all operations
- [ ] CUDA support - must work on GPU tensors
- [ ] torch.jit.script compatibility - can be compiled for performance

**Critical Test:**
```python
x = torch.tensor([1.0, 2.0], requires_grad=True)
y = torch.tensor([2.0, 0.0], requires_grad=True)
z = ntorch.div_safe(x, y, default=0.0)
z.sum().backward()
# x.grad and y.grad must be mathematically correct
```

---

### 1.3 JAX Integration (`neon.jax`)

**The Problem:** JAX requires pure functions that are jit-traceable and auto-vectorizable.

**The Neon Way:**
```python
import neon.jax as njax

@jax.jit
def loss_fn(params, x, y):
    pred = model(params, x)
    error = njax.div_safe(pred - y, y, default=0.0)
    return error.mean()
```

**Deliverables:**
- [ ] `neon.jax.div_safe()` - jit-compatible safe division
- [ ] `neon.jax.near()` - jit-compatible comparison
- [ ] Full `jax.grad` support - differentiable everywhere
- [ ] `jax.vmap` compatibility - automatic vectorization
- [ ] `jax.jit` compatibility - compilable to XLA

---

## Phase 2: Differentiable "Soft" Logic (v1.2.0)

**Goal:** Provide gradient-friendly approximations of hard logic.

### 2.1 Soft Clamping

**The Problem:**
```python
# Hard clamp kills gradients outside [min, max]
x_clamped = torch.clamp(x, min=0, max=1)
# If x = -5, gradient is ZERO (dead neuron)
```

**The Neon Way:**
```python
import neon.torch as ntorch
x_smooth = ntorch.soft_clamp(x, min=0, max=1, beta=10.0)
# Gradients flow even when x is outside bounds
# Uses LogSumExp: soft_max ≈ β^(-1) * log(1 + exp(β*(x-max)))
```

**Deliverables:**
- [ ] `soft_clamp(x, min, max, beta)` - Smooth approximation of clamp using LogSumExp
- [ ] `soft_relu(x, beta)` - Smooth ReLU that doesn't kill negative gradients
- [ ] Tunable `beta` parameter - controls smoothness vs. approximation quality
- [ ] Backward pass verification - test gradient flow in extreme cases

**Use Case:** Prevent gradient death in constrained optimization problems.

---

### 2.2 Soft Comparisons

**The Problem:**
```python
# Hard comparison: not differentiable
is_near = (abs(a - b) < tol).float()  # Gradient is zero everywhere
```

**The Neon Way:**
```python
import neon.torch as ntorch
nearness = ntorch.soft_near(a, b, rel_tol=1e-3, temperature=0.1)
# Returns float [0.0, 1.0] representing "degree of nearness"
# Uses sigmoid: σ((tol - |a-b|) / temperature)
```

**Deliverables:**
- [ ] `soft_near(a, b, *, rel_tol, abs_tol, temperature)` - Differentiable nearness score
- [ ] `soft_compare(a, b, temperature)` - Returns continuous value in [-1, 1]
- [ ] Use in loss functions - enable "approximately equal" constraints in training

---

## Phase 3: NaN Hunter - Killer Debugging (v1.3.0)

**Goal:** Diagnose numerical instability BEFORE it becomes NaN.

### 3.1 Instability Monitor

**The Problem:**
```python
# Current debugging experience
for epoch in range(100):
    loss = train_step(model, data)
    if math.isnan(loss):
        print("NaN detected!")  # Too late! Which layer? Which operation?
```

**The Neon Way:**
```python
import neon.torch as ntorch

with ntorch.monitor(break_on_instability=True, max_ulp_drift=1000) as mon:
    for epoch in range(100):
        loss = train_step(model, data)

# Crashes with detailed report:
# "Epoch 42, Layer 'transformer.layer3.attention':
#  - Operation 'SafeDiv' at line 156
#  - Denominator near-zero detected: min=1e-9, mean=0.003
#  - Would cause precision loss > 1000 ULPs
#  - Suggested fix: increase epsilon from 1e-10 to 1e-6"
```

**Deliverables:**
- [ ] `neon.torch.monitor()` - Context manager that hooks into PyTorch autograd
- [ ] Pre-NaN detection - flag operations before they produce NaN/inf
- [ ] ULP drift tracking - measure precision loss across operations
- [ ] Layer attribution - identify which model layer caused instability
- [ ] Actionable suggestions - recommend epsilon values, tolerances
- [ ] Performance overhead: <5% in debug mode, 0% when disabled

**Technical Approach:**
- Register forward/backward hooks on tensors
- Check for near-zero denominators, near-overflow multiplications
- Use Neon's ULP logic to detect precision loss
- Build execution graph to attribute errors to source code

---

### 3.2 Precision Profiler

**The Problem:** "Why is my model less accurate in FP16 than FP32?"

**The Neon Way:**
```python
import neon.torch as ntorch

with ntorch.precision_profile(target_dtype=torch.float16) as prof:
    output = model(input)

print(prof.report())
# Output:
# Layer 'attention.softmax': 15% of values will underflow in FP16
# Layer 'feedforward.gelu': 3% of gradients will overflow in FP16
# Recommendation: Use FP32 for attention.softmax, FP16 elsewhere (mixed precision)
```

**Deliverables:**
- [ ] Analyze FP32 tensors and predict behavior in FP16/BF16/FP8
- [ ] Detect underflow/overflow zones before casting
- [ ] Per-layer recommendations for mixed precision training
- [ ] Integration with `torch.amp` (automatic mixed precision)

---

## Phase 4: Low-Precision Safety (v1.4.0)

**Goal:** Make Neon's tolerances work correctly for FP16/BF16/FP8.

### 4.1 Precision-Aware Tolerances

**The Problem:**
```python
# FP32 tolerance doesn't work for FP16
neon.compare.near(a, b, rel_tol=1e-9)  # Meaningless! FP16 precision is ~1e-3
```

**The Neon Way:**
```python
import neon.fp16 as n16
n16.near(a, b)  # Uses rel_tol=1e-3, abs_tol=1e-4 (tuned for FP16)

import neon.bfloat16 as nbf16
nbf16.near(a, b)  # Uses rel_tol=1e-2, abs_tol=1e-3 (tuned for BF16)
```

**Deliverables:**
- [ ] `neon.fp16` module - FP16-specific tolerances
- [ ] `neon.bfloat16` module - BF16-specific tolerances
- [ ] `neon.fp8` module - FP8-specific tolerances (E4M3 and E5M2 variants)
- [ ] Auto-detect dtype and adjust tolerances
- [ ] Research-backed defaults based on precision analysis

**Reference Tolerances:**
- FP32: `rel_tol=1e-9, abs_tol=1e-9` (current defaults)
- FP16: `rel_tol=1e-3, abs_tol=1e-4` (3 decimal digits precision)
- BF16: `rel_tol=1e-2, abs_tol=1e-3` (2 decimal digits precision)
- FP8-E4M3: `rel_tol=1e-1, abs_tol=1e-2` (1 decimal digit precision)

---

### 4.2 Denormal Detection

**The Problem:** Denormals (subnormals) behave differently and can be 100x slower on some hardware.

**Deliverables:**
- [ ] `neon.analyze_precision(tensor)` - Report % of values in danger zones
- [ ] Detect denormal floats (values near zero with reduced precision)
- [ ] Detect near-overflow values
- [ ] Recommend when to flush denormals to zero for performance

---

## Phase 5: JIT Compatibility (v1.5.0)

**Goal:** Make Neon functions compilable by torch.compile, jax.jit, numba.

### 5.1 Compilation-Ready Implementation

**The Problem:**
```python
# Current implementation uses try/except - breaks JIT compilation
def div(a, b, default=None):
    try:
        return a / b
    except ZeroDivisionError:
        return default  # torch.jit.script fails here!
```

**The Neon Way:**
```python
# JIT-friendly implementation (no exceptions in hot path)
def div(a, b, default=None):
    mask = (b != 0)
    result = torch.where(mask, a / torch.where(mask, b, 1.0), default)
    return result
```

**Deliverables:**
- [ ] Rewrite all `neon.torch` functions to be `@torch.jit.script` compatible
- [ ] Rewrite all `neon.jax` functions to be `@jax.jit` compatible
- [ ] Add `@numba.jit` compatibility for `neon.numpy`
- [ ] Comprehensive JIT compilation tests
- [ ] Performance benchmarks: compiled vs. eager mode

**Constraints:**
- No Python try/except in hot paths (use masking instead)
- No dynamic types (everything must be statically typed)
- No Python list/dict (use tensors/arrays only)
- Pure functions only (no side effects)

---

## Implementation Priority

### Immediate (Next 2-4 weeks): Phase 1.1 - NumPy Integration
**Why First:**
- Foundation for PyTorch/JAX support
- Fastest to implement (no gradient logic needed)
- Immediate value for data scientists
- Proves the vectorization approach

**Success Metric:** `neon.numpy.div_safe()` is 10x faster than naive Python loops and matches hand-written NumPy performance.

### Short Term (1-2 months): Phase 1.2 - PyTorch Integration
**Why Second:**
- Largest user base (PyTorch dominates AI research)
- Gradient logic is critical but well-understood
- Enables Phase 2 (soft logic) and Phase 3 (NaN hunter)

**Success Metric:** Top 3 AI labs adopt Neon for LLM training runs.

### Medium Term (3-4 months): Phase 3 - NaN Hunter
**Why Third:**
- Killer feature that competitors don't have
- Solves the #1 pain point in AI research
- Builds on PyTorch integration

**Success Metric:** "Neon saved us 2 weeks of debugging" testimonials on Twitter.

### Long Term (6+ months): Phases 2, 4, 5
- Phase 2 (Soft Logic): Needed for advanced optimization
- Phase 4 (Low Precision): Needed as FP8 training becomes standard
- Phase 5 (JIT): Performance optimization, not critical path

---

## Marketing Pivot

### Core Positioning (v1.0.0 - Unchanged)
"Near-equality and tolerance arithmetic for floating-point numbers"
→ Clear, trustworthy, educational

**Target Audience (Existing):**
- ✅ Data scientists cleaning CSV files
- ✅ Financial engineers (precision matters)
- ✅ Scientists (proper error handling)
- ✅ Anyone who needs correct floating-point math

**Key Messaging (Unchanged):**
- "Zero dependencies, zero bugs"
- "Floating-point comparison that gets edge cases right"
- "Educational - learn why `0.1 + 0.2 != 0.3`"

### AI Extension Positioning (v1.1.0+)
"Stop your LLM training runs from crashing"
→ Specific, urgent, compelling

**Target Audience (New):**
- ✅ AI researchers training 70B parameter models
- ✅ ML engineers debugging NaN losses
- ✅ AI labs running multi-GPU training
- ✅ Anyone using PyTorch/JAX for deep learning

**Key Messaging:**
- "Built on Neon's battle-tested core - now vectorized for AI"
- "The #1 cause of failed training runs is NaN loss. Neon catches it before it happens."
- "Tired of `torch.where(mask, x/y, 0.0)` boilerplate? Use `neon.torch.div_safe()`."

**Two Products, One Philosophy:**
Both serve the same mission: **Make floating-point math safe and correct.**

---

## Technical Design Principles

### 1. Zero Overhead When Disabled
```python
# Production mode: zero overhead
neon.config.set_debug_mode(False)
result = ntorch.div_safe(x, y)  # Compiles to pure PyTorch ops

# Debug mode: full instrumentation
neon.config.set_debug_mode(True)
result = ntorch.div_safe(x, y)  # Adds monitoring, logging
```

### 2. Composable with Existing Code
```python
# Works with existing PyTorch modules
class MyModel(nn.Module):
    def forward(self, x):
        # Mix neon.torch and torch operations freely
        x = torch.matmul(x, self.weight)
        x = ntorch.div_safe(x, self.scale, default=0.0)
        return x
```

### 3. Fail Loudly in Debug, Silently in Prod
```python
# Debug mode: raise informative errors
with neon.debug_mode():
    result = ntorch.div_safe(x, y)  # Crashes with detailed report if unstable

# Production mode: handle gracefully
result = ntorch.div_safe(x, y, default=0.0)  # Never crashes, uses default
```

### 4. Performance = Correctness
- Neon operations must be **as fast as hand-written code**
- Use C/C++/CUDA extensions if needed
- Profile everything: <5% overhead is acceptable, >10% is not

---

## Success Metrics

### Adoption (Qualitative)
- [ ] 3+ top AI labs (OpenAI, Anthropic, Google DeepMind, Meta, etc.) using Neon
- [ ] Featured in popular AI training frameworks (HuggingFace Transformers, PyTorch Lightning)
- [ ] "Use Neon" becomes standard advice in LLM training guides

### Performance (Quantitative)
- [ ] 100K+ PyPI downloads/month (vs. 1K/month currently)
- [ ] 1000+ GitHub stars (vs. <100 currently)
- [ ] 10+ community contributors

### Technical (Measurable)
- [ ] Neon operations are <5% slower than hand-written equivalents
- [ ] NaN detection has <5% overhead in debug mode
- [ ] 95%+ test coverage maintained
- [ ] Full type safety with mypy --strict

---

## Non-Goals (Out of Scope)

- ❌ Replace NumPy/PyTorch (we integrate with them)
- ❌ Arbitrary precision arithmetic (use `decimal.Decimal`)
- ❌ Symbolic math (use SymPy)
- ❌ Automatic differentiation (use PyTorch/JAX)
- ❌ Custom neural network layers (just provide safe ops)

---

## Architectural Principles: Preserve the Essence

### What Makes Neon Special

**The Core Strengths (v1.0.0):**
1. **Zero dependencies** - Pure stdlib, instant install, no version hell
2. **Crystal clear intent** - `safe.div(x, 0, default=0.0)` reads like English
3. **Correct by default** - Handles edge cases (NaN, inf, denormals) that everyone else gets wrong
4. **Small, focused, perfect** - Does one thing exceptionally well
5. **Educational value** - README teaches you about floating-point pitfalls

**The Risk:** Adding NumPy/PyTorch could turn Neon into "yet another ML utilities library" - bloated, complex, loses identity.

### The Sacred Core

**The core of Neon (compare, clamp, safe, ulp) is FROZEN at v1.x:**
- ✅ **Zero dependencies forever** - Will never require NumPy/PyTorch/JAX
- ✅ **No breaking changes** - Existing code keeps working
- ✅ **Small and fast** - < 100KB installed size
- ✅ **Perfect edge cases** - NaN, inf, denormals all handled correctly
- ✅ **Readable code** - No obfuscated optimizations

**Why This Matters:**
Current users chose Neon because it's lightweight and trustworthy. We will never break that trust.

### Layered Extensions (Optional)

**New AI features live in separate, optional modules:**

```
# Install options
pip install elemental-neon              # Core only: 0 deps, 50KB
pip install elemental-neon[numpy]       # +NumPy support: 1 dep, 500KB
pip install elemental-neon[torch]       # +PyTorch support: 1 dep, 2GB
pip install elemental-neon[all]         # Everything
```

**Package structure:**
```python
neon/                     # Core (ZERO dependencies)
├── compare.py           # ✅ Unchanged
├── clamp.py             # ✅ Unchanged
├── safe.py              # ✅ Unchanged
├── ulp.py               # ✅ Unchanged
└── exceptions.py        # ✅ Unchanged

neon/numpy/              # Optional (requires numpy)
├── __init__.py          # ✅ New in v1.1
└── _safe.py             # ✅ New in v1.1

neon/torch/              # Optional (requires torch)
├── __init__.py          # ✅ New in v1.2
└── _safe.py             # ✅ New in v1.2
```

### Two Marketing Channels, One Philosophy

**Channel 1: Core Users (Current)**
- Pitch: "Zero-dependency floating-point comparison that gets edge cases right"
- Install: `pip install elemental-neon`
- Docs: Current README (unchanged)
- Examples: CSV cleaning, financial calculations, scientific computing

**Channel 2: AI/ML Users (New)**
- Pitch: "Stop your LLM training runs from crashing"
- Install: `pip install elemental-neon[torch]`
- Docs: New "AI Guide" section
- Examples: Safe division in loss functions, NaN detection, gradient monitoring

**Shared Mission:** Make floating-point math safe and correct.

---

## Resolved Design Questions

### 1. Dependencies

**Decision:** Core stays zero-dependency. Extensions are optional.

```python
# This always works (no dependencies)
from neon import safe
result = safe.div(1.0, 0.0, default=0.0)

# This requires: pip install elemental-neon[numpy]
import neon.numpy as nnp
result = nnp.div_safe(arr, 0.0, default=0.0)

# This requires: pip install elemental-neon[torch]
import neon.torch as ntorch
result = ntorch.div_safe(tensor, 0.0, default=0.0)
```

**Implementation:** Use optional imports with helpful error messages.

```python
# neon/numpy/__init__.py
try:
    import numpy as np
except ImportError:
    raise ImportError(
        "neon.numpy requires NumPy. Install with: pip install elemental-neon[numpy]"
    )
```

### 2. Versioning

**Decision:** No breaking changes. Extensions are additive.

- ✅ v1.0.x = Core only (stable)
- ✅ v1.1.0 = Core + optional `neon.numpy`
- ✅ v1.2.0 = Core + optional `neon.numpy` + optional `neon.torch`
- ✅ v2.x only if core API must change (unlikely)

**Guarantee:** `pip install elemental-neon==1.0.0` code will work on v1.9.0 without changes.

### 3. Performance

**Decision:** Core stays pure Python. Extensions can use C if needed.

- ✅ **Core (neon.safe, etc.):** Pure Python (readable, maintainable)
- ✅ **NumPy extension:** Uses NumPy's C primitives (np.where, etc.)
- ✅ **PyTorch extension:** Uses PyTorch's CUDA kernels
- ✅ **Only optimize if benchmarks show >10% overhead**

### 4. Naming

**Decision:** Clear namespacing with `_safe` suffix for array functions.

```python
# Scalar API (unchanged)
from neon import safe
safe.div(a, b)

# Array API (new, explicit suffix)
from neon import numpy as nnp
nnp.div_safe(a, b)  # Note: _safe suffix
```

**Rationale:** The `_safe` suffix makes it clear this is the safe version when used alongside `np.divide()` or `torch.div()`.

### The Commitment

**We promise:**
1. The core will **never** require NumPy/PyTorch/JAX
2. Current users get **zero breaking changes**
3. AI features are **opt-in**, not forced
4. Documentation stays **beginner-friendly**
5. Code stays **readable** (no obfuscated optimizations)
6. Package size stays **small** (core < 100KB)

---

## Resources Needed

### Development Time
- Phase 1.1 (NumPy): 20-40 hours
- Phase 1.2 (PyTorch): 40-80 hours
- Phase 1.3 (JAX): 40-80 hours
- Phase 3 (NaN Hunter): 80-120 hours

### Expertise Required
- NumPy internals (vectorization, broadcasting)
- PyTorch autograd (custom Function, backward hooks)
- JAX transformations (jit, vmap, grad)
- C/C++ (if performance optimization needed)

### Testing Infrastructure
- GPU CI runners for PyTorch CUDA tests
- Multi-precision test suite (FP16, BF16, FP32, FP64)
- Property-based testing for gradient correctness
- Performance regression benchmarks

---

**Next Step:** Start Phase 1.1 (NumPy Integration) with `neon.numpy.div_safe()` prototype.
