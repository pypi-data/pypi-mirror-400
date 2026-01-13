"""Advanced spreadsheet features.

Provides advanced spreadsheet features for professional documents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime

# ============================================================================
# Hidden Rows/Columns
# ============================================================================


@dataclass
class HiddenRowsColumns:
    """Configuration for hidden rows and columns.

    Examples:
        hidden = HiddenRowsColumns(
            hidden_rows=[2, 5, 10],
            hidden_columns=["C", "E"],
        )
    """

    hidden_rows: list[int] = field(default_factory=list)  # 1-based row numbers
    hidden_columns: list[str | int] = field(
        default_factory=list
    )  # Column letters or 1-based numbers

    def hide_row(self, row: int) -> None:
        """Hide a row (1-based index)."""
        if row not in self.hidden_rows:
            self.hidden_rows.append(row)

    def hide_column(self, column: str | int) -> None:
        """Hide a column (letter or 1-based index)."""
        if column not in self.hidden_columns:
            self.hidden_columns.append(column)

    def unhide_row(self, row: int) -> None:
        """Unhide a row."""
        if row in self.hidden_rows:
            self.hidden_rows.remove(row)

    def unhide_column(self, column: str | int) -> None:
        """Unhide a column."""
        if column in self.hidden_columns:
            self.hidden_columns.remove(column)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hiddenRows": self.hidden_rows,
            "hiddenColumns": self.hidden_columns,
        }


# ============================================================================
# Named Ranges
# ============================================================================


@dataclass
class NamedRange:
    """Named range definition.

    A named range provides a symbolic name for a cell range,
    making formulas more readable and maintainable.

    Examples:
        # Simple named range
        budget_range = NamedRange(
            name="Budget",
            sheet="Budget",
            range="B2:B100",
        )

        # Cross-sheet named range
        all_expenses = NamedRange(
            name="AllExpenses",
            sheet=None,  # Workbook scope
            range="Expenses.C2:C500",
        )
    """

    name: str
    range: str  # Cell range reference
    sheet: str | None = None  # None for workbook scope
    scope: str = "workbook"  # "workbook" or sheet name
    comment: str = ""

    def __post_init__(self) -> None:
        """Validate name follows naming rules."""
        # Names must start with letter or underscore
        if not self.name or not (self.name[0].isalpha() or self.name[0] == "_"):
            raise ValueError(f"Invalid named range name: {self.name}")
        # Names cannot contain spaces
        if " " in self.name:
            raise ValueError("Named range names cannot contain spaces")

    @property
    def full_reference(self) -> str:
        """Get full cell reference including sheet name."""
        if self.sheet:
            return f"${self.sheet}.{self.range}"
        return self.range

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "range": self.range,
            "sheet": self.sheet,
            "scope": self.scope,
            "comment": self.comment,
        }


# ============================================================================
# Cell Comments
# ============================================================================


@dataclass
class CellComment:
    """Cell comment/note.

    Comments provide additional information visible on hover.

    Examples:
        comment = CellComment(
            cell="B5",
            text="This value is calculated from Q1 actuals",
            author="Finance Team",
        )
    """

    cell: str  # Cell reference
    text: str
    author: str = ""
    visible: bool = False  # Whether comment is always visible
    width: str = "200pt"
    height: str = "100pt"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cell": self.cell,
            "text": self.text,
            "author": self.author,
            "visible": self.visible,
            "width": self.width,
            "height": self.height,
        }


# ============================================================================
# Outline Groups
# ============================================================================


class OutlineDirection(Enum):
    """Direction for outline summary."""

    ABOVE = "above"  # Summary row above detail
    BELOW = "below"  # Summary row below detail
    LEFT = "left"  # Summary column left of detail
    RIGHT = "right"  # Summary column right of detail


@dataclass
class OutlineGroup:
    """Row or column outline group for collapsible sections.

    Examples:
        # Group rows 5-10 (collapsible)
        group = OutlineGroup(
            is_row=True,
            start=5,
            end=10,
            level=1,
        )
    """

    is_row: bool = True  # True for row group, False for column
    start: int = 1  # Start row/column (1-based)
    end: int = 1  # End row/column (1-based)
    level: int = 1  # Outline level (1-8)
    collapsed: bool = False  # Initially collapsed

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "isRow": self.is_row,
            "start": self.start,
            "end": self.end,
            "level": self.level,
            "collapsed": self.collapsed,
        }


@dataclass
class OutlineSettings:
    """Outline settings for a sheet.

    Controls summary row/column positions and groups.
    """

    row_summary_direction: OutlineDirection = OutlineDirection.BELOW
    column_summary_direction: OutlineDirection = OutlineDirection.RIGHT
    show_summary_symbol: bool = True
    groups: list[OutlineGroup] = field(default_factory=list)

    def add_row_group(
        self,
        start: int,
        end: int,
        level: int = 1,
        collapsed: bool = False,
    ) -> None:
        """Add a row outline group."""
        self.groups.append(
            OutlineGroup(
                is_row=True,
                start=start,
                end=end,
                level=level,
                collapsed=collapsed,
            )
        )

    def add_column_group(
        self,
        start: int,
        end: int,
        level: int = 1,
        collapsed: bool = False,
    ) -> None:
        """Add a column outline group."""
        self.groups.append(
            OutlineGroup(
                is_row=False,
                start=start,
                end=end,
                level=level,
                collapsed=collapsed,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rowSummaryDirection": self.row_summary_direction.value,
            "columnSummaryDirection": self.column_summary_direction.value,
            "showSummarySymbol": self.show_summary_symbol,
            "groups": [g.to_dict() for g in self.groups],
        }


# ============================================================================
# Auto-Filter
# ============================================================================


class FilterOperator(Enum):
    """Filter comparison operators."""

    EQUALS = "equals"
    NOT_EQUALS = "notEquals"
    GREATER_THAN = "greaterThan"
    GREATER_THAN_OR_EQUAL = "greaterThanOrEqual"
    LESS_THAN = "lessThan"
    LESS_THAN_OR_EQUAL = "lessThanOrEqual"
    BEGINS_WITH = "beginsWith"
    ENDS_WITH = "endsWith"
    CONTAINS = "contains"
    NOT_CONTAINS = "notContains"
    BLANK = "blank"
    NOT_BLANK = "notBlank"


@dataclass
class FilterCriteria:
    """Filter criteria for a column.

    Examples:
        # Text contains
        criteria = FilterCriteria(
            operator=FilterOperator.CONTAINS,
            value="Budget",
        )

        # Greater than value
        criteria = FilterCriteria(
            operator=FilterOperator.GREATER_THAN,
            value=1000,
        )
    """

    operator: FilterOperator
    value: Any = None
    and_criteria: FilterCriteria | None = None  # For AND conditions

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "operator": self.operator.value,
        }
        if self.value is not None:
            result["value"] = self.value
        if self.and_criteria:
            result["and"] = self.and_criteria.to_dict()
        return result


@dataclass
class AutoFilter:
    """Auto-filter configuration for a range.

    Examples:
        # Enable filter on range
        filter = AutoFilter(
            range="A1:G100",
            column_filters={
                1: FilterCriteria(FilterOperator.NOT_BLANK),
                3: FilterCriteria(FilterOperator.GREATER_THAN, 1000),
            },
        )
    """

    range: str  # Range to filter
    column_filters: dict[int, FilterCriteria] = field(
        default_factory=dict
    )  # 0-based column index

    def set_filter(self, column: int, criteria: FilterCriteria) -> None:
        """Set filter for a column (0-based index)."""
        self.column_filters[column] = criteria

    def clear_filter(self, column: int) -> None:
        """Clear filter for a column."""
        self.column_filters.pop(column, None)

    def clear_all(self) -> None:
        """Clear all filters."""
        self.column_filters.clear()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "range": self.range,
            "columnFilters": {
                str(k): v.to_dict() for k, v in self.column_filters.items()
            },
        }


# ============================================================================
# Data Tables
# ============================================================================


@dataclass
class DataTable:
    """Data table configuration.

    Data tables enable what-if analysis by varying input values.

    Examples:
        # One-variable data table
        table = DataTable(
            range="D1:F10",
            row_input_cell="B1",  # Row variable
        )

        # Two-variable data table
        table = DataTable(
            range="D1:F10",
            row_input_cell="B1",
            column_input_cell="B2",
        )
    """

    range: str  # Table range
    row_input_cell: str | None = None  # Cell for row variable
    column_input_cell: str | None = None  # Cell for column variable

    @property
    def is_two_variable(self) -> bool:
        """Check if this is a two-variable table."""
        return self.row_input_cell is not None and self.column_input_cell is not None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {"range": self.range}
        if self.row_input_cell:
            result["rowInputCell"] = self.row_input_cell
        if self.column_input_cell:
            result["columnInputCell"] = self.column_input_cell
        return result


# ============================================================================
# Cell Hyperlinks
# ============================================================================


class HyperlinkType(Enum):
    """Types of hyperlinks."""

    URL = "url"  # Web URL
    FILE = "file"  # Local file
    EMAIL = "email"  # Email address
    CELL = "cell"  # Cell reference
    NAMED_RANGE = "named_range"  # Named range reference


@dataclass
class Hyperlink:
    """Cell hyperlink.

    Examples:
        # Web link
        link = Hyperlink(
            cell="A1",
            target="https://example.com",
            display_text="Click Here",
        )

        # Email link
        link = Hyperlink(
            cell="A2",
            target="mailto:finance@company.com",
            link_type=HyperlinkType.EMAIL,
        )

        # Internal cell link
        link = Hyperlink(
            cell="A3",
            target="Summary.A1",
            link_type=HyperlinkType.CELL,
            display_text="Go to Summary",
        )
    """

    cell: str  # Cell containing the link
    target: str  # Link target (URL, file path, cell reference)
    link_type: HyperlinkType = HyperlinkType.URL
    display_text: str | None = None  # Text to display (if different from target)
    tooltip: str | None = None  # Hover tooltip

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "cell": self.cell,
            "target": self.target,
            "type": self.link_type.value,
        }
        if self.display_text:
            result["displayText"] = self.display_text
        if self.tooltip:
            result["tooltip"] = self.tooltip
        return result


# ============================================================================
# Images and Objects
# ============================================================================


class ImageAnchor(Enum):
    """Image anchor type."""

    CELL = "cell"  # Anchored to cell (moves with cell)
    PAGE = "page"  # Anchored to page position
    PARAGRAPH = "paragraph"  # Anchored to paragraph


@dataclass
class Image:
    """Embedded image.

    Examples:
        image = Image(
            source="logo.png",
            cell="A1",
            width="100pt",
            height="50pt",
        )
    """

    source: str  # File path or URL
    cell: str  # Anchor cell
    width: str = "100pt"
    height: str = "100pt"
    anchor: ImageAnchor = ImageAnchor.CELL
    alt_text: str = ""
    move_with_cells: bool = True
    size_with_cells: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "cell": self.cell,
            "width": self.width,
            "height": self.height,
            "anchor": self.anchor.value,
            "altText": self.alt_text,
            "moveWithCells": self.move_with_cells,
            "sizeWithCells": self.size_with_cells,
        }


@dataclass
class Shape:
    """Shape object.

    Examples:
        shape = Shape(
            shape_type="rectangle",
            cell="B5",
            width="150pt",
            height="100pt",
            fill_color="#4472C4",
        )
    """

    shape_type: str  # rectangle, ellipse, arrow, etc.
    cell: str  # Anchor cell
    width: str = "100pt"
    height: str = "100pt"
    fill_color: str | None = None
    stroke_color: str = "#000000"
    stroke_width: str = "1pt"
    text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "type": self.shape_type,
            "cell": self.cell,
            "width": self.width,
            "height": self.height,
            "strokeColor": self.stroke_color,
            "strokeWidth": self.stroke_width,
        }
        if self.fill_color:
            result["fillColor"] = self.fill_color
        if self.text:
            result["text"] = self.text
        return result


# ============================================================================
# Document Properties
# ============================================================================


@dataclass
class DocumentProperties:
    """Document metadata properties.

    Standard and custom document properties for ODF documents.

    Examples:
        props = DocumentProperties(
            title="Q1 Budget Report",
            author="Finance Team",
            subject="Quarterly Budget",
            description="Detailed Q1 budget analysis",
            keywords=["budget", "finance", "Q1", "2024"],
            category="Financial Reports",
            custom_properties={
                "Department": "Finance",
                "Version": "2.1",
                "Approved By": "CFO",
            },
        )
    """

    # Standard properties
    title: str = ""
    author: str = ""
    subject: str = ""
    description: str = ""
    keywords: list[str] = field(default_factory=list)
    category: str = ""
    comments: str = ""

    # Dates
    created: datetime | None = None
    modified: datetime | None = None

    # Statistics (typically read-only)
    revision: int = 1
    editing_duration: int = 0  # seconds

    # Company info
    company: str = ""
    manager: str = ""

    # Custom properties
    custom_properties: dict[str, str] = field(default_factory=dict)

    def set_custom(self, name: str, value: str) -> None:
        """Set a custom property."""
        self.custom_properties[name] = value

    def get_custom(self, name: str, default: str = "") -> str:
        """Get a custom property."""
        return self.custom_properties.get(name, default)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "title": self.title,
            "author": self.author,
            "subject": self.subject,
            "description": self.description,
            "keywords": self.keywords,
            "category": self.category,
            "comments": self.comments,
            "revision": self.revision,
            "company": self.company,
            "manager": self.manager,
        }

        if self.created:
            result["created"] = self.created.isoformat()
        if self.modified:
            result["modified"] = self.modified.isoformat()
        if self.custom_properties:
            result["customProperties"] = self.custom_properties

        return result


# ============================================================================
# Sheet Configuration (Combines Features)
# ============================================================================


@dataclass
class SheetAdvancedFeatures:
    """Container for advanced sheet features.

    Combines all advanced features for a sheet.
    """

    hidden: HiddenRowsColumns = field(default_factory=HiddenRowsColumns)
    outline: OutlineSettings = field(default_factory=OutlineSettings)
    auto_filter: AutoFilter | None = None
    data_tables: list[DataTable] = field(default_factory=list)
    comments: list[CellComment] = field(default_factory=list)
    hyperlinks: list[Hyperlink] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)
    shapes: list[Shape] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {}

        if self.hidden.hidden_rows or self.hidden.hidden_columns:
            result["hidden"] = self.hidden.to_dict()
        if self.outline.groups:
            result["outline"] = self.outline.to_dict()
        if self.auto_filter:
            result["autoFilter"] = self.auto_filter.to_dict()
        if self.data_tables:
            result["dataTables"] = [t.to_dict() for t in self.data_tables]
        if self.comments:
            result["comments"] = [c.to_dict() for c in self.comments]
        if self.hyperlinks:
            result["hyperlinks"] = [h.to_dict() for h in self.hyperlinks]
        if self.images:
            result["images"] = [i.to_dict() for i in self.images]
        if self.shapes:
            result["shapes"] = [s.to_dict() for s in self.shapes]

        return result
