"""
Component Registry - Tracks registered tools, resources, and prompts.

Provides a catalog of components with metadata, filtering, and discovery.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set


@dataclass
class ComponentMetadata:
    """Metadata for a registered component."""

    name: str
    func: Callable
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    schema: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None


class ComponentRegistry:
    """
    Registry for MCP components (tools, resources, prompts).

    Provides Plugin Architecture pattern for component discovery and management.
    """

    def __init__(self):
        """Initialize component registry."""
        self._tools: Dict[str, ComponentMetadata] = {}
        self._resources: Dict[str, ComponentMetadata] = {}
        self._prompts: Dict[str, ComponentMetadata] = {}
        self._duplicate_policy: str = "error"

    def register_tool(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        schema: Optional[Dict[str, Any]] = None,
        security: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Register a tool.

        Args:
            func: Tool function
            name: Tool name (defaults to function name)
            description: Tool description (defaults to docstring)
            tags: Tags for filtering
            schema: JSON schema (auto-generated if None)
            security: Security metadata

        Raises:
            ValueError: If duplicate name and policy is "error"
        """
        name = name or func.__name__
        description = description or func.__doc__

        if name in self._tools:
            if self._duplicate_policy == "error":
                raise ValueError(f"Tool '{name}' already registered")
            elif self._duplicate_policy == "warn":
                import warnings

                warnings.warn(f"Tool '{name}' already registered, overwriting")
            elif self._duplicate_policy == "ignore":
                return False
            # "ignore" policy: silently overwrite

        metadata = ComponentMetadata(
            name=name,
            func=func,
            description=description,
            tags=tags or [],
            schema=schema,
            security=security,
        )

        self._tools[name] = metadata
        return True

    def register_resource(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        schema: Optional[Dict[str, Any]] = None,
        security: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Register a resource."""
        name = name or func.__name__
        description = description or func.__doc__

        if name in self._resources:
            if self._duplicate_policy == "error":
                raise ValueError(f"Resource '{name}' already registered")
            elif self._duplicate_policy == "warn":
                import warnings

                warnings.warn(f"Resource '{name}' already registered, overwriting")
            elif self._duplicate_policy == "ignore":
                return False

        metadata = ComponentMetadata(
            name=name,
            func=func,
            description=description,
            tags=tags or [],
            schema=schema,
            security=security,
        )

        self._resources[name] = metadata
        return True

    def register_prompt(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        schema: Optional[Dict[str, Any]] = None,
        security: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Register a prompt."""
        name = name or func.__name__
        description = description or func.__doc__

        if name in self._prompts:
            if self._duplicate_policy == "error":
                raise ValueError(f"Prompt '{name}' already registered")
            elif self._duplicate_policy == "warn":
                import warnings

                warnings.warn(f"Prompt '{name}' already registered, overwriting")
            elif self._duplicate_policy == "ignore":
                return False

        metadata = ComponentMetadata(
            name=name,
            func=func,
            description=description,
            tags=tags or [],
            schema=schema,
            security=security,
        )

        self._prompts[name] = metadata
        return True

    def get_tool(self, name: str) -> Optional[ComponentMetadata]:
        """Get tool metadata by name."""
        return self._tools.get(name)

    def get_resource(self, name: str) -> Optional[ComponentMetadata]:
        """Get resource metadata by name."""
        return self._resources.get(name)

    def get_prompt(self, name: str) -> Optional[ComponentMetadata]:
        """Get prompt metadata by name."""
        return self._prompts.get(name)

    def list_tools(
        self, include_tags: Optional[List[str]] = None, exclude_tags: Optional[List[str]] = None
    ) -> List[ComponentMetadata]:
        """
        List tools with optional tag filtering.

        Args:
            include_tags: Only include tools with these tags
            exclude_tags: Exclude tools with these tags

        Returns:
            List of tool metadata
        """
        return self._filter_components(
            list(self._tools.values()), include_tags, exclude_tags
        )

    def list_resources(
        self, include_tags: Optional[List[str]] = None, exclude_tags: Optional[List[str]] = None
    ) -> List[ComponentMetadata]:
        """List resources with optional tag filtering."""
        return self._filter_components(
            list(self._resources.values()), include_tags, exclude_tags
        )

    def list_prompts(
        self, include_tags: Optional[List[str]] = None, exclude_tags: Optional[List[str]] = None
    ) -> List[ComponentMetadata]:
        """List prompts with optional tag filtering."""
        return self._filter_components(
            list(self._prompts.values()), include_tags, exclude_tags
        )

    def _filter_components(
        self,
        components: List[ComponentMetadata],
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
    ) -> List[ComponentMetadata]:
        """Filter components by tags."""
        if not include_tags and not exclude_tags:
            return components

        filtered = []
        for component in components:
            component_tags = set(component.tags)

            # Include filter
            if include_tags:
                include_set = set(include_tags)
                if not component_tags.intersection(include_set):
                    continue

            # Exclude filter
            if exclude_tags:
                exclude_set = set(exclude_tags)
                if component_tags.intersection(exclude_set):
                    continue

            filtered.append(component)

        return filtered

    def set_duplicate_policy(self, policy: str) -> None:
        """
        Set duplicate registration policy.

        Args:
            policy: One of "error", "warn", "ignore"
        """
        if policy not in ("error", "warn", "ignore"):
            raise ValueError(f"Invalid duplicate policy: {policy}")
        self._duplicate_policy = policy

    def clear(self) -> None:
        """Clear all registered components."""
        self._tools.clear()
        self._resources.clear()
        self._prompts.clear()

    def get_stats(self) -> Dict[str, int]:
        """Get registry statistics."""
        return {
            "tools": len(self._tools),
            "resources": len(self._resources),
            "prompts": len(self._prompts),
        }

