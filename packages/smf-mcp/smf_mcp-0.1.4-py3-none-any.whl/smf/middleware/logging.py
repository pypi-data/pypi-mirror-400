"""
Structured Logging Middleware.

Provides JSON-structured logging for MCP operations.
"""

import json
import logging
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from smf.settings import Settings


def attach_logging(mcp: FastMCP, settings: Settings) -> None:
    """
    Attach structured logging middleware to FastMCP server.

    Args:
        mcp: FastMCP server instance
        settings: SMF settings
    """
    # Configure logging
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger = logging.getLogger("smf")

    if not logger.handlers:
        handler = logging.StreamHandler()
        if settings.log_format == "json":
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
        logger.addHandler(handler)
        logger.setLevel(log_level)

    # Attach hooks if FastMCP supports them
    # Note: This is a placeholder - actual implementation depends on FastMCP API
    if hasattr(mcp, "on_call_tool"):
        original_call_tool = getattr(mcp, "on_call_tool", None)

        def log_tool_call(tool_name: str, arguments: Dict[str, Any]) -> None:
            log_data = {
                "event": "tool_call",
                "tool": tool_name,
                "arguments": arguments,
            }
            logger.info(json.dumps(log_data) if settings.log_format == "json" else str(log_data))
            if original_call_tool:
                original_call_tool(tool_name, arguments)

        mcp.on_call_tool = log_tool_call

    if hasattr(mcp, "on_read_resource"):
        original_read_resource = getattr(mcp, "on_read_resource", None)

        def log_resource_read(resource_uri: str) -> None:
            log_data = {
                "event": "resource_read",
                "resource": resource_uri,
            }
            logger.info(json.dumps(log_data) if settings.log_format == "json" else str(log_data))
            if original_read_resource:
                original_read_resource(resource_uri)

        mcp.on_read_resource = log_resource_read


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

