"""JAX-based subtraction tool - Cython-compiled module."""

from typing import Union

try:
    import jax.numpy as jnp
except ImportError as e:
    raise ImportError(
        "JAX is not installed. Install it with: pip install 'jax[cpu]' "
        "or 'jax[cuda12]' for GPU support."
    ) from e


def execute_subtract_jax(a: float, b: float) -> float:
    """
    Perform subtraction using JAX (a - b).

    Args:
        a: First floating-point operand (minuend)
        b: Second floating-point operand (subtrahend)

    Returns:
        Difference of a and b as a Python float

    Raises:
        TypeError: If inputs are not numeric
        ValueError: If inputs are NaN or Inf

    Examples:
        >>> execute_subtract_jax(10.5, 3.2)
        7.3
        >>> execute_subtract_jax(5, 10)
        -5.0
    """
    # Input validation
    if not isinstance(a, (int, float)):
        raise TypeError(f"Operand 'a' must be numeric, got {type(a).__name__}")
    if not isinstance(b, (int, float)):
        raise TypeError(f"Operand 'b' must be numeric, got {type(b).__name__}")

    # Convert to JAX arrays
    jax_a = jnp.array(a, dtype=jnp.float32)
    jax_b = jnp.array(b, dtype=jnp.float32)

    # Perform subtraction
    result = jax_a - jax_b

    # Validate result
    if jnp.isnan(result).item():
        raise ValueError("Result is NaN (Not a Number)")
    if jnp.isinf(result).item():
        raise ValueError("Result is infinite")

    # Convert back to Python float
    return float(result)