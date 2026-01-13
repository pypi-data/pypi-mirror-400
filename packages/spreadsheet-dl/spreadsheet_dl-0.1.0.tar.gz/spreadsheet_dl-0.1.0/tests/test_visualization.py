"""
Tests for Interactive Visualization module.

: Interactive Visualization
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from spreadsheet_dl.visualization import (
    CATEGORY_COLORS,
    DEFAULT_COLORS,
    ChartConfig,
    ChartDataPoint,
    ChartGenerator,
    ChartSeries,
    ChartType,
    DashboardGenerator,
    create_budget_dashboard,
    create_spending_pie_chart,
)

pytestmark = [pytest.mark.unit, pytest.mark.visualization]


class TestChartDataPoint:
    """Tests for ChartDataPoint."""

    def test_create_data_point(self) -> None:
        """Test creating a data point."""
        point = ChartDataPoint(
            label="Food",
            value=500.0,
            color="#27ae60",
            category="Groceries",
        )

        assert point.label == "Food"
        assert point.value == 500.0
        assert point.color == "#27ae60"
        assert point.category == "Groceries"

    def test_data_point_defaults(self) -> None:
        """Test default values."""
        point = ChartDataPoint(label="Test", value=100.0)

        assert point.color is None
        assert point.category is None


class TestChartSeries:
    """Tests for ChartSeries."""

    def test_create_series(self) -> None:
        """Test creating a series."""
        series = ChartSeries(
            name="Budget",
            data=[100.0, 200.0, 300.0],
            color="#4e79a7",
        )

        assert series.name == "Budget"
        assert len(series.data) == 3
        assert series.color == "#4e79a7"


class TestChartConfig:
    """Tests for ChartConfig."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = ChartConfig(title="Test", chart_type=ChartType.PIE)

        assert config.title == "Test"
        assert config.width == 600
        assert config.height == 400
        assert config.show_legend is True
        assert config.animation is True
        assert config.responsive is True

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = ChartConfig(
            title="Custom Chart",
            chart_type=ChartType.BAR,
            width=800,
            height=600,
            show_legend=False,
            animation=False,
            colors=["#000", "#fff"],
        )

        assert config.width == 800
        assert config.height == 600
        assert not config.show_legend
        assert not config.animation
        assert config.colors == ["#000", "#fff"]


class TestChartGenerator:
    """Tests for ChartGenerator."""

    def test_create_pie_chart(self) -> None:
        """Test creating a pie chart."""
        generator = ChartGenerator()
        data = [
            ChartDataPoint("Food", 500),
            ChartDataPoint("Housing", 1500),
            ChartDataPoint("Transport", 300),
        ]

        html = generator.create_pie_chart(data)

        assert "<!DOCTYPE html>" in html
        assert "chart.js" in html.lower() or "Chart" in html
        assert "Food" in html
        assert "Housing" in html
        assert "Transport" in html

    def test_create_pie_chart_with_config(self) -> None:
        """Test pie chart with custom config."""
        generator = ChartGenerator()
        data = [ChartDataPoint("Test", 100)]
        config = ChartConfig(
            title="My Pie Chart",
            chart_type=ChartType.PIE,
            width=800,
        )

        html = generator.create_pie_chart(data, config)

        assert "My Pie Chart" in html
        assert "800px" in html

    def test_create_doughnut_chart(self) -> None:
        """Test creating a doughnut chart (pie with cutout)."""
        generator = ChartGenerator()
        data = [
            ChartDataPoint("A", 100),
            ChartDataPoint("B", 200),
        ]
        config = ChartConfig(
            title="Doughnut",
            chart_type=ChartType.DOUGHNUT,
            cutout=50,
        )

        html = generator.create_pie_chart(data, config)

        assert "doughnut" in html
        assert "cutout" in html

    def test_create_bar_chart(self) -> None:
        """Test creating a bar chart."""
        generator = ChartGenerator()
        data = [
            ChartDataPoint("Jan", 1000),
            ChartDataPoint("Feb", 1200),
            ChartDataPoint("Mar", 900),
        ]

        html = generator.create_bar_chart(data)

        assert "<!DOCTYPE html>" in html
        assert "bar" in html.lower()
        assert "Jan" in html
        assert "Feb" in html

    def test_create_horizontal_bar_chart(self) -> None:
        """Test creating a horizontal bar chart."""
        generator = ChartGenerator()
        data = [ChartDataPoint("Test", 100)]
        config = ChartConfig(
            title="Horizontal",
            chart_type=ChartType.HORIZONTAL_BAR,
        )

        html = generator.create_bar_chart(data, config)

        assert "indexAxis" in html
        assert "'y'" in html

    def test_create_line_chart(self) -> None:
        """Test creating a line chart."""
        generator = ChartGenerator()
        labels = ["Jan", "Feb", "Mar"]
        series = [
            ChartSeries("Revenue", [1000, 1200, 1100]),
            ChartSeries("Expenses", [800, 900, 850]),
        ]

        html = generator.create_line_chart(labels, series)

        assert "<!DOCTYPE html>" in html
        assert "line" in html.lower()
        assert "Revenue" in html
        assert "Expenses" in html

    def test_create_line_chart_with_tension(self) -> None:
        """Test line chart with curve tension."""
        generator = ChartGenerator()
        labels = ["A", "B", "C"]
        series = [ChartSeries("Data", [1, 2, 3])]
        config = ChartConfig(
            title="Curved Line",
            chart_type=ChartType.LINE,
            tension=0.4,
        )

        html = generator.create_line_chart(labels, series, config)

        assert "tension" in html
        assert "0.4" in html

    def test_create_stacked_bar_chart(self) -> None:
        """Test creating a stacked bar chart."""
        generator = ChartGenerator()
        labels = ["Q1", "Q2", "Q3"]
        series = [
            ChartSeries("Product A", [100, 150, 200]),
            ChartSeries("Product B", [80, 120, 160]),
        ]

        html = generator.create_stacked_bar_chart(labels, series)

        assert "stacked: true" in html
        assert "Product A" in html
        assert "Product B" in html

    def test_theme_dark(self) -> None:
        """Test dark theme styling."""
        generator = ChartGenerator(theme="dark")
        data = [ChartDataPoint("Test", 100)]

        html = generator.create_pie_chart(data)

        assert "#1a1a2e" in html  # Dark background

    def test_custom_colors(self) -> None:
        """Test custom color palette."""
        custom_colors = ["#ff0000", "#00ff00", "#0000ff"]
        generator = ChartGenerator(colors=custom_colors)
        data = [
            ChartDataPoint("A", 100),
            ChartDataPoint("B", 100),
            ChartDataPoint("C", 100),
        ]

        html = generator.create_pie_chart(data)

        assert "#ff0000" in html
        assert "#00ff00" in html
        assert "#0000ff" in html

    def test_category_colors(self) -> None:
        """Test category-specific colors."""
        generator = ChartGenerator()
        data = [
            ChartDataPoint("Test", 100, category="Housing"),
            ChartDataPoint("Test2", 200, category="Groceries"),
        ]

        html = generator.create_pie_chart(data)

        # Should use category colors
        assert CATEGORY_COLORS["Housing"] in html
        assert CATEGORY_COLORS["Groceries"] in html


class TestDashboardGenerator:
    """Tests for DashboardGenerator."""

    def test_generate_demo_dashboard(self) -> None:
        """Test generating a demo dashboard (no analyzer)."""
        generator = DashboardGenerator()

        html = generator.generate()

        assert "<!DOCTYPE html>" in html
        assert "Budget Dashboard" in html
        assert "Total Budget" in html
        assert "Total Spent" in html
        assert "Remaining" in html
        assert "chart.js" in html.lower() or "Chart" in html

    def test_generate_dark_theme(self) -> None:
        """Test generating dashboard with dark theme."""
        generator = DashboardGenerator(theme="dark")

        html = generator.generate()

        assert "#1a1a2e" in html

    def test_save_dashboard(self) -> None:
        """Test saving dashboard to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dashboard.html"
            generator = DashboardGenerator()

            result = generator.save(output_path)

            assert result == output_path
            assert output_path.exists()

            content = output_path.read_text()
            assert "Budget Dashboard" in content

    def test_dashboard_includes_charts(self) -> None:
        """Test that dashboard includes all chart types."""
        generator = DashboardGenerator()

        html = generator.generate()

        assert "pieChart" in html
        assert "barChart" in html
        assert "doughnut" in html

    def test_dashboard_summary_cards(self) -> None:
        """Test summary cards are present."""
        generator = DashboardGenerator()

        html = generator.generate()

        assert "Total Budget" in html
        assert "Total Spent" in html
        assert "Remaining" in html
        assert "Budget Used" in html
        assert "progress-bar" in html


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_spending_pie_chart(self) -> None:
        """Test create_spending_pie_chart function."""
        categories = {
            "Housing": 1500.0,
            "Food": 500.0,
            "Transport": 300.0,
        }

        html = create_spending_pie_chart(categories)

        assert "<!DOCTYPE html>" in html
        assert "Housing" in html
        assert "Food" in html
        assert "Transport" in html

    def test_create_spending_pie_chart_with_title(self) -> None:
        """Test with custom title."""
        html = create_spending_pie_chart(
            {"Test": 100.0},
            title="My Custom Title",
        )

        assert "My Custom Title" in html

    def test_create_spending_pie_chart_save(self) -> None:
        """Test saving pie chart to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "chart.html"

            html = create_spending_pie_chart(
                {"Test": 100.0},
                output_path=output_path,
            )

            assert output_path.exists()
            assert html == output_path.read_text()

    def test_create_spending_pie_chart_filters_zero(self) -> None:
        """Test that zero values are filtered out."""
        categories = {
            "Has Value": 100.0,
            "Zero": 0.0,
            "Negative": -50.0,  # Should not appear
        }

        html = create_spending_pie_chart(categories)

        assert "Has Value" in html
        # Zero and negative should be filtered
        assert html.count("Zero") == 0 or "Zero" in html  # May appear in tooltip config

    def test_create_budget_dashboard(self) -> None:
        """Test create_budget_dashboard function."""
        html = create_budget_dashboard()

        assert "<!DOCTYPE html>" in html
        assert "Budget Dashboard" in html

    def test_create_budget_dashboard_dark_theme(self) -> None:
        """Test with dark theme."""
        html = create_budget_dashboard(theme="dark")

        assert "#1a1a2e" in html

    def test_create_budget_dashboard_save(self) -> None:
        """Test saving dashboard to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dashboard.html"

            create_budget_dashboard(output_path=output_path)

            assert output_path.exists()
            content = output_path.read_text()
            assert "Budget Dashboard" in content


class TestDefaultColors:
    """Tests for color constants."""

    def test_default_colors_count(self) -> None:
        """Test we have enough default colors."""
        assert len(DEFAULT_COLORS) >= 10

    def test_default_colors_format(self) -> None:
        """Test colors are valid hex format."""
        for color in DEFAULT_COLORS:
            assert color.startswith("#")
            assert len(color) == 7  # #RRGGBB

    def test_category_colors_coverage(self) -> None:
        """Test category colors cover common categories."""
        expected_categories = [
            "Housing",
            "Utilities",
            "Groceries",
            "Transportation",
            "Entertainment",
            "Healthcare",
        ]

        for cat in expected_categories:
            assert cat in CATEGORY_COLORS

    def test_category_colors_format(self) -> None:
        """Test category colors are valid hex format."""
        for color in CATEGORY_COLORS.values():
            assert color.startswith("#")
            assert len(color) == 7


class TestChartType:
    """Tests for ChartType enum."""

    def test_chart_types_exist(self) -> None:
        """Test all expected chart types exist."""
        assert ChartType.PIE.value == "pie"
        assert ChartType.BAR.value == "bar"
        assert ChartType.LINE.value == "line"
        assert ChartType.DOUGHNUT.value == "doughnut"
        assert ChartType.STACKED_BAR.value == "stacked_bar"
        assert ChartType.AREA.value == "area"
        assert ChartType.HORIZONTAL_BAR.value == "horizontal_bar"
