"""Fluent DataValidationBuilder for data validation rules.

Provides a chainable API for building data validation rules
with support for lists, numbers, dates, and custom formulas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Self

from spreadsheet_dl.schema.data_validation import (
    DataValidation,
    ErrorAlert,
    ErrorAlertStyle,
    InputMessage,
    ValidationOperator,
    ValidationType,
)


@dataclass
class DataValidationBuilder:
    r"""Fluent builder for data validation rules.

    Examples:
        # List validation
        category_validation = DataValidationBuilder() \\
            .list(["Housing", "Utilities", "Groceries", "Transport"]) \\
            .show_dropdown() \\
            .input_message("Select Category", "Choose from the list") \\
            .error_alert("stop", "Invalid Category", "Please select from list") \\
            .build()

        # Number validation
        amount_validation = DataValidationBuilder() \\
            .decimal() \\
            .greater_than(0) \\
            .input_message("Enter Amount", "Enter positive amount") \\
            .build()

        # Date validation
        date_validation = DataValidationBuilder() \\
            .date() \\
            .between("2024-01-01", "2024-12-31") \\
            .input_message("Enter Date", "Date must be in 2024") \\
            .build()

        # Custom formula
        custom_validation = DataValidationBuilder() \\
            .custom("=A1<=SUM(B:B)") \\
            .error_alert("warning", "Over Budget", "Value exceeds total") \\
            .build()
    """

    # Validation type and operator
    _type: ValidationType = field(default=ValidationType.ANY)
    _operator: ValidationOperator | None = field(default=None)

    # Values
    _value1: Any = field(default=None)
    _value2: Any = field(default=None)

    # List options
    _list_items: list[str] = field(default_factory=list)
    _list_source: str | None = field(default=None)
    _show_dropdown: bool = field(default=True)

    # Custom formula
    _formula: str | None = field(default=None)

    # Allow blank
    _allow_blank: bool = field(default=True)

    # Messages
    _input_message: InputMessage | None = field(default=None)
    _error_alert: ErrorAlert | None = field(default=None)

    # ========================================================================
    # Type Selection
    # ========================================================================

    def list(self, items: list[str]) -> Self:
        """Set validation to list type with explicit items.

        Args:
            items: List of allowed values

        Returns:
            Self for chaining
        """
        self._type = ValidationType.LIST
        self._list_items = items
        return self

    def list_from_range(self, source_range: str) -> Self:
        """Set validation to list type from cell range.

        Args:
            source_range: Cell range containing allowed values

        Returns:
            Self for chaining
        """
        self._type = ValidationType.LIST
        self._list_source = source_range
        return self

    def whole_number(self) -> Self:
        """Set validation to whole number type."""
        self._type = ValidationType.WHOLE_NUMBER
        return self

    def decimal(self) -> Self:
        """Set validation to decimal type."""
        self._type = ValidationType.DECIMAL
        return self

    def date(self) -> Self:
        """Set validation to date type."""
        self._type = ValidationType.DATE
        return self

    def time(self) -> Self:
        """Set validation to time type."""
        self._type = ValidationType.TIME
        return self

    def text_length(self) -> Self:
        """Set validation to text length type."""
        self._type = ValidationType.TEXT_LENGTH
        return self

    def custom(self, formula: str) -> Self:
        """Set validation to custom formula type.

        Args:
            formula: Validation formula

        Returns:
            Self for chaining
        """
        self._type = ValidationType.CUSTOM
        self._formula = formula
        return self

    # ========================================================================
    # Operators
    # ========================================================================

    def between(self, min_value: Any, max_value: Any) -> Self:
        """Set between operator.

        Args:
            min_value: Minimum value
            max_value: Maximum value

        Returns:
            Self for chaining
        """
        self._operator = ValidationOperator.BETWEEN
        self._value1 = self._convert_value(min_value)
        self._value2 = self._convert_value(max_value)
        return self

    def not_between(self, min_value: Any, max_value: Any) -> Self:
        """Set not between operator.

        Args:
            min_value: Minimum value
            max_value: Maximum value

        Returns:
            Self for chaining
        """
        self._operator = ValidationOperator.NOT_BETWEEN
        self._value1 = self._convert_value(min_value)
        self._value2 = self._convert_value(max_value)
        return self

    def equal_to(self, value: Any) -> Self:
        """Set equal operator.

        Args:
            value: Value to compare

        Returns:
            Self for chaining
        """
        self._operator = ValidationOperator.EQUAL
        self._value1 = self._convert_value(value)
        return self

    def not_equal_to(self, value: Any) -> Self:
        """Set not equal operator.

        Args:
            value: Value to compare

        Returns:
            Self for chaining
        """
        self._operator = ValidationOperator.NOT_EQUAL
        self._value1 = self._convert_value(value)
        return self

    def greater_than(self, value: Any) -> Self:
        """Set greater than operator.

        Args:
            value: Value to compare

        Returns:
            Self for chaining
        """
        self._operator = ValidationOperator.GREATER_THAN
        self._value1 = self._convert_value(value)
        return self

    def less_than(self, value: Any) -> Self:
        """Set less than operator.

        Args:
            value: Value to compare

        Returns:
            Self for chaining
        """
        self._operator = ValidationOperator.LESS_THAN
        self._value1 = self._convert_value(value)
        return self

    def greater_than_or_equal(self, value: Any) -> Self:
        """Set greater than or equal operator.

        Args:
            value: Value to compare

        Returns:
            Self for chaining
        """
        self._operator = ValidationOperator.GREATER_THAN_OR_EQUAL
        self._value1 = self._convert_value(value)
        return self

    def less_than_or_equal(self, value: Any) -> Self:
        """Set less than or equal operator.

        Args:
            value: Value to compare

        Returns:
            Self for chaining
        """
        self._operator = ValidationOperator.LESS_THAN_OR_EQUAL
        self._value1 = self._convert_value(value)
        return self

    # ========================================================================
    # Options
    # ========================================================================

    def show_dropdown(self, show: bool = True) -> Self:
        """Show dropdown for list validation.

        Args:
            show: Whether to show dropdown

        Returns:
            Self for chaining
        """
        self._show_dropdown = show
        return self

    def allow_blank(self, allow: bool = True) -> Self:
        """Allow blank values.

        Args:
            allow: Whether to allow blanks

        Returns:
            Self for chaining
        """
        self._allow_blank = allow
        return self

    # ========================================================================
    # Messages
    # ========================================================================

    def input_message(self, title: str, body: str = "") -> Self:
        """Set input message shown when cell is selected.

        Args:
            title: Message title
            body: Message body

        Returns:
            Self for chaining
        """
        self._input_message = InputMessage(title=title, body=body)
        return self

    def error_alert(
        self,
        style: str | ErrorAlertStyle,
        title: str,
        message: str,
    ) -> Self:
        """Set error alert shown on invalid entry.

        Args:
            style: Alert style ("stop", "warning", "information")
            title: Alert title
            message: Alert message

        Returns:
            Self for chaining
        """
        if isinstance(style, str):
            style = ErrorAlertStyle(style.lower())

        self._error_alert = ErrorAlert(style=style, title=title, message=message)
        return self

    def stop_alert(self, title: str, message: str) -> Self:
        """Set stop error alert (prevents invalid entry).

        Args:
            title: Alert title
            message: Alert message

        Returns:
            Self for chaining
        """
        return self.error_alert(ErrorAlertStyle.STOP, title, message)

    def warning_alert(self, title: str, message: str) -> Self:
        """Set warning alert (warns but allows entry).

        Args:
            title: Alert title
            message: Alert message

        Returns:
            Self for chaining
        """
        return self.error_alert(ErrorAlertStyle.WARNING, title, message)

    def info_alert(self, title: str, message: str) -> Self:
        """Set information alert.

        Args:
            title: Alert title
            message: Alert message

        Returns:
            Self for chaining
        """
        return self.error_alert(ErrorAlertStyle.INFORMATION, title, message)

    # ========================================================================
    # Build
    # ========================================================================

    def build(self) -> DataValidation:
        """Build the DataValidation object.

        Returns:
            Configured DataValidation
        """
        return DataValidation(
            type=self._type,
            operator=self._operator,
            value1=self._value1,
            value2=self._value2,
            list_items=self._list_items,
            list_source=self._list_source,
            show_dropdown=self._show_dropdown,
            formula=self._formula,
            allow_blank=self._allow_blank,
            input_message=self._input_message,
            error_alert=self._error_alert,
        )

    # ========================================================================
    # Helpers
    # ========================================================================

    def _convert_value(self, value: Any) -> Any:
        """Convert value to appropriate format."""
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        return value


# ============================================================================
# Convenience Factory Functions
# ============================================================================


def list_validation(items: list[str]) -> DataValidationBuilder:
    """Create list validation builder."""
    return DataValidationBuilder().list(items)


def number_validation() -> DataValidationBuilder:
    """Create decimal number validation builder."""
    return DataValidationBuilder().decimal()


def date_validation() -> DataValidationBuilder:
    """Create date validation builder."""
    return DataValidationBuilder().date()


def positive_number_validation(
    allow_zero: bool = False,
    message: str = "Enter a positive number",
) -> DataValidation:
    """Create ready-to-use positive number validation.

    Args:
        allow_zero: Whether to allow zero
        message: Error message

    Returns:
        Configured DataValidation
    """
    builder = DataValidationBuilder().decimal()
    if allow_zero:
        builder.greater_than_or_equal(0)
    else:
        builder.greater_than(0)

    return (
        builder.input_message("Amount", message).stop_alert("Invalid", message).build()
    )


def category_validation(categories: list[str]) -> DataValidation:
    """Create ready-to-use category list validation.

    Args:
        categories: List of categories

    Returns:
        Configured DataValidation
    """
    return (
        DataValidationBuilder()
        .list(categories)
        .show_dropdown()
        .input_message("Category", "Select from list")
        .stop_alert("Invalid Category", "Please select from the dropdown list")
        .build()
    )
