#!/usr/bin/env python3
"""
Example plugin demonstrating the SpreadsheetDL plugin system.

This example shows how to create a custom plugin that extends
SpreadsheetDL functionality.


Usage:
    1. Copy this file to ~/.spreadsheet-dl/plugins/
    2. Run: spreadsheet-dl plugin list
    3. Run: spreadsheet-dl plugin enable example
    4. Run: spreadsheet-dl plugin info example
"""

from __future__ import annotations

from typing import Any

from spreadsheet_dl.plugins import PluginInterface


class ExamplePlugin(PluginInterface):
    """
    Example plugin for demonstration.

    This plugin demonstrates the basic plugin interface and lifecycle.
    It can be used as a template for creating custom plugins.

    """

    @property
    def name(self) -> str:
        """Plugin name (unique identifier)."""
        return "example"

    @property
    def version(self) -> str:
        """Plugin version (semantic versioning)."""
        return "1.0.0"

    @property
    def description(self) -> str:
        """Plugin description."""
        return "Example plugin for demonstration"

    @property
    def author(self) -> str:
        """Plugin author."""
        return "SpreadsheetDL Team"

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        """
        Initialize the plugin.

        Args:
            config: Plugin configuration dictionary

        """
        print(f"Initializing {self.name} plugin v{self.version}")
        if config:
            print(f"Config: {config}")
        # Perform plugin setup here

    def shutdown(self) -> None:
        """
        Cleanup when plugin is disabled/unloaded.

        """
        print(f"Shutting down {self.name} plugin")
        # Perform plugin cleanup here
