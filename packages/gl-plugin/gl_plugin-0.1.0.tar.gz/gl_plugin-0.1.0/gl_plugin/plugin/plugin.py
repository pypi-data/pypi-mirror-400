"""Plugin base class for the Plugin Architecture.

Authors:
    Samuel Lusandi (samuel.lusandi@gdplabs.id)

References:
    None
"""

from typing import Callable, Optional, Type

from gl_plugin.plugin.handler import PluginHandler
from gl_plugin.plugin.registry import ServiceRegistry


class Plugin:
    """Base class for BOSA Plugins."""

    name: str = None
    description: str = None
    version: str = None
    _handler_type: Optional[Type["PluginHandler"]] = None

    _registry: Optional[ServiceRegistry] = None

    def __init__(self, *args, **kwargs):
        """Initialize plugin instance.

        Raises:
            ValueError: If required class attributes are not set
        """
        super().__init__(*args, **kwargs)

        if not all([self.name, self.description, self.version]):
            raise ValueError(
                f"Plugin class {self.__class__.__name__} must set name, description, and version as class attributes"
            )

    @classmethod
    def get_handler_type(cls) -> Optional[Type["PluginHandler"]]:
        """Get the handler type for this plugin class.

        This method walks up the inheritance chain to find the handler_type.

        Returns:
            The handler type for this plugin, or None if not set
        """
        for base in cls.__mro__:
            if "_handler_type" in base.__dict__:
                return base._handler_type
        return None

    @classmethod
    def for_handler(cls, handler_type: Type["PluginHandler"]) -> Callable[[Type["Plugin"]], Type["Plugin"]]:
        """Decorator to specify which handler this plugin is designed for.

        Args:
            handler_type: The type of handler this plugin works with

        Returns:
            A decorator function that sets the handler type on the plugin class
        """

        def decorator(plugin_cls: Type["Plugin"]) -> Type["Plugin"]:
            plugin_cls._handler_type = handler_type
            return plugin_cls

        return decorator

    @classmethod
    def set_registry(cls, registry: ServiceRegistry) -> None:
        """Set the service registry for this plugin class.

        Args:
            registry: Service registry to use for dependency injection
        """
        cls._registry = registry

    @property
    def handler_type(self) -> Optional[Type["PluginHandler"]]:
        """Get the handler type for this plugin instance.

        Returns:
            The handler type for this plugin, or None if not set
        """
        return self.__class__.get_handler_type()

    def __new__(cls, *args, **kwargs):
        """Create a new plugin instance with injected services.

        This is called before __init__ and allows us to inject services
        before the instance is initialized.
        """
        instance = super().__new__(cls)

        if cls._registry is not None:
            cls._registry.inject_services(instance)

        return instance
