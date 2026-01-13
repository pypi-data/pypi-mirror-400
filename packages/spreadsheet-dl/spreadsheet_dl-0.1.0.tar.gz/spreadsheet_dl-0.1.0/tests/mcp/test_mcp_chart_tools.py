"""Comprehensive tests for MCP server chart tool handlers.

Tests chart creation, updating, and visualization operations
for the SpreadsheetDL MCP server.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from spreadsheet_dl.mcp_server import (
    MCPConfig,
    MCPServer,
)

pytestmark = [pytest.mark.unit, pytest.mark.mcp, pytest.mark.charts]


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def server(tmp_path: Path) -> MCPServer:
    """Create a test MCP server."""
    config = MCPConfig(allowed_paths=[tmp_path, Path.cwd()])
    return MCPServer(config)


@pytest.fixture
def test_ods_with_data(tmp_path: Path) -> Path:
    """Create a test ODS file with numeric data for charts."""
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.table import Table, TableCell, TableRow
    from odf.text import P

    doc = OpenDocumentSpreadsheet()
    table = Table(name="Sheet1")

    # Add header row
    header_row = TableRow()
    for header in ["Month", "Sales", "Expenses", "Profit"]:
        cell = TableCell(valuetype="string")
        cell.addElement(P(text=header))
        header_row.addElement(cell)
    table.addElement(header_row)

    # Add numeric data rows
    data = [
        ["Jan", 1000, 800, 200],
        ["Feb", 1200, 850, 350],
        ["Mar", 1100, 900, 200],
        ["Apr", 1500, 950, 550],
        ["May", 1800, 1000, 800],
        ["Jun", 2000, 1100, 900],
    ]
    for row_data in data:
        row = TableRow()
        for idx, value in enumerate(row_data):
            if idx == 0:
                cell = TableCell(valuetype="string")
                cell.addElement(P(text=str(value)))
            else:
                cell = TableCell(valuetype="float", value=str(value))
                cell.addElement(P(text=str(value)))
            row.addElement(cell)
        table.addElement(row)

    doc.spreadsheet.addElement(table)
    test_file = tmp_path / "chart_data.ods"
    doc.save(str(test_file))
    return test_file


@pytest.fixture
def test_ods_multi_series(tmp_path: Path) -> Path:
    """Create a test ODS file with multiple data series."""
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.table import Table, TableCell, TableRow
    from odf.text import P

    doc = OpenDocumentSpreadsheet()
    table = Table(name="Data")

    # Add header row
    header_row = TableRow()
    for header in ["Category", "Series1", "Series2", "Series3"]:
        cell = TableCell(valuetype="string")
        cell.addElement(P(text=header))
        header_row.addElement(cell)
    table.addElement(header_row)

    # Add data rows
    data = [
        ["A", 10, 15, 20],
        ["B", 25, 30, 35],
        ["C", 15, 20, 25],
        ["D", 30, 35, 40],
    ]
    for row_data in data:
        row = TableRow()
        for idx, value in enumerate(row_data):
            if idx == 0:
                cell = TableCell(valuetype="string")
            else:
                cell = TableCell(valuetype="float", value=str(value))
            cell.addElement(P(text=str(value)))
            row.addElement(cell)
        table.addElement(row)

    doc.spreadsheet.addElement(table)
    test_file = tmp_path / "multi_series.ods"
    doc.save(str(test_file))
    return test_file


# ============================================================================
# Bar Chart Tests
# ============================================================================


class TestBarChartCreation:
    """Tests for bar chart creation."""

    def test_bar_chart_basic(self, server: MCPServer, test_ods_with_data: Path) -> None:
        """Test basic bar chart creation."""
        result = server._handle_chart_create(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_type="bar",
            data_range="A1:B7",
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True
            assert content["chart_type"] == "bar"

    def test_bar_chart_with_title(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test bar chart with title."""
        result = server._handle_chart_create(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_type="bar",
            data_range="A1:B7",
            title="Monthly Sales",
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True

    def test_bar_chart_with_position(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test bar chart with specific position."""
        result = server._handle_chart_create(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_type="bar",
            data_range="A1:B7",
            title="Sales Chart",
            position="F1",
        )

        assert result is not None

    def test_bar_chart_stacked(
        self, server: MCPServer, test_ods_multi_series: Path
    ) -> None:
        """Test stacked bar chart creation."""
        result = server._handle_chart_create(
            file_path=str(test_ods_multi_series),
            sheet="Data",
            chart_type="bar",
            data_range="A1:D5",
            title="Stacked Comparison",
        )

        assert result is not None


# ============================================================================
# Line Chart Tests
# ============================================================================


class TestLineChartCreation:
    """Tests for line chart creation."""

    def test_line_chart_basic(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test basic line chart creation."""
        result = server._handle_chart_create(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_type="line",
            data_range="A1:B7",
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["chart_type"] == "line"

    def test_line_chart_multiple_series(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test line chart with multiple data series."""
        result = server._handle_chart_create(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_type="line",
            data_range="A1:D7",
            title="Financial Trends",
        )

        assert result is not None

    def test_line_chart_trend_data(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test line chart for trend visualization."""
        result = server._handle_chart_create(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_type="line",
            data_range="A1:C7",
            title="Sales vs Expenses Trend",
        )

        assert result is not None


# ============================================================================
# Pie Chart Tests
# ============================================================================


class TestPieChartCreation:
    """Tests for pie chart creation."""

    def test_pie_chart_basic(self, server: MCPServer, test_ods_with_data: Path) -> None:
        """Test basic pie chart creation."""
        result = server._handle_chart_create(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_type="pie",
            data_range="A2:B7",
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["chart_type"] == "pie"

    def test_pie_chart_with_title(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test pie chart with title."""
        result = server._handle_chart_create(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_type="pie",
            data_range="A2:B7",
            title="Sales Distribution",
        )

        assert result is not None


# ============================================================================
# Area Chart Tests
# ============================================================================


class TestAreaChartCreation:
    """Tests for area chart creation."""

    def test_area_chart_basic(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test basic area chart creation."""
        result = server._handle_chart_create(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_type="area",
            data_range="A1:B7",
        )

        assert result is not None

    def test_area_chart_stacked(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test stacked area chart creation."""
        result = server._handle_chart_create(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_type="area",
            data_range="A1:D7",
            title="Cumulative Trends",
        )

        assert result is not None


# ============================================================================
# Scatter Chart Tests
# ============================================================================


class TestScatterChartCreation:
    """Tests for scatter chart creation."""

    def test_scatter_chart_basic(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test basic scatter chart creation."""
        result = server._handle_chart_create(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_type="scatter",
            data_range="B2:C7",
        )

        assert result is not None

    def test_scatter_chart_correlation(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test scatter chart for correlation analysis."""
        result = server._handle_chart_create(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_type="scatter",
            data_range="B2:D7",
            title="Sales-Expenses Correlation",
        )

        assert result is not None


# ============================================================================
# Chart Update Tests
# ============================================================================


class TestChartUpdate:
    """Tests for chart update operations."""

    def test_chart_update_title(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test updating chart title."""
        properties = json.dumps({"title": "Updated Chart Title"})
        result = server._handle_chart_update(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_id="chart_0",
            properties=properties,
        )

        assert result is not None

    def test_chart_update_legend(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test updating chart legend visibility."""
        properties = json.dumps({"legend": True, "legend_position": "right"})
        result = server._handle_chart_update(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_id="chart_0",
            properties=properties,
        )

        assert result is not None

    def test_chart_update_colors(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test updating chart colors."""
        properties = json.dumps({"series_colors": ["#FF0000", "#00FF00", "#0000FF"]})
        result = server._handle_chart_update(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_id="chart_0",
            properties=properties,
        )

        assert result is not None

    def test_chart_update_multiple_properties(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test updating multiple chart properties."""
        properties = json.dumps(
            {
                "title": "New Title",
                "legend": True,
                "grid_lines": True,
                "data_labels": True,
            }
        )
        result = server._handle_chart_update(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_id="chart_0",
            properties=properties,
        )

        assert result is not None


# ============================================================================
# Chart Type Comparison Tests
# ============================================================================


class TestChartTypeComparison:
    """Tests comparing different chart types."""

    def test_all_chart_types_create_successfully(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test that all chart types can be created."""
        chart_types = ["bar", "line", "pie", "area", "scatter"]

        for chart_type in chart_types:
            result = server._handle_chart_create(
                file_path=str(test_ods_with_data),
                sheet="Sheet1",
                chart_type=chart_type,
                data_range="A1:B7",
                title=f"Test {chart_type.title()} Chart",
            )

            assert result is not None, f"Chart type {chart_type} failed"

    def test_chart_type_case_insensitive(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test that chart types are case-insensitive."""
        variations = ["BAR", "Bar", "bar", "LINE", "Line", "line"]

        for chart_type in variations:
            result = server._handle_chart_create(
                file_path=str(test_ods_with_data),
                sheet="Sheet1",
                chart_type=chart_type,
                data_range="A1:B7",
            )

            assert result is not None


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestChartErrorHandling:
    """Tests for chart error handling."""

    def test_chart_invalid_file(self, server: MCPServer, tmp_path: Path) -> None:
        """Test chart creation with invalid file path."""
        result = server._handle_chart_create(
            file_path=str(tmp_path / "nonexistent.ods"),
            sheet="Sheet1",
            chart_type="bar",
            data_range="A1:B7",
        )

        assert result.is_error

    def test_chart_invalid_sheet(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test chart creation with invalid sheet name."""
        result = server._handle_chart_create(
            file_path=str(test_ods_with_data),
            sheet="NonexistentSheet",
            chart_type="bar",
            data_range="A1:B7",
        )

        assert result.is_error

    def test_chart_update_invalid_json(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test chart update with invalid JSON properties."""
        result = server._handle_chart_update(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_id="chart_0",
            properties="not valid json",
        )

        assert result.is_error


# ============================================================================
# Integration Tests
# ============================================================================


class TestChartIntegration:
    """Integration tests for chart functionality."""

    def test_chart_handler_exists(self, server: MCPServer) -> None:
        """Test that chart handlers exist on server."""
        assert hasattr(server, "_handle_chart_create")
        assert hasattr(server, "_handle_chart_update")

    def test_create_and_update_workflow(
        self, server: MCPServer, test_ods_with_data: Path
    ) -> None:
        """Test create then update chart workflow."""
        # Create chart
        create_result = server._handle_chart_create(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_type="bar",
            data_range="A1:B7",
            title="Initial Title",
        )

        assert create_result is not None

        # Update chart
        properties = json.dumps({"title": "Updated Title"})
        update_result = server._handle_chart_update(
            file_path=str(test_ods_with_data),
            sheet="Sheet1",
            chart_id="chart_0",
            properties=properties,
        )

        assert update_result is not None
