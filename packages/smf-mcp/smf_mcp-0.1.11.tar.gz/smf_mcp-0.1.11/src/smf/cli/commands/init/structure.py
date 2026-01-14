from pathlib import Path

from smf.cli.io import write_utf8


def create_structure(project_path: Path) -> dict[str, Path]:
    (project_path / "src").mkdir(exist_ok=True)
    tools_dir = project_path / "src" / "tools"

    tools_dir.mkdir(parents=True, exist_ok=True)

    write_utf8(tools_dir / "__init__.py", '"""Tools module."""\n')

    return {
        "tools": tools_dir,
    }
