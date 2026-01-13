"""Comprehensive tests for XLSX sparkline rendering.

Task 2.3: XLSX Sparkline Tests for SpreadsheetDL v4.1.0 pre-release audit.

Tests:
    - All sparkline types (line, column, win/loss)
    - Sparkline markers and customization options
    - Sparkline colors and styling
    - Multiple sparklines per sheet
    - Sparkline groups
    - Edge cases and error handling
"""

from __future__ import annotations

from pathlib import Path

import pytest

from spreadsheet_dl.builder import CellSpec, ColumnSpec, RowSpec, SheetSpec

pytestmark = [pytest.mark.unit, pytest.mark.rendering, pytest.mark.charts]


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sparkline_data_sheet() -> SheetSpec:
    """Create a sheet with data suitable for sparklines."""
    return SheetSpec(
        name="SparklineData",
        columns=[
            ColumnSpec(name="Category"),
            ColumnSpec(name="Q1"),
            ColumnSpec(name="Q2"),
            ColumnSpec(name="Q3"),
            ColumnSpec(name="Q4"),
            ColumnSpec(name="Trend"),
        ],
        rows=[
            RowSpec(
                cells=[
                    CellSpec(value="Category"),
                    CellSpec(value="Q1"),
                    CellSpec(value="Q2"),
                    CellSpec(value="Q3"),
                    CellSpec(value="Q4"),
                    CellSpec(value="Trend"),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Product A"),
                    CellSpec(value=100),
                    CellSpec(value=120),
                    CellSpec(value=110),
                    CellSpec(value=130),
                    CellSpec(value=""),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Product B"),
                    CellSpec(value=80),
                    CellSpec(value=90),
                    CellSpec(value=85),
                    CellSpec(value=95),
                    CellSpec(value=""),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Product C"),
                    CellSpec(value=150),
                    CellSpec(value=140),
                    CellSpec(value=160),
                    CellSpec(value=170),
                    CellSpec(value=""),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Product D"),
                    CellSpec(value=50),
                    CellSpec(value=60),
                    CellSpec(value=45),
                    CellSpec(value=70),
                    CellSpec(value=""),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Product E"),
                    CellSpec(value=200),
                    CellSpec(value=180),
                    CellSpec(value=190),
                    CellSpec(value=220),
                    CellSpec(value=""),
                ]
            ),
        ],
    )


@pytest.fixture
def win_loss_data_sheet() -> SheetSpec:
    """Create a sheet with positive/negative data for win/loss sparklines."""
    return SheetSpec(
        name="WinLossData",
        columns=[
            ColumnSpec(name="Team"),
            ColumnSpec(name="G1"),
            ColumnSpec(name="G2"),
            ColumnSpec(name="G3"),
            ColumnSpec(name="G4"),
            ColumnSpec(name="G5"),
            ColumnSpec(name="G6"),
            ColumnSpec(name="Record"),
        ],
        rows=[
            RowSpec(
                cells=[
                    CellSpec(value="Team"),
                    CellSpec(value="G1"),
                    CellSpec(value="G2"),
                    CellSpec(value="G3"),
                    CellSpec(value="G4"),
                    CellSpec(value="G5"),
                    CellSpec(value="G6"),
                    CellSpec(value="Record"),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Team A"),
                    CellSpec(value=1),
                    CellSpec(value=-1),
                    CellSpec(value=1),
                    CellSpec(value=1),
                    CellSpec(value=-1),
                    CellSpec(value=1),
                    CellSpec(value=""),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Team B"),
                    CellSpec(value=-1),
                    CellSpec(value=-1),
                    CellSpec(value=1),
                    CellSpec(value=-1),
                    CellSpec(value=1),
                    CellSpec(value=1),
                    CellSpec(value=""),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Team C"),
                    CellSpec(value=1),
                    CellSpec(value=1),
                    CellSpec(value=1),
                    CellSpec(value=-1),
                    CellSpec(value=1),
                    CellSpec(value=1),
                    CellSpec(value=""),
                ]
            ),
        ],
    )


@pytest.fixture
def time_series_sheet() -> SheetSpec:
    """Create a sheet with time series data for sparklines."""
    return SheetSpec(
        name="TimeSeries",
        columns=[
            ColumnSpec(name="Date"),
            ColumnSpec(name="Value1"),
            ColumnSpec(name="Value2"),
            ColumnSpec(name="Value3"),
        ],
        rows=[
            RowSpec(
                cells=[
                    CellSpec(value="Date"),
                    CellSpec(value="Series 1"),
                    CellSpec(value="Series 2"),
                    CellSpec(value="Series 3"),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="2024-01"),
                    CellSpec(value=10),
                    CellSpec(value=20),
                    CellSpec(value=15),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="2024-02"),
                    CellSpec(value=15),
                    CellSpec(value=18),
                    CellSpec(value=22),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="2024-03"),
                    CellSpec(value=12),
                    CellSpec(value=25),
                    CellSpec(value=19),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="2024-04"),
                    CellSpec(value=18),
                    CellSpec(value=22),
                    CellSpec(value=25),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="2024-05"),
                    CellSpec(value=20),
                    CellSpec(value=30),
                    CellSpec(value=28),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="2024-06"),
                    CellSpec(value=25),
                    CellSpec(value=28),
                    CellSpec(value=32),
                ]
            ),
        ],
    )


# =============================================================================
# Line Sparkline Tests
# =============================================================================


class TestLineSparklines:
    """Test line sparkline rendering."""

    def test_basic_line_sparkline(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test rendering a basic line sparkline."""
        from openpyxl import load_workbook

        from spreadsheet_dl.charts import SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparkline = SparklineSpec(
            type=SparklineType.LINE,
            data_range="B2:E2",
            location="F2",
        )

        output_path = tmp_path / "basic_line_sparkline.xlsx"
        renderer = XlsxRenderer()
        renderer.render([sparkline_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()
        wb = load_workbook(output_path)
        wb.close()

    def test_line_sparkline_multiple_rows(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test line sparklines for multiple data rows."""
        from spreadsheet_dl.charts import SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparklines = [
            SparklineSpec(
                type=SparklineType.LINE,
                data_range=f"B{row}:E{row}",
                location=f"F{row}",
            )
            for row in range(2, 7)  # Rows 2-6
        ]

        output_path = tmp_path / "multiple_line_sparklines.xlsx"
        renderer = XlsxRenderer()
        renderer.render([sparkline_data_sheet], output_path, sparklines=sparklines)

        assert output_path.exists()

    def test_line_sparkline_with_all_markers(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test line sparkline with all marker types enabled."""
        from spreadsheet_dl.charts import SparklineMarkers, SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparkline = SparklineSpec(
            type=SparklineType.LINE,
            data_range="B2:E2",
            location="F2",
            markers=SparklineMarkers(
                high=True,
                low=True,
                first=True,
                last=True,
                negative=True,
            ),
        )

        output_path = tmp_path / "line_all_markers.xlsx"
        renderer = XlsxRenderer()
        renderer.render([sparkline_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()

    def test_line_sparkline_high_low_only(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test line sparkline with only high/low markers."""
        from spreadsheet_dl.charts import SparklineMarkers, SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparkline = SparklineSpec(
            type=SparklineType.LINE,
            data_range="B3:E3",
            location="F3",
            markers=SparklineMarkers(
                high=True,
                low=True,
            ),
        )

        output_path = tmp_path / "line_high_low_markers.xlsx"
        renderer = XlsxRenderer()
        renderer.render([sparkline_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()

    def test_line_sparkline_first_last_only(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test line sparkline with only first/last markers."""
        from spreadsheet_dl.charts import SparklineMarkers, SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparkline = SparklineSpec(
            type=SparklineType.LINE,
            data_range="B4:E4",
            location="F4",
            markers=SparklineMarkers(
                first=True,
                last=True,
            ),
        )

        output_path = tmp_path / "line_first_last_markers.xlsx"
        renderer = XlsxRenderer()
        renderer.render([sparkline_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()


# =============================================================================
# Column Sparkline Tests
# =============================================================================


class TestColumnSparklines:
    """Test column sparkline rendering."""

    def test_basic_column_sparkline(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test rendering a basic column sparkline."""
        from spreadsheet_dl.charts import SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparkline = SparklineSpec(
            type=SparklineType.COLUMN,
            data_range="B2:E2",
            location="F2",
        )

        output_path = tmp_path / "basic_column_sparkline.xlsx"
        renderer = XlsxRenderer()
        renderer.render([sparkline_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()

    def test_column_sparkline_multiple_rows(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test column sparklines for multiple data rows."""
        from spreadsheet_dl.charts import SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparklines = [
            SparklineSpec(
                type=SparklineType.COLUMN,
                data_range=f"B{row}:E{row}",
                location=f"F{row}",
            )
            for row in range(2, 7)
        ]

        output_path = tmp_path / "multiple_column_sparklines.xlsx"
        renderer = XlsxRenderer()
        renderer.render([sparkline_data_sheet], output_path, sparklines=sparklines)

        assert output_path.exists()

    def test_column_sparkline_with_high_marker(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test column sparkline highlighting highest value."""
        from spreadsheet_dl.charts import SparklineMarkers, SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparkline = SparklineSpec(
            type=SparklineType.COLUMN,
            data_range="B5:E5",
            location="F5",
            markers=SparklineMarkers(high=True),
        )

        output_path = tmp_path / "column_high_marker.xlsx"
        renderer = XlsxRenderer()
        renderer.render([sparkline_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()

    def test_column_sparkline_with_low_marker(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test column sparkline highlighting lowest value."""
        from spreadsheet_dl.charts import SparklineMarkers, SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparkline = SparklineSpec(
            type=SparklineType.COLUMN,
            data_range="B6:E6",
            location="F6",
            markers=SparklineMarkers(low=True),
        )

        output_path = tmp_path / "column_low_marker.xlsx"
        renderer = XlsxRenderer()
        renderer.render([sparkline_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()


# =============================================================================
# Win/Loss Sparkline Tests
# =============================================================================


class TestWinLossSparklines:
    """Test win/loss sparkline rendering."""

    def test_basic_winloss_sparkline(
        self, win_loss_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test rendering a basic win/loss sparkline."""
        from spreadsheet_dl.charts import SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparkline = SparklineSpec(
            type=SparklineType.WIN_LOSS,
            data_range="B2:G2",
            location="H2",
        )

        output_path = tmp_path / "basic_winloss_sparkline.xlsx"
        renderer = XlsxRenderer()
        renderer.render([win_loss_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()

    def test_winloss_multiple_teams(
        self, win_loss_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test win/loss sparklines for multiple teams."""
        from spreadsheet_dl.charts import SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparklines = [
            SparklineSpec(
                type=SparklineType.WIN_LOSS,
                data_range=f"B{row}:G{row}",
                location=f"H{row}",
            )
            for row in range(2, 5)  # Rows 2-4
        ]

        output_path = tmp_path / "multiple_winloss_sparklines.xlsx"
        renderer = XlsxRenderer()
        renderer.render([win_loss_data_sheet], output_path, sparklines=sparklines)

        assert output_path.exists()

    def test_winloss_with_negative_marker(
        self, win_loss_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test win/loss sparkline with negative value markers."""
        from spreadsheet_dl.charts import SparklineMarkers, SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparkline = SparklineSpec(
            type=SparklineType.WIN_LOSS,
            data_range="B3:G3",
            location="H3",
            markers=SparklineMarkers(negative=True),
        )

        output_path = tmp_path / "winloss_negative_marker.xlsx"
        renderer = XlsxRenderer()
        renderer.render([win_loss_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()


# =============================================================================
# Sparkline Color Tests
# =============================================================================


class TestSparklineColors:
    """Test sparkline color customization."""

    def test_sparkline_with_series_color(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test sparkline with custom series color."""
        from spreadsheet_dl.charts import SparklineColors, SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparkline = SparklineSpec(
            type=SparklineType.LINE,
            data_range="B2:E2",
            location="F2",
            colors=SparklineColors(series="#3366CC"),
        )

        output_path = tmp_path / "sparkline_series_color.xlsx"
        renderer = XlsxRenderer()
        renderer.render([sparkline_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()

    def test_sparkline_with_marker_colors(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test sparkline with custom marker colors."""
        from spreadsheet_dl.charts import (
            SparklineColors,
            SparklineMarkers,
            SparklineSpec,
            SparklineType,
        )
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparkline = SparklineSpec(
            type=SparklineType.LINE,
            data_range="B3:E3",
            location="F3",
            markers=SparklineMarkers(high=True, low=True),
            colors=SparklineColors(
                series="#336699",
                high="#00FF00",
                low="#FF0000",
            ),
        )

        output_path = tmp_path / "sparkline_marker_colors.xlsx"
        renderer = XlsxRenderer()
        renderer.render([sparkline_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()

    def test_column_sparkline_with_colors(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test column sparkline with custom colors."""
        from spreadsheet_dl.charts import (
            SparklineColors,
            SparklineMarkers,
            SparklineSpec,
            SparklineType,
        )
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparkline = SparklineSpec(
            type=SparklineType.COLUMN,
            data_range="B4:E4",
            location="F4",
            markers=SparklineMarkers(high=True, low=True, first=True, last=True),
            colors=SparklineColors(
                series="#4472C4",
                high="#70AD47",
                low="#C00000",
                first="#FFC000",
                last="#7030A0",
            ),
        )

        output_path = tmp_path / "column_sparkline_colors.xlsx"
        renderer = XlsxRenderer()
        renderer.render([sparkline_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()

    def test_winloss_sparkline_with_colors(
        self, win_loss_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test win/loss sparkline with custom positive/negative colors."""
        from spreadsheet_dl.charts import SparklineColors, SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparkline = SparklineSpec(
            type=SparklineType.WIN_LOSS,
            data_range="B2:G2",
            location="H2",
            colors=SparklineColors(
                series="#00AA00",  # Wins
                negative="#AA0000",  # Losses
            ),
        )

        output_path = tmp_path / "winloss_custom_colors.xlsx"
        renderer = XlsxRenderer()
        renderer.render([win_loss_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()


# =============================================================================
# Sparkline Group Tests
# =============================================================================


class TestSparklineGroups:
    """Test sparkline grouping functionality."""

    def test_sparkline_group_same_type(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test multiple sparklines of same type rendered together."""
        from spreadsheet_dl.charts import SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparklines = [
            SparklineSpec(
                type=SparklineType.LINE,
                data_range=f"B{row}:E{row}",
                location=f"F{row}",
            )
            for row in range(2, 7)
        ]

        output_path = tmp_path / "sparkline_group.xlsx"
        renderer = XlsxRenderer()
        renderer.render([sparkline_data_sheet], output_path, sparklines=sparklines)

        assert output_path.exists()

    def test_mixed_sparkline_types(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test mixing different sparkline types on same sheet."""
        from spreadsheet_dl.charts import SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparklines = [
            SparklineSpec(
                type=SparklineType.LINE,
                data_range="B2:E2",
                location="F2",
            ),
            SparklineSpec(
                type=SparklineType.COLUMN,
                data_range="B3:E3",
                location="F3",
            ),
            SparklineSpec(
                type=SparklineType.LINE,
                data_range="B4:E4",
                location="F4",
            ),
            SparklineSpec(
                type=SparklineType.COLUMN,
                data_range="B5:E5",
                location="F5",
            ),
        ]

        output_path = tmp_path / "mixed_sparklines.xlsx"
        renderer = XlsxRenderer()
        renderer.render([sparkline_data_sheet], output_path, sparklines=sparklines)

        assert output_path.exists()


# =============================================================================
# Time Series Sparkline Tests
# =============================================================================


class TestTimeSeriesSparklines:
    """Test sparklines with time series data."""

    def test_monthly_trend_sparkline(
        self, time_series_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test sparkline showing monthly trend."""
        from spreadsheet_dl.charts import SparklineMarkers, SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparkline = SparklineSpec(
            type=SparklineType.LINE,
            data_range="B2:B7",
            location="E2",
            markers=SparklineMarkers(first=True, last=True),
        )

        output_path = tmp_path / "monthly_trend_sparkline.xlsx"
        renderer = XlsxRenderer()
        renderer.render([time_series_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()

    def test_comparison_sparklines(
        self, time_series_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test sparklines comparing multiple time series."""
        from spreadsheet_dl.charts import SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        sparklines = [
            SparklineSpec(
                type=SparklineType.LINE,
                data_range=f"{col}2:{col}7",
                location=f"E{idx + 2}",
            )
            for idx, col in enumerate(["B", "C", "D"])
        ]

        output_path = tmp_path / "comparison_sparklines.xlsx"
        renderer = XlsxRenderer()
        renderer.render([time_series_sheet], output_path, sparklines=sparklines)

        assert output_path.exists()


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


class TestSparklineEdgeCases:
    """Test sparkline edge cases and error handling."""

    def test_sparkline_single_data_point(self, tmp_path: Path) -> None:
        """Test sparkline with only one data point."""
        from spreadsheet_dl.charts import SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        single_point_sheet = SheetSpec(
            name="SinglePoint",
            columns=[ColumnSpec(name="A"), ColumnSpec(name="B")],
            rows=[
                RowSpec(cells=[CellSpec(value="Label"), CellSpec(value="Value")]),
                RowSpec(cells=[CellSpec(value="Test"), CellSpec(value=100)]),
            ],
        )

        sparkline = SparklineSpec(
            type=SparklineType.LINE,
            data_range="B2",
            location="C2",
        )

        output_path = tmp_path / "single_point_sparkline.xlsx"
        renderer = XlsxRenderer()
        renderer.render([single_point_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()

    def test_sparkline_with_zeros(self, tmp_path: Path) -> None:
        """Test sparkline with zero values."""
        from spreadsheet_dl.charts import SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        zero_data_sheet = SheetSpec(
            name="ZeroData",
            columns=[
                ColumnSpec(name="A"),
                ColumnSpec(name="B"),
                ColumnSpec(name="C"),
                ColumnSpec(name="D"),
            ],
            rows=[
                RowSpec(
                    cells=[
                        CellSpec(value="Label"),
                        CellSpec(value="V1"),
                        CellSpec(value="V2"),
                        CellSpec(value="V3"),
                    ]
                ),
                RowSpec(
                    cells=[
                        CellSpec(value="Test"),
                        CellSpec(value=0),
                        CellSpec(value=0),
                        CellSpec(value=0),
                    ]
                ),
            ],
        )

        sparkline = SparklineSpec(
            type=SparklineType.COLUMN,
            data_range="B2:D2",
            location="E2",
        )

        output_path = tmp_path / "zero_sparkline.xlsx"
        renderer = XlsxRenderer()
        renderer.render([zero_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()

    def test_sparkline_with_negative_values(self, tmp_path: Path) -> None:
        """Test sparkline with negative values."""
        from spreadsheet_dl.charts import SparklineMarkers, SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        negative_data_sheet = SheetSpec(
            name="NegativeData",
            columns=[
                ColumnSpec(name="A"),
                ColumnSpec(name="B"),
                ColumnSpec(name="C"),
                ColumnSpec(name="D"),
                ColumnSpec(name="E"),
            ],
            rows=[
                RowSpec(
                    cells=[
                        CellSpec(value="Item"),
                        CellSpec(value="Q1"),
                        CellSpec(value="Q2"),
                        CellSpec(value="Q3"),
                        CellSpec(value="Q4"),
                    ]
                ),
                RowSpec(
                    cells=[
                        CellSpec(value="Profit/Loss"),
                        CellSpec(value=100),
                        CellSpec(value=-50),
                        CellSpec(value=75),
                        CellSpec(value=-25),
                    ]
                ),
            ],
        )

        sparkline = SparklineSpec(
            type=SparklineType.COLUMN,
            data_range="B2:E2",
            location="F2",
            markers=SparklineMarkers(negative=True),
        )

        output_path = tmp_path / "negative_sparkline.xlsx"
        renderer = XlsxRenderer()
        renderer.render([negative_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()

    def test_sparkline_large_dataset(self, tmp_path: Path) -> None:
        """Test sparkline with larger number of data points."""
        from spreadsheet_dl.charts import SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        # Create sheet with 50 data points
        columns = [ColumnSpec(name="Label")] + [
            ColumnSpec(name=f"D{i}") for i in range(1, 51)
        ]
        header_cells = [CellSpec(value="Header")] + [
            CellSpec(value=f"V{i}") for i in range(1, 51)
        ]
        data_cells = [CellSpec(value="Data")] + [
            CellSpec(value=i * 10 % 100 + (i % 7) * 5) for i in range(1, 51)
        ]

        large_data_sheet = SheetSpec(
            name="LargeData",
            columns=columns,
            rows=[
                RowSpec(cells=header_cells),
                RowSpec(cells=data_cells),
            ],
        )

        sparkline = SparklineSpec(
            type=SparklineType.LINE,
            data_range="B2:AY2",
            location="AZ2",
        )

        output_path = tmp_path / "large_sparkline.xlsx"
        renderer = XlsxRenderer()
        renderer.render([large_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()

    def test_sparkline_empty_data_range(self, tmp_path: Path) -> None:
        """Test sparkline with empty data range."""
        from spreadsheet_dl.charts import SparklineSpec, SparklineType
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        empty_data_sheet = SheetSpec(
            name="EmptyData",
            columns=[ColumnSpec(name="A")],
            rows=[RowSpec(cells=[CellSpec(value="")])],
        )

        sparkline = SparklineSpec(
            type=SparklineType.LINE,
            data_range="A1:D1",
            location="E1",
        )

        output_path = tmp_path / "empty_sparkline.xlsx"
        renderer = XlsxRenderer()
        # Should handle gracefully without crashing
        renderer.render([empty_data_sheet], output_path, sparklines=[sparkline])

        assert output_path.exists()


# =============================================================================
# Combined Chart and Sparkline Tests
# =============================================================================


class TestCombinedChartSparkline:
    """Test charts and sparklines on same sheet."""

    def test_chart_and_sparklines_together(
        self, sparkline_data_sheet: SheetSpec, tmp_path: Path
    ) -> None:
        """Test rendering both charts and sparklines on same sheet."""
        from spreadsheet_dl.charts import (
            ChartSpec,
            ChartType,
            DataRange,
            SparklineSpec,
            SparklineType,
        )
        from spreadsheet_dl.xlsx_renderer import XlsxRenderer

        chart = ChartSpec(
            type=ChartType.COLUMN,
            title="Quarterly Sales",
            data=DataRange(
                categories="A2:A6",
                values="B2:B6",
            ),
            position="H2",
        )

        sparklines = [
            SparklineSpec(
                type=SparklineType.LINE,
                data_range=f"B{row}:E{row}",
                location=f"F{row}",
            )
            for row in range(2, 7)
        ]

        output_path = tmp_path / "chart_with_sparklines.xlsx"
        renderer = XlsxRenderer()
        renderer.render(
            [sparkline_data_sheet], output_path, charts=[chart], sparklines=sparklines
        )

        assert output_path.exists()
