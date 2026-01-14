"""
Dependency Injection Container.

Provides IoC (Inversion of Control) for service dependencies.
"""

from typing import Any, Callable, Dict, Optional, Type, TypeVar

T = TypeVar("T")


class ServiceContainer:
    """
    Simple dependency injection container.

    Provides IoC pattern for managing service dependencies.
    """

    def __init__(self):
        """Initialize service container."""
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
        self._singletons: Dict[Type, Any] = {}

    def register(
        self,
        service_type: Type[T],
        instance: Optional[T] = None,
        factory: Optional[Callable[[], T]] = None,
        singleton: bool = True,
    ) -> None:
        """
        Register a service.

        Args:
            service_type: Type of the service
            instance: Optional instance to register
            factory: Optional factory function
            singleton: Whether to treat as singleton

        Raises:
            ValueError: If neither instance nor factory provided
        """
        if instance is not None:
            self._services[service_type] = instance
        elif factory is not None:
            if singleton:
                self._factories[service_type] = factory
            else:
                # For non-singletons, store factory but create new instance each time
                self._factories[service_type] = factory
        else:
            raise ValueError("Either instance or factory must be provided")

    def get(self, service_type: Type[T]) -> T:
        """
        Get a service instance.

        Args:
            service_type: Type of service to retrieve

        Returns:
            Service instance

        Raises:
            KeyError: If service not registered
        """
        # Check for direct instance
        if service_type in self._services:
            return self._services[service_type]

        # Check for singleton cache
        if service_type in self._singletons:
            return self._singletons[service_type]

        # Check for factory
        if service_type in self._factories:
            instance = self._factories[service_type]()
            # Cache singleton if applicable
            # (For simplicity, we assume factories create singletons)
            self._singletons[service_type] = instance
            return instance

        raise KeyError(f"Service {service_type} not registered")

    def has(self, service_type: Type) -> bool:
        """
        Check if service is registered.

        Args:
            service_type: Type to check

        Returns:
            True if registered
        """
        return (
            service_type in self._services
            or service_type in self._factories
            or service_type in self._singletons
        )

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """Get or create global service container."""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def set_container(container: ServiceContainer) -> None:
    """Set global service container."""
    global _container
    _container = container

