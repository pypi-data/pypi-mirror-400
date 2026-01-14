import json
from pathlib import Path


def write_settings(project_path: Path) -> None:
    """Write a simple config file (optional, for reference)."""
    settings_file = project_path / "mcp-config.yaml"
    default_settings = {
        "server_name": "SMF Server",
    }
    try:
        import yaml

        with open(settings_file, "w", encoding="utf-8") as f:
            yaml.dump(default_settings, f, default_flow_style=False, sort_keys=False)
    except ImportError:
        settings_file = project_path / "mcp-config.json"
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(default_settings, f, indent=2)
