import json
from pathlib import Path

from smf.settings import Settings


def write_settings(project_path: Path) -> None:
    settings_file = project_path / "mcp-config.yaml"
    default_settings = Settings().model_dump(exclude_none=True, mode="json")
    try:
        import yaml

        with open(settings_file, "w", encoding="utf-8") as f:
            yaml.dump(default_settings, f, default_flow_style=False, sort_keys=False)
    except ImportError:
        settings_file = project_path / "mcp-config.json"
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(default_settings, f, indent=2)
