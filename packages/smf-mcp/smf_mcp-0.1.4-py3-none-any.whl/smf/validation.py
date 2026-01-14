"""
Module de validation de configuration SMF.

Ce module fournit des fonctions de validation qui peuvent être utilisées
à la fois par la commande CLI `smf validate` et par les tests pytest.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from smf import create_server
from smf.settings import (
    AuthProvider,
    Settings,
    StorageBackend,
    TracingExporter,
    TransportType,
    load_settings,
)


class ValidationResult:
    """Résultat d'une validation."""

    def __init__(self, success: bool, message: str = "", details: Optional[Dict[str, Any]] = None):
        """
        Initialiser un résultat de validation.

        Args:
            success: True si la validation a réussi
            message: Message de validation
            details: Détails supplémentaires
        """
        self.success = success
        self.message = message
        self.details = details or {}

    def __bool__(self) -> bool:
        """Retourne True si la validation a réussi."""
        return self.success


class ConfigValidator:
    """Validateur de configuration SMF."""

    def __init__(self, config_file: Path):
        """
        Initialiser le validateur.

        Args:
            config_file: Chemin vers le fichier de configuration
        """
        self.config_file = config_file
        self.settings: Optional[Settings] = None
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        Valider complètement la configuration.

        Returns:
            Tuple (success, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # 1. Charger la configuration
        load_result = self._load_config()
        if not load_result:
            return False, self.errors, self.warnings

        # 2. Valider les valeurs
        self._validate_values()

        # 3. Valider l'application au serveur
        self._validate_server_creation()

        # 4. Valider les dépendances et cohérence
        self._validate_dependencies()

        return len(self.errors) == 0, self.errors, self.warnings

    def _load_config(self) -> bool:
        """Charger la configuration depuis le fichier."""
        try:
            if not self.config_file.exists():
                self.errors.append(f"Configuration file not found: {self.config_file}")
                return False

            self.settings = load_settings(
                base_dir=self.config_file.parent, config_file=self.config_file
            )
            return True
        except Exception as e:
            self.errors.append(f"Error loading configuration: {e}")
            return False

    def _validate_values(self) -> None:
        """Valider les valeurs de configuration."""
        if not self.settings:
            return

        # Valider log_level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.settings.log_level.upper() not in valid_log_levels:
            self.errors.append(
                f"Invalid log_level: {self.settings.log_level}. Must be one of {valid_log_levels}"
            )

        # Valider environment
        valid_environments = ["development", "staging", "production"]
        if self.settings.environment.lower() not in valid_environments:
            self.errors.append(
                f"Invalid environment: {self.settings.environment}. Must be one of {valid_environments}"
            )

        # Valider transport
        try:
            TransportType(self.settings.transport.value)
        except ValueError:
            self.errors.append(
                f"Invalid transport: {self.settings.transport}. Must be one of: stdio, http, sse"
            )

        # Valider auth_provider
        try:
            AuthProvider(self.settings.auth_provider.value)
        except ValueError:
            self.errors.append(
                f"Invalid auth_provider: {self.settings.auth_provider}. Must be one of: none, jwt, oauth, oauth_proxy, remote, token_verifier"
            )

        # Valider cache_backend
        try:
            StorageBackend(self.settings.cache_backend.value)
        except ValueError:
            self.errors.append(
                f"Invalid cache_backend: {self.settings.cache_backend}. Must be one of: memory"
            )

        # Valider storage_backend
        try:
            StorageBackend(self.settings.storage_backend.value)
        except ValueError:
            self.errors.append(
                f"Invalid storage_backend: {self.settings.storage_backend}. Must be one of: memory"
            )

        # Valider tracing_exporter
        try:
            TracingExporter(self.settings.tracing_exporter.value)
        except ValueError:
            self.errors.append(
                f"Invalid tracing_exporter: {self.settings.tracing_exporter}. Must be one of: none, otel, jaeger, zipkin"
            )

        # Valider duplicate_policy
        valid_policies = ["error", "warn", "ignore"]
        if self.settings.duplicate_policy not in valid_policies:
            self.errors.append(
                f"Invalid duplicate_policy: {self.settings.duplicate_policy}. Must be one of {valid_policies}"
            )

        # Valider port
        if self.settings.port < 1 or self.settings.port > 65535:
            self.errors.append(f"Invalid port: {self.settings.port}. Must be between 1 and 65535")

        # Valider rate limits
        if self.settings.rate_limit_enabled:
            if self.settings.rate_limit_per_minute < 1:
                self.errors.append("rate_limit_per_minute must be at least 1")
            if self.settings.rate_limit_per_hour < 1:
                self.errors.append("rate_limit_per_hour must be at least 1")
            if self.settings.rate_limit_per_hour < self.settings.rate_limit_per_minute:
                self.warnings.append(
                    "rate_limit_per_hour is less than rate_limit_per_minute, which may cause issues"
                )

        # Valider cache_ttl
        if self.settings.cache_enabled and self.settings.cache_ttl < 0:
            self.errors.append("cache_ttl must be non-negative")

    def _validate_server_creation(self) -> None:
        """Valider que le serveur peut être créé avec cette configuration."""
        if not self.settings:
            return

        try:
            mcp = create_server(settings=self.settings)

            # Vérifier les attributs FastMCP exposés
            if mcp.name != self.settings.server_name:
                self.errors.append(
                    f"Server name mismatch: expected {self.settings.server_name}, got {mcp.name}"
                )

            if mcp.strict_input_validation != self.settings.strict_input_validation:
                self.errors.append(
                    f"strict_input_validation mismatch: expected {self.settings.strict_input_validation}, got {mcp.strict_input_validation}"
                )

            if mcp.include_fastmcp_meta != self.settings.include_fastmcp_meta:
                self.errors.append(
                    f"include_fastmcp_meta mismatch: expected {self.settings.include_fastmcp_meta}, got {mcp.include_fastmcp_meta}"
                )

            # Vérifier que le serveur peut enregistrer des tools
            @mcp.tool
            def _test_tool() -> str:
                """Test tool for validation."""
                return "ok"

            # Si on arrive ici sans erreur, le serveur fonctionne correctement

        except Exception as e:
            self.errors.append(f"Error creating server: {e}")

    def _validate_dependencies(self) -> None:
        """Valider les dépendances et la cohérence de la configuration."""
        if not self.settings:
            return

        # Si tracing est activé, vérifier que l'exporter est configuré
        if self.settings.tracing_enabled and self.settings.tracing_exporter == TracingExporter.NONE:
            self.warnings.append(
                "tracing_enabled is True but tracing_exporter is 'none'. Tracing may not work correctly."
            )

        # Si authz est activé, vérifier qu'un provider est configuré
        if self.settings.enable_authz and not self.settings.authz_provider:
            self.warnings.append(
                "enable_authz is True but authz_provider is not configured. Authorization may not work."
            )

        # Si cache est activé avec include_tools, vérifier la cohérence
        if self.settings.cache_enabled and self.settings.cache_config:
            include_tools = self.settings.cache_config.get("include_tools", [])
            exclude_tools = self.settings.cache_config.get("exclude_tools", [])
            if include_tools and exclude_tools:
                overlap = set(include_tools) & set(exclude_tools)
                if overlap:
                    self.warnings.append(
                        f"Cache config has overlapping include/exclude tools: {overlap}"
                    )

        # Vérifier que les chemins de découverte existent
        if self.settings.auto_discover:
            base_dir = getattr(self.settings, "_smf_base_dir", self.config_file.parent)
            for path_str in self.settings.discovery_paths:
                path_obj = Path(path_str)
                if not path_obj.is_absolute():
                    path_obj = base_dir / path_obj
                if not path_obj.exists():
                    self.warnings.append(f"Discovery path does not exist: {path_obj}")

        # Vérifier que les chemins de plugins existent
        for path_str in self.settings.plugin_paths:
            path_obj = Path(path_str)
            if not path_obj.is_absolute():
                base_dir = getattr(self.settings, "_smf_base_dir", self.config_file.parent)
                path_obj = base_dir / path_obj
            if not path_obj.exists() and "." not in path_str:  # Peut être un module Python
                self.warnings.append(f"Plugin path may not exist: {path_obj}")


def validate_config_file(config_file: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Valider un fichier de configuration SMF.

    Args:
        config_file: Chemin vers le fichier de configuration

    Returns:
        Tuple (success, errors, warnings)
    """
    validator = ConfigValidator(config_file)
    return validator.validate()

