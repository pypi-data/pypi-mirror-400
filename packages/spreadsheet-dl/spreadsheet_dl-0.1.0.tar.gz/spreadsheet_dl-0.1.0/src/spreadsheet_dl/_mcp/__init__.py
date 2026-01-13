"""MCP (Model Context Protocol) server package.

This package provides a modular implementation of the MCP server,
split into focused components for better maintainability.

Package Structure:
    - cli: Command-line interface and server creation helpers
    - config: Configuration classes (MCPConfig, MCPCapabilities, MCPVersion)
    - exceptions: MCP-specific exceptions
    - handlers: Common handler utilities
    - models: Data models (MCPToolParameter, MCPTool, MCPToolResult)
    - registry: Tool registry with decorator-based registration
    - server: Core MCPServer implementation
    - tools/: Tool handler implementations organized by category
        - budget: Budget analysis tools
        - cell: Cell manipulation tools
        - style: Style and formatting tools
        - structure: Row/column/sheet structure tools
        - chart: Chart creation and manipulation tools
        - advanced: Advanced features (validation, workbook ops, data import/export, etc.)

For backward compatibility, all public APIs are re-exported here.
"""

from __future__ import annotations

# CLI helpers
from spreadsheet_dl._mcp.cli import create_mcp_server, main

# Configuration
from spreadsheet_dl._mcp.config import MCPCapabilities, MCPConfig, MCPVersion

# Exceptions
from spreadsheet_dl._mcp.exceptions import MCPError, MCPSecurityError, MCPToolError

# Models
from spreadsheet_dl._mcp.models import MCPTool, MCPToolParameter, MCPToolResult

# Registry
from spreadsheet_dl._mcp.registry import MCPToolRegistry

# Server
from spreadsheet_dl._mcp.server import MCPServer

__all__ = [
    "MCPCapabilities",
    "MCPConfig",
    "MCPError",
    "MCPSecurityError",
    "MCPServer",
    "MCPTool",
    "MCPToolError",
    "MCPToolParameter",
    "MCPToolRegistry",
    "MCPToolResult",
    "MCPVersion",
    "create_mcp_server",
    "main",
]
