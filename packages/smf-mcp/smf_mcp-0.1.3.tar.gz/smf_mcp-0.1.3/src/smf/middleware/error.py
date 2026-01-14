"""
Error Handling Middleware.

Normalizes exceptions to MCP error format.
"""

import logging
import traceback
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from smf.settings import Settings

logger = logging.getLogger("smf")


class SMFError(Exception):
    """Base exception for SMF errors."""

    def __init__(self, message: str, code: Optional[str] = None):
        """
        Initialize SMF error.

        Args:
            message: Error message
            code: Error code
        """
        super().__init__(message)
        self.message = message
        self.code = code or "SMF_ERROR"


class ToolError(SMFError):
    """Error during tool execution."""

    def __init__(self, message: str, tool_name: Optional[str] = None):
        """
        Initialize tool error.

        Args:
            message: Error message
            tool_name: Name of the tool that failed
        """
        super().__init__(message, code="TOOL_ERROR")
        self.tool_name = tool_name


class ResourceError(SMFError):
    """Error during resource access."""

    def __init__(self, message: str, resource_uri: Optional[str] = None):
        """
        Initialize resource error.

        Args:
            message: Error message
            resource_uri: URI of the resource that failed
        """
        super().__init__(message, code="RESOURCE_ERROR")
        self.resource_uri = resource_uri


def attach_error_handling(mcp: FastMCP, settings: Settings) -> None:
    """
    Attach error handling middleware to FastMCP server.

    Args:
        mcp: FastMCP server instance
        settings: SMF settings
    """
    # Attach error handlers
    # Note: This is a placeholder - actual implementation depends on FastMCP API
    if hasattr(mcp, "on_call_tool"):
        original_call_tool = getattr(mcp, "on_call_tool", None)

        def handle_tool_errors(tool_name: str, arguments: Dict[str, Any]) -> Any:
            try:
                if original_call_tool:
                    return original_call_tool(tool_name, arguments)
            except Exception as e:
                return _handle_error(e, tool_name=tool_name, settings=settings)

        mcp.on_call_tool = handle_tool_errors

    if hasattr(mcp, "on_read_resource"):
        original_read_resource = getattr(mcp, "on_read_resource", None)

        def handle_resource_errors(resource_uri: str) -> Any:
            try:
                if original_read_resource:
                    return original_read_resource(resource_uri)
            except Exception as e:
                return _handle_error(e, resource_uri=resource_uri, settings=settings)

        mcp.on_read_resource = handle_resource_errors


def _handle_error(
    error: Exception,
    settings: Settings,
    tool_name: Optional[str] = None,
    resource_uri: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Handle and normalize error.

    Args:
        error: Exception that occurred
        settings: SMF settings
        tool_name: Optional tool name
        resource_uri: Optional resource URI

    Returns:
        Normalized error response
    """
    # Log error
    logger.error(
        f"Error in {'tool' if tool_name else 'resource'}: {error}",
        exc_info=True,
    )

    # Determine error type
    if isinstance(error, SMFError):
        error_code = error.code
        error_message = error.message
    elif isinstance(error, ValueError):
        error_code = "VALIDATION_ERROR"
        error_message = str(error)
    elif isinstance(error, KeyError):
        error_code = "MISSING_PARAMETER"
        error_message = f"Missing parameter: {error}"
    else:
        error_code = "INTERNAL_ERROR"
        error_message = (
            str(error) if not settings.mask_error_details else "An internal error occurred"
        )

    # Build error response
    response: Dict[str, Any] = {
        "error": True,
        "code": error_code,
        "message": error_message,
    }

    # Add details if not masked
    if not settings.mask_error_details:
        response["details"] = {
            "type": type(error).__name__,
            "traceback": traceback.format_exc(),
        }
        if tool_name:
            response["details"]["tool"] = tool_name
        if resource_uri:
            response["details"]["resource"] = resource_uri

    return response

