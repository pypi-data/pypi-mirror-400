"""
Observability - Metrics and Health Checks.

Provides Prometheus metrics and health/readiness endpoints.
"""

from typing import Any, Dict, Optional

from fastmcp import FastMCP

from smf.settings import Settings


class MetricsCollector:
    """Collects Prometheus metrics for MCP operations."""

    def __init__(self):
        """Initialize metrics collector."""
        self._metrics: Dict[str, Any] = {}
        self._prometheus_client = None

        try:
            from prometheus_client import Counter, Histogram

            self._tool_calls_total = Counter(
                "smf_tool_calls_total",
                "Total number of tool calls",
                ["tool_name", "status"],
            )
            self._tool_duration_seconds = Histogram(
                "smf_tool_duration_seconds",
                "Tool call duration in seconds",
                ["tool_name"],
            )
            self._resource_reads_total = Counter(
                "smf_resource_reads_total",
                "Total number of resource reads",
                ["resource_uri"],
            )
            self._prometheus_client = True
        except ImportError:
            # Prometheus client not installed
            pass

    def record_tool_call(self, tool_name: str, duration: float, success: bool) -> None:
        """
        Record a tool call metric.

        Args:
            tool_name: Name of the tool
            duration: Call duration in seconds
            success: Whether call succeeded
        """
        if not self._prometheus_client:
            return

        status = "success" if success else "error"
        self._tool_calls_total.labels(tool_name=tool_name, status=status).inc()
        self._tool_duration_seconds.labels(tool_name=tool_name).observe(duration)

    def record_resource_read(self, resource_uri: str) -> None:
        """
        Record a resource read metric.

        Args:
            resource_uri: Resource URI
        """
        if not self._prometheus_client:
            return

        self._resource_reads_total.labels(resource_uri=resource_uri).inc()


_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def attach_metrics(mcp: FastMCP, settings: Settings) -> None:
    """
    Attach metrics collection to FastMCP server.

    Args:
        mcp: FastMCP server instance
        settings: SMF settings
    """
    if not settings.metrics_enabled:
        return

    collector = get_metrics_collector()

    # Attach metrics hooks
    if hasattr(mcp, "on_call_tool"):
        import time

        original_call_tool = getattr(mcp, "on_call_tool", None)

        def metrics_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Any:
            start_time = time.time()
            success = True
            try:
                if original_call_tool:
                    result = original_call_tool(tool_name, arguments)
                    return result
            except Exception:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                collector.record_tool_call(tool_name, duration, success)

        mcp.on_call_tool = metrics_tool_call

    if hasattr(mcp, "on_read_resource"):
        original_read_resource = getattr(mcp, "on_read_resource", None)

        def metrics_resource_read(resource_uri: str) -> Any:
            collector.record_resource_read(resource_uri)
            if original_read_resource:
                return original_read_resource(resource_uri)

        mcp.on_read_resource = metrics_resource_read


def attach_metrics_endpoint(mcp: FastMCP, settings: Settings) -> None:
    if not settings.metrics_enabled or not settings.metrics_path:
        return

    if getattr(mcp, "_smf_metrics_endpoint_attached", False):
        return

    if not hasattr(mcp, "http_app"):
        return

    try:
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
    except ImportError:
        return

    app = mcp.http_app()
    if app is None:
        return

    Response = None
    try:
        from fastapi import Response as FastAPIResponse

        Response = FastAPIResponse
    except ImportError:
        try:
            from starlette.responses import Response as StarletteResponse

            Response = StarletteResponse
        except ImportError:
            return

    def metrics_endpoint(request):
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    if hasattr(app, "add_api_route"):
        app.add_api_route(settings.metrics_path, metrics_endpoint, methods=["GET"])
    elif hasattr(app, "add_route"):
        app.add_route(settings.metrics_path, metrics_endpoint, methods=["GET"])
    else:
        return

    setattr(mcp, "_smf_metrics_endpoint_attached", True)


def get_health_status() -> Dict[str, Any]:
    """
    Get health status for health check endpoint.

    Returns:
        Health status dictionary
    """
    return {
        "status": "healthy",
        "version": "0.1.4",
    }


def get_readiness_status() -> Dict[str, Any]:
    """
    Get readiness status for readiness check endpoint.

    Returns:
        Readiness status dictionary
    """
    return {
        "ready": True,
    }

