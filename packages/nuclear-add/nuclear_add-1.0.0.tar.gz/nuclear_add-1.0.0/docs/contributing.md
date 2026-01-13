# Contributing Guide

## Project Structure

```
nuclear_add/
├── src/nuclear_add/     # Main source code
├── tests/               # Unit tests
├── docs/                # Documentation
└── .github/workflows/   # CI/CD
```

## Development Workflow

### 1. Setup

```bash
# Clone the project
git clone <repo-url>
cd nuclear_add

# Install dependencies
uv sync --extra dev

# Install the module in development mode
uv pip install -e .
```

### 2. Development

```bash
# Run tests
uv run pytest

# Check linting
uv run ruff check src/ tests/
uv run black --check src/ tests/
uv run mypy src/nuclear_add

# Format code
uv run black src/ tests/
uv run ruff check --fix src/ tests/
```

### 3. Tests

- Write tests for all new features
- Maintain code coverage > 60%
- Tests in `tests/` with `test_` prefix

### 4. Documentation

- Update docstrings for all new functions/classes
- Add examples in `docs/methods_guide.md` if needed
- Update `docs/api_reference.md` for new APIs

## Code Standards

### Type Hints

All functions must have type hints:

```python
def my_function(a: float, b: float) -> float:
    """Description."""
    return a + b
```

### Docstrings

Google style format:

```python
def add(a: Any, b: Any) -> Any:
    """
    Add two numbers safely.
    
    Args:
        a: First operand
        b: Second operand
    
    Returns:
        Sum of a and b
    
    Raises:
        TypeError: If inputs are not numeric
    """
```

### Naming

- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_` prefix

## Adding a New Backend

1. Create a class inheriting from `Backend`
2. Implement all abstract methods
3. Add to registry in `backends.py`
4. Add tests in `tests/test_backends.py`

Example:

```python
class MyBackend(Backend):
    @property
    def name(self) -> str:
        return "mybackend"
    
    @property
    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(...)
    
    def add(self, a, b):
        # Implementation
        pass
```

## Adding a New Type

1. Create the class in `types.py`
2. Add handling in `NuclearEngine._handle_special_types()`
3. Add tests
4. Document in `docs/api_reference.md`

## PR Process

1. Create a branch from `main`
2. Make changes
3. Add tests
4. Verify all tests pass
5. Update documentation
6. Create PR with clear description

## Pre-PR Checklist

- [ ] All tests pass
- [ ] Code coverage maintained
- [ ] Code formatted (black, ruff)
- [ ] Complete type hints
- [ ] Docstrings up to date
- [ ] Documentation updated
- [ ] No mypy warnings
- [ ] Working examples
