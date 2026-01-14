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
from smf.settings import Settings, TracingExporter, get_settings


class ServerFactory:
    """
    Factory for creating configured FastMCP servers.

    Applies default settings, attaches middleware, and configures auth.
    Uses Facade + Builder pattern to simplify server creation.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize ServerFactory.

        Args:
            settings: Optional settings instance. If None, uses global settings.
        """
        self.settings = settings or get_settings()
        self._registry = ComponentRegistry()
        self._registry.set_duplicate_policy(self.settings.duplicate_policy)

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
        # Merge settings with overrides
        fastmcp_params = self.settings.to_fastmcp_params()

        if name:
            fastmcp_params["name"] = name
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
        # Import here to avoid circular dependencies
        from smf.middleware import (
            attach_authorization,
            attach_cache,
            attach_error_handling,
            attach_governance,
            attach_logging,
            attach_rate_limiting,
            attach_tracing,
        )
        from smf.observability import attach_metrics, attach_metrics_endpoint

        # Attach middleware in order
        if self.settings.structured_logging:
            attach_logging(mcp, self.settings)

        if self.settings.tracing_enabled or self.settings.tracing_exporter != TracingExporter.NONE:
            attach_tracing(mcp, self.settings)

        if self.settings.cache_enabled:
            attach_cache(mcp, self.settings)

        # Authorization middleware (injecte aussi les claims automatiquement)
        # Doit être après le cache mais avant le rate limiting
        if self.settings.enable_authz or (self.settings.auth_provider and self.settings.auth_provider.value != "none"):
            attach_authorization(mcp, self.settings)

        if self.settings.governance_enabled:
            attach_governance(mcp, self.settings)

        if self.settings.rate_limit_enabled:
            attach_rate_limiting(mcp, self.settings)

        if self.settings.metrics_enabled:
            attach_metrics(mcp, self.settings)

        # Error handling should be last
        attach_error_handling(mcp, self.settings)

        if self.settings.metrics_enabled:
            attach_metrics_endpoint(mcp, self.settings)

    def _apply_duplicate_policy(self, mcp: FastMCP) -> None:
        def register_component(kind: str, func: Callable, name: str, description: Optional[str], tags: Optional[List[str]]) -> bool:
            if kind == "tool":
                return self._registry.register_tool(func, name=name, description=description, tags=tags)
            if kind == "resource":
                return self._registry.register_resource(func, name=name, description=description, tags=tags)
            if kind == "prompt":
                return self._registry.register_prompt(func, name=name, description=description, tags=tags)
            raise ValueError(f"Unknown component type: {kind}")

        def infer_name(kind: str, func: Callable, args: tuple, kwargs: dict) -> str:
            if kind == "resource":
                name = kwargs.get("name")
                if name is None and args and isinstance(args[0], str):
                    name = args[0]
                return name or func.__name__
            return kwargs.get("name") or func.__name__

        def wrap(original: Callable, kind: str) -> Callable:
            def decorator(*args: Any, **kwargs: Any) -> Any:
                if args and callable(args[0]):
                    func = args[0]
                    name = infer_name(kind, func, (), kwargs)
                    registered = register_component(
                        kind,
                        func,
                        name,
                        kwargs.get("description"),
                        kwargs.get("tags"),
                    )
                    if not registered:
                        return func
                    return original(func, **kwargs)

                def inner(func: Callable) -> Any:
                    name = infer_name(kind, func, args, kwargs)
                    registered = register_component(
                        kind,
                        func,
                        name,
                        kwargs.get("description"),
                        kwargs.get("tags"),
                    )
                    if not registered:
                        return func
                    decorated = original(*args, **kwargs)
                    return decorated(func)

                return inner

            return decorator

        mcp.tool = wrap(mcp.tool, "tool")
        mcp.resource = wrap(mcp.resource, "resource")
        mcp.prompt = wrap(mcp.prompt, "prompt")

    def _initialize_services(self, mcp: FastMCP) -> None:
        from smf.cache import create_cache
        from smf.storage import create_storage

        setattr(mcp, "storage", create_storage(self.settings))
        if self.settings.cache_enabled:
            setattr(mcp, "cache", create_cache(self.settings))

    def _load_plugins(self, mcp: FastMCP) -> None:
        if not self.settings.plugin_paths:
            return

        from smf.utils.import_tools import load_module

        base_dir = getattr(self.settings, "_smf_base_dir", Path.cwd())

        for entry in self.settings.plugin_paths:
            path_obj = Path(entry)
            if not path_obj.is_absolute():
                path_obj = base_dir / path_obj
            module = load_module(str(path_obj) if path_obj.exists() else entry)
            if hasattr(module, "register"):
                module.register(mcp)
            elif hasattr(module, "setup"):
                module.setup(mcp)

    def _auto_discover(self, mcp: FastMCP) -> None:
        if not self.settings.auto_discover or not self.settings.discovery_paths:
            return

        from smf.utils.import_tools import discover_components, import_from_path, load_module, scan_directory

        base_dir = getattr(self.settings, "_smf_base_dir", Path.cwd())

        for entry in self.settings.discovery_paths:
            path_obj = Path(entry)
            if not path_obj.is_absolute():
                path_obj = base_dir / path_obj
            modules = []
            if path_obj.exists():
                if path_obj.is_dir():
                    modules.extend(scan_directory(path_obj))
                else:
                    modules.append(import_from_path(str(path_obj)))
            else:
                modules.append(load_module(entry))

            for module in modules:
                if hasattr(module, "register"):
                    module.register(mcp)
                    continue
                if hasattr(module, "setup"):
                    module.setup(mcp)
                    continue
                components = discover_components(module)
                for component in components:
                    metadata = component.get("metadata", {})
                    if component["type"] == "tool":
                        mcp.tool(component["func"], **metadata)
                    elif component["type"] == "resource":
                        mcp.resource(component["func"], **metadata)
                    elif component["type"] == "prompt":
                        mcp.prompt(component["func"], **metadata)

    @property
    def registry(self) -> ComponentRegistry:
        """Get component registry."""
        return self._registry


class AppBuilder:
    """
    Fluent builder for registering tools, resources, and prompts.

    Uses Decorator + Fluent Builder pattern to register components
    before applying them to the server.
    """

    def __init__(
        self,
        server: Optional[FastMCP] = None,
        registry: Optional[ComponentRegistry] = None,
        settings: Optional[Settings] = None,
    ):
        """
        Initialize AppBuilder.

        Args:
            server: FastMCP server instance (created if None)
            registry: Component registry (created if None)
            settings: Settings instance (uses global if None)
        """
        self.settings = settings or get_settings()
        self._registry = registry or ComponentRegistry()
        self._registry.set_duplicate_policy(self.settings.duplicate_policy)
        self._server = server

    @property
    def server(self) -> FastMCP:
        """Get or create FastMCP server."""
        if self._server is None:
            factory = ServerFactory(self.settings)
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

    def resource(
        self,
        func: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Union[Callable, "AppBuilder"]:
        """
        Register a resource.

        Args:
            func: Function to register
            name: Resource name (defaults to function name)
            description: Resource description (defaults to docstring)
            tags: Tags for the resource

        Returns:
            Decorated function or builder instance
        """
        if func is None:
            return lambda f: self.resource(
                f, name=name, description=description, tags=tags
            )

        self._registry.register_resource(
            func, name=name, description=description, tags=tags
        )

        decorated = self.server.resource(func)
        return decorated

    def prompt(
        self,
        func: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Union[Callable, "AppBuilder"]:
        """
        Register a prompt.

        Args:
            func: Function to register
            name: Prompt name (defaults to function name)
            description: Prompt description (defaults to docstring)
            tags: Tags for the prompt

        Returns:
            Decorated function or builder instance
        """
        if func is None:
            return lambda f: self.prompt(
                f, name=name, description=description, tags=tags
            )

        self._registry.register_prompt(
            func, name=name, description=description, tags=tags
        )

        decorated = self.server.prompt(func)
        return decorated

    def register_module(self, module: Any) -> "AppBuilder":
        """
        Register all components from a module.

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
            elif component["type"] == "resource":
                self.resource(component["func"], **component.get("metadata", {}))
            elif component["type"] == "prompt":
                self.prompt(component["func"], **component.get("metadata", {}))

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
    settings: Optional[Settings] = None,
    **kwargs: Any,
) -> FastMCP:
    """
    Create a configured SMF server quickly.

    Args:
        name: Server name
        settings: Optional settings instance
        **kwargs: Additional FastMCP parameters

    Returns:
        Configured FastMCP instance

    Example:
        >>> mcp = create_server("My Server")
        >>> @mcp.tool
        >>> def greet(name: str) -> str:
        ...     return f"Hello, {name}!"
    """
    factory = ServerFactory(settings)
    return factory.create(name=name, **kwargs)

