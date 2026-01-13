# Nuclear Add Documentation

Welcome to the complete documentation of Nuclear Add, the most paranoid addition module ever created.

## 📚 Table of Contents

1. [Architecture](architecture.md) - System architecture overview
2. [API Reference](api_reference.md) - Complete API documentation
3. [Methods Guide](methods_guide.md) - Practical usage guide
4. [Design Decisions](design_decisions.md) - Why these choices were made
5. [Diagrams](diagrams.md) - Visual schemas and diagrams (Mermaid)
6. [Contributing Guide](contributing.md) - How to contribute to the project

## 🚀 Quick Start

### Installation

```bash
# Development installation
uv pip install -e .

# Or from another project
uv pip install -e /path/to/nuclear_add
```

### Basic Usage

```python
from nuclear_add import add

# Simple addition
result = add(2, 3)  # 5

# With decimal precision
from decimal import Decimal
result = add(Decimal("0.1"), Decimal("0.2"))  # Decimal('0.3')

# Vectorization
result = add([1, 2, 3], [4, 5, 6])  # [5, 7, 9]
```

## 🎯 Main Use Cases

### 1. Financial Calculations

```python
from nuclear_add import add
from decimal import Decimal

amount1 = Decimal("100.50")
amount2 = Decimal("0.25")
total = add(amount1, amount2)  # Decimal('100.75')
```

### 2. Scientific Computing

```python
from nuclear_add import sum_safe

# Precise sum of measurements
measurements = [0.1, 0.2, 0.3, ...]  # 1000 values
total = sum_safe(measurements, precision="kahan")
```

### 3. Machine Learning

```python
from nuclear_add import gradient

def loss_function(weight):
    return weight * weight * weight

grad = gradient(loss_function, 2.0)  # Automatic gradient
```

### 4. Physics Simulation

```python
from nuclear_add.types import Interval

# Uncertainty propagation
position = Interval.from_value(1.0, ulp_error=1)
velocity = Interval.from_value(0.1, ulp_error=1)

for dt in time_steps:
    position = position + velocity * dt

print(f"Position: {position}, Uncertainty: {position.width}")
```

## 📖 Documentation Structure

- **Architecture** : Understand how the system is built
- **API Reference** : Complete documentation of all functions and classes
- **Methods Guide** : Practical examples for each feature
- **Design Decisions** : Understand technical choices

## 🔗 Useful Links

- [Main README](../README.md)
- [Changelog](../CHANGELOG.md)

## 💡 Key Concepts

### Precision Modes

- `auto` : Automatic detection
- `float64` : IEEE 754 double precision
- `decimal` : Arbitrary precision
- `fraction` : Exact (rational)
- `interval` : Interval arithmetic

### Computation Modes

- `strict` : All checks enabled (default)
- `fast` : Optimized, fewer checks
- `paranoid` : All checks + complete tracing

### Error Policies

- `raise` : Raise an exception (default)
- `inf` / `propagate` : Return a special value
- `saturate` / `replace` : Replace with a safe value

## 🎓 Learn by Example

See [methods_guide.md](methods_guide.md) for detailed examples of each feature.

## 🤝 Contributing

To contribute to the project, see the main README and design decisions to understand the project philosophy.
