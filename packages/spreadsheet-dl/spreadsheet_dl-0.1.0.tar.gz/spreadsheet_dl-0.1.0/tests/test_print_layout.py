"""
Tests for print layout module.


"""

import pytest

from spreadsheet_dl.schema.print_layout import (
    HeaderFooter,
    HeaderFooterContent,
    PageMargins,
    PageOrientation,
    PageSetup,
    PageSetupBuilder,
    PageSize,
    PrintArea,
    PrintPresets,
    PrintScale,
    RepeatConfig,
)

pytestmark = [pytest.mark.unit, pytest.mark.rendering]


class TestPageSize:
    """Tests for PageSize enum."""

    def test_a4_dimensions(self) -> None:
        """Test A4 dimensions."""
        width, height = PageSize.A4.dimensions_mm
        assert width == 210.0
        assert height == 297.0

    def test_letter_dimensions(self) -> None:
        """Test Letter dimensions."""
        width, height = PageSize.LETTER.dimensions_mm
        assert width == 215.9
        assert height == 279.4

    def test_tabloid_dimensions(self) -> None:
        """Test Tabloid dimensions."""
        width, height = PageSize.TABLOID.dimensions_mm
        assert width == 279.4
        assert height == 431.8


class TestPageMargins:
    """Tests for PageMargins."""

    def test_default_margins(self) -> None:
        """Test default margin values."""
        margins = PageMargins()
        assert margins.top == 2.0
        assert margins.bottom == 2.0
        assert margins.left == 2.0
        assert margins.right == 2.0

    def test_narrow_margins(self) -> None:
        """Test narrow margin preset."""
        margins = PageMargins.narrow()
        assert margins.top == 1.27
        assert margins.left == 1.27

    def test_normal_margins(self) -> None:
        """Test normal margin preset."""
        margins = PageMargins.normal()
        assert margins.top == 2.54
        assert margins.left == 2.54

    def test_wide_margins(self) -> None:
        """Test wide margin preset."""
        margins = PageMargins.wide()
        assert margins.left == 5.08
        assert margins.right == 5.08

    def test_to_dict(self) -> None:
        """Test dictionary conversion."""
        margins = PageMargins(top=1.0, bottom=2.0, left=3.0, right=4.0)
        result = margins.to_dict()
        assert result["top"] == 1.0
        assert result["bottom"] == 2.0
        assert result["left"] == 3.0
        assert result["right"] == 4.0


class TestHeaderFooterContent:
    """Tests for HeaderFooterContent."""

    def test_basic_content(self) -> None:
        """Test basic content creation."""
        content = HeaderFooterContent(text="Budget Report")
        assert content.text == "Budget Report"
        assert content.font_size == 10.0
        assert content.bold is False

    def test_styled_content(self) -> None:
        """Test styled content."""
        content = HeaderFooterContent(
            text="Title",
            font_size=14.0,
            bold=True,
            italic=True,
        )
        assert content.font_size == 14.0
        assert content.bold is True
        assert content.italic is True

    def test_page_number_factory(self) -> None:
        """Test page number factory method."""
        content = HeaderFooterContent.page_number()
        assert "&[Page]" in content.text
        assert "&[Pages]" in content.text

    def test_date_time_factory(self) -> None:
        """Test date/time factory method."""
        content = HeaderFooterContent.date_time()
        assert "&[Date]" in content.text
        assert "&[Time]" in content.text

    def test_to_dict(self) -> None:
        """Test dictionary conversion."""
        content = HeaderFooterContent(text="Test", bold=True)
        result = content.to_dict()
        assert result["text"] == "Test"
        assert result["bold"] is True


class TestHeaderFooter:
    """Tests for HeaderFooter."""

    def test_empty_header(self) -> None:
        """Test empty header detection."""
        header = HeaderFooter()
        assert header.is_empty() is True

    def test_non_empty_header(self) -> None:
        """Test non-empty header."""
        header = HeaderFooter(center=HeaderFooterContent(text="Title"))
        assert header.is_empty() is False

    def test_simple_factory(self) -> None:
        """Test simple factory method."""
        header = HeaderFooter.simple("My Report", "center")
        assert header.center is not None
        assert header.center.text == "My Report"
        assert header.left is None
        assert header.right is None

    def test_page_number_right_factory(self) -> None:
        """Test page number right factory."""
        header = HeaderFooter.page_number_right()
        assert header.right is not None
        assert "&[Page]" in header.right.text

    def test_title_and_page_factory(self) -> None:
        """Test title and page factory."""
        header = HeaderFooter.title_and_page("Budget Report")
        assert header.center is not None
        assert header.center.text == "Budget Report"
        assert header.center is not None
        assert header.center.bold is True
        assert header.right is not None

    def test_to_dict(self) -> None:
        """Test dictionary conversion."""
        header = HeaderFooter(
            left=HeaderFooterContent(text="Left"),
            center=HeaderFooterContent(text="Center"),
            right=HeaderFooterContent(text="Right"),
        )
        result = header.to_dict()
        assert "left" in result
        assert "center" in result
        assert "right" in result


class TestPrintArea:
    """Tests for PrintArea."""

    def test_basic_print_area(self) -> None:
        """Test basic print area."""
        area = PrintArea(range="A1:D50")
        assert area.to_string() == "A1:D50"

    def test_print_area_with_sheet(self) -> None:
        """Test print area with sheet name."""
        area = PrintArea(range="A1:D50", sheet="Budget")
        assert area.to_string() == "Budget.A1:D50"


class TestRepeatConfig:
    """Tests for RepeatConfig."""

    def test_header_row(self) -> None:
        """Test header row repeat."""
        config = RepeatConfig.header_row()
        assert config.rows_start == 1
        assert config.rows_end == 1

    def test_header_rows_multiple(self) -> None:
        """Test multiple header rows."""
        config = RepeatConfig.header_row(rows=3)
        assert config.rows_start == 1
        assert config.rows_end == 3

    def test_label_column(self) -> None:
        """Test label column repeat."""
        config = RepeatConfig.label_column()
        assert config.columns_start == 1
        assert config.columns_end == 1

    def test_both_rows_and_columns(self) -> None:
        """Test repeating both rows and columns."""
        config = RepeatConfig.both(header_rows=2, label_columns=1)
        assert config.rows_start == 1
        assert config.rows_end == 2
        assert config.columns_start == 1
        assert config.columns_end == 1


class TestPageSetup:
    """Tests for PageSetup."""

    def test_default_setup(self) -> None:
        """Test default page setup."""
        setup = PageSetup()
        assert setup.size == PageSize.A4
        assert setup.orientation == PageOrientation.PORTRAIT

    def test_landscape_orientation(self) -> None:
        """Test landscape orientation."""
        setup = PageSetup(orientation=PageOrientation.LANDSCAPE)
        assert setup.orientation == PageOrientation.LANDSCAPE

    def test_effective_dimensions_portrait(self) -> None:
        """Test effective dimensions in portrait."""
        setup = PageSetup(
            size=PageSize.A4,
            orientation=PageOrientation.PORTRAIT,
        )
        width, height = setup.effective_dimensions()
        assert width == 210.0
        assert height == 297.0

    def test_effective_dimensions_landscape(self) -> None:
        """Test effective dimensions in landscape."""
        setup = PageSetup(
            size=PageSize.A4,
            orientation=PageOrientation.LANDSCAPE,
        )
        width, height = setup.effective_dimensions()
        assert width == 297.0
        assert height == 210.0

    def test_printable_area(self) -> None:
        """Test printable area calculation."""
        setup = PageSetup(
            size=PageSize.A4,
            margins=PageMargins(top=2.0, bottom=2.0, left=2.0, right=2.0),
        )
        width, height = setup.printable_area()
        # A4 is 210x297mm, margins are 2cm (20mm) each side
        assert width == pytest.approx(170.0)  # 210 - 20 - 20
        assert height == pytest.approx(257.0)  # 297 - 20 - 20

    def test_add_page_break(self) -> None:
        """Test adding page breaks."""
        setup = PageSetup()
        setup.add_page_break(10, is_row_break=True)
        setup.add_page_break(5, is_row_break=False)
        assert len(setup.page_breaks) == 2
        assert setup.page_breaks[0].position == 10
        assert setup.page_breaks[0].is_row_break is True

    def test_scale_modes(self) -> None:
        """Test different scale modes."""
        setup = PageSetup(scale_mode=PrintScale.FIT_TO_WIDTH)
        assert setup.scale_mode == PrintScale.FIT_TO_WIDTH

    def test_to_dict(self) -> None:
        """Test dictionary conversion."""
        setup = PageSetup(
            size=PageSize.A4,
            orientation=PageOrientation.LANDSCAPE,
            header=HeaderFooter.title_and_page("Report"),
        )
        result = setup.to_dict()
        assert result["size"] == "a4"
        assert result["orientation"] == "landscape"
        assert "header" in result


class TestPrintPresets:
    """Tests for PrintPresets."""

    def test_monthly_report(self) -> None:
        """Test monthly report preset."""
        setup = PrintPresets.monthly_report("Budget Report")
        assert setup.size == PageSize.A4
        assert setup.orientation == PageOrientation.PORTRAIT
        assert setup.header is not None
        assert setup.footer is not None
        assert setup.repeat is not None

    def test_budget_overview(self) -> None:
        """Test budget overview preset."""
        setup = PrintPresets.budget_overview()
        assert setup.orientation == PageOrientation.LANDSCAPE
        assert setup.scale_mode == PrintScale.FIT_TO_WIDTH

    def test_cash_flow_statement(self) -> None:
        """Test cash flow statement preset."""
        setup = PrintPresets.cash_flow_statement()
        assert setup.size == PageSize.LETTER
        assert setup.header is not None

    def test_invoice(self) -> None:
        """Test invoice preset."""
        setup = PrintPresets.invoice("ACME Corp")
        assert setup.print_gridlines is False

    def test_financial_dashboard(self) -> None:
        """Test financial dashboard preset."""
        setup = PrintPresets.financial_dashboard()
        assert setup.size == PageSize.TABLOID
        assert setup.orientation == PageOrientation.LANDSCAPE
        assert setup.center_horizontally is True


class TestPageSetupBuilder:
    """Tests for PageSetupBuilder fluent API."""

    def test_basic_builder(self) -> None:
        """Test basic builder usage."""
        setup = PageSetupBuilder().a4().portrait().build()
        assert setup.size == PageSize.A4
        assert setup.orientation == PageOrientation.PORTRAIT

    def test_landscape_with_margins(self) -> None:
        """Test landscape with custom margins."""
        setup = PageSetupBuilder().letter().landscape().narrow_margins().build()
        assert setup.size == PageSize.LETTER
        assert setup.orientation == PageOrientation.LANDSCAPE
        assert setup.margins.top == 1.27

    def test_scaling(self) -> None:
        """Test scaling options."""
        setup = PageSetupBuilder().a4().fit_to_width(2).build()
        assert setup.scale_mode == PrintScale.FIT_TO_WIDTH
        assert setup.fit_to_pages_wide == 2

    def test_fit_to_page(self) -> None:
        """Test fit to page."""
        setup = PageSetupBuilder().tabloid().fit_to_page().build()
        assert setup.scale_mode == PrintScale.FIT_TO_PAGE
        assert setup.fit_to_pages_wide == 1
        assert setup.fit_to_pages_tall == 1

    def test_header_footer(self) -> None:
        """Test header and footer configuration."""
        setup = (
            PageSetupBuilder()
            .a4()
            .header(title="Report", page_number=True)
            .footer(date=True)
            .build()
        )
        assert setup.header is not None
        assert setup.header.center is not None
        assert setup.header.center.text == "Report"
        assert setup.header.right is not None
        assert setup.footer is not None
        assert setup.footer.left is not None

    def test_print_area_and_repeat(self) -> None:
        """Test print area and repeat configuration."""
        setup = (
            PageSetupBuilder().a4().print_area("A1:G100").repeat_header_row(2).build()
        )
        assert setup.print_area is not None
        assert setup.print_area.range == "A1:G100"
        assert setup.repeat is not None
        assert setup.repeat.rows_end == 2

    def test_gridlines_and_centering(self) -> None:
        """Test gridlines and centering options."""
        setup = (
            PageSetupBuilder()
            .a4()
            .gridlines(True)
            .center(horizontally=True, vertically=False)
            .build()
        )
        assert setup.print_gridlines is True
        assert setup.center_horizontally is True
        assert setup.center_vertically is False

    def test_custom_size(self) -> None:
        """Test custom paper size."""
        setup = PageSetupBuilder().custom_size(200.0, 300.0).build()
        assert setup.size == PageSize.CUSTOM
        assert setup.custom_width == 200.0
        assert setup.custom_height == 300.0

    def test_percentage_scale(self) -> None:
        """Test percentage scaling."""
        setup = PageSetupBuilder().a4().scale(75).build()
        assert setup.scale_mode == PrintScale.PERCENTAGE
        assert setup.scale_percentage == 75

    def test_full_configuration(self) -> None:
        """Test full configuration chain."""
        setup = (
            PageSetupBuilder()
            .a4()
            .landscape()
            .narrow_margins()
            .fit_to_width()
            .header(title="Q1 Budget Report", page_number=True)
            .footer(date=True)
            .print_area("A1:L50")
            .repeat_header_row()
            .gridlines(True)
            .center(horizontally=True, vertically=True)
            .build()
        )

        assert setup.size == PageSize.A4
        assert setup.orientation == PageOrientation.LANDSCAPE
        assert setup.margins.top == 1.27
        assert setup.scale_mode == PrintScale.FIT_TO_WIDTH
        assert setup.header is not None
        assert setup.header.center is not None
        assert setup.header.center.text == "Q1 Budget Report"
        assert setup.print_area is not None
        assert setup.print_area.range == "A1:L50"
        assert setup.repeat is not None
        assert setup.repeat.rows_end == 1
        assert setup.print_gridlines is True
        assert setup.center_horizontally is True
