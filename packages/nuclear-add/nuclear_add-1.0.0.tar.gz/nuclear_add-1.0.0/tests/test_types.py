"""Tests for advanced types."""

import pytest

from nuclear_add.types import (
    DualNumber,
    Interval,
    LazyExpr,
    StochasticValue,
    TracedValue,
)


class TestInterval:
    """Test interval arithmetic."""

    def test_interval_creation(self):
        """Test interval creation."""
        interval = Interval(0.1, 0.2)
        assert interval.low == 0.1
        assert interval.high == 0.2

    def test_interval_from_value(self):
        """Test interval from value."""
        interval = Interval.from_value(0.1)
        assert 0.1 in interval

    def test_interval_addition(self):
        """Test interval addition."""
        a = Interval.from_value(0.1)
        b = Interval.from_value(0.2)
        c = a + b
        assert 0.3 in c

    def test_interval_contains(self):
        """Test interval contains check."""
        interval = Interval(0.0, 1.0)
        assert 0.5 in interval
        assert 1.5 not in interval

    def test_interval_width(self):
        """Test interval width."""
        interval = Interval(0.0, 1.0)
        assert interval.width == 1.0


class TestDualNumber:
    """Test dual numbers."""

    def test_dual_number_creation(self):
        """Test dual number creation."""
        x = DualNumber.variable(3.0)
        assert x.real == 3.0
        assert x.dual == 1.0

    def test_dual_number_constant(self):
        """Test dual number constant."""
        c = DualNumber.constant(5.0)
        assert c.real == 5.0
        assert c.dual == 0.0

    def test_dual_number_addition(self):
        """Test dual number addition."""
        x = DualNumber.variable(3.0)
        y = x + 2.0
        assert y.real == 5.0
        assert y.dual == 1.0

    def test_dual_number_multiplication(self):
        """Test dual number multiplication."""
        x = DualNumber.variable(3.0)
        y = x * x  # f(x) = x²
        assert y.real == 9.0
        assert y.dual == pytest.approx(6.0)  # f'(x) = 2x = 6


class TestTracedValue:
    """Test traced values."""

    def test_traced_value_creation(self):
        """Test traced value creation."""
        tv = TracedValue(10.0)
        assert tv.value == 10.0
        assert len(tv.trace) == 0

    def test_traced_value_operations(self):
        """Test traced value operations."""
        a = TracedValue(10.0)
        b = TracedValue(5.0)
        c = a + b
        assert c.value == 15.0
        assert len(c.trace) > 0


class TestLazyExpr:
    """Test lazy expressions."""

    def test_lazy_expr_creation(self):
        """Test lazy expression creation."""
        x = LazyExpr.var("x", 3.0)
        assert x.name == "x"
        assert x.value == 3.0

    def test_lazy_expr_evaluation(self):
        """Test lazy expression evaluation."""
        x = LazyExpr.var("x", 3.0)
        y = LazyExpr.var("y", 4.0)
        z = x * x + y * y
        result = z.eval()
        assert result == 25.0

    def test_lazy_expr_gradient(self):
        """Test lazy expression gradient."""
        x = LazyExpr.var("x", 2.0)
        y = x * x  # f(x) = x²
        grad = y.grad("x")
        assert grad.eval() == pytest.approx(4.0)  # f'(x) = 2x = 4


class TestStochasticValue:
    """Test stochastic values."""

    def test_stochastic_value_creation(self):
        """Test stochastic value creation."""
        sv = StochasticValue(0.5)
        assert sv.value == 0.5

    def test_stochastic_rounding(self):
        """Test stochastic rounding."""
        sv = StochasticValue(0.123456789, _rng_seed=42)
        assert isinstance(sv.value, float)
