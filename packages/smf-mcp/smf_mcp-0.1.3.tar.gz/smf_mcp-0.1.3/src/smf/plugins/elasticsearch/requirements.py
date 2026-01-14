import importlib.metadata
from pathlib import Path

from smf.plugins.elasticsearch.templates import requirements_template
from smf.cli.io import write_utf8


def _get_version() -> str:
    try:
        return importlib.metadata.version("smf-mcp")
    except importlib.metadata.PackageNotFoundError:
        return "0.1.1"


def write_requirements(project_path: Path) -> None:
    requirements_file = project_path / "requirements.txt"
    write_utf8(requirements_file, requirements_template(_get_version()))


def ensure_requirements(project_path: Path) -> None:
    req_file = project_path / "requirements.txt"
    if req_file.exists():
        req_content = req_file.read_text(encoding="utf-8")
        if "smf[elasticsearch]" not in req_content:
            with open(req_file, "a", encoding="utf-8") as f:
                f.write("\nsmf-mcp[elasticsearch]\n")
            print("? Added smf-mcp[elasticsearch] to requirements.txt")
    else:
        write_utf8(req_file, "smf-mcp[elasticsearch]\n")
        print("? Created requirements.txt")
