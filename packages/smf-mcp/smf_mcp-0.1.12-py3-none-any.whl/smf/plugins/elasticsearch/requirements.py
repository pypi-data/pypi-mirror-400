import importlib.metadata
from pathlib import Path

from smf.plugins.elasticsearch.template_loader import requirements_template
from smf.cli.io import write_utf8


def _get_version() -> str:
    try:
        return importlib.metadata.version("smf-mcp")
    except importlib.metadata.PackageNotFoundError:
        return "0.1.4"


def write_requirements(project_path: Path) -> None:
    requirements_file = project_path / "requirements.txt"
    write_utf8(requirements_file, requirements_template(_get_version()))


def ensure_requirements(project_path: Path) -> None:
    req_file = project_path / "requirements.txt"
    if req_file.exists():
        req_content = req_file.read_text(encoding="utf-8")
        # Check for both smf-mcp[elasticsearch] and smf[elasticsearch] (backward compatibility)
        if "smf-mcp[elasticsearch]" not in req_content and "smf[elasticsearch]" not in req_content:
            with open(req_file, "a", encoding="utf-8") as f:
                f.write(f"\nsmf-mcp[elasticsearch]>={_get_version()}\n")
            print("? Added smf-mcp[elasticsearch] to requirements.txt")
    else:
        # Create with version when file doesn't exist
        write_requirements(project_path)
        print("? Created requirements.txt")
