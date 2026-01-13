"""Charts and visualization support for SpreadsheetDL.

Provides a fluent API for creating charts with data series,
axis configuration, legends, and styling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Self

# ============================================================================
# Enums
# ============================================================================


class ChartType(Enum):
    """Chart type enumeration."""

    # Column charts
    COLUMN = auto()
    COLUMN_STACKED = auto()
    COLUMN_100_STACKED = auto()
    COLUMN_PERCENT_STACKED = auto()  # Alias for 100% stacked

    # Bar charts
    BAR = auto()
    BAR_STACKED = auto()
    BAR_100_STACKED = auto()
    BAR_CLUSTERED = auto()  # Alias for standard bar

    # Line charts
    LINE = auto()
    LINE_MARKERS = auto()
    LINE_SMOOTH = auto()

    # Area charts
    AREA = auto()
    AREA_STACKED = auto()
    AREA_100_STACKED = auto()

    # Pie charts
    PIE = auto()
    PIE_EXPLODED = auto()
    DOUGHNUT = auto()

    # Other
    SCATTER = auto()
    SCATTER_LINES = auto()
    BUBBLE = auto()
    COMBO = auto()  # Column + Line combination


class LegendPosition(Enum):
    """Legend position options."""

    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    NONE = "none"


class AxisType(Enum):
    """Axis type enumeration."""

    CATEGORY = "category"  # X-axis typically
    VALUE = "value"  # Y-axis typically
    SECONDARY_VALUE = "secondary_value"  # Secondary Y-axis


class DataLabelPosition(Enum):
    """Data label position options."""

    INSIDE = "inside"
    OUTSIDE = "outside"
    CENTER = "center"
    ABOVE = "above"
    BELOW = "below"
    LEFT = "left"
    RIGHT = "right"


class TrendlineType(Enum):
    """Trendline type enumeration."""

    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    POLYNOMIAL = "polynomial"
    POWER = "power"
    MOVING_AVERAGE = "moving_average"


class SparklineType(Enum):
    """Sparkline type enumeration."""

    LINE = "line"
    COLUMN = "column"
    WIN_LOSS = "win_loss"


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class ChartTitle:
    """Chart title configuration.

    Attributes:
        text: Title text
        font_family: Font family name
        font_size: Font size (e.g., "14pt")
        font_weight: Font weight (normal, bold)
        color: Text color (hex)
        position: Position (top, bottom, none)
    """

    text: str
    font_family: str | None = None
    font_size: str = "14pt"
    font_weight: str = "bold"
    color: str | None = None
    position: str = "top"


@dataclass(slots=True)
class AxisConfig:
    """Axis configuration for chart axes.

    Uses __slots__ for memory efficiency.

    Attributes:
        axis_type: Type of axis (category, value, secondary_value)
        title: Axis title text
        title_font_size: Title font size
        min_value: Minimum axis value (None for auto)
        max_value: Maximum axis value (None for auto)
        major_interval: Major gridline interval
        minor_interval: Minor gridline interval
        major_gridlines: Show major gridlines
        minor_gridlines: Show minor gridlines
        format_code: Number format code
        reversed: Reverse axis direction
        logarithmic: Use logarithmic scale
    """

    axis_type: AxisType = AxisType.VALUE
    title: str | None = None
    title_font_size: str = "11pt"
    min_value: float | None = None
    max_value: float | None = None
    major_interval: float | None = None
    minor_interval: float | None = None
    major_gridlines: bool = True
    minor_gridlines: bool = False
    format_code: str | None = None
    reversed: bool = False
    logarithmic: bool = False


@dataclass
class LegendConfig:
    """Legend configuration.

    Attributes:
        position: Legend position
        visible: Whether legend is visible
        font_family: Font family
        font_size: Font size
        overlay: Whether legend overlays chart
    """

    position: LegendPosition = LegendPosition.BOTTOM
    visible: bool = True
    font_family: str | None = None
    font_size: str = "10pt"
    overlay: bool = False


@dataclass
class DataLabelConfig:
    """Data label configuration.

    Attributes:
        show_value: Show value on label
        show_percentage: Show percentage (pie charts)
        show_category: Show category name
        show_series: Show series name
        position: Label position
        font_size: Font size
        format_code: Number format code
        separator: Separator between label parts
    """

    show_value: bool = False
    show_percentage: bool = False
    show_category: bool = False
    show_series: bool = False
    position: DataLabelPosition = DataLabelPosition.OUTSIDE
    font_size: str = "9pt"
    format_code: str | None = None
    separator: str = ", "


@dataclass
class Trendline:
    """Trendline configuration.

    Attributes:
        type: Trendline type
        order: Polynomial order (for polynomial type)
        period: Moving average period
        forward_periods: Number of periods to forecast forward
        backward_periods: Number of periods to forecast backward
        intercept: Force intercept value
        display_equation: Show equation on chart
        display_r_squared: Show R-squared value
        color: Trendline color (hex)
        width: Line width
        dash_style: Line dash style
    """

    type: TrendlineType = TrendlineType.LINEAR
    order: int = 2  # For polynomial
    period: int = 2  # For moving average
    forward_periods: int = 0
    backward_periods: int = 0
    intercept: float | None = None
    display_equation: bool = False
    display_r_squared: bool = False
    color: str | None = None
    width: str = "1pt"
    dash_style: str = "solid"


@dataclass(slots=True)
class DataSeries:
    """Chart data series configuration.

    Uses __slots__ for memory efficiency.

    Attributes:
        name: Series name (for legend)
        values: Range reference for values (e.g., "Sheet.B2:B20")
        categories: Range reference for categories (optional)
        color: Series color (hex, None for auto)
        secondary_axis: Use secondary Y-axis
        chart_type: Override chart type for combo charts
        data_labels: Data label configuration
        trendline: Trendline configuration
        marker_style: Marker style for line/scatter
        line_width: Line width for line charts
        fill_opacity: Fill opacity for area charts
    """

    name: str
    values: str
    categories: str | None = None
    color: str | None = None
    secondary_axis: bool = False
    chart_type: ChartType | None = None  # For combo charts
    data_labels: DataLabelConfig | None = None
    trendline: Trendline | None = None
    marker_style: str | None = None
    line_width: str = "2pt"
    fill_opacity: float = 0.8


@dataclass
class ChartPosition:
    """Chart position configuration.

    Attributes:
        cell: Anchor cell reference (e.g., "F2")
        offset_x: Horizontal offset in pixels
        offset_y: Vertical offset in pixels
        move_with_cells: Move chart when cells are resized
        size_with_cells: Size chart when cells are resized
        z_order: Z-order for overlapping charts
    """

    cell: str = "A1"
    offset_x: int = 0
    offset_y: int = 0
    move_with_cells: bool = True
    size_with_cells: bool = False
    z_order: int = 0


@dataclass
class ChartSize:
    """Chart size configuration.

    Attributes:
        width: Width in pixels
        height: Height in pixels
    """

    width: int = 400
    height: int = 300


@dataclass
class PlotAreaStyle:
    """Plot area styling.

    Attributes:
        background_color: Background color (hex)
        border_color: Border color (hex)
        border_width: Border width
    """

    background_color: str | None = None
    border_color: str | None = None
    border_width: str = "1pt"


# ============================================================================
# Sparklines
# ============================================================================


@dataclass
class SparklineMarkers:
    """Sparkline marker configuration.

    Attributes:
        high: Color for highest point (or True for default color)
        low: Color for lowest point (or True for default color)
        first: Color for first point (or True for default color)
        last: Color for last point (or True for default color)
        negative: Color for negative values (or True for default color)
    """

    high: str | bool | None = None
    low: str | bool | None = None
    first: str | bool | None = None
    last: str | bool | None = None
    negative: str | bool | None = None

    def __post_init__(self) -> None:
        """Convert bool markers to default color."""
        if self.high is True:
            self.high = "#FF0000"  # Default red for high
        if self.low is True:
            self.low = "#0000FF"  # Default blue for low
        if self.first is True:
            self.first = "#00FF00"  # Default green for first
        if self.last is True:
            self.last = "#FFA500"  # Default orange for last
        if self.negative is True:
            self.negative = "#FF0000"  # Default red for negative


@dataclass
class Sparkline:
    """Sparkline configuration.

    Attributes:
        type: Sparkline type (line, column, win_loss)
        data_range: Data range (can include {row} placeholder)
        location: Cell location where sparkline should be placed (e.g., "F2")
        color: Main sparkline color
        negative_color: Color for negative values
        markers: Marker configuration
        colors: Comprehensive color configuration (SparklineColors) - converted to color/markers
        min_axis: Minimum axis value (None for auto)
        max_axis: Maximum axis value (None for auto)
        same_scale: Use same scale for group
        show_axis: Show horizontal axis
        right_to_left: Display right to left
    """

    type: SparklineType = SparklineType.LINE
    data_range: str = ""
    location: str = ""
    color: str = "#4472C4"
    negative_color: str = "#FF0000"
    markers: SparklineMarkers | None = None
    colors: SparklineColors | None = field(default=None, repr=False)
    min_axis: float | None = None
    max_axis: float | None = None
    same_scale: bool = False
    show_axis: bool = False
    right_to_left: bool = False

    def __post_init__(self) -> None:
        """Convert colors parameter to color/markers if provided."""
        if self.colors is not None:
            self.color = self.colors.series
            self.negative_color = self.colors.negative
            if self.colors.markers is not None:
                self.markers = self.colors.markers


# Alias for backwards compatibility with tests
SparklineSpec = Sparkline


@dataclass
class SparklineColors:
    """Sparkline color configuration.

    Attributes:
        series: Main sparkline color
        negative: Color for negative values
        axis: Axis line color
        markers: Marker colors (high, low, first, last, negative points)
        background: Background fill color
        high: Color for highest point (shorthand for markers.high)
        low: Color for lowest point (shorthand for markers.low)
        first: Color for first point (shorthand for markers.first)
        last: Color for last point (shorthand for markers.last)
    """

    series: str = "#4472C4"
    negative: str = "#FF0000"
    axis: str | None = None
    markers: SparklineMarkers | None = None
    background: str | None = None
    high: str | None = None
    low: str | None = None
    first: str | None = None
    last: str | None = None

    def __post_init__(self) -> None:
        """Merge shorthand color fields into markers if provided."""
        if any([self.high, self.low, self.first, self.last]):
            if self.markers is None:
                self.markers = SparklineMarkers()
            if self.high is not None:
                self.markers.high = self.high
            if self.low is not None:
                self.markers.low = self.low
            if self.first is not None:
                self.markers.first = self.first
            if self.last is not None:
                self.markers.last = self.last


@dataclass
class DataRange:
    """Data range specification for charts and sparklines.

    Attributes:
        sheet: Sheet name (optional)
        start_cell: Starting cell reference (e.g., "A1")
        end_cell: Ending cell reference (e.g., "D10")
        range_string: Full range string (e.g., "Sheet1!A1:D10")
        categories: Category labels range (e.g., "A2:A6")
        values: Data values range - can be single string or list of strings for multiple series
    """

    sheet: str | None = None
    start_cell: str = ""
    end_cell: str = ""
    range_string: str = ""
    categories: str = ""
    values: str | list[str] = ""

    def __post_init__(self) -> None:
        """Build range_string if not provided and normalize values."""
        if not self.range_string and self.start_cell and self.end_cell:
            if self.sheet:
                self.range_string = f"{self.sheet}!{self.start_cell}:{self.end_cell}"
            else:
                self.range_string = f"{self.start_cell}:{self.end_cell}"

        # Convert list of values to comma-separated string for compatibility
        if isinstance(self.values, list):
            # Keep as list for now - downstream code can handle it
            pass


# ============================================================================
# Chart Specification
# ============================================================================


@dataclass
class ChartSpec:
    """Complete chart specification.

    This is the output of ChartBuilder and contains all configuration needed
    to render a chart. Can be constructed directly with simple arguments or
    through ChartBuilder for more complex configurations.

    Attributes:
        chart_type: Type of chart (can use 'type' as alias)
        title: Chart title configuration (str or ChartTitle)
        series: List of data series
        categories: Default category range for all series
        legend: Legend configuration (bool or LegendConfig)
        category_axis: Category (X) axis configuration
        value_axis: Value (Y) axis configuration
        secondary_axis: Secondary Y axis configuration
        position: Chart position (str or ChartPosition)
        size: Chart size
        plot_area: Plot area styling
        data_labels: Default data label configuration
        style_preset: Theme style preset name
        color_palette: Custom color palette
        threed: Enable 3D effects
        data: Simplified data specification (DataRange) - auto-converted to series
    """

    chart_type: ChartType = ChartType.COLUMN
    title: ChartTitle | str | None = None
    series: list[DataSeries] = field(default_factory=list)
    categories: str | None = None
    legend: LegendConfig | bool = field(default_factory=LegendConfig)
    category_axis: AxisConfig | None = None
    value_axis: AxisConfig | None = None
    secondary_axis: AxisConfig | None = None
    position: ChartPosition | str = field(default_factory=ChartPosition)
    size: ChartSize = field(default_factory=ChartSize)
    plot_area: PlotAreaStyle | None = None
    data_labels: DataLabelConfig | None = None
    style_preset: str | None = None
    color_palette: list[str] | None = None
    threed: bool = False
    # Simplified API fields (aliases/helpers)
    type: ChartType | None = field(default=None, repr=False)  # Alias for chart_type
    data: DataRange | None = field(default=None, repr=False)  # Simplified data spec
    width: int | None = field(default=None, repr=False)  # Alias for size.width
    height: int | None = field(default=None, repr=False)  # Alias for size.height
    legend_position: str | LegendPosition | None = field(
        default=None, repr=False
    )  # Alias for legend.position
    x_axis: AxisConfig | None = field(
        default=None, repr=False
    )  # Alias for category_axis
    y_axis: AxisConfig | None = field(default=None, repr=False)  # Alias for value_axis
    show_gridlines: bool | None = field(
        default=None, repr=False
    )  # Shorthand for axis gridlines

    def __post_init__(self) -> None:
        """Convert simplified arguments to full specifications."""
        # Handle 'type' alias for 'chart_type'
        if self.type is not None:
            self.chart_type = self.type

        # Handle width/height aliases for size
        if self.width is not None or self.height is not None:
            self.size = ChartSize(
                width=self.width if self.width is not None else self.size.width,
                height=self.height if self.height is not None else self.size.height,
            )

        # Handle x_axis/y_axis aliases
        if self.x_axis is not None:
            self.category_axis = self.x_axis
        if self.y_axis is not None:
            self.value_axis = self.y_axis

        # Convert string title to ChartTitle
        if isinstance(self.title, str):
            self.title = ChartTitle(text=self.title)

        # Convert string position to ChartPosition
        if isinstance(self.position, str):
            self.position = ChartPosition(cell=self.position)

        # Convert bool legend to LegendConfig
        if isinstance(self.legend, bool):
            self.legend = LegendConfig(visible=self.legend)

        # Handle legend_position alias
        if self.legend_position is not None and isinstance(self.legend, LegendConfig):
            if isinstance(self.legend_position, str):
                self.legend.position = LegendPosition(self.legend_position)
            else:
                self.legend.position = self.legend_position

        # Handle show_gridlines shorthand
        if self.show_gridlines is not None:
            if self.value_axis is not None:
                self.value_axis.major_gridlines = self.show_gridlines
            elif self.category_axis is not None:
                self.category_axis.major_gridlines = self.show_gridlines

        # Convert DataRange to series if provided
        if self.data is not None and hasattr(self.data, "categories"):
            # Create a data series from the DataRange
            if hasattr(self.data, "values"):
                values = self.data.values
                # Handle list of values (multiple series)
                if isinstance(values, list):
                    for i, val in enumerate(values):
                        self.series.append(
                            DataSeries(
                                name=f"Series {i + 1}",
                                values=val,
                                categories=self.data.categories
                                if hasattr(self.data, "categories")
                                else None,
                            )
                        )
                else:
                    # Single value string
                    self.series.append(
                        DataSeries(
                            name="Data",
                            values=values,
                            categories=self.data.categories
                            if hasattr(self.data, "categories")
                            else None,
                        )
                    )
            if hasattr(self.data, "categories"):
                self.categories = self.data.categories


# ============================================================================
# ChartBuilder
# ============================================================================


class ChartBuilder:
    r"""Fluent builder for creating charts.

    Provides a chainable API for building chart specifications
    with support for:
    - Multiple chart types
    - Data series configuration
    - Axis configuration
    - Legend and title
    - Positioning and sizing

    Examples:
        # Simple column chart
        chart = ChartBuilder() \\
            .column_chart() \\
            .title("Monthly Budget") \\
            .series("Budget", "Sheet.B2:B13") \\
            .series("Actual", "Sheet.C2:C13") \\
            .categories("Sheet.A2:A13") \\
            .legend(position="bottom") \\
            .position("F2") \\
            .size(400, 300) \\
            .build()

        # Pie chart with data labels
        pie = ChartBuilder() \\
            .pie_chart() \\
            .title("Spending by Category") \\
            .series("Amount", "Data.B2:B10") \\
            .categories("Data.A2:A10") \\
            .data_labels(show_percentage=True) \\
            .build()

        # Combo chart with secondary axis
        combo = ChartBuilder() \\
            .combo_chart() \\
            .series("Revenue", "Data.B:B", chart_type="column") \\
            .series("Growth Rate", "Data.C:C", chart_type="line", secondary_axis=True) \\
            .build()
    """

    def __init__(self) -> None:
        """Initialize chart builder."""
        self._spec = ChartSpec()
        self._current_series: DataSeries | None = None

    # =========================================================================
    # Chart Type Selection (AC1-AC7)
    # =========================================================================

    def column_chart(self, stacked: bool = False, percent: bool = False) -> Self:
        """Set chart type to column.

        Args:
            stacked: Use stacked columns
            percent: Use 100% stacked (requires stacked=True)

        Returns:
            Self for chaining
        """
        if percent:
            self._spec.chart_type = ChartType.COLUMN_100_STACKED
        elif stacked:
            self._spec.chart_type = ChartType.COLUMN_STACKED
        else:
            self._spec.chart_type = ChartType.COLUMN
        return self

    def bar_chart(self, stacked: bool = False, percent: bool = False) -> Self:
        """Set chart type to bar (horizontal columns).

        Args:
            stacked: Use stacked bars
            percent: Use 100% stacked

        Returns:
            Self for chaining
        """
        if percent:
            self._spec.chart_type = ChartType.BAR_100_STACKED
        elif stacked:
            self._spec.chart_type = ChartType.BAR_STACKED
        else:
            self._spec.chart_type = ChartType.BAR
        return self

    def line_chart(self, markers: bool = False, smooth: bool = False) -> Self:
        """Set chart type to line.

        Args:
            markers: Show data point markers
            smooth: Use smooth/curved lines

        Returns:
            Self for chaining
        """
        if smooth:
            self._spec.chart_type = ChartType.LINE_SMOOTH
        elif markers:
            self._spec.chart_type = ChartType.LINE_MARKERS
        else:
            self._spec.chart_type = ChartType.LINE
        return self

    def area_chart(self, stacked: bool = False, percent: bool = False) -> Self:
        """Set chart type to area.

        Args:
            stacked: Use stacked areas
            percent: Use 100% stacked

        Returns:
            Self for chaining
        """
        if percent:
            self._spec.chart_type = ChartType.AREA_100_STACKED
        elif stacked:
            self._spec.chart_type = ChartType.AREA_STACKED
        else:
            self._spec.chart_type = ChartType.AREA
        return self

    def pie_chart(self, doughnut: bool = False) -> Self:
        """Set chart type to pie.

        Args:
            doughnut: Use doughnut style

        Returns:
            Self for chaining
        """
        if doughnut:
            self._spec.chart_type = ChartType.DOUGHNUT
        else:
            self._spec.chart_type = ChartType.PIE
        return self

    def scatter_chart(self, lines: bool = False) -> Self:
        """Set chart type to scatter.

        Args:
            lines: Connect points with lines

        Returns:
            Self for chaining
        """
        if lines:
            self._spec.chart_type = ChartType.SCATTER_LINES
        else:
            self._spec.chart_type = ChartType.SCATTER
        return self

    def bubble_chart(self) -> Self:
        """Set chart type to bubble."""
        self._spec.chart_type = ChartType.BUBBLE
        return self

    def combo_chart(self) -> Self:
        """Set chart type to combo (column + line)."""
        self._spec.chart_type = ChartType.COMBO
        return self

    # =========================================================================
    # Title and Labels (AC1, AC4)
    # =========================================================================

    def title(
        self,
        text: str,
        *,
        font_size: str = "14pt",
        font_weight: str = "bold",
        color: str | None = None,
        position: str = "top",
    ) -> Self:
        """Set chart title.

        Args:
            text: Title text
            font_size: Font size
            font_weight: Font weight (normal, bold)
            color: Text color (hex)
            position: Position (top, bottom)

        Returns:
            Self for chaining
        """
        self._spec.title = ChartTitle(
            text=text,
            font_size=font_size,
            font_weight=font_weight,
            color=color,
            position=position,
        )
        return self

    def data_labels(
        self,
        *,
        show_value: bool = False,
        show_percentage: bool = False,
        show_category: bool = False,
        show_series: bool = False,
        position: str = "outside",
        font_size: str = "9pt",
        format_code: str | None = None,
    ) -> Self:
        """Configure data labels for all series.

        Args:
            show_value: Show value on label
            show_percentage: Show percentage
            show_category: Show category name
            show_series: Show series name
            position: Label position
            font_size: Font size
            format_code: Number format

        Returns:
            Self for chaining
        """
        pos_enum = (
            DataLabelPosition(position) if isinstance(position, str) else position
        )
        self._spec.data_labels = DataLabelConfig(
            show_value=show_value,
            show_percentage=show_percentage,
            show_category=show_category,
            show_series=show_series,
            position=pos_enum,
            font_size=font_size,
            format_code=format_code,
        )
        return self

    # =========================================================================
    # Data Series (AC1-AC5)
    # =========================================================================

    def series(
        self,
        name: str,
        values: str,
        *,
        color: str | None = None,
        secondary_axis: bool = False,
        chart_type: str | ChartType | None = None,
        trendline: str | None = None,
    ) -> Self:
        """Add a data series.

        Args:
            name: Series name (for legend)
            values: Range reference for values (e.g., "Sheet.B2:B20")
            color: Series color (hex)
            secondary_axis: Use secondary Y-axis
            chart_type: Override chart type for combo charts
            trendline: Trendline type (linear, exponential, etc.)

        Returns:
            Self for chaining
        """
        # Parse chart_type if string
        ct = None
        if chart_type is not None:
            if isinstance(chart_type, str):
                chart_type_map = {
                    "column": ChartType.COLUMN,
                    "bar": ChartType.BAR,
                    "line": ChartType.LINE,
                    "area": ChartType.AREA,
                }
                ct = chart_type_map.get(chart_type.lower())
            else:
                ct = chart_type

        # Parse trendline if string
        trend = None
        if trendline:
            trend = Trendline(type=TrendlineType(trendline.lower()))

        series = DataSeries(
            name=name,
            values=values,
            color=color,
            secondary_axis=secondary_axis,
            chart_type=ct,
            trendline=trend,
        )
        self._spec.series.append(series)
        self._current_series = series
        return self

    def series_color(self, color: str) -> Self:
        """Set color for the last added series.

        Args:
            color: Hex color

        Returns:
            Self for chaining
        """
        if self._current_series:
            self._current_series.color = color
        return self

    def series_trendline(
        self,
        type: str = "linear",
        *,
        forward_periods: int = 0,
        backward_periods: int = 0,
        display_equation: bool = False,
        display_r_squared: bool = False,
    ) -> Self:
        """Add trendline to the last added series.

        Args:
            type: Trendline type
            forward_periods: Forecast forward
            backward_periods: Forecast backward
            display_equation: Show equation
            display_r_squared: Show R-squared

        Returns:
            Self for chaining
        """
        if self._current_series:
            self._current_series.trendline = Trendline(
                type=TrendlineType(type.lower()),
                forward_periods=forward_periods,
                backward_periods=backward_periods,
                display_equation=display_equation,
                display_r_squared=display_r_squared,
            )
        return self

    def categories(self, range_ref: str) -> Self:
        """Set category range for all series.

        Args:
            range_ref: Range reference (e.g., "Sheet.A2:A20")

        Returns:
            Self for chaining
        """
        self._spec.categories = range_ref
        return self

    # =========================================================================
    # Legend Configuration (AC2)
    # =========================================================================

    def legend(
        self,
        *,
        position: str = "bottom",
        visible: bool = True,
        font_size: str = "10pt",
        overlay: bool = False,
    ) -> Self:
        """Configure chart legend.

        Args:
            position: Legend position (top, bottom, left, right, none)
            visible: Whether legend is visible
            font_size: Font size
            overlay: Whether legend overlays chart

        Returns:
            Self for chaining
        """
        pos_enum = (
            LegendPosition(position) if position != "none" else LegendPosition.NONE
        )
        self._spec.legend = LegendConfig(
            position=pos_enum,
            visible=visible and position != "none",
            font_size=font_size,
            overlay=overlay,
        )
        return self

    # =========================================================================
    # Axis Configuration (AC3)
    # =========================================================================

    def axis(
        self,
        axis_type: str,
        *,
        title: str | None = None,
        min: float | None = None,
        max: float | None = None,
        interval: float | None = None,
        format_code: str | None = None,
        gridlines: bool = True,
        logarithmic: bool = False,
    ) -> Self:
        """Configure an axis.

        Args:
            axis_type: Axis type ("category", "value", "secondary")
            title: Axis title
            min: Minimum value
            max: Maximum value
            interval: Major gridline interval
            format_code: Number format
            gridlines: Show gridlines
            logarithmic: Use logarithmic scale

        Returns:
            Self for chaining
        """
        axis_config = AxisConfig(
            title=title,
            min_value=min,
            max_value=max,
            major_interval=interval,
            major_gridlines=gridlines,
            format_code=format_code,
            logarithmic=logarithmic,
        )

        if axis_type == "category":
            axis_config.axis_type = AxisType.CATEGORY
            self._spec.category_axis = axis_config
        elif axis_type == "value":
            axis_config.axis_type = AxisType.VALUE
            self._spec.value_axis = axis_config
        elif axis_type in ("secondary", "secondary_value"):
            axis_config.axis_type = AxisType.SECONDARY_VALUE
            self._spec.secondary_axis = axis_config

        return self

    def category_axis(
        self,
        *,
        title: str | None = None,
        format_code: str | None = None,
        reversed: bool = False,
    ) -> Self:
        """Configure category (X) axis.

        Args:
            title: Axis title
            format_code: Number/date format
            reversed: Reverse axis

        Returns:
            Self for chaining
        """
        self._spec.category_axis = AxisConfig(
            axis_type=AxisType.CATEGORY,
            title=title,
            format_code=format_code,
            reversed=reversed,
        )
        return self

    def value_axis(
        self,
        *,
        title: str | None = None,
        min: float | None = None,
        max: float | None = None,
        format_code: str | None = None,
        logarithmic: bool = False,
    ) -> Self:
        """Configure value (Y) axis.

        Args:
            title: Axis title
            min: Minimum value
            max: Maximum value
            format_code: Number format
            logarithmic: Use logarithmic scale

        Returns:
            Self for chaining
        """
        self._spec.value_axis = AxisConfig(
            axis_type=AxisType.VALUE,
            title=title,
            min_value=min,
            max_value=max,
            format_code=format_code,
            logarithmic=logarithmic,
        )
        return self

    # =========================================================================
    # Position and Size (AC1-AC5)
    # =========================================================================

    def position(
        self,
        cell: str,
        *,
        offset_x: int = 0,
        offset_y: int = 0,
        move_with_cells: bool = True,
        size_with_cells: bool = False,
    ) -> Self:
        """Set chart position.

        Args:
            cell: Anchor cell (e.g., "F2")
            offset_x: Horizontal offset in pixels
            offset_y: Vertical offset in pixels
            move_with_cells: Move when cells resize
            size_with_cells: Size when cells resize

        Returns:
            Self for chaining
        """
        self._spec.position = ChartPosition(
            cell=cell,
            offset_x=offset_x,
            offset_y=offset_y,
            move_with_cells=move_with_cells,
            size_with_cells=size_with_cells,
        )
        return self

    def size(self, width: int, height: int) -> Self:
        """Set chart size.

        Args:
            width: Width in pixels
            height: Height in pixels

        Returns:
            Self for chaining
        """
        self._spec.size = ChartSize(width=width, height=height)
        return self

    # =========================================================================
    # Styling (AC1-AC5)
    # =========================================================================

    def style(self, preset: str) -> Self:
        """Apply a style preset.

        Args:
            preset: Style preset name (e.g., "theme", "minimal", "colorful")

        Returns:
            Self for chaining
        """
        self._spec.style_preset = preset
        return self

    def colors(self, *colors: str) -> Self:
        """Set custom color palette.

        Args:
            *colors: Hex color values

        Returns:
            Self for chaining
        """
        self._spec.color_palette = list(colors)
        return self

    def plot_area(
        self,
        *,
        background: str | None = None,
        border_color: str | None = None,
        border_width: str = "1pt",
    ) -> Self:
        """Configure plot area styling.

        Args:
            background: Background color
            border_color: Border color
            border_width: Border width

        Returns:
            Self for chaining
        """
        self._spec.plot_area = PlotAreaStyle(
            background_color=background,
            border_color=border_color,
            border_width=border_width,
        )
        return self

    def threed(self, enabled: bool = True) -> Self:
        """Enable 3D effects.

        Args:
            enabled: Whether to enable 3D

        Returns:
            Self for chaining
        """
        self._spec.threed = enabled
        return self

    # =========================================================================
    # Build
    # =========================================================================

    def build(self) -> ChartSpec:
        """Build the chart specification.

        Returns:
            ChartSpec object
        """
        return self._spec


# ============================================================================
# Sparkline Builder
# ============================================================================


class SparklineBuilder:
    r"""Fluent builder for creating sparklines.

    Examples:
        sparkline = SparklineBuilder() \\
            .line() \\
            .data("MonthlyData.B{row}:M{row}") \\
            .color("#4472C4") \\
            .markers(high="#00B050", low="#FF0000") \\
            .build()
    """

    def __init__(self) -> None:
        """Initialize sparkline builder."""
        self._sparkline = Sparkline()

    def line(self) -> Self:
        """Set sparkline type to line."""
        self._sparkline.type = SparklineType.LINE
        return self

    def column(self) -> Self:
        """Set sparkline type to column."""
        self._sparkline.type = SparklineType.COLUMN
        return self

    def win_loss(self) -> Self:
        """Set sparkline type to win/loss."""
        self._sparkline.type = SparklineType.WIN_LOSS
        return self

    def data(self, range_ref: str) -> Self:
        """Set data range.

        Args:
            range_ref: Range reference (can include {row} placeholder)

        Returns:
            Self for chaining
        """
        self._sparkline.data_range = range_ref
        return self

    def color(self, color: str) -> Self:
        """Set sparkline color.

        Args:
            color: Hex color

        Returns:
            Self for chaining
        """
        self._sparkline.color = color
        return self

    def negative_color(self, color: str) -> Self:
        """Set color for negative values.

        Args:
            color: Hex color

        Returns:
            Self for chaining
        """
        self._sparkline.negative_color = color
        return self

    def markers(
        self,
        *,
        high: str | None = None,
        low: str | None = None,
        first: str | None = None,
        last: str | None = None,
        negative: str | None = None,
    ) -> Self:
        """Configure marker colors.

        Args:
            high: Color for highest point
            low: Color for lowest point
            first: Color for first point
            last: Color for last point
            negative: Color for negative values

        Returns:
            Self for chaining
        """
        self._sparkline.markers = SparklineMarkers(
            high=high,
            low=low,
            first=first,
            last=last,
            negative=negative,
        )
        return self

    def axis_range(self, min: float | None = None, max: float | None = None) -> Self:
        """Set axis range.

        Args:
            min: Minimum value
            max: Maximum value

        Returns:
            Self for chaining
        """
        self._sparkline.min_axis = min
        self._sparkline.max_axis = max
        return self

    def same_scale(self, enabled: bool = True) -> Self:
        """Use same scale for group.

        Args:
            enabled: Whether to use same scale

        Returns:
            Self for chaining
        """
        self._sparkline.same_scale = enabled
        return self

    def show_axis(self, enabled: bool = True) -> Self:
        """Show horizontal axis.

        Args:
            enabled: Whether to show axis

        Returns:
            Self for chaining
        """
        self._sparkline.show_axis = enabled
        return self

    def build(self) -> Sparkline:
        """Build the sparkline specification.

        Returns:
            Sparkline object
        """
        return self._sparkline


# ============================================================================
# Convenience Functions
# ============================================================================


def chart() -> ChartBuilder:
    """Create a new chart builder.

    Returns:
        ChartBuilder instance
    """
    return ChartBuilder()


def sparkline() -> SparklineBuilder:
    """Create a new sparkline builder.

    Returns:
        SparklineBuilder instance
    """
    return SparklineBuilder()


# Pre-built chart configurations for common use cases


def budget_comparison_chart(
    categories: str,
    budget_values: str,
    actual_values: str,
    *,
    title: str = "Budget vs Actual",
    position: str = "F2",
) -> ChartSpec:
    """Create a budget comparison column chart.

    Args:
        categories: Category labels range
        budget_values: Budget values range
        actual_values: Actual values range
        title: Chart title
        position: Anchor cell

    Returns:
        ChartSpec for budget comparison
    """
    return (
        ChartBuilder()
        .column_chart()
        .title(title)
        .categories(categories)
        .series("Budget", budget_values, color="#4472C4")
        .series("Actual", actual_values, color="#ED7D31")
        .legend(position="bottom")
        .axis("value", title="Amount ($)", min=0)
        .position(position)
        .size(450, 300)
        .build()
    )


def spending_pie_chart(
    categories: str,
    values: str,
    *,
    title: str = "Spending by Category",
    position: str = "F2",
) -> ChartSpec:
    """Create a spending breakdown pie chart.

    Args:
        categories: Category labels range
        values: Values range
        title: Chart title
        position: Anchor cell

    Returns:
        ChartSpec for spending pie chart
    """
    return (
        ChartBuilder()
        .pie_chart()
        .title(title)
        .categories(categories)
        .series("Spending", values)
        .data_labels(show_percentage=True, show_category=True)
        .legend(position="right")
        .position(position)
        .size(400, 350)
        .build()
    )


def trend_line_chart(
    categories: str,
    values: str,
    *,
    title: str = "Trend Analysis",
    position: str = "F2",
    trendline: bool = True,
) -> ChartSpec:
    """Create a trend line chart.

    Args:
        categories: Category labels range (e.g., months)
        values: Values range
        title: Chart title
        position: Anchor cell
        trendline: Add linear trendline

    Returns:
        ChartSpec for trend chart
    """
    builder = (
        ChartBuilder()
        .line_chart(markers=True)
        .title(title)
        .categories(categories)
        .series("Values", values)
    )

    if trendline:
        builder.series_trendline("linear", display_equation=True)

    return (
        builder.legend(visible=False)
        .axis("value", gridlines=True)
        .position(position)
        .size(500, 300)
        .build()
    )


# ============================================================================
# Type Aliases for Backwards Compatibility
# ============================================================================

# SeriesSpec is an alias for DataSeries
SeriesSpec = DataSeries


def AxisSpec(
    *,
    title: str | None = None,
    format: str | None = None,
    min: float | None = None,
    max: float | None = None,
    **kwargs: object,
) -> AxisConfig:
    """Create AxisConfig with simplified parameter names.

    Args:
        title: Axis title
        format: Number format code (alias for format_code)
        min: Minimum value (alias for min_value)
        max: Maximum value (alias for max_value)
        **kwargs: Additional AxisConfig parameters

    Returns:
        AxisConfig instance
    """
    return AxisConfig(
        title=title,
        format_code=format,
        min_value=min,
        max_value=max,
        **kwargs,  # type: ignore[arg-type]
    )
