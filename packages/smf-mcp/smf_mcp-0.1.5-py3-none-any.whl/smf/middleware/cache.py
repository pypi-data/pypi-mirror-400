"""
Caching middleware for SMF.
"""

import json
from typing import Any, Dict, Optional, Set

from fastmcp import FastMCP

from smf.cache import create_cache
from smf.settings import Settings


def _serialize_args(arguments: Dict[str, Any]) -> str:
    return json.dumps(arguments, sort_keys=True, default=str)


def _build_cache_key(prefix: str, kind: str, name: str, payload: Optional[str] = None) -> str:
    if payload:
        return f"{prefix}:{kind}:{name}:{payload}"
    return f"{prefix}:{kind}:{name}"


def _should_cache(name: str, include: Set[str], exclude: Set[str]) -> bool:
    if include and name not in include:
        return False
    if name in exclude:
        return False
    return True


def attach_cache(mcp: FastMCP, settings: Settings) -> None:
    if not settings.cache_enabled:
        return

    cache = getattr(mcp, "cache", None) or create_cache(settings)
    setattr(mcp, "cache", cache)

    cache_config = settings.cache_config or {}
    key_prefix = cache_config.get("key_prefix", "smf")
    include_tools = set(cache_config.get("include_tools", []))
    exclude_tools = set(cache_config.get("exclude_tools", []))
    include_resources = set(cache_config.get("include_resources", []))
    exclude_resources = set(cache_config.get("exclude_resources", []))

    if hasattr(mcp, "on_call_tool"):
        original_call_tool = getattr(mcp, "on_call_tool", None)

        def cache_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Any:
            if _should_cache(tool_name, include_tools, exclude_tools):
                payload = _serialize_args(arguments)
                key = _build_cache_key(key_prefix, "tool", tool_name, payload)
                cached = cache.get(key)
                if cached is not None:
                    return cached

            result = original_call_tool(tool_name, arguments) if original_call_tool else None
            if _should_cache(tool_name, include_tools, exclude_tools):
                if not (isinstance(result, dict) and result.get("error")):
                    cache.set(key, result)
            return result

        mcp.on_call_tool = cache_tool_call

    if hasattr(mcp, "on_read_resource"):
        original_read_resource = getattr(mcp, "on_read_resource", None)

        def cache_resource_read(resource_uri: str) -> Any:
            if _should_cache(resource_uri, include_resources, exclude_resources):
                key = _build_cache_key(key_prefix, "resource", resource_uri)
                cached = cache.get(key)
                if cached is not None:
                    return cached

            result = original_read_resource(resource_uri) if original_read_resource else None
            if _should_cache(resource_uri, include_resources, exclude_resources):
                if not (isinstance(result, dict) and result.get("error")):
                    cache.set(key, result)
            return result

        mcp.on_read_resource = cache_resource_read
