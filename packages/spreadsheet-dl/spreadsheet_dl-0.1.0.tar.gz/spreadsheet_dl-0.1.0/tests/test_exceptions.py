"""Tests for custom exceptions."""

from __future__ import annotations

import json

import pytest

from spreadsheet_dl.exceptions import (
    AuthenticationError,
    CircularInheritanceError,
    ConfigMigrationError,
    ConfigSchemaError,
    ConfigurationError,
    ConnectionError,
    CSVColumnMissingError,
    CSVEncodingError,
    CSVImportError,
    CSVParseError,
    DownloadError,
    ErrorContext,
    ErrorSeverity,
    ExtensionError,
    FileError,
    FileExistsError,
    FileNotFoundError,
    FilePermissionError,
    FileReadError,
    FileWriteError,
    FormattingError,
    FormulaError,
    HookError,
    InvalidAmountError,
    InvalidCategoryError,
    InvalidColorError,
    InvalidConfigError,
    InvalidDateError,
    InvalidFileFormatError,
    InvalidFontError,
    InvalidNumberFormatError,
    InvalidOdsStructureError,
    InvalidRangeError,
    LocaleError,
    MissingConfigError,
    NotImplementedFeatureError,
    OdsError,
    OdsReadError,
    OdsWriteError,
    OperationCancelledError,
    PluginLoadError,
    PluginNotFoundError,
    PluginVersionError,
    RequiredFieldError,
    ServerError,
    SheetNotFoundError,
    SpreadsheetDLError,
    TemplateError,
    TemplateNotFoundError,
    TemplateValidationError,
    ThemeNotFoundError,
    ThemeValidationError,
    TimeoutError,
    UnknownError,
    UnsupportedBankFormatError,
    UploadError,
    ValidationError,
    WebDAVError,
)

pytestmark = [pytest.mark.unit]


class TestErrorContext:
    """Tests for ErrorContext dataclass."""

    def test_empty_context(self) -> None:
        """Test empty context returns empty dict."""
        ctx = ErrorContext()
        assert ctx.to_dict() == {}

    def test_context_with_file_path(self) -> None:
        """Test context with file path."""
        ctx = ErrorContext(file_path="/path/to/file.ods")
        result = ctx.to_dict()
        assert result["file"] == "/path/to/file.ods"

    def test_context_with_all_fields(self) -> None:
        """Test context with all fields populated."""
        ctx = ErrorContext(
            file_path="/path/to/file.csv",
            line_number=42,
            column=5,
            value="bad_value",
            expected="good_value",
            actual="bad_value",
            extra={"custom": "data"},
        )
        result = ctx.to_dict()
        assert result["file"] == "/path/to/file.csv"
        assert result["line"] == 42
        assert result["column"] == 5
        assert result["value"] == "bad_value"
        assert result["expected"] == "good_value"
        assert result["actual"] == "bad_value"
        assert result["custom"] == "data"


class TestErrorSeverity:
    """Tests for ErrorSeverity enum."""

    def test_severity_values(self) -> None:
        """Test severity enum values."""
        assert ErrorSeverity.ERROR.value == "error"
        assert ErrorSeverity.WARNING.value == "warning"
        assert ErrorSeverity.INFO.value == "info"


class TestSpreadsheetDLError:
    """Tests for base exception class."""

    def test_error_message(self) -> None:
        """Test error message is stored correctly."""
        error = SpreadsheetDLError("Test error message")
        assert error.message == "Test error message"

    def test_default_error_code(self) -> None:
        """Test default error code."""
        error = SpreadsheetDLError("Test")
        assert error.error_code == "FT-GEN-001"

    def test_custom_error_code(self) -> None:
        """Test custom error code override."""
        error = SpreadsheetDLError("Test", error_code="FT-CUSTOM-999")
        assert error.error_code == "FT-CUSTOM-999"

    def test_error_with_details(self) -> None:
        """Test error with details."""
        error = SpreadsheetDLError("Test", details="More information here")
        assert error.details == "More information here"

    def test_error_with_suggestion(self) -> None:
        """Test error with suggestion."""
        error = SpreadsheetDLError("Test", suggestion="Try this instead")
        assert error.suggestion == "Try this instead"

    def test_error_with_context(self) -> None:
        """Test error with context."""
        ctx = ErrorContext(file_path="/test.ods")
        error = SpreadsheetDLError("Test", context=ctx)
        assert error.context.file_path == "/test.ods"

    def test_doc_url(self) -> None:
        """Test documentation URL generation."""
        error = SpreadsheetDLError("Test")
        # Anchor is lowercase for GitHub markdown links
        assert "ft-gen-001" in error.doc_url

    def test_format_error_no_color(self) -> None:
        """Test error formatting without colors."""
        error = SpreadsheetDLError(
            "Test message",
            details="Some details",
            suggestion="Try this",
        )
        formatted = error.format_error(use_color=False)
        assert "Error [FT-GEN-001]" in formatted
        assert "Test message" in formatted
        assert "Some details" in formatted
        assert "Try this" in formatted

    def test_format_error_with_color(self) -> None:
        """Test error formatting with colors."""
        error = SpreadsheetDLError("Test message")
        formatted = error.format_error(use_color=True)
        # Should contain ANSI escape codes
        assert "\033[" in formatted

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        error = SpreadsheetDLError(
            "Test message",
            details="Details here",
            suggestion="Suggestion here",
        )
        result = error.to_dict()
        assert result["error_code"] == "FT-GEN-001"
        assert result["severity"] == "error"
        assert result["message"] == "Test message"
        assert result["details"] == "Details here"
        assert result["suggestion"] == "Suggestion here"

    def test_to_dict_is_json_serializable(self) -> None:
        """Test that to_dict output is JSON serializable."""
        error = SpreadsheetDLError(
            "Test message",
            context=ErrorContext(file_path="/test.ods", line_number=10),
        )
        # Should not raise
        json_str = json.dumps(error.to_dict())
        assert "FT-GEN-001" in json_str

    def test_str_method(self) -> None:
        """Test __str__ returns formatted error."""
        error = SpreadsheetDLError("Test message")
        str_output = str(error)
        assert "Error [FT-GEN-001]" in str_output
        assert "Test message" in str_output


class TestGeneralErrors:
    """Tests for general error classes."""

    def test_unknown_error(self) -> None:
        """Test UnknownError."""
        error = UnknownError()
        assert error.error_code == "FT-GEN-001"
        assert "unexpected" in error.message.lower()

    def test_unknown_error_with_original(self) -> None:
        """Test UnknownError with original exception."""
        original = ValueError("Original error")
        error = UnknownError("Wrapped error", original_error=original)
        assert error.original_error == original
        assert "Original error" in error.message

    def test_operation_cancelled(self) -> None:
        """Test OperationCancelledError."""
        error = OperationCancelledError("Upload")
        assert error.error_code == "FT-GEN-002"
        assert error.severity == ErrorSeverity.INFO
        assert "Upload" in error.message

    def test_not_implemented_feature(self) -> None:
        """Test NotImplementedFeatureError."""
        error = NotImplementedFeatureError("AI analysis")
        assert error.error_code == "FT-GEN-003"
        assert error.feature == "AI analysis"


class TestFileErrors:
    """Tests for file-related exception classes."""

    def test_file_not_found(self) -> None:
        """Test FileNotFoundError."""
        error = FileNotFoundError("/path/to/missing.ods", file_type="Budget file")
        assert error.error_code == "FT-FILE-101"
        assert error.file_path == "/path/to/missing.ods"
        assert "Budget file" in error.message

    def test_file_permission_error(self) -> None:
        """Test FilePermissionError."""
        error = FilePermissionError("/path/to/file.ods", operation="write")
        assert error.error_code == "FT-FILE-102"
        assert error.file_path == "/path/to/file.ods"
        assert error.operation == "write"

    def test_file_exists_error(self) -> None:
        """Test FileExistsError."""
        error = FileExistsError("/path/to/existing.ods")
        assert error.error_code == "FT-FILE-103"
        assert error.severity == ErrorSeverity.WARNING
        assert error.file_path == "/path/to/existing.ods"

    def test_invalid_file_format_error(self) -> None:
        """Test InvalidFileFormatError."""
        error = InvalidFileFormatError(
            "/path/to/file.txt", expected_format="ODS", actual_format="TXT"
        )
        assert error.error_code == "FT-FILE-104"
        assert error.expected_format == "ODS"
        assert error.actual_format == "TXT"

    def test_file_write_error(self) -> None:
        """Test FileWriteError."""
        error = FileWriteError("/path/to/file.ods", reason="Disk full")
        assert error.error_code == "FT-FILE-105"
        assert error.reason == "Disk full"

    def test_file_read_error(self) -> None:
        """Test FileReadError."""
        error = FileReadError("/path/to/file.ods", reason="File corrupted")
        assert error.error_code == "FT-FILE-106"
        assert error.reason == "File corrupted"


class TestOdsErrors:
    """Tests for ODS exception classes."""

    def test_ods_read_error(self) -> None:
        """Test OdsReadError."""
        error = OdsReadError("/path/to/budget.ods", reason="Invalid ZIP archive")
        assert error.error_code == "FT-ODS-201"
        assert error.file_path == "/path/to/budget.ods"
        assert error.reason == "Invalid ZIP archive"

    def test_ods_write_error(self) -> None:
        """Test OdsWriteError."""
        error = OdsWriteError("/path/to/budget.ods", reason="Permission denied")
        assert error.error_code == "FT-ODS-202"

    def test_sheet_not_found_error(self) -> None:
        """Test SheetNotFoundError."""
        error = SheetNotFoundError("Missing Sheet", ["Sheet1", "Sheet2"])
        assert error.error_code == "FT-ODS-203"
        assert error.sheet_name == "Missing Sheet"
        assert "Sheet1" in error.available_sheets
        assert error.details is not None
        assert "Sheet1" in error.details

    def test_sheet_not_found_error_no_available(self) -> None:
        """Test SheetNotFoundError without available sheets."""
        error = SheetNotFoundError("Missing Sheet")
        assert error.available_sheets == []

    def test_invalid_ods_structure(self) -> None:
        """Test InvalidOdsStructureError."""
        error = InvalidOdsStructureError(
            "/path/to/file.ods", issue="Missing Expense Log sheet"
        )
        assert error.error_code == "FT-ODS-204"
        assert error.issue == "Missing Expense Log sheet"

    def test_formula_error(self) -> None:
        """Test FormulaError."""
        error = FormulaError("=SUM(A1:A", reason="Unclosed parenthesis", cell="B10")
        assert error.error_code == "FT-ODS-205"
        assert error.formula == "=SUM(A1:A"
        assert error.cell == "B10"


class TestCSVImportErrors:
    """Tests for CSV import exception classes."""

    def test_csv_parse_error(self) -> None:
        """Test CSVParseError."""
        error = CSVParseError(
            "Unterminated quote", file_path="/path/to/file.csv", line_number=42
        )
        assert error.error_code == "FT-CSV-301"
        assert error.line_number == 42
        assert "line 42" in error.message

    def test_csv_parse_error_no_line(self) -> None:
        """Test CSVParseError without line number."""
        error = CSVParseError("General error")
        assert error.line_number is None
        assert "line" not in error.message.lower()

    def test_unsupported_bank_format_error(self) -> None:
        """Test UnsupportedBankFormatError."""
        error = UnsupportedBankFormatError(
            "MyBank", ["chase", "bank_of_america", "wells_fargo"]
        )
        assert error.error_code == "FT-CSV-302"
        assert error.severity == ErrorSeverity.WARNING
        assert error.bank == "MyBank"
        assert "chase" in error.supported_banks

    def test_csv_column_missing(self) -> None:
        """Test CSVColumnMissingError."""
        error = CSVColumnMissingError(
            "Amount", available_columns=["Date", "Description", "Balance"]
        )
        assert error.error_code == "FT-CSV-303"
        assert error.column_name == "Amount"
        assert "Date" in error.available_columns

    def test_csv_encoding_error(self) -> None:
        """Test CSVEncodingError."""
        error = CSVEncodingError("/path/to/file.csv", detected_encoding="windows-1252")
        assert error.error_code == "FT-CSV-304"
        assert error.detected_encoding == "windows-1252"


class TestValidationErrors:
    """Tests for validation exception classes."""

    def test_invalid_amount_error(self) -> None:
        """Test InvalidAmountError."""
        error = InvalidAmountError("abc123", "Not a valid number")
        assert error.error_code == "FT-VAL-401"
        assert error.value == "abc123"
        assert error.reason == "Not a valid number"

    def test_invalid_date_error(self) -> None:
        """Test InvalidDateError."""
        error = InvalidDateError("13-2025-01")
        assert error.error_code == "FT-VAL-402"
        assert error.value == "13-2025-01"
        assert error.context.expected is not None
        assert "YYYY-MM-DD" in error.context.expected

    def test_invalid_date_error_custom_format(self) -> None:
        """Test InvalidDateError with custom format."""
        error = InvalidDateError("bad-date", expected_format="DD/MM/YYYY")
        assert error.expected_format == "DD/MM/YYYY"

    def test_invalid_category_error(self) -> None:
        """Test InvalidCategoryError."""
        error = InvalidCategoryError(
            "NotACategory", ["Groceries", "Housing", "Utilities"]
        )
        assert error.error_code == "FT-VAL-403"
        assert error.category == "NotACategory"
        assert "Groceries" in error.valid_categories

    def test_invalid_range_error(self) -> None:
        """Test InvalidRangeError."""
        error = InvalidRangeError("month", 15, min_value=1, max_value=12)
        assert error.error_code == "FT-VAL-404"
        assert error.field == "month"
        assert error.value == 15
        assert "between 1 and 12" in error.message

    def test_required_field_error(self) -> None:
        """Test RequiredFieldError."""
        error = RequiredFieldError("amount")
        assert error.error_code == "FT-VAL-405"
        assert error.field == "amount"


class TestConfigurationErrors:
    """Tests for configuration exception classes."""

    def test_missing_config_error(self) -> None:
        """Test MissingConfigError."""
        error = MissingConfigError("NEXTCLOUD_URL", "environment")
        assert error.error_code == "FT-CFG-501"
        assert error.config_key == "NEXTCLOUD_URL"
        assert error.config_source == "environment"

    def test_invalid_config_error(self) -> None:
        """Test InvalidConfigError."""
        error = InvalidConfigError(
            "threshold", "abc", reason="Must be numeric", expected="float"
        )
        assert error.error_code == "FT-CFG-502"
        assert error.config_key == "threshold"
        assert error.value == "abc"

    def test_config_schema_error(self) -> None:
        """Test ConfigSchemaError."""
        error = ConfigSchemaError(
            "/path/to/config.yaml",
            errors=["Missing required field: nextcloud.url", "Invalid type for alerts"],
        )
        assert error.error_code == "FT-CFG-503"
        assert len(error.errors) == 2

    def test_config_migration_error(self) -> None:
        """Test ConfigMigrationError."""
        error = ConfigMigrationError("1.0", "2.0", "Incompatible schema")
        assert error.error_code == "FT-CFG-504"
        assert error.from_version == "1.0"
        assert error.to_version == "2.0"


class TestNetworkErrors:
    """Tests for network/WebDAV exception classes."""

    def test_connection_error(self) -> None:
        """Test ConnectionError."""
        error = ConnectionError(
            "https://cloud.example.com", reason="DNS resolution failed"
        )
        assert error.error_code == "FT-NET-601"
        assert error.url == "https://cloud.example.com"
        assert error.reason == "DNS resolution failed"

    def test_authentication_error(self) -> None:
        """Test AuthenticationError."""
        error = AuthenticationError(url="https://cloud.example.com")
        assert error.error_code == "FT-NET-602"
        assert error.url == "https://cloud.example.com"

    def test_upload_error(self) -> None:
        """Test UploadError."""
        error = UploadError(
            "/local/file.ods", "/remote/path/file.ods", reason="Quota exceeded"
        )
        assert error.error_code == "FT-NET-603"
        assert error.file_path == "/local/file.ods"
        assert error.remote_path == "/remote/path/file.ods"

    def test_download_error(self) -> None:
        """Test DownloadError."""
        error = DownloadError("/remote/file.ods", reason="File not found")
        assert error.error_code == "FT-NET-604"
        assert error.remote_path == "/remote/file.ods"

    def test_server_error(self) -> None:
        """Test ServerError."""
        error = ServerError(500, "Internal Server Error")
        assert error.error_code == "FT-NET-605"
        assert error.status_code == 500

    def test_timeout_error(self) -> None:
        """Test TimeoutError."""
        error = TimeoutError("Upload", timeout_seconds=30)
        assert error.error_code == "FT-NET-606"
        assert error.operation == "Upload"
        assert "30 seconds" in error.message


class TestTemplateErrors:
    """Tests for template exception classes."""

    def test_template_not_found_error(self) -> None:
        """Test TemplateNotFoundError."""
        error = TemplateNotFoundError(
            "my_template", ["50_30_20", "family", "minimalist"]
        )
        assert error.error_code == "FT-TMPL-701"
        assert error.template_name == "my_template"
        assert "50_30_20" in error.available_templates

    def test_template_validation_error(self) -> None:
        """Test TemplateValidationError."""
        error = TemplateValidationError(
            "custom_template", errors=["Missing allocations", "Invalid category"]
        )
        assert error.error_code == "FT-TMPL-702"
        assert error.template_name == "custom_template"
        assert len(error.errors) == 2

    def test_theme_not_found_error(self) -> None:
        """Test ThemeNotFoundError."""
        error = ThemeNotFoundError("my_theme", ["default", "corporate", "minimal"])
        assert error.error_code == "FT-TMPL-703"
        assert error.theme_name == "my_theme"
        assert "default" in error.available_themes

    def test_theme_validation_error(self) -> None:
        """Test ThemeValidationError."""
        error = ThemeValidationError(
            "/path/to/theme.yaml",
            errors=["Invalid color: #GGG", "Missing required: meta.name"],
            line_number=15,
        )
        assert error.error_code == "FT-TMPL-704"
        assert error.theme_path == "/path/to/theme.yaml"
        assert len(error.errors) == 2

    def test_circular_inheritance_error(self) -> None:
        """Test CircularInheritanceError."""
        error = CircularInheritanceError(["theme_a", "theme_b", "theme_c", "theme_a"])
        assert error.error_code == "FT-TMPL-705"
        assert error.chain == ["theme_a", "theme_b", "theme_c", "theme_a"]


class TestFormattingErrors:
    """Tests for formatting exception classes."""

    def test_invalid_color_error(self) -> None:
        """Test InvalidColorError."""
        error = InvalidColorError("#GGG")
        assert error.error_code == "FT-FMT-801"
        assert error.color == "#GGG"

    def test_invalid_font_error(self) -> None:
        """Test InvalidFontError."""
        error = InvalidFontError("NonExistentFont", reason="Font not installed")
        assert error.error_code == "FT-FMT-802"
        assert error.font == "NonExistentFont"

    def test_invalid_number_format_error(self) -> None:
        """Test InvalidNumberFormatError."""
        error = InvalidNumberFormatError("###.##.##", reason="Invalid pattern")
        assert error.error_code == "FT-FMT-803"
        assert error.pattern == "###.##.##"

    def test_locale_error(self) -> None:
        """Test LocaleError."""
        error = LocaleError("xx_XX")
        assert error.error_code == "FT-FMT-804"
        assert error.locale == "xx_XX"


class TestExtensionErrors:
    """Tests for extension/plugin exception classes."""

    def test_plugin_not_found_error(self) -> None:
        """Test PluginNotFoundError."""
        error = PluginNotFoundError("my-plugin")
        assert error.error_code == "FT-EXT-901"
        assert error.plugin_name == "my-plugin"

    def test_plugin_load_error(self) -> None:
        """Test PluginLoadError."""
        error = PluginLoadError("my-plugin", reason="Missing dependency: pandas")
        assert error.error_code == "FT-EXT-902"
        assert error.plugin_name == "my-plugin"
        assert error.reason == "Missing dependency: pandas"

    def test_plugin_version_error(self) -> None:
        """Test PluginVersionError."""
        error = PluginVersionError(
            "my-plugin", required_version="2.0", actual_version="1.5"
        )
        assert error.error_code == "FT-EXT-903"
        assert error.plugin_name == "my-plugin"
        assert error.required_version == "2.0"
        assert error.actual_version == "1.5"

    def test_hook_error(self) -> None:
        """Test HookError."""
        error = HookError("on_expense_added", "my-plugin", reason="TypeError in hook")
        assert error.error_code == "FT-EXT-904"
        assert error.hook_name == "on_expense_added"
        assert error.plugin_name == "my-plugin"


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""

    def test_file_error_is_spreadsheet_dl_error(self) -> None:
        """Test FileError inherits from SpreadsheetDLError."""
        assert issubclass(FileError, SpreadsheetDLError)

    def test_ods_error_is_spreadsheet_dl_error(self) -> None:
        """Test OdsError inherits from SpreadsheetDLError."""
        assert issubclass(OdsError, SpreadsheetDLError)

    def test_validation_error_is_spreadsheet_dl_error(self) -> None:
        """Test ValidationError inherits from SpreadsheetDLError."""
        assert issubclass(ValidationError, SpreadsheetDLError)

    def test_csv_import_error_is_spreadsheet_dl_error(self) -> None:
        """Test CSVImportError inherits from SpreadsheetDLError."""
        assert issubclass(CSVImportError, SpreadsheetDLError)

    def test_webdav_error_is_spreadsheet_dl_error(self) -> None:
        """Test WebDAVError inherits from SpreadsheetDLError."""
        assert issubclass(WebDAVError, SpreadsheetDLError)

    def test_configuration_error_is_spreadsheet_dl_error(self) -> None:
        """Test ConfigurationError inherits from SpreadsheetDLError."""
        assert issubclass(ConfigurationError, SpreadsheetDLError)

    def test_template_error_is_spreadsheet_dl_error(self) -> None:
        """Test TemplateError inherits from SpreadsheetDLError."""
        assert issubclass(TemplateError, SpreadsheetDLError)

    def test_formatting_error_is_spreadsheet_dl_error(self) -> None:
        """Test FormattingError inherits from SpreadsheetDLError."""
        assert issubclass(FormattingError, SpreadsheetDLError)

    def test_extension_error_is_spreadsheet_dl_error(self) -> None:
        """Test ExtensionError inherits from SpreadsheetDLError."""
        assert issubclass(ExtensionError, SpreadsheetDLError)

    def test_ods_read_error_is_ods_error(self) -> None:
        """Test OdsReadError inherits from OdsError."""
        assert issubclass(OdsReadError, OdsError)

    def test_can_catch_base_exception(self) -> None:
        """Test catching SpreadsheetDLError catches all subclasses."""
        errors = [
            FileError("test"),
            OdsError("test"),
            ValidationError("test"),
            CSVImportError("test"),
            WebDAVError("test"),
            ConfigurationError("test"),
            TemplateError("test"),
            FormattingError("test"),
            ExtensionError("test"),
        ]

        for error in errors:
            try:
                raise error
            except SpreadsheetDLError as e:
                assert e.message == "test"


class TestErrorCodeUniqueness:
    """Tests to ensure all error codes are unique."""

    def test_all_error_codes_are_unique(self) -> None:
        """Test that concrete exception classes have unique error codes.

        Note: Base exception classes may share codes with their primary concrete subclass.
        For example, UnknownError is the concrete representation of the base error type.
        """
        # Only test concrete (leaf) exception classes that should have unique codes
        # Exclude abstract base classes that may share codes with their concrete subclasses
        exception_classes = [
            # General errors (UnknownError uses FT-GEN-001 same as base, which is by design)
            OperationCancelledError,
            NotImplementedFeatureError,
            # File errors (concrete leaf classes only)
            FileNotFoundError,
            FilePermissionError,
            FileExistsError,
            InvalidFileFormatError,
            FileWriteError,
            FileReadError,
            # ODS errors
            OdsReadError,
            OdsWriteError,
            SheetNotFoundError,
            InvalidOdsStructureError,
            FormulaError,
            # CSV errors
            CSVParseError,
            UnsupportedBankFormatError,
            CSVColumnMissingError,
            CSVEncodingError,
            # Validation errors
            InvalidAmountError,
            InvalidDateError,
            InvalidCategoryError,
            InvalidRangeError,
            RequiredFieldError,
            # Configuration errors
            MissingConfigError,
            InvalidConfigError,
            ConfigSchemaError,
            ConfigMigrationError,
            # Network errors
            ConnectionError,
            AuthenticationError,
            UploadError,
            DownloadError,
            ServerError,
            TimeoutError,
            # Template errors
            TemplateNotFoundError,
            TemplateValidationError,
            ThemeNotFoundError,
            ThemeValidationError,
            CircularInheritanceError,
            # Formatting errors
            InvalidColorError,
            InvalidFontError,
            InvalidNumberFormatError,
            LocaleError,
            # Extension errors
            PluginNotFoundError,
            PluginLoadError,
            PluginVersionError,
            HookError,
        ]

        codes = set()
        duplicates = []

        for cls in exception_classes:
            # Access class attribute directly, not instance
            code = cls.error_code  # type: ignore[attr-defined]
            if code in codes:
                duplicates.append((cls.__name__, code))
            codes.add(code)

        assert not duplicates, f"Duplicate error codes found: {duplicates}"

    def test_error_codes_follow_format(self) -> None:
        """Test that all error codes follow FT-XXX-NNN format."""
        import re

        pattern = re.compile(r"^FT-[A-Z]{2,4}-\d{3}$")

        exception_classes = [
            FileNotFoundError,
            InvalidAmountError,
            CSVParseError,
            MissingConfigError,
            ConnectionError,
            TemplateNotFoundError,
            InvalidColorError,
            PluginNotFoundError,
        ]

        for cls in exception_classes:
            # Access class attribute directly, not instance
            code = cls.error_code  # type: ignore[attr-defined]
            assert pattern.match(code), (
                f"{cls.__name__} has invalid error code format: {code}"
            )
