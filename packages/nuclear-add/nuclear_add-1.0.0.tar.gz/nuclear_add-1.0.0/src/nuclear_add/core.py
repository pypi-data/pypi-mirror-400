"""Core engine for nuclear addition.

This module contains:
- NuclearConfig: Complete engine configuration
- NuclearEngine: Computation execution engine
- add(): Main addition function
"""

from __future__ import annotations

import math
import operator
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from decimal import Decimal, getcontext
from enum import Enum, auto
from fractions import Fraction
from numbers import Number, Real
from typing import (
    Any,
    Literal,
    TypeVar,
    overload,
)

from .backends import Backend, get_backend
from .tracing import (
    ErrorSeverity,
    ErrorType,
    NumericTracer,
    OverflowDetector,
    PrecisionAnalyzer,
    get_global_tracer,
)
from .types import DualNumber, Interval, LazyExpr, StochasticValue, TracedValue

# =============================================================================
# CONFIGURATION
# =============================================================================


class OverflowPolicy(Enum):
    """Overflow management policy."""

    RAISE = auto()  # Raise an exception
    INF = auto()  # Return inf
    SATURATE = auto()  # Saturate to MAX_FLOAT
    WRAP = auto()  # Wrap around (like integers)


class NaNPolicy(Enum):
    """NaN management policy."""

    RAISE = auto()  # Raise an exception
    PROPAGATE = auto()  # Propagate NaN
    REPLACE = auto()  # Replace with default value


class PrecisionMode(Enum):
    """Precision mode."""

    AUTO = auto()  # Automatic detection
    FLOAT64 = auto()  # IEEE 754 double precision
    DECIMAL = auto()  # Arbitrary precision (Decimal)
    FRACTION = auto()  # Exact (Fraction)
    INTERVAL = auto()  # Interval arithmetic


class MathMode(Enum):
    """Computation mode."""

    STRICT = auto()  # IEEE 754 strict, all checks
    FAST = auto()  # Optimized, fewer checks
    PARANOID = auto()  # All checks + tracing


@dataclass
class TypePromotionRules:
    """Type promotion rules.

    Defines how types are converted when adding
    values of different types.
    """

    # Default hierarchy (from most precise to least precise)
    hierarchy: list[str] = field(
        default_factory=lambda: [
            "Interval",
            "Decimal",
            "Fraction",
            "complex",
            "float",
            "int",
            "bool",
        ]
    )

    # Explicit conversions
    explicit_rules: dict[tuple[str, str], str] = field(
        default_factory=lambda: {
            ("int", "float"): "float",
            ("int", "Decimal"): "Decimal",
            ("int", "Fraction"): "Fraction",
            ("float", "Decimal"): "Decimal",
            ("float", "Fraction"): "Fraction",  # Controversial, but more precise
            ("float", "complex"): "complex",
            ("Decimal", "Fraction"): "Fraction",
        }
    )

    def get_target_type(self, type_a: str, type_b: str) -> str:
        """Determine target type for an operation."""
        # Same type: no conversion
        if type_a == type_b:
            return type_a

        # Explicit rule
        key = (type_a, type_b)
        if key in self.explicit_rules:
            return self.explicit_rules[key]
        key = (type_b, type_a)
        if key in self.explicit_rules:
            return self.explicit_rules[key]

        # Use hierarchy
        try:
            idx_a = self.hierarchy.index(type_a)
            idx_b = self.hierarchy.index(type_b)
            return self.hierarchy[min(idx_a, idx_b)]
        except ValueError:
            # Unknown type: no conversion
            return type_a


@dataclass
class NuclearConfig:
    """Complete addition engine configuration.

    Controls all aspects of computation:
    - Precision mode
    - Error handling
    - Computation backend
    - Tracing and debugging
    """

    # General mode
    math_mode: MathMode = MathMode.STRICT
    precision_mode: PrecisionMode = PrecisionMode.AUTO

    # Error policies
    overflow_policy: OverflowPolicy = OverflowPolicy.RAISE
    nan_policy: NaNPolicy = NaNPolicy.RAISE

    # Precision options
    decimal_precision: int = 50
    ulp_tolerance: int = 4  # ULP tolerance for comparisons

    # Backend
    backend: str = "auto"
    prefer_gpu: bool = False

    # Tracing
    enable_tracing: bool = True
    trace_all_operations: bool = False

    # Vectorization
    vectorize: bool = True
    use_kahan_for_sums: bool = True

    # Types
    type_promotion: TypePromotionRules = field(default_factory=TypePromotionRules)

    # Units (pint)
    enable_units: bool = True

    # Symbolic mode
    enable_symbolic_fallback: bool = False

    # Determinism
    deterministic: bool = True

    # Stochastic rounding
    stochastic_rounding: bool = False
    stochastic_seed: int | None = None

    def __post_init__(self) -> None:
        """Initialize configuration dependencies."""
        if self.precision_mode == PrecisionMode.DECIMAL:
            getcontext().prec = self.decimal_precision

    @classmethod
    def strict(cls) -> NuclearConfig:
        """Preset: strict IEEE 754 mode."""
        return cls(
            math_mode=MathMode.STRICT,
            overflow_policy=OverflowPolicy.RAISE,
            nan_policy=NaNPolicy.RAISE,
        )

    @classmethod
    def fast(cls) -> NuclearConfig:
        """Preset: fast mode, fewer checks."""
        return cls(
            math_mode=MathMode.FAST,
            overflow_policy=OverflowPolicy.INF,
            nan_policy=NaNPolicy.PROPAGATE,
            enable_tracing=False,
        )

    @classmethod
    def paranoid(cls) -> NuclearConfig:
        """Preset: paranoid mode, all checks."""
        return cls(
            math_mode=MathMode.PARANOID,
            overflow_policy=OverflowPolicy.RAISE,
            nan_policy=NaNPolicy.RAISE,
            enable_tracing=True,
            trace_all_operations=True,
            precision_mode=PrecisionMode.INTERVAL,
        )

    @classmethod
    def scientific(cls, precision: int = 100) -> NuclearConfig:
        """Preset: high precision scientific computation."""
        return cls(
            precision_mode=PrecisionMode.DECIMAL,
            decimal_precision=precision,
            use_kahan_for_sums=True,
            enable_tracing=True,
        )


# =============================================================================
# EXECUTION ENGINE
# =============================================================================


class NuclearEngine:
    """Execution engine for paranoid numerical computation.

    Handles:
    - Backend selection
    - Type conversion
    - Error checking
    - Tracing
    - Optimizations
    """

    def __init__(self, config: NuclearConfig | None = None):
        self.config = config or NuclearConfig()
        self._backend: Backend | None = None
        self._tracer: NumericTracer | None = None
        self._precision_analyzer = PrecisionAnalyzer()
        self._overflow_detector = OverflowDetector()

        # Cache for type conversions
        self._type_converters: dict[str, Callable] = {
            "int": int,
            "float": float,
            "Decimal": Decimal,
            "Fraction": Fraction,
            "complex": complex,
        }

        # Pint for units
        self._ureg = None
        if self.config.enable_units:
            try:
                from pint import UnitRegistry

                self._ureg = UnitRegistry()
            except ImportError:
                pass

        # SymPy for symbolic fallback
        self._sympy = None
        if self.config.enable_symbolic_fallback:
            try:
                import sympy

                self._sympy = sympy
            except ImportError:
                pass

    @property
    def backend(self) -> Backend:
        """Lazy-load backend."""
        if self._backend is None:
            self._backend = get_backend(
                self.config.backend,
                precision=self.config.decimal_precision if self.config.backend == "decimal" else 50,
            )
        return self._backend

    @property
    def tracer(self) -> NumericTracer:
        """Get tracer."""
        if self._tracer is None:
            self._tracer = get_global_tracer()
        return self._tracer

    def add(self, a: Any, b: Any) -> Any:
        """Perform addition with all checks."""
        # Paranoid mode: trace input
        if self.config.trace_all_operations:
            self.tracer.log_error(
                ErrorType.PRECISION_LOSS,
                ErrorSeverity.DEBUG,
                "add_start",
                (a, b),
                None,
                message=f"Addition start: {type(a).__name__} + {type(b).__name__}",
            )

        # Special type handling
        result = self._handle_special_types(a, b)
        if result is not None:
            return result

        # Input validation
        self._validate_inputs(a, b)

        # Type promotion
        a_conv, b_conv = self._promote_types(a, b)

        # Pre-operation check (predictive overflow)
        if self.config.math_mode in (MathMode.STRICT, MathMode.PARANOID):
            self._check_pre_operation(a_conv, b_conv)

        # Calcul effectif
        result = self._compute_add(a_conv, b_conv)

        # Vérification post-opération
        result = self._check_post_operation(a_conv, b_conv, result)

        # Arrondi stochastique si activé
        if self.config.stochastic_rounding and isinstance(result, float):
            result = StochasticValue._stochastic_round(result, self.config.stochastic_seed)

        return result

    def _handle_special_types(self, a: Any, b: Any) -> Any | None:
        """Handle special types (Interval, DualNumber, etc.)."""
        # Interval arithmetic
        if isinstance(a, Interval) or isinstance(b, Interval):
            if not isinstance(a, Interval):
                a = Interval.from_value(float(a))
            if not isinstance(b, Interval):
                b = Interval.from_value(float(b))
            return a + b

        # Dual numbers (autodiff)
        if isinstance(a, DualNumber) or isinstance(b, DualNumber):
            if not isinstance(a, DualNumber):
                a = DualNumber.constant(float(a))
            if not isinstance(b, DualNumber):
                b = DualNumber.constant(float(b))
            return a + b

        # Traced values
        if isinstance(a, TracedValue) or isinstance(b, TracedValue):
            if not isinstance(a, TracedValue):
                a = TracedValue(a)
            if not isinstance(b, TracedValue):
                b = TracedValue(b)
            return a + b

        # Lazy expressions
        if isinstance(a, LazyExpr) or isinstance(b, LazyExpr):
            if not isinstance(a, LazyExpr):
                a = LazyExpr.const(float(a))
            if not isinstance(b, LazyExpr):
                b = LazyExpr.const(float(b))
            return a + b

        # Units (pint)
        if self._ureg is not None:
            from pint import Quantity

            if isinstance(a, Quantity) or isinstance(b, Quantity):
                if not self.config.enable_units:
                    raise TypeError("Units disabled in configuration")
                return a + b

        return None

    def _validate_inputs(self, a: Any, b: Any) -> None:
        """Validate inputs."""
        # Check that they are numbers
        if not isinstance(a, (Number, bool)):
            raise TypeError(f"add() expects a number, got: {type(a).__name__}")
        if not isinstance(b, (Number, bool)):
            raise TypeError(f"add() expects a number, got: {type(b).__name__}")

    def _promote_types(self, a: Any, b: Any) -> tuple[Any, Any]:
        """Apply type promotion rules."""
        type_a = type(a).__name__
        type_b = type(b).__name__

        # Determine target type
        target_type = self.config.type_promotion.get_target_type(type_a, type_b)

        # Force precision mode if configured
        if self.config.precision_mode == PrecisionMode.DECIMAL:
            target_type = "Decimal"
        elif self.config.precision_mode == PrecisionMode.FRACTION:
            target_type = "Fraction"

        # Convert if necessary
        if target_type in self._type_converters:
            converter = self._type_converters[target_type]
            try:
                a = converter(str(a) if target_type in ("Decimal", "Fraction") else a)
                b = converter(str(b) if target_type in ("Decimal", "Fraction") else b)
            except (ValueError, TypeError) as e:
                self.tracer.log_error(
                    ErrorType.TYPE_COERCION,
                    ErrorSeverity.WARNING,
                    "type_promotion",
                    (a, b),
                    None,
                    message=f"Conversion failure to {target_type}: {e}",
                )

        return a, b

    def _check_pre_operation(self, a: Any, b: Any) -> None:
        """Pre-operation checks."""
        # Check overflow risk
        if (
            isinstance(a, float)
            and isinstance(b, float)
            and OverflowDetector.will_overflow_add(a, b)
            and self.config.overflow_policy == OverflowPolicy.RAISE
        ):
            raise OverflowError(f"Predicted overflow: {a} + {b}")
        elif (
            isinstance(a, float)
            and isinstance(b, float)
            and OverflowDetector.will_overflow_add(a, b)
        ):
            self.tracer.log_error(
                ErrorType.OVERFLOW,
                ErrorSeverity.WARNING,
                "add_pre",
                (a, b),
                None,
                message="Predicted overflow",
            )

    def _compute_add(self, a: Any, b: Any) -> Any:
        """Perform addition."""
        # Fast mode: direct operator
        if self.config.math_mode == MathMode.FAST:
            return operator.add(a, b)

        # Use backend if vectorized
        if hasattr(a, "__len__") and self.config.vectorize:
            return self.backend.add(a, b)

        # Standard addition
        return a + b

    def _check_post_operation(self, a: Any, b: Any, result: Any) -> Any:
        """Post-operation checks."""
        # Fast mode: no checks
        if self.config.math_mode == MathMode.FAST:
            return result

        # Check NaN
        if isinstance(result, float) and math.isnan(result):
            if self.config.nan_policy == NaNPolicy.RAISE:
                raise ArithmeticError(f"NaN produced: {a} + {b}")
            elif self.config.nan_policy == NaNPolicy.REPLACE:
                result = 0.0

            self.tracer.log_error(
                ErrorType.NAN_PRODUCED, ErrorSeverity.ERROR, "add", (a, b), result
            )

        # Check overflow
        if (
            isinstance(result, float)
            and math.isinf(result)
            and not (isinstance(a, float) and math.isinf(a))
            and not (isinstance(b, float) and math.isinf(b))
        ):
            if self.config.overflow_policy == OverflowPolicy.RAISE:
                raise OverflowError(f"Overflow: {a} + {b} = inf")
            elif self.config.overflow_policy == OverflowPolicy.SATURATE:
                result = math.copysign(1.7976931348623157e308, result)

            self.tracer.log_error(ErrorType.OVERFLOW, ErrorSeverity.ERROR, "add", (a, b), result)

        # Check precision (paranoid mode)
        if self.config.math_mode == MathMode.PARANOID:
            event = self._precision_analyzer.check_addition(
                float(a) if isinstance(a, Real) else 0,
                float(b) if isinstance(b, Real) else 0,
                float(result) if isinstance(result, Real) else 0,
            )
            if event:
                self.tracer.log(event)

        return result

    def add_many(self, values: Sequence, use_kahan: bool | None = None) -> Any:
        """Sum of multiple values.

        Args:
            values: Sequence of values to sum
            use_kahan: Force Kahan usage (None = auto)

        """
        if len(values) == 0:
            return 0

        if len(values) == 1:
            return values[0]

        # Determine if using Kahan
        use_kahan = use_kahan if use_kahan is not None else self.config.use_kahan_for_sums

        if use_kahan:
            return self.backend.kahan_sum(values)

        return self.backend.add_many(values)

    def add_interval(self, a: float, b: float, ulp_error: int = 1) -> Interval:
        """Addition with interval arithmetic.

        Returns an interval guaranteeing that the true
        mathematical value is contained within it.
        """
        ia = Interval.from_value(a, ulp_error)
        ib = Interval.from_value(b, ulp_error)
        return ia + ib

    def add_autodiff(self, a: float, b: float, grad_a: bool = True) -> DualNumber:
        """Addition with automatic differentiation.

        Args:
            a: First operand
            b: Second operand
            grad_a: If True, compute df/da, else df/db

        """
        if grad_a:
            da = DualNumber.variable(a)
            db = DualNumber.constant(b)
        else:
            da = DualNumber.constant(a)
            db = DualNumber.variable(b)

        return da + db

    def add_symbolic(self, a: Any, b: Any) -> Any:
        """Symbolic addition (fallback).

        Uses SymPy for exact symbolic computation.
        """
        if self._sympy is None:
            raise RuntimeError("SymPy not available")

        return self._sympy.Add(self._sympy.sympify(a), self._sympy.sympify(b))


# =============================================================================
# MAIN FUNCTION
# =============================================================================

# Default global engine
_default_engine: NuclearEngine | None = None


def get_engine() -> NuclearEngine:
    """Get default engine."""
    global _default_engine
    if _default_engine is None:
        _default_engine = NuclearEngine()
    return _default_engine


def set_engine(engine: NuclearEngine) -> None:
    """Set default engine."""
    global _default_engine
    _default_engine = engine


# Type hints pour les overloads
T = TypeVar("T", bound=Number)


@overload
def add(a: Decimal, b: Decimal, **kwargs: Any) -> Decimal: ...
@overload
def add(a: Fraction, b: Fraction, **kwargs: Any) -> Fraction: ...
@overload
def add(a: complex, b: complex, **kwargs: Any) -> complex: ...
@overload
def add(a: Interval, b: Interval, **kwargs: Any) -> Interval: ...
@overload
def add(a: DualNumber, b: DualNumber, **kwargs: Any) -> DualNumber: ...
@overload
def add(a: Real, b: Real, **kwargs: Any) -> float: ...
@overload
def add(a: Sequence, b: Sequence, **kwargs: Any) -> Sequence: ...
@overload
def add(a: T, b: T, **kwargs: Any) -> T: ...


def add(  # type: ignore[misc]
    a: Any,
    b: Any,
    *,
    # Mode
    mode: Literal["strict", "fast", "paranoid"] = "strict",
    precision: Literal["auto", "float64", "decimal", "fraction", "interval"] = "auto",
    # Policies
    overflow: Literal["raise", "inf", "saturate", "wrap"] = "raise",
    nan: Literal["raise", "propagate", "replace"] = "raise",
    # Options
    vectorize: bool = True,
    units: bool = True,
    trace: bool = True,
    kahan: bool = True,
    # Advanced
    stochastic: bool = False,
    symbolic_fallback: bool = False,
    # Custom configuration
    config: NuclearConfig | None = None,
    engine: NuclearEngine | None = None,
) -> Any:
    """Safe and generic addition.

    The most paranoid addition function ever created.

    Args:
        a: First operand
        b: Second operand
        mode: Computation mode ("strict", "fast", "paranoid")
        precision: Precision mode
        overflow: Overflow policy
        nan: NaN policy
        vectorize: Enable vectorization
        units: Support units (pint)
        trace: Enable tracing
        kahan: Use Kahan for sums
        stochastic: Stochastic rounding
        symbolic_fallback: SymPy fallback
        config: Complete custom configuration
        engine: Custom engine

    Returns:
        Addition result

    Raises:
        TypeError: If types are not numeric
        OverflowError: If overflow and policy="raise"
        ArithmeticError: If NaN and policy="raise"

    Examples:
        >>> add(0.1, 0.2, precision="decimal")

        Decimal('0.3')

        >>> add(1e308, 1e308)
        OverflowError: Overflow: 1e+308 + 1e+308 = inf

        >>> add(1e308, 1e308, overflow="inf")
        inf

        >>> add([1, 2, 3], [4, 5, 6])
        [5, 7, 9]

        >>> from pint import UnitRegistry
        >>> ureg = UnitRegistry()
        >>> add(10 * ureg.meter, 5 * ureg.meter)
        15 meter

    """
    # Use provided config or create one
    if config is None:
        # Map strings to enums
        mode_map = {
            "strict": MathMode.STRICT,
            "fast": MathMode.FAST,
            "paranoid": MathMode.PARANOID,
        }
        precision_map = {
            "auto": PrecisionMode.AUTO,
            "float64": PrecisionMode.FLOAT64,
            "decimal": PrecisionMode.DECIMAL,
            "fraction": PrecisionMode.FRACTION,
            "interval": PrecisionMode.INTERVAL,
        }
        overflow_map = {
            "raise": OverflowPolicy.RAISE,
            "inf": OverflowPolicy.INF,
            "saturate": OverflowPolicy.SATURATE,
            "wrap": OverflowPolicy.WRAP,
        }
        nan_map = {
            "raise": NaNPolicy.RAISE,
            "propagate": NaNPolicy.PROPAGATE,
            "replace": NaNPolicy.REPLACE,
        }

        config = NuclearConfig(
            math_mode=mode_map[mode],
            precision_mode=precision_map[precision],
            overflow_policy=overflow_map[overflow],
            nan_policy=nan_map[nan],
            vectorize=vectorize,
            enable_units=units,
            enable_tracing=trace,
            use_kahan_for_sums=kahan,
            stochastic_rounding=stochastic,
            enable_symbolic_fallback=symbolic_fallback,
        )

    # Use provided engine or create one
    if engine is None:
        engine = NuclearEngine(config)

    # Sequence handling (vectorization)
    if config.vectorize and _is_sequence(a):
        if not _is_sequence(b):
            # Scalar + vector
            return type(a)(engine.add(x, b) for x in a)
        if len(a) != len(b):
            raise ValueError(f"Incompatible vector sizes: {len(a)} vs {len(b)}")
        return type(a)(engine.add(x, y) for x, y in zip(a, b, strict=True))

    return engine.add(a, b)


def _is_sequence(x: Any) -> bool:
    """Check if x is a sequence (not str/bytes)."""
    return hasattr(x, "__iter__") and not isinstance(x, (str, bytes))


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def sum_safe(
    values: Sequence,
    *,
    precision: Literal["auto", "kahan", "pairwise", "neumaier"] = "kahan",
    **kwargs: Any,
) -> Any:
    """Safe sum of multiple values.

    Args:
        values: Values to sum
        precision: Summation algorithm
        **kwargs: Additional arguments passed to engine

    """
    engine = get_engine()

    if precision == "kahan":
        return engine.backend.kahan_sum(values)
    elif precision == "pairwise":
        from .backends import PythonBackend

        return PythonBackend().pairwise_sum(list(values))
    elif precision == "neumaier":
        from .backends import PythonBackend

        return PythonBackend().neumaier_sum(list(values))
    else:
        return engine.add_many(values)


def add_with_error(a: float, b: float) -> tuple[float, Interval]:
    """Addition also returning error bounds.

    Returns:
        (result, interval containing true value)

    """
    result = a + b
    interval = Interval.from_value(a) + Interval.from_value(b)
    return result, interval


def gradient(f: Callable[[DualNumber], DualNumber], x: float) -> float:
    """Compute gradient of f at x by automatic differentiation.

    Args:
        f: Function to differentiate
        x: Point to compute gradient

    Returns:
        Gradient value f'(x)

    """
    dual_x = DualNumber.variable(x)
    result = f(dual_x)
    if not isinstance(result, DualNumber):
        raise TypeError("Function must return a DualNumber")
    return result.dual
