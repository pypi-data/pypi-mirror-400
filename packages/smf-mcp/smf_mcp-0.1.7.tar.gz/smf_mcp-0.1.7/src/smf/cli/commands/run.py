import argparse
import sys
from pathlib import Path


def add_parser(subparsers) -> None:
    run_parser = subparsers.add_parser("run", help="Run server")
    run_parser.add_argument("server", help="Server file path")
    run_parser.add_argument("--transport", help="Transport type")
    run_parser.add_argument("--host", help="HTTP host")
    run_parser.add_argument("--port", type=int, help="HTTP port")
    run_parser.add_argument("--config", help="Config file path")
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

    from smf.settings import get_settings, load_settings, set_settings

    if args.config:
        config_file = Path(args.config)
        if not config_file.exists():
            print(f"Error: Config file not found: {config_file}")
            return 1
        set_settings(load_settings(base_dir=config_file.parent, config_file=config_file))
    else:
        get_settings(base_dir=server_file.parent)

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
        run_kwargs = {}
        if args.transport:
            run_kwargs["transport"] = args.transport
        if args.host:
            run_kwargs["host"] = args.host
        if args.port is not None:
            run_kwargs["port"] = args.port
        run_server(mcp, **run_kwargs)
    except KeyboardInterrupt:
        try:
            print("\nServer stopped", file=sys.stderr)
        except ValueError:
            pass
        return 0
    except Exception as e:
        print(f"Error running server: {e}")
        return 1
