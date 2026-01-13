"""Data validation rules and configuration.

Provides comprehensive data validation support for spreadsheets
including lists, numbers, dates, and custom formulas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any

# ============================================================================
# Enumerations
# ============================================================================


class ValidationType(Enum):
    """Types of data validation."""

    ANY = "any"  # No validation
    WHOLE_NUMBER = "wholeNumber"
    DECIMAL = "decimal"
    LIST = "list"
    DATE = "date"
    TIME = "time"
    TEXT_LENGTH = "textLength"
    CUSTOM = "custom"


class ValidationOperator(Enum):
    """Comparison operators for validation."""

    BETWEEN = "between"
    NOT_BETWEEN = "notBetween"
    EQUAL = "equal"
    NOT_EQUAL = "notEqual"
    GREATER_THAN = "greaterThan"
    LESS_THAN = "lessThan"
    GREATER_THAN_OR_EQUAL = "greaterThanOrEqual"
    LESS_THAN_OR_EQUAL = "lessThanOrEqual"


class ErrorAlertStyle(Enum):
    """Error alert styles."""

    STOP = "stop"  # Prevent invalid entry
    WARNING = "warning"  # Warn but allow
    INFORMATION = "information"  # Info only, always allow


# ============================================================================
# Input Message Configuration
# ============================================================================


@dataclass
class InputMessage:
    """Input message shown when cell is selected.

    Examples:
        msg = InputMessage(
            title="Enter Amount",
            body="Enter a positive dollar amount",
        )
    """

    title: str = ""
    body: str = ""
    show: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "body": self.body,
            "show": self.show,
        }


# ============================================================================
# Error Alert Configuration
# ============================================================================


@dataclass
class ErrorAlert:
    """Error alert shown on invalid entry.

    Examples:
        # Stop entry
        alert = ErrorAlert(
            style=ErrorAlertStyle.STOP,
            title="Invalid Amount",
            message="Please enter a positive number",
        )

        # Warning only
        alert = ErrorAlert(
            style=ErrorAlertStyle.WARNING,
            title="Unusual Value",
            message="This value is larger than typical. Continue?",
        )
    """

    style: ErrorAlertStyle = ErrorAlertStyle.STOP
    title: str = ""
    message: str = ""
    show: bool = True

    @classmethod
    def stop(cls, title: str, message: str) -> ErrorAlert:
        """Create stop error alert."""
        return cls(style=ErrorAlertStyle.STOP, title=title, message=message)

    @classmethod
    def warning(cls, title: str, message: str) -> ErrorAlert:
        """Create warning error alert."""
        return cls(style=ErrorAlertStyle.WARNING, title=title, message=message)

    @classmethod
    def info(cls, title: str, message: str) -> ErrorAlert:
        """Create information error alert."""
        return cls(style=ErrorAlertStyle.INFORMATION, title=title, message=message)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "style": self.style.value,
            "title": self.title,
            "message": self.message,
            "show": self.show,
        }


# ============================================================================
# Data Validation Rule
# ============================================================================


@dataclass
class DataValidation:
    """Data validation rule configuration.

    Examples:
        # List validation
        category_validation = DataValidation.list(
            items=["Housing", "Utilities", "Groceries", "Transport"],
            input_message=InputMessage("Category", "Select from list"),
            error_alert=ErrorAlert.stop("Invalid", "Select from dropdown"),
        )

        # Number validation
        amount_validation = DataValidation.decimal_greater_than(
            value=0,
            input_message=InputMessage("Amount", "Enter positive amount"),
        )

        # Date validation
        date_validation = DataValidation.date_after(
            date(2024, 1, 1),
            input_message=InputMessage("Date", "Enter date in 2024"),
        )

        # Custom formula
        custom_validation = DataValidation.custom(
            formula="AND(A1>0, A1<=SUM(B:B))",
            input_message=InputMessage("Value", "Must not exceed total"),
        )
    """

    type: ValidationType = ValidationType.ANY
    operator: ValidationOperator | None = None

    # Values for comparison
    value1: Any = None  # First value / formula / list reference
    value2: Any = None  # Second value for BETWEEN

    # For list validation
    list_items: list[str] = field(default_factory=list)
    list_source: str | None = None  # Cell range reference for list
    show_dropdown: bool = True

    # Custom formula
    formula: str | None = None

    # Allow blank cells
    allow_blank: bool = True

    # Messages
    input_message: InputMessage | None = None
    error_alert: ErrorAlert | None = None

    # ========================================================================
    # Factory Methods - List Validation
    # ========================================================================

    @classmethod
    def list(
        cls,
        items: list[str],
        show_dropdown: bool = True,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create list validation from explicit items."""
        return cls(
            type=ValidationType.LIST,
            list_items=items,
            show_dropdown=show_dropdown,
            allow_blank=allow_blank,
            input_message=input_message,
            error_alert=error_alert,
        )

    @classmethod
    def list_from_range(
        cls,
        source_range: str,
        show_dropdown: bool = True,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create list validation from cell range."""
        return cls(
            type=ValidationType.LIST,
            list_source=source_range,
            show_dropdown=show_dropdown,
            allow_blank=allow_blank,
            input_message=input_message,
            error_alert=error_alert,
        )

    # ========================================================================
    # Factory Methods - Number Validation
    # ========================================================================

    @classmethod
    def whole_number(
        cls,
        operator: ValidationOperator,
        value1: int | str,
        value2: int | str | None = None,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create whole number validation."""
        return cls(
            type=ValidationType.WHOLE_NUMBER,
            operator=operator,
            value1=value1,
            value2=value2,
            allow_blank=allow_blank,
            input_message=input_message,
            error_alert=error_alert,
        )

    @classmethod
    def decimal(
        cls,
        operator: ValidationOperator,
        value1: float | str,
        value2: float | str | None = None,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create decimal number validation."""
        return cls(
            type=ValidationType.DECIMAL,
            operator=operator,
            value1=value1,
            value2=value2,
            allow_blank=allow_blank,
            input_message=input_message,
            error_alert=error_alert,
        )

    @classmethod
    def decimal_between(
        cls,
        min_value: float | str,
        max_value: float | str,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create decimal between validation."""
        return cls.decimal(
            ValidationOperator.BETWEEN,
            min_value,
            max_value,
            allow_blank,
            input_message,
            error_alert,
        )

    @classmethod
    def decimal_greater_than(
        cls,
        value: float | str,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create decimal greater than validation."""
        return cls.decimal(
            ValidationOperator.GREATER_THAN,
            value,
            allow_blank=allow_blank,
            input_message=input_message,
            error_alert=error_alert,
        )

    @classmethod
    def positive_number(
        cls,
        allow_zero: bool = False,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create positive number validation."""
        op = (
            ValidationOperator.GREATER_THAN_OR_EQUAL
            if allow_zero
            else ValidationOperator.GREATER_THAN
        )
        return cls.decimal(
            op,
            0,
            allow_blank=allow_blank,
            input_message=input_message,
            error_alert=error_alert
            or ErrorAlert.stop(
                "Invalid Amount",
                "Please enter a positive number" + (" or zero" if allow_zero else ""),
            ),
        )

    @classmethod
    def percentage(
        cls,
        allow_over_100: bool = False,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create percentage validation (0-100% or 0-1)."""
        if allow_over_100:
            return cls.decimal_greater_than(
                0,
                allow_blank=allow_blank,
                input_message=input_message
                or InputMessage("Percentage", "Enter a percentage"),
                error_alert=error_alert,
            )
        return cls.decimal_between(
            0,
            1 if not allow_over_100 else 100,
            allow_blank=allow_blank,
            input_message=input_message or InputMessage("Percentage", "Enter 0-100%"),
            error_alert=error_alert
            or ErrorAlert.stop(
                "Invalid Percentage",
                "Enter a value between 0 and 100%",
            ),
        )

    # ========================================================================
    # Factory Methods - Date Validation
    # ========================================================================

    @classmethod
    def date_validation(
        cls,
        operator: ValidationOperator,
        value1: date | datetime | str,
        value2: date | datetime | str | None = None,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create date validation."""
        # Convert dates to strings if needed
        if isinstance(value1, (date, datetime)):
            value1 = value1.isoformat()
        if isinstance(value2, (date, datetime)):
            value2 = value2.isoformat()

        return cls(
            type=ValidationType.DATE,
            operator=operator,
            value1=value1,
            value2=value2,
            allow_blank=allow_blank,
            input_message=input_message,
            error_alert=error_alert,
        )

    @classmethod
    def date_between(
        cls,
        start_date: date | datetime | str,
        end_date: date | datetime | str,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create date between validation."""
        return cls.date_validation(
            ValidationOperator.BETWEEN,
            start_date,
            end_date,
            allow_blank,
            input_message,
            error_alert,
        )

    @classmethod
    def date_after(
        cls,
        after_date: date | datetime | str,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create date after validation."""
        return cls.date_validation(
            ValidationOperator.GREATER_THAN,
            after_date,
            allow_blank=allow_blank,
            input_message=input_message,
            error_alert=error_alert,
        )

    @classmethod
    def date_before(
        cls,
        before_date: date | datetime | str,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create date before validation."""
        return cls.date_validation(
            ValidationOperator.LESS_THAN,
            before_date,
            allow_blank=allow_blank,
            input_message=input_message,
            error_alert=error_alert,
        )

    @classmethod
    def future_date(
        cls,
        allow_today: bool = True,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create future date validation using formula."""
        formula = "A1>=TODAY()" if allow_today else "A1>TODAY()"
        return cls.custom(
            formula=formula,
            allow_blank=allow_blank,
            input_message=input_message
            or InputMessage(
                "Future Date",
                "Enter a date in the future" + (" or today" if allow_today else ""),
            ),
            error_alert=error_alert
            or ErrorAlert.stop(
                "Invalid Date",
                "Please enter a future date",
            ),
        )

    # ========================================================================
    # Factory Methods - Text Length Validation
    # ========================================================================

    @classmethod
    def text_length(
        cls,
        operator: ValidationOperator,
        value1: int | str,
        value2: int | str | None = None,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create text length validation."""
        return cls(
            type=ValidationType.TEXT_LENGTH,
            operator=operator,
            value1=value1,
            value2=value2,
            allow_blank=allow_blank,
            input_message=input_message,
            error_alert=error_alert,
        )

    @classmethod
    def text_max_length(
        cls,
        max_length: int,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create maximum text length validation."""
        return cls.text_length(
            ValidationOperator.LESS_THAN_OR_EQUAL,
            max_length,
            allow_blank=allow_blank,
            input_message=input_message
            or InputMessage(
                "Text Input",
                f"Enter up to {max_length} characters",
            ),
            error_alert=error_alert
            or ErrorAlert.stop(
                "Too Long",
                f"Text must be {max_length} characters or less",
            ),
        )

    # ========================================================================
    # Factory Methods - Custom Validation
    # ========================================================================

    @classmethod
    def custom(
        cls,
        formula: str,
        allow_blank: bool = True,
        input_message: InputMessage | None = None,
        error_alert: ErrorAlert | None = None,
    ) -> DataValidation:
        """Create custom formula validation."""
        return cls(
            type=ValidationType.CUSTOM,
            formula=formula,
            allow_blank=allow_blank,
            input_message=input_message,
            error_alert=error_alert,
        )

    # ========================================================================
    # Serialization
    # ========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "type": self.type.value,
            "allowBlank": self.allow_blank,
        }

        if self.operator:
            result["operator"] = self.operator.value
        if self.value1 is not None:
            result["value1"] = self.value1
        if self.value2 is not None:
            result["value2"] = self.value2
        if self.list_items:
            result["listItems"] = self.list_items
        if self.list_source:
            result["listSource"] = self.list_source
        if self.type == ValidationType.LIST:
            result["showDropdown"] = self.show_dropdown
        if self.formula:
            result["formula"] = self.formula
        if self.input_message:
            result["inputMessage"] = self.input_message.to_dict()
        if self.error_alert:
            result["errorAlert"] = self.error_alert.to_dict()

        return result


# ============================================================================
# Validation Configuration for a Range
# ============================================================================


@dataclass
class ValidationConfig:
    """Data validation configuration for a cell range.

    Combines range reference with validation rule.

    Examples:
        config = ValidationConfig(
            range="A2:A100",
            validation=DataValidation.list(
                ["Housing", "Utilities", "Groceries"],
            ),
        )
    """

    range: str
    validation: DataValidation

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "range": self.range,
            "validation": self.validation.to_dict(),
        }


# ============================================================================
# Financial Presets
# ============================================================================


class FinancialValidations:
    """Pre-configured validations for financial use cases."""

    @staticmethod
    def expense_category(categories: list[str] | None = None) -> DataValidation:
        """Create expense category validation."""
        default_categories = [
            "Housing",
            "Utilities",
            "Groceries",
            "Transport",
            "Healthcare",
            "Entertainment",
            "Dining",
            "Shopping",
            "Insurance",
            "Education",
            "Personal",
            "Other",
        ]
        return DataValidation.list(
            items=categories or default_categories,
            input_message=InputMessage("Category", "Select expense category"),
            error_alert=ErrorAlert.stop(
                "Invalid Category", "Select from dropdown list"
            ),
        )

    @staticmethod
    def dollar_amount(allow_zero: bool = True) -> DataValidation:
        """Create dollar amount validation (positive)."""
        return DataValidation.positive_number(
            allow_zero=allow_zero,
            input_message=InputMessage("Amount", "Enter dollar amount"),
            error_alert=ErrorAlert.stop(
                "Invalid Amount", "Enter a positive dollar amount"
            ),
        )

    @staticmethod
    def transaction_date(
        start_year: int = 2020,
        allow_future: bool = False,
    ) -> DataValidation:
        """Create transaction date validation."""
        if allow_future:
            return DataValidation.date_after(
                date(start_year, 1, 1),
                input_message=InputMessage("Date", f"Enter date from {start_year}"),
                error_alert=ErrorAlert.stop(
                    "Invalid Date", f"Date must be after {start_year}"
                ),
            )
        # Use custom formula to check <= TODAY()
        return DataValidation.custom(
            formula=f"AND(A1>=DATE({start_year},1,1), A1<=TODAY())",
            input_message=InputMessage(
                "Date", f"Enter date from {start_year} to today"
            ),
            error_alert=ErrorAlert.stop("Invalid Date", "Date must be in the past"),
        )

    @staticmethod
    def account_name(accounts: list[str]) -> DataValidation:
        """Create account name validation."""
        return DataValidation.list(
            items=accounts,
            input_message=InputMessage("Account", "Select account"),
            error_alert=ErrorAlert.stop("Invalid Account", "Select from dropdown list"),
        )

    @staticmethod
    def payment_method() -> DataValidation:
        """Create payment method validation."""
        methods = [
            "Cash",
            "Credit Card",
            "Debit Card",
            "Bank Transfer",
            "Check",
            "PayPal",
            "Venmo",
            "Other",
        ]
        return DataValidation.list(
            items=methods,
            input_message=InputMessage("Payment Method", "Select payment method"),
        )

    @staticmethod
    def description(max_length: int = 200) -> DataValidation:
        """Create description field validation."""
        return DataValidation.text_max_length(
            max_length=max_length,
            input_message=InputMessage(
                "Description", f"Enter description (max {max_length} chars)"
            ),
        )

    @staticmethod
    def budget_allocation() -> DataValidation:
        """Create budget allocation validation (0-100%)."""
        return DataValidation.percentage(
            allow_over_100=False,
            input_message=InputMessage(
                "Allocation", "Enter budget percentage (0-100%)"
            ),
            error_alert=ErrorAlert.stop("Invalid Percentage", "Enter 0-100%"),
        )

    @staticmethod
    def recurring_frequency() -> DataValidation:
        """Create recurring frequency validation."""
        frequencies = [
            "Daily",
            "Weekly",
            "Bi-Weekly",
            "Monthly",
            "Quarterly",
            "Semi-Annually",
            "Annually",
        ]
        return DataValidation.list(
            items=frequencies,
            input_message=InputMessage("Frequency", "Select recurring frequency"),
        )
