import argparse

from smf.cli.commands.tool.project import resolve_project_dir
from smf.cli.commands.tool.template_loader import tool_template
from smf.cli.io import write_utf8


def add_parser(subparsers) -> None:
    add_tool_parser = subparsers.add_parser("add-tool", help="Add new tool")
    add_tool_parser.add_argument("name", help="Tool name")
    add_tool_parser.add_argument("--directory", default=".", help="Project directory")
    add_tool_parser.add_argument("--description", help="Tool description")
    add_tool_parser.add_argument("--force", action="store_true", help="Overwrite existing")
    add_tool_parser.set_defaults(func=add_tool_command)


def add_tool_command(args: argparse.Namespace) -> int:
    tool_name = args.name

    project_dir = resolve_project_dir(args.directory)
    tool_file = project_dir / "src" / "tools" / f"{tool_name}.py"

    if tool_file.exists() and not args.force:
        print(f"Error: Tool {tool_name} already exists. Use --force to overwrite.")
        return 1

    tool_file.parent.mkdir(parents=True, exist_ok=True)

    init_file = tool_file.parent / "__init__.py"
    if not init_file.exists():
        write_utf8(init_file, '"""Tools module."""\n')

    write_utf8(tool_file, tool_template(tool_name, args.description))

    print(f"? Created tool template: {tool_file}")
    print("  To use it, import and register in server.py:")
    print(f"    from src.tools.{tool_name} import {tool_name}")
    print("    @mcp.tool")
    print(f"    {tool_name}")
    return 0
