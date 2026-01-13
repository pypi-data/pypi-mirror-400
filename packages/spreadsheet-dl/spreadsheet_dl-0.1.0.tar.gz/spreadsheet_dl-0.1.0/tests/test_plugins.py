"""
Tests for plugin system framework.

Tests:
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import pytest

from spreadsheet_dl.plugins import (
    PluginHook,
    PluginInterface,
    PluginLoader,
    PluginManager,
    get_plugin_manager,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain]


# Test plugin implementations
class SamplePluginBasic(PluginInterface):
    """Basic test plugin."""

    def __init__(self) -> None:
        self.initialized = False
        self.shutdown_called = False
        self.config_received: dict[str, Any] | None = None

    @property
    def name(self) -> str:
        return "test_basic"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Basic test plugin"

    @property
    def author(self) -> str:
        return "Test Author"

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        self.initialized = True
        self.config_received = config

    def shutdown(self) -> None:
        self.shutdown_called = True


class SamplePluginMinimal(PluginInterface):
    """Minimal test plugin with only required methods."""

    @property
    def name(self) -> str:
        return "test_minimal"

    @property
    def version(self) -> str:
        return "0.1.0"

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        pass


class TestPluginInterface:
    """Tests for PluginInterface abstract base class."""

    def test_cannot_instantiate_abstract_class(self) -> None:
        """Test that PluginInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            PluginInterface()  # type: ignore

    def test_plugin_with_all_properties(self) -> None:
        """Test plugin with all properties implemented."""
        plugin = SamplePluginBasic()
        assert plugin.name == "test_basic"
        assert plugin.version == "1.0.0"
        assert plugin.description == "Basic test plugin"
        assert plugin.author == "Test Author"

    def test_plugin_with_minimal_implementation(self) -> None:
        """Test plugin with only required methods."""
        plugin = SamplePluginMinimal()
        assert plugin.name == "test_minimal"
        assert plugin.version == "0.1.0"
        assert plugin.description == ""  # Default empty string
        assert plugin.author == ""  # Default empty string

    def test_plugin_initialization(self) -> None:
        """Test plugin initialization without config."""
        plugin = SamplePluginBasic()
        assert not plugin.initialized

        plugin.initialize()
        assert plugin.initialized
        assert plugin.config_received is None

    def test_plugin_initialization_with_config(self) -> None:
        """Test plugin initialization with config."""
        plugin = SamplePluginBasic()
        config = {"key": "value", "setting": 123}

        plugin.initialize(config)
        assert plugin.initialized
        assert plugin.config_received == config

    def test_plugin_shutdown(self) -> None:
        """Test plugin shutdown."""
        plugin = SamplePluginBasic()
        assert not plugin.shutdown_called

        plugin.shutdown()
        assert plugin.shutdown_called

    def test_plugin_lifecycle(self) -> None:
        """Test full plugin lifecycle."""
        plugin = SamplePluginBasic()

        # Initialize
        plugin.initialize({"test": True})
        assert plugin.initialized
        assert plugin.config_received == {"test": True}

        # Shutdown
        plugin.shutdown()
        assert plugin.shutdown_called


class TestPluginHook:
    """Tests for PluginHook event system."""

    def test_create_hook_system(self) -> None:
        """Test creating hook system."""
        hooks = PluginHook()
        assert hooks._hooks == {}

    def test_register_callback(self) -> None:
        """Test registering a callback."""
        hooks = PluginHook()
        callback_called = []

        def callback() -> None:
            callback_called.append(True)

        hooks.register("test_event", callback)
        assert "test_event" in hooks._hooks
        assert callback in hooks._hooks["test_event"]

    def test_register_multiple_callbacks(self) -> None:
        """Test registering multiple callbacks for same event."""
        hooks = PluginHook()

        def callback1() -> None:
            pass

        def callback2() -> None:
            pass

        hooks.register("event", callback1)
        hooks.register("event", callback2)

        assert len(hooks._hooks["event"]) == 2
        assert callback1 in hooks._hooks["event"]
        assert callback2 in hooks._hooks["event"]

    def test_unregister_callback(self) -> None:
        """Test unregistering a callback."""
        hooks = PluginHook()

        def callback() -> None:
            pass

        hooks.register("event", callback)
        assert callback in hooks._hooks["event"]

        hooks.unregister("event", callback)
        assert callback not in hooks._hooks["event"]

    def test_unregister_nonexistent_callback(self) -> None:
        """Test unregistering a callback that wasn't registered."""
        hooks = PluginHook()

        def callback() -> None:
            pass

        # Should not raise an error
        hooks.unregister("event", callback)

    def test_trigger_callback(self) -> None:
        """Test triggering a callback."""
        hooks = PluginHook()
        results = []

        def callback(value: str) -> str:
            results.append(value)
            return f"processed_{value}"

        hooks.register("event", callback)
        returned = hooks.trigger("event", "test")

        assert results == ["test"]
        assert returned == ["processed_test"]

    def test_trigger_multiple_callbacks(self) -> None:
        """Test triggering multiple callbacks."""
        hooks = PluginHook()
        results = []

        def callback1(value: int) -> int:
            results.append(value)
            return value * 2

        def callback2(value: int) -> int:
            results.append(value)
            return value * 3

        hooks.register("event", callback1)
        hooks.register("event", callback2)
        returned = hooks.trigger("event", 5)

        assert results == [5, 5]
        assert returned == [10, 15]

    def test_trigger_with_args_and_kwargs(self) -> None:
        """Test triggering callbacks with args and kwargs."""
        hooks = PluginHook()
        captured = []

        def callback(a: int, b: int, c: int = 0) -> int:
            captured.append((a, b, c))
            return a + b + c

        hooks.register("event", callback)
        result = hooks.trigger("event", 1, 2, c=3)

        assert captured == [(1, 2, 3)]
        assert result == [6]

    def test_trigger_nonexistent_event(self) -> None:
        """Test triggering an event with no callbacks."""
        hooks = PluginHook()
        result = hooks.trigger("nonexistent")
        assert result == []

    def test_trigger_with_exception(self) -> None:
        """Test that exceptions in callbacks don't break other callbacks."""
        hooks = PluginHook()
        results = []

        def callback1() -> None:
            results.append(1)
            raise ValueError("Test error")

        def callback2() -> None:
            results.append(2)

        hooks.register("event", callback1)
        hooks.register("event", callback2)

        # Should not raise, but print error
        returned = hooks.trigger("event")

        # Both callbacks should run despite error in first
        assert results == [1, 2]
        assert len(returned) == 1  # Only callback2 returned a value


class TestPluginLoader:
    """Tests for PluginLoader discovery and loading."""

    def test_discover_plugins_nonexistent_directory(self) -> None:
        """Test discovering plugins in non-existent directory."""
        plugins = PluginLoader.discover_plugins(Path("/nonexistent"))
        assert plugins == []

    def test_discover_plugins_empty_directory(self) -> None:
        """Test discovering plugins in empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugins = PluginLoader.discover_plugins(Path(tmpdir))
            assert plugins == []

    def test_discover_plugins_with_plugin_file(self) -> None:
        """Test discovering plugins from directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir)

            # Create a plugin file
            plugin_file = plugin_dir / "my_plugin.py"
            plugin_file.write_text(
                """
from spreadsheet_dl.plugins import PluginInterface

class MyPlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "my_plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self, config=None):
        pass
"""
            )

            plugins = PluginLoader.discover_plugins(plugin_dir)
            assert len(plugins) == 1
            assert plugins[0].__name__ == "MyPlugin"

    def test_discover_plugins_skips_private_files(self) -> None:
        """Test that discovery skips files starting with underscore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir)

            # Create private file
            private_file = plugin_dir / "_private.py"
            private_file.write_text(
                """
from spreadsheet_dl.plugins import PluginInterface

class PrivatePlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "private"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self, config=None):
        pass
"""
            )

            plugins = PluginLoader.discover_plugins(plugin_dir)
            assert len(plugins) == 0

    def test_load_plugin(self) -> None:
        """Test loading and initializing a plugin."""
        plugin = PluginLoader.load_plugin(SamplePluginBasic)
        assert isinstance(plugin, SamplePluginBasic)
        assert plugin.initialized

    def test_load_plugin_with_config(self) -> None:
        """Test loading plugin with configuration."""
        config = {"key": "value"}
        plugin = PluginLoader.load_plugin(SamplePluginBasic, config)
        assert isinstance(plugin, SamplePluginBasic)
        assert plugin.initialized
        assert plugin.config_received == config


class TestPluginManager:
    """Tests for PluginManager lifecycle management."""

    def test_create_manager(self) -> None:
        """Test creating plugin manager."""
        manager = PluginManager(plugin_dirs=[])
        assert manager._plugins == {}
        assert manager._enabled == set()
        assert isinstance(manager._hooks, PluginHook)

    def test_create_manager_with_default_dirs(self) -> None:
        """Test manager creates default plugin directories."""
        manager = PluginManager()
        assert len(manager._plugin_dirs) == 2
        assert manager._plugin_dirs[0] == Path.home() / ".spreadsheet-dl" / "plugins"
        assert manager._plugin_dirs[1] == Path.cwd() / "plugins"

    def test_discover_plugins(self) -> None:
        """Test plugin discovery."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = Path(tmpdir)

            # Create a plugin file
            plugin_file = plugin_dir / "test_plugin.py"
            plugin_file.write_text(
                """
from spreadsheet_dl.plugins import PluginInterface

class DiscoverablePlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "discoverable"

    @property
    def version(self) -> str:
        return "2.0.0"

    def initialize(self, config=None):
        pass
"""
            )

            manager = PluginManager(plugin_dirs=[plugin_dir])
            manager.discover()

            assert "discoverable" in manager._plugins
            assert manager._plugins["discoverable"].version == "2.0.0"

    def test_enable_plugin(self) -> None:
        """Test enabling a plugin."""
        manager = PluginManager(plugin_dirs=[])
        plugin = SamplePluginBasic()
        manager._plugins[plugin.name] = plugin

        assert plugin.name not in manager._enabled
        assert not plugin.initialized

        manager.enable(plugin.name)

        assert plugin.name in manager._enabled
        assert plugin.initialized

    def test_enable_plugin_with_config(self) -> None:
        """Test enabling a plugin with configuration."""
        manager = PluginManager(plugin_dirs=[])
        plugin = SamplePluginBasic()
        manager._plugins[plugin.name] = plugin

        config = {"setting": "value"}
        manager.enable(plugin.name, config)

        assert plugin.initialized
        assert plugin.config_received == config

    def test_enable_nonexistent_plugin(self) -> None:
        """Test enabling a plugin that doesn't exist."""
        manager = PluginManager(plugin_dirs=[])

        with pytest.raises(ValueError, match="Plugin not found"):
            manager.enable("nonexistent")

    def test_disable_plugin(self) -> None:
        """Test disabling a plugin."""
        manager = PluginManager(plugin_dirs=[])
        plugin = SamplePluginBasic()
        manager._plugins[plugin.name] = plugin
        manager.enable(plugin.name)

        assert plugin.name in manager._enabled
        assert not plugin.shutdown_called

        manager.disable(plugin.name)

        assert plugin.name not in manager._enabled
        assert plugin.shutdown_called

    def test_disable_already_disabled_plugin(self) -> None:
        """Test disabling a plugin that isn't enabled."""
        manager = PluginManager(plugin_dirs=[])
        plugin = SamplePluginBasic()
        manager._plugins[plugin.name] = plugin

        # Should not raise
        manager.disable(plugin.name)

    def test_list_plugins(self) -> None:
        """Test listing all plugins."""
        manager = PluginManager(plugin_dirs=[])
        plugin1 = SamplePluginBasic()
        plugin2 = SamplePluginMinimal()
        manager._plugins[plugin1.name] = plugin1
        manager._plugins[plugin2.name] = plugin2
        manager.enable(plugin1.name)

        plugins = manager.list_plugins()

        assert len(plugins) == 2
        assert any(p["name"] == "test_basic" and p["enabled"] for p in plugins)
        assert any(p["name"] == "test_minimal" and not p["enabled"] for p in plugins)

    def test_list_enabled_plugins_only(self) -> None:
        """Test listing only enabled plugins."""
        manager = PluginManager(plugin_dirs=[])
        plugin1 = SamplePluginBasic()
        plugin2 = SamplePluginMinimal()
        manager._plugins[plugin1.name] = plugin1
        manager._plugins[plugin2.name] = plugin2
        manager.enable(plugin1.name)

        plugins = manager.list_plugins(enabled_only=True)

        assert len(plugins) == 1
        assert plugins[0]["name"] == "test_basic"

    def test_get_plugin(self) -> None:
        """Test getting plugin by name."""
        manager = PluginManager(plugin_dirs=[])
        plugin = SamplePluginBasic()
        manager._plugins[plugin.name] = plugin

        retrieved = manager.get_plugin("test_basic")
        assert retrieved is plugin

    def test_get_nonexistent_plugin(self) -> None:
        """Test getting plugin that doesn't exist."""
        manager = PluginManager(plugin_dirs=[])
        assert manager.get_plugin("nonexistent") is None

    def test_hooks_property(self) -> None:
        """Test access to hooks system."""
        manager = PluginManager(plugin_dirs=[])
        assert isinstance(manager.hooks, PluginHook)


class TestGlobalPluginManager:
    """Tests for global plugin manager singleton."""

    def test_get_plugin_manager(self) -> None:
        """Test getting global plugin manager."""
        # Note: This test may have side effects on the global state
        manager = get_plugin_manager()
        assert isinstance(manager, PluginManager)

    def test_get_plugin_manager_singleton(self) -> None:
        """Test that get_plugin_manager returns same instance."""
        manager1 = get_plugin_manager()
        manager2 = get_plugin_manager()
        assert manager1 is manager2
