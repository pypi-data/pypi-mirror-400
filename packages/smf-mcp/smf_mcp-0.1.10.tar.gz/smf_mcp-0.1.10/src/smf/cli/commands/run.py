import argparse
import sys
from pathlib import Path


def add_parser(subparsers) -> None:
    run_parser = subparsers.add_parser("run", help="Run server")
    run_parser.add_argument("server", help="Server file path")
    run_parser.add_argument("--transport", default="stdio", help="Transport type (default: stdio)")
    run_parser.add_argument("--host", default="0.0.0.0", help="HTTP host (default: 0.0.0.0)")
    run_parser.add_argument("--port", type=int, default=8000, help="HTTP port (default: 8000)")
    run_parser.set_defaults(func=run_command)


def run_command(args: argparse.Namespace) -> int:
    """
    Run SMF server.

    Args:
        args: CLI arguments

    Returns:
        Exit code
    """
    server_file = Path(args.server)
    if not server_file.exists():
        print(f"Error: Server file not found: {server_file}")
        return 1

    # Import and run server
    import importlib.util

    spec = importlib.util.spec_from_file_location("server", server_file)
    if spec is None or spec.loader is None:
        print(f"Error: Cannot import server from {server_file}")
        return 1

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find mcp instance
    if not hasattr(module, "mcp"):
        print("Error: Server module must define 'mcp' variable")
        return 1

    mcp = module.mcp

    # Run server
    from smf.transport import run_server

    try:
        run_server(
            mcp,
            transport=args.transport,
            host=args.host,
            port=args.port,
        )
    except KeyboardInterrupt:
        try:
            print("\nServer stopped", file=sys.stderr)
        except ValueError:
            pass
        return 0
    except Exception as e:
        print(f"Error running server: {e}")
        return 1
