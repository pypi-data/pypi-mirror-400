"""Service registry for core services that can be injected into plugins.

Authors:
    Samuel Lusandi (samuel.lusandi@gdplabs.id)

References:
    None
"""

from typing import Any, Dict, Type, TypeVar, get_origin, get_type_hints

T = TypeVar("T")


class ServiceRegistry:
    """Registry for core services that can be injected into plugins."""

    def __init__(self):
        """Initialize an empty service registry."""
        self._services: Dict[Type, Any] = {}

    def register(self, service_type: Type[T], instance: T) -> None:
        """Register a service instance for a given type.

        Args:
            service_type: The type of the service (usually its class)
            instance: The service instance
        """
        self._services[service_type] = instance

    def get(self, service_type: Type[T]) -> T:
        """Get a service instance by its type.

        Args:
            service_type: The type of service to retrieve

        Returns:
            The service instance

        Raises:
            TypeError: If the service type is a built-in type
            KeyError: If the service type is not registered
        """
        if isinstance(service_type, type) and service_type.__module__ == "builtins":
            raise TypeError(
                f"Built-in type {service_type.__name__} cannot be injected. Pass this value directly instead."
            )

        if service_type not in self._services:
            raise KeyError(f"Service {getattr(service_type, '__name__', str(service_type))} not registered")
        return self._services[service_type]

    def inject_services(self, target: Any) -> None:
        """Inject registered services into an object based on its type hints.

        This will look for class-level type hints and inject matching services.
        If a service is registered that is a subclass of the requested type,
        it will be injected. Handles both regular and generic types.

        Args:
            target: The object to inject services into
        """
        hints = get_type_hints(target.__class__)

        for attr_name, attr_type in hints.items():
            # First try exact type match
            service = self._services.get(attr_type)

            # If no exact match, look for a subclass that implements the interface
            if service is None:
                target_type = get_origin(attr_type) or attr_type

                for registered_type, registered_service in self._services.items():
                    registered_base = get_origin(registered_type) or registered_type
                    try:
                        if isinstance(registered_base, type) and issubclass(registered_base, target_type):
                            service = registered_service
                            break
                    except TypeError:
                        # Skip if type checking fails (e.g. with complex generic types)
                        continue

            if service is not None:
                # This is created in order to accommodate services that are to be injected
                # as a new object. Usually, services are to be injected as a singleton or
                # as a class method. However, some services are to be injected as a new
                # object so their behavior is not shared. An example is the Router;
                # each Plugin *must* have its own Router otherwise, a shared route can
                # cause a conflict with another plugin.
                if callable(service) and not isinstance(service, type):
                    service = service()
                setattr(target, attr_name, service)
