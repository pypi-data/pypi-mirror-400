"""
Pytest fixtures for testing SMF servers.

Based on FastMCP testing patterns:
https://fastmcp.wiki/en/patterns/testing
"""

from typing import AsyncGenerator, Optional

import pytest
from fastmcp import FastMCP
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport

from smf.settings import Settings


@pytest.fixture
async def mcp_server_fixture(mcp: Optional[FastMCP] = None) -> FastMCP:
    """
    Fixture for creating a FastMCP server instance.
    
    Usage:
        @pytest.fixture
        def mcp(mcp_server_fixture):
            return mcp_server_fixture
    
    Or override with your own server:
        @pytest.fixture
        def mcp():
            return create_server("Test Server")
    """
    if mcp is None:
        from smf import create_server
        return create_server("Test SMF Server")
    return mcp


@pytest.fixture
async def mcp_client_fixture(
    mcp_server_fixture: FastMCP,
) -> AsyncGenerator[Client[FastMCPTransport], None]:
    """
    Fixture for creating a FastMCP client connected to a server.
    
    Usage:
        async def test_list_tools(mcp_client_fixture: Client[FastMCPTransport]):
            tools = await mcp_client_fixture.list_tools()
            assert len(tools) > 0
    """
    async with Client(transport=mcp_server_fixture) as client:
        yield client


@pytest.fixture
def smf_settings() -> Settings:
    """
    Fixture for creating SMF settings for testing.
    
    Usage:
        def test_with_settings(smf_settings: Settings):
            settings.server_name = "Test Server"
            # ...
    """
    return Settings(
        server_name="Test Server",
        structured_logging=False,  # Disable logging in tests
        metrics_enabled=False,  # Disable metrics in tests
        rate_limit_enabled=False,  # Disable rate limiting in tests
    )

