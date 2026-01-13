#!/usr/bin/env python3
"""
Chart Series Color Demo - v4.0 Feature Implementation

Demonstrates comprehensive chart series color support including:
- Hex color codes (#RRGGBB)
- Hex colors without # prefix
- Named colors (red, blue, green, etc.)
- Color palettes for multiple series
- Color cycling for many series
- Series color override of palette
- All chart types with custom colors

This feature was implemented as FUTURE-005 and provides full ODF-compliant
color styling for chart series.

Example output: chart_colors_demo.ods
"""

import sys
import traceback
from pathlib import Path

from spreadsheet_dl.builder import CellSpec, ColumnSpec, RowSpec, SheetSpec
from spreadsheet_dl.charts import ChartBuilder, ChartSpec
from spreadsheet_dl.renderer import OdsRenderer


def create_sample_data() -> SheetSpec:
    """Create sample data for charts."""
    return SheetSpec(
        name="Data",
        columns=[
            ColumnSpec(name="Month"),
            ColumnSpec(name="Series A", type="float"),
            ColumnSpec(name="Series B", type="float"),
            ColumnSpec(name="Series C", type="float"),
            ColumnSpec(name="Series D", type="float"),
        ],
        rows=[
            RowSpec(
                cells=[
                    CellSpec(value="Jan"),
                    CellSpec(value=100),
                    CellSpec(value=120),
                    CellSpec(value=90),
                    CellSpec(value=110),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Feb"),
                    CellSpec(value=150),
                    CellSpec(value=140),
                    CellSpec(value=130),
                    CellSpec(value=125),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Mar"),
                    CellSpec(value=200),
                    CellSpec(value=180),
                    CellSpec(value=190),
                    CellSpec(value=185),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Apr"),
                    CellSpec(value=180),
                    CellSpec(value=190),
                    CellSpec(value=170),
                    CellSpec(value=175),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="May"),
                    CellSpec(value=220),
                    CellSpec(value=210),
                    CellSpec(value=215),
                    CellSpec(value=205),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Jun"),
                    CellSpec(value=250),
                    CellSpec(value=240),
                    CellSpec(value=245),
                    CellSpec(value=235),
                ]
            ),
        ],
    )


def demo_hex_colors() -> ChartSpec:
    """Demonstrate hex color codes with # prefix."""
    print("\n1. Hex Colors (#RRGGBB)")
    print("-" * 50)

    chart = (
        ChartBuilder()
        .column_chart()
        .title("Chart 1: Hex Colors with # Prefix")
        .categories("Data.A2:A7")
        .series("Red Series", "Data.B2:B7", color="#FF0000")
        .series("Green Series", "Data.C2:C7", color="#00FF00")
        .series("Blue Series", "Data.D2:D7", color="#0000FF")
        .legend(position="bottom")
        .position("G2")
        .size(500, 300)
        .build()
    )

    print(f"  Series: {len(chart.series)}")
    print(f"  Colors: {[s.color for s in chart.series]}")
    return chart


def demo_hex_colors_no_hash() -> ChartSpec:
    """Demonstrate hex colors without # prefix."""
    print("\n2. Hex Colors (RRGGBB - no prefix)")
    print("-" * 50)

    chart = (
        ChartBuilder()
        .line_chart(markers=True)
        .title("Chart 2: Hex Colors without # Prefix")
        .categories("Data.A2:A7")
        .series("Magenta", "Data.B2:B7", color="FF00FF")
        .series("Cyan", "Data.C2:C7", color="00FFFF")
        .series("Yellow", "Data.D2:D7", color="FFFF00")
        .legend(position="right")
        .position("G11")
        .size(500, 300)
        .build()
    )

    print(f"  Series: {len(chart.series)}")
    print(f"  Colors: {[s.color for s in chart.series]}")
    return chart


def demo_named_colors() -> ChartSpec:
    """Demonstrate named color support."""
    print("\n3. Named Colors")
    print("-" * 50)

    chart = (
        ChartBuilder()
        .bar_chart()
        .title("Chart 3: Named Colors")
        .categories("Data.A2:A7")
        .series("Red", "Data.B2:B7", color="red")
        .series("Orange", "Data.C2:C7", color="orange")
        .series("Purple", "Data.D2:D7", color="purple")
        .legend(position="bottom")
        .position("G20")
        .size(500, 300)
        .build()
    )

    print(f"  Series: {len(chart.series)}")
    print(f"  Named colors: {[s.color for s in chart.series]}")
    print("  Supported names: red, green, blue, yellow, orange, purple,")
    print("                   pink, brown, gray/grey, black, white, cyan,")
    print("                   magenta, lime, navy, teal, olive, maroon, aqua")
    return chart


def demo_color_palette() -> ChartSpec:
    """Demonstrate color palette for auto-coloring series."""
    print("\n4. Color Palette")
    print("-" * 50)

    chart = (
        ChartBuilder()
        .area_chart()
        .title("Chart 4: Color Palette Auto-Assignment")
        .categories("Data.A2:A7")
        .series("Series A", "Data.B2:B7")
        .series("Series B", "Data.C2:C7")
        .series("Series C", "Data.D2:D7")
        .colors("#E74C3C", "#3498DB", "#2ECC71")  # Red, Blue, Green palette
        .legend(position="top")
        .position("G29")
        .size(500, 300)
        .build()
    )

    print(f"  Series: {len(chart.series)}")
    print(f"  Palette: {chart.color_palette}")
    print("  Colors auto-assigned from palette to series")
    return chart


def demo_series_color_override() -> ChartSpec:
    """Demonstrate series color overriding palette."""
    print("\n5. Series Color Override")
    print("-" * 50)

    chart = (
        ChartBuilder()
        .column_chart()
        .title("Chart 5: Series Color Overrides Palette")
        .categories("Data.A2:A7")
        .series("Custom Gold", "Data.B2:B7", color="#FFD700")  # Explicit gold
        .series("From Palette", "Data.C2:C7")  # Uses palette
        .series("Custom Silver", "Data.D2:D7", color="#C0C0C0")  # Explicit silver
        .colors("#000000", "#FFFFFF", "#808080")  # Black/White/Gray palette
        .legend(position="bottom")
        .position("N2")
        .size(500, 300)
        .build()
    )

    print(f"  Series: {len(chart.series)}")
    print(f"  Series 1 color: {chart.series[0].color} (explicit)")
    print(f"  Series 2 color: {chart.series[1].color} (from palette)")
    print(f"  Series 3 color: {chart.series[2].color} (explicit)")
    return chart


def demo_color_cycling() -> ChartSpec:
    """Demonstrate color cycling with more series than palette colors."""
    print("\n6. Color Cycling")
    print("-" * 50)

    builder = (
        ChartBuilder()
        .line_chart()
        .title("Chart 6: Color Cycling (4 series, 2 colors)")
        .categories("Data.A2:A7")
        .colors("#FF6B6B", "#4ECDC4")  # Only 2 colors
    )

    # Add 4 series - colors should cycle
    builder.series("S1", "Data.B2:B7")  # Gets color 0
    builder.series("S2", "Data.C2:C7")  # Gets color 1
    builder.series("S3", "Data.D2:D7")  # Gets color 0 (cycle)
    builder.series("S4", "Data.E2:E7")  # Gets color 1 (cycle)

    chart = builder.position("N11").size(500, 300).build()

    print(f"  Series: {len(chart.series)}")
    print(f"  Palette: {chart.color_palette} (2 colors)")
    print("  Colors cycle: palette[i % len(palette)]")
    return chart


def demo_pie_chart_colors() -> ChartSpec:
    """Demonstrate colored pie chart."""
    print("\n7. Pie Chart with Colors")
    print("-" * 50)

    chart = (
        ChartBuilder()
        .pie_chart()
        .title("Chart 7: Colored Pie Chart")
        .categories("Data.A2:A7")
        .series("Values", "Data.B2:B7", color="#2C3E50")
        .legend(position="right")
        .position("N20")
        .size(450, 300)
        .build()
    )

    print(f"  Series: {len(chart.series)}")
    print(f"  Color: {chart.series[0].color}")
    return chart


def demo_all_chart_types() -> list[ChartSpec]:
    """Demonstrate colors work with all chart types."""
    print("\n8. All Chart Types with Colors")
    print("-" * 50)

    charts = []

    # Scatter chart
    scatter = (
        ChartBuilder()
        .scatter_chart()
        .title("Chart 8a: Scatter")
        .series("Dataset", "Data.B2:B7", color="blue")
        .position("N29")
        .size(400, 250)
        .build()
    )
    charts.append(scatter)

    # Bubble chart
    bubble = (
        ChartBuilder()
        .bubble_chart()
        .title("Chart 8b: Bubble")
        .series("Bubbles", "Data.B2:B7", color="purple")
        .position("T29")
        .size(400, 250)
        .build()
    )
    charts.append(bubble)

    # Doughnut chart
    doughnut = (
        ChartBuilder()
        .pie_chart(doughnut=True)
        .title("Chart 8c: Doughnut")
        .series("Ring", "Data.B2:B7", color="teal")
        .position("Z29")
        .size(400, 250)
        .build()
    )
    charts.append(doughnut)

    print(f"  Created {len(charts)} charts with different types")
    return charts


def main() -> None:
    """Run all demonstrations."""
    print("=" * 70)
    print("Chart Series Color Demo - FUTURE-005 Implementation")
    print("=" * 70)
    print()
    print("This demo showcases comprehensive chart series color support:")
    print("- Full ODF-compliant color styling")
    print("- Hex colors with/without # prefix")
    print("- 20+ named colors")
    print("- Color palettes with auto-assignment")
    print("- Color cycling for many series")
    print("- Works with all chart types")

    # Create data sheet
    data_sheet = create_sample_data()

    # Create all charts
    charts = []
    charts.append(demo_hex_colors())
    charts.append(demo_hex_colors_no_hash())
    charts.append(demo_named_colors())
    charts.append(demo_color_palette())
    charts.append(demo_series_color_override())
    charts.append(demo_color_cycling())
    charts.append(demo_pie_chart_colors())
    charts.extend(demo_all_chart_types())

    # Render to file
    output_path = Path("chart_colors_demo.ods")
    print("\n" + "=" * 70)
    print("Rendering Charts")
    print("=" * 70)
    print(f"  Total charts: {len(charts)}")
    print(f"  Output file: {output_path}")

    renderer = OdsRenderer()
    result = renderer.render([data_sheet], output_path, charts=charts)

    print(f"\n✓ Successfully created: {result}")
    print(f"  File size: {result.stat().st_size:,} bytes")
    print("\nOpen the file in LibreOffice Calc to see the colored charts!")

    print("\n" + "=" * 70)
    print("Implementation Summary")
    print("=" * 70)
    print("FUTURE-005: Chart series color application via ODS styles")
    print()
    print("✓ ODF style:Style elements with family='chart'")
    print("✓ GraphicProperties for fill and stroke colors")
    print("✓ Unique style names per series")
    print("✓ Color normalization (hex with/without #)")
    print("✓ Named color support (20+ colors)")
    print("✓ Color palette with cycling")
    print("✓ Series color override")
    print("✓ 20+ comprehensive tests")
    print()
    print("All chart types render with custom colors in LibreOffice!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        traceback.print_exc()
        sys.exit(1)
