#!/usr/bin/env python3
"""Nuclear Add - Complete Demonstration.

This script demonstrates all features of the nuclear_add module,
the most paranoid addition ever created.

Usage:
    uv run python -m nuclear_add.demo
    or
    uv run nuclear-add-demo
"""

import io
import sys

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from decimal import Decimal
from fractions import Fraction

from nuclear_add import add, gradient, sum_safe
from nuclear_add.backends import get_backend, list_available_backends
from nuclear_add.core import NuclearConfig, NuclearEngine, set_engine
from nuclear_add.tracing import NumericTracer
from nuclear_add.types import DualNumber, Interval, LazyExpr, StochasticValue, TracedValue


def banner(title: str) -> None:
    """Display a banner."""
    print("\n" + "=" * 70)
    print(f" 🔥 {title}")
    print("=" * 70)


def section(title: str) -> None:
    """Display a section title."""
    print(f"\n--- {title} ---")


def demo_basic_addition() -> None:
    """Demonstration of basic additions."""
    banner("1. BASIC ADDITIONS")

    section("Integers and floats")
    print(f"add(2, 3) = {add(2, 3)}")
    print(f"add(1.5, 2.5) = {add(1.5, 2.5)}")
    print(f"add(-10, 25) = {add(-10, 25)}")

    section("Complex numbers")
    print(f"add(1+2j, 3+4j) = {add(1+2j, 3+4j)}")

    section("The famous 0.1 + 0.2 (classic float problem)")
    print(f"Native Python: 0.1 + 0.2 = {0.1 + 0.2}")
    print(f"Nuclear (auto): add(0.1, 0.2) = {add(0.1, 0.2)}")
    result_decimal = add(0.1, 0.2, precision="decimal")
    print(f"Nuclear (decimal): add(0.1, 0.2, precision='decimal') = {result_decimal}")


def demo_precision_modes() -> None:
    """Demonstration of precision modes."""
    banner("2. PRECISION MODES")

    section("Decimal (arbitrary precision)")
    result = add(Decimal("0.1"), Decimal("0.2"))
    print(f"add(Decimal('0.1'), Decimal('0.2')) = {result}")

    section("Fraction (exact)")
    result_fraction = add(Fraction(1, 3), Fraction(1, 6))
    print(f"add(Fraction(1/3), Fraction(1/6)) = {result_fraction}")

    section("Force precision mode")
    result_complex = add(0.1, 0.2, precision="fraction")
    print(f"add(0.1, 0.2, precision='fraction') = {result_complex}")


def demo_overflow_handling() -> None:
    """Demonstration of overflow handling."""
    banner("3. OVERFLOW HANDLING")

    print("Native Python: 1e308 + 1e308 =", 1e308 + 1e308, "(silent!)")

    section("STRICT mode (default) - raises exception")
    try:
        result = add(1e308, 1e308)
        print(f"Result: {result}")
    except OverflowError as e:
        print(f"✓ OverflowError caught: {e}")

    section("INF mode - returns inf")
    result = add(1e308, 1e308, overflow="inf")
    print(f"add(1e308, 1e308, overflow='inf') = {result}")

    section("SATURATE mode - saturates to MAX_FLOAT")
    result = add(1e308, 1e308, overflow="saturate")
    print(f"add(1e308, 1e308, overflow='saturate') = {result}")


def demo_nan_handling() -> None:
    """Demonstration of NaN handling."""
    banner("4. NaN HANDLING")

    print("Native Python: float('nan') + 1 =", float("nan") + 1, "(propagates!)")

    section("RAISE mode (default)")
    try:
        result = add(float("nan"), 1)
    except ArithmeticError as e:
        print(f"✓ ArithmeticError caught: {e}")

    section("PROPAGATE mode")
    result = add(float("nan"), 1, nan="propagate")
    print(f"add(nan, 1, nan='propagate') = {result}")

    section("REPLACE mode")
    result = add(float("nan"), 1, nan="replace")
    print(f"add(nan, 1, nan='replace') = {result}")


def demo_interval_arithmetic() -> None:
    """Demonstration of interval arithmetic."""
    banner("5. INTERVAL ARITHMETIC")

    section("Creating intervals")
    a = Interval.from_value(0.1)
    b = Interval.from_value(0.2)
    print(f"a = {a}")
    print(f"b = {b}")

    section("Adding intervals")
    c = add(a, b)
    print(f"a + b = {c}")
    print(f"0.3 ∈ interval? {0.3 in c}")
    print(f"Interval width: {c.width:.2e}")

    section("Uncertainty propagation")
    x = Interval(0.99, 1.01)  # 1.0 ± 0.01
    y = Interval(1.99, 2.01)  # 2.0 ± 0.01
    z = x + y
    print(f"[0.99, 1.01] + [1.99, 2.01] = {z}")
    print(f"Uncertainty adds up: width = {z.width}")


def demo_autodiff() -> None:
    """Demonstration of automatic differentiation."""
    banner("6. AUTOMATIC DIFFERENTIATION")

    section("Dual numbers")
    x = DualNumber.variable(3.0)  # x = 3, dx/dx = 1
    print(f"x = {x}")

    section("Computing f(x) = x² + 2x")
    y = x * x + 2 * x
    print(f"f(3) = {y.real}")
    print(f"f'(3) = {y.dual}  (analytically: 2x + 2 = 8 ✓)")

    section("gradient() function")

    def f(x: float) -> float:
        return x * x * x  # f(x) = x³

    def f_dual(x_dual: DualNumber) -> DualNumber:
        """Wrap function for gradient computation."""
        return x_dual * x_dual * x_dual

    grad = gradient(f_dual, 2.0)  # f'(2) = 3x² = 12
    print("f(x) = x³")
    print(f"f'(2) = {grad}  (analytically: 3×2² = 12 ✓)")

    section("Chain of derivation")
    x = DualNumber.variable(1.0)
    result = (x * x + 1).sqrt()  # f(x) = √(x² + 1)
    print("f(x) = √(x² + 1)")
    print(f"f(1) = {result.real:.6f}")
    print(f"f'(1) = {result.dual:.6f}  (analytically: x/√(x²+1) = 1/√2 ≈ 0.707 ✓)")


def demo_lazy_evaluation() -> None:
    """Demonstration of lazy evaluation."""
    banner("7. LAZY EVALUATION & COMPUTATION GRAPHS")

    section("Building expressions")
    x = LazyExpr.var("x", 3.0)
    y = LazyExpr.var("y", 4.0)

    # Pythagorean: √(x² + y²)
    z = (x * x + y * y).sqrt()
    print("Expression: z = √(x² + y²)")
    print("Not yet evaluated!")

    section("Evaluation")
    result = z.eval()
    print(f"z.eval() with x=3, y=4 → {result} (= 5 ✓)")

    section("Symbolic differentiation")
    dz_dx = z.grad("x")
    print(f"∂z/∂x = {dz_dx.eval():.6f}  (analytically: x/√(x²+y²) = 3/5 = 0.6 ✓)")

    section("Computation graph (DOT format)")
    simple = x + y
    print(simple.to_graph())


def demo_tracing() -> None:
    """Demonstration of tracing system."""
    banner("8. NUMERIC ERROR TRACING")

    section("Creating a tracer")
    _tracer = NumericTracer()

    section("Tracing operations")
    config = NuclearConfig.paranoid()
    engine = NuclearEngine(config)
    set_engine(engine)

    # Some operations that may generate warnings
    import contextlib

    with contextlib.suppress(BaseException):
        add(1e308, 1e308, mode="paranoid", overflow="inf")

    section("Tracing summary")
    global_tracer = engine.tracer
    summary = global_tracer.get_summary()
    print(f"Recorded events: {summary.get('total_events', 0)}")

    for event in global_tracer.events[-3:]:  # Last 3 events
        print(f"  • {event}")


def demo_kahan_summation() -> None:
    """Demonstration of Kahan summation."""
    banner("9. KAHAN SUMMATION (MAXIMUM PRECISION)")

    section("Problem: summing many small numbers")
    # Add 1.0 ten million times, then subtract 10 million
    # Should give 0, but errors accumulate

    n = 10_000_000
    values = [1.0] * n + [-float(n)]

    section("Native Python sum")
    result_native = sum(values)
    print(f"sum(values) = {result_native}")
    print(f"Error: {abs(result_native)}")

    section("Kahan sum")
    result_kahan = sum_safe(values, precision="kahan")
    print(f"sum_safe(values, precision='kahan') = {result_kahan}")
    print(f"Error: {abs(result_kahan)}")

    section("Neumaier sum (improvement of Kahan)")
    result_neumaier = sum_safe(values, precision="neumaier")
    print(f"sum_safe(values, precision='neumaier') = {result_neumaier}")

    section("Pairwise sum")
    # Slower but good precision/speed tradeoff
    small_values = [0.1] * 1000
    result_pairwise = sum_safe(small_values, precision="pairwise")
    print("Sum of 1000 × 0.1:")
    print(f"  Native: {sum(small_values)}")
    print(f"  Pairwise: {result_pairwise}")


def demo_traced_values() -> None:
    """Demonstration of traced values."""
    banner("10. VALUES WITH COMPLETE HISTORY")

    section("Creating traced values")
    a = TracedValue(10.0)
    b = TracedValue(5.0)

    section("Operations")
    c = a + b
    d = c * TracedValue(2.0)
    e = d - a

    print("a = 10, b = 5")
    print(f"c = a + b = {c.value}")
    print(f"d = c * 2 = {d.value}")
    print(f"e = d - a = {e.value}")

    section("Complete history")
    print(e.get_full_trace())


def demo_vectorization() -> None:
    """Demonstration of vectorization."""
    banner("11. VECTORIZATION")

    section("Vector + vector addition")
    result = add([1, 2, 3], [4, 5, 6])
    print(f"add([1, 2, 3], [4, 5, 6]) = {list(result)}")

    section("Vector + scalar addition (broadcasting)")
    result_list = add([1, 2, 3], 10)  # type: ignore[call-overload]
    print(f"add([1, 2, 3], 10) = {list(result_list)}")

    section("Tuples")
    result = add((1.5, 2.5), (3.5, 4.5))
    print(f"add((1.5, 2.5), (3.5, 4.5)) = {tuple(result)}")


def demo_backends() -> None:
    """Demonstration of different backends."""
    banner("12. COMPUTATION BACKENDS")

    section("Available backends")
    available = list_available_backends()
    print(f"Backends on this system: {available}")

    section("Backend capabilities")
    for name in available:
        backend = get_backend(name)
        caps = backend.capabilities
        features = []
        if caps.vectorized:
            features.append("vectorized")
        if caps.gpu:
            features.append("GPU")
        if caps.jit:
            features.append("JIT")
        if caps.simd:
            features.append("SIMD")
        if caps.arbitrary_precision:
            features.append("arbitrary precision")
        if caps.deterministic:
            features.append("deterministic")

        print(f"  {name}: {', '.join(features) or 'basic'}")

    section("Explicit backend usage")
    python_backend = get_backend("python")
    result = python_backend.kahan_sum([0.1] * 100)
    print(f"Python backend, Kahan sum of 100×0.1 = {result}")


def demo_stochastic_rounding() -> None:
    """Demonstration of stochastic rounding."""
    banner("13. STOCHASTIC ROUNDING")

    section("Concept")
    print("Stochastic rounding eliminates systematic bias")
    print("in long sums of floats.")

    section("Demonstration")
    results = []
    for seed in range(10):
        sv = StochasticValue(0.123456789, _rng_seed=seed)
        results.append(sv.value)

    print("Original value: 0.123456789")
    print("After stochastic rounding (10 different seeds):")
    for i, r in enumerate(results[:5]):
        print(f"  seed={i}: {r}")


def demo_config_presets() -> None:
    """Demonstration of configuration presets."""
    banner("14. CONFIGURATION PRESETS")

    section("STRICT preset (default)")
    config = NuclearConfig.strict()
    print(f"  Mode: {config.math_mode.name}")
    print(f"  Overflow: {config.overflow_policy.name}")
    print(f"  NaN: {config.nan_policy.name}")

    section("FAST preset")
    config = NuclearConfig.fast()
    print(f"  Mode: {config.math_mode.name}")
    print(f"  Overflow: {config.overflow_policy.name}")
    print(f"  Tracing: {config.enable_tracing}")

    section("PARANOID preset")
    config = NuclearConfig.paranoid()
    print(f"  Mode: {config.math_mode.name}")
    print(f"  Precision: {config.precision_mode.name}")
    print(f"  Trace all: {config.trace_all_operations}")

    section("SCIENTIFIC preset")
    config = NuclearConfig.scientific(precision=100)
    print(f"  Precision mode: {config.precision_mode.name}")
    print(f"  Decimal precision: {config.decimal_precision} digits")


def demo_error_bounds() -> None:
    """Demonstration of formal error bounds."""
    banner("15. FORMAL ERROR BOUNDS")

    from nuclear_add.core import add_with_error

    section("Addition with error bounds")
    result, bounds = add_with_error(0.1, 0.2)
    print(f"0.1 + 0.2 = {result}")
    print(f"Guaranteed bounds: {bounds}")
    print(f"Max relative error: {bounds.relative_error:.2e}")

    section("Error propagation")
    # Simulate a chain of calculations
    a = Interval.from_value(1.0, ulp_error=1)
    for _i in range(10):
        a = a + Interval.from_value(0.1, ulp_error=1)

    print("After 10 additions of 0.1:")
    print(f"  Interval: {a}")
    print(f"  Width: {a.width:.2e}")
    print(f"  Is 2.0 in interval? {2.0 in a}")


def main() -> None:
    """Run all demonstrations."""
    print(
        """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     ███╗   ██╗██╗   ██╗ ██████╗██╗     ███████╗ █████╗ ██████╗               ║
║     ████╗  ██║██║   ██║██╔════╝██║     ██╔════╝██╔══██╗██╔══██╗              ║
║     ██╔██╗ ██║██║   ██║██║     ██║     █████╗  ███████║██████╔╝              ║
║     ██║╚██╗██║██║   ██║██║     ██║     ██╔══╝  ██╔══██║██╔══██╗              ║
║     ██║ ╚████║╚██████╔╝╚██████╗███████╗███████╗██║  ██║██║  ██║              ║
║     ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝              ║
║                                                                               ║
║          █████╗ ██████╗ ██████╗      ██╗   ██╗ ██╗    ██████╗                ║
║         ██╔══██╗██╔══██╗██╔══██╗     ██║   ██║███║   ██╔═████╗               ║
║         ███████║██║  ██║██║  ██║     ██║   ██║╚██║   ██║██╔██║               ║
║         ██╔══██║██║  ██║██║  ██║     ╚██╗ ██╔╝ ██║   ████╔╝██║               ║
║         ██║  ██║██████╔╝██████╔╝      ╚████╔╝  ██║██╗╚██████╔╝               ║
║         ╚═╝  ╚═╝╚═════╝ ╚═════╝        ╚═══╝   ╚═╝╚═╝ ╚═════╝                ║
║                                                                               ║
║              The most paranoid addition ever created                          ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """
    )

    demos = [
        demo_basic_addition,
        demo_precision_modes,
        demo_overflow_handling,
        demo_nan_handling,
        demo_interval_arithmetic,
        demo_autodiff,
        demo_lazy_evaluation,
        demo_traced_values,
        demo_kahan_summation,
        demo_vectorization,
        demo_backends,
        demo_stochastic_rounding,
        demo_config_presets,
        demo_error_bounds,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n⚠️ Error in {demo.__name__}: {e}")
            import traceback

            traceback.print_exc()
        print()

    print("\n" + "=" * 70)
    print(" 🎉 DEMONSTRATION COMPLETED")
    print("=" * 70)
    print(
        """
This module is intentionally OVERKILL.

It demonstrates that a simple addition can become:
• A numerical precision problem
• An error handling challenge
• An optimization opportunity
• An API design exercise

For 99.9% of cases: just use +

For the remaining 0.1%: now you know this exists 😈
    """
    )


if __name__ == "__main__":
    main()
