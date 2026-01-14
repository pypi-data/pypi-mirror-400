from pathlib import Path

from smf.cli.commands.init.template_loader import (
    example_prompt_template,
    example_resource_template,
    example_test_template,
    example_tool_template,
)
from smf.cli.io import write_utf8


def write_examples(paths: dict[str, Path]) -> None:
    tools_dir = paths["tools"]
    resources_dir = paths["resources"]
    prompts_dir = paths["prompts"]
    tests_dir = paths["tests"]

    write_utf8(tools_dir / "tools.py", example_tool_template())
    write_utf8(resources_dir / "resources.py", example_resource_template())
    write_utf8(prompts_dir / "prompts.py", example_prompt_template())
    write_utf8(tests_dir / "tests.py", example_test_template())
