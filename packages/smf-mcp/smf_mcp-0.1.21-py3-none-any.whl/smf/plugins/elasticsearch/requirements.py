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
        # Check for elasticsearch extras (elasticsearch7, elasticsearch8, elasticsearch9)
        has_es_extra = (
            "smf-mcp[elasticsearch7]" in req_content
            or "smf-mcp[elasticsearch8]" in req_content
            or "smf-mcp[elasticsearch9]" in req_content
            or "smf-mcp[elasticsearch]" in req_content  # Backward compatibility
            or "smf[elasticsearch]" in req_content  # Backward compatibility
        )
        if not has_es_extra:
            with open(req_file, "a", encoding="utf-8") as f:
                f.write(f"\n# Choose the version matching your Elasticsearch cluster:\n")
                f.write(f"# smf-mcp[elasticsearch7]>={_get_version()}  # For Elasticsearch 7.x\n")
                f.write(f"# smf-mcp[elasticsearch8]>={_get_version()}  # For Elasticsearch 8.x\n")
                f.write(f"smf-mcp[elasticsearch9]>={_get_version()}  # For Elasticsearch 9.x\n")
            print("? Added smf-mcp[elasticsearch9] to requirements.txt (default)")
    else:
        # Create with version when file doesn't exist
        write_requirements(project_path)
        print("? Created requirements.txt")
