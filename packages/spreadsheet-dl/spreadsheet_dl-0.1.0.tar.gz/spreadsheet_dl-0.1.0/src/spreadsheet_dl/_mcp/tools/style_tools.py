"""Style and formatting operation tools.

Provides MCP tools for:
- Style operations (list, get, create, update, delete, apply)
- Cell formatting (cells, number, font, fill, border)
- Theme management (list, get, create, update, delete, apply, preview)
- Color scheme generation
- Font set application
- Style guide creation

Note: Many style operations are not yet implemented in OdsEditor.
These tools return appropriate error messages indicating unavailable functionality.
"""

from __future__ import annotations

from typing import Any

from spreadsheet_dl._mcp.models import MCPToolParameter, MCPToolResult


def register_style_tools(
    registry: Any,
    validate_path: Any,
) -> None:
    """Register all style and formatting tools.

    Args:
        registry: MCPToolRegistry instance
        validate_path: Path validation function
    """
    _register_style_operations(registry, validate_path)
    _register_format_operations(registry, validate_path)
    _register_theme_operations(registry, validate_path)


def _register_style_operations(registry: Any, validate_path: Any) -> None:
    """Register style operation tools."""
    # style_list
    registry.register(
        name="style_list",
        description="List all available styles in the workbook",
        handler=_make_style_list_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
        ],
        category="style_operations",
    )

    # style_get
    registry.register(
        name="style_get",
        description="Get details of a specific style",
        handler=_make_style_get_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="style_name",
                type="string",
                description="Name of the style to retrieve",
            ),
        ],
        category="style_operations",
    )

    # style_create
    registry.register(
        name="style_create",
        description="Create a new style",
        handler=_make_style_create_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="style_name",
                type="string",
                description="Name for the new style",
            ),
            MCPToolParameter(
                name="properties",
                type="string",
                description="JSON object with style properties",
            ),
        ],
        category="style_operations",
    )

    # style_update
    registry.register(
        name="style_update",
        description="Update an existing style",
        handler=_make_style_update_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="style_name",
                type="string",
                description="Name of the style to update",
            ),
            MCPToolParameter(
                name="properties",
                type="string",
                description="JSON object with updated properties",
            ),
        ],
        category="style_operations",
    )

    # style_delete
    registry.register(
        name="style_delete",
        description="Delete a style",
        handler=_make_style_delete_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="style_name",
                type="string",
                description="Name of the style to delete",
            ),
        ],
        category="style_operations",
    )

    # style_apply
    registry.register(
        name="style_apply",
        description="Apply a style to a cell or range",
        handler=_make_style_apply_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet name",
            ),
            MCPToolParameter(
                name="range",
                type="string",
                description="Cell or range reference",
            ),
            MCPToolParameter(
                name="style_name",
                type="string",
                description="Name of the style to apply",
            ),
        ],
        category="style_operations",
    )


def _register_format_operations(registry: Any, validate_path: Any) -> None:
    """Register cell formatting tools."""
    # format_cells
    registry.register(
        name="format_cells",
        description="Apply formatting to cells",
        handler=_make_format_cells_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet name",
            ),
            MCPToolParameter(
                name="range",
                type="string",
                description="Cell or range reference",
            ),
            MCPToolParameter(
                name="format",
                type="string",
                description="JSON object with formatting options",
            ),
        ],
        category="style_operations",
    )

    # format_number
    registry.register(
        name="format_number",
        description="Apply number format to cells",
        handler=_make_format_number_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet name",
            ),
            MCPToolParameter(
                name="range",
                type="string",
                description="Cell or range reference",
            ),
            MCPToolParameter(
                name="format_code",
                type="string",
                description="Number format code (e.g., '#,##0.00', '0%')",
            ),
        ],
        category="style_operations",
    )

    # format_font
    registry.register(
        name="format_font",
        description="Apply font formatting to cells",
        handler=_make_format_font_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet name",
            ),
            MCPToolParameter(
                name="range",
                type="string",
                description="Cell or range reference",
            ),
            MCPToolParameter(
                name="font",
                type="string",
                description="JSON with font properties (name, size, bold, italic, color)",
            ),
        ],
        category="style_operations",
    )

    # format_fill
    registry.register(
        name="format_fill",
        description="Apply fill/background color to cells",
        handler=_make_format_fill_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet name",
            ),
            MCPToolParameter(
                name="range",
                type="string",
                description="Cell or range reference",
            ),
            MCPToolParameter(
                name="color",
                type="string",
                description="Fill color (hex code like '#FF0000' or name like 'red')",
            ),
        ],
        category="style_operations",
    )

    # format_border
    registry.register(
        name="format_border",
        description="Apply border formatting to cells",
        handler=_make_format_border_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet name",
            ),
            MCPToolParameter(
                name="range",
                type="string",
                description="Cell or range reference",
            ),
            MCPToolParameter(
                name="border",
                type="string",
                description="JSON with border properties (style, color, sides)",
            ),
        ],
        category="style_operations",
    )


def _register_theme_operations(registry: Any, validate_path: Any) -> None:
    """Register theme management tools."""
    # theme_list
    registry.register(
        name="theme_list",
        description="List all available themes",
        handler=_make_theme_list_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
        ],
        category="theme_management",
    )

    # theme_get
    registry.register(
        name="theme_get",
        description="Get details of a specific theme",
        handler=_make_theme_get_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="theme_name",
                type="string",
                description="Name of the theme",
            ),
        ],
        category="theme_management",
    )

    # theme_create
    registry.register(
        name="theme_create",
        description="Create a new theme",
        handler=_make_theme_create_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="theme_name",
                type="string",
                description="Name for the new theme",
            ),
            MCPToolParameter(
                name="properties",
                type="string",
                description="JSON object with theme properties",
            ),
        ],
        category="theme_management",
    )

    # theme_apply
    registry.register(
        name="theme_apply",
        description="Apply a theme to the workbook",
        handler=_make_theme_apply_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="theme_name",
                type="string",
                description="Name of the theme to apply",
            ),
        ],
        category="theme_management",
    )

    # color_scheme_generate
    registry.register(
        name="color_scheme_generate",
        description="Generate a color scheme from a base color",
        handler=_make_color_scheme_generate_handler(),
        parameters=[
            MCPToolParameter(
                name="base_color",
                type="string",
                description="Base color (hex code like '#3366CC')",
            ),
            MCPToolParameter(
                name="scheme_type",
                type="string",
                description="Type of scheme: analogous, complementary, triadic, etc.",
                required=False,
            ),
        ],
        category="theme_management",
    )


# =============================================================================
# Handler Factory Functions - Style Operations
# =============================================================================


def _make_style_list_handler(validate_path: Any) -> Any:
    """Create style_list handler."""

    def handler(file_path: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have list_styles method
            # Return empty list with info message
            return MCPToolResult.json(
                {
                    "styles": [],
                    "info": "Style listing not yet implemented for ODS files. "
                    "Use SpreadsheetBuilder with themes for style management.",
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_style_get_handler(validate_path: Any) -> Any:
    """Create style_get handler."""

    def handler(file_path: str, style_name: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have get_style method
            return MCPToolResult.error(
                f"Style '{style_name}' retrieval not yet implemented for ODS files. "
                "Use SpreadsheetBuilder with themes for style management."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_style_create_handler(validate_path: Any) -> Any:
    """Create style_create handler."""

    def handler(file_path: str, style_name: str, properties: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have create_style method
            return MCPToolResult.error(
                "Style creation not yet implemented for ODS files. "
                "Use SpreadsheetBuilder with themes for style management."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_style_update_handler(validate_path: Any) -> Any:
    """Create style_update handler."""

    def handler(file_path: str, style_name: str, properties: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have update_style method
            return MCPToolResult.error(
                "Style update not yet implemented for ODS files. "
                "Use SpreadsheetBuilder with themes for style management."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_style_delete_handler(validate_path: Any) -> Any:
    """Create style_delete handler."""

    def handler(file_path: str, style_name: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have delete_style method
            return MCPToolResult.error(
                "Style deletion not yet implemented for ODS files. "
                "Use SpreadsheetBuilder with themes for style management."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_style_apply_handler(validate_path: Any) -> Any:
    """Create style_apply handler."""

    def handler(
        file_path: str, sheet: str, range: str, style_name: str
    ) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have apply_style method
            return MCPToolResult.error(
                "Style application not yet implemented for ODS files. "
                "Use SpreadsheetBuilder with themes for style management."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


# =============================================================================
# Handler Factory Functions - Format Operations
# =============================================================================


def _make_format_cells_handler(validate_path: Any) -> Any:
    """Create format_cells handler."""

    def handler(file_path: str, sheet: str, range: str, format: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have format_cells method
            return MCPToolResult.error(
                "Cell formatting not yet implemented for ODS files. "
                "Use SpreadsheetBuilder with themes for cell formatting."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_format_number_handler(validate_path: Any) -> Any:
    """Create format_number handler."""

    def handler(
        file_path: str, sheet: str, range: str, format_code: str
    ) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have set_number_format method
            return MCPToolResult.error(
                "Number format not yet implemented for ODS files. "
                "Use SpreadsheetBuilder with themes for number formatting."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_format_font_handler(validate_path: Any) -> Any:
    """Create format_font handler."""

    def handler(file_path: str, sheet: str, range: str, font: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have set_font method
            return MCPToolResult.error(
                "Font formatting not yet implemented for ODS files. "
                "Use SpreadsheetBuilder with themes for font formatting."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_format_fill_handler(validate_path: Any) -> Any:
    """Create format_fill handler."""

    def handler(file_path: str, sheet: str, range: str, color: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have set_fill_color method
            return MCPToolResult.error(
                "Fill color not yet implemented for ODS files. "
                "Use SpreadsheetBuilder with themes for fill colors."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_format_border_handler(validate_path: Any) -> Any:
    """Create format_border handler."""

    def handler(file_path: str, sheet: str, range: str, border: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have set_border method
            return MCPToolResult.error(
                "Border formatting not yet implemented for ODS files. "
                "Use SpreadsheetBuilder with themes for borders."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


# =============================================================================
# Handler Factory Functions - Theme Operations
# =============================================================================


def _make_theme_list_handler(validate_path: Any) -> Any:
    """Create theme_list handler."""

    def handler(file_path: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have list_themes method
            # Return empty list with info
            return MCPToolResult.json(
                {
                    "themes": [],
                    "info": "Theme listing not yet implemented for ODS files. "
                    "Use SpreadsheetBuilder with themes for theme management.",
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_theme_get_handler(validate_path: Any) -> Any:
    """Create theme_get handler."""

    def handler(file_path: str, theme_name: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have get_theme method
            return MCPToolResult.error(
                f"Theme '{theme_name}' retrieval not yet implemented for ODS files. "
                "Use SpreadsheetBuilder with themes for theme management."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_theme_create_handler(validate_path: Any) -> Any:
    """Create theme_create handler."""

    def handler(file_path: str, theme_name: str, properties: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have create_theme method
            return MCPToolResult.error(
                "Theme creation not yet implemented for ODS files. "
                "Use SpreadsheetBuilder with themes for theme management."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_theme_apply_handler(validate_path: Any) -> Any:
    """Create theme_apply handler."""

    def handler(file_path: str, theme_name: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have apply_theme method
            return MCPToolResult.error(
                "Theme application not yet implemented for ODS files. "
                "Use SpreadsheetBuilder with themes for theme management."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_color_scheme_generate_handler() -> Any:
    """Create color_scheme_generate handler."""

    def handler(base_color: str, scheme_type: str = "monochromatic") -> MCPToolResult:
        try:
            from spreadsheet_dl.schema.styles import Color

            base = Color.from_hex(base_color)

            # Generate color scheme based on type using available Color methods
            if scheme_type == "monochromatic":
                # Create shades and tints of the base color
                colors = [
                    base.darken(0.4),
                    base.darken(0.2),
                    base,
                    base.lighten(0.2),
                    base.lighten(0.4),
                ]
            elif scheme_type == "complementary":
                # Invert creates an approximate complementary color
                colors = [base, base.invert()]
            elif scheme_type == "analogous":
                # Create analogous by adjusting hue slightly via saturation/lightness
                h, s, lightness = base.to_hsl()
                colors = [
                    Color.from_hsl((h - 30) % 360, s, lightness),
                    Color.from_hsl((h - 15) % 360, s, lightness),
                    base,
                    Color.from_hsl((h + 15) % 360, s, lightness),
                    Color.from_hsl((h + 30) % 360, s, lightness),
                ]
            elif scheme_type == "triadic":
                h, s, lightness = base.to_hsl()
                colors = [
                    base,
                    Color.from_hsl((h + 120) % 360, s, lightness),
                    Color.from_hsl((h + 240) % 360, s, lightness),
                ]
            elif scheme_type == "split_complementary":
                h, s, lightness = base.to_hsl()
                colors = [
                    base,
                    Color.from_hsl((h + 150) % 360, s, lightness),
                    Color.from_hsl((h + 210) % 360, s, lightness),
                ]
            else:
                # Default to monochromatic
                colors = [
                    base.darken(0.3),
                    base,
                    base.lighten(0.3),
                ]

            result = [str(c) for c in colors]

            return MCPToolResult.json(
                {
                    "base_color": base_color,
                    "scheme_type": scheme_type,
                    "colors": result,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler
