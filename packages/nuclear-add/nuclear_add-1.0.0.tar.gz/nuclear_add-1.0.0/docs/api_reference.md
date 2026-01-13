# API Reference

## Main Functions

### `add(a, b, **kwargs)`

Main safe addition function.

**Parameters:**
- `a` : First operand (number, sequence, or special type)
- `b` : Second operand (number, sequence, or special type)
- `mode` : Computation mode (`"strict"`, `"fast"`, `"paranoid"`)
- `precision` : Precision mode (`"auto"`, `"float64"`, `"decimal"`, `"fraction"`, `"interval"`)
- `overflow` : Overflow policy (`"raise"`, `"inf"`, `"saturate"`, `"wrap"`)
- `nan` : NaN policy (`"raise"`, `"propagate"`, `"replace"`)
- `vectorize` : Enable vectorization (default: `True`)
- `units` : Support Pint units (default: `True`)
- `trace` : Enable tracing (default: `True`)
- `kahan` : Use Kahan for sums (default: `True`)

**Returns:**
- Addition result (type depends on operands)

**Examples:**
```python
add(2, 3)  # 5
add(0.1, 0.2, precision="decimal")  # Decimal('0.3')
add([1, 2, 3], [4, 5, 6])  # [5, 7, 9]
```

**Raises:**
- `TypeError` : If types are not numeric
- `OverflowError` : If overflow and `overflow="raise"`
- `ArithmeticError` : If NaN and `nan="raise"`

---

### `sum_safe(values, precision="kahan", **kwargs)`

Safe sum of multiple values with error compensation.

**Parameters:**
- `values` : Sequence of values to sum
- `precision` : Algorithm (`"kahan"`, `"pairwise"`, `"neumaier"`, `"auto"`)

**Returns:**
- Sum with maximum precision

**Examples:**
```python
values = [0.1] * 100
sum_safe(values, precision="kahan")  # 10.0 (precise)
```

---

### `gradient(f, x)`

Computes the gradient of a function using automatic differentiation.

**Parameters:**
- `f` : Function to differentiate (callable)
- `x` : Point where to compute the gradient

**Returns:**
- Gradient value `f'(x)`

**Examples:**
```python
def f(x):
    return x * x * x

gradient(f, 2.0)  # 12.0 (= 3×2²)
```

---

### `add_with_error(a, b)`

Addition also returning error bounds.

**Parameters:**
- `a` : First operand (float)
- `b` : Second operand (float)

**Returns:**
- Tuple `(result, interval)` containing the true value

**Examples:**
```python
result, bounds = add_with_error(0.1, 0.2)
# result = 0.30000000000000004
# bounds = Interval guaranteeing that 0.3 is inside
```

---

## Main Classes

### `NuclearConfig`

Complete addition engine configuration.

**Class Methods:**
- `strict()` : Strict IEEE 754 mode
- `fast()` : Fast mode, fewer checks
- `paranoid()` : Paranoid mode, all checks
- `scientific(precision=100)` : High precision scientific mode

**Main Attributes:**
- `math_mode` : Computation mode (`MathMode`)
- `precision_mode` : Precision mode (`PrecisionMode`)
- `overflow_policy` : Overflow policy (`OverflowPolicy`)
- `nan_policy` : NaN policy (`NaNPolicy`)
- `decimal_precision` : Decimal precision (int)
- `enable_tracing` : Enable tracing (bool)
- `vectorize` : Enable vectorization (bool)

**Examples:**
```python
config = NuclearConfig.strict()
config = NuclearConfig.paranoid()
config = NuclearConfig.scientific(precision=200)
```

---

### `NuclearEngine`

Execution engine for numerical computation.

**Methods:**
- `add(a, b)` : Main addition
- `add_many(values, use_kahan=None)` : Sum of multiple values
- `add_interval(a, b, ulp_error=1)` : Addition with intervals
- `add_autodiff(a, b, grad_a=True)` : Addition with autodiff
- `add_symbolic(a, b)` : Symbolic addition (SymPy)

**Properties:**
- `backend` : Current backend (lazy-loaded)
- `tracer` : Current tracer
- `config` : Configuration

**Examples:**
```python
engine = NuclearEngine(NuclearConfig.paranoid())
result = engine.add(2, 3)
```

---

## Advanced Types

### `Interval`

Interval arithmetic for uncertainty propagation.

**Class Methods:**
- `from_value(value, ulp_error=1)` : Create from a value
- `exact(value)` : Create an exact interval

**Properties:**
- `low`, `high` : Interval bounds
- `midpoint` : Center point
- `width` : Total width
- `radius` : Radius (half-width)
- `relative_error` : Relative error

**Methods:**
- `overlaps(other)` : Check overlap
- `contains_interval(other)` : Check inclusion
- `sqrt()` : Square root

**Examples:**
```python
a = Interval.from_value(0.1)
b = Interval.from_value(0.2)
c = a + b
print(0.3 in c)  # True
```

---

### `DualNumber`

Dual number for automatic differentiation.

**Class Methods:**
- `variable(value)` : Create a variable (dual=1)
- `constant(value)` : Create a constant (dual=0)

**Properties:**
- `real` : Real value
- `dual` : Derivative

**Methods:**
- `exp()`, `log()`, `sin()`, `cos()`, `sqrt()` : Mathematical functions

**Examples:**
```python
x = DualNumber.variable(3.0)
y = x * x  # f(x) = x²
print(y.real)  # 9.0
print(y.dual)  # 6.0 (= 2x)
```

---

### `LazyExpr`

Lazy expression for computation graphs.

**Class Methods:**
- `var(name, value)` : Create a variable
- `const(value)` : Create a constant

**Methods:**
- `eval()` : Evaluate the expression
- `grad(var_name)` : Compute symbolic gradient
- `to_graph()` : Generate DOT graph

**Examples:**
```python
x = LazyExpr.var("x", 3.0)
y = LazyExpr.var("y", 4.0)
z = (x * x + y * y).sqrt()
print(z.eval())  # 5.0
print(z.grad("x").eval())  # 0.6
```

---

### `TracedValue`

Value with complete operation history.

**Methods:**
- `get_full_trace()` : Get formatted full trace

**Examples:**
```python
a = TracedValue(10.0)
b = TracedValue(5.0)
c = a + b
print(c.get_full_trace())
```

---

## Backends

### `get_backend(name="auto", **kwargs)`

Gets a backend by name.

**Parameters:**
- `name` : Backend name (`"python"`, `"numpy"`, `"cupy"`, `"numba"`, `"decimal"`, `"auto"`)
- `**kwargs` : Constructor arguments (e.g., `precision=100` for Decimal)

**Returns:**
- Backend instance

**Examples:**
```python
backend = get_backend("python")
backend = get_backend("decimal", precision=100)
backend = get_backend("auto")  # Automatic selection
```

---

### `list_available_backends()`

Lists available backends on the system.

**Returns:**
- List of available backend names

**Examples:**
```python
backends = list_available_backends()
# ['python', 'numpy'] if NumPy is installed
```

---

## Tracing

### `NumericTracer`

Numerical error tracer.

**Methods:**
- `log(event)` : Log an event
- `log_error(...)` : Shortcut to create and log
- `clear()` : Clear all events
- `get_by_type(error_type)` : Filter by type
- `get_by_severity(min_severity)` : Filter by severity
- `get_summary()` : Get summary
- `to_json()` : Export to JSON

**Properties:**
- `events` : List of logged events

**Examples:**
```python
tracer = NumericTracer()
# ... operations ...
summary = tracer.get_summary()
print(summary["total_events"])
```

---

### `get_global_tracer()` / `set_global_tracer(tracer)`

Manage the global tracer.

**Examples:**
```python
tracer = get_global_tracer()
tracer.log_error(...)
```
