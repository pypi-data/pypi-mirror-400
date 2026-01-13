"""
Tests for MCP server CLI.

Tests IR-MCP-002: Native MCP Server - CLI.
"""

from __future__ import annotations

import contextlib
import json
import logging
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from spreadsheet_dl.mcp_server import (
    MCPConfig,
    MCPServer,
    create_mcp_server,
)

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = [pytest.mark.unit, pytest.mark.mcp]


class TestMCPServerMain:
    """Tests for main CLI function."""

    def test_main_function_imports(self) -> None:
        """Test that main function can be imported."""
        from spreadsheet_dl.mcp_server import main

        assert callable(main)


class TestMCPServerMainCLI:
    """Tests for main CLI function and run loop."""

    def test_main_cli_argument_parsing(self) -> None:
        """Test main function argument parsing."""
        from unittest.mock import MagicMock

        from spreadsheet_dl.mcp_server import main

        with (
            patch("sys.argv", ["mcp_server", "--debug", "--allowed-paths", "/tmp"]),
            patch("spreadsheet_dl._mcp.cli.create_mcp_server") as mock_create,
            patch("logging.basicConfig") as mock_logging,
        ):
            mock_server = MagicMock()
            mock_create.return_value = mock_server
            mock_server.run.side_effect = KeyboardInterrupt()

            with contextlib.suppress(KeyboardInterrupt):
                main()

            mock_create.assert_called_once()
            mock_logging.assert_called_once()
            # Verify debug logging was enabled
            call_kwargs = mock_logging.call_args[1]
            assert call_kwargs["level"] == logging.DEBUG

    def test_main_cli_without_debug(self) -> None:
        """Test main function without debug flag."""
        from spreadsheet_dl.mcp_server import main

        with (
            patch("sys.argv", ["mcp_server"]),
            patch("spreadsheet_dl._mcp.cli.create_mcp_server") as mock_create,
            patch("logging.basicConfig") as mock_logging,
        ):
            mock_server = MagicMock()
            mock_create.return_value = mock_server
            mock_server.run.side_effect = KeyboardInterrupt()

            with contextlib.suppress(KeyboardInterrupt):
                main()

            call_kwargs = mock_logging.call_args[1]
            assert call_kwargs["level"] == logging.INFO

    def test_server_run_loop_with_valid_message(self, tmp_path: Path) -> None:
        """Test server run loop with valid JSON-RPC message."""
        config = MCPConfig(allowed_paths=[tmp_path])
        server = MCPServer(config)

        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }

        with (
            patch("sys.stdin.readline", side_effect=[json.dumps(message) + "\n", ""]),
            patch("sys.stdout.write") as mock_write,
            patch("sys.stdout.flush"),
        ):
            server.run()

            # Verify response was written
            assert mock_write.called

    def test_server_run_loop_with_invalid_json(self, tmp_path: Path) -> None:
        """Test server run loop with invalid JSON."""
        config = MCPConfig(allowed_paths=[tmp_path])
        server = MCPServer(config)

        with (
            patch("sys.stdin.readline", side_effect=["{invalid json\n", ""]),
            patch("sys.stdout.write"),
            patch("sys.stdout.flush"),
        ):
            server.run()

            # Should not crash, just log error

    def test_server_run_loop_keyboard_interrupt(self, tmp_path: Path) -> None:
        """Test server run loop handles keyboard interrupt."""
        config = MCPConfig(allowed_paths=[tmp_path])
        server = MCPServer(config)

        with patch("sys.stdin.readline", side_effect=KeyboardInterrupt()):
            server.run()
            # Should exit gracefully

    def test_server_run_loop_general_exception(self, tmp_path: Path) -> None:
        """Test server run loop handles general exceptions."""
        config = MCPConfig(allowed_paths=[tmp_path])
        server = MCPServer(config)

        with patch("sys.stdin.readline", side_effect=Exception("Unexpected error")):
            server.run()
            # Should exit gracefully

    def test_create_mcp_server_with_paths(self) -> None:
        """Test create_mcp_server with allowed paths."""

        server = create_mcp_server(allowed_paths=["/tmp", "/home"])

        assert server is not None
        assert len(server.config.allowed_paths) == 2

    def test_create_mcp_server_without_paths(self) -> None:
        """Test create_mcp_server without allowed paths uses defaults."""

        server = create_mcp_server(allowed_paths=None)

        assert server is not None
        # MCPConfig sets default paths in __post_init__ when allowed_paths is empty
        assert len(server.config.allowed_paths) > 0
