"""Schema validation utilities.

    - Formula syntax validation

Provides validation functions for themes, styles, colors, and formulas
to catch configuration errors early.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.schema.styles import (
    BorderStyle,
    Color,
    FontWeight,
    StyleDefinition,
    TextAlign,
    Theme,
    VerticalAlign,
)


class SchemaValidationError(Exception):
    """Error raised when schema validation fails.

    Attributes:
        field: The field that failed validation
        message: Description of the validation failure
        value: The invalid value
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None,
    ) -> None:
        """Initialize the instance."""
        self.field = field
        self.message = message
        self.value = value
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        parts = []
        if self.field:
            parts.append(f"Field '{self.field}'")
        parts.append(self.message)
        if self.value is not None:
            parts.append(f"(got: {self.value!r})")
        return ": ".join(parts) if len(parts) > 1 else parts[0]


# Regex patterns for validation
HEX_COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")
SIZE_PATTERN = re.compile(r"^\d+(\.\d+)?(pt|px|cm|mm|in|em|%)$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def validate_color(value: str | Color, field: str = "color") -> Color:
    """Validate and return a Color object.

    Args:
        value: Color value (hex string or Color)
        field: Field name for error messages

    Returns:
        Validated Color

    Raises:
        SchemaValidationError: If color is invalid
    """
    if isinstance(value, Color):
        return value

    if not isinstance(value, str):
        raise SchemaValidationError(
            "must be a hex color string",
            field=field,
            value=value,
        )

    # Handle color references (will be resolved later)
    if value.startswith("{") and value.endswith("}"):
        # Return a placeholder - actual resolution happens in theme
        return Color("#000000")  # Placeholder

    if not HEX_COLOR_PATTERN.match(value):
        raise SchemaValidationError(
            "must be a valid hex color (e.g., #RRGGBB or #RGB)",
            field=field,
            value=value,
        )

    return Color(value)


def validate_size(value: str, field: str = "size") -> str:
    """Validate a size value (e.g., "10pt", "2.5cm").

    Args:
        value: Size string
        field: Field name for error messages

    Returns:
        Validated size string

    Raises:
        SchemaValidationError: If size is invalid
    """
    if not isinstance(value, str):
        raise SchemaValidationError(
            "must be a string",
            field=field,
            value=value,
        )

    if not SIZE_PATTERN.match(value):
        raise SchemaValidationError(
            "must be a valid size (e.g., '10pt', '2.5cm', '12px')",
            field=field,
            value=value,
        )

    return value


def validate_font_weight(
    value: str | FontWeight, field: str = "font_weight"
) -> FontWeight:
    """Validate and return a FontWeight.

    Args:
        value: Font weight value (numeric string like "700" or name like "bold")
        field: Field name for error messages

    Returns:
        Validated FontWeight

    Raises:
        SchemaValidationError: If font weight is invalid
    """
    if isinstance(value, FontWeight):
        return value

    if not isinstance(value, str):
        raise SchemaValidationError(
            "must be a string",
            field=field,
            value=value,
        )

    # First try numeric values like "700"
    try:
        return FontWeight(value)
    except ValueError:
        pass

    # Then try named values like "bold"
    try:
        return FontWeight.from_name(value)
    except (ValueError, KeyError) as e:
        valid_names = [
            "thin",
            "light",
            "normal",
            "medium",
            "semibold",
            "bold",
            "extrabold",
            "black",
        ]
        valid_values = [w.value for w in FontWeight]
        raise SchemaValidationError(
            f"must be one of: {', '.join(valid_names)} or numeric values: {', '.join(valid_values)}",
            field=field,
            value=value,
        ) from e


def validate_text_align(value: str | TextAlign, field: str = "text_align") -> TextAlign:
    """Validate and return a TextAlign.

    Args:
        value: Text alignment value
        field: Field name for error messages

    Returns:
        Validated TextAlign

    Raises:
        SchemaValidationError: If alignment is invalid
    """
    if isinstance(value, TextAlign):
        return value

    if not isinstance(value, str):
        raise SchemaValidationError(
            "must be a string",
            field=field,
            value=value,
        )
    try:
        return TextAlign(value.lower())
    except ValueError as e:
        valid = [a.value for a in TextAlign]
        raise SchemaValidationError(
            f"must be one of: {', '.join(valid)}",
            field=field,
            value=value,
        ) from e


def validate_vertical_align(
    value: str | VerticalAlign,
    field: str = "vertical_align",
) -> VerticalAlign:
    """Validate and return a VerticalAlign.

    Args:
        value: Vertical alignment value
        field: Field name for error messages

    Returns:
        Validated VerticalAlign

    Raises:
        SchemaValidationError: If alignment is invalid
    """
    if isinstance(value, VerticalAlign):
        return value

    if not isinstance(value, str):
        raise SchemaValidationError(
            "must be a string",
            field=field,
            value=value,
        )
    try:
        return VerticalAlign(value.lower())
    except ValueError as e:
        valid = [a.value for a in VerticalAlign]
        raise SchemaValidationError(
            f"must be one of: {', '.join(valid)}",
            field=field,
            value=value,
        ) from e


def validate_border_style(
    value: str | BorderStyle,
    field: str = "border_style",
) -> BorderStyle:
    """Validate and return a BorderStyle.

    Args:
        value: Border style value
        field: Field name for error messages

    Returns:
        Validated BorderStyle

    Raises:
        SchemaValidationError: If style is invalid
    """
    if isinstance(value, BorderStyle):
        return value

    if not isinstance(value, str):
        raise SchemaValidationError(
            "must be a string",
            field=field,
            value=value,
        )
    try:
        return BorderStyle(value.lower())
    except ValueError as e:
        valid = [s.value for s in BorderStyle]
        raise SchemaValidationError(
            f"must be one of: {', '.join(valid)}",
            field=field,
            value=value,
        ) from e


def validate_style(style: StyleDefinition) -> list[str]:
    """Validate a style definition.

    Args:
        style: Style definition to validate

    Returns:
        List of warning messages (empty if all valid)

    Raises:
        SchemaValidationError: If validation fails
    """
    warnings: list[str] = []

    if not style.name:
        raise SchemaValidationError("Style name is required", field="name")
    # Validate size fields
    if style.font_size:
        try:
            validate_size(style.font_size, "font_size")
        except SchemaValidationError:
            warnings.append(
                f"Style '{style.name}': Invalid font_size '{style.font_size}'"
            )

    if style.padding:
        try:
            validate_size(style.padding, "padding")
        except SchemaValidationError:
            warnings.append(f"Style '{style.name}': Invalid padding '{style.padding}'")

    return warnings


def validate_theme(theme: Theme, strict: bool = False) -> list[str]:
    """Validate a complete theme.

    Args:
        theme: Theme to validate
        strict: If True, raise on warnings

    Returns:
        List of warning messages

    Raises:
        SchemaValidationError: If validation fails (or strict mode with warnings)
    """
    warnings: list[str] = []

    # Validate metadata
    if not theme.meta.name:
        raise SchemaValidationError("Theme name is required", field="meta.name")

    if theme.meta.version and not VERSION_PATTERN.match(theme.meta.version):
        warnings.append(f"Theme version '{theme.meta.version}' is not semver format")

    # Validate base styles
    for name, style in theme.base_styles.items():
        if style.name != name:
            warnings.append(
                f"Base style key '{name}' doesn't match style.name '{style.name}'"
            )
        warnings.extend(validate_style(style))

    # Validate styles
    for name, style in theme.styles.items():
        if style.name != name:
            warnings.append(
                f"Style key '{name}' doesn't match style.name '{style.name}'"
            )
        warnings.extend(validate_style(style))

        # Check that extends references exist
        if style.extends and (
            style.extends not in theme.base_styles and style.extends not in theme.styles
        ):
            raise SchemaValidationError(
                f"Style '{name}' extends unknown style '{style.extends}'",
                field=f"styles.{name}.extends",
            )

    # Check for circular inheritance
    for name in theme.styles:
        try:
            theme.get_style(name)
        except ValueError as e:
            raise SchemaValidationError(str(e)) from e

    if strict and warnings:
        raise SchemaValidationError(f"Validation warnings: {'; '.join(warnings)}")

    return warnings


def validate_yaml_data(data: dict[str, Any]) -> list[str]:
    """Validate raw YAML data before parsing into theme.

    Args:
        data: Raw YAML data dictionary

    Returns:
        List of warning messages

    Raises:
        SchemaValidationError: If required fields are missing
    """
    warnings: list[str] = []

    # Check required sections
    if "meta" not in data:
        raise SchemaValidationError("Theme must have 'meta' section")
    meta = data["meta"]
    if not isinstance(meta, dict):
        raise SchemaValidationError("'meta' must be a dictionary")

    if "name" not in meta:
        raise SchemaValidationError("Theme meta must have 'name'")

    # Validate color references in styles
    def check_color_refs(obj: Any, path: str = "") -> None:
        """Recursively check color references."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                check_color_refs(value, new_path)
        elif isinstance(obj, str) and obj.startswith("{colors."):
            # Extract color name
            match = re.match(r"\{colors\.(\w+)\}", obj)
            if match:
                color_name = match.group(1)
                colors = data.get("colors", {})
                if color_name not in colors:
                    # Check if it's a standard color
                    standard_colors = {
                        "primary",
                        "primary_light",
                        "primary_dark",
                        "secondary",
                        "success",
                        "success_bg",
                        "warning",
                        "warning_bg",
                        "danger",
                        "danger_bg",
                        "neutral_100",
                        "neutral_200",
                        "neutral_300",
                        "neutral_800",
                        "neutral_900",
                    }
                    if color_name not in standard_colors:
                        warnings.append(
                            f"Reference to undefined color '{color_name}' at {path}"
                        )

    check_color_refs(data.get("base_styles", {}), "base_styles")
    check_color_refs(data.get("styles", {}), "styles")

    return warnings


# ============================================================================
# Formula Validation
# ============================================================================


class FormulaValidationError(Exception):
    """Error raised when formula validation fails.

    Implements Formula syntax validation

    Attributes:
        formula: The formula that failed validation
        position: Character position where error occurred (if applicable)
        message: Description of the validation failure
    """

    def __init__(
        self,
        message: str,
        formula: str | None = None,
        position: int | None = None,
    ) -> None:
        """Initialize the instance."""
        self.formula = formula
        self.position = position
        self.message = message
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        parts = [self.message]
        if self.formula:
            parts.append(f"in formula: {self.formula!r}")
        if self.position is not None:
            parts.append(f"at position {self.position}")
        return " ".join(parts)


@dataclass
class FormulaValidationResult:
    """Result of formula validation.

    Attributes:
        is_valid: Whether the formula is valid
        errors: List of validation error messages
        warnings: List of validation warnings
    """

    is_valid: bool
    errors: list[str]
    warnings: list[str]


# Known ODF/Excel function names (subset of most common ones)
KNOWN_FUNCTIONS = {
    # Mathematical
    "SUM",
    "SUMIF",
    "SUMIFS",
    "AVERAGE",
    "AVERAGEIF",
    "AVERAGEIFS",
    "COUNT",
    "COUNTA",
    "COUNTIF",
    "COUNTIFS",
    "COUNTBLANK",
    "MAX",
    "MIN",
    "ROUND",
    "ROUNDUP",
    "ROUNDDOWN",
    "ABS",
    "SQRT",
    "POWER",
    "MOD",
    "PRODUCT",
    # Financial
    "PMT",
    "PV",
    "FV",
    "NPV",
    "IRR",
    "NPER",
    "RATE",
    # Logical
    "IF",
    "IFERROR",
    "IFNA",
    "AND",
    "OR",
    "NOT",
    "ISBLANK",
    "ISERROR",
    "ISNUMBER",
    "ISTEXT",
    # Lookup
    "VLOOKUP",
    "HLOOKUP",
    "INDEX",
    "MATCH",
    "OFFSET",
    "INDIRECT",
    # Text
    "CONCATENATE",
    "CONCAT",
    "TEXT",
    "LEFT",
    "RIGHT",
    "MID",
    "LEN",
    "TRIM",
    "UPPER",
    "LOWER",
    "PROPER",
    "FIND",
    "SEARCH",
    "SUBSTITUTE",
    # Date/Time
    "TODAY",
    "NOW",
    "DATE",
    "YEAR",
    "MONTH",
    "DAY",
    "WEEKDAY",
    "WEEKNUM",
    "EOMONTH",
    "DATEDIF",
    # Statistical
    "MEDIAN",
    "STDEV",
    "STDEVP",
    "VAR",
    "PERCENTILE",
}

# Regex patterns for formula validation
CELL_REF_PATTERN = re.compile(r"\$?[A-Z]+\$?[0-9]+")
RANGE_REF_PATTERN = re.compile(r"\$?[A-Z]+\$?[0-9]+:\$?[A-Z]+\$?[0-9]+")
FUNCTION_PATTERN = re.compile(r"([A-Z]+)\s*\(")


class FormulaValidator:
    """Validates ODF formula syntax.

    Implements Formula syntax validation

    Provides validation for:
    - Parentheses matching
    - Function name validation
    - Cell reference validation
    - Basic syntax errors
    """

    def __init__(self, strict: bool = False) -> None:
        """Initialize formula validator.

        Args:
            strict: If True, treat warnings as errors
        """
        self.strict = strict

    def validate(self, formula: str) -> FormulaValidationResult:
        """Validate a formula.

        Args:
            formula: Formula string (with or without "of:=" prefix)

        Returns:
            FormulaValidationResult with validation outcome
        """
        errors: list[str] = []
        warnings: list[str] = []

        if not formula:
            errors.append("Formula is empty")
            return FormulaValidationResult(False, errors, warnings)

        # Strip ODF prefix if present
        formula_body = formula
        if formula.startswith("of:="):
            formula_body = formula[4:]
        elif formula.startswith("="):
            formula_body = formula[1:]

        # Validate parentheses
        paren_error = self._validate_parentheses(formula_body)
        if paren_error:
            errors.append(paren_error)

        # Validate function names
        func_errors, func_warnings = self._validate_functions(formula_body)
        errors.extend(func_errors)
        warnings.extend(func_warnings)

        # Validate cell references
        ref_warnings = self._validate_cell_references(formula_body)
        warnings.extend(ref_warnings)

        # Check for common mistakes
        common_errors = self._check_common_mistakes(formula_body)
        errors.extend(common_errors)

        is_valid = len(errors) == 0 and (not self.strict or len(warnings) == 0)
        return FormulaValidationResult(is_valid, errors, warnings)

    def _validate_parentheses(self, formula: str) -> str | None:
        """Validate parentheses matching.

        Args:
            formula: Formula body (without prefix)

        Returns:
            Error message if invalid, None if valid
        """
        stack: list[tuple[str, int]] = []
        in_string = False
        escape_next = False

        for i, char in enumerate(formula):
            if escape_next:
                escape_next = False
                continue

            if char == "\\":
                escape_next = True
                continue

            if char == '"':
                in_string = not in_string
                continue

            if in_string:
                continue

            if char in "([{":
                stack.append((char, i))
            elif char in ")]}":
                if not stack:
                    return f"Unmatched closing '{char}' at position {i}"
                opening, pos = stack.pop()
                pairs = {"(": ")", "[": "]", "{": "}"}
                if pairs.get(opening) != char:
                    return f"Mismatched parenthesis: '{opening}' at {pos} closed by '{char}' at {i}"

        if stack:
            opening, pos = stack[0]
            return f"Unclosed '{opening}' at position {pos}"

        return None

    def _validate_functions(self, formula: str) -> tuple[list[str], list[str]]:
        """Validate function names.

        Args:
            formula: Formula body

        Returns:
            Tuple of (errors, warnings)
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Find all function calls
        matches = FUNCTION_PATTERN.finditer(formula)
        for match in matches:
            func_name = match.group(1).upper()
            if func_name not in KNOWN_FUNCTIONS:
                warnings.append(f"Unknown function: {func_name}")

        return errors, warnings

    def _validate_cell_references(self, formula: str) -> list[str]:
        """Validate cell references.

        Args:
            formula: Formula body

        Returns:
            List of warnings
        """
        warnings: list[str] = []

        # Find cell references
        matches = CELL_REF_PATTERN.finditer(formula)
        for match in matches:
            ref = match.group(0)
            # Extract column and row
            col = ""
            row = ""
            for char in ref:
                if char.isalpha():
                    col += char
                elif char.isdigit():
                    row += char

            # Basic sanity checks
            col_clean = col.replace("$", "")
            if len(col_clean) > 3:  # XFD is max column
                warnings.append(f"Suspicious column reference: {ref}")

            if row:
                row_num = int(row.replace("$", ""))
                if row_num > 1048576:  # Excel max rows
                    warnings.append(f"Row number exceeds maximum: {ref}")

        return warnings

    def _check_common_mistakes(self, formula: str) -> list[str]:
        """Check for common formula mistakes.

        Args:
            formula: Formula body

        Returns:
            List of errors
        """
        errors: list[str] = []

        # Check for empty function calls
        if re.search(r"[A-Z]+\(\s*\)", formula):
            errors.append("Empty function call detected")

        # Check for double operators
        if re.search(r"[+\-*/]{2,}", formula):
            errors.append("Double operator detected (e.g., ++, --)")

        # Check for division by zero literal
        if re.search(r"/\s*0\s*(?:[+\-*/;)]|$)", formula):
            errors.append("Division by zero literal detected")

        return errors
