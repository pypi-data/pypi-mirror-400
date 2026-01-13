"""Conditional formatting rules and configuration.

Provides comprehensive conditional formatting support for spreadsheets
with financial-specific presets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from spreadsheet_dl.schema.styles import CellStyle, Color


# ============================================================================
# Enumerations
# ============================================================================


class RuleOperator(Enum):
    """Comparison operators for cell value rules."""

    EQUAL = "equal"
    NOT_EQUAL = "notEqual"
    GREATER_THAN = "greaterThan"
    LESS_THAN = "lessThan"
    GREATER_THAN_OR_EQUAL = "greaterThanOrEqual"
    LESS_THAN_OR_EQUAL = "lessThanOrEqual"
    BETWEEN = "between"
    NOT_BETWEEN = "notBetween"
    CONTAINS_TEXT = "containsText"
    NOT_CONTAINS_TEXT = "notContainsText"
    BEGINS_WITH = "beginsWith"
    ENDS_WITH = "endsWith"
    BLANK = "blank"
    NOT_BLANK = "notBlank"
    ERROR = "error"
    NOT_ERROR = "notError"


class ConditionalRuleType(Enum):
    """Types of conditional formatting rules."""

    CELL_VALUE = "cellValue"
    FORMULA = "formula"
    COLOR_SCALE = "colorScale"
    DATA_BAR = "dataBar"
    ICON_SET = "iconSet"
    TOP_BOTTOM = "topBottom"
    ABOVE_BELOW_AVERAGE = "aboveBelowAverage"
    DUPLICATE_UNIQUE = "duplicateUnique"
    TEXT = "text"
    DATE = "date"


class IconSetType(Enum):
    """Icon set types for icon-based conditional formatting."""

    THREE_ARROWS = "3Arrows"
    THREE_ARROWS_GRAY = "3ArrowsGray"
    THREE_FLAGS = "3Flags"
    THREE_TRAFFIC_LIGHTS_1 = "3TrafficLights1"
    THREE_TRAFFIC_LIGHTS_2 = "3TrafficLights2"
    THREE_SIGNS = "3Signs"
    THREE_SYMBOLS = "3Symbols"
    THREE_SYMBOLS_2 = "3Symbols2"
    THREE_STARS = "3Stars"
    THREE_TRIANGLES = "3Triangles"
    FOUR_ARROWS = "4Arrows"
    FOUR_ARROWS_GRAY = "4ArrowsGray"
    FOUR_RATINGS = "4Ratings"
    FOUR_RED_TO_BLACK = "4RedToBlack"
    FOUR_TRAFFIC_LIGHTS = "4TrafficLights"
    FIVE_ARROWS = "5Arrows"
    FIVE_ARROWS_GRAY = "5ArrowsGray"
    FIVE_RATINGS = "5Ratings"
    FIVE_QUARTERS = "5Quarters"
    FIVE_BOXES = "5Boxes"


class DateRuleType(Enum):
    """Date-based rule types."""

    YESTERDAY = "yesterday"
    TODAY = "today"
    TOMORROW = "tomorrow"
    LAST_7_DAYS = "last7Days"
    THIS_WEEK = "thisWeek"
    LAST_WEEK = "lastWeek"
    NEXT_WEEK = "nextWeek"
    THIS_MONTH = "thisMonth"
    LAST_MONTH = "lastMonth"
    NEXT_MONTH = "nextMonth"
    THIS_QUARTER = "thisQuarter"
    LAST_QUARTER = "lastQuarter"
    NEXT_QUARTER = "nextQuarter"
    THIS_YEAR = "thisYear"
    LAST_YEAR = "lastYear"
    NEXT_YEAR = "nextYear"


class ColorScaleType(Enum):
    """Color scale types."""

    TWO_COLOR = "twoColor"
    THREE_COLOR = "threeColor"


class ValueType(Enum):
    """Value types for color scales and data bars."""

    MIN = "min"
    MAX = "max"
    NUMBER = "num"
    PERCENT = "percent"
    PERCENTILE = "percentile"
    FORMULA = "formula"
    AUTOMATIC = "autoMin"


# ============================================================================
# Color Scale Configuration
# ============================================================================


@dataclass(frozen=True)
class ColorScalePoint:
    """A point on a color scale.

    Implements Missing frozen=True on value objects
    """

    value_type: ValueType
    value: float | str | None = None  # None for min/max
    color: Color | str | None = None  # Color or reference

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {"type": self.value_type.value}
        if self.value is not None:
            result["value"] = self.value
        if self.color is not None:
            result["color"] = (
                str(self.color) if hasattr(self.color, "__str__") else self.color
            )
        return result


@dataclass(frozen=True)
class ColorScale:
    """Color scale configuration for gradient-style conditional formatting.

    Implements Missing frozen=True on value objects

    Examples:
        # Two-color scale (red to green)
        scale = ColorScale.two_color(
            min_color=Color("#FF0000"),  # Red
            max_color=Color("#00FF00"),  # Green
        )

        # Three-color scale (red-yellow-green)
        scale = ColorScale.three_color(
            min_color=Color("#F8696B"),  # Red
            mid_color=Color("#FFEB84"),  # Yellow
            max_color=Color("#63BE7B"),  # Green
        )

        # With percentile midpoint
        scale = ColorScale.three_color(
            min_color=Color("#F8696B"),
            mid_color=Color("#FFEB84"),
            max_color=Color("#63BE7B"),
            mid_type=ValueType.PERCENTILE,
            mid_value=50,
        )
    """

    type: ColorScaleType
    points: tuple[ColorScalePoint, ...] = field(default_factory=tuple)

    @classmethod
    def two_color(
        cls,
        min_color: Color | str,
        max_color: Color | str,
        min_type: ValueType = ValueType.MIN,
        max_type: ValueType = ValueType.MAX,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> ColorScale:
        """Create a two-color scale."""
        return cls(
            type=ColorScaleType.TWO_COLOR,
            points=(
                ColorScalePoint(min_type, min_value, min_color),
                ColorScalePoint(max_type, max_value, max_color),
            ),
        )

    @classmethod
    def three_color(
        cls,
        min_color: Color | str,
        mid_color: Color | str,
        max_color: Color | str,
        min_type: ValueType = ValueType.MIN,
        mid_type: ValueType = ValueType.PERCENTILE,
        max_type: ValueType = ValueType.MAX,
        min_value: float | None = None,
        mid_value: float = 50,
        max_value: float | None = None,
    ) -> ColorScale:
        """Create a three-color scale."""
        return cls(
            type=ColorScaleType.THREE_COLOR,
            points=(
                ColorScalePoint(min_type, min_value, min_color),
                ColorScalePoint(mid_type, mid_value, mid_color),
                ColorScalePoint(max_type, max_value, max_color),
            ),
        )

    @classmethod
    def red_yellow_green(cls) -> ColorScale:
        """Create standard red-yellow-green color scale."""
        from spreadsheet_dl.schema.styles import Color

        return cls.three_color(
            min_color=Color("#F8696B"),
            mid_color=Color("#FFEB84"),
            max_color=Color("#63BE7B"),
        )

    @classmethod
    def green_yellow_red(cls) -> ColorScale:
        """Create inverted green-yellow-red color scale."""
        from spreadsheet_dl.schema.styles import Color

        return cls.three_color(
            min_color=Color("#63BE7B"),
            mid_color=Color("#FFEB84"),
            max_color=Color("#F8696B"),
        )

    @classmethod
    def white_to_blue(cls) -> ColorScale:
        """Create white to blue color scale."""
        from spreadsheet_dl.schema.styles import Color

        return cls.two_color(
            min_color=Color("#FFFFFF"),
            max_color=Color("#5A8AC6"),
        )

    @classmethod
    def red_white_blue(cls) -> ColorScale:
        """Create red-white-blue diverging color scale."""
        from spreadsheet_dl.schema.styles import Color

        return cls.three_color(
            min_color=Color("#F8696B"),
            mid_color=Color("#FFFFFF"),
            max_color=Color("#5A8AC6"),
        )


# ============================================================================
# Data Bar Configuration
# ============================================================================


@dataclass(frozen=True)
class DataBar:
    """Data bar configuration for bar-style conditional formatting.

    Implements Missing frozen=True on value objects

    Examples:
        # Default blue bars
        bar = DataBar()

        # Custom color and min/max
        bar = DataBar(
            fill_color=Color("#4472C4"),
            negative_color=Color("#C00000"),
            min_type=ValueType.NUMBER,
            min_value=0,
            show_value=True,
        )

        # Gradient fill
        bar = DataBar(
            fill_color=Color("#638EC6"),
            gradient_fill=True,
        )
    """

    fill_color: Color | str | None = None
    border_color: Color | str | None = None
    negative_color: Color | str | None = None
    negative_border_color: Color | str | None = None

    min_type: ValueType = ValueType.AUTOMATIC
    max_type: ValueType = ValueType.AUTOMATIC
    min_value: float | None = None
    max_value: float | None = None

    show_value: bool = True
    gradient_fill: bool = False
    axis_position: str = "automatic"  # "automatic", "midpoint", "none"
    direction: str = "context"  # "context", "leftToRight", "rightToLeft"

    @classmethod
    def default(cls) -> DataBar:
        """Create default blue data bar."""
        from spreadsheet_dl.schema.styles import Color

        return cls(fill_color=Color("#638EC6"))

    @classmethod
    def budget_variance(cls) -> DataBar:
        """Create data bar for budget variance (green positive, red negative)."""
        from spreadsheet_dl.schema.styles import Color

        return cls(
            fill_color=Color("#63BE7B"),
            negative_color=Color("#C00000"),
            show_value=True,
            axis_position="midpoint",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "showValue": self.show_value,
            "gradient": self.gradient_fill,
            "axisPosition": self.axis_position,
            "direction": self.direction,
        }
        if self.fill_color:
            result["fillColor"] = str(self.fill_color)
        if self.negative_color:
            result["negativeColor"] = str(self.negative_color)
        if self.min_type != ValueType.AUTOMATIC:
            result["minType"] = self.min_type.value
            if self.min_value is not None:
                result["minValue"] = self.min_value
        if self.max_type != ValueType.AUTOMATIC:
            result["maxType"] = self.max_type.value
            if self.max_value is not None:
                result["maxValue"] = self.max_value
        return result


# ============================================================================
# Icon Set Configuration
# ============================================================================


@dataclass(frozen=True)
class IconSetThreshold:
    """A threshold for icon set rules.

    Implements Missing frozen=True on value objects
    """

    value_type: ValueType
    value: float | str
    icon_index: int  # Which icon in the set (0-based)
    gte: bool = True  # Greater than or equal (vs greater than)


@dataclass(frozen=True)
class IconSet:
    """Icon set configuration.

    Implements Missing frozen=True on value objects

    Examples:
        # Three arrows
        icons = IconSet(icon_set=IconSetType.THREE_ARROWS)

        # Custom thresholds
        icons = IconSet(
            icon_set=IconSetType.THREE_TRAFFIC_LIGHTS_1,
            thresholds=[
                IconSetThreshold(ValueType.PERCENT, 67, 0),  # Green >= 67%
                IconSetThreshold(ValueType.PERCENT, 33, 1),  # Yellow >= 33%
            ],  # Red < 33%
        )

        # Show only icons
        icons = IconSet(
            icon_set=IconSetType.THREE_SYMBOLS,
            show_value=False,
        )
    """

    icon_set: IconSetType
    thresholds: tuple[IconSetThreshold, ...] = field(default_factory=tuple)
    show_value: bool = True
    reverse: bool = False

    @classmethod
    def three_arrows(cls, reverse: bool = False) -> IconSet:
        """Create three arrows icon set with default thresholds."""
        return cls(
            icon_set=IconSetType.THREE_ARROWS,
            thresholds=(
                IconSetThreshold(ValueType.PERCENT, 67, 0),
                IconSetThreshold(ValueType.PERCENT, 33, 1),
            ),
            reverse=reverse,
        )

    @classmethod
    def three_traffic_lights(cls) -> IconSet:
        """Create three traffic lights icon set."""
        return cls(
            icon_set=IconSetType.THREE_TRAFFIC_LIGHTS_1,
            thresholds=(
                IconSetThreshold(ValueType.PERCENT, 67, 0),
                IconSetThreshold(ValueType.PERCENT, 33, 1),
            ),
        )

    @classmethod
    def five_ratings(cls) -> IconSet:
        """Create five ratings (stars) icon set."""
        return cls(
            icon_set=IconSetType.FIVE_RATINGS,
            thresholds=(
                IconSetThreshold(ValueType.PERCENT, 80, 0),
                IconSetThreshold(ValueType.PERCENT, 60, 1),
                IconSetThreshold(ValueType.PERCENT, 40, 2),
                IconSetThreshold(ValueType.PERCENT, 20, 3),
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "iconSet": self.icon_set.value,
            "showValue": self.show_value,
            "reverse": self.reverse,
        }
        if self.thresholds:
            result["thresholds"] = [
                {
                    "type": t.value_type.value,
                    "value": t.value,
                    "iconIndex": t.icon_index,
                    "gte": t.gte,
                }
                for t in self.thresholds
            ]
        return result


# ============================================================================
# Conditional Formatting Rule (Base)
# ============================================================================


@dataclass
class ConditionalRule:
    """Base conditional formatting rule.

    Examples:
        # Value rule: highlight negative values
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.LESS_THAN,
            value=0,
            style=danger_style,
        )

        # Formula rule: highlight if exceeds budget
        rule = ConditionalRule.from_formula(
            formula="C2>B2",
            style=warning_style,
        )

        # Between rule
        rule = ConditionalRule.between(
            min_value=0,
            max_value=100,
            style=normal_style,
        )
    """

    type: ConditionalRuleType
    priority: int = 1
    stop_if_true: bool = False

    # For cell value rules
    operator: RuleOperator | None = None
    value: Any = None
    value2: Any = None  # For BETWEEN operator

    # For formula rules
    formula: str | None = None

    # For color scale, data bar, icon set
    color_scale: ColorScale | None = None
    data_bar: DataBar | None = None
    icon_set: IconSet | None = None

    # For top/bottom rules
    rank: int | None = None
    percent: bool = False
    bottom: bool = False

    # For above/below average
    std_dev: float | None = None  # Number of standard deviations
    above: bool = True
    equal_average: bool = True

    # For text rules
    text: str | None = None

    # For date rules
    date_type: DateRuleType | None = None

    # Style to apply (for value, formula, text, date, top/bottom rules)
    style: CellStyle | str | None = None

    @classmethod
    def cell_value(
        cls,
        operator: RuleOperator,
        value: Any,
        style: CellStyle | str,
        value2: Any = None,
        priority: int = 1,
    ) -> ConditionalRule:
        """Create cell value rule."""
        return cls(
            type=ConditionalRuleType.CELL_VALUE,
            operator=operator,
            value=value,
            value2=value2,
            style=style,
            priority=priority,
        )

    @classmethod
    def from_formula(
        cls,
        formula: str,
        style: CellStyle | str,
        priority: int = 1,
    ) -> ConditionalRule:
        """Create formula-based rule."""
        return cls(
            type=ConditionalRuleType.FORMULA,
            formula=formula,
            style=style,
            priority=priority,
        )

    @classmethod
    def between(
        cls,
        min_value: Any,
        max_value: Any,
        style: CellStyle | str,
        priority: int = 1,
    ) -> ConditionalRule:
        """Create between rule."""
        return cls(
            type=ConditionalRuleType.CELL_VALUE,
            operator=RuleOperator.BETWEEN,
            value=min_value,
            value2=max_value,
            style=style,
            priority=priority,
        )

    @classmethod
    def contains_text(
        cls,
        text: str,
        style: CellStyle | str,
        priority: int = 1,
    ) -> ConditionalRule:
        """Create text contains rule."""
        return cls(
            type=ConditionalRuleType.TEXT,
            operator=RuleOperator.CONTAINS_TEXT,
            text=text,
            style=style,
            priority=priority,
        )

    @classmethod
    def top_n(
        cls,
        n: int,
        style: CellStyle | str,
        percent: bool = False,
        priority: int = 1,
    ) -> ConditionalRule:
        """Create top N rule."""
        return cls(
            type=ConditionalRuleType.TOP_BOTTOM,
            rank=n,
            percent=percent,
            bottom=False,
            style=style,
            priority=priority,
        )

    @classmethod
    def bottom_n(
        cls,
        n: int,
        style: CellStyle | str,
        percent: bool = False,
        priority: int = 1,
    ) -> ConditionalRule:
        """Create bottom N rule."""
        return cls(
            type=ConditionalRuleType.TOP_BOTTOM,
            rank=n,
            percent=percent,
            bottom=True,
            style=style,
            priority=priority,
        )

    @classmethod
    def above_average(
        cls,
        style: CellStyle | str,
        std_dev: float | None = None,
        priority: int = 1,
    ) -> ConditionalRule:
        """Create above average rule."""
        return cls(
            type=ConditionalRuleType.ABOVE_BELOW_AVERAGE,
            above=True,
            std_dev=std_dev,
            style=style,
            priority=priority,
        )

    @classmethod
    def below_average(
        cls,
        style: CellStyle | str,
        std_dev: float | None = None,
        priority: int = 1,
    ) -> ConditionalRule:
        """Create below average rule."""
        return cls(
            type=ConditionalRuleType.ABOVE_BELOW_AVERAGE,
            above=False,
            std_dev=std_dev,
            style=style,
            priority=priority,
        )

    @classmethod
    def duplicate(cls, style: CellStyle | str, priority: int = 1) -> ConditionalRule:
        """Create duplicate values rule."""
        return cls(
            type=ConditionalRuleType.DUPLICATE_UNIQUE,
            style=style,
            priority=priority,
        )

    @classmethod
    def date_rule(
        cls,
        date_type: DateRuleType,
        style: CellStyle | str,
        priority: int = 1,
    ) -> ConditionalRule:
        """Create date-based rule."""
        return cls(
            type=ConditionalRuleType.DATE,
            date_type=date_type,
            style=style,
            priority=priority,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "type": self.type.value,
            "priority": self.priority,
            "stopIfTrue": self.stop_if_true,
        }

        if self.operator:
            result["operator"] = self.operator.value
        if self.value is not None:
            result["value"] = self.value
        if self.value2 is not None:
            result["value2"] = self.value2
        if self.formula:
            result["formula"] = self.formula
        if self.color_scale:
            result["colorScale"] = {
                "type": self.color_scale.type.value,
                "points": [p.to_dict() for p in self.color_scale.points],
            }
        if self.data_bar:
            result["dataBar"] = self.data_bar.to_dict()
        if self.icon_set:
            result["iconSet"] = self.icon_set.to_dict()
        if self.rank is not None:
            result["rank"] = self.rank
            result["percent"] = self.percent
            result["bottom"] = self.bottom
        if self.text:
            result["text"] = self.text
        if self.date_type:
            result["dateType"] = self.date_type.value
        if self.style:
            result["style"] = (
                self.style if isinstance(self.style, str) else self.style.name
            )

        return result


# ============================================================================
# Conditional Formatting Configuration
# ============================================================================


@dataclass
class ConditionalFormat:
    """Conditional formatting configuration for a range.

    Combines a range reference with one or more conditional rules.

    Examples:
        # Single rule
        fmt = ConditionalFormat(
            range="D2:D100",
            rules=[
                ConditionalRule.cell_value(
                    RuleOperator.LESS_THAN, 0, "danger_style"
                ),
            ],
        )

        # Multiple rules with priority
        fmt = ConditionalFormat(
            range="D2:D100",
            rules=[
                ConditionalRule.cell_value(
                    RuleOperator.LESS_THAN, 0, "danger", priority=1
                ),
                ConditionalRule.cell_value(
                    RuleOperator.LESS_THAN, 100, "warning", priority=2
                ),
                ConditionalRule.cell_value(
                    RuleOperator.GREATER_THAN_OR_EQUAL, 100, "success", priority=3
                ),
            ],
        )

        # Color scale
        fmt = ConditionalFormat(
            range="E2:E100",
            rules=[
                ConditionalRule(
                    type=ConditionalRuleType.COLOR_SCALE,
                    color_scale=ColorScale.red_yellow_green(),
                ),
            ],
        )
    """

    range: str
    rules: list[ConditionalRule] = field(default_factory=list)

    def add_rule(self, rule: ConditionalRule) -> None:
        """Add a rule to this conditional format."""
        self.rules.append(rule)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "range": self.range,
            "rules": [r.to_dict() for r in self.rules],
        }


# ============================================================================
# Financial Presets
# ============================================================================


class FinancialFormats:
    """Pre-configured conditional formats for financial use cases.

    Provides ready-to-use conditional formatting rules for common
    financial scenarios.
    """

    @staticmethod
    def budget_variance(
        range_ref: str,
        danger_style: CellStyle | str = "danger",
        warning_style: CellStyle | str = "warning",
        success_style: CellStyle | str = "success",
    ) -> ConditionalFormat:
        """Create budget variance formatting (remaining budget column).

        - Negative: Red (over budget)
        - 0-10% of budget: Yellow (near limit)
        - >10% of budget: Green (healthy)
        """
        return ConditionalFormat(
            range=range_ref,
            rules=[
                ConditionalRule.cell_value(
                    RuleOperator.LESS_THAN,
                    0,
                    danger_style,
                    priority=1,
                ),
                # Formula checks if remaining < 10% of budget
                ConditionalRule.from_formula(
                    formula="AND(D2>=0, D2<B2*0.1)",
                    style=warning_style,
                    priority=2,
                ),
                ConditionalRule.cell_value(
                    RuleOperator.GREATER_THAN_OR_EQUAL,
                    0,
                    success_style,
                    priority=3,
                ),
            ],
        )

    @staticmethod
    def percent_used_scale(range_ref: str) -> ConditionalFormat:
        """Create percentage used color scale (0-100%+).

        Green at 0%, yellow at 50%, red at 100%.
        """
        return ConditionalFormat(
            range=range_ref,
            rules=[
                ConditionalRule(
                    type=ConditionalRuleType.COLOR_SCALE,
                    color_scale=ColorScale.three_color(
                        min_color="#63BE7B",  # Green
                        mid_color="#FFEB84",  # Yellow
                        max_color="#F8696B",  # Red
                        min_type=ValueType.NUMBER,
                        mid_type=ValueType.NUMBER,
                        max_type=ValueType.NUMBER,
                        min_value=0,
                        mid_value=0.5,
                        max_value=1,
                    ),
                ),
            ],
        )

    @staticmethod
    def expense_data_bar(range_ref: str) -> ConditionalFormat:
        """Create data bars for expense amounts."""
        from spreadsheet_dl.schema.styles import Color

        return ConditionalFormat(
            range=range_ref,
            rules=[
                ConditionalRule(
                    type=ConditionalRuleType.DATA_BAR,
                    data_bar=DataBar(
                        fill_color=Color("#638EC6"),
                        gradient_fill=True,
                        min_type=ValueType.NUMBER,
                        min_value=0,
                    ),
                ),
            ],
        )

    @staticmethod
    def due_date_alerts(
        range_ref: str,
        overdue_style: CellStyle | str = "danger",
        due_soon_style: CellStyle | str = "warning",
    ) -> ConditionalFormat:
        """Create due date alert formatting.

        - Overdue (past dates): Red
        - Due within 7 days: Yellow
        """
        return ConditionalFormat(
            range=range_ref,
            rules=[
                ConditionalRule.date_rule(
                    DateRuleType.YESTERDAY,
                    overdue_style,
                    priority=1,
                ),
                ConditionalRule.date_rule(
                    DateRuleType.LAST_7_DAYS,
                    due_soon_style,
                    priority=2,
                ),
            ],
        )

    @staticmethod
    def positive_negative(
        range_ref: str,
        positive_style: CellStyle | str = "success",
        negative_style: CellStyle | str = "danger",
    ) -> ConditionalFormat:
        """Simple positive/negative value formatting.

        Positive: Green, Negative: Red
        """
        return ConditionalFormat(
            range=range_ref,
            rules=[
                ConditionalRule.cell_value(
                    RuleOperator.LESS_THAN,
                    0,
                    negative_style,
                    priority=1,
                ),
                ConditionalRule.cell_value(
                    RuleOperator.GREATER_THAN,
                    0,
                    positive_style,
                    priority=2,
                ),
            ],
        )

    @staticmethod
    def trend_arrows(range_ref: str) -> ConditionalFormat:
        """Create trend arrows icon set."""
        return ConditionalFormat(
            range=range_ref,
            rules=[
                ConditionalRule(
                    type=ConditionalRuleType.ICON_SET,
                    icon_set=IconSet.three_arrows(),
                ),
            ],
        )
