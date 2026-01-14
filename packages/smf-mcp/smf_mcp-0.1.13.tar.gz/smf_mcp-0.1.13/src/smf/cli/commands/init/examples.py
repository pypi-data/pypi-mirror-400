from pathlib import Path

from smf.cli.commands.init.template_loader import (
    example_tool_template,
)
from smf.cli.io import write_utf8


def write_examples(paths: dict[str, Path]) -> None:
    tools_dir = paths["tools"]

    write_utf8(tools_dir / "tools.py", example_tool_template())
