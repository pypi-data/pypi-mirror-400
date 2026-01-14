"""Performance benchmarks for neon library.

Run with: python benchmarks/bench_neon.py
"""

import math
import time
from typing import Callable

from neon import compare, clamp, safe, ulp


def benchmark(func: Callable, iterations: int = 1_000_000) -> float:
    """Benchmark a function and return ops/sec."""
    start = time.perf_counter()
    for _ in range(iterations):
        func()
    elapsed = time.perf_counter() - start
    return iterations / elapsed


def main() -> None:
    """Run all benchmarks."""
    print("Neon Performance Benchmarks")
    print("=" * 60)
    print()

    # Compare module benchmarks
    print("compare.near():")
    ops_per_sec = benchmark(lambda: compare.near(0.1 + 0.2, 0.3))
    us_per_op = 1_000_000 / ops_per_sec
    print(f"  {ops_per_sec:,.0f} ops/sec (~{us_per_op:.2f}µs per op)")

    print("\ncompare.near_zero():")
    ops_per_sec = benchmark(lambda: compare.near_zero(1e-15))
    us_per_op = 1_000_000 / ops_per_sec
    print(f"  {ops_per_sec:,.0f} ops/sec (~{us_per_op:.2f}µs per op)")

    print("\ncompare.is_integer():")
    ops_per_sec = benchmark(lambda: compare.is_integer(3.0000000001))
    us_per_op = 1_000_000 / ops_per_sec
    print(f"  {ops_per_sec:,.0f} ops/sec (~{us_per_op:.2f}µs per op)")

    # Clamp module benchmarks
    print("\nclamp.to_zero():")
    ops_per_sec = benchmark(lambda: clamp.to_zero(1e-15))
    us_per_op = 1_000_000 / ops_per_sec
    print(f"  {ops_per_sec:,.0f} ops/sec (~{us_per_op:.2f}µs per op)")

    print("\nclamp.to_int():")
    ops_per_sec = benchmark(lambda: clamp.to_int(2.9999999999))
    us_per_op = 1_000_000 / ops_per_sec
    print(f"  {ops_per_sec:,.0f} ops/sec (~{us_per_op:.2f}µs per op)")

    print("\nclamp.to_range():")
    ops_per_sec = benchmark(lambda: clamp.to_range(5, 0, 10))
    us_per_op = 1_000_000 / ops_per_sec
    print(f"  {ops_per_sec:,.0f} ops/sec (~{us_per_op:.2f}µs per op)")

    # Safe module benchmarks
    print("\nsafe.div():")
    ops_per_sec = benchmark(lambda: safe.div(6, 3))
    us_per_op = 1_000_000 / ops_per_sec
    print(f"  {ops_per_sec:,.0f} ops/sec (~{us_per_op:.2f}µs per op)")

    print("\nsafe.sqrt():")
    ops_per_sec = benchmark(lambda: safe.sqrt(4))
    us_per_op = 1_000_000 / ops_per_sec
    print(f"  {ops_per_sec:,.0f} ops/sec (~{us_per_op:.2f}µs per op)")

    # ULP module benchmarks
    print("\nulp.of():")
    ops_per_sec = benchmark(lambda: ulp.of(1.0))
    us_per_op = 1_000_000 / ops_per_sec
    print(f"  {ops_per_sec:,.0f} ops/sec (~{us_per_op:.2f}µs per op)")

    print("\nulp.diff():")
    ops_per_sec = benchmark(lambda: ulp.diff(1.0, 1.0 + 2.2e-16))
    us_per_op = 1_000_000 / ops_per_sec
    print(f"  {ops_per_sec:,.0f} ops/sec (~{us_per_op:.2f}µs per op)")

    print("\nulp.within():")
    ops_per_sec = benchmark(lambda: ulp.within(1.0, 1.0 + 1e-15))
    us_per_op = 1_000_000 / ops_per_sec
    print(f"  {ops_per_sec:,.0f} ops/sec (~{us_per_op:.2f}µs per op)")

    print("\nulp.next():")
    ops_per_sec = benchmark(lambda: ulp.next(1.0))
    us_per_op = 1_000_000 / ops_per_sec
    print(f"  {ops_per_sec:,.0f} ops/sec (~{us_per_op:.2f}µs per op)")

    # Batch operations
    print("\n" + "=" * 60)
    print("Batch Operations (100 values)")
    print("=" * 60)

    values_100 = [0.1] * 100

    print("\nsafe.sum_exact() vs sum():")
    ops_per_sec_exact = benchmark(lambda: safe.sum_exact(values_100), iterations=100_000)
    ops_per_sec_naive = benchmark(lambda: sum(values_100), iterations=100_000)
    print(f"  safe.sum_exact(): {ops_per_sec_exact:,.0f} ops/sec")
    print(f"  sum():            {ops_per_sec_naive:,.0f} ops/sec")
    print(f"  Overhead: {(ops_per_sec_naive / ops_per_sec_exact):.2f}x")

    pairs_100 = [(0.1, 0.1) for _ in range(100)]

    print("\ncompare.near_many() vs loop:")
    ops_per_sec_batch = benchmark(
        lambda: compare.near_many(pairs_100), iterations=100_000
    )
    ops_per_sec_loop = benchmark(
        lambda: [compare.near(a, b) for a, b in pairs_100], iterations=100_000
    )
    print(f"  near_many(): {ops_per_sec_batch:,.0f} ops/sec")
    print(f"  list comp:   {ops_per_sec_loop:,.0f} ops/sec")
    print(f"  Speedup: {(ops_per_sec_batch / ops_per_sec_loop):.2f}x")

    print()
    print("=" * 60)
    print("Benchmark complete!")


if __name__ == "__main__":
    main()
