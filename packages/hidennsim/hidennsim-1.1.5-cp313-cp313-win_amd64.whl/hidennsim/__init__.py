"""
HIDENNSIM - MCP Server with JAX Integration.

A Model Context Protocol (MCP) server providing JAX-based
numerical computation tools.
"""

__version__ = "1.1.5"
__author__ = "HIDENNSIM Team"
__license__ = "MIT"

from .server import HIDENNSIMServer

__all__ = ["HIDENNSIMServer"]
