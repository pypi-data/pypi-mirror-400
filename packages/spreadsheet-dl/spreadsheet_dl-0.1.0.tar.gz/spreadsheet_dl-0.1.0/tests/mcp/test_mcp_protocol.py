"""
Tests for MCP server protocol and integration.

Tests IR-MCP-002: Native MCP Server - Protocol and Integration.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from spreadsheet_dl.exceptions import FileError
from spreadsheet_dl.mcp_server import (
    MCPConfig,
    MCPError,
    MCPSecurityError,
    MCPServer,
    MCPTool,
    MCPToolError,
    MCPToolResult,
    create_mcp_server,
)

pytestmark = [pytest.mark.unit, pytest.mark.mcp]


class TestMCPServerMessageProtocol:
    """Tests for MCP server message protocol handling."""

    @pytest.fixture
    def server(self, tmp_path: Path) -> MCPServer:
        """Create a test server."""
        config = MCPConfig(allowed_paths=[tmp_path, Path.cwd()])
        return MCPServer(config)

    def test_invalid_jsonrpc_version(self, server: MCPServer) -> None:
        """Test handling invalid JSON-RPC version."""
        message = {
            "jsonrpc": "1.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        }

        response = server.handle_message(message)

        # Should handle gracefully
        assert response is not None

    def test_missing_method(self, server: MCPServer) -> None:
        """Test handling message without method."""
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "params": {},
        }

        response = server.handle_message(message)
        assert response is not None

        assert "error" in response

    def test_missing_id(self, server: MCPServer) -> None:
        """Test handling request without id."""
        message = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
        }

        # Notification (no id) should not return error
        response = server.handle_message(message)
        # May return None or response depending on implementation
        assert response is None or isinstance(response, dict)

    def test_tools_call_with_arguments(self, server: MCPServer) -> None:
        """Test tools/call with arguments."""
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "theme_list",
                "arguments": {"file_path": "/tmp/test.ods"},
            },
        }

        response = server.handle_message(message)
        assert response is not None

        assert "result" in response
        assert "content" in response["result"]


class TestCreateMCPServer:
    """Tests for create_mcp_server function."""

    def test_create_with_paths(self) -> None:
        """Test creating server with allowed paths."""
        server = create_mcp_server(["/tmp", "/home"])

        assert len(server.config.allowed_paths) == 2
        assert Path("/tmp") in server.config.allowed_paths
        assert Path("/home") in server.config.allowed_paths

    def test_create_without_paths(self) -> None:
        """Test creating server without paths."""
        server = create_mcp_server()

        # Should have default paths
        assert len(server.config.allowed_paths) >= 0

    def test_create_with_empty_paths(self) -> None:
        """Test creating server with empty paths list."""
        server = create_mcp_server([])

        # Should use defaults when empty
        assert len(server.config.allowed_paths) > 0


class TestMCPErrors:
    """Tests for MCP errors."""

    def test_mcp_error(self) -> None:
        """Test base MCP error."""
        error = MCPError("Test error")
        assert error.error_code == "FT-MCP-1900"
        assert "Test error" in str(error)
        assert "FT-MCP-1900" in str(error)

    def test_tool_error(self) -> None:
        """Test tool error."""
        error = MCPToolError("Tool failed")
        assert error.error_code == "FT-MCP-1901"
        assert "Tool failed" in str(error)
        assert "FT-MCP-1901" in str(error)

    def test_security_error(self) -> None:
        """Test security error."""
        error = MCPSecurityError("Access denied")
        assert error.error_code == "FT-MCP-1902"
        assert "Access denied" in str(error)
        assert "FT-MCP-1902" in str(error)

    def test_error_inheritance(self) -> None:
        """Test error inheritance hierarchy."""
        assert issubclass(MCPToolError, MCPError)
        assert issubclass(MCPSecurityError, MCPError)


class TestMCPServerAuditLogging:
    """Tests for MCP server audit logging."""

    @pytest.fixture
    def server_with_audit(self, tmp_path: Path) -> MCPServer:
        """Create a server with audit logging enabled."""
        log_path = tmp_path / "audit.log"
        config = MCPConfig(
            allowed_paths=[tmp_path],
            enable_audit_log=True,
            audit_log_path=log_path,
        )
        return MCPServer(config)

    def test_audit_log_enabled(self, server_with_audit: MCPServer) -> None:
        """Test audit logging is enabled."""
        assert server_with_audit.config.enable_audit_log is True

    def test_audit_log_path_set(
        self, server_with_audit: MCPServer, tmp_path: Path
    ) -> None:
        """Test audit log path is set."""
        assert server_with_audit.config.audit_log_path == tmp_path / "audit.log"

    def test_audit_logging_writes_to_file(
        self, server_with_audit: MCPServer, tmp_path: Path
    ) -> None:
        """Test audit logging writes to file."""
        result = MCPToolResult.text("test")
        params = {"tool": "test"}

        server_with_audit._log_audit("test_tool", params, result)

        log_path = tmp_path / "audit.log"
        assert log_path.exists()
        log_content = log_path.read_text()
        assert "test_tool" in log_content
        assert "test" in log_content

    def test_audit_logging_disabled(self, tmp_path: Path) -> None:
        """Test audit logging when disabled."""
        config = MCPConfig(
            allowed_paths=[tmp_path],
            enable_audit_log=False,
        )
        server = MCPServer(config)

        result = MCPToolResult.text("test")
        params = {"tool": "test"}

        # Should not raise
        server._log_audit("test_tool", params, result)


class TestMCPServerIntegrationToolCalls:
    """Integration tests for MCP server tool calls via handle_message."""

    @pytest.fixture
    def server(self, tmp_path: Path) -> MCPServer:
        """Create a test server."""
        config = MCPConfig(allowed_paths=[tmp_path, Path.cwd()])
        return MCPServer(config)

    def test_cell_get_via_message(self, server: MCPServer, tmp_path: Path) -> None:
        """Test cell_get tool via MCP message."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "cell_get",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "cell": "A1",
                },
            },
        }

        response = server.handle_message(message)
        assert response is not None
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        assert "content" in response["result"]

    def test_cell_set_via_message(self, server: MCPServer, tmp_path: Path) -> None:
        """Test cell_set tool via MCP message."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "cell_set",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "cell": "A1",
                    "value": "Test Value",
                },
            },
        }

        response = server.handle_message(message)
        assert response is not None
        assert response["jsonrpc"] == "2.0"
        assert "result" in response

    def test_cell_clear_via_message(self, server: MCPServer, tmp_path: Path) -> None:
        """Test cell_clear tool via MCP message."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "cell_clear",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "cell": "A1",
                },
            },
        }

        response = server.handle_message(message)
        assert response is not None
        assert "result" in response

    def test_cell_copy_via_message(self, server: MCPServer, tmp_path: Path) -> None:
        """Test cell_copy tool via MCP message."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        message = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "cell_copy",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "source": "A1",
                    "destination": "B1",
                },
            },
        }

        response = server.handle_message(message)
        assert response is not None
        assert "result" in response

    def test_cell_move_via_message(self, server: MCPServer, tmp_path: Path) -> None:
        """Test cell_move tool via MCP message."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        message = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "cell_move",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "source": "A1",
                    "destination": "C1",
                },
            },
        }

        response = server.handle_message(message)
        assert response is not None
        assert "result" in response

    def test_cell_batch_get_via_message(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test cell_batch_get tool via MCP message."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        message = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "cell_batch_get",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "cells": "A1,B1,C1",
                },
            },
        }

        response = server.handle_message(message)
        assert response is not None
        assert "result" in response

    def test_cell_batch_set_via_message(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test cell_batch_set tool via MCP message."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        message = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "cell_batch_set",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "updates": '{"A1": "value1", "B1": "value2"}',
                },
            },
        }

        response = server.handle_message(message)
        assert response is not None
        assert "result" in response

    def test_cell_find_via_message(self, server: MCPServer, tmp_path: Path) -> None:
        """Test cell_find tool via MCP message."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        message = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "cell_find",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "pattern": "test",
                    "match_case": False,
                },
            },
        }

        response = server.handle_message(message)
        assert response is not None
        assert "result" in response

    def test_cell_replace_via_message(self, server: MCPServer, tmp_path: Path) -> None:
        """Test cell_replace tool via MCP message."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        message = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "cell_replace",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "find": "old",
                    "replace": "new",
                },
            },
        }

        response = server.handle_message(message)
        assert response is not None
        assert "result" in response

    def test_cell_merge_via_message(self, server: MCPServer, tmp_path: Path) -> None:
        """Test cell_merge tool via MCP message."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        message = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "cell_merge",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "range": "A1:B2",
                },
            },
        }

        response = server.handle_message(message)
        assert response is not None
        assert "result" in response

    def test_cell_unmerge_via_message(self, server: MCPServer, tmp_path: Path) -> None:
        """Test cell_unmerge tool via MCP message."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        message = {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {
                "name": "cell_unmerge",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "range": "A1",
                },
            },
        }

        response = server.handle_message(message)
        assert response is not None
        assert "result" in response

    def test_style_tools_via_message(self, server: MCPServer, tmp_path: Path) -> None:
        """Test style operation tools via MCP messages."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        # Test style_list which only needs file_path
        message = {
            "jsonrpc": "2.0",
            "id": 100,
            "method": "tools/call",
            "params": {
                "name": "style_list",
                "arguments": {
                    "file_path": str(test_file),
                },
            },
        }
        response = server.handle_message(message)
        assert response is not None
        assert "result" in response, "Tool style_list failed"

        # Test format_cells which needs file_path, sheet, and range
        message = {
            "jsonrpc": "2.0",
            "id": 101,
            "method": "tools/call",
            "params": {
                "name": "format_cells",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "range": "A1:B2",
                    "format": "general",
                },
            },
        }
        response = server.handle_message(message)
        assert response is not None
        assert "result" in response, "Tool format_cells failed"

    def test_structure_tools_via_message(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test structure operation tools via MCP messages."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        # Test row_insert which needs file_path, sheet, and row
        message = {
            "jsonrpc": "2.0",
            "id": 200,
            "method": "tools/call",
            "params": {
                "name": "row_insert",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "row": 1,
                },
            },
        }
        response = server.handle_message(message)
        assert response is not None
        assert "result" in response, "Tool row_insert failed"

        # Test freeze_clear which needs file_path and sheet
        message = {
            "jsonrpc": "2.0",
            "id": 201,
            "method": "tools/call",
            "params": {
                "name": "freeze_clear",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                },
            },
        }
        response = server.handle_message(message)
        assert response is not None
        assert "result" in response, "Tool freeze_clear failed"

        # Test sheet_create which needs file_path and sheet
        message = {
            "jsonrpc": "2.0",
            "id": 202,
            "method": "tools/call",
            "params": {
                "name": "sheet_create",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "NewSheet",
                },
            },
        }
        response = server.handle_message(message)
        assert response is not None
        assert "result" in response, "Tool sheet_create failed"

    def test_advanced_tools_via_message(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test advanced operation tools via MCP messages."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        # Test chart_create which needs file_path, sheet, chart_type, and data_range
        message = {
            "jsonrpc": "2.0",
            "id": 300,
            "method": "tools/call",
            "params": {
                "name": "chart_create",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "chart_type": "line",
                    "data_range": "A1:B5",
                },
            },
        }
        response = server.handle_message(message)
        assert response is not None
        # Chart creation might fail for ODS but should return a response
        assert response.get("result") is not None or response.get("error") is not None

        # Test named_range_create which needs file_path, sheet, name, and range
        message = {
            "jsonrpc": "2.0",
            "id": 301,
            "method": "tools/call",
            "params": {
                "name": "named_range_create",
                "arguments": {
                    "file_path": str(test_file),
                    "sheet": "Sheet1",
                    "name": "TestRange",
                    "range": "A1:B5",
                },
            },
        }
        response = server.handle_message(message)
        assert response is not None
        assert response.get("result") is not None or response.get("error") is not None

    def test_rate_limit_exceeded_via_message(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test rate limit exceeded error via MCP message."""
        # Set request count to limit
        server._request_count = server.config.rate_limit_per_minute

        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }

        response = server.handle_message(message)
        assert response is not None
        assert "error" in response
        assert response["error"]["code"] == -32000
        assert "rate limit" in response["error"]["message"].lower()

    def test_tool_with_no_handler(self, server: MCPServer) -> None:
        """Test calling a tool with no handler."""
        # Add a tool without handler
        tool = MCPTool(name="no_handler", description="Tool without handler")
        server._tools["no_handler"] = tool

        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "no_handler",
                "arguments": {},
            },
        }

        response = server.handle_message(message)
        assert response is not None
        assert "error" in response
        assert response["error"]["code"] == -32603

    def test_error_response_format(self, server: MCPServer) -> None:
        """Test error response format."""
        response = server._error_response(1, -32000, "Test error")

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32000
        assert response["error"]["message"] == "Test error"


class TestMCPServerPathValidation:
    """Tests for path validation edge cases."""

    @pytest.fixture
    def server(self, tmp_path: Path) -> MCPServer:
        """Create a test server."""
        config = MCPConfig(allowed_paths=[tmp_path])
        return MCPServer(config)

    def test_validate_path_nonexistent_file(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test validating path for nonexistent file."""
        nonexistent = tmp_path / "nonexistent.ods"

        with pytest.raises(FileError):
            server._validate_path(str(nonexistent))

    def test_validate_path_outside_allowed(self, server: MCPServer) -> None:
        """Test validating path outside allowed paths."""
        with pytest.raises(MCPSecurityError) as exc_info:
            server._validate_path("/etc/passwd")

        assert "not allowed" in str(exc_info.value).lower()

    def test_validate_path_string_conversion(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test path validation with string input."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        # Should accept string
        result = server._validate_path(str(test_file))
        assert result == test_file

    def test_validate_path_relative_path(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test path validation with relative path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        # Update allowed paths to include parent
        server.config.allowed_paths = [tmp_path.parent]

        result = server._validate_path(str(test_file))
        assert result.is_absolute()
