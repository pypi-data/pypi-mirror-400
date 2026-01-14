"""
SMF Settings - Centralized configuration management.

This module provides a Pydantic-based settings system that:
- Loads from environment variables (prefix: SMF_)
- Supports .env files
- Maps to FastMCP parameters
- Provides defaults for production-ready behavior
"""

from enum import Enum
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthProvider(str, Enum):
    """Supported authentication providers."""

    NONE = "none"
    JWT = "jwt"
    OAUTH = "oauth"
    OAUTH_PROXY = "oauth_proxy"
    REMOTE = "remote"
    TOKEN_VERIFIER = "token_verifier"


class StorageBackend(str, Enum):
    """Supported storage backends."""

    MEMORY = "memory"
    REDIS = "redis"
    POSTGRES = "postgres"


class TransportType(str, Enum):
    """Supported transport types."""

    STDIO = "stdio"
    HTTP = "http"
    SSE = "sse"


class TracingExporter(str, Enum):
    """Supported tracing exporters."""

    NONE = "none"
    OTEL = "otel"
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"


class Settings(BaseSettings):
    """
    Centralized SMF configuration.

    Maps to FastMCP parameters and adds enterprise features.
    """

    # Server Identity
    server_name: str = Field(default="SMF Server", description="Server name")
    server_version: Optional[str] = Field(default=None, description="Server version")
    server_instructions: Optional[str] = Field(
        default=None, description="Server instructions for LLM"
    )

    # FastMCP Parameters
    strict_input_validation: bool = Field(
        default=True, description="Enable strict input validation"
    )
    include_tags: Optional[List[str]] = Field(
        default=None, description="Tags to include"
    )
    exclude_tags: Optional[List[str]] = Field(
        default=None, description="Tags to exclude"
    )
    include_fastmcp_meta: bool = Field(
        default=False, description="Include FastMCP metadata"
    )
    mask_error_details: bool = Field(
        default=True, description="Mask error details in responses"
    )
    duplicate_policy: str = Field(
        default="error", description="Policy for duplicate registrations"
    )

    # Transport Configuration
    transport: TransportType = Field(
        default=TransportType.STDIO, description="Transport type"
    )
    host: str = Field(default="0.0.0.0", description="HTTP host")
    port: int = Field(default=8000, description="HTTP port")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="json", description="Log format: json or text"
    )
    structured_logging: bool = Field(
        default=True, description="Enable structured logging"
    )

    # Authentication & Authorization
    auth_provider: AuthProvider = Field(
        default=AuthProvider.NONE, description="Authentication provider"
    )
    auth_config: Dict[str, Any] = Field(
        default_factory=dict, description="Auth provider configuration"
    )
    enable_authz: bool = Field(
        default=False, description="Enable authorization middleware"
    )
    authz_provider: Optional[str] = Field(
        default=None, description="Authorization provider (e.g., permit, eunomia)"
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(
        default=True, description="Enable rate limiting"
    )
    rate_limit_per_minute: int = Field(
        default=60, description="Requests per minute"
    )
    rate_limit_per_hour: int = Field(
        default=1000, description="Requests per hour"
    )

    # Caching
    cache_enabled: bool = Field(default=False, description="Enable caching")
    cache_backend: StorageBackend = Field(
        default=StorageBackend.MEMORY, description="Cache backend"
    )
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    cache_config: Dict[str, Any] = Field(
        default_factory=dict, description="Cache backend configuration"
    )

    # Observability
    metrics_enabled: bool = Field(
        default=True, description="Enable Prometheus metrics"
    )
    metrics_path: str = Field(
        default="/metrics", description="Metrics endpoint path"
    )
    tracing_enabled: bool = Field(
        default=False, description="Enable OpenTelemetry tracing"
    )
    tracing_exporter: TracingExporter = Field(
        default=TracingExporter.NONE, description="Tracing exporter"
    )
    tracing_endpoint: Optional[str] = Field(
        default=None, description="Tracing endpoint URL"
    )

    # Storage
    storage_backend: StorageBackend = Field(
        default=StorageBackend.MEMORY, description="Storage backend"
    )
    storage_config: Dict[str, Any] = Field(
        default_factory=dict, description="Storage backend configuration"
    )

    # Plugin & Discovery
    auto_discover: bool = Field(
        default=True, description="Auto-discover components"
    )
    discovery_paths: List[str] = Field(
        default_factory=list, description="Paths to scan for components"
    )
    plugin_paths: List[str] = Field(
        default_factory=list, description="Plugin entry point paths"
    )

    # Governance
    governance_enabled: bool = Field(
        default=False, description="Enable governance hooks"
    )
    governance_config: Dict[str, Any] = Field(
        default_factory=dict, description="Governance configuration"
    )

    # Environment
    environment: str = Field(
        default="production", description="Environment: development, staging, production"
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    model_config = SettingsConfigDict(
        env_prefix="SMF_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def model_post_init(self, __context: Any) -> None:
        if self.environment == "development" and "debug" not in self.model_fields_set:
            self.debug = True

        if self.debug:
            if "log_level" not in self.model_fields_set:
                self.log_level = "DEBUG"
            if "mask_error_details" not in self.model_fields_set:
                self.mask_error_details = False

        if self.tracing_enabled and self.tracing_exporter == TracingExporter.NONE:
            self.tracing_exporter = TracingExporter.OTEL

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v.lower()

    def to_fastmcp_params(self) -> Dict[str, Any]:
        """
        Convert settings to FastMCP constructor parameters.

        Returns:
            Dictionary of parameters for FastMCP constructor
        """
        params: Dict[str, Any] = {
            "name": self.server_name,
            "strict_input_validation": self.strict_input_validation,
            "include_fastmcp_meta": self.include_fastmcp_meta,
            "mask_error_details": self.mask_error_details,
        }

        if self.server_version:
            params["version"] = self.server_version

        if self.server_instructions:
            params["instructions"] = self.server_instructions

        if self.include_tags:
            params["include_tags"] = self.include_tags

        if self.exclude_tags:
            params["exclude_tags"] = self.exclude_tags

        # Note: duplicate_policy is an SMF internal setting, not a FastMCP parameter
        # It's handled by ComponentRegistry, not passed to FastMCP

        # Auth configuration (will be handled by AuthManager)
        if self.auth_provider != AuthProvider.NONE:
            params["auth"] = self._build_auth_config()

        return params

    def _build_auth_config(self) -> Dict[str, Any]:
        """Build auth configuration for FastMCP."""
        # This will be expanded by AuthManager
        return {
            "provider": self.auth_provider.value,
            **self.auth_config,
        }

    @classmethod
    def from_file(cls, path: Path, env_file: Optional[Path] = None) -> "Settings":
        """Load settings from a file."""
        import json

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Settings file not found: {path}")

        with open(path, "r") as f:
            if path.suffix == ".json":
                data = json.load(f)
            elif path.suffix in (".yaml", ".yml"):
                try:
                    import yaml
                    data = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML required for YAML config files. Install with: pip install pyyaml")
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")

        data = _resolve_env_vars(data or {})
        return cls(**data, _env_file=env_file)

    def save_to_file(self, path: Path) -> None:
        """Save settings to a file."""
        import json

        path = Path(path)
        data = self.model_dump(exclude_none=True)

        with open(path, "w") as f:
            if path.suffix == ".json":
                json.dump(data, f, indent=2)
            elif path.suffix in (".yaml", ".yml"):
                try:
                    import yaml
                    yaml.dump(data, f, default_flow_style=False)
                except ImportError:
                    raise ImportError("PyYAML required for YAML config files. Install with: pip install pyyaml")
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")


# Global settings instance (lazy-loaded)
_settings: Optional[Settings] = None


def _resolve_env_vars(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _resolve_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env_vars(v) for v in value]
    if isinstance(value, str):
        pattern = re.compile(r"\$\{([^}]+)\}")

        def replace(match: re.Match[str]) -> str:
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))

        return pattern.sub(replace, value)
    return value


def _find_config_file(base_dir: Path) -> Optional[Path]:
    env_name = os.getenv("SMF_ENVIRONMENT")
    if env_name:
        env_name = env_name.lower()
        for ext in ("yaml", "yml", "json"):
            candidate = base_dir / f"smf.{env_name}.{ext}"
            if candidate.exists():
                return candidate

    for name in ("smf.yaml", "smf.yml", "smf.json"):
        candidate = base_dir / name
        if candidate.exists():
            return candidate

    return None


def load_settings(
    base_dir: Optional[Path] = None, config_file: Optional[Path] = None
) -> Settings:
    base_dir = Path(base_dir) if base_dir else Path.cwd()
    env_file = base_dir / ".env"

    if config_file:
        settings = Settings.from_file(config_file, env_file=env_file)
        setattr(settings, "_smf_base_dir", base_dir)
        return settings

    config_path = _find_config_file(base_dir)
    if config_path:
        settings = Settings.from_file(config_path, env_file=env_file)
        setattr(settings, "_smf_base_dir", base_dir)
        return settings

    settings = Settings(_env_file=env_file)
    setattr(settings, "_smf_base_dir", base_dir)
    return settings


def get_settings(base_dir: Optional[Path] = None) -> Settings:
    """
    Get or create global settings instance.
    
    Automatically looks for smf.yaml or smf.json in the current directory.
    """
    global _settings
    if _settings is None:
        _settings = load_settings(base_dir)
            
    return _settings


def set_settings(settings: Settings) -> None:
    """Set global settings instance."""
    global _settings
    _settings = settings

