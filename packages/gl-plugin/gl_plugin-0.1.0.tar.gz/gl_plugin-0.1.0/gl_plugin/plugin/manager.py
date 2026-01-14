"""Plugin manager.

Authors:
    Samuel Lusandi (samuel.lusandi@gdplabs.id)

References:
    None
"""

import asyncio
import logging
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union, get_origin

from dotenv import load_dotenv

from gl_plugin.plugin.handler import PluginHandler
from gl_plugin.plugin.plugin import Plugin
from gl_plugin.plugin.registry import ServiceRegistry
from gl_plugin.services.config import ConfigService

T = TypeVar("T", bound=PluginHandler)


class HandlerNotFoundError(RuntimeError):
    """Raised when a requested plugin handler is not found."""


class PluginManager:
    """Manages plugin lifecycle and service injection.

    This manager can handle different types of plugins based on the services provided.
    Services are automatically registered based on the plugin handler interfaces provided.

    This class follows the singleton pattern - only one instance will ever exist.
    Thread-safe implementation using double-checked locking pattern.
    """

    _instance = None
    _multi_instance = {}
    _lock = Lock()
    _initialized = False
    _multi_initialized = {}  # Track initialization per key

    def __new__(
        cls,
        *,
        handlers: Optional[List[PluginHandler]] = None,
        env_file: Optional[str] = None,
        global_services: List[Any] = (),
        key_instance: Optional[str] = None,
    ) -> "PluginManager":
        """Create or return the singleton instance or multi-instance.

        Args:
            handlers: List of plugin handlers that provide injections
            env_file: Optional environment file for loading environment variables
            global_services: List of services to register globally
            key_instance: Optional key for multi-instance pattern. If None, uses singleton.

        Returns:
            The singleton PluginManager instance or specified multi-instance

        Raises:
            ValueError: If handlers is not provided during first initialization
        """
        with cls._lock:
            if key_instance is not None:
                # Multi-instance pattern
                if key_instance not in cls._multi_instance:
                    if handlers is None:
                        raise ValueError(
                            f"handlers must be provided when creating instance '{key_instance}' for the first time"
                        )
                    instance = super().__new__(cls)
                    instance._key_instance = key_instance  # Store the key for this instance
                    instance._initialized = False
                    cls._multi_instance[key_instance] = instance
                    cls._multi_initialized[key_instance] = False
                return cls._multi_instance[key_instance]
            else:
                # Singleton pattern
                if cls._instance is None:
                    if handlers is None:
                        raise ValueError("handlers must be provided when creating the first instance")
                    instance = super().__new__(cls)
                    instance._key_instance = None  # Mark as singleton
                    instance._initialized = False
                    cls._instance = instance
                return cls._instance

    def __init__(
        self,
        *,
        handlers: Optional[List[PluginHandler]] = None,
        env_file: Optional[str] = None,
        global_services: List[Any] = (),
        key_instance: Optional[str] = None,
    ):
        """Initialize plugin manager.

        This will only run once per instance (singleton or multi-instance).

        Args:
            handlers: List of plugin handlers that provide injections
            env_file: Optional environment file for loading environment variables
            global_services: List of custom services to be injected into the global registry
            key_instance: Optional key for multi-instance pattern
        """
        with self._lock:
            # Check if this specific instance is already initialized
            if key_instance is not None:
                if self._multi_initialized.get(key_instance, False):
                    return
                self._multi_initialized[key_instance] = True
            else:
                if self._initialized:
                    return
                self._initialized = True

            if not handlers:
                raise ValueError("At least one plugin handler must be provided")

            self._load_environment(env_file)

            self._handler_registries: Dict[Type[PluginHandler], ServiceRegistry] = {}
            self._plugins: Dict[str, Plugin] = {}
            self._handlers: Dict[Type[PluginHandler], PluginHandler] = {}

            for handler in handlers:
                handler_type = type(handler)
                registry = ServiceRegistry()
                registry.register(ConfigService, ConfigService())

                for service in global_services:
                    registry.register(type(service), service)

                for service_type, service_instance in handler_type.create_injections(handler).items():
                    registry.register(service_type, service_instance)

                self._handler_registries[handler_type] = registry
                self._handlers[handler_type] = handler

    def _load_environment(self, env_file: Optional[str] = None) -> None:
        """Load environment variables from .env file.

        If env_file is provided, loads from that file.
        Otherwise, searches for .env in current directory and up to 3 levels up.

        Args:
            env_file: Optional path to environment file
        """
        if env_file:
            load_dotenv(env_file)
            return

        current_dir = Path.cwd()
        env_file_path = None

        for _ in range(4):
            if (current_dir / ".env").exists():
                env_file_path = current_dir / ".env"
                break
            current_dir = current_dir.parent

        if env_file_path:
            load_dotenv(env_file_path)

    def _prepare_plugin_registration(  # noqa: PLR0912
        self, plugin_class: Type[Plugin], additional_params: Optional[Dict[str, Any]] = None
    ) -> Tuple[Any, ServiceRegistry, Type, Plugin]:
        """Prepare plugin registration by validating and setting up plugin instance.

        Args:
            plugin_class: Plugin class to register
            additional_params: Optional dictionary of keyword arguments to pass to the plugin constructor

        Returns:
            Tuple containing:
                - compatible_handler: The handler instance compatible with this plugin
                - compatible_registry: The service registry to use for this plugin
                - handler_type: The type of handler required by the plugin
                - plugin: The instantiated plugin instance

        Raises:
            ValueError: If plugin doesn't specify a handler type
            RuntimeError: If no compatible handler is found
        """
        if not plugin_class.get_handler_type():
            raise ValueError(
                f"Plugin {plugin_class.__name__} must specify a handler type using @Plugin.for_handler decorator"
            )

        # Find compatible handler (exact match or subclass)
        handler_type = plugin_class.get_handler_type()
        compatible_handler = None
        compatible_registry = None

        for registered_type, handler in self._handlers.items():
            if issubclass(type(handler), handler_type):
                compatible_handler = handler
                compatible_registry = self._handler_registries[registered_type]
                break

        if not compatible_handler:
            raise RuntimeError(
                f"Plugin {plugin_class.__name__} requires handler {handler_type.__name__} or a subclass, "
                "but none was provided"
            )

        logging.info(f"Initializing plugin {plugin_class.__name__}")

        # Validate plugin requirements before instantiation
        hints = plugin_class.__annotations__ if hasattr(plugin_class, "__annotations__") else {}

        # Check for Union types and required services against handler-specific registry
        unsupported_unions = []
        missing_services = []

        for field_name, service in hints.items():
            if isinstance(service, type) and service.__module__ == "builtins":
                continue

            # Check for both Union[] syntax and | syntax (PEP 604)
            is_union = (hasattr(service, "__origin__") and service.__origin__ is Union) or (
                hasattr(service, "__or__")
                and not isinstance(service, type)
                and any(arg is type(None) for arg in service.__args__)
            )

            if is_union:
                unsupported_unions.append(field_name)
            else:
                target_type = get_origin(service) or service

                service_found = False
                for registered_type in compatible_registry._services:
                    registered_base = get_origin(registered_type) or registered_type
                    try:
                        if isinstance(registered_base, type) and issubclass(registered_base, target_type):
                            service_found = True
                            break
                    except TypeError:
                        continue

                if not service_found:
                    missing_services.append(getattr(service, "__name__", str(service)))

        if unsupported_unions:
            logging.warning(
                f"Plugin {plugin_class.__name__} using handler {handler_type.__name__} has "
                f"Union types which are not supported for injection: {', '.join(unsupported_unions)}",
            )

        if missing_services:
            logging.warning(
                f"Plugin {plugin_class.__name__} using handler {handler_type.__name__} "
                f"could not inject the following services: {', '.join(missing_services)}",
            )

        # Set handler-specific registry and initialize plugin
        plugin_class.set_registry(compatible_registry)
        plugin = plugin_class(**additional_params) if additional_params else plugin_class()
        self._plugins[plugin.name] = plugin

        return compatible_handler, compatible_registry, handler_type, plugin

    def register_plugin(  # noqa: PLR0912
        self,
        plugin_class: Type[Plugin],
        custom_initializer: Optional[Callable[[Plugin], None]] = None,
        additional_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register and initialize a plugin.

        Args:
            plugin_class: Plugin class to register
            custom_initializer: Optional callable that will be called with the plugin instance after initialization
            additional_params: Optional dictionary of keyword arguments to pass to the plugin constructor

        Raises:
            ValueError: If plugin doesn't specify a handler type
        """
        compatible_handler, _, _, plugin = self._prepare_plugin_registration(plugin_class, additional_params)

        # Initialize plugin with its specific handler
        type(compatible_handler).initialize_plugin(compatible_handler, plugin)

        # Call custom initializer if provided
        if custom_initializer is not None:
            custom_initializer(plugin)

    async def aregister_plugin(
        self,
        plugin_class: Type[Plugin],
        custom_initializer: Optional[Callable[[Plugin], Any]] = None,
        additional_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register and initialize a plugin asynchronously.

        This is backwards compatible with the synchronous version;
        passing a synchronous plugin will be handled appropriately.

        Args:
            plugin_class: Plugin class to register
            custom_initializer: Optional callable that will be called with the plugin instance after initialization.
                               Can be either a synchronous or asynchronous function.
            additional_params: Optional dictionary of keyword arguments to pass to the plugin constructor

        Raises:
            ValueError: If plugin doesn't specify a handler type
        """
        compatible_handler, _, _, plugin = self._prepare_plugin_registration(plugin_class, additional_params)

        if asyncio.iscoroutinefunction(type(compatible_handler).ainitialize_plugin):
            await type(compatible_handler).ainitialize_plugin(compatible_handler, plugin)
        else:
            type(compatible_handler).initialize_plugin(compatible_handler, plugin)

        # Call custom initializer if provided
        if custom_initializer is not None:
            if asyncio.iscoroutinefunction(custom_initializer):
                await custom_initializer(plugin)
            else:
                custom_initializer(plugin)

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name.

        Args:
            name: Name of plugin to get

        Returns:
            Plugin instance if found, None otherwise
        """
        return self._plugins.get(name)

    def get_plugins(
        self, handler_type: Optional[Type[PluginHandler]] = None, plugin_names: Optional[List[str]] = None
    ) -> List[Plugin]:
        """Get all registered plugins, optionally filtered by handler type and names.

        Args:
            handler_type: Optional handler type to filter plugins by. If provided,
                        only returns plugins that have this handler type registered.
            plugin_names: Optional list of plugin names to filter by. If provided,
                        only returns plugins whose names are in this list.

        Returns:
            List of plugin instances
        """
        plugins = list(self._plugins.values())

        if handler_type is not None:
            plugins = [
                plugin for plugin in plugins if plugin.handler_type and issubclass(plugin.handler_type, handler_type)
            ]

        if plugin_names is not None:
            plugins = [plugin for plugin in plugins if plugin.name in plugin_names]

        return plugins

    def get_handlers(self, handler_type: Optional[Type[PluginHandler]] = None) -> List[PluginHandler]:
        """Get all registered handlers, optionally filtered by type.

        Args:
            handler_type: Optional handler type to filter by. If provided,
                        only returns handlers that are instances of this type.

        Returns:
            List of handler instances
        """
        if handler_type is None:
            return list(self._handlers.values())

        return [handler for handler in self._handlers.values() if isinstance(handler, handler_type)]

    def get_handler(self, handler_type: Type[T]) -> T:
        """Get a handler of the specified type.

        Args:
            handler_type: The type of handler to get

        Returns:
            The handler instance of the specified type

        Raises:
            HandlerNotFoundError: If no handler of the specified type is found
        """
        for handler in self._handlers.values():
            if isinstance(handler, handler_type):
                return handler  # type: ignore
        raise HandlerNotFoundError(f"No handler of type {handler_type.__name__} found")
