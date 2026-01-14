"""
Precision Configuration Module
----------------------------------------------------------------------------------
Central configuration for numerical precision (float32/float64) across all pyinn modules.

This module MUST be imported first, before any other JAX operations.
The precision is set via environment variable or direct function call.

Usage in main.py:
    from precision import set_precision, get_float_dtype, get_int_dtype
    set_precision(use_float64=True)  # Must be called BEFORE other imports

Usage in other modules:
    from precision import FDTYPE, IDTYPE

Copyright (C) 2024  Chanwook Park
Northwestern University, Evanston, Illinois, US, chanwookpark2024@u.northwestern.edu
"""

import os
from jax import config as jax_config

# Default precision setting (can be overridden)
_USE_FLOAT64 = False
_PRECISION_SET = False

def set_precision(use_float64: bool = True):
    """
    Set the numerical precision for all JAX operations.

    IMPORTANT: This function must be called BEFORE importing other pyinn modules
    or performing any JAX operations.

    Args:
        use_float64: If True, use float64/int64. If False, use float32/int32.
    """
    global _USE_FLOAT64, _PRECISION_SET, FDTYPE, IDTYPE, NP_FDTYPE, NP_IDTYPE

    if _PRECISION_SET:
        import warnings
        warnings.warn(
            "Precision has already been set. Changing precision after JAX operations "
            "have been performed may not take effect. Restart the Python process for "
            "guaranteed precision change."
        )

    _USE_FLOAT64 = use_float64
    _PRECISION_SET = True

    # Set JAX x64 mode
    jax_config.update("jax_enable_x64", use_float64)

    # Update dtype constants
    import jax.numpy as jnp
    import numpy as np

    if use_float64:
        FDTYPE = jnp.float64
        IDTYPE = jnp.int64
        NP_FDTYPE = np.float64
        NP_IDTYPE = np.int64
    else:
        FDTYPE = jnp.float32
        IDTYPE = jnp.int32
        NP_FDTYPE = np.float32
        NP_IDTYPE = np.int32

    # Update module-level variables
    globals()['FDTYPE'] = FDTYPE
    globals()['IDTYPE'] = IDTYPE
    globals()['NP_FDTYPE'] = NP_FDTYPE
    globals()['NP_IDTYPE'] = NP_IDTYPE


def get_float_dtype():
    """Get the current float dtype for JAX arrays."""
    import jax.numpy as jnp
    return jnp.float64 if _USE_FLOAT64 else jnp.float32


def get_int_dtype():
    """Get the current int dtype for JAX arrays."""
    import jax.numpy as jnp
    return jnp.int64 if _USE_FLOAT64 else jnp.int32


def get_np_float_dtype():
    """Get the current float dtype for NumPy arrays."""
    import numpy as np
    return np.float64 if _USE_FLOAT64 else np.float32


def get_np_int_dtype():
    """Get the current int dtype for NumPy arrays."""
    import numpy as np
    return np.int64 if _USE_FLOAT64 else np.int32


def is_float64_enabled():
    """Check if float64 precision is enabled."""
    return _USE_FLOAT64


# Initialize with environment variable if set
_env_precision = os.environ.get('PYINN_USE_FLOAT64', '').lower()
if _env_precision in ('1', 'true', 'yes'):
    set_precision(use_float64=True)
elif _env_precision in ('0', 'false', 'no'):
    set_precision(use_float64=False)
else:
    # Default initialization (float32 for backward compatibility)
    # Note: This sets _PRECISION_SET to True, so subsequent set_precision calls will warn
    # To avoid this, call set_precision() explicitly in main.py before other imports
    import jax.numpy as jnp
    import numpy as np
    FDTYPE = jnp.float32
    IDTYPE = jnp.int32
    NP_FDTYPE = np.float32
    NP_IDTYPE = np.int32
