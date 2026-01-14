import json
from pathlib import Path

from smf.settings import Settings


def write_settings(project_path: Path, server_name: str) -> None:
    settings_file = project_path / "smf.yaml"
    default_settings = Settings(
        server_name=server_name,
        structured_logging=True,
        metrics_enabled=True,
    ).model_dump(exclude_none=True, mode="json")

    try:
        import yaml

        with open(settings_file, "w", encoding="utf-8") as f:
            yaml.dump(default_settings, f, default_flow_style=False, sort_keys=False)
    except ImportError:
        settings_file = project_path / "smf.json"
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(default_settings, f, indent=2)
