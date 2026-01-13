"""MCP-specific exceptions.

Part of the modular MCP server implementation.
All MCP exceptions inherit from the base SpreadsheetDLError.
"""

from __future__ import annotations

from spreadsheet_dl.exceptions import SpreadsheetDLError


class MCPError(SpreadsheetDLError):
    """Base exception for MCP server errors."""

    error_code = "FT-MCP-1900"


class MCPToolError(MCPError):
    """Raised when a tool execution fails."""

    error_code = "FT-MCP-1901"


class MCPSecurityError(MCPError):
    """Raised when a security violation occurs."""

    error_code = "FT-MCP-1902"
