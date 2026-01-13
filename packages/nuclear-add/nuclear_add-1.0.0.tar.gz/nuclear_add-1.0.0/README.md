# 🔥 NUCLEAR ADD v1.0.0

> **The most paranoid addition ever created.**

A simple addition? No. A **militarized numerical computation engine**.

```python
from nuclear_add import add

# Normal addition... but better
add(0.1, 0.2)  # It works!

# The classic float problem
0.1 + 0.2 == 0.3  # False (native Python)
add(0.1, 0.2, precision="decimal") == Decimal("0.3")  # True ✓

# Overflow? No more silent surprises
1e308 + 1e308  # inf (native Python, silent)
add(1e308, 1e308)  # OverflowError! (Nuclear Add)
```

---

## 🎯 Why This Project Exists

Because an addition can:
- **Lose precision** (0.1 + 0.2 ≠ 0.3)
- **Overflow silently** (1e308 + 1e308 → inf)
- **Propagate NaN** without warning
- **Accumulate errors** in long sums
- **Hide bugs** in critical scientific code

This module solves **all** these problems.

---

## 🚀 Features

### 1. Precision Modes
```python
add(0.1, 0.2, precision="decimal")   # Decimal('0.3')
add(0.1, 0.2, precision="fraction")  # Fraction(3, 10)
add(0.1, 0.2, precision="interval")  # Interval with error bounds
```

### 2. Error Handling
```python
# Overflow
add(1e308, 1e308, overflow="raise")    # OverflowError
add(1e308, 1e308, overflow="inf")      # inf
add(1e308, 1e308, overflow="saturate") # 1.79e308

# NaN
add(float('nan'), 1, nan="raise")      # ArithmeticError
add(float('nan'), 1, nan="propagate")  # nan
add(float('nan'), 1, nan="replace")    # 0.0
```

### 3. Interval Arithmetic
```python
from nuclear_add.types import Interval

a = Interval.from_value(0.1)
b = Interval.from_value(0.2)
c = a + b
print(0.3 in c)  # True - true value is guaranteed in interval
```

### 4. Automatic Differentiation
```python
from nuclear_add.types import DualNumber
from nuclear_add import gradient

# Gradient computation
def f(x):
    return x * x * x  # f(x) = x³

gradient(f, 2.0)  # 12.0 (= 3×2² = f'(2))
```

### 5. Kahan Summation
```python
from nuclear_add import sum_safe

# Sum of 10 million numbers
values = [1.0] * 10_000_000
sum(values)              # Accumulated rounding error
sum_safe(values)         # Maximum precision with Kahan
```

### 6. Lazy Evaluation
```python
from nuclear_add.types import LazyExpr

x = LazyExpr.var("x", 3.0)
y = LazyExpr.var("y", 4.0)
z = (x * x + y * y).sqrt()  # Not computed yet!

z.eval()        # 5.0 (computed now)
z.grad("x")     # Symbolic gradient
z.to_graph()    # Computation graph DOT
```

### 7. Error Tracing
```python
from nuclear_add.tracing import NumericTracer

tracer = NumericTracer()
# ... computations ...
tracer.get_summary()  # Summary of all anomalies
tracer.to_json()      # Export for analysis
```

### 8. Vectorization
```python
add([1, 2, 3], [4, 5, 6])  # [5, 7, 9]
add([1, 2, 3], 10)         # [11, 12, 13] (broadcasting)
```

### 9. Multiple Backends
```python
from nuclear_add.backends import get_backend

# Pure Python (portable)
get_backend("python")

# NumPy SIMD (vectorized)
get_backend("numpy")

# CuPy GPU (CUDA)
get_backend("cupy")

# Numba JIT (compiled)
get_backend("numba")

# Decimal (arbitrary precision)
get_backend("decimal", precision=100)
```

### 10. Unit Support (Pint)
```python
from pint import UnitRegistry
ureg = UnitRegistry()

add(10 * ureg.meter, 5 * ureg.meter)    # 15 meter
add(10 * ureg.meter, 5 * ureg.second)   # DimensionalityError!
```

---

## 📦 Installation

### Local Development Installation (for use in other projects)

To use this module in other projects without downloading/cloning:

```bash
# Navigate to the project directory
cd C:\Users\jessy\Documents\dev\nuclear_add\nuclear_add

# Install in editable mode (recommended)
uv pip install -e .

# Or with development dependencies
uv pip install -e ".[dev]"
```

Now you can use it in any Python project:

```python
from nuclear_add import add
result = add(2, 3)  # 5
```

### From Another Project

If you're in another project and want to use nuclear_add:

```bash
# Install from local path
uv pip install -e C:\Users\jessy\Documents\dev\nuclear_add\nuclear_add

# Or add to PYTHONPATH
# Windows PowerShell:
$env:PYTHONPATH = "C:\Users\jessy\Documents\dev\nuclear_add\nuclear_add\src;$env:PYTHONPATH"
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/example/nuclear-add.git
cd nuclear-add

# Install dependencies (base)
uv sync

# Install with development dependencies
uv sync --extra dev

# Run the demo
uv run python -m nuclear_add.demo

# Run tests
uv run pytest
```

### Using pip

```bash
# Base installation
pip install nuclear-add

# With NumPy
pip install nuclear-add[numpy]

# With GPU support
pip install nuclear-add[gpu]

# With JIT compilation
pip install nuclear-add[jit]

# With units
pip install nuclear-add[units]

# With symbolic fallback
pip install nuclear-add[symbolic]

# Install everything
pip install nuclear-add[all]
```

---

## 🎮 Configuration Presets

```python
from nuclear_add.core import NuclearConfig, NuclearEngine

# Strict mode (default)
config = NuclearConfig.strict()

# Fast mode (fewer checks)
config = NuclearConfig.fast()

# Paranoid mode (ALL checks)
config = NuclearConfig.paranoid()

# Scientific mode (high precision)
config = NuclearConfig.scientific(precision=100)

# Use with custom engine
engine = NuclearEngine(config)
engine.add(a, b)
```

---

## 🔬 Use Cases

### Finance / Trading
```python
# No surprises with amounts
add(Decimal("100.50"), Decimal("0.25"), precision="decimal")
```

### Scientific Computing
```python
# Precise sums of large series
sum_safe(measurements, precision="kahan")
```

### Physics Simulation
```python
# Uncertainty propagation
pos = Interval.from_value(initial_pos, ulp_error=1)
for dt in time_steps:
    pos = add(pos, velocity * dt)
print(f"Final position: {pos}, uncertainty: {pos.width}")
```

### Machine Learning
```python
# Automatic gradients
loss = compute_loss(DualNumber.variable(weight))
gradient = loss.dual
```

---

## 📊 Comparison

| Operation | Native Python | Nuclear Add |
|-----------|-------------|-------------|
| `0.1 + 0.2` | `0.30000000000000004` | `Decimal('0.3')` |
| `1e308 + 1e308` | `inf` (silent) | `OverflowError` |
| `nan + 1` | `nan` (propagates) | `ArithmeticError` |
| Sum of 10M values | Accumulated errors | Kahan compensated |
| Gradient of f(x) | Finite differences | Exact autodiff |

---

## 🧪 Testing

```bash
# Run tests with uv
uv run pytest tests/ -v --cov=src/nuclear_add

# Or with pip
pytest tests/ -v --cov=nuclear_add
```

---

## 📚 Documentation

Documentation complète disponible dans le dossier `docs/` :

- **[Index](docs/index.md)** - Point d'entrée de la documentation
- **[Architecture](docs/architecture.md)** - Vue d'ensemble de l'architecture
- **[API Reference](docs/api_reference.md)** - Documentation complète de l'API
- **[Guide des méthodes](docs/methods_guide.md)** - Exemples pratiques
- **[Décisions de conception](docs/design_decisions.md)** - Choix techniques
- **[Diagrammes](docs/diagrams.md)** - Schémas et diagrammes visuels (Mermaid)
- **[Guide de contribution](docs/contributing.md)** - Comment contribuer

## 🛠️ Development

### Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/example/nuclear-add.git
cd nuclear-add

# Install dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run linters
uv run ruff check src/ tests/
uv run black --check src/ tests/
uv run mypy src/nuclear_add
```

### Project Structure

```
nuclear_add/
├── src/
│   └── nuclear_add/
│       ├── __init__.py
│       ├── core.py          # Core engine and configuration
│       ├── types.py          # Advanced types (Interval, DualNumber, etc.)
│       ├── backends.py       # Computation backends
│       ├── tracing.py         # Error tracing system
│       └── demo.py           # Demonstration script
├── tests/
│   ├── test_core.py
│   ├── test_types.py
│   ├── test_backends.py
│   └── test_tracing.py
├── docs/
│   ├── index.md              # Documentation index
│   ├── architecture.md       # System architecture
│   ├── api_reference.md      # Complete API reference
│   ├── methods_guide.md      # Practical usage guide
│   ├── design_decisions.md   # Design decisions
│   ├── diagrams.md           # Visual diagrams
│   └── contributing.md       # Contributing guide
├── .github/
│   └── workflows/
│       └── ci.yml            # CI/CD configuration
├── pyproject.toml            # Project configuration
├── README.md                 # This file
└── CHANGELOG.md              # Changelog
```

---

## 📜 License

MIT - Use this code for whatever you want.

---

## 🤔 FAQ

**Q: Is this really useful?**
A: For 99.9% of cases, use `+`. For the critical 0.1% (finance, science, simulations), yes.

**Q: Isn't this overkill?**
A: That's **literally** the point of the project.

**Q: Performance?**
A: `fast` mode = quasi-native. `paranoid` mode = 10-100x slower but bulletproof.

**Q: Why does `add(1e308, 1e308)` raise an error?**
A: Because `inf` is not a valid mathematical result. If you want `inf`, use `overflow="inf"`.

---

## 🙏 Credits

Inspired by:
- Universal frustration with `0.1 + 0.2`
- Silent bugs in numerical code
- The desire to truly understand how floats work
- A ChatGPT conversation that got out of hand

---

**Made with 🔥 and an unhealthy obsession with numerical precision.**
