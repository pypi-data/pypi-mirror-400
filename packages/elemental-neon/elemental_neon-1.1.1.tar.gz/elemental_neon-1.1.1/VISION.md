# Neon Vision: The Essence

## What We Are

**Neon is the floating-point safety library that gets edge cases right.**

We handle the hard parts of floating-point arithmetic so you don't have to worry about:
- Division by zero
- NaN comparisons
- Denormal floats
- Catastrophic cancellation
- Precision loss

## What Makes Us Special

1. **Zero dependencies** - Pure Python stdlib. Always.
2. **Correct by default** - We handle edge cases others ignore.
3. **Crystal clear** - Code reads like the documentation.
4. **Educational** - Learn why floating-point is hard.
5. **Small and focused** - One thing done perfectly.

## The Sacred Core (v1.x Forever)

These modules are **frozen** - zero dependencies, zero breaking changes:
- `neon.compare` - Tolerance-based comparisons
- `neon.clamp` - Value snapping and clamping
- `neon.safe` - Safe arithmetic operations
- `neon.ulp` - ULP-based precision control

**Promise:** If it works with `pip install elemental-neon==1.0.0`, it works forever.

## The AI Evolution (v1.1.0+)

**New, optional extensions** for AI/ML workloads:
- `neon.numpy` - Vectorized operations (requires `pip install elemental-neon[numpy]`)
- `neon.torch` - Gradient-aware safety (requires `pip install elemental-neon[torch]`)
- `neon.jax` - JIT-compilable ops (requires `pip install elemental-neon[jax]`)

**Same philosophy, new scale:** The safety guarantees of Neon core, now for millions of floats at GPU speed.

## Two Audiences, One Mission

### Audience 1: Current Users
**Who:** Data scientists, financial engineers, scientists, anyone doing numerical Python
**Pitch:** "Zero dependencies, zero bugs"
**Install:** `pip install elemental-neon`
**Value:** Lightweight, trustworthy, educational

### Audience 2: AI/ML Teams
**Who:** AI researchers, ML engineers, anyone training neural networks
**Pitch:** "Stop your LLM training from crashing"
**Install:** `pip install elemental-neon[torch]`
**Value:** Catch NaN before it happens, gradient-aware safety, performance at scale

**Both audiences get:** Floating-point math that actually works correctly.

## What We Will Never Do

- ❌ Break the zero-dependency core
- ❌ Require AI libraries for basic functionality
- ❌ Bloat the package (core stays < 100KB)
- ❌ Sacrifice readability for performance
- ❌ Break backward compatibility in v1.x
- ❌ Become "yet another ML utilities library"

## What We Will Always Do

- ✅ Keep the core lightweight and dependency-free
- ✅ Handle edge cases correctly (NaN, inf, denormals)
- ✅ Provide clear, educational documentation
- ✅ Maintain backward compatibility
- ✅ Write readable, maintainable code
- ✅ Test everything with 95%+ coverage

## The North Star

**Question to ask for every feature:**
> "Does this make floating-point math safer and more correct?"

**If yes:** Consider it.
**If no:** Reject it.

**Follow-up questions:**
- Does it require new dependencies for the core? → Reject
- Does it break existing code? → Reject (unless v2.0+)
- Does it make the code harder to understand? → Rethink
- Is it solving a real problem? → Proceed

## Success Metrics

### Qualitative
- Users trust Neon for production financial calculations
- AI researchers adopt it to prevent training crashes
- Beginners learn about floating-point from our docs
- Code reviews cite Neon's edge case handling as reference

### Quantitative
- 100K+ PyPI downloads/month
- 1000+ GitHub stars
- 95%+ test coverage maintained
- <5% performance overhead vs hand-written equivalents

### Testimonials We Want
- "Neon saved us 2 weeks of debugging a NaN loss issue"
- "Finally, a library that handles 0.1 + 0.2 == 0.3 correctly"
- "Zero dependencies means I can actually use this in production"
- "The README taught me more about floats than my CS degree"

## The Long-term Vision

**v1.0 (✅ Shipped):** The lightweight, perfect core
**v1.1 (Next):** Add NumPy vectorization (optional)
**v1.2 (Future):** Add PyTorch gradient safety (optional)
**v1.3 (Future):** Add NaN Hunter debugging tools
**v2.0 (Maybe never):** Only if core API must evolve

**End state:** Neon is the standard answer to:
1. "How do I compare floats correctly?" → Use Neon core
2. "How do I prevent NaN loss in training?" → Use Neon + PyTorch
3. "How do I debug numerical instability?" → Use Neon NaN Hunter

---

**Remember:** We're not building a framework. We're building a scalpel - small, sharp, essential.

**Our job:** Make floating-point math boring. When it works correctly, nobody thinks about it. That's success.
