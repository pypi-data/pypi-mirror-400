"""
Transport Abstraction.

Wraps FastMCP transport mechanisms (stdio, HTTP, SSE) with strategy pattern.
"""

from typing import Any, Callable, Dict, Optional

from fastmcp import FastMCP

from smf.settings import Settings, TransportType


class TransportStrategy:
    """
    Strategy for selecting and configuring transport.

    Uses Strategy + Adapter pattern to select transport based on config.
    """

    def __init__(self, settings: Settings):
        """
        Initialize transport strategy.

        Args:
            settings: SMF settings
        """
        self.settings = settings

    def run(self, mcp: FastMCP, **kwargs: Any) -> None:
        """
        Run server with configured transport.

        Args:
            mcp: FastMCP server instance
            **kwargs: Additional transport parameters
        """
        transport = kwargs.get("transport") or self.settings.transport
        if isinstance(transport, str):
            transport = TransportType(transport.lower())

        if transport == TransportType.STDIO:
            self._run_stdio(mcp)
        elif transport == TransportType.HTTP:
            self._run_http(mcp, **kwargs)
        elif transport == TransportType.SSE:
            self._run_sse(mcp, **kwargs)
        else:
            raise ValueError(f"Unsupported transport: {transport}")

    async def run_async(self, mcp: FastMCP, **kwargs: Any) -> None:
        """
        Run server asynchronously with configured transport.

        Args:
            mcp: FastMCP server instance
            **kwargs: Additional transport parameters
        """
        transport = kwargs.get("transport") or self.settings.transport
        if isinstance(transport, str):
            transport = TransportType(transport.lower())

        if transport == TransportType.STDIO:
            await self._run_stdio_async(mcp)
        elif transport == TransportType.HTTP:
            await self._run_http_async(mcp, **kwargs)
        elif transport == TransportType.SSE:
            await self._run_sse_async(mcp, **kwargs)
        else:
            raise ValueError(f"Unsupported transport: {transport}")

    def _run_stdio(self, mcp: FastMCP) -> None:
        """Run with stdio transport."""
        mcp.run()

    async def _run_stdio_async(self, mcp: FastMCP) -> None:
        """Run with stdio transport (async)."""
        # FastMCP may support async stdio
        if hasattr(mcp, "run_async"):
            await mcp.run_async()
        else:
            # Fallback to sync
            mcp.run()

    def _run_http(self, mcp: FastMCP, **kwargs: Any) -> None:
        """Run with HTTP transport."""
        host = kwargs.get("host") or self.settings.host
        port = kwargs.get("port") or self.settings.port

        if hasattr(mcp, "run"):
            # FastMCP HTTP transport
            mcp.run(transport="http", host=host, port=port)
        else:
            raise NotImplementedError("HTTP transport not available")

    async def _run_http_async(self, mcp: FastMCP, **kwargs: Any) -> None:
        """Run with HTTP transport (async)."""
        host = kwargs.get("host") or self.settings.host
        port = kwargs.get("port") or self.settings.port

        if hasattr(mcp, "run_async"):
            await mcp.run_async(transport="http", host=host, port=port)
        else:
            # Fallback to sync
            self._run_http(mcp, host=host, port=port)

    def _run_sse(self, mcp: FastMCP, **kwargs: Any) -> None:
        """Run with SSE transport."""
        host = kwargs.get("host") or self.settings.host
        port = kwargs.get("port") or self.settings.port

        if hasattr(mcp, "run"):
            mcp.run(transport="sse", host=host, port=port)
        else:
            raise NotImplementedError("SSE transport not available")

    async def _run_sse_async(self, mcp: FastMCP, **kwargs: Any) -> None:
        """Run with SSE transport (async)."""
        host = kwargs.get("host") or self.settings.host
        port = kwargs.get("port") or self.settings.port

        if hasattr(mcp, "run_async"):
            await mcp.run_async(transport="sse", host=host, port=port)
        else:
            # Fallback to sync
            self._run_sse(mcp, host=host, port=port)

    def get_asgi_app(self, mcp: FastMCP) -> Any:
        """
        Get ASGI application for HTTP transport.

        Args:
            mcp: FastMCP server instance

        Returns:
            ASGI application
        """
        if hasattr(mcp, "http_app"):
            return mcp.http_app()
        else:
            raise NotImplementedError("ASGI app not available")


def run_server(mcp: FastMCP, settings: Optional[Settings] = None, **kwargs: Any) -> None:
    """
    Run server with transport abstraction.

    Args:
        mcp: FastMCP server instance
        settings: Optional settings (uses global if None)
        **kwargs: Transport parameters
    """
    from smf.settings import get_settings

    settings = settings or get_settings()
    strategy = TransportStrategy(settings)
    strategy.run(mcp, **kwargs)


async def run_server_async(
    mcp: FastMCP, settings: Optional[Settings] = None, **kwargs: Any
) -> None:
    """
    Run server asynchronously with transport abstraction.

    Args:
        mcp: FastMCP server instance
        settings: Optional settings (uses global if None)
        **kwargs: Transport parameters
    """
    from smf.settings import get_settings

    settings = settings or get_settings()
    strategy = TransportStrategy(settings)
    await strategy.run_async(mcp, **kwargs)

