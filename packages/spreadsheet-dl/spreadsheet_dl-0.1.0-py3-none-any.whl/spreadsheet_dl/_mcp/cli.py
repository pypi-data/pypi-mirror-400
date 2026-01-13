"""Helper functions for MCP server creation and CLI entry point.

These functions provide convenient wrappers for creating and running
the MCP server from Python code or command line.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from spreadsheet_dl._mcp.config import MCPConfig
from spreadsheet_dl._mcp.server import MCPServer


def create_mcp_server(
    allowed_paths: list[str | Path] | None = None,
) -> MCPServer:
    """Create an MCP server with optional path restrictions.

    Args:
        allowed_paths: List of paths the server can access.

    Returns:
        Configured MCPServer instance.
    """
    config = MCPConfig(
        allowed_paths=[Path(p) for p in allowed_paths] if allowed_paths else [],
    )
    return MCPServer(config)


def main() -> None:
    """Entry point for MCP server CLI."""
    parser = argparse.ArgumentParser(
        description="SpreadsheetDL MCP Server",
    )
    parser.add_argument(
        "--allowed-paths",
        nargs="*",
        help="Allowed file paths",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    # Configure logging
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    # Create and run server
    server = create_mcp_server(args.allowed_paths)
    server.run()


__all__ = ["create_mcp_server", "main"]
