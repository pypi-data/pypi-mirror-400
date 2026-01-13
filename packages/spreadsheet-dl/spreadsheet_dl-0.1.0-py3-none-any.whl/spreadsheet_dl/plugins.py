"""Plugin system framework for SpreadsheetDL extensibility.

This module provides a plugin architecture allowing users to extend
SpreadsheetDL functionality with custom plugins.

New in v4.0.0:
    - PluginInterface: Abstract base class for all plugins
    - PluginHook: Event-based hook system for callbacks
    - PluginLoader: Discovery and loading of plugins from directories
    - PluginManager: Lifecycle management (register, enable, disable, list)
"""

from __future__ import annotations

import importlib.util
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class PluginInterface(ABC):
    """Abstract base class for all plugins.

    Plugins must implement this interface to be discoverable by the
    plugin system.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name (unique identifier).

        Returns:
            Unique plugin name (lowercase, no spaces)
        """
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version (semantic versioning).

        Returns:
            Version string (e.g., "1.0.0")
        """
        pass

    @property
    def description(self) -> str:
        """Plugin description.

        Returns:
            Human-readable plugin description
        """
        return ""

    @property
    def author(self) -> str:
        """Plugin author.

        Returns:
            Author name or organization
        """
        return ""

    @abstractmethod
    def initialize(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the plugin.

        Called when the plugin is enabled. Should perform any setup
        operations needed by the plugin.

        Args:
            config: Plugin configuration dictionary
        """
        pass

    def shutdown(self) -> None:  # noqa: B027
        """Cleanup when plugin is disabled/unloaded.

        Called when the plugin is disabled. Should perform cleanup
        operations and release resources.
        """
        pass


class PluginHook:
    """Plugin hook system for pre/post operation callbacks.

    Provides event-based hooks that plugins can register callbacks for.
    Supports multiple callbacks per event.
    """

    def __init__(self) -> None:
        """Initialize the hook system."""
        self._hooks: dict[str, list[Callable[..., Any]]] = {}

    def register(self, event: str, callback: Callable[..., Any]) -> None:
        """Register callback for event.

        Args:
            event: Event name to listen for
            callback: Callable to invoke when event is triggered
        """
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)

    def unregister(self, event: str, callback: Callable[..., Any]) -> None:
        """Unregister callback from event.

        Args:
            event: Event name
            callback: Callback to remove
        """
        if event in self._hooks and callback in self._hooks[event]:
            self._hooks[event].remove(callback)

    def trigger(self, event: str, *args: Any, **kwargs: Any) -> list[Any]:
        """Trigger all callbacks for an event.

        Calls all registered callbacks for the event in order of registration.
        If a callback raises an exception, it is caught and logged, but does
        not prevent other callbacks from running.

        Args:
            event: Event name to trigger
            *args: Positional arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks

        Returns:
            List of return values from all callbacks
        """
        results = []
        errors: list[tuple[str, Exception]] = []
        for callback in self._hooks.get(event, []):
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                # Intentionally broad: plugin callbacks can raise any exception
                # Collect errors but don't break other plugins
                callback_name = getattr(callback, "__name__", repr(callback))
                errors.append((callback_name, e))
        # Log collected errors after all callbacks have run
        for callback_name, error in errors:
            print(
                f"Plugin hook error for {event} in {callback_name}: {error}",
                file=sys.stderr,
            )
        return results


class PluginLoader:
    """Discovers and loads plugins from directories.

    Scans Python files in plugin directories and discovers classes
    that implement the PluginInterface.
    """

    @staticmethod
    def discover_plugins(plugin_dir: Path) -> list[type[PluginInterface]]:
        """Discover all plugins in directory.

        Scans the directory for Python files (excluding files starting with _)
        and finds classes that implement PluginInterface.

        Args:
            plugin_dir: Directory to scan for plugins

        Returns:
            List of plugin classes found
        """
        plugins: list[type[PluginInterface]] = []

        if not plugin_dir.exists():
            return plugins

        for py_file in plugin_dir.glob("*.py"):
            if py_file.stem.startswith("_"):
                continue  # Skip private modules

            try:
                # Load module
                spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[py_file.stem] = module
                    spec.loader.exec_module(module)

                    # Find plugin classes
                    for name in dir(module):
                        obj = getattr(module, name)
                        if (
                            isinstance(obj, type)
                            and issubclass(obj, PluginInterface)
                            and obj is not PluginInterface
                        ):
                            plugins.append(obj)
            except Exception as e:
                # Intentionally broad: plugin modules can have any import/execution errors
                print(f"Failed to load plugin {py_file}: {e}", file=sys.stderr)

        return plugins

    @staticmethod
    def load_plugin(
        plugin_class: type[PluginInterface], config: dict[str, Any] | None = None
    ) -> PluginInterface:
        """Instantiate and initialize a plugin.

        Creates an instance of the plugin class and calls its initialize method.

        Args:
            plugin_class: Plugin class to instantiate
            config: Plugin configuration

        Returns:
            Initialized plugin instance
        """
        plugin = plugin_class()
        plugin.initialize(config)
        return plugin


class PluginManager:
    """Manages plugin lifecycle (register, enable, disable, list).

    Central manager for plugin operations. Discovers plugins from configured
    directories, tracks enabled/disabled state, and provides access to the
    hook system.
    """

    def __init__(self, plugin_dirs: list[Path] | None = None) -> None:
        """Initialize the plugin manager.

        Args:
            plugin_dirs: List of directories to search for plugins.
                If None, uses default directories.
        """
        self._plugins: dict[str, PluginInterface] = {}
        self._enabled: set[str] = set()
        self._hooks = PluginHook()

        # Default plugin directories
        if plugin_dirs is None:
            plugin_dirs = [
                Path.home() / ".spreadsheet-dl" / "plugins",
                Path.cwd() / "plugins",
            ]
        self._plugin_dirs = plugin_dirs

    def discover(self) -> None:
        """Discover all available plugins.

        Scans plugin directories and registers discovered plugins.
        Does not enable plugins automatically.
        """
        for plugin_dir in self._plugin_dirs:
            plugin_classes = PluginLoader.discover_plugins(plugin_dir)
            for plugin_class in plugin_classes:
                plugin = plugin_class()
                self._plugins[plugin.name] = plugin

    def enable(self, name: str, config: dict[str, Any] | None = None) -> None:
        """Enable a plugin.

        Initializes and enables a previously discovered plugin.

        Args:
            name: Plugin name
            config: Plugin configuration dictionary

        Raises:
            ValueError: If plugin not found
        """
        if name not in self._plugins:
            raise ValueError(f"Plugin not found: {name}")

        if name not in self._enabled:
            plugin = self._plugins[name]
            plugin.initialize(config)
            self._enabled.add(name)

    def disable(self, name: str) -> None:
        """Disable a plugin.

        Shuts down and disables an enabled plugin.

        Args:
            name: Plugin name
        """
        if name in self._enabled:
            plugin = self._plugins[name]
            plugin.shutdown()
            self._enabled.remove(name)

    def list_plugins(self, enabled_only: bool = False) -> list[dict[str, Any]]:
        """List all plugins with metadata.

        Args:
            enabled_only: If True, only return enabled plugins

        Returns:
            List of plugin metadata dictionaries
        """
        result = []
        for name, plugin in self._plugins.items():
            if enabled_only and name not in self._enabled:
                continue
            result.append(
                {
                    "name": name,
                    "version": plugin.version,
                    "description": plugin.description,
                    "author": plugin.author,
                    "enabled": name in self._enabled,
                }
            )
        return result

    def get_plugin(self, name: str) -> PluginInterface | None:
        """Get plugin instance by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(name)

    @property
    def hooks(self) -> PluginHook:
        """Access to hook system.

        Returns:
            Plugin hook system instance
        """
        return self._hooks


# Global plugin manager instance
_plugin_manager: PluginManager | None = None


def get_plugin_manager() -> PluginManager:
    """Get or create global plugin manager.

    Provides singleton access to the plugin manager. Creates and discovers
    plugins on first call.

    Returns:
        Global PluginManager instance
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
        _plugin_manager.discover()
    return _plugin_manager
