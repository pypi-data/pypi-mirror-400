"""JAX-based addition tool - Cython-compiled module."""

from typing import Union

try:
    import jax.numpy as jnp
except ImportError as e:
    raise ImportError(
        "JAX is not installed. Install it with: pip install 'jax[cpu]' "
        "or 'jax[cuda12]' for GPU support."
    ) from e


def execute_add_jax(a: float, b: float) -> float:
    """
    Perform addition using JAX.

    Args:
        a: First floating-point operand
        b: Second floating-point operand

    Returns:
        Sum of a and b as a Python float

    Raises:
        TypeError: If inputs are not numeric
        ValueError: If inputs are NaN or Inf
    """
    # Input validation
    if not isinstance(a, (int, float)):
        raise TypeError(f"Operand 'a' must be numeric, got {type(a).__name__}")
    if not isinstance(b, (int, float)):
        raise TypeError(f"Operand 'b' must be numeric, got {type(b).__name__}")

    # Convert to JAX arrays
    jax_a = jnp.array(a, dtype=jnp.float32)
    jax_b = jnp.array(b, dtype=jnp.float32)

    # Perform addition
    result = jax_a + jax_b

    # Validate result
    if jnp.isnan(result).item():
        raise ValueError("Result is NaN (Not a Number)")
    if jnp.isinf(result).item():
        raise ValueError("Result is infinite")

    # Convert back to Python float
    return float(result)
