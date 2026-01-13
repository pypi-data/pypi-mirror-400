"""Domain test fixtures and configuration."""

from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture
def domain_plugin_factory() -> type:
    """Factory fixture for creating domain plugin instances."""

    class PluginFactory:
        """Factory for domain plugin instances."""

        @staticmethod
        def create(plugin_class: type[Any]) -> Any:
            """Create and initialize a plugin instance."""
            plugin = plugin_class()
            plugin.initialize()
            return plugin

    return PluginFactory
