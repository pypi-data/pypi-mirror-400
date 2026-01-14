"""
Compatibility wrapper for the SMF CLI.

This module keeps legacy imports working while routing to smf.cli.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import sys
from pathlib import Path

__all__ = [
    "main",
    "write_utf8",
    "init_command",
    "add_tool_command",
    "validate_command",
    "run_command",
]

_LAZY_ATTRS = {
    "write_utf8": ("smf.cli.io", "write_utf8"),
    "init_command": ("smf.cli.commands.init", "init_command"),
    "add_tool_command": ("smf.cli.commands.tool", "add_tool_command"),
    "validate_command": ("smf.cli.commands.validate", "validate_command"),
    "run_command": ("smf.cli.commands.run", "run_command"),
}


def __getattr__(name: str):
    if name in _LAZY_ATTRS:
        module_name, attr = _LAZY_ATTRS[name]
        module = importlib.import_module(module_name)
        value = getattr(module, attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _print_version() -> None:
    prog = Path(sys.argv[0]).name or "smf"
    try:
        version = importlib.metadata.version("smf-mcp")
    except importlib.metadata.PackageNotFoundError:
        version = "unknown"
    print(f"{prog} {version}")


def main() -> int:
    argv = sys.argv[1:]
    if "--version" in argv:
        _print_version()
        return 0

    from smf.cli.main import main as cli_main

    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
