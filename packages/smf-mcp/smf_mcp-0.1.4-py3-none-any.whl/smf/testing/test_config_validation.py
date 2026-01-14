"""
Tests pour valider que tous les paramètres de configuration smf.yaml fonctionnent correctement.

Ce module teste:
- Le chargement des paramètres depuis un fichier YAML
- La validation des valeurs (log_level, environment, etc.)
- L'application des paramètres au serveur lors de la création
- Les cas d'erreur avec des valeurs invalides
"""

import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

from smf import create_server
from smf.settings import (
    AuthProvider,
    Settings,
    StorageBackend,
    TracingExporter,
    TransportType,
    load_settings,
)


class TestConfigLoading:
    """Tests pour le chargement de configuration depuis smf.yaml."""

    def test_load_all_config_parameters(self):
        """Test que tous les paramètres peuvent être chargés depuis un fichier YAML."""
        config = {
            "server_name": "Test SMF Server",
            "server_version": "1.0.0",
            "server_instructions": "Test instructions",
            "strict_input_validation": True,
            "include_fastmcp_meta": False,
            "mask_error_details": True,
            "duplicate_policy": "error",
            "transport": "stdio",
            "host": "0.0.0.0",
            "port": 8000,
            "log_level": "INFO",
            "log_format": "json",
            "structured_logging": True,
            "auth_provider": "none",
            "auth_config": {},
            "enable_authz": False,
            "rate_limit_enabled": True,
            "rate_limit_per_minute": 60,
            "rate_limit_per_hour": 1000,
            "cache_enabled": False,
            "cache_backend": "memory",
            "cache_ttl": 300,
            "cache_config": {},
            "metrics_enabled": True,
            "metrics_path": "/metrics",
            "tracing_enabled": False,
            "tracing_exporter": "none",
            "storage_backend": "memory",
            "storage_config": {},
            "auto_discover": True,
            "discovery_paths": [],
            "plugin_paths": [],
            "governance_enabled": False,
            "governance_config": {},
            "environment": "production",
            "debug": False,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            settings = Settings.from_file(config_path)

            # Vérifier que tous les paramètres sont chargés
            assert settings.server_name == "Test SMF Server"
            assert settings.server_version == "1.0.0"
            assert settings.server_instructions == "Test instructions"
            assert settings.strict_input_validation is True
            assert settings.include_fastmcp_meta is False
            assert settings.mask_error_details is True
            assert settings.duplicate_policy == "error"
            assert settings.transport == TransportType.STDIO
            assert settings.host == "0.0.0.0"
            assert settings.port == 8000
            assert settings.log_level == "INFO"
            assert settings.log_format == "json"
            assert settings.structured_logging is True
            assert settings.auth_provider == AuthProvider.NONE
            assert settings.enable_authz is False
            assert settings.rate_limit_enabled is True
            assert settings.rate_limit_per_minute == 60
            assert settings.rate_limit_per_hour == 1000
            assert settings.cache_enabled is False
            assert settings.cache_backend == StorageBackend.MEMORY
            assert settings.cache_ttl == 300
            assert settings.metrics_enabled is True
            assert settings.metrics_path == "/metrics"
            assert settings.tracing_enabled is False
            assert settings.tracing_exporter == TracingExporter.NONE
            assert settings.storage_backend == StorageBackend.MEMORY
            assert settings.auto_discover is True
            assert settings.governance_enabled is False
            assert settings.environment == "production"
            assert settings.debug is False

    def test_load_config_with_all_transport_types(self):
        """Test le chargement avec tous les types de transport."""
        transports = ["stdio", "http", "sse"]
        for transport in transports:
            config = {"transport": transport}
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = Path(tmpdir) / "smf.yaml"
                with open(config_path, "w") as f:
                    yaml.dump(config, f)

                settings = Settings.from_file(config_path)
                assert settings.transport == TransportType(transport)

    def test_load_config_with_all_auth_providers(self):
        """Test le chargement avec tous les providers d'authentification."""
        providers = ["none", "jwt", "oauth", "oauth_proxy", "remote", "token_verifier"]
        for provider in providers:
            config = {"auth_provider": provider}
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = Path(tmpdir) / "smf.yaml"
                with open(config_path, "w") as f:
                    yaml.dump(config, f)

                settings = Settings.from_file(config_path)
                assert settings.auth_provider == AuthProvider(provider)

    def test_load_config_with_all_environments(self):
        """Test le chargement avec tous les environnements."""
        environments = ["development", "staging", "production"]
        for env in environments:
            config = {"environment": env}
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = Path(tmpdir) / "smf.yaml"
                with open(config_path, "w") as f:
                    yaml.dump(config, f)

                settings = Settings.from_file(config_path)
                assert settings.environment == env

    def test_load_config_with_all_log_levels(self):
        """Test le chargement avec tous les niveaux de log."""
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in log_levels:
            config = {"log_level": level}
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = Path(tmpdir) / "smf.yaml"
                with open(config_path, "w") as f:
                    yaml.dump(config, f)

                settings = Settings.from_file(config_path)
                assert settings.log_level == level

    def test_load_config_with_complex_dicts(self):
        """Test le chargement avec des dictionnaires complexes."""
        config = {
            "auth_config": {"secret": "test-secret", "algorithm": "HS256"},
            "cache_config": {
                "key_prefix": "smf",
                "include_tools": ["tool1", "tool2"],
                "exclude_resources": ["resource1"],
            },
            "storage_config": {"host": "localhost", "port": 5432},
            "governance_config": {
                "handlers": ["my_module:handler"],
                "mode": "error",
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            settings = Settings.from_file(config_path)
            assert settings.auth_config == config["auth_config"]
            assert settings.cache_config == config["cache_config"]
            assert settings.storage_config == config["storage_config"]
            assert settings.governance_config == config["governance_config"]

    def test_load_config_with_lists(self):
        """Test le chargement avec des listes."""
        config = {
            "discovery_paths": ["src/tools", "src/resources"],
            "plugin_paths": ["plugins/my_plugin.py"],
            "include_tags": ["public", "v1"],
            "exclude_tags": ["internal"],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            settings = Settings.from_file(config_path)
            assert settings.discovery_paths == config["discovery_paths"]
            assert settings.plugin_paths == config["plugin_paths"]
            assert settings.include_tags == config["include_tags"]
            assert settings.exclude_tags == config["exclude_tags"]


class TestConfigValidation:
    """Tests pour la validation des paramètres de configuration."""

    def test_validate_log_level_invalid(self):
        """Test que les niveaux de log invalides sont rejetés."""
        config = {"log_level": "INVALID"}
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            with pytest.raises(ValueError, match="Log level must be one of"):
                Settings.from_file(config_path)

    def test_validate_environment_invalid(self):
        """Test que les environnements invalides sont rejetés."""
        config = {"environment": "invalid"}
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            with pytest.raises(ValueError, match="Environment must be one of"):
                Settings.from_file(config_path)

    def test_validate_log_level_case_insensitive(self):
        """Test que les niveaux de log sont normalisés en majuscules."""
        config = {"log_level": "info"}
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            settings = Settings.from_file(config_path)
            assert settings.log_level == "INFO"

    def test_validate_environment_case_insensitive(self):
        """Test que les environnements sont normalisés en minuscules."""
        config = {"environment": "PRODUCTION"}
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            settings = Settings.from_file(config_path)
            assert settings.environment == "production"


class TestConfigApplication:
    """Tests pour vérifier que les paramètres sont appliqués au serveur."""

    def test_server_creation_with_all_settings(self):
        """Test que tous les paramètres sont appliqués lors de la création du serveur."""
        config = {
            "server_name": "Test Server",
            "server_version": "1.0.0",
            "server_instructions": "Test instructions",
            "strict_input_validation": True,
            "include_fastmcp_meta": False,
            "mask_error_details": True,
            "duplicate_policy": "error",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            settings = Settings.from_file(config_path)
            mcp = create_server(settings=settings)

            # Vérifier que les paramètres FastMCP sont appliqués
            fastmcp_params = settings.to_fastmcp_params()
            assert mcp.name == fastmcp_params["name"]
            assert mcp.strict_input_validation == fastmcp_params["strict_input_validation"]
            assert mcp.include_fastmcp_meta == fastmcp_params["include_fastmcp_meta"]
            # mask_error_details est passé au constructeur mais n'est pas un attribut exposé
            # Vérifier via les settings à la place
            assert settings.mask_error_details == fastmcp_params["mask_error_details"]

    def test_to_fastmcp_params_includes_all_relevant_settings(self):
        """Test que to_fastmcp_params() inclut tous les paramètres pertinents."""
        config = {
            "server_name": "Test Server",
            "server_version": "1.0.0",
            "server_instructions": "Test instructions",
            "strict_input_validation": True,
            "include_fastmcp_meta": False,
            "mask_error_details": True,
            "include_tags": ["public"],
            "exclude_tags": ["internal"],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            settings = Settings.from_file(config_path)
            params = settings.to_fastmcp_params()

            assert "name" in params
            assert "strict_input_validation" in params
            assert "include_fastmcp_meta" in params
            assert "mask_error_details" in params
            assert "version" in params
            assert "instructions" in params
            assert "include_tags" in params
            assert "exclude_tags" in params

    def test_duplicate_policy_applied_to_registry(self):
        """Test que duplicate_policy est appliqué au registre."""
        for policy in ["error", "warn", "ignore"]:
            config = {"duplicate_policy": policy}
            with tempfile.TemporaryDirectory() as tmpdir:
                config_path = Path(tmpdir) / "smf.yaml"
                with open(config_path, "w") as f:
                    yaml.dump(config, f)

                settings = Settings.from_file(config_path)
                from smf.core import ServerFactory

                factory = ServerFactory(settings)
                assert factory.registry._duplicate_policy == policy


class TestConfigDefaults:
    """Tests pour vérifier les valeurs par défaut."""

    def test_default_settings(self):
        """Test que les valeurs par défaut sont correctes."""
        settings = Settings()

        assert settings.server_name == "SMF Server"
        assert settings.strict_input_validation is True
        assert settings.include_fastmcp_meta is False
        assert settings.mask_error_details is True
        assert settings.duplicate_policy == "error"
        assert settings.transport == TransportType.STDIO
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.log_level == "INFO"
        assert settings.log_format == "json"
        assert settings.structured_logging is True
        assert settings.auth_provider == AuthProvider.NONE
        assert settings.enable_authz is False
        assert settings.rate_limit_enabled is True
        assert settings.rate_limit_per_minute == 60
        assert settings.rate_limit_per_hour == 1000
        assert settings.cache_enabled is False
        assert settings.cache_backend == StorageBackend.MEMORY
        assert settings.cache_ttl == 300
        assert settings.metrics_enabled is True
        assert settings.metrics_path == "/metrics"
        assert settings.tracing_enabled is False
        assert settings.tracing_exporter == TracingExporter.NONE
        assert settings.storage_backend == StorageBackend.MEMORY
        assert settings.auto_discover is True
        assert settings.governance_enabled is False
        assert settings.environment == "production"
        assert settings.debug is False

    def test_development_environment_sets_debug(self):
        """Test que l'environnement development active debug automatiquement."""
        config = {"environment": "development"}
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            settings = Settings.from_file(config_path)
            assert settings.debug is True

    def test_debug_mode_sets_log_level_and_mask_error_details(self):
        """Test que le mode debug modifie log_level et mask_error_details."""
        config = {"debug": True}
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            settings = Settings.from_file(config_path)
            assert settings.log_level == "DEBUG"
            assert settings.mask_error_details is False

    def test_tracing_enabled_sets_exporter(self):
        """Test que l'activation du tracing définit l'exporter par défaut."""
        config = {"tracing_enabled": True}
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            settings = Settings.from_file(config_path)
            assert settings.tracing_exporter == TracingExporter.OTEL


class TestConfigFileDiscovery:
    """Tests pour la découverte automatique des fichiers de configuration."""

    def test_load_settings_finds_smf_yaml(self):
        """Test que load_settings trouve smf.yaml."""
        config = {"server_name": "Found Server"}
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            settings = load_settings(base_dir=Path(tmpdir))
            assert settings.server_name == "Found Server"

    def test_load_settings_finds_smf_yml(self):
        """Test que load_settings trouve smf.yml."""
        config = {"server_name": "Found Server YML"}
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            settings = load_settings(base_dir=Path(tmpdir))
            assert settings.server_name == "Found Server YML"

    def test_load_settings_uses_defaults_when_no_file(self):
        """Test que load_settings utilise les valeurs par défaut si aucun fichier."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = load_settings(base_dir=Path(tmpdir))
            assert settings.server_name == "SMF Server"


class TestRealWorldConfig:
    """Tests avec une configuration réelle comme celle générée par le framework."""

    def test_admin_server_config(self):
        """Test avec la configuration réelle du serveur admin."""
        # Configuration basée sur admin/smf.yaml
        config = {
            "server_name": "SMF Server",
            "strict_input_validation": True,
            "include_fastmcp_meta": False,
            "mask_error_details": True,
            "duplicate_policy": "error",
            "transport": "stdio",
            "host": "0.0.0.0",
            "port": 8000,
            "log_level": "INFO",
            "log_format": "json",
            "structured_logging": True,
            "auth_provider": "none",
            "auth_config": {},
            "enable_authz": False,
            "rate_limit_enabled": True,
            "rate_limit_per_minute": 60,
            "rate_limit_per_hour": 1000,
            "cache_enabled": False,
            "cache_backend": "memory",
            "cache_ttl": 300,
            "cache_config": {},
            "metrics_enabled": True,
            "metrics_path": "/metrics",
            "tracing_enabled": False,
            "tracing_exporter": "none",
            "storage_backend": "memory",
            "storage_config": {},
            "auto_discover": True,
            "discovery_paths": [],
            "plugin_paths": [],
            "governance_enabled": False,
            "governance_config": {},
            "environment": "production",
            "debug": False,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "smf.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            # Charger et créer le serveur
            settings = Settings.from_file(config_path)
            mcp = create_server(settings=settings)

            # Vérifier que le serveur est créé avec succès
            assert mcp is not None
            assert mcp.name == "SMF Server"
            assert mcp.strict_input_validation is True
            assert mcp.include_fastmcp_meta is False
            # mask_error_details est passé au constructeur mais n'est pas un attribut exposé
            # Vérifier via les settings à la place
            assert settings.mask_error_details is True

            # Vérifier que tous les paramètres sont accessibles
            assert settings.transport == TransportType.STDIO
            assert settings.host == "0.0.0.0"
            assert settings.port == 8000
            assert settings.log_level == "INFO"
            assert settings.log_format == "json"
            assert settings.structured_logging is True
            assert settings.auth_provider == AuthProvider.NONE
            assert settings.rate_limit_enabled is True
            assert settings.cache_enabled is False
            assert settings.metrics_enabled is True
            assert settings.tracing_enabled is False
            assert settings.auto_discover is True
            assert settings.environment == "production"
            assert settings.debug is False

