from pathlib import Path

from smf.cli.commands.init.templates import readme_template
from smf.cli.io import write_utf8


def write_readme(project_path: Path, project_name: str) -> None:
    readme_file = project_path / "README.md"
    write_utf8(readme_file, readme_template(project_name))
