# Plugin System Guide

**New in v0.1.0**: Extensible plugin system for custom functionality

The SpreadsheetDL plugin system allows you to extend functionality with custom plugins. This guide covers everything you need to know about creating, installing, and managing plugins.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Plugin Development](#plugin-development)
- [Plugin Interface Reference](#plugin-interface-reference)
- [Hook System](#hook-system)
- [Plugin Directory Structure](#plugin-directory-structure)
- [CLI Commands](#cli-commands)
- [Testing Plugins](#testing-plugins)
- [Best Practices](#best-practices)
- [Example Plugins](#example-plugins)

## Overview

The plugin system provides:

- **PluginInterface**: Abstract base class for all plugins
- **PluginManager**: Lifecycle management (discover, enable, disable)
- **PluginHook**: Event-based callback system
- **PluginLoader**: Automatic discovery and loading

### Key Features

- Automatic plugin discovery from directories
- Enable/disable plugins at runtime
- Configuration support per plugin
- Event-based hooks for extending core functionality
- Isolated error handling (one plugin error doesn't break others)

## Quick Start

### Install a Plugin

1. Create plugin directory:

   ```bash
   mkdir -p ~/.spreadsheet-dl/plugins
   ```

2. Copy plugin file to directory:

   ```bash
   cp my_plugin.py ~/.spreadsheet-dl/plugins/
   ```

3. List available plugins:

   ```bash
   spreadsheet-dl plugin list
   ```

4. Enable the plugin:

   ```bash
   spreadsheet-dl plugin enable my_plugin
   ```

### Create Your First Plugin

Create `hello_plugin.py`:

```python
from spreadsheet_dl.plugins import PluginInterface

class HelloPlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "hello"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Simple hello world plugin"

    @property
    def author(self) -> str:
        return "Your Name"

    def initialize(self, config=None):
        print("Hello from HelloPlugin!")

    def shutdown(self):
        print("Goodbye from HelloPlugin!")
```

Copy to `~/.spreadsheet-dl/plugins/hello_plugin.py` and enable it.

## Plugin Development

### Minimal Plugin

Every plugin must implement `PluginInterface`:

```python
from spreadsheet_dl.plugins import PluginInterface

class MinimalPlugin(PluginInterface):
    @property
    def name(self) -> str:
        """Unique plugin identifier (lowercase, no spaces)."""
        return "minimal"

    @property
    def version(self) -> str:
        """Semantic version (e.g., '1.0.0')."""
        return "1.0.0"

    def initialize(self, config=None):
        """Called when plugin is enabled."""
        pass
```

### Full-Featured Plugin

```python
from spreadsheet_dl.plugins import PluginInterface
from typing import Any

class AdvancedPlugin(PluginInterface):
    def __init__(self):
        self.settings = {}
        self.is_active = False

    @property
    def name(self) -> str:
        return "advanced"

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def description(self) -> str:
        return "Advanced plugin with configuration"

    @property
    def author(self) -> str:
        return "Developer Name"

    def initialize(self, config: dict[str, Any] | None = None):
        """Initialize with optional configuration."""
        if config:
            self.settings = config

        # Perform setup
        self.is_active = True
        print(f"Initialized {self.name} with settings: {self.settings}")

    def shutdown(self):
        """Clean up when disabled."""
        self.is_active = False
        print(f"Shutting down {self.name}")
```

### Using Configuration

Enable plugin with configuration:

```bash
spreadsheet-dl plugin enable advanced --config '{"api_key":"xxx","debug":true}'
```

Access in plugin:

```python
def initialize(self, config=None):
    if config:
        self.api_key = config.get('api_key')
        self.debug = config.get('debug', False)
```

## Plugin Interface Reference

### Required Properties

#### `name`

```python
@property
def name(self) -> str:
    """Unique plugin identifier."""
    return "my_plugin"
```

- Must be unique across all plugins
- Use lowercase, underscores for spaces
- Used for enable/disable operations

#### `version`

```python
@property
def version(self) -> str:
    """Plugin version."""
    return "1.0.0"
```

- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Displayed in plugin listings

### Optional Properties

#### `description`

```python
@property
def description(self) -> str:
    """Human-readable description."""
    return "What this plugin does"
```

#### `author`

```python
@property
def author(self) -> str:
    """Plugin author."""
    return "Your Name or Organization"
```

### Required Methods

#### `initialize(config)`

```python
def initialize(self, config: dict[str, Any] | None = None) -> None:
    """Called when plugin is enabled."""
    # Setup code here
    pass
```

- Called when plugin is enabled
- Receives optional configuration dictionary
- Perform initialization, register hooks, etc.

### Optional Methods

#### `shutdown()`

```python
def shutdown(self) -> None:
    """Called when plugin is disabled."""
    # Cleanup code here
    pass
```

- Called when plugin is disabled
- Release resources, unregister hooks, save state

## Hook System

Plugins can register callbacks for events:

```python
from spreadsheet_dl.plugins import get_plugin_manager

class HookPlugin(PluginInterface):
    def initialize(self, config=None):
        manager = get_plugin_manager()

        # Register callback for event
        manager.hooks.register('before_export', self.on_before_export)

    def on_before_export(self, filepath, format):
        print(f"Exporting to {filepath} as {format}")
        # Modify export behavior

    def shutdown(self):
        manager = get_plugin_manager()
        manager.hooks.unregister('before_export', self.on_before_export)
```

### Triggering Hooks

Core code can trigger hooks:

```python
from spreadsheet_dl.plugins import get_plugin_manager

def export_file(filepath, format):
    manager = get_plugin_manager()

    # Trigger pre-export hooks
    manager.hooks.trigger('before_export', filepath, format)

    # ... perform export ...

    # Trigger post-export hooks
    manager.hooks.trigger('after_export', filepath, format)
```

### Available Hook Events

Common hook events (may vary by version):

- `before_export` - Before file export
- `after_export` - After file export
- `before_import` - Before file import
- `after_import` - After file import
- `budget_created` - After budget creation
- `expense_added` - After expense entry

_Note: Check core documentation for complete hook event list._

## Plugin Directory Structure

### Default Plugin Directories

Plugins are discovered from:

1. `~/.spreadsheet-dl/plugins/` (user plugins)
2. `./plugins/` (project-local plugins)

### Directory Layout

```
~/.spreadsheet-dl/
└── plugins/
    ├── my_plugin.py          # Single-file plugin
    ├── advanced_plugin.py
    └── custom_plugin.py
```

### Private Files

Files starting with underscore are ignored:

```
plugins/
├── my_plugin.py       # ✓ Discovered
├── _helper.py         # ✗ Skipped (private)
└── __init__.py        # ✗ Skipped (private)
```

## CLI Commands

### List Plugins

```bash
# List all plugins
spreadsheet-dl plugin list

# List only enabled plugins
spreadsheet-dl plugin list --enabled-only

# JSON output
spreadsheet-dl plugin list --json
```

### Enable Plugin

```bash
# Enable without configuration
spreadsheet-dl plugin enable my_plugin

# Enable with configuration
spreadsheet-dl plugin enable my_plugin --config '{"key":"value"}'
```

### Disable Plugin

```bash
spreadsheet-dl plugin disable my_plugin
```

### Plugin Info

```bash
spreadsheet-dl plugin info my_plugin
```

Output:

```
Plugin: my_plugin
========================================
  Version:     1.0.0
  Author:      Developer Name
  Description: Plugin description
  Status:      Enabled
```

## Testing Plugins

### Manual Testing

1. Create test plugin:

   ```python
   # test_plugin.py
   from spreadsheet_dl.plugins import PluginInterface

   class TestPlugin(PluginInterface):
       @property
       def name(self) -> str:
           return "test"

       @property
       def version(self) -> str:
           return "0.1.0"

       def initialize(self, config=None):
           print("Test plugin initialized")
   ```

2. Copy to plugin directory
3. Test discovery: `spreadsheet-dl plugin list`
4. Test enable: `spreadsheet-dl plugin enable test`
5. Test disable: `spreadsheet-dl plugin disable test`

### Automated Testing

Use pytest for plugin tests:

```python
# test_my_plugin.py
import pytest
from my_plugin import MyPlugin

def test_plugin_properties():
    plugin = MyPlugin()
    assert plugin.name == "my_plugin"
    assert plugin.version.startswith("1.")

def test_plugin_initialization():
    plugin = MyPlugin()
    plugin.initialize({"debug": True})
    assert plugin.debug is True

def test_plugin_shutdown():
    plugin = MyPlugin()
    plugin.initialize()
    plugin.shutdown()
    # Verify cleanup occurred
```

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
def initialize(self, config=None):
    try:
        # Setup code
        self.connect()
    except Exception as e:
        print(f"Plugin {self.name} initialization failed: {e}")
        raise
```

### 2. Resource Cleanup

Clean up in shutdown:

```python
def shutdown(self):
    # Close connections
    if hasattr(self, 'connection'):
        self.connection.close()

    # Save state
    if hasattr(self, 'state'):
        self.save_state()
```

### 3. Configuration Validation

Validate configuration:

```python
def initialize(self, config=None):
    if config:
        required = ['api_key', 'endpoint']
        for key in required:
            if key not in config:
                raise ValueError(f"Missing required config: {key}")
```

### 4. Version Compatibility

Document compatible SpreadsheetDL versions:

```python
@property
def description(self) -> str:
    return "My plugin (requires SpreadsheetDL >= 0.1.0)"
```

### 5. Thread Safety

If using threads, ensure thread safety:

```python
import threading

class ThreadSafePlugin(PluginInterface):
    def __init__(self):
        self._lock = threading.Lock()

    def process(self, data):
        with self._lock:
            # Thread-safe operation
            pass
```

## Example Plugins

### Logging Plugin

```python
import logging
from spreadsheet_dl.plugins import PluginInterface, get_plugin_manager

class LoggingPlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "logging"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Log all SpreadsheetDL operations"

    def initialize(self, config=None):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('spreadsheet_dl')

        # Register hooks
        manager = get_plugin_manager()
        manager.hooks.register('before_export', self.log_export)

    def log_export(self, filepath, format):
        self.logger.info(f"Exporting to {filepath} as {format}")
```

### Custom Format Plugin

```python
from spreadsheet_dl.plugins import PluginInterface

class CustomFormatPlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "custom_format"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Add support for custom file format"

    def initialize(self, config=None):
        # Register custom export format
        self.register_exporter()

    def register_exporter(self):
        # Implementation to add custom format
        pass
```

### Notification Plugin

```python
from spreadsheet_dl.plugins import PluginInterface, get_plugin_manager
import requests

class NotificationPlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "notifications"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self, config=None):
        self.webhook_url = config.get('webhook_url') if config else None

        manager = get_plugin_manager()
        manager.hooks.register('budget_created', self.notify)

    def notify(self, filepath):
        if self.webhook_url:
            requests.post(self.webhook_url, json={
                'message': f'Budget created: {filepath}'
            })
```

## Troubleshooting

### Plugin Not Discovered

1. Check file location (must be in plugin directory)
2. Check filename (no leading underscore)
3. Verify plugin implements `PluginInterface`
4. Run `spreadsheet-dl plugin list` to see errors

### Plugin Won't Enable

1. Check for initialization errors
2. Verify required configuration is provided
3. Check for missing dependencies
4. Review plugin logs/output

### Plugin Errors

Plugins are isolated - one plugin error won't crash SpreadsheetDL:

```
Plugin hook error for before_export: connection timeout
```

Fix the plugin and re-enable it.

## Advanced Topics

### Multi-File Plugins

For complex plugins, use Python packages:

```
plugins/
└── my_plugin/
    ├── __init__.py
    ├── plugin.py      # Plugin class
    ├── helpers.py     # Helper functions
    └── config.yaml    # Configuration
```

In `plugin.py`:

```python
from spreadsheet_dl.plugins import PluginInterface

class MyPlugin(PluginInterface):
    # Plugin implementation
    pass
```

### Dependency Management

Document dependencies in plugin:

```python
"""
Dependencies:
    - requests>=2.31.0
    - pandas>=2.0.0

Install: uv pip install requests pandas
"""
```

### Plugin Distribution

Share plugins via:

1. Git repository
2. PyPI package
3. Direct file sharing

## API Reference

See module documentation for complete API:

- `spreadsheet_dl.plugins.PluginInterface` - Base class
- `spreadsheet_dl.plugins.PluginManager` - Lifecycle manager
- `spreadsheet_dl.plugins.PluginHook` - Event system
- `spreadsheet_dl.plugins.PluginLoader` - Discovery/loading
- `spreadsheet_dl.plugins.get_plugin_manager()` - Global singleton

## Further Reading

- [API Documentation](./api/index.md)
- [Best Practices](guides/best-practices.md)
- [Example Plugins](./examples/index.md)
- [GitHub Repository](https://github.com/lair-click-bats/spreadsheet-dl)

---

**Version**: 0.1.0
**Last Updated**: 2026-01-03
