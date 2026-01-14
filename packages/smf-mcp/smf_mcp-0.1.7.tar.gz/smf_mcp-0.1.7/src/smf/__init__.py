"""
SMF - Enterprise MCP Framework

A production-ready framework built on FastMCP for creating,
structuring, and deploying MCP servers.
"""

from smf.core import AppBuilder, ServerFactory, create_server
from smf.registry import ComponentRegistry, ComponentMetadata
from smf.settings import Settings, get_settings, set_settings

# Export auth helpers for easy access
from smf.auth.helpers import (
    can_access_index,
    get_accessible_indices,
    get_current_user,
    get_user_id,
    get_user_roles,
    has_role,
    require_auth,
    require_permission,
    require_role,
)
from smf.auth.simple import (
    create_role_based_authorize,
    elasticsearch_permission_based_authorize,
    simple_role_based_authorize,
)
from smf.middleware.authz import get_current_claims

__version__ = "0.1.4"

__all__ = [
    # Core
    "AppBuilder",
    "ServerFactory",
    "create_server",
    "ComponentRegistry",
    "ComponentMetadata",
    "Settings",
    "get_settings",
    "set_settings",
    # Auth helpers
    "get_current_user",
    "get_current_claims",
    "get_user_id",
    "get_user_roles",
    "has_role",
    "require_auth",
    "require_role",
    "require_permission",
    "get_accessible_indices",
    "can_access_index",
    # Simple auth providers
    "simple_role_based_authorize",
    "elasticsearch_permission_based_authorize",
    "create_role_based_authorize",
]

