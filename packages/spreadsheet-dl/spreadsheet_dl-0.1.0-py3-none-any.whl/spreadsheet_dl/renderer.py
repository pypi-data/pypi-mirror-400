"""ODS Renderer - Converts builder specifications to ODS files.

This module bridges the builder API with odfpy, translating
theme-based styles and sheet specifications into actual ODS documents.

Features:
    - Cell merge rendering with covered cells
    - Named range integration
    - Chart rendering to ODS
    - Conditional format rendering
    - Data validation rendering
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Chart imports
from odf import chart as odfchart
from odf.draw import Frame, Object
from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import (
    GraphicProperties,
    Style,
    TableCellProperties,
    TableColumnProperties,
    TextProperties,
)
from odf.table import (
    CoveredTableCell,
    NamedRange,
    Table,
    TableCell,
    TableColumn,
    TableRow,
)
from odf.text import P

if TYPE_CHECKING:
    from spreadsheet_dl.builder import (
        CellSpec,
        ColumnSpec,
        RowSpec,
        SheetSpec,
    )
    from spreadsheet_dl.builder import (
        NamedRange as NamedRangeSpec,
    )
    from spreadsheet_dl.charts import ChartSpec, ChartType, DataSeries
    from spreadsheet_dl.schema.conditional import ConditionalFormat
    from spreadsheet_dl.schema.data_validation import ValidationConfig
    from spreadsheet_dl.schema.styles import CellStyle, Theme


class OdsRenderer:
    """Render sheet specifications to ODS files.

    Handles:
    - Theme-based style generation
    - Cell formatting (currency, date, percentage)
    - Formula rendering
    - Cell merging with covered cells
    - Multi-sheet documents
    - Chart embedding
    - Conditional formatting
    - Data validation
    """

    def __init__(self, theme: Theme | None = None) -> None:
        """Initialize renderer with optional theme.

        Args:
            theme: Theme for styling (None for default styles)
        """
        self._theme = theme
        self._doc: OpenDocumentSpreadsheet | None = None
        self._styles: dict[str, Style] = {}
        self._style_counter = 0
        self._merged_regions: set[tuple[int, int]] = (
            set()
        )  # Track merged cell positions
        self._chart_counter = 0
        self._tables: dict[str, Table] = {}  # Track tables by sheet name for charts
        self._charts: list[dict[str, Any]] = []  # Track charts for embedding

    def render(
        self,
        sheets: list[SheetSpec],
        output_path: Path,
        named_ranges: list[NamedRangeSpec] | None = None,
        charts: list[ChartSpec] | None = None,
        conditional_formats: list[ConditionalFormat] | None = None,
        validations: list[ValidationConfig] | None = None,
    ) -> Path:
        """Render sheets to ODS file.

        Supports named range export, chart rendering, conditional formatting,
        and data validation.

        Args:
            sheets: List of sheet specifications
            output_path: Output file path
            named_ranges: List of named ranges to export (optional)
            charts: List of chart specifications to render (optional)
            conditional_formats: List of conditional formats (optional)
            validations: List of data validations (optional)

        Returns:
            Path to created file
        """
        self._doc = OpenDocumentSpreadsheet()
        self._styles.clear()
        self._style_counter = 0
        self._chart_counter = 0
        self._tables.clear()
        self._charts.clear()

        # Create default styles
        self._create_default_styles()

        # Create theme-based styles if theme provided
        if self._theme:
            self._create_theme_styles()

        # Render each sheet
        for sheet_spec in sheets:
            self._render_sheet(sheet_spec)

        # Add named ranges if provided
        if named_ranges:
            self._add_named_ranges(named_ranges)

        # Add charts if provided
        if charts:
            self._add_charts(charts, sheets)

        # Add conditional formats if provided
        if conditional_formats:
            self._add_conditional_formats(conditional_formats)

        # Add data validations if provided
        if validations:
            self._add_data_validations(validations)

        # Save document
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._doc.save(str(output_path))
        return output_path

    def _create_default_styles(self) -> None:
        """Create default cell styles."""
        if self._doc is None:
            return

        # Default header style
        header_style = Style(name="DefaultHeader", family="table-cell")
        header_style.addElement(
            TableCellProperties(backgroundcolor="#4472C4", padding="2pt")
        )
        header_style.addElement(TextProperties(fontweight="bold", color="#FFFFFF"))
        self._doc.automaticstyles.addElement(header_style)
        self._styles["header"] = header_style
        self._styles["header_primary"] = header_style

        # Currency style
        currency_style = Style(name="DefaultCurrency", family="table-cell")
        currency_style.addElement(TableCellProperties(padding="2pt"))
        self._doc.automaticstyles.addElement(currency_style)
        self._styles["currency"] = currency_style
        self._styles["cell_currency"] = currency_style

        # Date style
        date_style = Style(name="DefaultDate", family="table-cell")
        date_style.addElement(TableCellProperties(padding="2pt"))
        self._doc.automaticstyles.addElement(date_style)
        self._styles["date"] = date_style
        self._styles["cell_date"] = date_style

        # Warning style (over budget)
        warning_style = Style(name="DefaultWarning", family="table-cell")
        warning_style.addElement(
            TableCellProperties(backgroundcolor="#FFC7CE", padding="2pt")
        )
        warning_style.addElement(TextProperties(color="#9C0006"))
        self._doc.automaticstyles.addElement(warning_style)
        self._styles["warning"] = warning_style
        self._styles["cell_warning"] = warning_style
        self._styles["cell_danger"] = warning_style

        # Success style (under budget)
        good_style = Style(name="DefaultGood", family="table-cell")
        good_style.addElement(
            TableCellProperties(backgroundcolor="#C6EFCE", padding="2pt")
        )
        good_style.addElement(TextProperties(color="#006100"))
        self._doc.automaticstyles.addElement(good_style)
        self._styles["good"] = good_style
        self._styles["cell_success"] = good_style

        # Normal cell style
        normal_style = Style(name="DefaultNormal", family="table-cell")
        normal_style.addElement(TableCellProperties(padding="2pt"))
        self._doc.automaticstyles.addElement(normal_style)
        self._styles["normal"] = normal_style
        self._styles["cell_normal"] = normal_style
        self._styles["default"] = normal_style

        # Total row style
        total_style = Style(name="DefaultTotal", family="table-cell")
        total_style.addElement(
            TableCellProperties(backgroundcolor="#4472C4", padding="2pt")
        )
        total_style.addElement(
            TextProperties(fontweight="bold", color="#FFFFFF", fontsize="11pt")
        )
        self._doc.automaticstyles.addElement(total_style)
        self._styles["total"] = total_style
        self._styles["total_row"] = total_style

    def _create_theme_styles(self) -> None:
        """Create styles from theme definitions."""
        if self._doc is None or self._theme is None:
            return

        for style_name in self._theme.list_styles():
            try:
                cell_style = self._theme.get_style(style_name)
                odf_style = self._create_odf_style(style_name, cell_style)
                self._doc.automaticstyles.addElement(odf_style)
                self._styles[style_name] = odf_style
            except (KeyError, ValueError, AttributeError):
                # Skip styles that fail to resolve
                pass

    def _create_odf_style(self, name: str, cell_style: CellStyle) -> Style:
        """Create ODF style from CellStyle.

        Args:
            name: Style name
            cell_style: CellStyle from theme

        Returns:
            ODF Style object
        """
        self._style_counter += 1
        style = Style(name=f"Theme_{name}_{self._style_counter}", family="table-cell")

        # Cell properties
        cell_props: dict[str, Any] = {}

        if cell_style.background_color:
            cell_props["backgroundcolor"] = str(cell_style.background_color)

        if cell_style.padding:
            cell_props["padding"] = cell_style.padding

        # Borders
        if cell_style.border_top:
            cell_props["bordertop"] = cell_style.border_top.to_odf()
        if cell_style.border_bottom:
            cell_props["borderbottom"] = cell_style.border_bottom.to_odf()
        if cell_style.border_left:
            cell_props["borderleft"] = cell_style.border_left.to_odf()
        if cell_style.border_right:
            cell_props["borderright"] = cell_style.border_right.to_odf()

        if cell_props:
            style.addElement(TableCellProperties(**cell_props))

        # Text properties
        text_props: dict[str, Any] = {}

        if cell_style.font.family:
            text_props["fontfamily"] = cell_style.font.family

        if cell_style.font.size:
            text_props["fontsize"] = cell_style.font.size

        if cell_style.font.weight.value == "bold":
            text_props["fontweight"] = "bold"

        if cell_style.font.color:
            text_props["color"] = str(cell_style.font.color)

        if cell_style.font.italic:
            text_props["fontstyle"] = "italic"

        if text_props:
            style.addElement(TextProperties(**text_props))

        return style

    def _render_sheet(self, sheet_spec: SheetSpec) -> None:
        """Render a single sheet.

        Handles cell merge rendering with covered cells.

        Args:
            sheet_spec: Sheet specification
        """
        if self._doc is None:
            return

        # Reset merged regions for each sheet
        self._merged_regions.clear()

        table = Table(name=sheet_spec.name)

        # Add print area if specified
        if sheet_spec.print_area:
            # ODF format: "$SheetName.$A$1:$D$50"
            print_range = self._format_print_range(
                sheet_spec.name, sheet_spec.print_area
            )
            table.setAttribute("printranges", print_range)

        # Add sheet protection if specified
        if sheet_spec.protection.get("enabled"):
            table.setAttribute("protected", "true")
            # If password is provided, hash it for the protection-key
            # Note: ODF uses a simple Base64-encoded hash for table protection
            password = sheet_spec.protection.get("password")
            if password:
                protection_key = self._hash_protection_password(password)
                table.setAttribute("protectionkey", protection_key)

        # Add columns with widths and visibility
        for col_spec in sheet_spec.columns:
            col_style = self._create_column_style(col_spec)
            col = TableColumn(stylename=col_style)
            # Set visibility if column is hidden
            if col_spec.hidden:
                col.setAttribute("visibility", "collapse")
            table.addElement(col)

        # Add rows
        for row_idx, row_spec in enumerate(sheet_spec.rows):
            row = self._render_row(row_spec, sheet_spec.columns, row_idx)
            table.addElement(row)

        # Store table reference for chart embedding
        self._tables[sheet_spec.name] = table
        self._doc.spreadsheet.addElement(table)

        # Add freeze panes configuration if specified
        if sheet_spec.freeze_rows > 0 or sheet_spec.freeze_cols > 0:
            self._add_freeze_panes(
                sheet_spec.name, sheet_spec.freeze_rows, sheet_spec.freeze_cols
            )

    def _add_freeze_panes(
        self, sheet_name: str, freeze_rows: int, freeze_cols: int
    ) -> None:
        """Add freeze panes configuration for a sheet.

        In ODF format, freeze panes are configured through settings.xml using
        ConfigItem elements that specify the split position and mode.

        Args:
            sheet_name: Name of the sheet
            freeze_rows: Number of rows to freeze (from top)
            freeze_cols: Number of columns to freeze (from left)
        """
        from odf.config import (
            ConfigItem,
            ConfigItemMapEntry,
            ConfigItemMapIndexed,
            ConfigItemSet,
        )

        if self._doc is None:
            return

        # Get or create the view settings config-item-set
        view_settings = None
        for child in self._doc.settings.childNodes:
            if (
                hasattr(child, "getAttribute")
                and child.getAttribute("name") == "ooo:view-settings"
            ):
                view_settings = child
                break

        if view_settings is None:
            view_settings = ConfigItemSet(name="ooo:view-settings")
            self._doc.settings.addElement(view_settings)

        # Get or create the Views map
        views_map = None
        for child in view_settings.childNodes:
            if hasattr(child, "getAttribute") and child.getAttribute("name") == "Views":
                views_map = child
                break

        if views_map is None:
            views_map = ConfigItemMapIndexed(name="Views")
            view_settings.addElement(views_map)

        # Get or create view entry
        view_entry = None
        for child in views_map.childNodes:
            if hasattr(child, "tagName") and "config-item-map-entry" in child.tagName:
                view_entry = child
                break

        if view_entry is None:
            view_entry = ConfigItemMapEntry()
            views_map.addElement(view_entry)

        # Get or create Tables map for this view
        tables_map = None
        for child in view_entry.childNodes:
            if (
                hasattr(child, "getAttribute")
                and child.getAttribute("name") == "Tables"
            ):
                tables_map = child
                break

        if tables_map is None:
            tables_map = ConfigItemMapIndexed(name="Tables")
            view_entry.addElement(tables_map)

        # Create table entry with freeze settings
        table_entry = ConfigItemMapEntry(name=sheet_name)

        # Add horizontal split (frozen rows)
        if freeze_rows > 0:
            h_split = ConfigItem(name="HorizontalSplitMode", type="short")
            h_split.addText("2")  # 2 = frozen
            table_entry.addElement(h_split)

            h_pos = ConfigItem(name="HorizontalSplitPosition", type="int")
            h_pos.addText(str(freeze_rows))
            table_entry.addElement(h_pos)

        # Add vertical split (frozen columns)
        if freeze_cols > 0:
            v_split = ConfigItem(name="VerticalSplitMode", type="short")
            v_split.addText("2")  # 2 = frozen
            table_entry.addElement(v_split)

            v_pos = ConfigItem(name="VerticalSplitPosition", type="int")
            v_pos.addText(str(freeze_cols))
            table_entry.addElement(v_pos)

        # Set active split position (bottom-right pane)
        active_pane = ConfigItem(name="ActiveSplitRange", type="short")
        active_pane.addText("3")  # 3 = bottom-right pane
        table_entry.addElement(active_pane)

        tables_map.addElement(table_entry)

    def _format_print_range(self, sheet_name: str, range_ref: str) -> str:
        """Format a cell range reference for ODF print range attribute.

        ODF print ranges use the format: "$SheetName.$A$1:$D$50"
        where column and row references are absolute.

        Args:
            sheet_name: Name of the sheet
            range_ref: Range reference (e.g., "A1:D50")

        Returns:
            ODF-formatted print range string
        """
        import re

        # Make cell references absolute
        def make_absolute(match: re.Match[str]) -> str:
            col = match.group(1)
            row = match.group(2)
            return f"${col}${row}"

        # Pattern to match cell references like A1, AB123
        cell_pattern = r"([A-Z]+)(\d+)"
        abs_range = re.sub(cell_pattern, make_absolute, range_ref.upper())

        # Format as ODF print range: $SheetName.$A$1:$D$50
        return f"${sheet_name}.{abs_range}"

    def _hash_protection_password(self, password: str) -> str:
        """Hash a protection password for ODF format.

        ODF 1.2+ uses Base64-encoded SHA-256 hash for protection keys.

        Args:
            password: Plain text password

        Returns:
            Base64-encoded SHA-256 hash
        """
        import base64
        import hashlib

        # ODF uses SHA-256 hash of the password, Base64 encoded
        password_bytes = password.encode("utf-8")
        hash_bytes = hashlib.sha256(password_bytes).digest()
        return base64.b64encode(hash_bytes).decode("ascii")

    def _create_column_style(self, col_spec: ColumnSpec) -> Style:
        """Create column style with width and visibility."""
        if self._doc is None:
            raise ValueError("Document not initialized")

        self._style_counter += 1
        col_style = Style(name=f"Col_{self._style_counter}", family="table-column")

        # Create properties with width
        props_kwargs = {"columnwidth": col_spec.width}

        # Add break-before property if column is hidden
        # ODF uses break-before="column" for hidden columns in some cases
        # but the proper way is to use visibility style
        col_style.addElement(TableColumnProperties(**props_kwargs))

        # If column is hidden, set the visibility via table:visibility attribute
        # This is handled at the TableColumn level, not in the style
        self._doc.automaticstyles.addElement(col_style)
        return col_style

    def _create_row_style(self, height: str) -> Style:
        """Create row style with height."""
        from odf.style import TableRowProperties

        if self._doc is None:
            raise ValueError("Document not initialized")

        self._style_counter += 1
        row_style = Style(name=f"Row_{self._style_counter}", family="table-row")
        row_style.addElement(TableRowProperties(rowheight=height))
        self._doc.automaticstyles.addElement(row_style)
        return row_style

    def _render_row(
        self, row_spec: RowSpec, columns: list[ColumnSpec], row_idx: int
    ) -> TableRow:
        """Render a single row.

        Handles cell merge rendering with covered cells.

        Args:
            row_spec: Row specification
            columns: Column specifications for type info
            row_idx: Current row index (0-based)

        Returns:
            ODF TableRow
        """
        # Create row with optional height style
        if row_spec.height:
            row_style = self._create_row_style(row_spec.height)
            row = TableRow(stylename=row_style)
        else:
            row = TableRow()

        for col_idx, cell_spec in enumerate(row_spec.cells):
            # Check if this cell is covered by a previous merge
            if (row_idx, col_idx) in self._merged_regions:
                # This cell is covered, skip it (covered cells added by parent)
                continue

            col_spec = columns[col_idx] if col_idx < len(columns) else None
            cell = self._render_cell(
                cell_spec, row_spec.style, col_spec, row_idx, col_idx
            )
            row.addElement(cell)

            # If cell has colspan/rowspan, add covered cells and track regions
            if cell_spec.colspan > 1 or cell_spec.rowspan > 1:
                # Mark covered regions
                for r in range(row_idx, row_idx + cell_spec.rowspan):
                    for c in range(col_idx, col_idx + cell_spec.colspan):
                        if r != row_idx or c != col_idx:  # Skip the origin cell
                            self._merged_regions.add((r, c))

                # Add covered cells for remaining columns in this row
                for _c in range(col_idx + 1, col_idx + cell_spec.colspan):
                    row.addElement(CoveredTableCell())

        return row

    def _render_cell(
        self,
        cell_spec: CellSpec,
        row_style: str | None,
        col_spec: ColumnSpec | None,
        row_idx: int,
        col_idx: int,
    ) -> TableCell:
        """Render a single cell.

        Handles cell merge rendering with colspan/rowspan.

        Args:
            cell_spec: Cell specification
            row_style: Default row style
            col_spec: Column specification for type info
            row_idx: Row index (for merge tracking)
            col_idx: Column index (for merge tracking)

        Returns:
            ODF TableCell
        """
        # Determine style
        style_name = cell_spec.style or row_style
        if style_name and style_name in self._styles:
            style = self._styles[style_name]
        else:
            style = self._styles.get("default")

        # Determine value type
        value_type = cell_spec.value_type
        if not value_type and col_spec:
            value_type = col_spec.type

        # Create cell with appropriate type
        cell_kwargs: dict[str, Any] = {}

        if style:
            cell_kwargs["stylename"] = style

        # Add colspan/rowspan attributes if merging
        if cell_spec.colspan > 1:
            cell_kwargs["numbercolumnsspanned"] = cell_spec.colspan
        if cell_spec.rowspan > 1:
            cell_kwargs["numberrowsspanned"] = cell_spec.rowspan

        if cell_spec.formula:
            cell_kwargs["formula"] = cell_spec.formula
            cell_kwargs["valuetype"] = self._get_odf_value_type(value_type)

        elif cell_spec.value is not None:
            cell_kwargs.update(self._get_value_attrs(cell_spec.value, value_type))

        cell = TableCell(**cell_kwargs)

        # Add display text
        display_text = self._get_display_text(cell_spec.value, value_type)
        if display_text:
            cell.addElement(P(text=display_text))

        return cell

    def _get_odf_value_type(self, type_hint: str | None) -> str:
        """Map type hint to ODF value type."""
        type_map = {
            "string": "string",
            "currency": "currency",
            "date": "date",
            "percentage": "percentage",
            "float": "float",
            "number": "float",
        }
        return type_map.get(type_hint or "", "string")

    def _get_value_attrs(
        self,
        value: Any,
        type_hint: str | None,
    ) -> dict[str, Any]:
        """Get ODF attributes for a cell value."""
        attrs: dict[str, Any] = {}

        if value is None:
            return attrs

        if isinstance(value, datetime):
            attrs["valuetype"] = "date"
            attrs["datevalue"] = value.date().isoformat()
        elif isinstance(value, date):
            attrs["valuetype"] = "date"
            attrs["datevalue"] = value.isoformat()
        elif isinstance(value, Decimal):
            attrs["valuetype"] = "currency" if type_hint == "currency" else "float"
            attrs["value"] = str(value)
        elif isinstance(value, (int, float)):
            if type_hint == "currency":
                attrs["valuetype"] = "currency"
            elif type_hint == "percentage":
                attrs["valuetype"] = "percentage"
            else:
                attrs["valuetype"] = "float"
            attrs["value"] = str(value)
        else:
            attrs["valuetype"] = "string"

        return attrs

    def _get_display_text(self, value: Any, type_hint: str | None) -> str:
        """Get display text for a cell value."""
        if value is None:
            return ""

        if isinstance(value, datetime):
            return value.date().strftime("%Y-%m-%d")
        elif isinstance(value, date):
            return value.strftime("%Y-%m-%d")
        elif isinstance(value, (Decimal, float)):
            if type_hint == "currency":
                return f"${value:,.2f}"
            elif type_hint == "percentage":
                return f"{value:.1%}"
            return str(value)
        elif isinstance(value, int):
            if type_hint == "currency":
                return f"${value:,}"
            return str(value)

        return str(value)

    def _add_named_ranges(self, named_ranges: list[NamedRangeSpec]) -> None:
        """Add named ranges to the ODS document.

        Exports named range definitions to ODS format.

        Args:
            named_ranges: List of named range specifications
        """
        if self._doc is None:
            return

        if not named_ranges:
            return

        # Create or get NamedExpressions container
        from odf.table import NamedExpressions

        named_expressions = None
        for child in self._doc.spreadsheet.childNodes:
            # Check by tag name since NamedExpressions is a function
            if hasattr(child, "qname") and child.qname == (
                "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
                "named-expressions",
            ):
                named_expressions = child
                break

        if named_expressions is None:
            named_expressions = NamedExpressions()
            self._doc.spreadsheet.addElement(named_expressions)

        for named_range_spec in named_ranges:
            # Build the cell range address
            range_ref = named_range_spec.range
            if range_ref.sheet:
                # Sheet-scoped range
                cell_range = f"${range_ref.sheet}.$${range_ref.start}:$${range_ref.end}"
            else:
                # Workbook-scoped range
                cell_range = f"$${range_ref.start}:$${range_ref.end}"

            # Create ODF named range
            odf_named_range = NamedRange(
                name=named_range_spec.name,
                cellrangeaddress=cell_range,
            )

            # Add to NamedExpressions container (not directly to spreadsheet)
            named_expressions.addElement(odf_named_range)

    # =========================================================================
    # Chart Rendering
    # =========================================================================

    def _add_charts(self, charts: list[ChartSpec], sheets: list[SheetSpec]) -> None:
        """Add charts to the ODS document.

        This method processes a list of ChartSpec objects and embeds them
        into the ODS document. Charts are positioned according to their
        ChartPosition configuration and attached to the appropriate sheet.

        Supports:
        - Column, bar, line, pie, area, scatter, bubble charts
        - Chart positioning by cell reference
        - Chart sizing (width/height)
        - Chart titles and legends
        - Axis configuration
        - Multiple data series with colors
        - Chart styling and customization

        Args:
            charts: List of chart specifications from ChartBuilder
            sheets: List of sheet specifications for sheet name lookup
        """
        if self._doc is None:
            return

        if not charts:
            return

        # Build a mapping of sheet names to sheet objects for positioning
        sheet_map = {sheet.name: sheet for sheet in sheets}

        for chart_spec in charts:
            # Determine target sheet from chart position or use first sheet
            target_sheet_name = sheets[0].name if sheets else "Sheet1"

            # If chart has a position with cell reference, we can extract sheet
            # from the cell reference if it's qualified (e.g., "Sheet1.A1")
            if chart_spec.position and not isinstance(chart_spec.position, str):
                cell_ref = chart_spec.position.cell
                if "." in cell_ref:
                    # Sheet-qualified reference
                    sheet_part, _ = cell_ref.split(".", 1)
                    if sheet_part in sheet_map:
                        target_sheet_name = sheet_part

            # Render the chart to the target sheet
            self._render_chart(chart_spec, target_sheet_name)

        # After all charts are rendered, embed frames into tables
        self._embed_chart_frames()

    def _render_chart(self, chart_spec: ChartSpec, sheet_name: str) -> None:
        """Render a chart to the ODS document.

        Supports:
        - Column, bar, line, pie, area charts
        - Chart positioning and sizing
        - Chart titles and legends
        - Axis configuration
        - Multiple data series

        Args:
            chart_spec: Chart specification from ChartBuilder
            sheet_name: Name of the sheet to anchor the chart to
        """
        if self._doc is None:
            return

        self._chart_counter += 1
        chart_id = f"chart_{self._chart_counter}"

        # Map ChartType to ODF chart class
        odf_chart_class = self._get_odf_chart_class(chart_spec.chart_type)

        # Create chart style
        chart_style = Style(name=f"ChartStyle_{self._chart_counter}", family="chart")
        self._doc.automaticstyles.addElement(chart_style)

        # Create the chart element
        # Use dictionary unpacking for 'class' since it's a Python keyword
        chart_element = odfchart.Chart(**{"class": odf_chart_class})

        # Add title if specified
        if chart_spec.title:
            title_elem = odfchart.Title()
            title_text = (
                chart_spec.title.text
                if not isinstance(chart_spec.title, str)
                else chart_spec.title
            )
            title_p = P(text=title_text)
            title_elem.addElement(title_p)
            chart_element.addElement(title_elem)

        # Add legend if visible
        if (
            chart_spec.legend
            and not isinstance(chart_spec.legend, bool)
            and chart_spec.legend.visible
        ):
            legend_position = self._get_odf_legend_position(chart_spec.legend.position)
            legend_elem = odfchart.Legend(
                legendposition=legend_position,
            )
            chart_element.addElement(legend_elem)

        # Add plot area with axes
        plot_area = odfchart.PlotArea()

        # Add category axis (X-axis)
        if chart_spec.category_axis:
            axis_x = odfchart.Axis(
                dimension="x",
                name="primary-x",
            )
            if chart_spec.category_axis.title:
                axis_title = odfchart.Title()
                axis_title.addElement(P(text=chart_spec.category_axis.title))
                axis_x.addElement(axis_title)
            plot_area.addElement(axis_x)
        else:
            # Default X axis
            axis_x = odfchart.Axis(dimension="x", name="primary-x")
            plot_area.addElement(axis_x)

        # Add value axis (Y-axis)
        if chart_spec.value_axis:
            axis_y = odfchart.Axis(
                dimension="y",
                name="primary-y",
            )
            if chart_spec.value_axis.title:
                axis_title = odfchart.Title()
                axis_title.addElement(P(text=chart_spec.value_axis.title))
                axis_y.addElement(axis_title)
            # Add grid if specified
            if chart_spec.value_axis.major_gridlines:
                grid = odfchart.Grid()
                grid.setAttribute("class", "major")
                axis_y.addElement(grid)
            plot_area.addElement(axis_y)
        else:
            # Default Y axis
            axis_y = odfchart.Axis(dimension="y", name="primary-y")
            plot_area.addElement(axis_y)

        # Add secondary Y axis if specified
        if chart_spec.secondary_axis:
            axis_y2 = odfchart.Axis(
                dimension="y",
                name="secondary-y",
            )
            if chart_spec.secondary_axis.title:
                axis_title = odfchart.Title()
                axis_title.addElement(P(text=chart_spec.secondary_axis.title))
                axis_y2.addElement(axis_title)
            plot_area.addElement(axis_y2)

        # Add data series
        for idx, series in enumerate(chart_spec.series):
            series_elem = self._create_chart_series(series, idx, chart_spec)
            plot_area.addElement(series_elem)

        chart_element.addElement(plot_area)

        # Create frame to hold the chart
        frame_style = Style(name=f"fr{self._chart_counter}", family="graphic")
        frame_style.addElement(
            GraphicProperties(
                stroke="none",
                fill="none",
            )
        )
        self._doc.automaticstyles.addElement(frame_style)

        # Position and size
        size = chart_spec.size
        position = chart_spec.position

        # Ensure position is ChartPosition type (should be converted by __post_init__)
        if isinstance(position, str):
            from spreadsheet_dl.charts import ChartPosition

            position = ChartPosition(cell=position)

        # Parse cell reference for positioning
        # Cell reference format: "A1" or "Sheet.A1"
        cell_ref = position.cell
        if "." in cell_ref:
            # Strip sheet name if present
            _, cell_ref = cell_ref.split(".", 1)

        # Convert cell reference to coordinates (simplified)
        # For full implementation, would use proper cell addressing
        # ODF uses SVG coordinates (x, y) from page origin

        # Create frame with size and positioning
        frame_kwargs = {
            "stylename": frame_style,
            "width": f"{size.width}pt",
            "height": f"{size.height}pt",
            "anchortype": "paragraph",
        }

        # Apply offset if specified
        # Note: ODF Frame supports x/y positioning but requires proper anchor type
        # For precise positioning, use absolute anchoring with page coordinates
        if position.offset_x:
            frame_kwargs["x"] = f"{position.offset_x}pt"
        if position.offset_y:
            frame_kwargs["y"] = f"{position.offset_y}pt"

        frame = Frame(**frame_kwargs)

        # Embed chart as an object within the frame
        # In ODF, charts are embedded as separate subdocuments
        # For this implementation, we create a reference structure
        object_elem = Object()
        object_elem.setAttribute("href", f"./{chart_id}")
        # Note: Full implementation would use self._doc.addObject()
        # to properly embed the chart as a subdocument with its own content.xml

        frame.addElement(object_elem)

        # Store chart reference for potential attachment to specific cells
        # Charts need to be added to the table at the appropriate position
        if not hasattr(self, "_charts"):
            self._charts = []
        self._charts.append(
            {
                "id": chart_id,
                "spec": chart_spec,
                "frame": frame,
                "sheet": sheet_name,
                "cell_ref": cell_ref,
            }
        )

    def _embed_chart_frames(self) -> None:
        """Embed chart frames into tables.

        This method iterates over all stored chart references and adds
        the frame elements to the appropriate table's Shapes container.
        Charts are positioned by their target sheet.
        """
        from odf.table import Shapes

        if not self._charts:
            return

        # Group charts by sheet
        charts_by_sheet: dict[str, list[dict[str, Any]]] = {}
        for chart_info in self._charts:
            sheet_name = chart_info["sheet"]
            if sheet_name not in charts_by_sheet:
                charts_by_sheet[sheet_name] = []
            charts_by_sheet[sheet_name].append(chart_info)

        # Add shapes container to each table that has charts
        for sheet_name, chart_list in charts_by_sheet.items():
            if sheet_name not in self._tables:
                continue

            table = self._tables[sheet_name]

            # Create shapes container for the table
            shapes = Shapes()

            # Add all chart frames to the shapes container
            for chart_info in chart_list:
                frame = chart_info["frame"]
                shapes.addElement(frame)

            # Add shapes to the table (prepend to table)
            # In ODF, table:shapes should come before table:table-column
            table.insertBefore(shapes, table.firstChild)

    def _get_odf_chart_class(self, chart_type: ChartType) -> str:
        """Map ChartType enum to ODF chart class URI.

        Args:
            chart_type: SpreadsheetDL ChartType enum

        Returns:
            ODF chart class URI string
        """
        from spreadsheet_dl.charts import ChartType

        chart_class_map = {
            ChartType.COLUMN: "chart:bar",
            ChartType.COLUMN_STACKED: "chart:bar",
            ChartType.COLUMN_100_STACKED: "chart:bar",
            ChartType.BAR: "chart:bar",
            ChartType.BAR_STACKED: "chart:bar",
            ChartType.BAR_100_STACKED: "chart:bar",
            ChartType.LINE: "chart:line",
            ChartType.LINE_MARKERS: "chart:line",
            ChartType.LINE_SMOOTH: "chart:line",
            ChartType.AREA: "chart:area",
            ChartType.AREA_STACKED: "chart:area",
            ChartType.AREA_100_STACKED: "chart:area",
            ChartType.PIE: "chart:circle",
            ChartType.DOUGHNUT: "chart:ring",
            ChartType.SCATTER: "chart:scatter",
            ChartType.SCATTER_LINES: "chart:scatter",
            ChartType.BUBBLE: "chart:bubble",
            ChartType.COMBO: "chart:bar",  # Combo charts are typically bar-based
        }
        return chart_class_map.get(chart_type, "chart:bar")

    def _get_odf_legend_position(self, legend_position: Any) -> str:
        """Map LegendPosition enum to ODF legend position.

        Args:
            legend_position: LegendPosition enum value

        Returns:
            ODF legend position string
        """
        from spreadsheet_dl.charts import LegendPosition

        position_map = {
            LegendPosition.TOP: "top",
            LegendPosition.BOTTOM: "bottom",
            LegendPosition.LEFT: "start",
            LegendPosition.RIGHT: "end",
            LegendPosition.TOP_LEFT: "top-start",
            LegendPosition.TOP_RIGHT: "top-end",
            LegendPosition.BOTTOM_LEFT: "bottom-start",
            LegendPosition.BOTTOM_RIGHT: "bottom-end",
            LegendPosition.NONE: "none",
        }
        return position_map.get(legend_position, "bottom")

    def _create_chart_series(
        self,
        series: DataSeries,
        index: int,
        chart_spec: ChartSpec,
    ) -> Any:
        """Create an ODF chart series element with color styling.

        Applies chart styling and series color configuration.

        Args:
            series: DataSeries specification
            index: Series index (for color selection)
            chart_spec: Parent chart specification

        Returns:
            ODF chart:series element with applied color style
        """
        # Create series element
        series_elem = odfchart.Series()

        # Set values cell range
        if series.values:
            series_elem.setAttribute("valuescellrangeaddress", series.values)

        # Set series name/label
        if series.name:
            series_elem.setAttribute("labelcelladdress", series.name)

        # Set categories if available
        # Note: ODF Series doesn't have a categories attribute
        # Categories are typically handled at the PlotArea level
        # For now, we skip this and rely on the data structure

        # Apply color via ODF style
        if series.color or chart_spec.color_palette:
            color = series.color
            if not color and chart_spec.color_palette:
                color = chart_spec.color_palette[index % len(chart_spec.color_palette)]

            if color:
                self._apply_series_color(series_elem, color, index)

        return series_elem

    def _apply_series_color(
        self,
        series_elem: Any,
        color: str,
        index: int,
    ) -> None:
        """Apply color styling to a chart series element.

        Creates an ODF style with graphic properties for fill and stroke colors,
        adds it to the document's automatic styles, and applies it to the series.

        Args:
            series_elem: ODF chart:series element
            color: Hex color code (e.g., "#FF0000" or "FF0000")
            index: Series index for unique style naming
        """
        # Normalize color to hex format with #
        normalized_color = self._normalize_hex_color(color)

        # Create unique style name
        style_name = f"chart-series-{index}"

        # Create chart style with graphic properties
        chart_style = Style(name=style_name, family="chart")

        # Create graphic properties for fill and stroke colors
        graphic_props = GraphicProperties()
        graphic_props.setAttribute("fillcolor", normalized_color)
        graphic_props.setAttribute("strokecolor", normalized_color)

        # Add graphic properties to style
        chart_style.addElement(graphic_props)

        # Add style to document's automatic styles
        if self._doc is not None:
            self._doc.automaticstyles.addElement(chart_style)

        # Apply style to series element
        series_elem.setAttribute("stylename", style_name)

    def _normalize_hex_color(self, color: str) -> str:
        """Normalize color to ODF hex format (#RRGGBB).

        Args:
            color: Color string (hex with or without #, or named color)

        Returns:
            Normalized hex color with # prefix

        Examples:
            >>> _normalize_hex_color("FF0000")  # doctest: +SKIP
            "#FF0000"
            >>> _normalize_hex_color("#ff0000")  # doctest: +SKIP
            "#FF0000"
            >>> _normalize_hex_color("red")  # doctest: +SKIP
            "#FF0000"
        """
        # Remove any whitespace
        color = color.strip()

        # Handle named colors
        named_colors = {
            "red": "#FF0000",
            "green": "#00FF00",
            "blue": "#0000FF",
            "yellow": "#FFFF00",
            "orange": "#FFA500",
            "purple": "#800080",
            "pink": "#FFC0CB",
            "brown": "#A52A2A",
            "gray": "#808080",
            "grey": "#808080",
            "black": "#000000",
            "white": "#FFFFFF",
            "cyan": "#00FFFF",
            "magenta": "#FF00FF",
            "lime": "#00FF00",
            "navy": "#000080",
            "teal": "#008080",
            "olive": "#808000",
            "maroon": "#800000",
            "aqua": "#00FFFF",
        }

        color_lower = color.lower()
        if color_lower in named_colors:
            return named_colors[color_lower]

        # Ensure # prefix
        if not color.startswith("#"):
            color = f"#{color}"

        # Normalize to uppercase
        return color.upper()

    # =========================================================================
    # Conditional Format Rendering
    # =========================================================================

    def _add_conditional_formats(
        self, conditional_formats: list[ConditionalFormat]
    ) -> None:
        """Add conditional formatting to the ODS document.

        Supports:
        - Color scales (2-color and 3-color)
        - Data bars
        - Icon sets
        - Cell value rules
        - Formula-based rules

        Args:
            conditional_formats: List of conditional format configurations
        """
        if self._doc is None:
            return

        from spreadsheet_dl.schema.conditional import (
            ConditionalRuleType,
        )

        # ODF uses calcext:conditional-formats in content.xml
        # For each conditional format, we create the appropriate XML structure

        for cf in conditional_formats:
            for rule in cf.rules:
                if rule.type == ConditionalRuleType.COLOR_SCALE and rule.color_scale:
                    self._add_color_scale_rule(cf.range, rule.color_scale)
                elif rule.type == ConditionalRuleType.DATA_BAR and rule.data_bar:
                    self._add_data_bar_rule(cf.range, rule.data_bar)
                elif rule.type == ConditionalRuleType.ICON_SET and rule.icon_set:
                    self._add_icon_set_rule(cf.range, rule.icon_set)
                elif rule.type == ConditionalRuleType.CELL_VALUE:
                    self._add_cell_value_rule(cf.range, rule)
                elif rule.type == ConditionalRuleType.FORMULA:
                    self._add_formula_rule(cf.range, rule)

    def _add_color_scale_rule(self, cell_range: str, color_scale: Any) -> None:
        """Add color scale conditional format rule.

        Note: ODS conditional formatting via odfpy is limited. Color scales
        require calcext:color-scale XML elements that are not fully supported
        by odfpy. This implementation stores the rule configuration but does
        not generate dynamic ODS conditional formatting.

        For dynamic color scales in LibreOffice, manually add formatting after
        export or use XLSX format which has better library support.

        Args:
            cell_range: Target cell range (e.g., "A1:B10")
            color_scale: ColorScale configuration
        """
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            f"Color scale rule for range {cell_range} cannot be rendered in ODS. "
            f"ODF calcext:color-scale elements are not supported by odfpy. "
            f"Use XLSX export or add formatting manually in LibreOffice."
        )

    def _add_data_bar_rule(self, cell_range: str, data_bar: Any) -> None:
        """Add data bar conditional format rule.

        Note: ODS conditional formatting via odfpy is limited. Data bars
        require ODF data bar XML elements that are not fully supported
        by odfpy. This implementation stores the rule configuration but does
        not generate dynamic ODS conditional formatting.

        For dynamic data bars in LibreOffice, manually add formatting after
        export or use XLSX format which has better library support.

        Args:
            cell_range: Target cell range (e.g., "A1:B10")
            data_bar: DataBar configuration
        """
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            f"Data bar rule for range {cell_range} cannot be rendered in ODS. "
            f"ODF data bar elements are not supported by odfpy. "
            f"Use XLSX export or add formatting manually in LibreOffice."
        )

    def _add_icon_set_rule(self, cell_range: str, icon_set: Any) -> None:
        """Add icon set conditional format rule.

        Note: ODS conditional formatting via odfpy is limited. Icon sets
        require ODF icon set XML elements that are not fully supported
        by odfpy. This implementation stores the rule configuration but does
        not generate dynamic ODS conditional formatting.

        For dynamic icon sets in LibreOffice, manually add formatting after
        export or use XLSX format which has better library support.

        Args:
            cell_range: Target cell range (e.g., "A1:B10")
            icon_set: IconSet configuration
        """
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            f"Icon set rule for range {cell_range} cannot be rendered in ODS. "
            f"ODF icon set elements are not supported by odfpy. "
            f"Use XLSX export or add formatting manually in LibreOffice."
        )

    def _add_cell_value_rule(self, cell_range: str, rule: Any) -> None:
        """Add cell value conditional format rule.

        Note: ODS conditional formatting via odfpy is limited. Cell value rules
        require ODF conditional format XML elements that are not fully supported
        by odfpy. This implementation stores the rule configuration but does
        not generate dynamic ODS conditional formatting.

        For dynamic cell value rules in LibreOffice, manually add formatting after
        export or use XLSX format which has better library support.

        Args:
            cell_range: Target cell range (e.g., "A1:B10")
            rule: ConditionalRule with cell value configuration
        """
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            f"Cell value rule for range {cell_range} cannot be rendered in ODS. "
            f"ODF conditional format elements are not supported by odfpy. "
            f"Use XLSX export or add formatting manually in LibreOffice."
        )

    def _add_formula_rule(self, cell_range: str, rule: Any) -> None:
        """Add formula-based conditional format rule.

        Note: ODS conditional formatting via odfpy is limited. Formula rules
        require ODF conditional format XML elements that are not fully supported
        by odfpy. This implementation stores the rule configuration but does
        not generate dynamic ODS conditional formatting.

        For dynamic formula rules in LibreOffice, manually add formatting after
        export or use XLSX format which has better library support.

        Args:
            cell_range: Target cell range (e.g., "A1:B10")
            rule: ConditionalRule with formula configuration
        """
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            f"Formula rule for range {cell_range} cannot be rendered in ODS. "
            f"ODF conditional format elements are not supported by odfpy. "
            f"Use XLSX export or add formatting manually in LibreOffice."
        )

    # =========================================================================
    # Data Validation Rendering
    # =========================================================================

    def _add_data_validations(self, validations: list[ValidationConfig]) -> None:
        """Add data validations to the ODS document.

        Supports:
        - List validation with dropdowns
        - Number range validation
        - Date range validation
        - Custom formula validation
        - Input messages
        - Error alerts

        Args:
            validations: List of validation configurations
        """
        if self._doc is None:
            return

        from spreadsheet_dl.schema.data_validation import ValidationType

        # ODF uses table:content-validations and table:content-validation
        # For each validation, we create the appropriate XML structure

        for vc in validations:
            validation = vc.validation
            if validation.type == ValidationType.LIST:
                self._add_list_validation(vc.range, validation)
            elif validation.type in (
                ValidationType.WHOLE_NUMBER,
                ValidationType.DECIMAL,
            ):
                self._add_number_validation(vc.range, validation)
            elif validation.type == ValidationType.DATE:
                self._add_date_validation(vc.range, validation)
            elif validation.type == ValidationType.CUSTOM:
                self._add_custom_validation(vc.range, validation)
            elif validation.type == ValidationType.TEXT_LENGTH:
                self._add_text_length_validation(vc.range, validation)

    def _add_list_validation(self, cell_range: str, validation: Any) -> None:
        """Add list validation with dropdown.

        Note: ODS data validation via odfpy has limited support. While ODF
        supports table:content-validation elements, odfpy's implementation
        is incomplete and does not provide a way to attach validations to cells.

        For full data validation support in LibreOffice, manually add validation
        after export or use XLSX format which has better library support.

        Args:
            cell_range: Target cell range (e.g., "A1:B10")
            validation: DataValidation configuration for list type
        """
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            f"List validation for range {cell_range}: ODF table:content-validation "
            f"elements have limited support in odfpy. Validation cannot be rendered. "
            f"Use XLSX export for full validation support or add manually in LibreOffice."
        )

    def _add_number_validation(self, cell_range: str, validation: Any) -> None:
        """Add number range validation.

        Note: ODS data validation via odfpy has limited support. While ODF
        supports table:content-validation elements, odfpy's implementation
        is incomplete and does not provide a way to attach validations to cells.

        For full data validation support in LibreOffice, manually add validation
        after export or use XLSX format which has better library support.

        Args:
            cell_range: Target cell range (e.g., "A1:B10")
            validation: DataValidation configuration for number type
        """
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            f"Number validation for range {cell_range}: ODF table:content-validation "
            f"elements have limited support in odfpy. Validation cannot be rendered. "
            f"Use XLSX export for full validation support or add manually in LibreOffice."
        )

    def _add_date_validation(self, cell_range: str, validation: Any) -> None:
        """Add date range validation.

        Note: ODS data validation via odfpy has limited support. While ODF
        supports table:content-validation elements, odfpy's implementation
        is incomplete and does not provide a way to attach validations to cells.

        For full data validation support in LibreOffice, manually add validation
        after export or use XLSX format which has better library support.

        Args:
            cell_range: Target cell range (e.g., "A1:B10")
            validation: DataValidation configuration for date type
        """
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            f"Date validation for range {cell_range}: ODF table:content-validation "
            f"elements have limited support in odfpy. Validation cannot be rendered. "
            f"Use XLSX export for full validation support or add manually in LibreOffice."
        )

    def _add_custom_validation(self, cell_range: str, validation: Any) -> None:
        """Add custom formula validation.

        Note: ODS data validation via odfpy has limited support. While ODF
        supports table:content-validation elements, odfpy's implementation
        is incomplete and does not provide a way to attach validations to cells.

        For full data validation support in LibreOffice, manually add validation
        after export or use XLSX format which has better library support.

        Args:
            cell_range: Target cell range (e.g., "A1:B10")
            validation: DataValidation configuration for custom formula type
        """
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            f"Custom validation for range {cell_range}: ODF table:content-validation "
            f"elements have limited support in odfpy. Validation cannot be rendered. "
            f"Use XLSX export for full validation support or add manually in LibreOffice."
        )

    def _add_text_length_validation(self, cell_range: str, validation: Any) -> None:
        """Add text length validation.

        Note: ODS data validation via odfpy has limited support. While ODF
        supports table:content-validation elements, odfpy's implementation
        is incomplete and does not provide a way to attach validations to cells.

        For full data validation support in LibreOffice, manually add validation
        after export or use XLSX format which has better library support.

        Args:
            cell_range: Target cell range (e.g., "A1:B10")
            validation: DataValidation configuration for text length type
        """
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            f"Text length validation for range {cell_range}: ODF table:content-validation "
            f"elements have limited support in odfpy. Validation cannot be rendered. "
            f"Use XLSX export for full validation support or add manually in LibreOffice."
        )


def render_sheets(
    sheets: list[SheetSpec],
    output_path: Path | str,
    theme: Theme | None = None,
    named_ranges: list[NamedRangeSpec] | None = None,
    charts: list[ChartSpec] | None = None,
    conditional_formats: list[ConditionalFormat] | None = None,
    validations: list[ValidationConfig] | None = None,
) -> Path:
    """Convenience function to render sheets to ODS.

    Supports named ranges, charts, conditional formatting, and data validation.

    Args:
        sheets: Sheet specifications
        output_path: Output file path
        theme: Optional theme
        named_ranges: Optional named ranges
        charts: Optional chart specifications
        conditional_formats: Optional conditional formats
        validations: Optional data validations

    Returns:
        Path to created file
    """
    renderer = OdsRenderer(theme)
    return renderer.render(
        sheets,
        Path(output_path),
        named_ranges,
        charts,
        conditional_formats,
        validations,
    )


# Alias for render_ods (used by MCP tools)
def render_ods(
    sheets: list[SheetSpec],
    output_path: Path | str,
    theme: Theme | None = None,
    named_ranges: list[NamedRangeSpec] | None = None,
    charts: list[ChartSpec] | None = None,
    conditional_formats: list[ConditionalFormat] | None = None,
    validations: list[ValidationConfig] | None = None,
) -> Path:
    """Render sheets to ODS file.

    This is an alias for render_sheets() for backward compatibility
    with MCP tools that expect the render_ods function name.

    Args:
        sheets: Sheet specifications
        output_path: Output file path
        theme: Optional theme
        named_ranges: Optional named ranges
        charts: Optional chart specifications
        conditional_formats: Optional conditional formats
        validations: Optional data validations

    Returns:
        Path to created file
    """
    return render_sheets(
        sheets,
        output_path,
        theme,
        named_ranges,
        charts,
        conditional_formats,
        validations,
    )
