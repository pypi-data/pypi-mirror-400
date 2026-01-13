"""Tests for computation backends."""

import pytest

from nuclear_add.backends import (
    PythonBackend,
    get_backend,
    list_available_backends,
)


class TestPythonBackend:
    """Test Python backend."""

    def test_backend_creation(self):
        """Test backend creation."""
        backend = PythonBackend()
        assert backend.name == "python"
        assert backend.is_available() is True

    def test_backend_add(self):
        """Test backend addition."""
        backend = PythonBackend()
        result = backend.add(2, 3)
        assert result == 5

    def test_backend_add_many(self):
        """Test backend add_many."""
        backend = PythonBackend()
        result = backend.add_many([1, 2, 3, 4])
        assert result == 10

    def test_backend_kahan_sum(self):
        """Test backend Kahan sum."""
        backend = PythonBackend()
        values = [0.1] * 10
        result = backend.kahan_sum(values)
        assert result == pytest.approx(1.0)

    def test_backend_neumaier_sum(self):
        """Test backend Neumaier sum."""
        backend = PythonBackend()
        values = [0.1] * 10
        result = backend.neumaier_sum(values)
        assert result == pytest.approx(1.0)

    def test_backend_pairwise_sum(self):
        """Test backend pairwise sum."""
        backend = PythonBackend()
        values = [1.0] * 8
        result = backend.pairwise_sum(values)
        assert result == 8.0

    def test_backend_capabilities(self):
        """Test backend capabilities."""
        backend = PythonBackend()
        caps = backend.capabilities
        assert caps.deterministic is True
        assert caps.vectorized is False
        assert caps.gpu is False


class TestBackendRegistry:
    """Test backend registry."""

    def test_get_backend_python(self):
        """Test getting Python backend."""
        backend = get_backend("python")
        assert backend.name == "python"
        assert backend.is_available() is True

    def test_get_backend_auto(self):
        """Test auto backend selection."""
        backend = get_backend("auto")
        assert backend is not None
        assert backend.is_available() is True

    def test_get_backend_invalid(self):
        """Test invalid backend name."""
        with pytest.raises(ValueError):
            get_backend("invalid_backend")

    def test_list_available_backends(self):
        """Test listing available backends."""
        backends = list_available_backends()
        assert "python" in backends
        assert isinstance(backends, list)
        assert len(backends) > 0


class TestBackendCapabilities:
    """Test backend capabilities."""

    def test_python_backend_capabilities(self):
        """Test Python backend capabilities."""
        backend = PythonBackend()
        caps = backend.capabilities

        assert caps.deterministic is True
        assert caps.vectorized is False
        assert caps.gpu is False
        assert caps.jit is False
        assert caps.arbitrary_precision is False
        assert caps.simd is False
