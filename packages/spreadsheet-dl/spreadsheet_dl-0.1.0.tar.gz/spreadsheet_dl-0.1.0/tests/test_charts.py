"""
Tests for charts module.

Implements tests for:
"""

import pytest

from spreadsheet_dl.charts import (
    AxisConfig,
    AxisType,
    ChartBuilder,
    ChartPosition,
    ChartSize,
    ChartSpec,
    ChartTitle,
    ChartType,
    DataLabelConfig,
    DataLabelPosition,
    DataSeries,
    LegendConfig,
    LegendPosition,
    PlotAreaStyle,
    Sparkline,
    SparklineBuilder,
    SparklineMarkers,
    SparklineType,
    Trendline,
    TrendlineType,
    budget_comparison_chart,
    chart,
    sparkline,
    spending_pie_chart,
    trend_line_chart,
)

pytestmark = [pytest.mark.unit, pytest.mark.visualization]


class TestChartTypes:
    """Test chart type enums and selection."""

    def test_chart_type_enum_values(self) -> None:
        """Test ChartType enum has expected values."""
        assert ChartType.COLUMN is not None
        assert ChartType.COLUMN_STACKED is not None
        assert ChartType.BAR is not None
        assert ChartType.LINE is not None
        assert ChartType.PIE is not None
        assert ChartType.SCATTER is not None
        assert ChartType.COMBO is not None

    def test_column_chart_builder(self) -> None:
        """Test column chart creation."""
        spec = ChartBuilder().column_chart().build()
        assert spec.chart_type == ChartType.COLUMN

    def test_stacked_column_chart(self) -> None:
        """Test stacked column chart creation."""
        spec = ChartBuilder().column_chart(stacked=True).build()
        assert spec.chart_type == ChartType.COLUMN_STACKED

    def test_100_stacked_column_chart(self) -> None:
        """Test 100% stacked column chart creation."""
        spec = ChartBuilder().column_chart(stacked=True, percent=True).build()
        assert spec.chart_type == ChartType.COLUMN_100_STACKED

    def test_bar_chart_builder(self) -> None:
        """Test bar chart creation."""
        spec = ChartBuilder().bar_chart().build()
        assert spec.chart_type == ChartType.BAR

    def test_bar_chart_stacked(self) -> None:
        """Test stacked bar chart creation."""
        spec = ChartBuilder().bar_chart(stacked=True).build()
        assert spec.chart_type == ChartType.BAR_STACKED

    def test_bar_chart_100_stacked(self) -> None:
        """Test 100% stacked bar chart creation."""
        spec = ChartBuilder().bar_chart(stacked=True, percent=True).build()
        assert spec.chart_type == ChartType.BAR_100_STACKED

    def test_line_chart_builder(self) -> None:
        """Test line chart creation."""
        spec = ChartBuilder().line_chart().build()
        assert spec.chart_type == ChartType.LINE

    def test_line_chart_with_markers(self) -> None:
        """Test line chart with markers."""
        spec = ChartBuilder().line_chart(markers=True).build()
        assert spec.chart_type == ChartType.LINE_MARKERS

    def test_smooth_line_chart(self) -> None:
        """Test smooth line chart."""
        spec = ChartBuilder().line_chart(smooth=True).build()
        assert spec.chart_type == ChartType.LINE_SMOOTH

    def test_area_chart_builder(self) -> None:
        """Test area chart creation."""
        spec = ChartBuilder().area_chart().build()
        assert spec.chart_type == ChartType.AREA

    def test_area_chart_stacked(self) -> None:
        """Test stacked area chart creation."""
        spec = ChartBuilder().area_chart(stacked=True).build()
        assert spec.chart_type == ChartType.AREA_STACKED

    def test_area_chart_100_stacked(self) -> None:
        """Test 100% stacked area chart creation."""
        spec = ChartBuilder().area_chart(stacked=True, percent=True).build()
        assert spec.chart_type == ChartType.AREA_100_STACKED

    def test_pie_chart_builder(self) -> None:
        """Test pie chart creation."""
        spec = ChartBuilder().pie_chart().build()
        assert spec.chart_type == ChartType.PIE

    def test_doughnut_chart(self) -> None:
        """Test doughnut chart creation."""
        spec = ChartBuilder().pie_chart(doughnut=True).build()
        assert spec.chart_type == ChartType.DOUGHNUT

    def test_scatter_chart_builder(self) -> None:
        """Test scatter chart creation."""
        spec = ChartBuilder().scatter_chart().build()
        assert spec.chart_type == ChartType.SCATTER

    def test_scatter_chart_with_lines(self) -> None:
        """Test scatter chart with connecting lines."""
        spec = ChartBuilder().scatter_chart(lines=True).build()
        assert spec.chart_type == ChartType.SCATTER_LINES

    def test_bubble_chart_builder(self) -> None:
        """Test bubble chart creation."""
        spec = ChartBuilder().bubble_chart().build()
        assert spec.chart_type == ChartType.BUBBLE

    def test_combo_chart_builder(self) -> None:
        """Test combo chart creation."""
        spec = ChartBuilder().combo_chart().build()
        assert spec.chart_type == ChartType.COMBO


class TestChartConfiguration:
    """Test chart configuration options."""

    def test_chart_title(self) -> None:
        """Test setting chart title."""
        spec = (
            ChartBuilder()
            .column_chart()
            .title("Monthly Budget", font_size="16pt", font_weight="bold")
            .build()
        )
        assert spec.title is not None
        assert spec.title.text == "Monthly Budget"  # type: ignore[union-attr]
        assert spec.title.font_size == "16pt"  # type: ignore[union-attr]
        assert spec.title.font_weight == "bold"  # type: ignore[union-attr]

    def test_chart_title_with_color(self) -> None:
        """Test title with custom color."""
        spec = ChartBuilder().column_chart().title("Budget", color="#1A3A5C").build()
        assert spec.title is not None
        assert spec.title.color == "#1A3A5C"  # type: ignore[union-attr]

    def test_chart_title_with_position(self) -> None:
        """Test title with custom position."""
        spec = ChartBuilder().column_chart().title("Budget", position="bottom").build()
        assert spec.title is not None
        assert spec.title.position == "bottom"  # type: ignore[union-attr]

    def test_legend_configuration(self) -> None:
        """Test legend configuration."""
        spec = (
            ChartBuilder()
            .column_chart()
            .legend(position="bottom", visible=True)
            .build()
        )
        assert spec.legend.position == LegendPosition.BOTTOM  # type: ignore[union-attr]
        assert spec.legend.visible is True  # type: ignore[union-attr]

    def test_legend_none(self) -> None:
        """Test hiding legend."""
        spec = ChartBuilder().column_chart().legend(position="none").build()
        assert spec.legend.position == LegendPosition.NONE  # type: ignore[union-attr]
        assert spec.legend.visible is False  # type: ignore[union-attr]

    def test_legend_with_overlay(self) -> None:
        """Test legend with overlay option."""
        spec = (
            ChartBuilder().column_chart().legend(position="right", overlay=True).build()
        )
        assert spec.legend.overlay is True  # type: ignore[union-attr]

    def test_legend_with_font_size(self) -> None:
        """Test legend with custom font size."""
        spec = ChartBuilder().column_chart().legend(font_size="12pt").build()
        assert spec.legend.font_size == "12pt"  # type: ignore[union-attr]

    def test_value_axis_configuration(self) -> None:
        """Test value axis configuration."""
        spec = (
            ChartBuilder()
            .column_chart()
            .axis("value", title="Amount ($)", min=0, max=1000)
            .build()
        )
        assert spec.value_axis is not None
        assert spec.value_axis.title == "Amount ($)"
        assert spec.value_axis.min_value == 0
        assert spec.value_axis.max_value == 1000

    def test_category_axis_configuration(self) -> None:
        """Test category axis configuration."""
        spec = ChartBuilder().column_chart().category_axis(title="Months").build()
        assert spec.category_axis is not None
        assert spec.category_axis.title == "Months"

    def test_category_axis_reversed(self) -> None:
        """Test category axis with reversed order."""
        spec = (
            ChartBuilder()
            .column_chart()
            .category_axis(title="Items", reversed=True)
            .build()
        )
        assert spec.category_axis is not None
        assert spec.category_axis.reversed is True

    def test_category_axis_with_format_code(self) -> None:
        """Test category axis with format code."""
        spec = (
            ChartBuilder().column_chart().category_axis(format_code="MMM YYYY").build()
        )
        assert spec.category_axis is not None
        assert spec.category_axis.format_code == "MMM YYYY"

    def test_value_axis_method(self) -> None:
        """Test value_axis() method."""
        spec = (
            ChartBuilder()
            .column_chart()
            .value_axis(title="Values", min=0, max=500, logarithmic=True)
            .build()
        )
        assert spec.value_axis is not None
        assert spec.value_axis.title == "Values"
        assert spec.value_axis.min_value == 0
        assert spec.value_axis.max_value == 500
        assert spec.value_axis.logarithmic is True

    def test_value_axis_with_format_code(self) -> None:
        """Test value axis with number format."""
        spec = ChartBuilder().column_chart().value_axis(format_code="$#,##0").build()
        assert spec.value_axis is not None
        assert spec.value_axis.format_code == "$#,##0"

    def test_secondary_axis_configuration(self) -> None:
        """Test secondary axis configuration."""
        spec = (
            ChartBuilder()
            .combo_chart()
            .axis("secondary", title="Percentage", min=0, max=100)
            .build()
        )
        assert spec.secondary_axis is not None
        assert spec.secondary_axis.title == "Percentage"
        assert spec.secondary_axis.axis_type == AxisType.SECONDARY_VALUE

    def test_axis_with_interval(self) -> None:
        """Test axis with major interval setting."""
        spec = ChartBuilder().column_chart().axis("value", interval=50).build()
        assert spec.value_axis is not None
        assert spec.value_axis.major_interval == 50

    def test_axis_with_gridlines_disabled(self) -> None:
        """Test axis with gridlines disabled."""
        spec = ChartBuilder().column_chart().axis("value", gridlines=False).build()
        assert spec.value_axis is not None
        assert spec.value_axis.major_gridlines is False

    def test_axis_logarithmic(self) -> None:
        """Test axis with logarithmic scale."""
        spec = ChartBuilder().scatter_chart().axis("value", logarithmic=True).build()
        assert spec.value_axis is not None
        assert spec.value_axis.logarithmic is True

    def test_data_labels(self) -> None:
        """Test data label configuration."""
        spec = (
            ChartBuilder()
            .pie_chart()
            .data_labels(show_value=True, show_percentage=True)
            .build()
        )
        assert spec.data_labels is not None
        assert spec.data_labels.show_value is True
        assert spec.data_labels.show_percentage is True

    def test_data_labels_with_category(self) -> None:
        """Test data labels showing category."""
        spec = ChartBuilder().pie_chart().data_labels(show_category=True).build()
        assert spec.data_labels is not None
        assert spec.data_labels.show_category is True

    def test_data_labels_with_series(self) -> None:
        """Test data labels showing series name."""
        spec = ChartBuilder().column_chart().data_labels(show_series=True).build()
        assert spec.data_labels is not None
        assert spec.data_labels.show_series is True

    def test_data_labels_position_inside(self) -> None:
        """Test data labels with inside position."""
        spec = ChartBuilder().column_chart().data_labels(position="inside").build()
        assert spec.data_labels is not None
        assert spec.data_labels.position == DataLabelPosition.INSIDE

    def test_data_labels_with_format_code(self) -> None:
        """Test data labels with number format."""
        spec = (
            ChartBuilder()
            .column_chart()
            .data_labels(show_value=True, format_code="$#,##0")
            .build()
        )
        assert spec.data_labels is not None
        assert spec.data_labels.format_code == "$#,##0"


class TestDataSeries:
    """Test data series configuration."""

    def test_add_series(self) -> None:
        """Test adding a data series."""
        spec = ChartBuilder().column_chart().series("Budget", "Sheet.B2:B13").build()
        assert len(spec.series) == 1
        assert spec.series[0].name == "Budget"
        assert spec.series[0].values == "Sheet.B2:B13"

    def test_multiple_series(self) -> None:
        """Test adding multiple data series."""
        spec = (
            ChartBuilder()
            .column_chart()
            .series("Budget", "Sheet.B2:B13")
            .series("Actual", "Sheet.C2:C13")
            .build()
        )
        assert len(spec.series) == 2
        assert spec.series[0].name == "Budget"
        assert spec.series[1].name == "Actual"

    def test_series_with_color(self) -> None:
        """Test series with custom color."""
        spec = (
            ChartBuilder()
            .column_chart()
            .series("Budget", "Sheet.B2:B13", color="#4472C4")
            .build()
        )
        assert spec.series[0].color == "#4472C4"

    def test_series_secondary_axis(self) -> None:
        """Test series on secondary axis."""
        spec = (
            ChartBuilder()
            .combo_chart()
            .series("Revenue", "Sheet.B2:B13")
            .series("Growth", "Sheet.C2:C13", secondary_axis=True)
            .build()
        )
        assert spec.series[0].secondary_axis is False
        assert spec.series[1].secondary_axis is True

    def test_series_with_chart_type_override(self) -> None:
        """Test series with chart type override for combo charts."""
        spec = (
            ChartBuilder()
            .combo_chart()
            .series("Revenue", "Sheet.B2:B13", chart_type="column")
            .series("Trend", "Sheet.C2:C13", chart_type="line")
            .build()
        )
        assert spec.series[0].chart_type == ChartType.COLUMN
        assert spec.series[1].chart_type == ChartType.LINE

    def test_series_with_chart_type_enum(self) -> None:
        """Test series with ChartType enum override."""
        spec = (
            ChartBuilder()
            .combo_chart()
            .series("Data", "Sheet.B2:B13", chart_type=ChartType.AREA)
            .build()
        )
        assert spec.series[0].chart_type == ChartType.AREA

    def test_series_with_trendline_param(self) -> None:
        """Test series with trendline parameter."""
        spec = (
            ChartBuilder()
            .scatter_chart()
            .series("Data", "Sheet.B2:B13", trendline="linear")
            .build()
        )
        assert spec.series[0].trendline is not None
        assert spec.series[0].trendline.type == TrendlineType.LINEAR

    def test_series_with_exponential_trendline(self) -> None:
        """Test series with exponential trendline."""
        spec = (
            ChartBuilder()
            .scatter_chart()
            .series("Data", "Sheet.B2:B13", trendline="exponential")
            .build()
        )
        assert spec.series[0].trendline is not None
        assert spec.series[0].trendline.type == TrendlineType.EXPONENTIAL

    def test_categories(self) -> None:
        """Test setting category range."""
        spec = (
            ChartBuilder()
            .column_chart()
            .categories("Sheet.A2:A13")
            .series("Budget", "Sheet.B2:B13")
            .build()
        )
        assert spec.categories == "Sheet.A2:A13"

    def test_series_color_method(self) -> None:
        """Test series_color() method to set color on last series."""
        spec = (
            ChartBuilder()
            .column_chart()
            .series("Budget", "Sheet.B2:B13")
            .series_color("#FF5733")
            .build()
        )
        assert spec.series[0].color == "#FF5733"

    def test_series_color_method_no_series(self) -> None:
        """Test series_color() when no series added."""
        builder = ChartBuilder().column_chart()
        # Should not raise, just do nothing
        builder.series_color("#FF5733")
        spec = builder.build()
        assert len(spec.series) == 0


class TestChartPositioning:
    """Test chart positioning."""

    def test_chart_position(self) -> None:
        """Test setting chart position."""
        spec = (
            ChartBuilder()
            .column_chart()
            .position("F2", offset_x=10, offset_y=5)
            .build()
        )
        assert spec.position.cell == "F2"  # type: ignore[union-attr]
        assert spec.position.offset_x == 10  # type: ignore[union-attr]
        assert spec.position.offset_y == 5  # type: ignore[union-attr]

    def test_chart_size(self) -> None:
        """Test setting chart size."""
        spec = ChartBuilder().column_chart().size(500, 350).build()
        assert spec.size.width == 500
        assert spec.size.height == 350

    def test_position_with_cells(self) -> None:
        """Test move/size with cells options."""
        spec = (
            ChartBuilder()
            .column_chart()
            .position("F2", move_with_cells=True, size_with_cells=True)
            .build()
        )
        assert spec.position.move_with_cells is True  # type: ignore[union-attr]
        assert spec.position.size_with_cells is True  # type: ignore[union-attr]


class TestChartStyling:
    """Test chart styling options."""

    def test_style_preset(self) -> None:
        """Test applying style preset."""
        spec = ChartBuilder().column_chart().style("theme").build()
        assert spec.style_preset == "theme"

    def test_custom_colors(self) -> None:
        """Test custom color palette."""
        spec = (
            ChartBuilder()
            .column_chart()
            .colors("#4472C4", "#ED7D31", "#A5A5A5")
            .build()
        )
        assert spec.color_palette == ["#4472C4", "#ED7D31", "#A5A5A5"]

    def test_plot_area_styling(self) -> None:
        """Test plot area styling."""
        spec = (
            ChartBuilder()
            .column_chart()
            .plot_area(background="#F5F5F5", border_color="#CCCCCC")
            .build()
        )
        assert spec.plot_area is not None
        assert spec.plot_area.background_color == "#F5F5F5"
        assert spec.plot_area.border_color == "#CCCCCC"

    def test_plot_area_border_width(self) -> None:
        """Test plot area border width."""
        spec = ChartBuilder().column_chart().plot_area(border_width="2pt").build()
        assert spec.plot_area is not None
        assert spec.plot_area.border_width == "2pt"

    def test_3d_effects(self) -> None:
        """Test 3D effects."""
        spec = ChartBuilder().column_chart().threed(True).build()
        assert spec.threed is True

    def test_3d_effects_disabled(self) -> None:
        """Test disabling 3D effects."""
        spec = ChartBuilder().column_chart().threed(False).build()
        assert spec.threed is False


class TestTrendlines:
    """Test trendline configuration."""

    def test_series_trendline(self) -> None:
        """Test adding trendline to series."""
        spec = (
            ChartBuilder()
            .scatter_chart()
            .series("Data", "Sheet.B2:B100")
            .series_trendline("linear")
            .build()
        )
        assert spec.series[0].trendline is not None
        assert spec.series[0].trendline.type == TrendlineType.LINEAR

    def test_trendline_with_forecast(self) -> None:
        """Test trendline with forecast periods."""
        spec = (
            ChartBuilder()
            .scatter_chart()
            .series("Data", "Sheet.B2:B100")
            .series_trendline("linear", forward_periods=3)
            .build()
        )
        assert spec.series[0].trendline is not None
        assert spec.series[0].trendline.forward_periods == 3

    def test_trendline_with_backward_forecast(self) -> None:
        """Test trendline with backward forecast periods."""
        spec = (
            ChartBuilder()
            .scatter_chart()
            .series("Data", "Sheet.B2:B100")
            .series_trendline("linear", backward_periods=2)
            .build()
        )
        assert spec.series[0].trendline is not None
        assert spec.series[0].trendline.backward_periods == 2

    def test_trendline_display_options(self) -> None:
        """Test trendline display options."""
        spec = (
            ChartBuilder()
            .scatter_chart()
            .series("Data", "Sheet.B2:B100")
            .series_trendline("linear", display_equation=True, display_r_squared=True)
            .build()
        )
        assert spec.series[0].trendline is not None
        assert spec.series[0].trendline.display_equation is True
        assert spec.series[0].trendline.display_r_squared is True

    def test_trendline_types(self) -> None:
        """Test all trendline types."""
        types = [
            ("linear", TrendlineType.LINEAR),
            ("exponential", TrendlineType.EXPONENTIAL),
            ("logarithmic", TrendlineType.LOGARITHMIC),
            ("polynomial", TrendlineType.POLYNOMIAL),
            ("power", TrendlineType.POWER),
            ("moving_average", TrendlineType.MOVING_AVERAGE),
        ]
        for type_str, type_enum in types:
            spec = (
                ChartBuilder()
                .scatter_chart()
                .series("Data", "Sheet.B2:B100")
                .series_trendline(type_str)
                .build()
            )
            assert spec.series[0].trendline is not None
            assert spec.series[0].trendline.type == type_enum

    def test_trendline_no_current_series(self) -> None:
        """Test trendline when no series added."""
        builder = ChartBuilder().scatter_chart()
        # Should not raise, just do nothing
        builder.series_trendline("linear")
        spec = builder.build()
        assert len(spec.series) == 0


class TestSparklines:
    """Test sparkline configuration."""

    def test_line_sparkline(self) -> None:
        """Test line sparkline creation."""
        spark = SparklineBuilder().line().data("B1:M1").build()
        assert spark.type == SparklineType.LINE
        assert spark.data_range == "B1:M1"

    def test_column_sparkline(self) -> None:
        """Test column sparkline creation."""
        spark = SparklineBuilder().column().data("B1:M1").build()
        assert spark.type == SparklineType.COLUMN

    def test_win_loss_sparkline(self) -> None:
        """Test win/loss sparkline creation."""
        spark = SparklineBuilder().win_loss().data("B1:M1").build()
        assert spark.type == SparklineType.WIN_LOSS

    def test_sparkline_color(self) -> None:
        """Test sparkline color setting."""
        spark = SparklineBuilder().line().data("B1:M1").color("#4472C4").build()
        assert spark.color == "#4472C4"

    def test_sparkline_negative_color(self) -> None:
        """Test sparkline negative color setting."""
        spark = (
            SparklineBuilder().line().data("B1:M1").negative_color("#FF0000").build()
        )
        assert spark.negative_color == "#FF0000"

    def test_sparkline_markers(self) -> None:
        """Test sparkline marker colors."""
        spark = (
            SparklineBuilder()
            .line()
            .data("B1:M1")
            .markers(high="#00B050", low="#FF0000")
            .build()
        )
        assert spark.markers is not None
        assert spark.markers.high == "#00B050"
        assert spark.markers.low == "#FF0000"

    def test_sparkline_markers_all(self) -> None:
        """Test sparkline with all marker colors."""
        spark = (
            SparklineBuilder()
            .line()
            .data("B1:M1")
            .markers(
                high="#00B050",
                low="#FF0000",
                first="#FFC000",
                last="#7030A0",
                negative="#C00000",
            )
            .build()
        )
        assert spark.markers is not None
        assert spark.markers.high == "#00B050"
        assert spark.markers is not None
        assert spark.markers.low == "#FF0000"
        assert spark.markers is not None
        assert spark.markers.first == "#FFC000"
        assert spark.markers is not None
        assert spark.markers.last == "#7030A0"
        assert spark.markers is not None
        assert spark.markers.negative == "#C00000"

    def test_sparkline_axis_range(self) -> None:
        """Test sparkline axis range."""
        spark = (
            SparklineBuilder().line().data("B1:M1").axis_range(min=0, max=100).build()
        )
        assert spark.min_axis == 0
        assert spark.max_axis == 100

    def test_sparkline_axis_range_partial(self) -> None:
        """Test sparkline axis range with only min or max."""
        spark_min = SparklineBuilder().line().data("B1:M1").axis_range(min=0).build()
        assert spark_min.min_axis == 0
        assert spark_min.max_axis is None

        spark_max = SparklineBuilder().line().data("B1:M1").axis_range(max=100).build()
        assert spark_max.min_axis is None
        assert spark_max.max_axis == 100

    def test_sparkline_same_scale(self) -> None:
        """Test sparkline same scale for group."""
        spark = SparklineBuilder().line().data("B1:M1").same_scale(True).build()
        assert spark.same_scale is True

    def test_sparkline_show_axis(self) -> None:
        """Test sparkline show axis."""
        spark = SparklineBuilder().line().data("B1:M1").show_axis(True).build()
        assert spark.show_axis is True


class TestConvenienceFunctions:
    """Test convenience functions for chart creation."""

    def test_chart_function(self) -> None:
        """Test chart() convenience function."""
        builder = chart()
        assert isinstance(builder, ChartBuilder)

    def test_sparkline_function(self) -> None:
        """Test sparkline() convenience function."""
        builder = sparkline()
        assert isinstance(builder, SparklineBuilder)

    def test_budget_comparison_chart(self) -> None:
        """Test pre-built budget comparison chart."""
        spec = budget_comparison_chart(
            categories="Sheet.A2:A13",
            budget_values="Sheet.B2:B13",
            actual_values="Sheet.C2:C13",
        )
        assert spec.chart_type == ChartType.COLUMN
        assert len(spec.series) == 2
        assert spec.series[0].name == "Budget"
        assert spec.series[1].name == "Actual"

    def test_budget_comparison_chart_custom_title(self) -> None:
        """Test budget comparison chart with custom title."""
        spec = budget_comparison_chart(
            categories="Sheet.A2:A13",
            budget_values="Sheet.B2:B13",
            actual_values="Sheet.C2:C13",
            title="Custom Title",
        )
        assert spec.title is not None
        assert spec.title.text == "Custom Title"  # type: ignore[union-attr]

    def test_budget_comparison_chart_custom_position(self) -> None:
        """Test budget comparison chart with custom position."""
        spec = budget_comparison_chart(
            categories="Sheet.A2:A13",
            budget_values="Sheet.B2:B13",
            actual_values="Sheet.C2:C13",
            position="G5",
        )
        assert spec.position.cell == "G5"  # type: ignore[union-attr]

    def test_spending_pie_chart(self) -> None:
        """Test pre-built spending pie chart."""
        spec = spending_pie_chart(
            categories="Data.A2:A10",
            values="Data.B2:B10",
        )
        assert spec.chart_type == ChartType.PIE
        assert spec.data_labels is not None
        assert spec.data_labels.show_percentage is True

    def test_spending_pie_chart_custom_title(self) -> None:
        """Test spending pie chart with custom title."""
        spec = spending_pie_chart(
            categories="Data.A2:A10",
            values="Data.B2:B10",
            title="Monthly Expenses",
        )
        assert spec.title is not None
        assert spec.title.text == "Monthly Expenses"  # type: ignore[union-attr]

    def test_spending_pie_chart_custom_position(self) -> None:
        """Test spending pie chart with custom position."""
        spec = spending_pie_chart(
            categories="Data.A2:A10",
            values="Data.B2:B10",
            position="H10",
        )
        assert spec.position.cell == "H10"  # type: ignore[union-attr]

    def test_trend_line_chart(self) -> None:
        """Test pre-built trend line chart."""
        spec = trend_line_chart(
            categories="Data.A2:A24",
            values="Data.B2:B24",
            trendline=True,
        )
        assert spec.chart_type == ChartType.LINE_MARKERS
        assert len(spec.series) == 1
        assert spec.series[0].trendline is not None

    def test_trend_line_chart_without_trendline(self) -> None:
        """Test trend line chart without trendline."""
        spec = trend_line_chart(
            categories="Data.A2:A24",
            values="Data.B2:B24",
            trendline=False,
        )
        assert spec.chart_type == ChartType.LINE_MARKERS
        assert spec.series[0].trendline is None

    def test_trend_line_chart_custom_title(self) -> None:
        """Test trend line chart with custom title."""
        spec = trend_line_chart(
            categories="Data.A2:A24",
            values="Data.B2:B24",
            title="Revenue Trend",
        )
        assert spec.title is not None
        assert spec.title.text == "Revenue Trend"  # type: ignore[union-attr]

    def test_trend_line_chart_custom_position(self) -> None:
        """Test trend line chart with custom position."""
        spec = trend_line_chart(
            categories="Data.A2:A24",
            values="Data.B2:B24",
            position="E15",
        )
        assert spec.position.cell == "E15"  # type: ignore[union-attr]


class TestChartDataClasses:
    """Test chart data class creation and defaults."""

    def test_chart_title_defaults(self) -> None:
        """Test ChartTitle default values."""
        title = ChartTitle(text="Test")
        assert title.font_size == "14pt"
        assert title.font_weight == "bold"
        assert title.position == "top"
        assert title.font_family is None
        assert title.color is None

    def test_chart_title_full(self) -> None:
        """Test ChartTitle with all values."""
        title = ChartTitle(
            text="Full Title",
            font_family="Arial",
            font_size="18pt",
            font_weight="normal",
            color="#333333",
            position="bottom",
        )
        assert title.text == "Full Title"
        assert title.font_family == "Arial"
        assert title.font_size == "18pt"
        assert title.font_weight == "normal"
        assert title.color == "#333333"
        assert title.position == "bottom"

    def test_axis_config_defaults(self) -> None:
        """Test AxisConfig default values."""
        axis = AxisConfig()
        assert axis.axis_type == AxisType.VALUE
        assert axis.major_gridlines is True
        assert axis.minor_gridlines is False
        assert axis.logarithmic is False
        assert axis.reversed is False
        assert axis.title is None
        assert axis.min_value is None
        assert axis.max_value is None

    def test_axis_config_full(self) -> None:
        """Test AxisConfig with all values."""
        axis = AxisConfig(
            axis_type=AxisType.CATEGORY,
            title="X Axis",
            title_font_size="12pt",
            min_value=0,
            max_value=100,
            major_interval=10,
            minor_interval=2,
            major_gridlines=True,
            minor_gridlines=True,
            format_code="#,##0",
            reversed=True,
            logarithmic=True,
        )
        assert axis.axis_type == AxisType.CATEGORY
        assert axis.title == "X Axis"
        assert axis.title_font_size == "12pt"
        assert axis.min_value == 0
        assert axis.max_value == 100
        assert axis.major_interval == 10
        assert axis.minor_interval == 2
        assert axis.major_gridlines is True
        assert axis.minor_gridlines is True
        assert axis.format_code == "#,##0"
        assert axis.reversed is True
        assert axis.logarithmic is True

    def test_legend_config_defaults(self) -> None:
        """Test LegendConfig default values."""
        legend = LegendConfig()
        assert legend.position == LegendPosition.BOTTOM
        assert legend.visible is True
        assert legend.overlay is False
        assert legend.font_family is None
        assert legend.font_size == "10pt"

    def test_legend_position_enum(self) -> None:
        """Test LegendPosition enum values."""
        assert LegendPosition.TOP.value == "top"
        assert LegendPosition.BOTTOM.value == "bottom"
        assert LegendPosition.LEFT.value == "left"
        assert LegendPosition.RIGHT.value == "right"
        assert LegendPosition.TOP_LEFT.value == "top-left"
        assert LegendPosition.TOP_RIGHT.value == "top-right"
        assert LegendPosition.BOTTOM_LEFT.value == "bottom-left"
        assert LegendPosition.BOTTOM_RIGHT.value == "bottom-right"
        assert LegendPosition.NONE.value == "none"

    def test_data_label_config_defaults(self) -> None:
        """Test DataLabelConfig default values."""
        labels = DataLabelConfig()
        assert labels.show_value is False
        assert labels.show_percentage is False
        assert labels.show_category is False
        assert labels.show_series is False
        assert labels.position == DataLabelPosition.OUTSIDE
        assert labels.font_size == "9pt"
        assert labels.format_code is None
        assert labels.separator == ", "

    def test_data_label_position_enum(self) -> None:
        """Test DataLabelPosition enum values."""
        assert DataLabelPosition.INSIDE.value == "inside"
        assert DataLabelPosition.OUTSIDE.value == "outside"
        assert DataLabelPosition.CENTER.value == "center"
        assert DataLabelPosition.ABOVE.value == "above"
        assert DataLabelPosition.BELOW.value == "below"
        assert DataLabelPosition.LEFT.value == "left"
        assert DataLabelPosition.RIGHT.value == "right"

    def test_data_series_defaults(self) -> None:
        """Test DataSeries default values."""
        series = DataSeries(name="Test", values="A1:A10")
        assert series.secondary_axis is False
        assert series.chart_type is None
        assert series.line_width == "2pt"
        assert series.fill_opacity == 0.8
        assert series.categories is None
        assert series.color is None
        assert series.data_labels is None
        assert series.trendline is None
        assert series.marker_style is None

    def test_data_series_full(self) -> None:
        """Test DataSeries with all values."""
        trend = Trendline(type=TrendlineType.LINEAR)
        labels = DataLabelConfig(show_value=True)
        series = DataSeries(
            name="Full Series",
            values="B1:B100",
            categories="A1:A100",
            color="#FF5733",
            secondary_axis=True,
            chart_type=ChartType.LINE,
            data_labels=labels,
            trendline=trend,
            marker_style="circle",
            line_width="3pt",
            fill_opacity=0.5,
        )
        assert series.name == "Full Series"
        assert series.values == "B1:B100"
        assert series.categories == "A1:A100"
        assert series.color == "#FF5733"
        assert series.secondary_axis is True
        assert series.chart_type == ChartType.LINE
        assert series.data_labels == labels
        assert series.trendline == trend
        assert series.marker_style == "circle"
        assert series.line_width == "3pt"
        assert series.fill_opacity == 0.5

    def test_chart_position_defaults(self) -> None:
        """Test ChartPosition default values."""
        pos = ChartPosition()
        assert pos.cell == "A1"
        assert pos.offset_x == 0
        assert pos.offset_y == 0
        assert pos.move_with_cells is True
        assert pos.size_with_cells is False
        assert pos.z_order == 0

    def test_chart_size_defaults(self) -> None:
        """Test ChartSize default values."""
        size = ChartSize()
        assert size.width == 400
        assert size.height == 300

    def test_plot_area_style_defaults(self) -> None:
        """Test PlotAreaStyle default values."""
        style = PlotAreaStyle()
        assert style.background_color is None
        assert style.border_color is None
        assert style.border_width == "1pt"

    def test_trendline_defaults(self) -> None:
        """Test Trendline default values."""
        trend = Trendline()
        assert trend.type == TrendlineType.LINEAR
        assert trend.order == 2
        assert trend.period == 2
        assert trend.forward_periods == 0
        assert trend.backward_periods == 0
        assert trend.intercept is None
        assert trend.display_equation is False
        assert trend.display_r_squared is False
        assert trend.color is None
        assert trend.width == "1pt"
        assert trend.dash_style == "solid"

    def test_trendline_type_enum(self) -> None:
        """Test TrendlineType enum values."""
        assert TrendlineType.LINEAR.value == "linear"
        assert TrendlineType.EXPONENTIAL.value == "exponential"
        assert TrendlineType.LOGARITHMIC.value == "logarithmic"
        assert TrendlineType.POLYNOMIAL.value == "polynomial"
        assert TrendlineType.POWER.value == "power"
        assert TrendlineType.MOVING_AVERAGE.value == "moving_average"

    def test_sparkline_defaults(self) -> None:
        """Test Sparkline default values."""
        spark = Sparkline()
        assert spark.type == SparklineType.LINE
        assert spark.data_range == ""
        assert spark.color == "#4472C4"
        assert spark.negative_color == "#FF0000"
        assert spark.markers is None
        assert spark.min_axis is None
        assert spark.max_axis is None
        assert spark.same_scale is False
        assert spark.show_axis is False
        assert spark.right_to_left is False

    def test_sparkline_type_enum(self) -> None:
        """Test SparklineType enum values."""
        assert SparklineType.LINE.value == "line"
        assert SparklineType.COLUMN.value == "column"
        assert SparklineType.WIN_LOSS.value == "win_loss"

    def test_sparkline_markers_defaults(self) -> None:
        """Test SparklineMarkers default values."""
        markers = SparklineMarkers()
        assert markers.high is None
        assert markers.low is None
        assert markers.first is None
        assert markers.last is None
        assert markers.negative is None

    def test_chart_spec_defaults(self) -> None:
        """Test ChartSpec default values."""
        spec = ChartSpec()
        assert spec.chart_type == ChartType.COLUMN
        assert spec.title is None
        assert spec.series == []
        assert spec.categories is None
        assert spec.legend is not None
        assert spec.category_axis is None
        assert spec.value_axis is None
        assert spec.secondary_axis is None
        assert spec.position is not None
        assert spec.size is not None
        assert spec.plot_area is None
        assert spec.data_labels is None
        assert spec.style_preset is None
        assert spec.color_palette is None
        assert spec.threed is False

    def test_axis_type_enum(self) -> None:
        """Test AxisType enum values."""
        assert AxisType.CATEGORY.value == "category"
        assert AxisType.VALUE.value == "value"
        assert AxisType.SECONDARY_VALUE.value == "secondary_value"


class TestChartBuilderChaining:
    """Test ChartBuilder method chaining."""

    def test_full_chart_configuration(self) -> None:
        """Test complete chart configuration with all options."""
        spec = (
            ChartBuilder()
            .column_chart()
            .title("Monthly Budget vs Actual", font_size="16pt")
            .categories("Budget.A2:A13")
            .series("Budget", "Budget.B2:B13", color="#4472C4")
            .series("Actual", "Budget.C2:C13", color="#ED7D31")
            .legend(position="bottom")
            .axis("value", title="Amount ($)", min=0)
            .axis("category", title="Month")
            .position("F2")
            .size(500, 350)
            .colors("#4472C4", "#ED7D31", "#A5A5A5")
            .style("theme")
            .build()
        )

        # Verify all settings
        assert spec.chart_type == ChartType.COLUMN
        assert spec.title is not None
        assert spec.title.text == "Monthly Budget vs Actual"  # type: ignore[union-attr]
        assert spec.categories == "Budget.A2:A13"
        assert len(spec.series) == 2
        assert spec.legend.position == LegendPosition.BOTTOM  # type: ignore[union-attr]
        assert spec.value_axis is not None
        assert spec.value_axis.title == "Amount ($)"
        assert spec.position.cell == "F2"  # type: ignore[union-attr]
        assert spec.size.width == 500
        assert spec.style_preset == "theme"

    def test_builder_returns_self(self) -> None:
        """Test that all builder methods return self for chaining."""
        builder = ChartBuilder()

        # All methods should return the same builder instance
        assert builder.column_chart() is builder
        assert builder.title("Test") is builder
        assert builder.series("Test", "A1:A10") is builder
        assert builder.categories("B1:B10") is builder
        assert builder.legend() is builder
        assert builder.axis("value") is builder
        assert builder.position("A1") is builder
        assert builder.size(400, 300) is builder
        assert builder.style("theme") is builder
        assert builder.colors("#000") is builder
        assert builder.plot_area() is builder
        assert builder.threed() is builder
        assert builder.data_labels() is builder
        assert builder.category_axis() is builder
        assert builder.value_axis() is builder
        assert builder.series_color("#FFF") is builder
        assert builder.series_trendline("linear") is builder

    def test_builder_all_chart_types_return_self(self) -> None:
        """Test that all chart type methods return self."""
        builder = ChartBuilder()

        assert builder.column_chart() is builder
        assert builder.bar_chart() is builder
        assert builder.line_chart() is builder
        assert builder.area_chart() is builder
        assert builder.pie_chart() is builder
        assert builder.scatter_chart() is builder
        assert builder.bubble_chart() is builder
        assert builder.combo_chart() is builder


class TestSparklineBuilderChaining:
    """Test SparklineBuilder method chaining."""

    def test_full_sparkline_configuration(self) -> None:
        """Test complete sparkline configuration."""
        spark = (
            SparklineBuilder()
            .line()
            .data("MonthlyData.B{row}:M{row}")
            .color("#4472C4")
            .negative_color("#FF0000")
            .markers(high="#00B050", low="#C00000", first="#FFC000", last="#FFC000")
            .axis_range(min=0, max=100)
            .same_scale(True)
            .show_axis(True)
            .build()
        )

        assert spark.type == SparklineType.LINE
        assert spark.color == "#4472C4"
        assert spark.negative_color == "#FF0000"
        assert spark.markers is not None
        assert spark.markers.high == "#00B050"
        assert spark.min_axis == 0
        assert spark.same_scale is True
        assert spark.show_axis is True

    def test_sparkline_builder_returns_self(self) -> None:
        """Test that all sparkline builder methods return self."""
        builder = SparklineBuilder()

        assert builder.line() is builder
        assert builder.column() is builder
        assert builder.win_loss() is builder
        assert builder.data("A1:Z1") is builder
        assert builder.color("#000") is builder
        assert builder.negative_color("#F00") is builder
        assert builder.markers() is builder
        assert builder.axis_range() is builder
        assert builder.same_scale() is builder
        assert builder.show_axis() is builder
