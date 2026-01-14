import argparse
import importlib


_COMMAND_MODULES = [
    "smf.cli.commands.init",
    "smf.cli.commands.run",
    "smf.cli.commands.inspector",
    "smf.plugins.elasticsearch",
]


def build_parser(version: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SMF - Stellantis MCP Framework")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version}",
        help="Show the version and exit",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    for module_name in _COMMAND_MODULES:
        module = importlib.import_module(module_name)
        module.add_parser(subparsers)

    return parser
