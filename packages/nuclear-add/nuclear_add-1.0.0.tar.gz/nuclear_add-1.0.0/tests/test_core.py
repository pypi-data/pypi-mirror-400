"""Tests for core functionality."""

from decimal import Decimal
from fractions import Fraction

import pytest

from nuclear_add import add, gradient, sum_safe
from nuclear_add.core import NuclearConfig, NuclearEngine


class TestBasicAddition:
    """Test basic addition functionality."""

    def test_integer_addition(self):
        """Test addition of integers."""
        assert add(2, 3) == 5
        assert add(-10, 25) == 15

    def test_float_addition(self):
        """Test addition of floats."""
        assert add(1.5, 2.5) == 4.0
        assert add(0.1, 0.2) == pytest.approx(0.3)

    def test_decimal_precision(self):
        """Test decimal precision mode."""
        result = add(Decimal("0.1"), Decimal("0.2"))
        assert result == Decimal("0.3")

    def test_fraction_precision(self):
        """Test fraction precision mode."""
        result = add(Fraction(1, 3), Fraction(1, 6))
        assert result == Fraction(1, 2)

    def test_complex_addition(self):
        """Test addition of complex numbers."""
        result = add(1 + 2j, 3 + 4j)
        assert result == 4 + 6j


class TestOverflowHandling:
    """Test overflow handling."""

    def test_overflow_raise(self):
        """Test overflow raises exception by default."""
        with pytest.raises(OverflowError):
            add(1e308, 1e308)

    def test_overflow_inf(self):
        """Test overflow returns inf."""
        result = add(1e308, 1e308, overflow="inf")
        assert result == float("inf")

    def test_overflow_saturate(self):
        """Test overflow saturation."""
        result = add(1e308, 1e308, overflow="saturate")
        assert result < float("inf")


class TestNaNHandling:
    """Test NaN handling."""

    def test_nan_raise(self):
        """Test NaN raises exception by default."""
        with pytest.raises(ArithmeticError):
            add(float("nan"), 1)

    def test_nan_propagate(self):
        """Test NaN propagation."""
        result = add(float("nan"), 1, nan="propagate")
        assert result != result  # NaN comparison

    def test_nan_replace(self):
        """Test NaN replacement."""
        result = add(float("nan"), 1, nan="replace")
        # NaN + 1 = NaN, which gets replaced by 0.0
        assert result == 0.0


class TestVectorization:
    """Test vectorization support."""

    def test_vector_addition(self):
        """Test vector addition."""
        result = add([1, 2, 3], [4, 5, 6])
        assert list(result) == [5, 7, 9]

    def test_broadcasting(self):
        """Test broadcasting."""
        result = add([1, 2, 3], 10)
        assert list(result) == [11, 12, 13]


class TestSumSafe:
    """Test safe summation."""

    def test_kahan_sum(self):
        """Test Kahan summation."""
        values = [1.0] * 1000
        result = sum_safe(values, precision="kahan")
        assert result == pytest.approx(1000.0)

    def test_pairwise_sum(self):
        """Test pairwise summation."""
        values = [0.1] * 100
        result = sum_safe(values, precision="pairwise")
        assert result == pytest.approx(10.0)


class TestGradient:
    """Test automatic differentiation."""

    def test_simple_gradient(self):
        """Test simple gradient computation."""

        def f(x: float) -> float:
            return x * x * x  # f(x) = x³

        grad = gradient(f, 2.0)  # f'(2) = 3×2² = 12
        assert grad == pytest.approx(12.0)


class TestConfig:
    """Test configuration presets."""

    def test_strict_config(self):
        """Test strict configuration."""
        config = NuclearConfig.strict()
        assert config.math_mode.name == "STRICT"
        assert config.overflow_policy.name == "RAISE"

    def test_fast_config(self):
        """Test fast configuration."""
        config = NuclearConfig.fast()
        assert config.math_mode.name == "FAST"

    def test_paranoid_config(self):
        """Test paranoid configuration."""
        config = NuclearConfig.paranoid()
        assert config.math_mode.name == "PARANOID"
        assert config.trace_all_operations is True

    def test_scientific_config(self):
        """Test scientific configuration."""
        config = NuclearConfig.scientific(precision=100)
        assert config.precision_mode.name == "DECIMAL"
        assert config.decimal_precision == 100


class TestEngine:
    """Test engine functionality."""

    def test_engine_creation(self):
        """Test engine creation."""
        engine = NuclearEngine()
        assert engine is not None

    def test_engine_add(self):
        """Test engine add method."""
        engine = NuclearEngine()
        result = engine.add(2, 3)
        assert result == 5

    def test_custom_config(self):
        """Test engine with custom config."""
        config = NuclearConfig.fast()
        engine = NuclearEngine(config)
        assert engine.config.math_mode.name == "FAST"
