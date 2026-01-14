from pathlib import Path


def resolve_project_dir(directory: str) -> Path:
    project_dir = Path(directory).resolve()
    if not (project_dir / "smf.yaml").exists() and not (project_dir / "smf.json").exists():
        if (project_dir.parent / "smf.yaml").exists() or (project_dir.parent / "smf.json").exists():
            project_dir = project_dir.parent
        else:
            project_dir = Path(".").resolve()
    return project_dir
