#!/usr/bin/env python3
"""
Advanced Chart Builder Examples - v4.0 Feature Showcase

Demonstrates comprehensive usage of the ChartBuilder API including:
- Multiple chart types (column, bar, line, pie, scatter, combo)
- Sparklines for inline data visualization
- Trendline analysis
- Chart positioning and sizing
- Multi-series charts with secondary axes
- Chart styling and customization
- Real-world budget visualization scenarios

The ChartBuilder provides a fluent API for creating professional charts
without writing complex ODF XML.
"""

import sys

# ============================================================================
# Example 1: Basic Column Charts
# ============================================================================


def example_column_charts() -> None:
    """
    Demonstrate column chart creation.

    Shows:
    - Simple column chart
    - Stacked column chart
    - 100% stacked column chart
    - Multiple series with custom colors
    """
    from spreadsheet_dl.charts import ChartBuilder

    print("=" * 70)
    print("Example 1: Column Charts")
    print("=" * 70)

    # 1. Simple column chart
    print("\n1. Simple column chart:")
    chart = (
        ChartBuilder()
        .column_chart()
        .title("Monthly Budget vs Actual")
        .categories("Budget.A2:A13")  # Month names
        .series("Budget", "Budget.B2:B13", color="#4472C4")
        .series("Actual", "Budget.C2:C13", color="#ED7D31")
        .legend(position="bottom")
        .value_axis(title="Amount ($)", min=0, format_code="$#,##0")
        .position("F2")
        .size(500, 350)
        .build()
    )

    print(f"   Chart type: {chart.chart_type.name}")
    print(f"   Title: {chart.title.text if chart.title else 'N/A'}")  # type: ignore[union-attr]
    print(f"   Series: {len(chart.series)}")
    print(f"   Position: {chart.position.cell}")  # type: ignore[union-attr]
    print(f"   Size: {chart.size.width}x{chart.size.height}px")

    # 2. Stacked column chart
    print("\n2. Stacked column chart:")
    chart = (
        ChartBuilder()
        .column_chart(stacked=True)
        .title("Spending by Category")
        .categories("Expenses.A2:A13")
        .series("Housing", "Expenses.B2:B13")
        .series("Food", "Expenses.C2:C13")
        .series("Transportation", "Expenses.D2:D13")
        .series("Entertainment", "Expenses.E2:E13")
        .legend(position="right")
        .position("H2")
        .build()
    )

    print(f"   Chart type: {chart.chart_type.name}")
    print(f"   Stacked: {chart.chart_type.name.endswith('STACKED')}")
    print(f"   Series count: {len(chart.series)}")

    # 3. 100% stacked column chart
    print("\n3. 100% stacked column chart:")
    chart = (
        ChartBuilder()
        .column_chart(stacked=True, percent=True)
        .title("Budget Allocation (%)")
        .categories("Categories.A2:A8")
        .series("Percentage", "Categories.B2:B8")
        .data_labels(show_percentage=True)
        .legend(visible=False)
        .position("F15")
        .build()
    )

    print(f"   Chart type: {chart.chart_type.name}")
    assert chart.data_labels is not None
    print(f"   Shows percentages: {chart.data_labels.show_percentage}")

    print("\n✓ Column charts created")
    print()


# ============================================================================
# Example 2: Line and Area Charts
# ============================================================================


def example_line_area_charts() -> None:
    """
    Demonstrate line and area chart creation.

    Shows:
    - Simple line chart
    - Line chart with markers
    - Smooth line chart
    - Line chart with trendline
    - Area chart
    - Stacked area chart
    """
    from spreadsheet_dl.charts import ChartBuilder

    print("=" * 70)
    print("Example 2: Line and Area Charts")
    print("=" * 70)

    # 1. Line chart with markers
    print("\n1. Line chart with markers:")
    chart = (
        ChartBuilder()
        .line_chart(markers=True)
        .title("Monthly Spending Trend")
        .categories("Trends.A2:A13")
        .series("Spending", "Trends.B2:B13", color="#70AD47")
        .value_axis(title="Amount ($)")
        .position("F2")
        .size(600, 300)
        .build()
    )

    print(f"   Chart type: {chart.chart_type.name}")
    print(f"   Has markers: {'MARKERS' in chart.chart_type.name}")

    # 2. Smooth line chart with trendline
    print("\n2. Smooth line chart with trendline:")
    chart = (
        ChartBuilder()
        .line_chart(smooth=True)
        .title("Savings Growth with Forecast")
        .categories("Savings.A2:A13")
        .series("Actual", "Savings.B2:B13", color="#4472C4")
        .series_trendline(
            type="linear",
            forward_periods=3,
            display_equation=True,
            display_r_squared=True,
        )
        .value_axis(title="Savings ($)", format_code="$#,##0")
        .legend(position="top")
        .position("F10")
        .build()
    )

    print(f"   Chart type: {chart.chart_type.name}")
    print(f"   Has trendline: {chart.series[0].trendline is not None}")
    if chart.series[0].trendline:
        print(f"   Trendline type: {chart.series[0].trendline.type.name}")
        print(f"   Forecast periods: {chart.series[0].trendline.forward_periods}")

    # 3. Multi-line comparison
    print("\n3. Multi-line comparison chart:")
    chart = (
        ChartBuilder()
        .line_chart(markers=True)
        .title("Budget Comparison: 2024 vs 2025")
        .categories("Comparison.A2:A13")
        .series("2024 Spending", "Comparison.B2:B13", color="#4472C4")
        .series("2025 Spending", "Comparison.C2:C13", color="#ED7D31")
        .series("Budget", "Comparison.D2:D13", color="#A5A5A5")
        .legend(position="bottom")
        .axis("value", min=0)
        .position("F18")
        .size(600, 350)
        .build()
    )

    print(f"   Series count: {len(chart.series)}")
    for i, series in enumerate(chart.series):
        print(f"   Series {i + 1}: {series.name} (color: {series.color})")

    # 4. Area chart
    print("\n4. Stacked area chart:")
    chart = (
        ChartBuilder()
        .area_chart(stacked=True)
        .title("Cumulative Spending by Category")
        .categories("Monthly.A2:A13")
        .series("Housing", "Monthly.B2:B13")
        .series("Food", "Monthly.C2:C13")
        .series("Transport", "Monthly.D2:D13")
        .series("Other", "Monthly.E2:E13")
        .legend(position="top")
        .position("F22")
        .build()
    )

    print(f"   Chart type: {chart.chart_type.name}")
    print("   Shows cumulative data: Stacked area")

    print("\n✓ Line and area charts created")
    print()


# ============================================================================
# Example 3: Pie and Doughnut Charts
# ============================================================================


def example_pie_charts() -> None:
    """
    Demonstrate pie and doughnut chart creation.

    Shows:
    - Simple pie chart
    - Pie chart with data labels
    - Pie chart showing percentages
    - Doughnut chart
    - Custom colors and styling
    """
    from spreadsheet_dl.charts import ChartBuilder

    print("=" * 70)
    print("Example 3: Pie and Doughnut Charts")
    print("=" * 70)

    # 1. Pie chart with percentages
    print("\n1. Pie chart with percentages:")
    chart = (
        ChartBuilder()
        .pie_chart()
        .title("Budget Allocation by Category")
        .categories("Categories.A2:A8")
        .series("Amount", "Categories.B2:B8")
        .data_labels(
            show_percentage=True,
            show_category=True,
            position="outside",
        )
        .legend(position="right")
        .position("F2")
        .size(450, 400)
        .build()
    )

    print(f"   Chart type: {chart.chart_type.name}")
    assert chart.data_labels is not None
    print(f"   Shows percentages: {chart.data_labels.show_percentage}")
    assert chart.data_labels is not None
    print(f"   Shows categories: {chart.data_labels.show_category}")

    # 2. Pie chart with values
    print("\n2. Pie chart showing values:")
    chart = (
        ChartBuilder()
        .pie_chart()
        .title("January Spending ($)")
        .categories("January.A2:A8")
        .series("Spending", "January.B2:B8")
        .data_labels(
            show_value=True,
            format_code="$#,##0",
        )
        .colors(
            "#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#5B9BD5", "#70AD47", "#264478"
        )
        .legend(position="bottom")
        .position("F12")
        .build()
    )

    print(f"   Custom colors: {len(chart.color_palette) if chart.color_palette else 0}")

    # 3. Doughnut chart
    print("\n3. Doughnut chart:")
    chart = (
        ChartBuilder()
        .pie_chart(doughnut=True)
        .title("Spending Distribution")
        .categories("Distribution.A2:A6")
        .series("Percentage", "Distribution.B2:B6")
        .data_labels(
            show_percentage=True,
            show_category=True,
        )
        .legend(position="none")
        .position("L2")
        .build()
    )

    print(f"   Chart type: {chart.chart_type.name}")
    print(f"   Legend visible: {chart.legend.visible}")  # type: ignore[union-attr]

    print("\n✓ Pie and doughnut charts created")
    print()


# ============================================================================
# Example 4: Combo and Multi-Axis Charts
# ============================================================================


def example_combo_charts() -> None:
    """
    Demonstrate combo charts with multiple axes.

    Shows:
    - Column + line combo chart
    - Primary and secondary axes
    - Different chart types per series
    - Mixing absolute values with percentages
    """
    from spreadsheet_dl.charts import ChartBuilder

    print("=" * 70)
    print("Example 4: Combo and Multi-Axis Charts")
    print("=" * 70)

    # 1. Revenue and growth rate
    print("\n1. Revenue with growth rate (combo chart):")
    chart = (
        ChartBuilder()
        .combo_chart()
        .title("Monthly Revenue and Growth Rate")
        .categories("Revenue.A2:A13")
        .series(
            "Revenue",
            "Revenue.B2:B13",
            chart_type="column",
            color="#4472C4",
        )
        .series(
            "Growth Rate",
            "Revenue.C2:C13",
            chart_type="line",
            secondary_axis=True,
            color="#ED7D31",
        )
        .value_axis(title="Revenue ($)", min=0, format_code="$#,##0")
        .axis(
            "secondary",
            title="Growth Rate (%)",
            min=0,
            max=100,
            format_code="0%",
        )
        .legend(position="top")
        .position("F2")
        .size(600, 400)
        .build()
    )

    print(f"   Chart type: {chart.chart_type.name}")
    print(f"   Primary axis: {chart.value_axis.title if chart.value_axis else 'N/A'}")
    print(
        f"   Secondary axis: {chart.secondary_axis.title if chart.secondary_axis else 'N/A'}"
    )
    print(
        f"   Series on secondary axis: {sum(1 for s in chart.series if s.secondary_axis)}"
    )

    # 2. Budget vs actual with variance percentage
    print("\n2. Budget vs actual with variance:")
    chart = (
        ChartBuilder()
        .combo_chart()
        .title("Budget Performance Analysis")
        .categories("Performance.A2:A13")
        .series("Budget", "Performance.B2:B13", chart_type="column", color="#A5A5A5")
        .series("Actual", "Performance.C2:C13", chart_type="column", color="#4472C4")
        .series(
            "Variance %",
            "Performance.D2:D13",
            chart_type="line",
            secondary_axis=True,
            color="#ED7D31",
        )
        .series_trendline(type="linear")
        .value_axis(title="Amount ($)")
        .axis("secondary", title="Variance (%)", format_code="0.0%")
        .legend(position="bottom")
        .position("F12")
        .build()
    )

    print(
        f"   Primary series count: {sum(1 for s in chart.series if not s.secondary_axis)}"
    )
    print(
        f"   Secondary series count: {sum(1 for s in chart.series if s.secondary_axis)}"
    )
    print(f"   Has trendline: {chart.series[-1].trendline is not None}")

    # 3. Stacked columns with line overlay
    print("\n3. Stacked spending with total line:")
    chart = (
        ChartBuilder()
        .combo_chart()
        .title("Category Spending with Total")
        .categories("Detailed.A2:A13")
        .series("Housing", "Detailed.B2:B13", chart_type="column")
        .series("Food", "Detailed.C2:C13", chart_type="column")
        .series("Transport", "Detailed.D2:D13", chart_type="column")
        .series(
            "Total",
            "Detailed.E2:E13",
            chart_type="line",
            color="#000000",
        )
        .legend(position="top")
        .position("F22")
        .build()
    )

    print(
        f"   Column series: {sum(1 for s in chart.series if s.chart_type and 'COLUMN' in s.chart_type.name)}"
    )
    print(
        f"   Line series: {sum(1 for s in chart.series if s.chart_type and 'LINE' in s.chart_type.name)}"
    )

    print("\n✓ Combo charts created")
    print()


# ============================================================================
# Example 5: Sparklines
# ============================================================================


def example_sparklines() -> None:
    """
    Demonstrate sparkline creation.

    Shows:
    - Line sparklines
    - Column sparklines
    - Win/loss sparklines
    - Sparkline markers (high, low, first, last)
    - Custom colors and axis ranges
    """
    from spreadsheet_dl.charts import SparklineBuilder

    print("=" * 70)
    print("Example 5: Sparklines")
    print("=" * 70)

    # 1. Simple line sparkline
    print("\n1. Simple line sparkline:")
    sparkline = (
        SparklineBuilder()
        .line()
        .data("MonthlyData.B{row}:M{row}")  # {row} placeholder for template
        .color("#4472C4")
        .build()
    )

    print(f"   Type: {sparkline.type.name}")
    print(f"   Data range: {sparkline.data_range}")
    print(f"   Color: {sparkline.color}")

    # 2. Line sparkline with markers
    print("\n2. Line sparkline with markers:")
    sparkline = (
        SparklineBuilder()
        .line()
        .data("Trends.B{row}:M{row}")
        .color("#4472C4")
        .markers(
            high="#00B050",  # Green for highest
            low="#FF0000",  # Red for lowest
            first="#4472C4",  # Blue for first
            last="#ED7D31",  # Orange for last
        )
        .show_axis(True)
        .build()
    )

    print(f"   Markers enabled: {sparkline.markers is not None}")
    if sparkline.markers:
        print(f"   High marker: {sparkline.markers.high}")
        print(f"   Low marker: {sparkline.markers.low}")
    print(f"   Show axis: {sparkline.show_axis}")

    # 3. Column sparkline
    print("\n3. Column sparkline:")
    sparkline = (
        SparklineBuilder()
        .column()
        .data("Sales.B{row}:M{row}")
        .color("#70AD47")
        .negative_color("#FF0000")
        .build()
    )

    print(f"   Type: {sparkline.type.name}")
    print(f"   Positive color: {sparkline.color}")
    print(f"   Negative color: {sparkline.negative_color}")

    # 4. Win/loss sparkline
    print("\n4. Win/loss sparkline:")
    sparkline = (
        SparklineBuilder()
        .win_loss()
        .data("Performance.B{row}:M{row}")
        .color("#00B050")  # Green for wins
        .negative_color("#FF0000")  # Red for losses
        .build()
    )

    print(f"   Type: {sparkline.type.name}")
    print(f"   Win color: {sparkline.color}")
    print(f"   Loss color: {sparkline.negative_color}")

    # 5. Sparkline with custom axis range
    print("\n5. Sparkline with custom axis range:")
    from spreadsheet_dl.charts import SparklineBuilder

    sparkline = (
        SparklineBuilder()
        .line()
        .data("Values.B{row}:M{row}")
        .color("#4472C4")
        .axis_range(min=0, max=1000)
        .same_scale(True)
        .build()
    )

    print(f"   Min axis: {sparkline.min_axis}")
    print(f"   Max axis: {sparkline.max_axis}")
    print(f"   Same scale for group: {sparkline.same_scale}")

    print("\n✓ Sparklines created")
    print()


# ============================================================================
# Example 6: Advanced Styling and Customization
# ============================================================================


def example_chart_styling() -> None:
    """
    Demonstrate chart styling and customization.

    Shows:
    - Custom color palettes
    - Plot area styling
    - Font customization
    - 3D effects
    - Style presets
    """
    from spreadsheet_dl.charts import ChartBuilder

    print("=" * 70)
    print("Example 6: Chart Styling and Customization")
    print("=" * 70)

    # 1. Custom color palette
    print("\n1. Chart with custom color palette:")
    chart = (
        ChartBuilder()
        .column_chart()
        .title(
            "Quarterly Results", font_size="16pt", font_weight="bold", color="#1F4E78"
        )
        .categories("Quarterly.A2:A5")
        .series("Q1", "Quarterly.B2:B5")
        .series("Q2", "Quarterly.C2:C5")
        .series("Q3", "Quarterly.D2:D5")
        .series("Q4", "Quarterly.E2:E5")
        .colors("#264478", "#4472C4", "#5B9BD5", "#8FAADC")  # Blue gradient
        .legend(position="bottom", font_size="11pt")
        .position("F2")
        .build()
    )

    print(f"   Title font size: {chart.title.font_size if chart.title else 'N/A'}")  # type: ignore[union-attr]
    print(f"   Title color: {chart.title.color if chart.title else 'N/A'}")  # type: ignore[union-attr]
    print(
        f"   Custom palette: {len(chart.color_palette) if chart.color_palette else 0} colors"
    )

    # 2. Plot area styling
    print("\n2. Chart with styled plot area:")
    chart = (
        ChartBuilder()
        .line_chart(markers=True)
        .title("Performance Metrics")
        .categories("Metrics.A2:A13")
        .series("Metric", "Metrics.B2:B13", color="#ED7D31")
        .plot_area(
            background="#F5F5F5",
            border_color="#CCCCCC",
            border_width="1pt",
        )
        .legend(visible=False)
        .position("F10")
        .build()
    )

    print(
        f"   Plot area background: {chart.plot_area.background_color if chart.plot_area else 'N/A'}"
    )
    print(
        f"   Plot area border: {chart.plot_area.border_color if chart.plot_area else 'N/A'}"
    )

    # 3. Chart with data labels
    print("\n3. Chart with formatted data labels:")
    chart = (
        ChartBuilder()
        .column_chart()
        .title("Top 5 Expenses")
        .categories("Top5.A2:A6")
        .series("Amount", "Top5.B2:B6", color="#ED7D31")
        .data_labels(
            show_value=True,
            position="outside",
            font_size="10pt",
            format_code="$#,##0",
        )
        .legend(visible=False)
        .position("F18")
        .size(400, 350)
        .build()
    )

    print(
        f"   Data labels: {chart.data_labels.show_value if chart.data_labels else False}"
    )
    print(
        f"   Label format: {chart.data_labels.format_code if chart.data_labels else 'N/A'}"
    )
    print(
        f"   Label position: {chart.data_labels.position.value if chart.data_labels else 'N/A'}"
    )

    # 4. 3D chart
    print("\n4. Chart with 3D effects:")
    chart = (
        ChartBuilder()
        .column_chart()
        .title("3D Budget Overview")
        .categories("Budget3D.A2:A6")
        .series("Amount", "Budget3D.B2:B6")
        .threed(True)
        .position("L2")
        .build()
    )

    print(f"   3D enabled: {chart.threed}")

    # 5. Styled combo chart
    print("\n5. Professional styled combo chart:")
    chart = (
        ChartBuilder()
        .combo_chart()
        .title(
            "Sales and Profit Analysis",
            font_size="18pt",
            font_weight="bold",
            color="#1F4E78",
        )
        .categories("Sales.A2:A13")
        .series("Sales", "Sales.B2:B13", chart_type="column", color="#4472C4")
        .series(
            "Profit Margin",
            "Sales.C2:C13",
            chart_type="line",
            secondary_axis=True,
            color="#ED7D31",
        )
        .value_axis(
            title="Sales ($)",
            min=0,
            format_code="$#,##0",
        )
        .axis(
            "secondary",
            title="Profit Margin (%)",
            min=0,
            max=50,
            format_code="0%",
        )
        .legend(position="top", font_size="11pt")
        .plot_area(background="#FFFFFF", border_color="#D9D9D9")
        .position("F26")
        .size(650, 400)
        .build()
    )

    print("   Professional styling applied")
    print(f"   Chart size: {chart.size.width}x{chart.size.height}px")

    print("\n✓ Chart styling demonstrated")
    print()


# ============================================================================
# Example 7: Real-World Budget Visualizations
# ============================================================================


def example_budget_visualizations() -> None:
    """
    Demonstrate real-world budget visualization scenarios.

    Shows:
    - Budget vs actual comparison
    - Spending by category pie chart
    - Trend analysis with forecast
    - Category breakdown with sparklines
    """
    from spreadsheet_dl.charts import (
        budget_comparison_chart,
        spending_pie_chart,
        trend_line_chart,
    )

    print("=" * 70)
    print("Example 7: Real-World Budget Visualizations")
    print("=" * 70)

    # 1. Budget comparison (pre-built template)
    print("\n1. Budget vs Actual comparison:")
    chart = budget_comparison_chart(
        categories="Budget.A2:A13",
        budget_values="Budget.B2:B13",
        actual_values="Budget.C2:C13",
        title="2025 Budget vs Actual",
        position="F2",
    )

    print(f"   Title: {chart.title.text if chart.title else 'N/A'}")  # type: ignore[union-attr]
    print(f"   Chart type: {chart.chart_type.name}")
    print(f"   Series: {', '.join(s.name for s in chart.series)}")

    # 2. Spending pie chart (pre-built template)
    print("\n2. Spending by category:")
    chart = spending_pie_chart(
        categories="Categories.A2:A8",
        values="Categories.B2:B8",
        title="January Spending Breakdown",
        position="L2",
    )

    print(f"   Chart type: {chart.chart_type.name}")
    print(
        f"   Shows percentages: {chart.data_labels.show_percentage if chart.data_labels else False}"
    )

    # 3. Trend analysis (pre-built template)
    print("\n3. Spending trend with forecast:")
    chart = trend_line_chart(
        categories="Trends.A2:A13",
        values="Trends.B2:B13",
        title="Monthly Spending Trend",
        position="F12",
        trendline=True,
    )

    print(f"   Chart type: {chart.chart_type.name}")
    print(f"   Has trendline: {chart.series[0].trendline is not None}")

    # 4. Custom budget dashboard chart
    print("\n4. Budget dashboard - variance analysis:")
    from spreadsheet_dl.charts import ChartBuilder

    chart = (
        ChartBuilder()
        .combo_chart()
        .title("Budget Variance Analysis", font_size="16pt", color="#1F4E78")
        .categories("Variance.A2:A8")
        .series("Budget", "Variance.B2:B8", chart_type="column", color="#A5A5A5")
        .series("Actual", "Variance.C2:C8", chart_type="column", color="#4472C4")
        .series(
            "Variance %",
            "Variance.D2:D8",
            chart_type="line",
            secondary_axis=True,
            color="#ED7D31",
        )
        .data_labels(show_value=False)  # Clean look
        .value_axis(title="Amount ($)", format_code="$#,##0")
        .axis(
            "secondary",
            title="Variance (%)",
            min=-50,
            max=50,
            format_code="0%",
        )
        .legend(position="top")
        .plot_area(background="#FAFAFA")
        .position("F22")
        .size(700, 400)
        .build()
    )

    print("   Dashboard chart created")
    print("   Visualizes: Budget, Actual, and Variance")
    print(f"   Size: {chart.size.width}x{chart.size.height}px")

    print("\n✓ Budget visualizations created")
    print()


# ============================================================================
# Example 8: Chart Positioning and Layout
# ============================================================================


def example_chart_positioning() -> None:
    """
    Demonstrate chart positioning and layout options.

    Shows:
    - Absolute positioning
    - Offset positioning
    - Chart sizing
    - Move with cells
    - Size with cells
    - Z-order for overlapping charts
    """
    from spreadsheet_dl.charts import ChartBuilder

    print("=" * 70)
    print("Example 8: Chart Positioning and Layout")
    print("=" * 70)

    # 1. Basic positioning
    print("\n1. Chart positioned at F2:")
    chart = (
        ChartBuilder()
        .column_chart()
        .title("Sales by Region")
        .categories("Sales.A2:A6")
        .series("Amount", "Sales.B2:B6")
        .position("F2")
        .size(400, 300)
        .build()
    )

    print(f"   Anchor cell: {chart.position.cell}")  # type: ignore[union-attr]
    print(f"   Size: {chart.size.width}x{chart.size.height}px")

    # 2. Positioning with offset
    print("\n2. Chart with offset positioning:")
    chart = (
        ChartBuilder()
        .line_chart()
        .title("Trend Analysis")
        .categories("Trends.A2:A13")
        .series("Value", "Trends.B2:B13")
        .position("F2", offset_x=20, offset_y=10)
        .size(500, 350)
        .build()
    )

    print(f"   Anchor cell: {chart.position.cell}")  # type: ignore[union-attr]
    print(f"   Offset: X={chart.position.offset_x}px, Y={chart.position.offset_y}px")  # type: ignore[union-attr]

    # 3. Chart that moves with cells
    print("\n3. Chart that moves with cells:")
    chart = (
        ChartBuilder()
        .pie_chart()
        .title("Distribution")
        .categories("Data.A2:A6")
        .series("Values", "Data.B2:B6")
        .position("F10", move_with_cells=True, size_with_cells=False)
        .build()
    )

    print(f"   Move with cells: {chart.position.move_with_cells}")  # type: ignore[union-attr]
    print(f"   Size with cells: {chart.position.size_with_cells}")  # type: ignore[union-attr]

    # 4. Multiple charts in a grid layout
    print("\n4. Creating dashboard grid layout:")
    positions = [
        ("F2", "Chart 1: Top-left"),
        ("L2", "Chart 2: Top-right"),
        ("F15", "Chart 3: Bottom-left"),
        ("L15", "Chart 4: Bottom-right"),
    ]

    for pos, desc in positions:
        chart = (
            ChartBuilder()
            .column_chart()
            .title(desc)
            .categories("Data.A2:A6")
            .series("Values", "Data.B2:B6")
            .position(pos)
            .size(350, 250)
            .build()
        )
        print(f"   {desc}: {pos}")

    # 5. Custom sizing
    print("\n5. Charts with different sizes:")
    sizes = [
        (300, 200, "Small"),
        (500, 350, "Medium"),
        (700, 450, "Large"),
    ]

    for width, height, size_name in sizes:
        chart = (
            ChartBuilder()
            .line_chart()
            .title(f"{size_name} Chart")
            .categories("Data.A2:A13")
            .series("Value", "Data.B2:B13")
            .size(width, height)
            .build()
        )
        print(f"   {size_name}: {width}x{height}px")

    print("\n✓ Chart positioning demonstrated")
    print()


# ============================================================================
# Main Example Runner
# ============================================================================


def main() -> None:
    """Run all chart builder examples."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print(
        "║" + "  Advanced Chart Builder Examples - SpreadsheetDL v4.0".center(68) + "║"
    )
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    try:
        # Run all examples
        example_column_charts()
        example_line_area_charts()
        example_pie_charts()
        example_combo_charts()
        example_sparklines()
        example_chart_styling()
        example_budget_visualizations()
        example_chart_positioning()

        print("=" * 70)
        print("All Chart Builder Examples Completed Successfully!")
        print("=" * 70)
        print()
        print("Key Features Demonstrated:")
        print("  • Multiple chart types: column, bar, line, area, pie, scatter, combo")
        print("  • Sparklines for inline data visualization")
        print("  • Trendline analysis with forecasting")
        print("  • Multi-series charts with secondary axes")
        print("  • Professional styling and customization")
        print("  • Flexible positioning and sizing")
        print("  • Pre-built budget visualization templates")
        print()
        print("ChartBuilder Benefits:")
        print("  • Fluent API for easy chart creation")
        print("  • No manual ODF XML manipulation required")
        print("  • Type-safe configuration with Python dataclasses")
        print("  • Reusable chart templates")
        print("  • Comprehensive styling options")
        print()

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
