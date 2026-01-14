import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def add_parser(subparsers) -> None:
    inspector_parser = subparsers.add_parser(
        "inspector",
        help="Launch MCP Inspector for testing SMF servers",
        description="Launch the official MCP Inspector using npx to test and debug SMF servers.",
        epilog="""
Examples:
  # Launch Inspector for server.py
  smf inspector server.py
  
  # Launch Inspector with default server.py
  smf inspector
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    inspector_parser.add_argument(
        "server",
        help="Server file path (e.g., server.py)",
        nargs="?",
        default="server.py",
    )
    inspector_parser.set_defaults(func=inspector_command)


def inspector_command(args: argparse.Namespace) -> int:
    """
    Run the official MCP Inspector using npx.

    Args:
        args: CLI arguments containing server file path

    Returns:
        Exit code
    """
    server_file = args.server

    # Check for npx
    npx_path = shutil.which("npx")
    if not npx_path:
        print("Error: 'npx' is required to run the inspector.", file=sys.stderr)
        print("Please install Node.js and npm.", file=sys.stderr)
        return 1

    # Construct command
    # npx -y @modelcontextprotocol/inspector uv run <server_file>
    # Use the resolved npx path
    # Also resolve server_file to absolute path to avoid issues with relative paths (like .\server.py)
    # when passed through npx/inspector on Windows.
    # IMPORTANT: Use .as_posix() to ensure forward slashes are used.
    # Backslashes can be stripped or misinterpreted as escape characters when passed through
    # the inspector's argument parsing or shell execution, leading to "H:Desktopsmfadminserver.py".
    server_path = Path(server_file).resolve().as_posix()
    cmd = [npx_path, "-y", "@modelcontextprotocol/inspector", "uv", "run", server_path]

    print(f"Launching MCP Inspector for {server_file}...")
    print(f"Command: {' '.join(cmd)}")

    try:
        # Run interactively
        # On Windows, shell=True is often needed for .cmd files even with full path
        use_shell = sys.platform == "win32"
        return subprocess.call(cmd, shell=use_shell)
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        print(f"Error running inspector: {e}", file=sys.stderr)
        return 1
