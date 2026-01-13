"""Print layout configuration for professional spreadsheet output.

Provides comprehensive print configuration including:
- Page size and orientation
- Margins and scaling
- Headers and footers with dynamic content
- Repeat rows/columns for multi-page prints
- Page break management
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ============================================================================
# Enumerations
# ============================================================================


class PageSize(Enum):
    """Standard paper sizes."""

    LETTER = "letter"  # 8.5 x 11 inches
    LEGAL = "legal"  # 8.5 x 14 inches
    TABLOID = "tabloid"  # 11 x 17 inches
    A3 = "a3"  # 297 x 420 mm
    A4 = "a4"  # 210 x 297 mm
    A5 = "a5"  # 148 x 210 mm
    B4 = "b4"  # 250 x 353 mm
    B5 = "b5"  # 176 x 250 mm
    EXECUTIVE = "executive"  # 7.25 x 10.5 inches
    CUSTOM = "custom"

    @property
    def dimensions_mm(self) -> tuple[float, float]:
        """Get dimensions in millimeters (width, height)."""
        sizes = {
            "letter": (215.9, 279.4),
            "legal": (215.9, 355.6),
            "tabloid": (279.4, 431.8),
            "a3": (297.0, 420.0),
            "a4": (210.0, 297.0),
            "a5": (148.0, 210.0),
            "b4": (250.0, 353.0),
            "b5": (176.0, 250.0),
            "executive": (184.2, 266.7),
            "custom": (210.0, 297.0),  # Default to A4
        }
        return sizes.get(self.value, (210.0, 297.0))


class PageOrientation(Enum):
    """Page orientation."""

    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class PrintQuality(Enum):
    """Print quality options."""

    DRAFT = 150
    NORMAL = 300
    HIGH = 600


class HeaderFooterSection(Enum):
    """Header/footer section."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class PrintScale(Enum):
    """Print scaling options."""

    NONE = "none"  # No scaling
    FIT_TO_PAGE = "fit_to_page"  # Fit all on one page
    FIT_TO_WIDTH = "fit_to_width"  # Fit to page width
    FIT_TO_HEIGHT = "fit_to_height"  # Fit to page height
    PERCENTAGE = "percentage"  # Custom percentage


# ============================================================================
# Page Margins
# ============================================================================


@dataclass
class PageMargins:
    """Page margin configuration.

    All measurements in centimeters.

    Attributes:
        top: Top margin
        bottom: Bottom margin
        left: Left margin
        right: Right margin
        header: Header margin (distance from edge to header)
        footer: Footer margin (distance from edge to footer)
    """

    top: float = 2.0
    bottom: float = 2.0
    left: float = 2.0
    right: float = 2.0
    header: float = 1.0
    footer: float = 1.0

    @classmethod
    def narrow(cls) -> PageMargins:
        """Create narrow margins."""
        return cls(
            top=1.27,
            bottom=1.27,
            left=1.27,
            right=1.27,
            header=0.76,
            footer=0.76,
        )

    @classmethod
    def normal(cls) -> PageMargins:
        """Create normal margins."""
        return cls(
            top=2.54,
            bottom=2.54,
            left=2.54,
            right=2.54,
            header=1.27,
            footer=1.27,
        )

    @classmethod
    def wide(cls) -> PageMargins:
        """Create wide margins."""
        return cls(
            top=2.54,
            bottom=2.54,
            left=5.08,
            right=5.08,
            header=1.27,
            footer=1.27,
        )

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "top": self.top,
            "bottom": self.bottom,
            "left": self.left,
            "right": self.right,
            "header": self.header,
            "footer": self.footer,
        }


# ============================================================================
# Header/Footer Content
# ============================================================================


@dataclass
class HeaderFooterContent:
    """Content for a header or footer section.

    Supports dynamic placeholders:
    - &[Page] - Current page number
    - &[Pages] - Total page count
    - &[Date] - Current date
    - &[Time] - Current time
    - &[File] - File name
    - &[Tab] - Sheet name
    - &[Path] - Full file path

    Attributes:
        text: Content text with placeholders
        font_family: Font family
        font_size: Font size in points
        bold: Bold text
        italic: Italic text
        color: Text color (hex)
    """

    text: str = ""
    font_family: str | None = None
    font_size: float = 10.0
    bold: bool = False
    italic: bool = False
    color: str | None = None

    @classmethod
    def page_number(cls) -> HeaderFooterContent:
        """Create page number content."""
        return cls(text="Page &[Page] of &[Pages]")

    @classmethod
    def date_time(cls) -> HeaderFooterContent:
        """Create date/time content."""
        return cls(text="&[Date] &[Time]")

    @classmethod
    def file_name(cls) -> HeaderFooterContent:
        """Create file name content."""
        return cls(text="&[File]")

    @classmethod
    def sheet_name(cls) -> HeaderFooterContent:
        """Create sheet name content."""
        return cls(text="&[Tab]")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {"text": self.text}
        if self.font_family:
            result["fontFamily"] = self.font_family
        if self.font_size != 10.0:
            result["fontSize"] = self.font_size
        if self.bold:
            result["bold"] = True
        if self.italic:
            result["italic"] = True
        if self.color:
            result["color"] = self.color
        return result


@dataclass
class HeaderFooter:
    """Complete header or footer specification.

    A header/footer has three sections: left, center, and right.

    Examples:
        # Header with title center and page number right
        header = HeaderFooter(
            center=HeaderFooterContent(text="Monthly Budget Report", bold=True),
            right=HeaderFooterContent.page_number(),
        )

        # Footer with file name left and date right
        footer = HeaderFooter(
            left=HeaderFooterContent.file_name(),
            right=HeaderFooterContent.date_time(),
        )
    """

    left: HeaderFooterContent | None = None
    center: HeaderFooterContent | None = None
    right: HeaderFooterContent | None = None

    # Visibility
    different_first_page: bool = False
    different_odd_even: bool = False
    scale_with_document: bool = True

    @classmethod
    def simple(cls, text: str, position: str = "center") -> HeaderFooter:
        """Create simple header/footer with text in one position."""
        content = HeaderFooterContent(text=text)
        if position == "left":
            return cls(left=content)
        elif position == "right":
            return cls(right=content)
        return cls(center=content)

    @classmethod
    def page_number_right(cls) -> HeaderFooter:
        """Create header/footer with page number on right."""
        return cls(right=HeaderFooterContent.page_number())

    @classmethod
    def title_and_page(cls, title: str) -> HeaderFooter:
        """Create header with title center and page number right."""
        return cls(
            center=HeaderFooterContent(text=title, bold=True),
            right=HeaderFooterContent.page_number(),
        )

    def is_empty(self) -> bool:
        """Check if header/footer has no content."""
        return (
            (self.left is None or not self.left.text)
            and (self.center is None or not self.center.text)
            and (self.right is None or not self.right.text)
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "differentFirstPage": self.different_first_page,
            "differentOddEven": self.different_odd_even,
            "scaleWithDocument": self.scale_with_document,
        }
        if self.left:
            result["left"] = self.left.to_dict()
        if self.center:
            result["center"] = self.center.to_dict()
        if self.right:
            result["right"] = self.right.to_dict()
        return result


# ============================================================================
# Page Break Configuration
# ============================================================================


@dataclass
class PageBreak:
    """Page break specification.

    Attributes:
        position: Row or column number (1-based)
        is_row_break: True for row break, False for column break
        manual: Whether this is a manual break
    """

    position: int
    is_row_break: bool = True
    manual: bool = True


# ============================================================================
# Print Area Configuration
# ============================================================================


@dataclass
class PrintArea:
    """Print area specification.

    Attributes:
        range: Cell range to print (e.g., "A1:D50")
        sheet: Sheet name (optional for multi-sheet)
    """

    range: str
    sheet: str | None = None

    def to_string(self) -> str:
        """Convert to range string."""
        if self.sheet:
            return f"{self.sheet}.{self.range}"
        return self.range


# ============================================================================
# Repeat Configuration
# ============================================================================


@dataclass
class RepeatConfig:
    """Configuration for repeating rows/columns on each page.

    Attributes:
        rows_start: First row to repeat (1-based, None for none)
        rows_end: Last row to repeat (1-based, None for none)
        columns_start: First column to repeat (1-based, None for none)
        columns_end: Last column to repeat (1-based, None for none)
    """

    rows_start: int | None = None
    rows_end: int | None = None
    columns_start: int | None = None
    columns_end: int | None = None

    @classmethod
    def header_row(cls, rows: int = 1) -> RepeatConfig:
        """Create config to repeat header row(s)."""
        return cls(rows_start=1, rows_end=rows)

    @classmethod
    def header_rows(cls, start: int, end: int) -> RepeatConfig:
        """Create config to repeat specific rows."""
        return cls(rows_start=start, rows_end=end)

    @classmethod
    def label_column(cls, columns: int = 1) -> RepeatConfig:
        """Create config to repeat label column(s)."""
        return cls(columns_start=1, columns_end=columns)

    @classmethod
    def both(
        cls,
        header_rows: int = 1,
        label_columns: int = 1,
    ) -> RepeatConfig:
        """Create config to repeat both rows and columns."""
        return cls(
            rows_start=1,
            rows_end=header_rows,
            columns_start=1,
            columns_end=label_columns,
        )

    def to_dict(self) -> dict[str, int | None]:
        """Convert to dictionary."""
        return {
            "rowsStart": self.rows_start,
            "rowsEnd": self.rows_end,
            "columnsStart": self.columns_start,
            "columnsEnd": self.columns_end,
        }


# ============================================================================
# Complete Page Setup
# ============================================================================


@dataclass
class PageSetup:
    """Complete page setup configuration.

    Combines all print layout settings.

    Examples:
        # Basic A4 landscape with header
        setup = PageSetup(
            size=PageSize.A4,
            orientation=PageOrientation.LANDSCAPE,
            header=HeaderFooter.title_and_page("Monthly Budget"),
            footer=HeaderFooter(
                left=HeaderFooterContent.file_name(),
                right=HeaderFooterContent.date_time(),
            ),
        )

        # Custom print area with repeat headers
        setup = PageSetup(
            print_area=PrintArea("A1:G100"),
            repeat=RepeatConfig.header_row(),
            margins=PageMargins.narrow(),
            scale_mode=PrintScale.FIT_TO_WIDTH,
        )
    """

    # Page size and orientation
    size: PageSize = PageSize.A4
    orientation: PageOrientation = PageOrientation.PORTRAIT
    custom_width: float | None = None  # mm, for custom size
    custom_height: float | None = None  # mm, for custom size

    # Margins
    margins: PageMargins = field(default_factory=PageMargins.normal)

    # Scaling
    scale_mode: PrintScale = PrintScale.NONE
    scale_percentage: int = 100  # For PERCENTAGE mode
    fit_to_pages_wide: int = 1  # For FIT_TO_WIDTH
    fit_to_pages_tall: int = 1  # For FIT_TO_HEIGHT

    # Headers and footers
    header: HeaderFooter | None = None
    footer: HeaderFooter | None = None

    # Print area and repeat
    print_area: PrintArea | None = None
    repeat: RepeatConfig | None = None

    # Page breaks
    page_breaks: list[PageBreak] = field(default_factory=list)

    # Print options
    print_gridlines: bool = False
    print_row_col_headers: bool = False
    print_comments: str = "none"  # "none", "at_end", "in_place"
    print_errors: str = "displayed"  # "displayed", "blank", "dash", "na"
    black_and_white: bool = False
    draft_quality: bool = False
    print_order: str = "down_then_over"  # or "over_then_down"

    # Quality
    print_quality: PrintQuality = PrintQuality.NORMAL
    horizontal_dpi: int | None = None
    vertical_dpi: int | None = None

    # Center on page
    center_horizontally: bool = False
    center_vertically: bool = False

    def add_page_break(
        self,
        position: int,
        is_row_break: bool = True,
    ) -> None:
        """Add a manual page break."""
        self.page_breaks.append(PageBreak(position=position, is_row_break=is_row_break))

    def effective_dimensions(self) -> tuple[float, float]:
        """Get effective page dimensions considering orientation.

        Returns:
            (width, height) in millimeters
        """
        if self.size == PageSize.CUSTOM:
            width = self.custom_width or 210.0
            height = self.custom_height or 297.0
        else:
            width, height = self.size.dimensions_mm

        if self.orientation == PageOrientation.LANDSCAPE:
            return (height, width)
        return (width, height)

    def printable_area(self) -> tuple[float, float]:
        """Get printable area dimensions.

        Returns:
            (width, height) in millimeters
        """
        width, height = self.effective_dimensions()

        # Convert margins from cm to mm
        margin_left_mm = self.margins.left * 10
        margin_right_mm = self.margins.right * 10
        margin_top_mm = self.margins.top * 10
        margin_bottom_mm = self.margins.bottom * 10

        printable_width = width - margin_left_mm - margin_right_mm
        printable_height = height - margin_top_mm - margin_bottom_mm

        return (printable_width, printable_height)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "size": self.size.value,
            "orientation": self.orientation.value,
            "margins": self.margins.to_dict(),
            "scaleMode": self.scale_mode.value,
        }

        if self.size == PageSize.CUSTOM:
            result["customWidth"] = self.custom_width
            result["customHeight"] = self.custom_height

        if self.scale_mode == PrintScale.PERCENTAGE:
            result["scalePercentage"] = self.scale_percentage
        elif self.scale_mode in (PrintScale.FIT_TO_WIDTH, PrintScale.FIT_TO_PAGE):
            result["fitToPagesWide"] = self.fit_to_pages_wide
            result["fitToPagesTall"] = self.fit_to_pages_tall

        if self.header and not self.header.is_empty():
            result["header"] = self.header.to_dict()
        if self.footer and not self.footer.is_empty():
            result["footer"] = self.footer.to_dict()

        if self.print_area:
            result["printArea"] = self.print_area.to_string()
        if self.repeat:
            result["repeat"] = self.repeat.to_dict()

        if self.page_breaks:
            result["pageBreaks"] = [
                {
                    "position": pb.position,
                    "isRowBreak": pb.is_row_break,
                    "manual": pb.manual,
                }
                for pb in self.page_breaks
            ]

        # Print options
        result["options"] = {
            "gridlines": self.print_gridlines,
            "rowColHeaders": self.print_row_col_headers,
            "comments": self.print_comments,
            "errors": self.print_errors,
            "blackAndWhite": self.black_and_white,
            "draftQuality": self.draft_quality,
            "printOrder": self.print_order,
            "centerHorizontally": self.center_horizontally,
            "centerVertically": self.center_vertically,
        }

        return result


# ============================================================================
# Financial Report Presets
# ============================================================================


class PrintPresets:
    """Pre-configured print setups for common financial reports.

    Provides ready-to-use page setups for standard financial documents.
    """

    @staticmethod
    def monthly_report(title: str = "Monthly Report") -> PageSetup:
        """Create page setup for monthly financial report.

        A4 portrait with title header and page numbers.
        """
        return PageSetup(
            size=PageSize.A4,
            orientation=PageOrientation.PORTRAIT,
            margins=PageMargins.normal(),
            header=HeaderFooter(
                center=HeaderFooterContent(text=title, bold=True, font_size=12),
            ),
            footer=HeaderFooter(
                left=HeaderFooterContent.date_time(),
                right=HeaderFooterContent.page_number(),
            ),
            repeat=RepeatConfig.header_row(),
            print_gridlines=True,
        )

    @staticmethod
    def budget_overview(title: str = "Budget Overview") -> PageSetup:
        """Create page setup for budget overview (landscape).

        A4 landscape for wide tables with multiple columns.
        """
        return PageSetup(
            size=PageSize.A4,
            orientation=PageOrientation.LANDSCAPE,
            margins=PageMargins.narrow(),
            scale_mode=PrintScale.FIT_TO_WIDTH,
            fit_to_pages_wide=1,
            header=HeaderFooter(
                center=HeaderFooterContent(text=title, bold=True, font_size=14),
            ),
            footer=HeaderFooter(
                center=HeaderFooterContent.page_number(),
            ),
            repeat=RepeatConfig.both(header_rows=1, label_columns=1),
        )

    @staticmethod
    def cash_flow_statement(title: str = "Cash Flow Statement") -> PageSetup:
        """Create page setup for cash flow statement.

        Letter size portrait, professional formatting.
        """
        return PageSetup(
            size=PageSize.LETTER,
            orientation=PageOrientation.PORTRAIT,
            margins=PageMargins(
                top=2.5,
                bottom=2.5,
                left=3.0,
                right=2.0,
                header=1.5,
                footer=1.5,
            ),
            header=HeaderFooter(
                left=HeaderFooterContent(text="CONFIDENTIAL", italic=True),
                center=HeaderFooterContent(text=title, bold=True),
                right=HeaderFooterContent.date_time(),
            ),
            footer=HeaderFooter(
                center=HeaderFooterContent.page_number(),
            ),
            repeat=RepeatConfig.header_row(),
        )

    @staticmethod
    def invoice(company_name: str = "") -> PageSetup:
        """Create page setup for invoices.

        A4 portrait, minimal margins, no gridlines.
        """
        header_text = company_name if company_name else ""
        return PageSetup(
            size=PageSize.A4,
            orientation=PageOrientation.PORTRAIT,
            margins=PageMargins(
                top=1.5,
                bottom=1.5,
                left=1.5,
                right=1.5,
                header=0.75,
                footer=0.75,
            ),
            header=HeaderFooter(
                left=HeaderFooterContent(text=header_text, bold=True, font_size=12)
                if header_text
                else None,
            ),
            footer=HeaderFooter(
                center=HeaderFooterContent(text="Thank you for your business"),
            ),
            print_gridlines=False,
        )

    @staticmethod
    def financial_dashboard() -> PageSetup:
        """Create page setup for dashboard printouts.

        Tabloid landscape for comprehensive dashboards.
        """
        return PageSetup(
            size=PageSize.TABLOID,
            orientation=PageOrientation.LANDSCAPE,
            margins=PageMargins.narrow(),
            scale_mode=PrintScale.FIT_TO_PAGE,
            fit_to_pages_wide=1,
            fit_to_pages_tall=1,
            footer=HeaderFooter(
                left=HeaderFooterContent.file_name(),
                center=HeaderFooterContent.date_time(),
                right=HeaderFooterContent.page_number(),
            ),
            center_horizontally=True,
            center_vertically=True,
        )

    @staticmethod
    def expense_report(employee_name: str = "") -> PageSetup:
        """Create page setup for expense reports.

        Letter size portrait with employee header.
        """
        return PageSetup(
            size=PageSize.LETTER,
            orientation=PageOrientation.PORTRAIT,
            margins=PageMargins.normal(),
            header=HeaderFooter(
                left=HeaderFooterContent(
                    text=f"Employee: {employee_name}" if employee_name else ""
                ),
                center=HeaderFooterContent(text="Expense Report", bold=True),
                right=HeaderFooterContent(text="&[Tab]"),
            ),
            footer=HeaderFooter(
                left=HeaderFooterContent(text="Submitted: &[Date]"),
                right=HeaderFooterContent.page_number(),
            ),
            repeat=RepeatConfig.header_row(),
            print_gridlines=True,
        )


# ============================================================================
# Builder API for Page Setup (Fluent Interface)
# ============================================================================


@dataclass
class PageSetupBuilder:
    r"""Fluent builder for PageSetup configuration.

    Examples:
        setup = PageSetupBuilder() \\
            .a4() \\
            .landscape() \\
            .narrow_margins() \\
            .fit_to_width() \\
            .header(title="Monthly Budget", page_number=True) \\
            .footer(date=True) \\
            .repeat_header_row() \\
            .build()
    """

    _setup: PageSetup = field(default_factory=PageSetup)

    # Size methods
    def a4(self) -> PageSetupBuilder:
        """Set A4 paper size."""
        self._setup.size = PageSize.A4
        return self

    def letter(self) -> PageSetupBuilder:
        """Set Letter paper size."""
        self._setup.size = PageSize.LETTER
        return self

    def legal(self) -> PageSetupBuilder:
        """Set Legal paper size."""
        self._setup.size = PageSize.LEGAL
        return self

    def tabloid(self) -> PageSetupBuilder:
        """Set Tabloid paper size."""
        self._setup.size = PageSize.TABLOID
        return self

    def custom_size(self, width_mm: float, height_mm: float) -> PageSetupBuilder:
        """Set custom paper size in millimeters."""
        self._setup.size = PageSize.CUSTOM
        self._setup.custom_width = width_mm
        self._setup.custom_height = height_mm
        return self

    # Orientation methods
    def portrait(self) -> PageSetupBuilder:
        """Set portrait orientation."""
        self._setup.orientation = PageOrientation.PORTRAIT
        return self

    def landscape(self) -> PageSetupBuilder:
        """Set landscape orientation."""
        self._setup.orientation = PageOrientation.LANDSCAPE
        return self

    # Margin methods
    def narrow_margins(self) -> PageSetupBuilder:
        """Set narrow margins."""
        self._setup.margins = PageMargins.narrow()
        return self

    def normal_margins(self) -> PageSetupBuilder:
        """Set normal margins."""
        self._setup.margins = PageMargins.normal()
        return self

    def wide_margins(self) -> PageSetupBuilder:
        """Set wide margins."""
        self._setup.margins = PageMargins.wide()
        return self

    def margins(
        self,
        top: float = 2.0,
        bottom: float = 2.0,
        left: float = 2.0,
        right: float = 2.0,
    ) -> PageSetupBuilder:
        """Set custom margins in centimeters."""
        self._setup.margins = PageMargins(
            top=top,
            bottom=bottom,
            left=left,
            right=right,
        )
        return self

    # Scaling methods
    def fit_to_width(self, pages: int = 1) -> PageSetupBuilder:
        """Fit content to specified number of pages wide."""
        self._setup.scale_mode = PrintScale.FIT_TO_WIDTH
        self._setup.fit_to_pages_wide = pages
        return self

    def fit_to_page(self) -> PageSetupBuilder:
        """Fit all content on one page."""
        self._setup.scale_mode = PrintScale.FIT_TO_PAGE
        self._setup.fit_to_pages_wide = 1
        self._setup.fit_to_pages_tall = 1
        return self

    def scale(self, percentage: int) -> PageSetupBuilder:
        """Set scaling percentage."""
        self._setup.scale_mode = PrintScale.PERCENTAGE
        self._setup.scale_percentage = percentage
        return self

    # Header/footer methods
    def header(
        self,
        title: str | None = None,
        page_number: bool = False,
        date: bool = False,
    ) -> PageSetupBuilder:
        """Configure header."""
        left = None
        center = None
        right = None

        if title:
            center = HeaderFooterContent(text=title, bold=True)
        if page_number:
            right = HeaderFooterContent.page_number()
        if date:
            left = HeaderFooterContent.date_time()

        self._setup.header = HeaderFooter(left=left, center=center, right=right)
        return self

    def footer(
        self,
        text: str | None = None,
        page_number: bool = False,
        date: bool = False,
    ) -> PageSetupBuilder:
        """Configure footer."""
        left = None
        center = None
        right = None

        if text:
            center = HeaderFooterContent(text=text)
        if page_number:
            right = HeaderFooterContent.page_number()
        if date:
            left = HeaderFooterContent.date_time()

        self._setup.footer = HeaderFooter(left=left, center=center, right=right)
        return self

    # Print area methods
    def print_area(self, range_ref: str) -> PageSetupBuilder:
        """Set print area."""
        self._setup.print_area = PrintArea(range=range_ref)
        return self

    # Repeat methods
    def repeat_header_row(self, rows: int = 1) -> PageSetupBuilder:
        """Repeat header row(s) on each page."""
        self._setup.repeat = RepeatConfig.header_row(rows)
        return self

    def repeat_label_column(self, columns: int = 1) -> PageSetupBuilder:
        """Repeat label column(s) on each page."""
        self._setup.repeat = RepeatConfig.label_column(columns)
        return self

    # Options
    def gridlines(self, show: bool = True) -> PageSetupBuilder:
        """Show gridlines when printing."""
        self._setup.print_gridlines = show
        return self

    def center(
        self,
        horizontally: bool = True,
        vertically: bool = True,
    ) -> PageSetupBuilder:
        """Center content on page."""
        self._setup.center_horizontally = horizontally
        self._setup.center_vertically = vertically
        return self

    def build(self) -> PageSetup:
        """Build the PageSetup object."""
        return self._setup
