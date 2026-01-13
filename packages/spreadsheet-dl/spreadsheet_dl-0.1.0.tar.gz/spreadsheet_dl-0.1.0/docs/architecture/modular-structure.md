# Modular Package Structure

## Overview

As of v0.1.0, SpreadsheetDL has begun transitioning to a more modular package structure to improve maintainability and code organization. The large monolithic files have been split into focused packages.

## Current Structure

### MCP Package (`spreadsheet_dl._mcp/`)

The MCP server implementation is organized into focused modules:

```
src/spreadsheet_dl/_mcp/
├── __init__.py          # Public API exports
├── config.py            # Configuration classes (MCPConfig, MCPCapabilities, MCPVersion)
├── exceptions.py        # MCP-specific exceptions
├── models.py            # Data models (MCPToolParameter, MCPTool, MCPToolResult)
└── registry.py          # Tool registry with decorator-based registration
```

**Usage:**

```python
# Option 1: Import from _mcp package directly
from spreadsheet_dl._mcp import MCPConfig, MCPServer

# Option 2: Use package namespace
from spreadsheet_dl import mcp_pkg
config = mcp_pkg.MCPConfig()

# Option 3: Original import (backward compatible)
from spreadsheet_dl.mcp_server import MCPConfig, MCPServer
```

### Builder Package (`spreadsheet_dl._builder/`)

The builder API will be organized into focused modules:

```
src/spreadsheet_dl/_builder/
├── __init__.py          # Public API exports
├── exceptions.py        # Builder-specific exceptions (planned)
├── models.py            # Data models (CellSpec, RowSpec, etc.) (planned)
├── references.py        # Cell and range references (planned)
├── formulas.py          # Formula builder (planned)
└── core.py              # Main SpreadsheetBuilder class (planned)
```

**Current Status:** Re-exports from `builder.py` for compatibility.

**Usage:**

```python
# Option 1: Import from _builder package
from spreadsheet_dl._builder import SpreadsheetBuilder, FormulaBuilder

# Option 2: Use package namespace
from spreadsheet_dl import builder_pkg
builder = builder_pkg.SpreadsheetBuilder()

# Option 3: Original import (backward compatible)
from spreadsheet_dl.builder import SpreadsheetBuilder
```

### CLI Package (`spreadsheet_dl._cli/`)

The CLI implementation will be organized into focused modules:

```
src/spreadsheet_dl/_cli/
├── __init__.py          # Public API exports
├── utils.py             # Confirmation utilities (planned)
├── commands.py          # Command implementations (planned)
└── app.py               # Main CLI application (planned)
```

**Current Status:** Re-exports from `cli.py` for compatibility.

**Usage:**

```python
# Option 1: Import from _cli package
from spreadsheet_dl._cli import main, confirm_action

# Option 2: Use package namespace
from spreadsheet_dl import cli_pkg
cli_pkg.main()

# Option 3: Original import (backward compatible)
from spreadsheet_dl.cli import main
```

## Migration Status

### Completed (v0.1.0)

- ✅ Created modular package structure
- ✅ Extracted MCP configuration, exceptions, models, and registry
- ✅ Set up backward-compatible re-exports
- ✅ Added public package namespace access
- ✅ All tests passing
- ✅ Zero regressions

### Planned (Future Releases)

- ⏳ Extract MCP tool handlers to `_mcp/tools.py`
- ⏳ Extract MCP server core to `_mcp/server.py`
- ⏳ Split `builder.py` into modular components
- ⏳ Split `cli.py` into modular components
- ⏳ Update internal imports to use new structure
- ⏳ Phase out monolithic files (post-v0.1.0)

## Backward Compatibility

**IMPORTANT:** All original import paths continue to work. This is critical for:

- Existing user code
- Examples and documentation
- Third-party integrations

Example:

```python
# These all work and will continue to work:
from spreadsheet_dl.mcp_server import MCPServer
from spreadsheet_dl.builder import SpreadsheetBuilder
from spreadsheet_dl.cli import main
```

## Design Principles

1. **Gradual Migration:** Transition incrementally to minimize risk
2. **Backward Compatibility:** Never break existing imports
3. **Clear Organization:** Each module has a single, focused responsibility
4. **Public API:** Package structure is part of the public API
5. **Testing:** 100% test coverage maintained throughout transition

## File Size Reduction (Planned)

Current monolithic files:

- `mcp_server.py`: 4,354 lines → Split into 7 focused modules
- `builder.py`: 2,498 lines → Split into 6 focused modules
- `cli.py`: 2,373 lines → Split into 4 focused modules

**Total:** 9,225 lines → 17 focused modules (~500 lines each)

## Benefits

1. **Maintainability:** Easier to understand and modify focused modules
2. **Testing:** Easier to test isolated components
3. **Collaboration:** Multiple developers can work on different modules
4. **Performance:** Faster imports (import only what you need)
5. **Documentation:** Clearer API structure

## Internal Package Naming

Packages are prefixed with `_` to indicate they are primarily for internal organization:

- `_mcp` - MCP server internals
- `_builder` - Builder API internals
- `_cli` - CLI internals

These are publicly accessible via the main package for users who want modular access.

## See Also

- [Architecture Overview](../ARCHITECTURE.md)
- [Migration Guide](../guides/migration-guide.md)
- [API Documentation](../api/index.md)
