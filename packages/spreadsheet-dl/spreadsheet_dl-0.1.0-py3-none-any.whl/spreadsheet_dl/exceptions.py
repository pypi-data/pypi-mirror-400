"""Custom exceptions for SpreadsheetDL.

Provides a comprehensive hierarchy of exceptions with error codes,
actionable guidance, and contextual information for better error handling
and programmatic error recovery.

Error Code Format: FT-<CATEGORY>-<NUMBER>

Categories:
    GEN (001-099): General/uncategorized errors
    FILE (100-199): File system errors
    ODS (200-299): ODS file errors
    CSV (300-399): CSV import errors
    VAL (400-499): Validation errors
    CFG (500-599): Configuration errors
    NET (600-699): Network/WebDAV errors
    TMPL (700-799): Template errors
    FMT (800-899): Formatting errors
    EXT (900-999): Extension/plugin errors
    SEC (1000-1099): Security errors
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ErrorSeverity(Enum):
    """Severity level for errors."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ErrorContext:
    """Context information for an error."""

    file_path: str | None = None
    line_number: int | None = None
    column: int | None = None
    value: str | None = None
    expected: str | None = None
    actual: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        result: dict[str, Any] = {}
        if self.file_path:
            result["file"] = self.file_path
        if self.line_number is not None:
            result["line"] = self.line_number
        if self.column is not None:
            result["column"] = self.column
        if self.value:
            result["value"] = self.value
        if self.expected:
            result["expected"] = self.expected
        if self.actual:
            result["actual"] = self.actual
        if self.extra:
            result.update(self.extra)
        return result


class SpreadsheetDLError(Exception):
    """Base exception for all SpreadsheetDL errors.

    Provides structured error information including:
    - Machine-readable error code
    - Human-readable summary
    - Detailed explanation
    - Actionable suggestion
    - Documentation reference
    - Contextual information
    """

    # Default error code - subclasses should override
    error_code: str = "FT-GEN-001"
    severity: ErrorSeverity = ErrorSeverity.ERROR
    doc_url_base: str = "https://github.com/lair-click-bats/spreadsheet-dl/blob/main/docs/error-codes.md"

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        details: str | None = None,
        suggestion: str | None = None,
        context: ErrorContext | None = None,
        severity: ErrorSeverity | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable summary (one line).
            error_code: Optional override for error code.
            details: Detailed explanation of the error.
            suggestion: Actionable fix suggestion.
            context: Contextual information (file, line, value).
            severity: Error severity level.
        """
        super().__init__(message)
        self.message = message
        if error_code:
            self.error_code = error_code
        if severity:
            self.severity = severity
        self.details = details
        self.suggestion = suggestion
        self.context = context or ErrorContext()

    @property
    def doc_url(self) -> str:
        """Get documentation URL for this error."""
        # Generate anchor link for error code (e.g., FT-GEN-001 -> #ft-gen-001)
        anchor = self.error_code.lower()
        return f"{self.doc_url_base}#{anchor}"

    def format_error(self, use_color: bool = True, show_debug: bool = False) -> str:
        """Format error for display.

        Args:
            use_color: Whether to use ANSI colors.
            show_debug: Whether to include debug information.

        Returns:
            Formatted error string.
        """
        lines = []

        # Colors
        if use_color:
            red = "\033[91m"
            yellow = "\033[93m"
            blue = "\033[94m"
            gray = "\033[90m"
            bold = "\033[1m"
            reset = "\033[0m"
        else:
            red = yellow = blue = gray = bold = reset = ""

        # Header with error code
        severity_color = red if self.severity == ErrorSeverity.ERROR else yellow
        lines.append(
            f"{severity_color}{bold}Error [{self.error_code}]{reset}: {self.message}"
        )

        # Context section
        ctx = self.context.to_dict()
        if ctx:
            lines.append("")
            if "file" in ctx:
                lines.append(f"  {gray}File:{reset}    {ctx['file']}")
            if "line" in ctx:
                lines.append(f"  {gray}Line:{reset}    {ctx['line']}")
            if "value" in ctx:
                lines.append(f"  {gray}Value:{reset}   {ctx['value']}")
            if "expected" in ctx:
                lines.append(f"  {gray}Expected:{reset} {ctx['expected']}")
            if "actual" in ctx:
                lines.append(f"  {gray}Found:{reset}    {ctx['actual']}")

        # Details section
        if self.details:
            lines.append("")
            lines.append(f"  {self.details}")

        # Suggestion section
        if self.suggestion:
            lines.append("")
            lines.append(f"{blue}Suggestion:{reset} {self.suggestion}")

        # Documentation link
        lines.append("")
        lines.append(f"{gray}Documentation: {self.doc_url}{reset}")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for JSON output."""
        return {
            "error_code": self.error_code,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "suggestion": self.suggestion,
            "context": self.context.to_dict(),
            "doc_url": self.doc_url,
        }

    def __str__(self) -> str:
        """Return formatted error string without colors."""
        return self.format_error(use_color=False)


# =============================================================================
# General Errors (FT-GEN-001 to FT-GEN-099)
# =============================================================================


class UnknownError(SpreadsheetDLError):
    """Unknown or unexpected error."""

    error_code = "FT-GEN-001"

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        *,
        original_error: Exception | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the error.

        Args:
            message: Error message describing what went wrong.
            original_error: The underlying exception that caused this error.
            **kwargs: Additional error context.
        """
        suggestion = "Please report this issue with the error details."
        if original_error:
            message = f"{message}: {original_error}"
        super().__init__(message, suggestion=suggestion, **kwargs)
        self.original_error = original_error


class OperationCancelledError(SpreadsheetDLError):
    """User cancelled the operation."""

    error_code = "FT-GEN-002"
    severity = ErrorSeverity.INFO

    def __init__(self, operation: str = "Operation", **kwargs: Any) -> None:
        """Initialize the error.

        Args:
            operation: Name of the operation that was cancelled.
            **kwargs: Additional error context.
        """
        super().__init__(
            f"{operation} was cancelled by user",
            suggestion="Re-run the command to try again.",
            **kwargs,
        )


class NotImplementedFeatureError(SpreadsheetDLError):
    """Feature is not yet implemented."""

    error_code = "FT-GEN-003"

    def __init__(self, feature: str, **kwargs: Any) -> None:
        """Initialize the error.

        Args:
            feature: Name of the feature that is not implemented.
            **kwargs: Additional error context.
        """
        self.feature = feature
        super().__init__(
            f"Feature '{feature}' is not yet implemented",
            suggestion="Check the roadmap for planned features.",
            **kwargs,
        )


# =============================================================================
# File Errors (FT-FILE-100 to FT-FILE-199)
# =============================================================================


class FileError(SpreadsheetDLError):
    """Base exception for file-related errors."""

    error_code = "FT-FILE-100"


class FileNotFoundError(FileError):
    """Raised when a required file is not found."""

    error_code = "FT-FILE-101"

    def __init__(
        self,
        file_path: str | None = None,
        file_type: str = "File",
        **kwargs: Any,
    ) -> None:
        """Initialize the error.

        Args:
            file_path: Path to the file that was not found.
            file_type: Type of file for error message.
            **kwargs: Additional error context.
        """
        self.file_path = file_path
        message = f"{file_type} not found"
        if file_path:
            message = f"{file_type} not found: {file_path}"
        context = ErrorContext(file_path=file_path)
        super().__init__(
            message,
            context=context,
            suggestion="Check that the file path is correct and the file exists.",
            details=f"The specified {file_type.lower()} could not be located on the filesystem.",
            **kwargs,
        )


class FilePermissionError(FileError):
    """Raised when file permission is denied."""

    error_code = "FT-FILE-102"

    def __init__(
        self,
        file_path: str,
        operation: str = "access",
        **kwargs: Any,
    ) -> None:
        """Initialize the error.

        Args:
            file_path: Path to the file with permission issues.
            operation: Operation that was attempted.
            **kwargs: Additional error context.
        """
        self.file_path = file_path
        self.operation = operation
        context = ErrorContext(file_path=file_path)
        super().__init__(
            f"Permission denied: cannot {operation} '{file_path}'",
            context=context,
            suggestion="Check file permissions or run with appropriate privileges.",
            details=f"The current user does not have permission to {operation} this file.",
            **kwargs,
        )


class FileExistsError(FileError):
    """Raised when a file already exists."""

    error_code = "FT-FILE-103"
    severity = ErrorSeverity.WARNING

    def __init__(
        self,
        file_path: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the error.

        Args:
            file_path: Path to the file that already exists.
            **kwargs: Additional error context.
        """
        self.file_path = file_path
        context = ErrorContext(file_path=file_path)
        super().__init__(
            f"File already exists: {file_path}",
            context=context,
            suggestion="Use --force to overwrite or choose a different filename.",
            details="The target file already exists and would be overwritten.",
            **kwargs,
        )


class InvalidFileFormatError(FileError):
    """Raised when a file has an invalid format."""

    error_code = "FT-FILE-104"

    def __init__(
        self,
        file_path: str,
        expected_format: str,
        actual_format: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.file_path = file_path
        self.expected_format = expected_format
        self.actual_format = actual_format
        context = ErrorContext(
            file_path=file_path, expected=expected_format, actual=actual_format
        )
        message = f"Invalid file format for '{file_path}'"
        details = f"Expected {expected_format} format"
        if actual_format:
            details += f", but found {actual_format}"
        super().__init__(
            message,
            context=context,
            details=details,
            suggestion=f"Ensure the file is a valid {expected_format} file.",
            **kwargs,
        )


class FileWriteError(FileError):
    """Raised when writing to a file fails."""

    error_code = "FT-FILE-105"

    def __init__(
        self,
        file_path: str,
        reason: str = "Unknown error",
        **kwargs: Any,
    ) -> None:
        """Initialize the error.

        Args:
            file_path: Path to the file that could not be written.
            reason: Reason for the write failure.
            **kwargs: Additional error context.
        """
        self.file_path = file_path
        self.reason = reason
        context = ErrorContext(file_path=file_path)
        super().__init__(
            f"Failed to write file: {file_path}",
            context=context,
            details=f"Write operation failed: {reason}",
            suggestion="Check disk space and write permissions.",
            **kwargs,
        )


class FileReadError(FileError):
    """Raised when reading a file fails."""

    error_code = "FT-FILE-106"

    def __init__(
        self,
        file_path: str,
        reason: str = "Unknown error",
        **kwargs: Any,
    ) -> None:
        """Initialize the error.

        Args:
            file_path: Path to the file that could not be read.
            reason: Reason for the read failure.
            **kwargs: Additional error context.
        """
        self.file_path = file_path
        self.reason = reason
        context = ErrorContext(file_path=file_path)
        super().__init__(
            f"Failed to read file: {file_path}",
            context=context,
            details=f"Read operation failed: {reason}",
            suggestion="Check that the file is not corrupted and is readable.",
            **kwargs,
        )


# =============================================================================
# ODS Errors (FT-ODS-200 to FT-ODS-299)
# =============================================================================


class OdsError(SpreadsheetDLError):
    """Base exception for ODS file errors."""

    error_code = "FT-ODS-200"


class OdsReadError(OdsError):
    """Raised when reading an ODS file fails."""

    error_code = "FT-ODS-201"

    def __init__(
        self,
        file_path: str,
        reason: str = "Unable to parse ODS file",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.file_path = file_path
        self.reason = reason
        context = ErrorContext(file_path=file_path)
        super().__init__(
            f"Cannot read ODS file: {file_path}",
            context=context,
            details=reason,
            suggestion="Ensure the file is a valid ODS spreadsheet created by LibreOffice or Collabora.",
            **kwargs,
        )


class OdsWriteError(OdsError):
    """Raised when writing an ODS file fails."""

    error_code = "FT-ODS-202"

    def __init__(
        self,
        file_path: str,
        reason: str = "Unable to write ODS file",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.file_path = file_path
        self.reason = reason
        context = ErrorContext(file_path=file_path)
        super().__init__(
            f"Cannot write ODS file: {file_path}",
            context=context,
            details=reason,
            suggestion="Check disk space and write permissions.",
            **kwargs,
        )


class SheetNotFoundError(OdsError):
    """Raised when a required sheet is not found in ODS file."""

    error_code = "FT-ODS-203"

    def __init__(
        self, sheet_name: str, available_sheets: list[str] | None = None, **kwargs: Any
    ) -> None:
        """Initialize the instance."""
        self.sheet_name = sheet_name
        self.available_sheets = available_sheets or []

        message = f"Sheet '{sheet_name}' not found"
        details = None
        if available_sheets:
            details = f"Available sheets: {', '.join(available_sheets)}"

        super().__init__(
            message,
            details=details,
            suggestion="Check the sheet name or use one of the available sheets.",
            context=ErrorContext(
                value=sheet_name,
                extra={"available_sheets": self.available_sheets},
            ),
            **kwargs,
        )


class InvalidOdsStructureError(OdsError):
    """Raised when ODS file structure is invalid."""

    error_code = "FT-ODS-204"

    def __init__(
        self,
        file_path: str,
        issue: str = "Invalid structure",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.file_path = file_path
        self.issue = issue
        context = ErrorContext(file_path=file_path)
        super().__init__(
            f"Invalid ODS file structure: {issue}",
            context=context,
            details="The ODS file does not have the expected structure for a SpreadsheetDL document.",
            suggestion="Use 'generate' command to create a new valid file.",
            **kwargs,
        )


class FormulaError(OdsError):
    """Raised when a formula is invalid."""

    error_code = "FT-ODS-205"

    def __init__(
        self,
        formula: str,
        reason: str = "Invalid formula syntax",
        cell: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.formula = formula
        self.reason = reason
        self.cell = cell
        context = ErrorContext(value=formula, extra={"cell": cell} if cell else {})
        super().__init__(
            f"Invalid formula: {reason}",
            context=context,
            details=f"Formula: {formula}",
            suggestion="Check formula syntax matches ODS/LibreOffice format.",
            **kwargs,
        )


# =============================================================================
# CSV Errors (FT-CSV-300 to FT-CSV-399)
# =============================================================================


class CSVImportError(SpreadsheetDLError):
    """Base exception for CSV import errors."""

    error_code = "FT-CSV-300"


class CSVParseError(CSVImportError):
    """Raised when parsing a CSV file fails."""

    error_code = "FT-CSV-301"

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        line_number: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.file_path = file_path
        self.line_number = line_number
        context = ErrorContext(file_path=file_path, line_number=line_number)

        full_message = f"CSV parse error: {message}"
        if line_number:
            full_message = f"CSV parse error at line {line_number}: {message}"

        super().__init__(
            full_message,
            context=context,
            suggestion="Check that the CSV file is properly formatted.",
            **kwargs,
        )


class UnsupportedBankFormatError(CSVImportError):
    """Raised when a bank format is not supported."""

    error_code = "FT-CSV-302"
    severity = ErrorSeverity.WARNING

    def __init__(
        self, bank: str, supported_banks: list[str] | None = None, **kwargs: Any
    ) -> None:
        """Initialize the instance."""
        self.bank = bank
        self.supported_banks = supported_banks or []

        message = f"Unsupported bank format: '{bank}'"
        details = None
        if supported_banks:
            details = f"Supported banks: {', '.join(supported_banks)}"

        super().__init__(
            message,
            details=details,
            suggestion="Use --bank=generic for manual column mapping or create a custom bank format.",
            context=ErrorContext(
                value=bank, extra={"supported_banks": self.supported_banks}
            ),
            **kwargs,
        )


class CSVColumnMissingError(CSVImportError):
    """Raised when a required CSV column is missing."""

    error_code = "FT-CSV-303"

    def __init__(
        self,
        column_name: str,
        available_columns: list[str] | None = None,
        file_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.column_name = column_name
        self.available_columns = available_columns or []
        context = ErrorContext(
            file_path=file_path,
            value=column_name,
            extra={"available_columns": self.available_columns},
        )
        message = f"Required column '{column_name}' not found in CSV"
        details = None
        if available_columns:
            details = f"Available columns: {', '.join(available_columns)}"
        super().__init__(
            message,
            context=context,
            details=details,
            suggestion="Ensure the CSV has the required columns or specify column mapping.",
            **kwargs,
        )


class CSVEncodingError(CSVImportError):
    """Raised when CSV encoding cannot be determined or read."""

    error_code = "FT-CSV-304"

    def __init__(
        self,
        file_path: str,
        detected_encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.file_path = file_path
        self.detected_encoding = detected_encoding
        context = ErrorContext(file_path=file_path)
        message = f"Cannot read CSV file due to encoding issues: {file_path}"
        details = None
        if detected_encoding:
            details = f"Detected encoding: {detected_encoding}"
        super().__init__(
            message,
            context=context,
            details=details,
            suggestion="Try specifying encoding with --encoding=utf-8 or --encoding=latin-1",
            **kwargs,
        )


# =============================================================================
# Validation Errors (FT-VAL-400 to FT-VAL-499)
# =============================================================================


class ValidationError(SpreadsheetDLError):
    """Base exception for data validation errors."""

    error_code = "FT-VAL-400"


class InvalidAmountError(ValidationError):
    """Raised when an amount value is invalid."""

    error_code = "FT-VAL-401"

    def __init__(
        self,
        value: str,
        reason: str = "Invalid format",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.value = value
        self.reason = reason
        context = ErrorContext(
            value=value, expected="numeric value (e.g., 123.45, $99.00)"
        )
        super().__init__(
            f"Invalid amount '{value}': {reason}",
            context=context,
            suggestion="Enter a numeric value without letters (e.g., 99.99 or 99).",
            **kwargs,
        )


class InvalidDateError(ValidationError):
    """Raised when a date value is invalid."""

    error_code = "FT-VAL-402"

    def __init__(
        self,
        value: str,
        expected_format: str = "YYYY-MM-DD",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.value = value
        self.expected_format = expected_format
        context = ErrorContext(value=value, expected=expected_format)
        super().__init__(
            f"Invalid date '{value}'",
            context=context,
            details=f"Expected format: {expected_format}",
            suggestion="Enter date in YYYY-MM-DD format (e.g., 2024-12-28).",
            **kwargs,
        )


class InvalidCategoryError(ValidationError):
    """Raised when a category is not recognized."""

    error_code = "FT-VAL-403"

    def __init__(
        self, category: str, valid_categories: list[str] | None = None, **kwargs: Any
    ) -> None:
        """Initialize the instance."""
        self.category = category
        self.valid_categories = valid_categories or []

        message = f"Invalid category '{category}'"
        details = None
        if valid_categories:
            details = f"Valid categories: {', '.join(valid_categories)}"

        super().__init__(
            message,
            context=ErrorContext(
                value=category, extra={"valid_categories": self.valid_categories}
            ),
            details=details,
            suggestion="Use one of the predefined categories or configure custom categories.",
            **kwargs,
        )


class InvalidRangeError(ValidationError):
    """Raised when a value is outside valid range."""

    error_code = "FT-VAL-404"

    def __init__(
        self,
        field: str,
        value: Any,
        min_value: Any | None = None,
        max_value: Any | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.field = field
        self.value = value
        self.min_value = min_value
        self.max_value = max_value

        range_desc = ""
        if min_value is not None and max_value is not None:
            range_desc = f" (must be between {min_value} and {max_value})"
        elif min_value is not None:
            range_desc = f" (must be at least {min_value})"
        elif max_value is not None:
            range_desc = f" (must be at most {max_value})"

        super().__init__(
            f"Invalid {field}: {value}{range_desc}",
            context=ErrorContext(value=str(value)),
            suggestion=f"Provide a valid {field} within the accepted range.",
            **kwargs,
        )


class RequiredFieldError(ValidationError):
    """Raised when a required field is missing."""

    error_code = "FT-VAL-405"

    def __init__(self, field: str, **kwargs: Any) -> None:
        """Initialize the instance."""
        self.field = field
        super().__init__(
            f"Required field '{field}' is missing",
            suggestion=f"Provide a value for the {field} field.",
            **kwargs,
        )


# =============================================================================
# Configuration Errors (FT-CFG-500 to FT-CFG-599)
# =============================================================================


class ConfigurationError(SpreadsheetDLError):
    """Base exception for configuration errors."""

    error_code = "FT-CFG-500"


class MissingConfigError(ConfigurationError):
    """Raised when required configuration is missing."""

    error_code = "FT-CFG-501"

    def __init__(
        self,
        config_key: str,
        config_source: str = "configuration",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.config_key = config_key
        self.config_source = config_source
        super().__init__(
            f"Missing required configuration: '{config_key}'",
            details=f"This value should be set in {config_source}.",
            suggestion=f"Set '{config_key}' in your config file or as environment variable.",
            context=ErrorContext(value=config_key),
            **kwargs,
        )


class InvalidConfigError(ConfigurationError):
    """Raised when configuration value is invalid."""

    error_code = "FT-CFG-502"

    def __init__(
        self,
        config_key: str,
        value: str,
        reason: str = "Invalid value",
        expected: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.config_key = config_key
        self.value = value
        self.reason = reason
        context = ErrorContext(value=value, expected=expected)
        super().__init__(
            f"Invalid configuration for '{config_key}': {reason}",
            context=context,
            suggestion="Check the configuration documentation for valid values.",
            **kwargs,
        )


class ConfigSchemaError(ConfigurationError):
    """Raised when configuration fails schema validation."""

    error_code = "FT-CFG-503"

    def __init__(
        self,
        config_path: str,
        errors: list[str],
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.config_path = config_path
        self.errors = errors
        context = ErrorContext(file_path=config_path)
        details = "Validation errors:\n" + "\n".join(f"  - {e}" for e in errors)
        super().__init__(
            f"Configuration file failed validation: {config_path}",
            context=context,
            details=details,
            suggestion="Fix the listed errors in your configuration file.",
            **kwargs,
        )


class ConfigMigrationError(ConfigurationError):
    """Raised when configuration migration fails."""

    error_code = "FT-CFG-504"

    def __init__(
        self,
        from_version: str,
        to_version: str,
        reason: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.from_version = from_version
        self.to_version = to_version
        self.reason = reason
        super().__init__(
            f"Failed to migrate configuration from v{from_version} to v{to_version}",
            details=reason,
            suggestion="Backup your config and create a fresh configuration.",
            **kwargs,
        )


# =============================================================================
# Network/WebDAV Errors (FT-NET-600 to FT-NET-699)
# =============================================================================


class WebDAVError(SpreadsheetDLError):
    """Base exception for WebDAV errors."""

    error_code = "FT-NET-600"


class ConnectionError(WebDAVError):
    """Raised when connection to WebDAV server fails."""

    error_code = "FT-NET-601"

    def __init__(
        self,
        url: str,
        reason: str = "Connection failed",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.url = url
        self.reason = reason
        super().__init__(
            f"Cannot connect to server: {url}",
            details=reason,
            suggestion="Check your network connection and server URL.",
            context=ErrorContext(extra={"url": url}),
            **kwargs,
        )


class AuthenticationError(WebDAVError):
    """Raised when WebDAV authentication fails."""

    error_code = "FT-NET-602"

    def __init__(
        self,
        url: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.url = url
        super().__init__(
            "Authentication failed",
            details="Invalid username or password for WebDAV/Nextcloud server.",
            suggestion="Check your credentials. For Nextcloud, use an app password.",
            context=ErrorContext(extra={"url": url} if url else {}),
            **kwargs,
        )


class UploadError(WebDAVError):
    """Raised when uploading a file fails."""

    error_code = "FT-NET-603"

    def __init__(
        self,
        file_path: str,
        remote_path: str,
        reason: str = "Upload failed",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.file_path = file_path
        self.remote_path = remote_path
        self.reason = reason
        context = ErrorContext(file_path=file_path, extra={"remote_path": remote_path})
        super().__init__(
            f"Failed to upload '{file_path}' to '{remote_path}'",
            context=context,
            details=reason,
            suggestion="Check network connection and remote path permissions.",
            **kwargs,
        )


class DownloadError(WebDAVError):
    """Raised when downloading a file fails."""

    error_code = "FT-NET-604"

    def __init__(
        self,
        remote_path: str,
        reason: str = "Download failed",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.remote_path = remote_path
        self.reason = reason
        super().__init__(
            f"Failed to download '{remote_path}'",
            details=reason,
            suggestion="Check that the remote file exists and you have read permissions.",
            context=ErrorContext(extra={"remote_path": remote_path}),
            **kwargs,
        )


class ServerError(WebDAVError):
    """Raised when server returns an error."""

    error_code = "FT-NET-605"

    def __init__(
        self,
        status_code: int,
        message: str = "Server error",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.status_code = status_code
        super().__init__(
            f"Server returned error {status_code}: {message}",
            suggestion="Try again later or contact server administrator.",
            context=ErrorContext(extra={"status_code": status_code}),
            **kwargs,
        )


class TimeoutError(WebDAVError):
    """Raised when network operation times out."""

    error_code = "FT-NET-606"

    def __init__(
        self,
        operation: str = "Operation",
        timeout_seconds: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        message = f"{operation} timed out"
        if timeout_seconds:
            message += f" after {timeout_seconds} seconds"
        super().__init__(
            message,
            suggestion="Check your network connection or increase timeout settings.",
            **kwargs,
        )


# =============================================================================
# Template Errors (FT-TMPL-700 to FT-TMPL-799)
# =============================================================================


class TemplateError(SpreadsheetDLError):
    """Base exception for template errors."""

    error_code = "FT-TMPL-700"


class TemplateNotFoundError(TemplateError):
    """Raised when a template is not found."""

    error_code = "FT-TMPL-701"

    def __init__(
        self,
        template_name: str,
        available_templates: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.template_name = template_name
        self.available_templates = available_templates or []

        message = f"Template '{template_name}' not found"
        details = None
        if available_templates:
            details = f"Available templates: {', '.join(available_templates)}"

        super().__init__(
            message,
            context=ErrorContext(
                value=template_name,
                extra={"available_templates": self.available_templates},
            ),
            details=details,
            suggestion="Use 'templates' command to list available templates.",
            **kwargs,
        )


class TemplateValidationError(TemplateError):
    """Raised when template validation fails."""

    error_code = "FT-TMPL-702"

    def __init__(
        self,
        template_name: str,
        errors: list[str],
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.template_name = template_name
        self.errors = errors
        details = "Validation errors:\n" + "\n".join(f"  - {e}" for e in errors)
        super().__init__(
            f"Template '{template_name}' failed validation",
            details=details,
            suggestion="Fix the template definition according to the schema.",
            context=ErrorContext(value=template_name),
            **kwargs,
        )


class ThemeNotFoundError(TemplateError):
    """Raised when a theme is not found."""

    error_code = "FT-TMPL-703"

    def __init__(
        self,
        theme_name: str,
        available_themes: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.theme_name = theme_name
        self.available_themes = available_themes or []

        message = f"Theme '{theme_name}' not found"
        details = None
        if available_themes:
            details = f"Available themes: {', '.join(available_themes)}"

        super().__init__(
            message,
            context=ErrorContext(
                value=theme_name, extra={"available_themes": self.available_themes}
            ),
            details=details,
            suggestion="Use 'themes' command to list available themes.",
            **kwargs,
        )


class ThemeValidationError(TemplateError):
    """Raised when theme validation fails."""

    error_code = "FT-TMPL-704"

    def __init__(
        self,
        theme_path: str,
        errors: list[str],
        line_number: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.theme_path = theme_path
        self.errors = errors
        details = "Validation errors:\n" + "\n".join(f"  - {e}" for e in errors)
        context = ErrorContext(file_path=theme_path, line_number=line_number)
        super().__init__(
            f"Theme validation failed: {theme_path}",
            context=context,
            details=details,
            suggestion="Check theme YAML syntax and required fields.",
            **kwargs,
        )


class CircularInheritanceError(TemplateError):
    """Raised when theme inheritance creates a cycle."""

    error_code = "FT-TMPL-705"

    def __init__(
        self,
        chain: list[str],
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.chain = chain
        super().__init__(
            "Circular inheritance detected in theme chain",
            details=f"Inheritance chain: {' -> '.join(chain)}",
            suggestion="Remove the circular reference in theme 'extends' fields.",
            **kwargs,
        )


# =============================================================================
# Formatting Errors (FT-FMT-800 to FT-FMT-899)
# =============================================================================


class FormattingError(SpreadsheetDLError):
    """Base exception for formatting errors."""

    error_code = "FT-FMT-800"


class InvalidColorError(FormattingError):
    """Raised when a color value is invalid."""

    error_code = "FT-FMT-801"

    def __init__(
        self,
        color: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.color = color
        super().__init__(
            f"Invalid color value: '{color}'",
            context=ErrorContext(value=color, expected="#RRGGBB format"),
            suggestion="Use hex color format: #RRGGBB (e.g., #FF5733).",
            **kwargs,
        )


class InvalidFontError(FormattingError):
    """Raised when a font specification is invalid."""

    error_code = "FT-FMT-802"

    def __init__(
        self,
        font: str,
        reason: str = "Unknown font",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.font = font
        self.reason = reason
        super().__init__(
            f"Invalid font specification: '{font}'",
            details=reason,
            suggestion="Use a common font family name (e.g., 'Arial', 'Liberation Sans').",
            context=ErrorContext(value=font),
            **kwargs,
        )


class InvalidNumberFormatError(FormattingError):
    """Raised when a number format pattern is invalid."""

    error_code = "FT-FMT-803"

    def __init__(
        self,
        pattern: str,
        reason: str = "Invalid pattern",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.pattern = pattern
        self.reason = reason
        super().__init__(
            f"Invalid number format pattern: '{pattern}'",
            details=reason,
            context=ErrorContext(value=pattern, expected="ODS number format pattern"),
            suggestion="Use standard ODS number format (e.g., '#,##0.00').",
            **kwargs,
        )


class LocaleError(FormattingError):
    """Raised when locale configuration is invalid."""

    error_code = "FT-FMT-804"

    def __init__(
        self,
        locale: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.locale = locale
        super().__init__(
            f"Invalid or unsupported locale: '{locale}'",
            suggestion="Use a valid locale code (e.g., 'en_US', 'de_DE').",
            context=ErrorContext(value=locale),
            **kwargs,
        )


# =============================================================================
# Extension/Plugin Errors (FT-EXT-900 to FT-EXT-999)
# =============================================================================


class ExtensionError(SpreadsheetDLError):
    """Base exception for extension/plugin errors."""

    error_code = "FT-EXT-900"


class PluginNotFoundError(ExtensionError):
    """Raised when a plugin is not found."""

    error_code = "FT-EXT-901"

    def __init__(
        self,
        plugin_name: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.plugin_name = plugin_name
        super().__init__(
            f"Plugin '{plugin_name}' not found",
            suggestion="Install the plugin with: pip install spreadsheet-dl-plugin-{name}",
            context=ErrorContext(value=plugin_name),
            **kwargs,
        )


class PluginLoadError(ExtensionError):
    """Raised when loading a plugin fails."""

    error_code = "FT-EXT-902"

    def __init__(
        self,
        plugin_name: str,
        reason: str = "Load failed",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(
            f"Failed to load plugin '{plugin_name}'",
            details=reason,
            suggestion="Check plugin compatibility and dependencies.",
            context=ErrorContext(value=plugin_name),
            **kwargs,
        )


class PluginVersionError(ExtensionError):
    """Raised when plugin version is incompatible."""

    error_code = "FT-EXT-903"

    def __init__(
        self,
        plugin_name: str,
        required_version: str,
        actual_version: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.plugin_name = plugin_name
        self.required_version = required_version
        self.actual_version = actual_version
        super().__init__(
            f"Plugin '{plugin_name}' version mismatch",
            details=f"Required: {required_version}, Found: {actual_version}",
            suggestion=f"Update plugin: pip install --upgrade spreadsheet-dl-plugin-{plugin_name}",
            context=ErrorContext(expected=required_version, actual=actual_version),
            **kwargs,
        )


class HookError(ExtensionError):
    """Raised when a plugin hook fails."""

    error_code = "FT-EXT-904"

    def __init__(
        self,
        hook_name: str,
        plugin_name: str,
        reason: str = "Hook execution failed",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.hook_name = hook_name
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(
            f"Plugin hook '{hook_name}' failed in '{plugin_name}'",
            details=reason,
            suggestion="Check plugin logs or disable the problematic plugin.",
            **kwargs,
        )


# =============================================================================
# Security Errors (FT-SEC-1000 to FT-SEC-1099)
# =============================================================================


class SecurityError(SpreadsheetDLError):
    """Base exception for security-related errors."""

    error_code = "FT-SEC-1000"


class EncryptionError(SecurityError):
    """Raised when encryption operation fails."""

    error_code = "FT-SEC-1001"

    def __init__(
        self,
        message: str = "Encryption failed",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        super().__init__(
            message,
            suggestion="Check that the password is correct and the file is not corrupted.",
            **kwargs,
        )


class DecryptionError(SecurityError):
    """Raised when decryption operation fails."""

    error_code = "FT-SEC-1002"

    def __init__(
        self,
        message: str = "Decryption failed",
        reason: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        details = None
        if reason:
            details = f"Reason: {reason}"
        super().__init__(
            message,
            details=details,
            suggestion="Verify the password is correct. The file may be corrupted or tampered with.",
            **kwargs,
        )


class KeyDerivationError(SecurityError):
    """Raised when key derivation fails."""

    error_code = "FT-SEC-1003"

    def __init__(
        self,
        message: str = "Key derivation failed",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        super().__init__(
            message,
            suggestion="Check system entropy and memory availability.",
            **kwargs,
        )


class IntegrityError(SecurityError):
    """Raised when data integrity check fails."""

    error_code = "FT-SEC-1004"

    def __init__(
        self,
        message: str = "Data integrity check failed",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        super().__init__(
            message,
            suggestion="The file may have been tampered with or corrupted during transfer.",
            **kwargs,
        )


class CredentialError(SecurityError):
    """Raised when credential operations fail."""

    error_code = "FT-SEC-1005"

    def __init__(
        self,
        message: str = "Credential operation failed",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        super().__init__(
            message,
            suggestion="Check that the master password is correct.",
            **kwargs,
        )


class WeakPasswordError(SecurityError):
    """Raised when password does not meet strength requirements."""

    error_code = "FT-SEC-1006"
    severity = ErrorSeverity.WARNING

    def __init__(
        self,
        feedback: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.feedback = feedback or []
        details = None
        if feedback:
            details = "Recommendations:\n" + "\n".join(f"  - {f}" for f in feedback)
        super().__init__(
            "Password does not meet security requirements",
            details=details,
            suggestion="Use a stronger password with at least 12 characters, mixed case, numbers, and symbols.",
            **kwargs,
        )
