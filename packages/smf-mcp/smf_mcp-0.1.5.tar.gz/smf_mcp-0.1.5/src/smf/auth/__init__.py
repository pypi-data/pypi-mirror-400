"""
SMF Authentication & Authorization Module.

Simplified authentication and authorization for SMF servers.
"""

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
from smf.auth.manager import AuthManager
from smf.auth.providers import (
    AuthenticationError,
    AuthProvider,
    JWTAuthProvider,
    OAuthProvider,
    TokenVerifierProvider,
)

__all__ = [
    # Manager
    "AuthManager",
    # Providers
    "AuthProvider",
    "JWTAuthProvider",
    "OAuthProvider",
    "TokenVerifierProvider",
    "AuthenticationError",
    # Helpers
    "get_current_user",
    "get_user_id",
    "get_user_roles",
    "has_role",
    "require_auth",
    "require_role",
    "require_permission",
    "get_accessible_indices",
    "can_access_index",
]
