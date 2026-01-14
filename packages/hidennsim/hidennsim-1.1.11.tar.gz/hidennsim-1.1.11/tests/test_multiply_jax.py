"""Tests for multiply_jax tool."""

import pytest
from hidennsim.tools.multiply_jax import execute_multiply_jax


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

    def test_large_numbers(self):
        """Test multiplication with large numbers."""
        result = execute_multiply_jax(1e6, 2e3)
        assert result == 2e9

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

    def test_multiplicative_identity(self):
        """Test multiplication by 1 (identity element)."""
        result = execute_multiply_jax(42.5, 1.0)
        assert result == 42.5

    def test_negative_result(self):
        """Test multiplication of negative and positive numbers."""
        result = execute_multiply_jax(-10, 5)
        assert result == -50.0

    def test_both_negative(self):
        """Test multiplication of two negative numbers."""
        result = execute_multiply_jax(-4.0, -5.0)
        assert result == 20.0
