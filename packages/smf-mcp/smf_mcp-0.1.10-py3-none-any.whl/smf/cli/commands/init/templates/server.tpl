import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from smf import create_server

# Create server
mcp = create_server()

# Import components
from tools.tools import greet as greet_tool, calculate as calculate_tool

# Register tools
@mcp.tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return greet_tool(name)

@mcp.tool
def calculate(operation: str, a: float, b: float) -> float:
    """Perform a calculation."""
    return calculate_tool(operation, a, b)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run mcp server")
    parser.add_argument("--transport", help="Transport type")
    parser.add_argument("--host", help="HTTP host")
    parser.add_argument("--port", type=int, help="HTTP port")
    args = parser.parse_args()

    from smf.transport import run_server

    run_server(
        mcp,
        transport=args.transport or "stdio",
        host=args.host or "0.0.0.0",
        port=args.port or 8000,
    )
