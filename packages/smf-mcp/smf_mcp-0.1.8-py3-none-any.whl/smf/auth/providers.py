"""
Authentication Provider Interfaces.

Implements Adapter + Strategy pattern for pluggable auth providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AuthProvider(ABC):
    """
    Base class for authentication providers.

    Adapter interface that adapts different auth implementations
    to FastMCP's auth system.
    """

    @abstractmethod
    def authenticate(self, token: str) -> Dict[str, Any]:
        """
        Authenticate a token and return claims.

        Args:
            token: Authentication token

        Returns:
            Dictionary of claims (user_id, roles, etc.)

        Raises:
            AuthenticationError: If authentication fails
        """
        pass

    @abstractmethod
    def get_fastmcp_config(self) -> Dict[str, Any]:
        """
        Get FastMCP auth configuration.

        Returns:
            Configuration dictionary for FastMCP auth parameter
        """
        pass


class JWTAuthProvider(AuthProvider):
    """JWT-based authentication provider."""

    def __init__(
        self,
        secret: Optional[str] = None,
        algorithm: str = "HS256",
        issuer: Optional[str] = None,
        audience: Optional[str] = None,
    ):
        """
        Initialize JWT auth provider.

        Args:
            secret: JWT secret key
            algorithm: JWT algorithm (default: HS256)
            issuer: Expected JWT issuer
            audience: Expected JWT audience
        """
        self.secret = secret
        self.algorithm = algorithm
        self.issuer = issuer
        self.audience = audience

    def authenticate(self, token: str) -> Dict[str, Any]:
        """Authenticate JWT token."""
        try:
            import jwt

            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience,
            )
            return payload
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {e}") from e

    def get_fastmcp_config(self) -> Dict[str, Any]:
        """Get FastMCP config for JWT auth."""
        return {
            "type": "jwt",
            "secret": self.secret,
            "algorithm": self.algorithm,
        }


class OAuthProvider(AuthProvider):
    """OAuth-based authentication provider."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        authorization_url: str,
        token_url: str,
        userinfo_url: Optional[str] = None,
    ):
        """
        Initialize OAuth provider.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            authorization_url: OAuth authorization URL
            token_url: OAuth token URL
            userinfo_url: Optional userinfo URL
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_url = authorization_url
        self.token_url = token_url
        self.userinfo_url = userinfo_url

    def authenticate(self, token: str) -> Dict[str, Any]:
        """Authenticate OAuth token."""
        # Placeholder - actual implementation depends on OAuth library
        # This would typically validate the token with the OAuth provider
        raise NotImplementedError("OAuth authentication not yet implemented")

    def get_fastmcp_config(self) -> Dict[str, Any]:
        """Get FastMCP config for OAuth."""
        return {
            "type": "oauth",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "authorization_url": self.authorization_url,
            "token_url": self.token_url,
        }


class TokenVerifierProvider(AuthProvider):
    """Token verifier provider (for OIDC, etc.)."""

    def __init__(self, verification_url: str, audience: Optional[str] = None):
        """
        Initialize token verifier.

        Args:
            verification_url: URL to verify tokens
            audience: Expected audience
        """
        self.verification_url = verification_url
        self.audience = audience

    def authenticate(self, token: str) -> Dict[str, Any]:
        """Verify token with remote service."""
        # Placeholder - would make HTTP request to verification_url
        raise NotImplementedError("Token verification not yet implemented")

    def get_fastmcp_config(self) -> Dict[str, Any]:
        """Get FastMCP config for token verifier."""
        return {
            "type": "token_verifier",
            "verification_url": self.verification_url,
            "audience": self.audience,
        }


class AuthenticationError(Exception):
    """Authentication failed error."""

    pass

