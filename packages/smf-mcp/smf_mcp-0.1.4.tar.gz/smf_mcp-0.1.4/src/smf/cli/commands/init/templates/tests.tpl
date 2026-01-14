import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import pytest
import pytest_asyncio
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport

from smf import create_server


@pytest.fixture
def mcp():
    """Create test MCP server with example tools."""
    mcp = create_server("Test Server")
    
    # Import and register example tools
    from tools.example_tool import greet as greet_tool, calculate as calculate_tool
    
    @mcp.tool
    def greet(name: str) -> str:
        """Greet someone by name."""
        return greet_tool(name)
    
    @mcp.tool
    def calculate(operation: str, a: float, b: float) -> float:
        """Perform a calculation."""
        return calculate_tool(operation, a, b)
    
    return mcp


@pytest_asyncio.fixture
async def mcp_client(mcp):
    """Create a client connected to the test server."""
    async with Client(transport=mcp) as client:
        yield client


# Unit tests (testing functions directly)
def test_greet_function():
    """Test greet function directly."""
    from tools.example_tool import greet
    result = greet("Alice")
    assert "Alice" in result
    assert "Hello" in result


def test_calculate_add():
    """Test calculate function - addition."""
    from tools.example_tool import calculate
    result = calculate("add", 5, 3)
    assert result == 8


def test_calculate_multiply():
    """Test calculate function - multiplication."""
    from tools.example_tool import calculate
    result = calculate("multiply", 4, 7)
    assert result == 28


def test_calculate_divide():
    """Test calculate function - division."""
    from tools.example_tool import calculate
    result = calculate("divide", 10, 2)
    assert result == 5.0


def test_calculate_divide_by_zero():
    """Test calculate function - division by zero error."""
    from tools.example_tool import calculate
    with pytest.raises(ValueError, match="Division by zero"):
        calculate("divide", 10, 0)


# Integration tests (testing via MCP Client)
@pytest.mark.asyncio
async def test_list_tools(mcp_client: Client[FastMCPTransport]):
    """Test listing tools via MCP client."""
    tools = await mcp_client.list_tools()
    assert len(tools) >= 2
    tool_names = [tool.name for tool in tools]
    assert "greet" in tool_names
    assert "calculate" in tool_names


@pytest.mark.parametrize(
    "name, expected_contains",
    [
        ("Alice", "Alice"),
        ("Bob", "Bob"),
        ("World", "World"),
    ],
)
@pytest.mark.asyncio
async def test_greet_tool(
    name: str,
    expected_contains: str,
    mcp_client: Client[FastMCPTransport],
):
    """Test greet tool via MCP client with parametrize."""
    result = await mcp_client.call_tool(name="greet", arguments={"name": name})
    assert result.data is not None
    assert isinstance(result.data, str)
    assert expected_contains in result.data


@pytest.mark.parametrize(
    "operation, a, b, expected",
    [
        ("add", 1, 2, 3),
        ("add", 5, 3, 8),
        ("multiply", 4, 7, 28),
        ("multiply", 2, 3, 6),
        ("divide", 10, 2, 5.0),
        ("divide", 15, 3, 5.0),
        ("subtract", 10, 3, 7),
    ],
)
@pytest.mark.asyncio
async def test_calculate_tool(
    operation: str,
    a: float,
    b: float,
    expected: float,
    mcp_client: Client[FastMCPTransport],
):
    """Test calculate tool via MCP client with parametrize."""
    result = await mcp_client.call_tool(
        name="calculate",
        arguments={"operation": operation, "a": a, "b": b}
    )
    assert result.data is not None
    assert isinstance(result.data, (int, float))
    assert result.data == expected
