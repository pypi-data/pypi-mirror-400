"""
SMF Core - High-level abstractions for building MCP servers.

This module provides:
- ServerFactory: Creates configured FastMCP servers
- AppBuilder: Fluent interface for registering components
- ComponentRegistry: Tracks registered components
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

from fastmcp import FastMCP

from smf.registry import ComponentRegistry


class ServerFactory:
    """
    Factory for creating configured FastMCP servers.

    Uses Facade + Builder pattern to simplify server creation.
    """

    def __init__(self, duplicate_policy: str = "error"):
        """
        Initialize ServerFactory.

        Args:
            duplicate_policy: Policy for duplicate registrations (default: "error")
        """
        self._registry = ComponentRegistry()
        self._registry.set_duplicate_policy(duplicate_policy)

    def create(
        self,
        name: Optional[str] = None,
        instructions: Optional[str] = None,
        version: Optional[str] = None,
        **kwargs: Any,
    ) -> FastMCP:
        """
        Create a configured FastMCP server.

        Args:
            name: Server name (overrides settings)
            instructions: Server instructions (overrides settings)
            version: Server version (overrides settings)
            **kwargs: Additional FastMCP parameters

        Returns:
            Configured FastMCP instance
        """
        # Build FastMCP parameters
        fastmcp_params: Dict[str, Any] = {
            "name": name or "SMF Server",
            "strict_input_validation": kwargs.pop("strict_input_validation", True),
            "include_fastmcp_meta": kwargs.pop("include_fastmcp_meta", False),
            "mask_error_details": kwargs.pop("mask_error_details", True),
        }

        if instructions:
            fastmcp_params["instructions"] = instructions
        if version:
            fastmcp_params["version"] = version

        # Apply user overrides
        fastmcp_params.update(kwargs)

        # Create FastMCP instance
        mcp = FastMCP(**fastmcp_params)

        self._apply_duplicate_policy(mcp)
        self._initialize_services(mcp)
        self._load_plugins(mcp)
        self._auto_discover(mcp)

        # Attach middleware (will be implemented in middleware module)
        self._attach_middleware(mcp)

        return mcp

    def _attach_middleware(self, mcp: FastMCP) -> None:
        """Attach middleware to FastMCP instance."""
        # Middleware functionality has been simplified/removed
        # This method is kept for future extensibility
        # If middleware modules are re-added, they can be attached here
        pass

    def _apply_duplicate_policy(self, mcp: FastMCP) -> None:
        def wrap(original: Callable) -> Callable:
            def decorator(*args: Any, **kwargs: Any) -> Any:
                if args and callable(args[0]):
                    func = args[0]
                    name = kwargs.get("name") or func.__name__
                    registered = self._registry.register_tool(
                        func,
                        name=name,
                        description=kwargs.get("description"),
                        tags=kwargs.get("tags"),
                    )
                    if not registered:
                        return func
                    return original(func, **kwargs)

                def inner(func: Callable) -> Any:
                    name = kwargs.get("name") or func.__name__
                    registered = self._registry.register_tool(
                        func,
                        name=name,
                        description=kwargs.get("description"),
                        tags=kwargs.get("tags"),
                    )
                    if not registered:
                        return func
                    decorated = original(*args, **kwargs)
                    return decorated(func)

                return inner

            return decorator

        mcp.tool = wrap(mcp.tool)

    def _initialize_services(self, mcp: FastMCP) -> None:
        # Services initialization can be added here if needed
        pass

    def _load_plugins(self, mcp: FastMCP) -> None:
        # Plugin loading can be added here if needed
        pass

    def _auto_discover(self, mcp: FastMCP) -> None:
        # Auto-discovery can be added here if needed
        pass

    @property
    def registry(self) -> ComponentRegistry:
        """Get component registry."""
        return self._registry


class AppBuilder:
    """
    Fluent builder for registering tools.

    Uses Decorator + Fluent Builder pattern to register components
    before applying them to the server.
    """

    def __init__(
        self,
        server: Optional[FastMCP] = None,
        registry: Optional[ComponentRegistry] = None,
        duplicate_policy: str = "error",
    ):
        """
        Initialize AppBuilder.

        Args:
            server: FastMCP server instance (created if None)
            registry: Component registry (created if None)
            duplicate_policy: Policy for duplicate registrations (default: "error")
        """
        self._registry = registry or ComponentRegistry()
        self._registry.set_duplicate_policy(duplicate_policy)
        self._server = server

    @property
    def server(self) -> FastMCP:
        """Get or create FastMCP server."""
        if self._server is None:
            factory = ServerFactory()
            self._server = factory.create()
        return self._server

    def tool(
        self,
        func: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Union[Callable, "AppBuilder"]:
        """
        Register a tool.

        Can be used as decorator or method:
        - @builder.tool
        - builder.tool(my_function)
        - builder.tool(name="my_tool")(my_function)

        Args:
            func: Function to register
            name: Tool name (defaults to function name)
            description: Tool description (defaults to docstring)
            tags: Tags for the tool

        Returns:
            Decorated function or builder instance
        """
        if func is None:
            # Used as decorator with arguments: @builder.tool(name="...")
            return lambda f: self.tool(f, name=name, description=description, tags=tags)

        # Register in registry
        self._registry.register_tool(
            func, name=name, description=description, tags=tags
        )

        # Apply to FastMCP server
        decorated = self.server.tool(func)
        return decorated

    def register_module(self, module: Any) -> "AppBuilder":
        """
        Register all tools from a module.

        Scans module for decorated functions and registers them.

        Args:
            module: Python module to scan

        Returns:
            Self for method chaining
        """
        from smf.utils.import_tools import discover_components

        components = discover_components(module)
        for component in components:
            if component["type"] == "tool":
                self.tool(component["func"], **component.get("metadata", {}))

        return self

    def register_from_path(self, path: str) -> "AppBuilder":
        """
        Register components from a filesystem path.

        Args:
            path: Path to scan for components

        Returns:
            Self for method chaining
        """
        from smf.utils.import_tools import import_from_path

        module = import_from_path(path)
        return self.register_module(module)

    def build(self) -> FastMCP:
        """
        Build and return the configured server.

        Returns:
            Configured FastMCP instance
        """
        return self.server

    def __enter__(self) -> "AppBuilder":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        pass


# Convenience function for quick server creation
def create_server(
    name: Optional[str] = None,
    **kwargs: Any,
) -> FastMCP:
    """
    Create a configured SMF server quickly.

    Args:
        name: Server name
        **kwargs: Additional FastMCP parameters

    Returns:
        Configured FastMCP instance

    Example:
        >>> mcp = create_server("My Server")
        >>> @mcp.tool
        >>> def greet(name: str) -> str:
        ...     return f"Hello, {name}!"
    """
    factory = ServerFactory()
    return factory.create(name=name, **kwargs)

