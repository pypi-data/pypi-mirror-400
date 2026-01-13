# Methods Guide

## Addition Methods

### 1. Basic Addition

```python
from nuclear_add import add

# Integers
add(2, 3)  # 5

# Floats
add(1.5, 2.5)  # 4.0

# Complex numbers
add(1+2j, 3+4j)  # (4+6j)
```

### 2. Addition with Controlled Precision

```python
from decimal import Decimal
from fractions import Fraction

# Arbitrary decimal precision
add(Decimal("0.1"), Decimal("0.2"))  # Decimal('0.3')

# Exact fractions
add(Fraction(1, 3), Fraction(1, 6))  # Fraction(1, 2)

# Force a precision mode
add(0.1, 0.2, precision="decimal")  # Decimal('0.3')
add(0.1, 0.2, precision="fraction")  # Fraction(3, 10)
```

### 3. Addition with Error Handling

```python
# Overflow - raise exception (default)
try:
    add(1e308, 1e308)
except OverflowError:
    print("Overflow detected!")

# Overflow - return inf
add(1e308, 1e308, overflow="inf")  # inf

# Overflow - saturate
add(1e308, 1e308, overflow="saturate")  # ~1.79e308

# NaN - raise exception (default)
try:
    add(float('nan'), 1)
except ArithmeticError:
    print("NaN detected!")

# NaN - propagate
add(float('nan'), 1, nan="propagate")  # nan

# NaN - replace
add(float('nan'), 1, nan="replace")  # 0.0
```

### 4. Vectorized Addition

```python
# Vector + Vector
add([1, 2, 3], [4, 5, 6])  # [5, 7, 9]

# Broadcasting (scalar + vector)
add([1, 2, 3], 10)  # [11, 12, 13]

# Tuples
add((1.5, 2.5), (3.5, 4.5))  # (5.0, 7.0)
```

## Summation Methods

### 1. Safe Sum (Kahan)

```python
from nuclear_add import sum_safe

values = [0.1] * 100
result = sum_safe(values, precision="kahan")  # 10.0 (precise)
```

### 2. Pairwise Sum

```python
result = sum_safe(values, precision="pairwise")  # Good speed/precision trade-off
```

### 3. Neumaier Sum

```python
result = sum_safe(values, precision="neumaier")  # Kahan improvement
```

## Differentiation Methods

### 1. Automatic Gradient

```python
from nuclear_add import gradient

def f(x):
    return x * x * x  # f(x) = x³

grad = gradient(f, 2.0)  # 12.0 (= 3×2²)
```

### 2. Dual Numbers

```python
from nuclear_add.types import DualNumber

x = DualNumber.variable(3.0)  # x = 3, dx/dx = 1
y = x * x + 2 * x  # f(x) = x² + 2x
print(y.real)  # 15.0 (= f(3))
print(y.dual)  # 8.0 (= f'(3) = 2x + 2)
```

### 3. Symbolic Gradient (LazyExpr)

```python
from nuclear_add.types import LazyExpr

x = LazyExpr.var("x", 2.0)
y = x * x  # f(x) = x²
grad = y.grad("x")
print(grad.eval())  # 4.0 (= 2x)
```

## Interval Methods

### 1. Interval Creation

```python
from nuclear_add.types import Interval

# From a value with ULP error
a = Interval.from_value(0.1, ulp_error=1)

# Exact interval
b = Interval.exact(0.2)

# Manual interval
c = Interval(0.99, 1.01)  # 1.0 ± 0.01
```

### 2. Interval Operations

```python
a = Interval.from_value(0.1)
b = Interval.from_value(0.2)
c = a + b

# Check membership
print(0.3 in c)  # True

# Properties
print(c.midpoint)  # 0.3
print(c.width)  # Interval width
print(c.relative_error)  # Relative error
```

### 3. Uncertainty Propagation

```python
# Simulate a computation chain
pos = Interval.from_value(1.0, ulp_error=1)
for i in range(10):
    pos = pos + Interval.from_value(0.1, ulp_error=1)

print(f"Final position: {pos}")
print(f"Uncertainty: {pos.width}")
```

## Configuration Methods

### 1. Configuration Presets

```python
from nuclear_add.core import NuclearConfig, NuclearEngine

# Strict mode (default)
config = NuclearConfig.strict()
engine = NuclearEngine(config)

# Fast mode
config = NuclearConfig.fast()

# Paranoid mode
config = NuclearConfig.paranoid()

# Scientific mode
config = NuclearConfig.scientific(precision=100)
```

### 2. Custom Configuration

```python
from nuclear_add.core import NuclearConfig, MathMode, PrecisionMode

config = NuclearConfig(
    math_mode=MathMode.PARANOID,
    precision_mode=PrecisionMode.DECIMAL,
    decimal_precision=200,
    enable_tracing=True,
    trace_all_operations=True,
)
```

## Tracing Methods

### 1. Basic Usage

```python
from nuclear_add.tracing import NumericTracer

tracer = NumericTracer()

# ... perform operations ...
from nuclear_add import add
add(1e308, 1e308, overflow="inf")

# Get summary
summary = tracer.get_summary()
print(summary)
```

### 2. Event Filtering

```python
from nuclear_add.tracing import ErrorType, ErrorSeverity

# By type
overflow_events = tracer.get_by_type(ErrorType.OVERFLOW)

# By minimum severity
errors = tracer.get_by_severity(ErrorSeverity.ERROR)
```

### 3. JSON Export

```python
json_data = tracer.to_json()
# Save or analyze
```

## Backend Methods

### 1. Manual Selection

```python
from nuclear_add.backends import get_backend

backend = get_backend("python")
result = backend.add(2, 3)

backend = get_backend("decimal", precision=100)
result = backend.add("0.1", "0.2")
```

### 2. Automatic Selection

```python
backend = get_backend("auto")  # Chooses best available
```

### 3. List Available Backends

```python
from nuclear_add.backends import list_available_backends

available = list_available_backends()
# ['python', 'numpy'] if NumPy is installed
```

## Advanced Methods

### 1. Lazy Evaluation

```python
from nuclear_add.types import LazyExpr

x = LazyExpr.var("x", 3.0)
y = LazyExpr.var("y", 4.0)
z = (x * x + y * y).sqrt()  # Not computed yet!

result = z.eval()  # 5.0 (computed now)
```

### 2. Computation Graph

```python
expr = x + y
graph = expr.to_graph()  # DOT format
print(graph)
```

### 3. Traced Values

```python
from nuclear_add.types import TracedValue

a = TracedValue(10.0)
b = TracedValue(5.0)
c = a + b
d = c * TracedValue(2.0)

print(d.get_full_trace())  # Complete history
```

### 4. Stochastic Rounding

```python
from nuclear_add.types import StochasticValue

sv = StochasticValue(0.123456789, _rng_seed=42)
# Eliminates systematic bias in long sums
```
