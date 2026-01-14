"""
Component Discovery Utilities.

Provides auto-discovery of tools, resources, and prompts from modules.
"""

import importlib
import importlib.util
import inspect
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional, Callable


def discover_components(module: ModuleType) -> List[Dict[str, Any]]:
    """
    Discover MCP components in a module.

    Scans module for functions decorated with @mcp.tool, @mcp.resource, or @mcp.prompt.

    Args:
        module: Python module to scan

    Returns:
        List of discovered components with metadata
    """
    components = []

    for name, obj in inspect.getmembers(module):
        if not inspect.isfunction(obj):
            continue

        # Check if function has FastMCP decorator attributes
        # FastMCP decorators typically add metadata to the function
        if hasattr(obj, "__mcp_tool__"):
            components.append(
                {
                    "type": "tool",
                    "name": name,
                    "func": obj,
                    "metadata": getattr(obj, "__mcp_tool__", {}),
                }
            )
        elif hasattr(obj, "__mcp_resource__"):
            components.append(
                {
                    "type": "resource",
                    "name": name,
                    "func": obj,
                    "metadata": getattr(obj, "__mcp_resource__", {}),
                }
            )
        elif hasattr(obj, "__mcp_prompt__"):
            components.append(
                {
                    "type": "prompt",
                    "name": name,
                    "func": obj,
                    "metadata": getattr(obj, "__mcp_prompt__", {}),
                }
            )

    return components


def import_from_path(path: str) -> ModuleType:
    """
    Import a module from a filesystem path.

    Args:
        path: Path to Python file or directory

    Returns:
        Imported module

    Raises:
        ImportError: If module cannot be imported
    """
    path_obj = Path(path)

    if path_obj.is_file():
        # Import single file
        module_name = path_obj.stem
        spec = importlib.util.spec_from_file_location(module_name, path_obj)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot import module from {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    elif path_obj.is_dir():
        # Import package
        if not (path_obj / "__init__.py").exists():
            raise ImportError(f"Directory {path} is not a Python package")
        module_name = path_obj.name
        spec = importlib.util.spec_from_file_location(
            module_name, path_obj / "__init__.py"
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot import package from {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    else:
        raise ImportError(f"Path does not exist: {path}")


def scan_directory(directory: Path, pattern: str = "*.py") -> List[ModuleType]:
    """
    Scan directory for Python modules.

    Args:
        directory: Directory to scan
        pattern: File pattern to match

    Returns:
        List of imported modules
    """
    modules = []
    for file_path in directory.glob(pattern):
        if file_path.name == "__init__.py":
            continue
        try:
            module = import_from_path(str(file_path))
            modules.append(module)
        except Exception as e:
            import warnings

            warnings.warn(f"Failed to import {file_path}: {e}")
    return modules


def load_module(path_or_module: str) -> ModuleType:
    path_obj = Path(path_or_module)
    if path_obj.exists():
        return import_from_path(str(path_obj))
    return importlib.import_module(path_or_module)


def load_callable(path: str) -> Callable[..., Any]:
    if ":" in path:
        module_path, attr = path.split(":", 1)
    else:
        module_path, attr = path.rsplit(".", 1)

    module = load_module(module_path)
    try:
        return getattr(module, attr)
    except AttributeError as exc:
        raise AttributeError(f"Callable not found: {path}") from exc

