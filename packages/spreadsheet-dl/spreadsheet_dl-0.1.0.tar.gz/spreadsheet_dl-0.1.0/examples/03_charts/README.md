# 03_charts - Data Visualization

Transform budget data into visual insights with charts and sparklines.

## Prerequisites

- **Completed**: [02_formulas](../02_formulas/) - Budget analysis and reporting
- **Skills needed**: Understanding of chart types and when to use them
- **Time**: 45 minutes

## Learning Objectives

By completing these examples, you'll learn how to:

1. **Create basic charts** - Pie, bar, and line charts
2. **Use ChartBuilder** - Advanced chart configuration with builder pattern
3. **Customize colors** - Apply color schemes and themes
4. **Add sparklines** - Create compact inline visualizations
5. **Position charts** - Control chart placement in spreadsheets
6. **Style visualizations** - Professional formatting and appearance

## Examples in This Section

### 01_basic_charts.py

**What it does**: Create fundamental chart types (pie, bar, line)

**Concepts covered**:

- Pie charts for category distribution
- Bar charts for comparisons
- Line charts for trends over time
- Chart positioning in spreadsheet cells
- Basic chart configuration
- Data range specification

**Run it**:

```bash
uv run python examples/03_charts/01_basic_charts.py
```

**Expected output**: `output/budget_with_charts.ods` containing multiple chart types

**Key code**:

```python
from spreadsheet_dl import ChartBuilder, ChartType

# Create a pie chart
chart = ChartBuilder.create(ChartType.PIE) \
    .with_title("Spending by Category") \
    .with_data_range("A2:B10") \
    .build()
```

---

### 02_chart_builder_advanced.py

**What it does**: Demonstrate advanced ChartBuilder features

**Concepts covered**:

- Builder pattern for chart construction
- Custom legends and labels
- Axis configuration (min/max, labels)
- Multiple data series
- Chart sizing and positioning
- 3D chart effects
- Data point markers

**Run it**:

```bash
uv run python examples/03_charts/02_chart_builder_advanced.py
```

**Expected output**: `output/advanced_charts.ods` with sophisticated visualizations

**Key code**:

```python
chart = ChartBuilder.create(ChartType.COLUMN) \
    .with_title("Monthly Budget Comparison") \
    .with_subtitle("Actual vs. Planned") \
    .with_data_range("A1:C13") \
    .with_legend(position="right") \
    .with_x_axis(title="Month") \
    .with_y_axis(title="Amount ($)", min=0, max=5000) \
    .with_size(width=600, height=400) \
    .build()
```

---

### 03_chart_colors.py

**What it does**: Apply color schemes and custom colors to charts

**Concepts covered**:

- Predefined color schemes
- Custom color palettes
- Theme application
- Brand color consistency
- Accessibility considerations
- Color gradient generation

**Run it**:

```bash
uv run python examples/03_charts/03_chart_colors.py
```

**Expected output**: `output/colored_charts.ods` with various color schemes

**Color schemes available**:

- **Professional**: Blues, greens, corporate colors
- **Vibrant**: Bright, high-contrast colors
- **Pastel**: Soft, muted tones
- **Monochrome**: Grayscale variations
- **Custom**: Your own hex color lists

**Key code**:

```python
from spreadsheet_dl import ColorScheme

chart = ChartBuilder.create(ChartType.PIE) \
    .with_title("Spending Categories") \
    .with_color_scheme(ColorScheme.PROFESSIONAL) \
    .build()

# Or custom colors
chart = ChartBuilder.create(ChartType.BAR) \
    .with_colors(["#FF5733", "#33FF57", "#3357FF"]) \
    .build()
```

---

### 04_sparklines.py

**What it does**: Create compact sparkline visualizations in cells

**Concepts covered**:

- Sparkline types (line, bar, win/loss)
- Inline data visualization
- Trend indicators
- Cell-based charts
- Compact formatting
- Quick visual summaries

**Run it**:

```bash
uv run python examples/03_charts/04_sparklines.py
```

**Expected output**: `output/budget_with_sparklines.ods` with sparklines in cells

**Use cases**:

- **Line sparklines**: Show spending trends over time
- **Bar sparklines**: Compare category amounts
- **Win/loss sparklines**: Track over/under budget status

**Key code**:

```python
from spreadsheet_dl import SparklineBuilder, SparklineType

# Line sparkline for trend
sparkline = SparklineBuilder.create(SparklineType.LINE) \
    .with_data_range("B2:B13") \
    .with_color("#4CAF50") \
    .build()

# Position in cell
sheet.add_sparkline(sparkline, cell="M2")
```

## Key Concepts

### ChartBuilder

Fluent builder pattern for chart creation:

```python
from spreadsheet_dl import ChartBuilder, ChartType

chart = ChartBuilder.create(ChartType.PIE) \
    .with_title("Chart Title") \
    .with_subtitle("Optional subtitle") \
    .with_data_range("A1:B10") \
    .with_legend(position="bottom") \
    .with_size(width=500, height=300) \
    .at_position(row=2, col=5) \
    .build()
```

### Chart Types

Available chart types:

```python
ChartType.PIE          # Pie chart - show proportions
ChartType.BAR          # Horizontal bar chart - compare items
ChartType.COLUMN       # Vertical column chart - compare over time
ChartType.LINE         # Line chart - show trends
ChartType.AREA         # Area chart - show cumulative totals
ChartType.SCATTER      # Scatter plot - show correlations
ChartType.BUBBLE       # Bubble chart - 3D data visualization
```

### Positioning Charts

Control where charts appear:

```python
# Absolute positioning
chart.at_position(row=5, col=8)  # Cell H5

# Or specify cell reference
chart.at_cell("H5")

# Size control
chart.with_size(width=600, height=400)  # pixels
```

### Sparklines

Compact visualizations in cells:

```python
from spreadsheet_dl import SparklineBuilder, SparklineType

# Line sparkline
sparkline = SparklineBuilder.create(SparklineType.LINE) \
    .with_data_range("B2:M2") \
    .with_min_max_markers(True) \
    .with_color("#2196F3") \
    .build()

# Bar sparkline
sparkline = SparklineBuilder.create(SparklineType.BAR) \
    .with_data_range("B3:M3") \
    .with_color("#FF9800") \
    .build()

# Win/loss sparkline (positive/negative)
sparkline = SparklineBuilder.create(SparklineType.WIN_LOSS) \
    .with_data_range("B4:M4") \
    .with_positive_color("#4CAF50") \
    .with_negative_color("#F44336") \
    .build()
```

## Chart Selection Guide

**Use Pie Charts when**:

- Showing parts of a whole (budget categories)
- Less than 7 categories
- Proportions are important

**Use Bar/Column Charts when**:

- Comparing discrete items
- Labels are long (use horizontal bars)
- Showing time series (use vertical columns)

**Use Line Charts when**:

- Showing trends over time
- Continuous data
- Multiple series comparison

**Use Sparklines when**:

- Space is limited
- Quick visual summary needed
- Embedded in tables

## Estimated Time

- **Quick review**: 10 minutes (read code, view examples)
- **Run all examples**: 15 minutes
- **Hands-on practice**: 45 minutes (create custom charts)

## Common Issues

**Issue**: Charts not appearing in spreadsheet
**Solution**: Check data range references are correct (e.g., "A2:B10")

**Issue**: Chart overlaps with data
**Solution**: Position charts carefully with `.at_position()` or `.at_cell()`

**Issue**: Colors not displaying as expected
**Solution**: Use hex color codes (#RRGGBB) or predefined ColorScheme enums

**Issue**: Sparklines showing errors
**Solution**: Ensure data range contains numeric values only

**Issue**: Chart too small/large
**Solution**: Adjust with `.with_size(width=pixels, height=pixels)`

## Tips and Best Practices

1. **Choose the right chart type** for your data:

   ```python
   # Proportions -> Pie
   # Comparisons -> Bar/Column
   # Trends -> Line
   # Quick summary -> Sparkline
   ```

2. **Use consistent colors** across related charts:

   ```python
   brand_colors = ["#1E88E5", "#FFC107", "#43A047"]
   chart1.with_colors(brand_colors)
   chart2.with_colors(brand_colors)
   ```

3. **Add clear titles** to every chart:

   ```python
   chart.with_title("Clear, Descriptive Title") \
        .with_subtitle("Additional context if needed")
   ```

4. **Position charts strategically**:

   ```python
   # Leave space between data and charts
   chart.at_position(row=2, col=10)  # Column J, away from data
   ```

5. **Test with real data** to ensure scaling works:

   ```python
   # Set axis ranges explicitly if needed
   chart.with_y_axis(min=0, max=10000)
   ```

## Next Steps

Ready to extend SpreadsheetDL? Move on to:

**[04_advanced](../04_advanced/)** - Learn about plugin systems, MCP integration, and custom extensions

## Additional Resources

- [ChartBuilder API Reference](../../docs/api/_builder/core.md)
- [Chart Examples Gallery](../../docs/examples/gallery.md)
- [Color Scheme Reference](../../docs/guides/styling.md)
- [ODF Chart Specification](https://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html#__RefHeading__1415330_253892949)

## Questions?

- Review chart examples in the gallery
- Check API documentation for detailed options
- Open an issue on GitHub for bugs or feature requests
