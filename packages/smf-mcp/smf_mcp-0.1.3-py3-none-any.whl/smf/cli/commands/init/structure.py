from pathlib import Path

from smf.cli.io import write_utf8


def create_structure(project_path: Path) -> dict[str, Path]:
    (project_path / "src").mkdir(exist_ok=True)
    tools_dir = project_path / "src" / "tools"
    resources_dir = project_path / "src" / "resources"
    prompts_dir = project_path / "src" / "prompts"
    tests_dir = project_path / "tests"

    tools_dir.mkdir(parents=True, exist_ok=True)
    resources_dir.mkdir(parents=True, exist_ok=True)
    prompts_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)

    write_utf8(tools_dir / "__init__.py", '"""Tools module."""\n')
    write_utf8(resources_dir / "__init__.py", '"""Resources module."""\n')
    write_utf8(prompts_dir / "__init__.py", '"""Prompts module."""\n')

    return {
        "tools": tools_dir,
        "resources": resources_dir,
        "prompts": prompts_dir,
        "tests": tests_dir,
    }
