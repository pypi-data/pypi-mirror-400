"""
Authentication & Authorization Manager.

Centralizes auth/authz logic and selects providers based on settings.
"""

from typing import Any, Dict, Optional

from smf.auth.providers import (
    AuthProvider,
    AuthenticationError,
    JWTAuthProvider,
    OAuthProvider,
    TokenVerifierProvider,
)
from smf.settings import AuthProvider as AuthProviderType, Settings


class AuthManager:
    """
    Manages authentication and authorization.

    Uses Strategy pattern to select auth provider based on settings.
    """

    def __init__(self, settings: Settings):
        """
        Initialize AuthManager.

        Args:
            settings: SMF settings
        """
        self.settings = settings
        self._provider: Optional[AuthProvider] = None
        self._initialize_provider()

    def _initialize_provider(self) -> None:
        """Initialize auth provider based on settings."""
        if self.settings.auth_provider == AuthProviderType.NONE:
            self._provider = None
            return

        auth_config = self.settings.auth_config

        if self.settings.auth_provider == AuthProviderType.JWT:
            self._provider = JWTAuthProvider(
                secret=auth_config.get("secret"),
                algorithm=auth_config.get("algorithm", "HS256"),
                issuer=auth_config.get("issuer"),
                audience=auth_config.get("audience"),
            )
        elif self.settings.auth_provider == AuthProviderType.OAUTH:
            self._provider = OAuthProvider(
                client_id=auth_config.get("client_id", ""),
                client_secret=auth_config.get("client_secret", ""),
                authorization_url=auth_config.get("authorization_url", ""),
                token_url=auth_config.get("token_url", ""),
                userinfo_url=auth_config.get("userinfo_url"),
            )
        elif self.settings.auth_provider == AuthProviderType.TOKEN_VERIFIER:
            self._provider = TokenVerifierProvider(
                verification_url=auth_config.get("verification_url", ""),
                audience=auth_config.get("audience"),
            )
        else:
            raise ValueError(f"Unsupported auth provider: {self.settings.auth_provider}")

    def get_fastmcp_auth_config(self) -> Optional[Dict[str, Any]]:
        """
        Get FastMCP auth configuration.

        Returns:
            Auth config dict for FastMCP, or None if auth disabled
        """
        if self._provider is None:
            return None
        return self._provider.get_fastmcp_config()

    def authenticate(self, token: str) -> Dict[str, Any]:
        """
        Authenticate a token.

        Args:
            token: Authentication token

        Returns:
            Claims dictionary

        Raises:
            AuthenticationError: If authentication fails
        """
        if self._provider is None:
            raise AuthenticationError("Authentication not configured")

        return self._provider.authenticate(token)

    def authorize(
        self, user_claims: Dict[str, Any], resource: str, action: str
    ) -> bool:
        """
        Authorize user action on resource.

        Args:
            user_claims: User claims from authentication
            resource: Resource identifier
            action: Action to perform

        Returns:
            True if authorized, False otherwise
        """
        if not self.settings.enable_authz:
            return True  # Authorization disabled

        # Placeholder - actual implementation would integrate with
        # authorization providers like Permit.io or Eunomia
        return True

