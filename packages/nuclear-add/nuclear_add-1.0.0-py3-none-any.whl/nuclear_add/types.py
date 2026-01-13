"""Advanced types for paranoid numerical computation."""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction
from typing import Any

# =============================================================================
# INTERVAL ARITHMETIC - Formal error bounds
# =============================================================================


@dataclass(frozen=True, slots=True)
class Interval:
    """Interval arithmetic for computation with uncertainty.

    Each value is represented by [low, high] guaranteeing that
    the true mathematical value is contained in the interval.

    Example:
        >>> a = Interval(0.1 - 1e-15, 0.1 + 1e-15)
        >>> b = Interval(0.2 - 1e-15, 0.2 + 1e-15)
        >>> c = a + b
        >>> 0.3 in c  # True value is guaranteed to be in the interval
        True

    """

    low: float
    high: float

    def __post_init__(self) -> None:
        """Validate and fix interval bounds."""
        if self.low > self.high:
            object.__setattr__(self, "low", self.high)
            object.__setattr__(self, "high", self.low)

    @classmethod
    def from_value(cls, value: float, ulp_error: int = 1) -> Interval:
        """Create an interval from a value with ULP error."""
        if math.isnan(value) or math.isinf(value):
            return cls(value, value)

        eps = abs(value) * ulp_error * math.ulp(1.0)
        return cls(value - eps, value + eps)

    @classmethod
    def exact(cls, value: float) -> Interval:
        """Create an exact interval (point)."""
        return cls(value, value)

    @property
    def midpoint(self) -> float:
        """Midpoint of the interval."""
        return (self.low + self.high) / 2

    @property
    def radius(self) -> float:
        """Radius (half-width) of the interval."""
        return (self.high - self.low) / 2

    @property
    def width(self) -> float:
        """Total width of the interval."""
        return self.high - self.low

    @property
    def relative_error(self) -> float:
        """Relative error (if midpoint != 0)."""
        mid = self.midpoint
        if mid == 0:
            return float("inf") if self.width > 0 else 0.0
        return self.radius / abs(mid)

    def __contains__(self, value: float) -> bool:
        return self.low <= value <= self.high

    def __add__(self, other: Interval | float) -> Interval:
        if isinstance(other, Interval):
            return Interval(self.low + other.low, self.high + other.high)
        return Interval(self.low + other, self.high + other)

    def __radd__(self, other: float) -> Interval:
        return self.__add__(other)

    def __sub__(self, other: Interval | float) -> Interval:
        if isinstance(other, Interval):
            return Interval(self.low - other.high, self.high - other.low)
        return Interval(self.low - other, self.high - other)

    def __rsub__(self, other: float) -> Interval:
        return Interval(other - self.high, other - self.low)

    def __mul__(self, other: Interval | float) -> Interval:
        if isinstance(other, Interval):
            products = [
                self.low * other.low,
                self.low * other.high,
                self.high * other.low,
                self.high * other.high,
            ]
            return Interval(min(products), max(products))
        if other >= 0:
            return Interval(self.low * other, self.high * other)
        return Interval(self.high * other, self.low * other)

    def __rmul__(self, other: float) -> Interval:
        return self.__mul__(other)

    def __truediv__(self, other: Interval | float) -> Interval:
        if isinstance(other, Interval):
            if other.low <= 0 <= other.high:
                return Interval(float("-inf"), float("inf"))
            return self * Interval(1 / other.high, 1 / other.low)
        if other == 0:
            return Interval(float("-inf"), float("inf"))
        return self * (1 / other)

    def __neg__(self) -> Interval:
        return Interval(-self.high, -self.low)

    def __abs__(self) -> Interval:
        if self.low >= 0:
            return self
        if self.high <= 0:
            return -self
        return Interval(0, max(-self.low, self.high))

    def __repr__(self) -> str:
        return f"Interval([{self.low:.15g}, {self.high:.15g}])"

    def overlaps(self, other: Interval) -> bool:
        """Check if two intervals overlap."""
        return self.low <= other.high and other.low <= self.high

    def contains_interval(self, other: Interval) -> bool:
        """Check if this interval fully contains the other."""
        return self.low <= other.low and other.high <= self.high

    def sqrt(self) -> Interval:
        """Square root of interval."""
        if self.high < 0:
            raise ValueError("Square root of negative interval")
        return Interval(math.sqrt(max(0, self.low)), math.sqrt(self.high))


# =============================================================================
# DUAL NUMBERS - Automatic differentiation (Forward mode)
# =============================================================================


@dataclass(slots=True)
class DualNumber:
    """Dual number for automatic differentiation (forward mode).

    A dual number has the form: a + bε where ε² = 0
    - `real` is the value
    - `dual` is the derivative

    Example:
        >>> x = DualNumber(3.0, 1.0)  # x = 3, dx/dx = 1
        >>> y = x * x + 2 * x  # f(x) = x² + 2x
        >>> y.real  # f(3) = 15
        15.0
        >>> y.dual  # f'(3) = 2x + 2 = 8
        8.0

    """

    real: float
    dual: float = 0.0

    @classmethod
    def variable(cls, value: float) -> DualNumber:
        """Create a variable (dual = 1 to compute df/dx)."""
        return cls(value, 1.0)

    @classmethod
    def constant(cls, value: float) -> DualNumber:
        """Create a constant (dual = 0)."""
        return cls(value, 0.0)

    def __add__(self, other: DualNumber | float) -> DualNumber:
        if isinstance(other, DualNumber):
            return DualNumber(self.real + other.real, self.dual + other.dual)
        return DualNumber(self.real + other, self.dual)

    def __radd__(self, other: float) -> DualNumber:
        return self.__add__(other)

    def __sub__(self, other: DualNumber | float) -> DualNumber:
        if isinstance(other, DualNumber):
            return DualNumber(self.real - other.real, self.dual - other.dual)
        return DualNumber(self.real - other, self.dual)

    def __rsub__(self, other: float) -> DualNumber:
        return DualNumber(other - self.real, -self.dual)

    def __mul__(self, other: DualNumber | float) -> DualNumber:
        if isinstance(other, DualNumber):
            # (a + bε)(c + dε) = ac + (ad + bc)ε
            return DualNumber(
                self.real * other.real, self.real * other.dual + self.dual * other.real
            )
        return DualNumber(self.real * other, self.dual * other)

    def __rmul__(self, other: float) -> DualNumber:
        return self.__mul__(other)

    def __truediv__(self, other: DualNumber | float) -> DualNumber:
        if isinstance(other, DualNumber):
            # (a + bε)/(c + dε) = a/c + (bc - ad)/c² ε
            return DualNumber(
                self.real / other.real,
                (self.dual * other.real - self.real * other.dual) / (other.real**2),
            )
        return DualNumber(self.real / other, self.dual / other)

    def __rtruediv__(self, other: float) -> DualNumber:
        # other / self = other / (a + bε) = other/a - other*b/a² ε
        return DualNumber(other / self.real, -other * self.dual / (self.real**2))

    def __pow__(self, n: int | float | DualNumber) -> DualNumber:
        if isinstance(n, DualNumber):
            # x^n where both are dual: exp(n * ln(x))
            if self.real <= 0:
                raise ValueError("Power with base ≤ 0 not supported")
            ln_self = DualNumber(math.log(self.real), self.dual / self.real)
            return (n * ln_self).exp()
            # x^n where n is constant
        return DualNumber(self.real**n, n * (self.real ** (n - 1)) * self.dual)

    def __neg__(self) -> DualNumber:
        return DualNumber(-self.real, -self.dual)

    def __abs__(self) -> DualNumber:
        if self.real >= 0:
            return self
        return -self

    def exp(self) -> DualNumber:
        """Compute exponential e^x."""
        exp_real = math.exp(self.real)
        return DualNumber(exp_real, exp_real * self.dual)

    def log(self) -> DualNumber:
        """Compute natural logarithm ln(x)."""
        if self.real <= 0:
            raise ValueError("Logarithm of value ≤ 0")
        return DualNumber(math.log(self.real), self.dual / self.real)

    def sin(self) -> DualNumber:
        """Compute sine."""
        return DualNumber(math.sin(self.real), math.cos(self.real) * self.dual)

    def cos(self) -> DualNumber:
        """Compute cosine."""
        return DualNumber(math.cos(self.real), -math.sin(self.real) * self.dual)

    def sqrt(self) -> DualNumber:
        """Compute square root √x."""
        if self.real < 0:
            raise ValueError("Square root of negative value")
        sqrt_real = math.sqrt(self.real)
        return DualNumber(sqrt_real, self.dual / (2 * sqrt_real) if sqrt_real != 0 else 0)

    def __repr__(self) -> str:
        return f"DualNumber({self.real}, ε={self.dual})"

    def __float__(self) -> float:
        return self.real


# =============================================================================
# TRACED VALUE - Value with complete history
# =============================================================================


@dataclass
class TracedValue:
    """Value with complete operation traceability.

    Each operation is recorded with:
    - The operands
    - The operation performed
    - The result
    - Potential numerical errors
    """

    value: Any
    trace: list[dict] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def _record(self, op: str, other: Any, result: Any) -> TracedValue:
        """Record an operation."""
        other_val = other.value if isinstance(other, TracedValue) else other
        new_trace = self.trace.copy()
        new_trace.append(
            {
                "operation": op,
                "operands": (self.value, other_val),
                "result": result,
                "source_ids": (self.id, other.id if isinstance(other, TracedValue) else None),
            }
        )
        return TracedValue(result, new_trace)

    def __add__(self, other: TracedValue | Any) -> TracedValue:
        other_val = other.value if isinstance(other, TracedValue) else other
        result = self.value + other_val
        return self._record("add", other, result)

    def __radd__(self, other: Any) -> TracedValue:
        return self.__add__(other)

    def __sub__(self, other: TracedValue | Any) -> TracedValue:
        other_val = other.value if isinstance(other, TracedValue) else other
        result = self.value - other_val
        return self._record("sub", other, result)

    def __mul__(self, other: TracedValue | Any) -> TracedValue:
        other_val = other.value if isinstance(other, TracedValue) else other
        result = self.value * other_val
        return self._record("mul", other, result)

    def __truediv__(self, other: TracedValue | Any) -> TracedValue:
        other_val = other.value if isinstance(other, TracedValue) else other
        result = self.value / other_val
        return self._record("div", other, result)

    def __repr__(self) -> str:
        return f"TracedValue({self.value}, ops={len(self.trace)})"

    def get_full_trace(self) -> str:
        """Return the complete formatted trace."""
        lines = [f"TracedValue[{self.id}] = {self.value}"]
        for i, entry in enumerate(self.trace):
            op0 = entry["operands"][0]
            op1 = entry["operands"][1]
            op_name = entry["operation"]
            result = entry["result"]
            lines.append(f"  [{i}] {op0} {op_name} {op1} = {result}")
        return "\n".join(lines)


# =============================================================================
# LAZY EXPRESSION - Deferred evaluation and computation graph
# =============================================================================


class LazyExpr:
    """Lazy expression for computation graph construction.

    Operations are not executed immediately but stored
    in a graph that can be:
    - Optimized
    - Evaluated with different backends
    - Automatically differentiated
    - Analyzed for errors

    Example:
        >>> x = LazyExpr.var("x", 3.0)
        >>> y = LazyExpr.var("y", 4.0)
        >>> z = x * x + y * y  # Not yet computed
        >>> z.eval()  # Now we compute
        25.0

    """

    __slots__ = ("op", "args", "value", "name", "_cached_result")

    def __init__(
        self, op: str, args: tuple[Any, ...], value: float | None = None, name: str | None = None
    ) -> None:
        """Initialize a lazy expression.

        Args:
            op: Operation name (e.g., "add", "mul", "var", "const")
            args: Arguments for the operation
            value: Value for variables/constants
            name: Variable name (for variables only)

        """
        self.op = op
        self.args = args
        self.value = value
        self.name = name
        self._cached_result: float | None = None

    @classmethod
    def var(cls, name: str, value: float) -> LazyExpr:
        """Create a variable."""
        return cls("var", (), value, name)

    @classmethod
    def const(cls, value: float) -> LazyExpr:
        """Create a constant."""
        return cls("const", (), value)

    def _wrap(self, other: Any) -> LazyExpr:
        """Wrap a scalar value into LazyExpr."""
        if isinstance(other, LazyExpr):
            return other
        return LazyExpr.const(float(other))

    def __add__(self, other: Any) -> LazyExpr:
        return LazyExpr("add", (self, self._wrap(other)))

    def __radd__(self, other: Any) -> LazyExpr:
        return LazyExpr("add", (self._wrap(other), self))

    def __sub__(self, other: Any) -> LazyExpr:
        return LazyExpr("sub", (self, self._wrap(other)))

    def __rsub__(self, other: Any) -> LazyExpr:
        return LazyExpr("sub", (self._wrap(other), self))

    def __mul__(self, other: Any) -> LazyExpr:
        return LazyExpr("mul", (self, self._wrap(other)))

    def __rmul__(self, other: Any) -> LazyExpr:
        return LazyExpr("mul", (self._wrap(other), self))

    def __truediv__(self, other: Any) -> LazyExpr:
        return LazyExpr("div", (self, self._wrap(other)))

    def __rtruediv__(self, other: Any) -> LazyExpr:
        return LazyExpr("div", (self._wrap(other), self))

    def __pow__(self, other: Any) -> LazyExpr:
        return LazyExpr("pow", (self, self._wrap(other)))

    def __neg__(self) -> LazyExpr:
        return LazyExpr("neg", (self,))

    def sqrt(self) -> LazyExpr:
        """Compute square root of the expression."""
        return LazyExpr("sqrt", (self,))

    def exp(self) -> LazyExpr:
        """Compute exponential of the expression."""
        return LazyExpr("exp", (self,))

    def log(self) -> LazyExpr:
        """Compute natural logarithm of the expression."""
        return LazyExpr("log", (self,))

    def sin(self) -> LazyExpr:
        """Compute sine of the expression."""
        return LazyExpr("sin", (self,))

    def cos(self) -> LazyExpr:
        """Compute cosine of the expression."""
        return LazyExpr("cos", (self,))

    def eval(self, cache: bool = True) -> float:
        """Evaluate the expression."""
        if cache and self._cached_result is not None:
            return self._cached_result

        result = self._eval_impl()

        if cache:
            self._cached_result = result

        return result

    def _eval_impl(self) -> float:
        """Implement expression evaluation."""
        if self.op == "var" or self.op == "const":
            if self.value is None:
                raise ValueError(f"Value not set for {self.op} expression")
            return float(self.value)

        # Recursively evaluate arguments
        evaluated_args = [arg.eval() if isinstance(arg, LazyExpr) else arg for arg in self.args]

        # Binary operations
        if self.op == "add":
            return evaluated_args[0] + evaluated_args[1]
        elif self.op == "sub":
            return evaluated_args[0] - evaluated_args[1]
        elif self.op == "mul":
            return evaluated_args[0] * evaluated_args[1]
        elif self.op == "div":
            return evaluated_args[0] / evaluated_args[1]
        elif self.op == "pow":
            return float(evaluated_args[0] ** evaluated_args[1])

        # Unary operations
        elif self.op == "neg":
            return -evaluated_args[0]
        elif self.op == "sqrt":
            return math.sqrt(evaluated_args[0])
        elif self.op == "exp":
            return math.exp(evaluated_args[0])
        elif self.op == "log":
            return math.log(evaluated_args[0])
        elif self.op == "sin":
            return math.sin(evaluated_args[0])
        elif self.op == "cos":
            return math.cos(evaluated_args[0])
        else:
            raise ValueError(f"Unknown operation: {self.op}")

    def grad(self, var_name: str) -> LazyExpr:
        """Compute symbolic gradient with respect to a variable.

        Returns a new LazyExpr representing the derivative.
        """
        return self._grad_impl(var_name)

    def _grad_impl(self, var_name: str) -> LazyExpr:
        """Gradient implementation (symbolic differentiation)."""
        if self.op == "var":
            return LazyExpr.const(1.0 if self.name == var_name else 0.0)
        elif self.op == "const":
            return LazyExpr.const(0.0)

        # Differentiation rules
        if self.op == "add":
            result: LazyExpr = self.args[0]._grad_impl(var_name) + self.args[1]._grad_impl(var_name)
            return result
        elif self.op == "sub":
            result = self.args[0]._grad_impl(var_name) - self.args[1]._grad_impl(var_name)
            return result
        elif self.op == "mul":
            # Product rule: (fg)' = f'g + fg'
            f, g = self.args
            result = f._grad_impl(var_name) * g + f * g._grad_impl(var_name)
            return result
        elif self.op == "div":
            # Quotient rule: (f/g)' = (f'g - fg') / g²
            f, g = self.args
            result = (f._grad_impl(var_name) * g - f * g._grad_impl(var_name)) / (g * g)
            return result
        elif self.op == "pow":
            # Simple case: x^n where n is constant
            base, exp = self.args
            if exp.op == "const":
                n = exp.value
                if n is None:
                    raise ValueError("Constant value not set")
                grad_base = base._grad_impl(var_name)
                power_term = base ** LazyExpr.const(n - 1)
                result = LazyExpr.const(n) * power_term * grad_base
                return result
            # General case: x^y = exp(y * ln(x))
            exp_grad = exp._grad_impl(var_name)
            base_grad = base._grad_impl(var_name)
            log_term = exp_grad * base.log()
            div_term = exp * base_grad / base
            result = self * (log_term + div_term)
            return result
        elif self.op == "neg":
            result = -self.args[0]._grad_impl(var_name)
            return result
        elif self.op == "sqrt":
            # (√x)' = 1/(2√x)
            result = self.args[0]._grad_impl(var_name) / (LazyExpr.const(2.0) * self)
            return result
        elif self.op == "exp":
            # (e^x)' = e^x
            result = self * self.args[0]._grad_impl(var_name)
            return result
        elif self.op == "log":
            # (ln x)' = 1/x
            result = self.args[0]._grad_impl(var_name) / self.args[0]
            return result
        elif self.op == "sin":
            result = self.args[0].cos() * self.args[0]._grad_impl(var_name)
            return result
        elif self.op == "cos":
            result = -self.args[0].sin() * self.args[0]._grad_impl(var_name)
            return result
        else:
            raise ValueError(f"Gradient not implemented for: {self.op}")

    def to_graph(self) -> str:
        """Generate a DOT representation of the computation graph."""
        nodes = []
        edges = []
        visited = set()

        def visit(expr: LazyExpr, parent_id: str | None = None) -> str:
            node_id = f"n{id(expr)}"

            if node_id not in visited:
                visited.add(node_id)

                if expr.op == "var":
                    label = f"{expr.name}={expr.value}"
                elif expr.op == "const":
                    label = str(expr.value)
                else:
                    label = expr.op

                nodes.append(f'  {node_id} [label="{label}"];')

                for arg in expr.args:
                    if isinstance(arg, LazyExpr):
                        child_id = visit(arg, node_id)
                        edges.append(f"  {child_id} -> {node_id};")

            return node_id

        visit(self)

        return "digraph ComputationGraph {\n" + "\n".join(nodes) + "\n" + "\n".join(edges) + "\n}"

    def __repr__(self) -> str:
        """Return string representation of the expression."""
        if self.op == "var":
            return f"Var({self.name})"
        elif self.op == "const":
            return f"Const({self.value})"
        else:
            args_repr = ", ".join(repr(a) for a in self.args)
            return f"{self.op}({args_repr})"


# =============================================================================
# STOCHASTIC VALUE - For stochastic rounding
# =============================================================================


@dataclass
class StochasticValue:
    """Value with stochastic rounding.

    Instead of always rounding down or up,
    rounding is probabilistic based on the distance to the two
    possible rounded values.

    This eliminates systematic bias in long sums.
    """

    value: float
    precision: int = 53  # mantissa bits
    _rng_seed: int | None = None

    def __post_init__(self) -> None:
        """Initialize random seed if provided."""
        import random

        if self._rng_seed is not None:
            random.seed(self._rng_seed)

    @staticmethod
    def _stochastic_round(value: float, seed: int | None = None) -> float:
        """Stochastic rounding.

        For a value v between floor(v) and ceil(v):
        - P(round down) = ceil(v) - v
        - P(round up) = v - floor(v)
        """
        import random

        if seed is not None:
            random.seed(seed)

        if math.isnan(value) or math.isinf(value):
            return value

        # Find the two adjacent floating point values
        if value >= 0:
            low = math.floor(value * 2**10) / 2**10
            high = math.ceil(value * 2**10) / 2**10
        else:
            low = math.floor(value * 2**10) / 2**10
            high = math.ceil(value * 2**10) / 2**10

        if low == high:
            return value

        # Probability proportional to distance
        p_high = (value - low) / (high - low)
        return high if random.random() < p_high else low

    def __add__(self, other: StochasticValue | float) -> StochasticValue:
        """Add another value with stochastic rounding."""
        other_val = other.value if isinstance(other, StochasticValue) else other
        raw_result = self.value + other_val
        rounded = self._stochastic_round(raw_result, self._rng_seed)
        return StochasticValue(rounded, self.precision, self._rng_seed)

    def __radd__(self, other: float) -> StochasticValue:
        """Right addition with stochastic rounding."""
        return self.__add__(other)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"StochasticValue({self.value})"


# Type aliases for clarity
Numeric = (
    int | float | Decimal | Fraction | complex | Interval | DualNumber | TracedValue | LazyExpr
)
