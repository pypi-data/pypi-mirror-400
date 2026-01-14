"""
OpenTelemetry Tracing Middleware.

Provides distributed tracing for MCP operations.
"""

from typing import Any, Dict, Optional

from fastmcp import FastMCP

from smf.settings import Settings, TracingExporter


def attach_tracing(mcp: FastMCP, settings: Settings) -> None:
    """
    Attach OpenTelemetry tracing middleware to FastMCP server.

    Args:
        mcp: FastMCP server instance
        settings: SMF settings
    """
    if settings.tracing_exporter == TracingExporter.NONE:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        # Create tracer provider
        resource = Resource.create({"service.name": settings.server_name})
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)

        # Configure exporter
        if settings.tracing_endpoint:
            exporter = OTLPSpanExporter(endpoint=settings.tracing_endpoint)
        else:
            # Default OTLP endpoint
            exporter = OTLPSpanExporter()

        provider.add_span_processor(BatchSpanProcessor(exporter))

        tracer = trace.get_tracer(__name__)

        # Attach tracing hooks
        if hasattr(mcp, "on_call_tool"):
            original_call_tool = getattr(mcp, "on_call_tool", None)

            def trace_tool_call(tool_name: str, arguments: Dict[str, Any]) -> None:
                with tracer.start_as_current_span(
                    f"tool.{tool_name}", kind=trace.SpanKind.SERVER
                ) as span:
                    span.set_attribute("tool.name", tool_name)
                    span.set_attribute("tool.arguments", str(arguments))
                    if original_call_tool:
                        original_call_tool(tool_name, arguments)

            mcp.on_call_tool = trace_tool_call

        if hasattr(mcp, "on_read_resource"):
            original_read_resource = getattr(mcp, "on_read_resource", None)

            def trace_resource_read(resource_uri: str) -> None:
                with tracer.start_as_current_span(
                    f"resource.read", kind=trace.SpanKind.SERVER
                ) as span:
                    span.set_attribute("resource.uri", resource_uri)
                    if original_read_resource:
                        original_read_resource(resource_uri)

            mcp.on_read_resource = trace_resource_read

    except ImportError:
        # OpenTelemetry not installed - tracing disabled
        import warnings

        warnings.warn(
            "OpenTelemetry not installed. Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp"
        )

