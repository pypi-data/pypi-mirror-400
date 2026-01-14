"""
SMF - Enterprise MCP Framework

A production-ready framework built on FastMCP for creating,
structuring, and deploying MCP servers.
"""

from smf.core import AppBuilder, ServerFactory, create_server
from smf.registry import ComponentRegistry, ComponentMetadata

__version__ = "0.1.4"

__all__ = [
    # Core
    "AppBuilder",
    "ServerFactory",
    "create_server",
    "ComponentRegistry",
    "ComponentMetadata",
]

