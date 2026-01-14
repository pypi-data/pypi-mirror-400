"""Tests for JAX-based computation tools."""

import pytest
from hidennsim.tools.add_jax import execute_add_jax
from hidennsim.tools.subtract_jax import execute_subtract_jax
from hidennsim.tools.multiply_jax import execute_multiply_jax


class TestAddJax:
    """Tests for the add_jax tool."""

    def test_basic_addition(self):
        """Test basic floating-point addition."""
        result = execute_add_jax(2.5, 3.7)
        assert abs(result - 6.2) < 0.001

    def test_integer_inputs(self):
        """Test that integer inputs work."""
        result = execute_add_jax(5, 10)
        assert result == 15.0

    def test_negative_numbers(self):
        """Test addition with negative numbers."""
        result = execute_add_jax(-5.5, 3.2)
        assert abs(result - (-2.3)) < 0.001

    def test_zero_addition(self):
        """Test addition with zero."""
        result = execute_add_jax(42.0, 0.0)
        assert result == 42.0

    def test_large_numbers(self):
        """Test addition with large numbers."""
        result = execute_add_jax(1e6, 2e6)
        assert result == 3e6

    def test_basic_subtraction(self):
        """Test basic floating-point subtraction."""
        result = execute_subtract_jax(10.5, 3.2)
        assert abs(result - 7.3) < 0.001

    def test_type_error_string(self):
        """Test that string inputs raise TypeError."""
        with pytest.raises(TypeError, match="must be numeric"):
            execute_add_jax("5", 10)

    def test_type_error_none(self):
        """Test that None inputs raise TypeError."""
        with pytest.raises(TypeError, match="must be numeric"):
            execute_add_jax(None, 10)

    def test_commutative_property(self):
        """Test that addition is commutative."""
        result1 = execute_add_jax(3.5, 7.2)
        result2 = execute_add_jax(7.2, 3.5)
        assert abs(result1 - result2) < 0.001


class TestMultiplyJax:
    """Tests for the multiply_jax tool."""

    def test_basic_multiplication(self):
        """Test basic floating-point multiplication."""
        result = execute_multiply_jax(10.5, 3.2)
        assert abs(result - 33.6) < 0.001

    def test_integer_inputs(self):
        """Test that integer inputs work."""
        result = execute_multiply_jax(5, 10)
        assert result == 50.0

    def test_negative_numbers(self):
        """Test multiplication with negative numbers."""
        result = execute_multiply_jax(-5.5, 3.2)
        assert abs(result - (-17.6)) < 0.001

    def test_zero_multiplication(self):
        """Test multiplication with zero."""
        result = execute_multiply_jax(42.0, 0.0)
        assert result == 0.0

    def test_type_error_string(self):
        """Test that string inputs raise TypeError."""
        with pytest.raises(TypeError, match="must be numeric"):
            execute_multiply_jax("5", 10)

    def test_type_error_none(self):
        """Test that None inputs raise TypeError."""
        with pytest.raises(TypeError, match="must be numeric"):
            execute_multiply_jax(None, 10)

    def test_commutative_property(self):
        """Test that multiplication is commutative."""
        result1 = execute_multiply_jax(3.5, 7.2)
        result2 = execute_multiply_jax(7.2, 3.5)
        assert abs(result1 - result2) < 0.001
