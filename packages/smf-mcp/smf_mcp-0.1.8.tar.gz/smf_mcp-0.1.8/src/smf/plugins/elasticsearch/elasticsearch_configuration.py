"""
Elasticsearch Configuration.

Pydantic model for Elasticsearch connection configuration.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensure .env files are loaded
try:
    from dotenv import load_dotenv
    _DOTENV_AVAILABLE = True
except ImportError:
    _DOTENV_AVAILABLE = False
    load_dotenv = None


class ElasticsearchConfiguration(BaseSettings):
    """
    Configuration for Elasticsearch connection.
    
    Supports all parameters from the official Elasticsearch Python client.
    Automatically loads .env files if available.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="ELASTICSEARCH_",
        case_sensitive=False,
        extra="ignore",
    )

    # Hosts configuration
    hosts: Union[str, List[str]] = Field(
        default="http://localhost:9200",
        description="Elasticsearch host(s). Can be a string or list of strings."
    )

    # Authentication
    api_key: Optional[str] = Field(
        default=None,
        description="API key for authentication"
    )
    basic_auth: Optional[Tuple[str, str]] = Field(
        default=None,
        description="Basic authentication as (username, password) tuple"
    )
    bearer_auth: Optional[str] = Field(
        default=None,
        description="Bearer token for authentication"
    )

    # SSL/TLS Configuration
    verify_certs: bool = Field(
        default=True,
        description="Whether to verify SSL certificates"
    )
    ssl_show_warn: bool = Field(
        default=True,
        description="Show SSL warnings"
    )
    ca_certs: Optional[str] = Field(
        default=None,
        description="Path to CA certificates file"
    )
    client_cert: Optional[str] = Field(
        default=None,
        description="Path to client certificate file"
    )
    client_key: Optional[str] = Field(
        default=None,
        description="Path to client key file"
    )

    # Connection settings
    timeout: Optional[float] = Field(
        default=None,
        description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries"
    )
    retry_on_timeout: bool = Field(
        default=False,
        description="Whether to retry on timeout"
    )
    retry_on_status: Optional[List[int]] = Field(
        default=None,
        description="List of HTTP status codes to retry on"
    )

    # Other options
    request_timeout: Optional[float] = Field(
        default=None,
        description="Request timeout (alias for timeout)"
    )
    maxsize: int = Field(
        default=10,
        description="Maximum number of connections in the connection pool"
    )

    @field_validator("hosts", mode="before")
    @classmethod
    def validate_hosts(cls, v: Any) -> Union[str, List[str]]:
        """Validate and normalize hosts."""
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            return v
        if isinstance(v, (tuple, set)):
            return list(v)
        raise ValueError(f"hosts must be a string or list of strings, got {type(v).__name__}")

    @field_validator("basic_auth", mode="before")
    @classmethod
    def validate_basic_auth(cls, v: Any) -> Optional[Tuple[str, str]]:
        """Validate basic_auth format."""
        if v is None:
            return None
        if isinstance(v, tuple) and len(v) == 2:
            return tuple(v)
        if isinstance(v, list) and len(v) == 2:
            return tuple(v)
        raise ValueError("basic_auth must be a tuple or list of (username, password)")

    def to_client_kwargs(self) -> Dict[str, Any]:
        """
        Convert configuration to keyword arguments for Elasticsearch client.
        
        Returns:
            Dictionary of parameters ready to pass to Elasticsearch/AsyncElasticsearch
        """
        kwargs: Dict[str, Any] = {
            "hosts": self.hosts,
        }

        # Authentication
        if self.api_key:
            kwargs["api_key"] = self.api_key
        elif self.basic_auth:
            kwargs["basic_auth"] = self.basic_auth
        elif self.bearer_auth:
            kwargs["bearer_auth"] = self.bearer_auth

        # SSL/TLS
        kwargs["verify_certs"] = self.verify_certs
        kwargs["ssl_show_warn"] = self.ssl_show_warn
        if self.ca_certs:
            kwargs["ca_certs"] = self.ca_certs
        if self.client_cert:
            kwargs["client_cert"] = self.client_cert
        if self.client_key:
            kwargs["client_key"] = self.client_key

        # Connection settings
        if self.timeout is not None:
            kwargs["timeout"] = self.timeout
        elif self.request_timeout is not None:
            kwargs["timeout"] = self.request_timeout

        kwargs["max_retries"] = self.max_retries
        kwargs["retry_on_timeout"] = self.retry_on_timeout
        if self.retry_on_status:
            kwargs["retry_on_status"] = self.retry_on_status

        # Connection pool
        kwargs["maxsize"] = self.maxsize

        return kwargs

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "ElasticsearchConfiguration":
        """
        Create configuration from dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            ElasticsearchConfiguration instance
        """
        return cls(**config)

    @classmethod
    def from_env(cls, env_file: Optional[Union[str, Path]] = None) -> "ElasticsearchConfiguration":
        """
        Create configuration from environment variables.
        
        Automatically loads .env file if available.
        
        Args:
            env_file: Optional path to .env file. If None, searches for .env in current directory.
        
        Environment variables:
        - ELASTICSEARCH_HOSTS: Host(s) (default: http://localhost:9200)
        - ELASTICSEARCH_API_KEY: API key
        - ELASTICSEARCH_USERNAME: Username for basic auth
        - ELASTICSEARCH_PASSWORD: Password for basic auth
        - ELASTICSEARCH_VERIFY_CERTS: Verify SSL certificates (default: true)
        - ELASTICSEARCH_TIMEOUT: Request timeout in seconds
        - ELASTICSEARCH_MAX_RETRIES: Maximum retries (default: 3)
        
        Returns:
            ElasticsearchConfiguration instance
        """
        import os

        # Load .env file if available
        if _DOTENV_AVAILABLE and load_dotenv:
            if env_file:
                load_dotenv(dotenv_path=Path(env_file))
            else:
                # Try to find .env in current directory
                env_path = Path.cwd() / ".env"
                if env_path.exists():
                    load_dotenv(dotenv_path=env_path)

        # Use Pydantic's built-in .env loading via BaseSettings
        # This will automatically load from .env file if configured
        return cls()
