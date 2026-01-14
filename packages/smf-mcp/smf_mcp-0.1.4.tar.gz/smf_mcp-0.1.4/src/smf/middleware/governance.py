"""
Governance middleware for SMF.
"""

import warnings
from typing import Any, Callable, Dict, List

from fastmcp import FastMCP

from smf.settings import Settings
from smf.utils.import_tools import load_callable


class GovernanceError(Exception):
    """Governance policy violation."""


def _load_handlers(config: Dict[str, Any]) -> List[Callable[[Dict[str, Any]], Any]]:
    handlers = config.get("handlers") or config.get("handler")
    if not handlers:
        raise ValueError("Governance enabled but no handler configured")
    if not isinstance(handlers, list):
        handlers = [handlers]
    loaded = []
    for handler in handlers:
        if isinstance(handler, str):
            loaded.append(load_callable(handler))
        elif callable(handler):
            loaded.append(handler)
        else:
            raise ValueError("Governance handler must be a callable or import path")
    return loaded


def _handle_violation(mode: str, message: str) -> None:
    if mode == "warn":
        warnings.warn(message)
        return
    raise GovernanceError(message)


def attach_governance(mcp: FastMCP, settings: Settings) -> None:
    if not settings.governance_enabled:
        return

    config = settings.governance_config or {}
    handlers = _load_handlers(config)
    mode = config.get("mode", "error")

    def run_handlers(event: Dict[str, Any]) -> None:
        for handler in handlers:
            result = handler(event)
            if result is False:
                _handle_violation(mode, "Governance policy rejected event")

    if hasattr(mcp, "on_call_tool"):
        original_call_tool = getattr(mcp, "on_call_tool", None)

        def govern_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Any:
            run_handlers(
                {
                    "stage": "before",
                    "action": "tool_call",
                    "name": tool_name,
                    "arguments": arguments,
                }
            )
            try:
                result = original_call_tool(tool_name, arguments) if original_call_tool else None
            except Exception as exc:
                run_handlers(
                    {
                        "stage": "error",
                        "action": "tool_call",
                        "name": tool_name,
                        "arguments": arguments,
                        "error": str(exc),
                    }
                )
                raise
            run_handlers(
                {
                    "stage": "after",
                    "action": "tool_call",
                    "name": tool_name,
                    "arguments": arguments,
                    "result": result,
                }
            )
            return result

        mcp.on_call_tool = govern_tool_call

    if hasattr(mcp, "on_read_resource"):
        original_read_resource = getattr(mcp, "on_read_resource", None)

        def govern_resource_read(resource_uri: str) -> Any:
            run_handlers(
                {
                    "stage": "before",
                    "action": "resource_read",
                    "name": resource_uri,
                }
            )
            try:
                result = original_read_resource(resource_uri) if original_read_resource else None
            except Exception as exc:
                run_handlers(
                    {
                        "stage": "error",
                        "action": "resource_read",
                        "name": resource_uri,
                        "error": str(exc),
                    }
                )
                raise
            run_handlers(
                {
                    "stage": "after",
                    "action": "resource_read",
                    "name": resource_uri,
                    "result": result,
                }
            )
            return result

        mcp.on_read_resource = govern_resource_read
