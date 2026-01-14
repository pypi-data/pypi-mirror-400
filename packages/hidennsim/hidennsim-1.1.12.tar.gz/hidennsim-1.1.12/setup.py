"""Setup configuration for hidennsim."""

import os
from pathlib import Path
from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize


# Determine platform-specific compilation flags
def get_compile_args():
    """Get platform-specific compiler flags."""
    if os.name == 'nt':  # Windows
        return ['/O2', '/GL']  # Optimize for speed, whole program optimization
    else:  # macOS, Linux
        return ['-O3', '-s']  # Optimize, strip symbols


# Define Cython extensions
extensions = [
    Extension(
        "hidennsim.server",
        ["hidennsim/server.py"],
        extra_compile_args=get_compile_args(),
    ),
    Extension(
        "hidennsim.tools.add_jax",
        ["hidennsim/tools/add_jax.py"],
        extra_compile_args=get_compile_args(),
    ),
    Extension(
        "hidennsim.tools.subtract_jax",
        ["hidennsim/tools/subtract_jax.py"],
        extra_compile_args=get_compile_args(),
    ),
    Extension(
        "hidennsim.tools.multiply_jax",
        ["hidennsim/tools/multiply_jax.py"],
        extra_compile_args=get_compile_args(),
    ),
    Extension(
        "hidennsim.tools.csv_dimensions",
        ["hidennsim/tools/csv_dimensions.py"],
        extra_compile_args=get_compile_args(),
    ),
    Extension(
        "hidennsim.tools.train_data",
        ["hidennsim/tools/train_data.py"],
        extra_compile_args=get_compile_args(),
    ),
]


setup(
    name="hidennsim",
    version="1.1.12",
    description="MCP server with JAX-based numerical tools",
    long_description=Path("README.md").read_text(encoding="utf-8") if Path("README.md").exists() else "",
    long_description_content_type="text/markdown",
    author="HIDENNSIM Team",
    author_email="support@hidennsim.com",
    url="https://github.com/yourusername/hidennsim",
    license="MIT",

    packages=find_packages(exclude=['tests', 'tests.*']),

    # Explicitly exclude source files for Cython-compiled modules
    exclude_package_data={
        'hidennsim': ['server.py'],
        'hidennsim.tools': ['add_jax.py', 'subtract_jax.py', 'multiply_jax.py', 'csv_dimensions.py', 'train_data.py'],
    },

    # Include only necessary package data
    package_data={
        'hidennsim': ['*.pyd', '*.so', 'py.typed'],
        'hidennsim.tools': ['config/*.yaml'],
        'hidennsim.tools.pyinn': ['*.py'],  # Include all pyinn Python source files
    },

    # Cython compilation with security optimization
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'embedsignature': False,
            'binding': False,
            'c_string_type': 'unicode',
            'c_string_encoding': 'utf8',
        },
        build_dir="build",
    ),

    # Dependencies
    install_requires=[
        "mcp>=1.0.0",
        "pandas>=2.0.0",
        "pyyaml>=6.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "optax>=0.1.7",
    ],

    # Optional dependencies
    extras_require={
        "cpu": ["jax[cpu]>=0.4.20"],
        "cuda": ["jax[cuda12]>=0.4.20"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },

    # CLI entry points
    entry_points={
        "console_scripts": [
            "hidennsim=hidennsim.server:main",
        ],
    },

    # Python version requirement
    python_requires=">=3.10",

    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Cython",
    ],
)
