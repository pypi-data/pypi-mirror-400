import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from smf import create_server
from smf.settings import get_settings

get_settings(base_dir=Path(__file__).parent)

# Create server
mcp = create_server()

# Import components
from tools.tools import greet as greet_tool, calculate as calculate_tool
from resources.resources import get_server_info
from prompts.prompts import system_prompt

# Register tools
@mcp.tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return greet_tool(name)

@mcp.tool
def calculate(operation: str, a: float, b: float) -> float:
    """Perform a calculation."""
    return calculate_tool(operation, a, b)

# Register resources
@mcp.resource("server://info")
def server_info() -> str:
    """Get server information."""
    return get_server_info()

# Register prompts
@mcp.prompt
def system() -> str:
    """System prompt template."""
    return system_prompt()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run mcp server")
    parser.add_argument("--transport", help="Transport type")
    parser.add_argument("--host", help="HTTP host")
    parser.add_argument("--port", type=int, help="HTTP port")
    args = parser.parse_args()

    from smf.transport import run_server

    run_kwargs = {}
    if args.transport:
        run_kwargs["transport"] = args.transport
    if args.host:
        run_kwargs["host"] = args.host
    if args.port is not None:
        run_kwargs["port"] = args.port

    run_server(mcp, **run_kwargs)
