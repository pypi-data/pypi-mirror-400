"""
Tests for MCP server direct handler calls and exception handling.

Tests IR-MCP-002: Native MCP Server - Handlers.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from spreadsheet_dl.mcp_server import (
    MCPConfig,
    MCPServer,
    MCPToolResult,
)

pytestmark = [pytest.mark.unit, pytest.mark.mcp]


class TestMCPServerDirectHandlerCalls:
    """Direct tests for handler methods to increase coverage."""

    @pytest.fixture
    def server(self, tmp_path: Path) -> MCPServer:
        """Create a test server."""
        config = MCPConfig(allowed_paths=[tmp_path, Path.cwd()])
        return MCPServer(config)

    def test_handle_cell_get_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to cell_get handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_cell_get(
            file_path=str(test_file),
            sheet="Sheet1",
            cell="A1",
        )

        assert result is not None
        assert isinstance(result, MCPToolResult)

    def test_handle_cell_set_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to cell_set handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_cell_set(
            file_path=str(test_file),
            sheet="Sheet1",
            cell="A1",
            value="test value",
        )

        assert result is not None

    def test_handle_cell_clear_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to cell_clear handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_cell_clear(
            file_path=str(test_file),
            sheet="Sheet1",
            cell="A1",
        )

        assert result is not None

    def test_handle_cell_copy_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to cell_copy handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_cell_copy(
            file_path=str(test_file),
            sheet="Sheet1",
            source="A1",
            destination="B1",
        )

        assert result is not None

    def test_handle_cell_move_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to cell_move handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_cell_move(
            file_path=str(test_file),
            sheet="Sheet1",
            source="A1",
            destination="C1",
        )

        assert result is not None

    def test_handle_cell_batch_get_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to cell_batch_get handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_cell_batch_get(
            file_path=str(test_file),
            sheet="Sheet1",
            cells="A1,B1,C1",
        )

        assert result is not None

    def test_handle_cell_batch_set_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to cell_batch_set handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_cell_batch_set(
            file_path=str(test_file),
            sheet="Sheet1",
            updates='{"A1": "val1", "B1": "val2"}',
        )

        assert result is not None

    def test_handle_cell_find_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to cell_find handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_cell_find(
            file_path=str(test_file),
            sheet="Sheet1",
            pattern="test",
            match_case=True,
        )

        assert result is not None

    def test_handle_cell_replace_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to cell_replace handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_cell_replace(
            file_path=str(test_file),
            sheet="Sheet1",
            find="old",
            replace="new",
        )

        assert result is not None

    def test_handle_cell_merge_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to cell_merge handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_cell_merge(
            file_path=str(test_file),
            sheet="Sheet1",
            range="A1:B2",
        )

        assert result is not None

    def test_handle_cell_unmerge_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to cell_unmerge handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_cell_unmerge(
            file_path=str(test_file),
            sheet="Sheet1",
            range="A1:B2",
        )

        assert result is not None

    def test_handle_style_list_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to style_list handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_style_list(
            file_path=str(test_file),
        )

        assert result is not None

    def test_handle_style_get_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to style_get handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_style_get(
            file_path=str(test_file),
            style_name="default",
        )

        assert result is not None

    def test_handle_style_create_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to style_create handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_style_create(
            file_path=str(test_file),
            style_name="test_style",
            properties='{"bold": true}',
        )

        assert result is not None

    def test_handle_style_update_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to style_update handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_style_update(
            file_path=str(test_file),
            style_name="test_style",
            properties='{"bold": false}',
        )

        assert result is not None

    def test_handle_style_delete_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to style_delete handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_style_delete(
            file_path=str(test_file),
            style_name="test_style",
        )

        assert result is not None

    def test_handle_style_apply_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to style_apply handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_style_apply(
            file_path=str(test_file),
            sheet="Sheet1",
            range="A1:B2",
            style_name="default",
        )

        assert result is not None

    def test_handle_format_cells_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to format_cells handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_format_cells(
            file_path=str(test_file),
            sheet="Sheet1",
            range="A1:B2",
            format="general",
        )

        assert result is not None

    def test_handle_format_number_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to format_number handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_format_number(
            file_path=str(test_file),
            sheet="Sheet1",
            range="A1:B2",
            format_code="#,##0.00",
        )

        assert result is not None

    def test_handle_format_font_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to format_font handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_format_font(
            file_path=str(test_file),
            sheet="Sheet1",
            range="A1:B2",
            font='{"name": "Arial", "size": 12}',
        )

        assert result is not None

    def test_handle_format_fill_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to format_fill handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_format_fill(
            file_path=str(test_file),
            sheet="Sheet1",
            range="A1:B2",
            color="#FF0000",
        )

        assert result is not None

    def test_handle_format_border_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to format_border handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_format_border(
            file_path=str(test_file),
            sheet="Sheet1",
            range="A1:B2",
            border='{"style": "thin", "color": "#000000"}',
        )

        assert result is not None

    def test_handle_row_insert_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to row_insert handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_row_insert(
            file_path=str(test_file),
            sheet="Sheet1",
            row=1,
            count=1,
        )

        assert result is not None

    def test_handle_row_delete_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to row_delete handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_row_delete(
            file_path=str(test_file),
            sheet="Sheet1",
            row=1,
            count=1,
        )

        assert result is not None

    def test_handle_row_hide_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to row_hide handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_row_hide(
            file_path=str(test_file),
            sheet="Sheet1",
            row=1,
            hidden=True,
        )

        assert result is not None

    def test_handle_column_insert_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to column_insert handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_column_insert(
            file_path=str(test_file),
            sheet="Sheet1",
            column="A",
            count=1,
        )

        assert result is not None

    def test_handle_column_delete_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to column_delete handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_column_delete(
            file_path=str(test_file),
            sheet="Sheet1",
            column="A",
            count=1,
        )

        assert result is not None

    def test_handle_column_hide_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to column_hide handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_column_hide(
            file_path=str(test_file),
            sheet="Sheet1",
            column="A",
            hidden=True,
        )

        assert result is not None

    def test_handle_freeze_set_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to freeze_set handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_freeze_set(
            file_path=str(test_file),
            sheet="Sheet1",
            cell="B2",
        )

        assert result is not None

    def test_handle_freeze_clear_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to freeze_clear handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_freeze_clear(
            file_path=str(test_file),
            sheet="Sheet1",
        )

        assert result is not None

    def test_handle_sheet_create_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to sheet_create handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_sheet_create(
            file_path=str(test_file),
            sheet="NewSheet",
        )

        assert result is not None

    def test_handle_sheet_delete_direct(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test direct call to sheet_delete handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_sheet_delete(
            file_path=str(test_file),
            sheet="Sheet1",
        )

        assert result is not None

    def test_handle_sheet_copy_direct(self, server: MCPServer, tmp_path: Path) -> None:
        """Test direct call to sheet_copy handler."""
        test_file = tmp_path / "test.ods"
        test_file.write_bytes(b"test")

        result = server._handle_sheet_copy(
            file_path=str(test_file),
            sheet="Sheet1",
            new_name="Sheet1_Copy",
        )

        assert result is not None


class TestMCPServerExceptionHandling:
    """Tests for exception handling in tool handlers."""

    @pytest.fixture
    def server(self, tmp_path: Path) -> MCPServer:
        """Create a test server."""
        config = MCPConfig(allowed_paths=[tmp_path])
        return MCPServer(config)

    def test_cell_handlers_with_invalid_path(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test cell handlers with invalid path return errors."""
        result = server._handle_cell_get(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            cell="A1",
        )
        assert result.is_error is True

        result = server._handle_cell_set(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            cell="A1",
            value="test",
        )
        assert result.is_error is True

        result = server._handle_cell_clear(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            cell="A1",
        )
        assert result.is_error is True

        result = server._handle_cell_copy(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            source="A1",
            destination="B1",
        )
        assert result.is_error is True

        result = server._handle_cell_move(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            source="A1",
            destination="B1",
        )
        assert result.is_error is True

        result = server._handle_cell_batch_get(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            cells="A1,B1",
        )
        assert result.is_error is True

        result = server._handle_cell_batch_set(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            updates='{"A1": "val"}',
        )
        assert result.is_error is True

        result = server._handle_cell_find(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            pattern="test",
        )
        assert result.is_error is True

        result = server._handle_cell_replace(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            find="old",
            replace="new",
        )
        assert result.is_error is True

        result = server._handle_cell_merge(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            range="A1:B2",
        )
        assert result.is_error is True

        result = server._handle_cell_unmerge(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            range="A1",
        )
        assert result.is_error is True

    def test_style_handlers_with_invalid_path(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test style handlers with invalid path return errors."""
        result = server._handle_style_list(file_path="/nonexistent/file.ods")
        assert result.is_error is True

        result = server._handle_style_get(
            file_path="/nonexistent/file.ods", style_name="default"
        )
        assert result.is_error is True

        result = server._handle_style_create(
            file_path="/nonexistent/file.ods",
            style_name="test",
            properties='{"bold": true}',
        )
        assert result.is_error is True

        result = server._handle_style_update(
            file_path="/nonexistent/file.ods",
            style_name="test",
            properties='{"bold": false}',
        )
        assert result.is_error is True

        result = server._handle_style_delete(
            file_path="/nonexistent/file.ods", style_name="test"
        )
        assert result.is_error is True

        result = server._handle_style_apply(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            range="A1:B2",
            style_name="default",
        )
        assert result.is_error is True

        result = server._handle_format_cells(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            range="A1:B2",
            format="general",
        )
        assert result.is_error is True

        result = server._handle_format_number(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            range="A1:B2",
            format_code="#,##0.00",
        )
        assert result.is_error is True

        result = server._handle_format_font(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            range="A1:B2",
            font='{"name": "Arial"}',
        )
        assert result.is_error is True

        result = server._handle_format_fill(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            range="A1:B2",
            color="#FF0000",
        )
        assert result.is_error is True

        result = server._handle_format_border(
            file_path="/nonexistent/file.ods",
            sheet="Sheet1",
            range="A1:B2",
            border='{"style": "thin"}',
        )
        assert result.is_error is True

    def test_structure_handlers_with_invalid_path(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test structure handlers with invalid path return errors."""
        result = server._handle_row_insert(
            file_path="/nonexistent/file.ods", sheet="Sheet1", row=1
        )
        assert result.is_error is True

        result = server._handle_row_delete(
            file_path="/nonexistent/file.ods", sheet="Sheet1", row=1
        )
        assert result.is_error is True

        result = server._handle_row_hide(
            file_path="/nonexistent/file.ods", sheet="Sheet1", row=1, hidden=True
        )
        assert result.is_error is True

        result = server._handle_column_insert(
            file_path="/nonexistent/file.ods", sheet="Sheet1", column="A"
        )
        assert result.is_error is True

        result = server._handle_column_delete(
            file_path="/nonexistent/file.ods", sheet="Sheet1", column="A"
        )
        assert result.is_error is True

        result = server._handle_column_hide(
            file_path="/nonexistent/file.ods", sheet="Sheet1", column="A", hidden=True
        )
        assert result.is_error is True

        result = server._handle_freeze_set(
            file_path="/nonexistent/file.ods", sheet="Sheet1", cell="B2"
        )
        assert result.is_error is True

        result = server._handle_freeze_clear(
            file_path="/nonexistent/file.ods", sheet="Sheet1"
        )
        assert result.is_error is True

        result = server._handle_sheet_create(
            file_path="/nonexistent/file.ods", sheet="NewSheet"
        )
        assert result.is_error is True

        result = server._handle_sheet_delete(
            file_path="/nonexistent/file.ods", sheet="Sheet1"
        )
        assert result.is_error is True

        result = server._handle_sheet_copy(
            file_path="/nonexistent/file.ods", sheet="Sheet1", new_name="Sheet1_Copy"
        )
        assert result.is_error is True

    def test_handle_message_exception_handling(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test handle_message exception handling."""
        # Trigger an exception by passing invalid message
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "cell_get",
                "arguments": {"invalid": "argument"},
            },
        }

        # This should not crash, should return error response
        response = server.handle_message(message)
        assert response is not None
        # Either error in response or isError in result
        assert "error" in response or response.get("result", {}).get("isError") is True
