"""
Tests for Extended Bank Format Support.

: Extended Bank Formats
"""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import pytest

from spreadsheet_dl import (
    BUILTIN_FORMATS,
    BankFormatDefinition,
    BankFormatRegistry,
    FormatBuilder,
    count_formats,
    detect_format,
    get_format,
    list_formats,
)

pytestmark = [pytest.mark.unit, pytest.mark.finance]


class TestBankFormatDefinition:
    """Tests for BankFormatDefinition."""

    def test_create_format(self) -> None:
        """Test creating a format definition."""
        fmt = BankFormatDefinition(
            id="test_bank",
            name="Test Bank",
            institution="Test",
            date_column="Date",
            amount_column="Amount",
            description_column="Description",
        )

        assert fmt.id == "test_bank"
        assert fmt.name == "Test Bank"
        assert fmt.date_column == "Date"

    def test_to_dict(self) -> None:
        """Test serialization to dict."""
        fmt = BankFormatDefinition(
            id="test",
            name="Test",
            institution="Test Bank",
            date_format="%Y-%m-%d",
        )

        data = fmt.to_dict()

        assert data["id"] == "test"
        assert data["name"] == "Test"
        assert data["institution"] == "Test Bank"
        assert data["date_format"] == "%Y-%m-%d"

    def test_from_dict(self) -> None:
        """Test deserialization from dict."""
        data = {
            "id": "test",
            "name": "Test Format",
            "institution": "Test Bank",
            "date_column": "Trans Date",
            "date_format": "%m/%d/%Y",
            "amount_column": "Amount",
            "description_column": "Payee",
            "expense_is_negative": False,
        }

        fmt = BankFormatDefinition.from_dict(data)

        assert fmt.id == "test"
        assert fmt.date_column == "Trans Date"
        assert fmt.date_format == "%m/%d/%Y"
        assert not fmt.expense_is_negative

    def test_to_yaml(self) -> None:
        """Test YAML export."""
        fmt = BankFormatDefinition(
            id="test",
            name="Test",
            institution="Test Bank",
            header_patterns=["date", "amount"],
        )

        yaml_str = fmt.to_yaml()

        assert "id: test" in yaml_str
        assert "name: Test" in yaml_str
        assert "institution: Test Bank" in yaml_str
        assert "header_patterns:" in yaml_str

    def test_default_values(self) -> None:
        """Test default values are set correctly."""
        fmt = BankFormatDefinition(id="test", name="Test")

        assert fmt.format_type == "checking"
        assert fmt.date_format == "%m/%d/%Y"
        assert fmt.encoding == "utf-8-sig"
        assert fmt.delimiter == ","
        assert fmt.expense_is_negative is True
        assert fmt.skip_rows == 0


class TestBuiltinFormats:
    """Tests for built-in format definitions."""

    def test_minimum_format_count(self) -> None:
        """Test we have at least 50 formats."""
        assert len(BUILTIN_FORMATS) >= 50

    def test_major_banks_included(self) -> None:
        """Test major banks are included."""
        major_banks = [
            "chase_checking",
            "chase_credit",
            "bank_of_america_checking",
            "wells_fargo_checking",
            "citi_checking",
            "capital_one_checking",
            "amex",
            "discover_credit",
        ]

        for bank_id in major_banks:
            assert bank_id in BUILTIN_FORMATS, f"Missing format: {bank_id}"

    def test_fintechs_included(self) -> None:
        """Test fintech banks are included."""
        fintechs = ["ally_bank", "chime", "sofi", "wealthfront"]

        for fintech_id in fintechs:
            assert fintech_id in BUILTIN_FORMATS, f"Missing format: {fintech_id}"

    def test_payment_services_included(self) -> None:
        """Test payment services are included."""
        services = ["paypal", "venmo", "cashapp", "apple_card"]

        for service_id in services:
            assert service_id in BUILTIN_FORMATS, f"Missing format: {service_id}"

    def test_all_formats_valid(self) -> None:
        """Test all formats have required fields."""
        for format_id, fmt in BUILTIN_FORMATS.items():
            assert fmt.id == format_id, f"ID mismatch for {format_id}"
            assert fmt.name, f"Missing name for {format_id}"
            assert fmt.date_column, f"Missing date_column for {format_id}"
            assert fmt.date_format, f"Missing date_format for {format_id}"
            assert fmt.description_column, f"Missing description_column for {format_id}"

            # Either single amount column or debit/credit columns
            if not fmt.debit_column:
                assert fmt.amount_column, f"Missing amount_column for {format_id}"


class TestBankFormatRegistry:
    """Tests for BankFormatRegistry."""

    def test_get_builtin_format(self) -> None:
        """Test getting a built-in format."""
        registry = BankFormatRegistry()

        fmt = registry.get_format("chase_checking")

        assert fmt is not None
        assert fmt.institution == "Chase"

    def test_get_nonexistent_format(self) -> None:
        """Test getting a non-existent format."""
        registry = BankFormatRegistry()

        fmt = registry.get_format("nonexistent")

        assert fmt is None

    def test_list_all_formats(self) -> None:
        """Test listing all formats."""
        registry = BankFormatRegistry()

        formats = registry.list_formats()

        assert len(formats) >= 50

    def test_list_formats_by_institution(self) -> None:
        """Test filtering by institution."""
        registry = BankFormatRegistry()

        chase_formats = registry.list_formats(institution="Chase")

        assert len(chase_formats) >= 2
        for fmt in chase_formats:
            assert "chase" in fmt.institution.lower()

    def test_list_formats_by_type(self) -> None:
        """Test filtering by format type."""
        registry = BankFormatRegistry()

        credit_formats = registry.list_formats(format_type="credit")

        assert len(credit_formats) >= 5
        for fmt in credit_formats:
            assert fmt.format_type == "credit"

    def test_list_institutions(self) -> None:
        """Test listing unique institutions."""
        registry = BankFormatRegistry()

        institutions = registry.list_institutions()

        assert "Chase" in institutions
        assert "Bank of America" in institutions
        assert len(institutions) >= 20

    def test_add_custom_format(self) -> None:
        """Test adding a custom format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = BankFormatRegistry(custom_dir=tmpdir)

            custom = BankFormatDefinition(
                id="my_bank",
                name="My Bank",
                institution="My Bank",
                date_column="Trans Date",
                amount_column="Amount",
                description_column="Details",
            )

            registry.add_custom_format(custom)

            # Should be retrievable
            retrieved = registry.get_format("my_bank")
            assert retrieved is not None
            assert retrieved.name == "My Bank"

            # Should persist
            registry2 = BankFormatRegistry(custom_dir=tmpdir)
            retrieved2 = registry2.get_format("my_bank")
            assert retrieved2 is not None

    def test_remove_custom_format(self) -> None:
        """Test removing a custom format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = BankFormatRegistry(custom_dir=tmpdir)

            custom = BankFormatDefinition(
                id="temp_bank",
                name="Temp Bank",
            )
            registry.add_custom_format(custom)

            result = registry.remove_custom_format("temp_bank")
            assert result is True
            assert registry.get_format("temp_bank") is None

    def test_custom_overrides_builtin(self) -> None:
        """Test custom format overrides built-in."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = BankFormatRegistry(custom_dir=tmpdir)

            # Override chase_checking
            custom = BankFormatDefinition(
                id="chase_checking",
                name="My Custom Chase",
                institution="Chase",
            )
            registry.add_custom_format(custom)

            fmt = registry.get_format("chase_checking")
            assert fmt is not None
            assert fmt.name == "My Custom Chase"

    def test_detect_format_chase(self) -> None:
        """Test format detection for Chase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "chase.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["Posting Date", "Description", "Amount", "Type", "Balance"]
                )
                writer.writerow(
                    ["01/15/2024", "COFFEE SHOP", "-5.00", "Debit", "1000.00"]
                )

            registry = BankFormatRegistry()
            detected = registry.detect_format(csv_path)

            assert detected is not None
            assert "chase" in detected.id.lower()

    def test_detect_format_capital_one(self) -> None:
        """Test format detection for Capital One."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "capital_one.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["Transaction Date", "Transaction Description", "Debit", "Credit"]
                )
                writer.writerow(["2024-01-15", "PURCHASE", "50.00", ""])

            registry = BankFormatRegistry()
            detected = registry.detect_format(csv_path)

            assert detected is not None
            assert (
                "capital" in detected.id.lower()
                or "capital" in detected.institution.lower()
            )

    def test_validate_format(self) -> None:
        """Test format validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Amount", "Description"])
                writer.writerow(["2024-01-15", "-50.00", "Test"])

            registry = BankFormatRegistry()
            fmt = registry.get_format("generic")
            assert fmt is not None

            errors = registry.validate_format(fmt, csv_path)
            assert len(errors) == 0

    def test_validate_format_missing_columns(self) -> None:
        """Test validation with missing columns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Value"])  # Missing Description
                writer.writerow(["2024-01-15", "-50.00"])

            registry = BankFormatRegistry()
            fmt = BankFormatDefinition(
                id="test",
                name="Test",
                date_column="Date",
                amount_column="Amount",
                description_column="Description",
            )

            errors = registry.validate_format(fmt, csv_path)
            assert len(errors) >= 2  # Missing Amount and Description

    def test_iteration(self) -> None:
        """Test iterating over formats."""
        registry = BankFormatRegistry()

        count = 0
        for fmt in registry:
            assert isinstance(fmt, BankFormatDefinition)
            count += 1

        assert count >= 50

    def test_len(self) -> None:
        """Test format count."""
        registry = BankFormatRegistry()

        assert len(registry) >= 50


class TestFormatBuilder:
    """Tests for FormatBuilder."""

    def test_build_simple_format(self) -> None:
        """Test building a simple format."""
        builder = FormatBuilder()
        builder.set_institution("Test Bank")
        builder.set_date_column("Date", "%Y-%m-%d")
        builder.set_amount_column("Amount")
        builder.set_description_column("Description")

        fmt = builder.build("test_format")

        assert fmt.id == "test_format"
        assert fmt.institution == "Test Bank"
        assert fmt.date_column == "Date"
        assert fmt.date_format == "%Y-%m-%d"

    def test_build_with_debit_credit(self) -> None:
        """Test building format with debit/credit columns."""
        builder = FormatBuilder()
        builder.set_institution("Bank")
        builder.set_debit_credit_columns("Debit", "Credit")
        builder.set_description_column("Description")

        fmt = builder.build("test")

        assert fmt.debit_column == "Debit"
        assert fmt.credit_column == "Credit"
        assert not fmt.expense_is_negative

    def test_chaining(self) -> None:
        """Test method chaining."""
        fmt = (
            FormatBuilder()
            .set_institution("Bank")
            .set_name("My Bank Format")
            .set_format_type("credit")
            .set_date_column("Trans Date", "%m/%d/%Y")
            .set_amount_column("Amount")
            .set_description_column("Merchant")
            .set_category_column("Category")
            .set_memo_column("Notes")
            .add_header_pattern("trans date")
            .add_header_pattern("merchant")
            .set_notes("Custom format for my credit card")
            .build("my_credit_card")
        )

        assert fmt.id == "my_credit_card"
        assert fmt.name == "My Bank Format"
        assert fmt.format_type == "credit"
        assert len(fmt.header_patterns) == 2

    def test_from_csv_headers(self) -> None:
        """Test inferring format from CSV headers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "sample.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "Transaction Date",
                        "Description",
                        "Debit",
                        "Credit",
                        "Balance",
                        "Category",
                    ]
                )
                writer.writerow(
                    [
                        "2024-01-15",
                        "Coffee Shop",
                        "5.00",
                        "",
                        "1000.00",
                        "Dining",
                    ]
                )

            builder = FormatBuilder()
            builder.from_csv_headers(csv_path)

            fmt = builder.build("inferred")

            assert fmt.date_column == "Transaction Date"
            assert fmt.description_column == "Description"
            assert fmt.debit_column == "Debit"
            assert fmt.credit_column == "Credit"
            assert fmt.balance_column == "Balance"
            assert fmt.category_column == "Category"

    def test_auto_name(self) -> None:
        """Test automatic name generation."""
        fmt = (
            FormatBuilder()
            .set_institution("My Bank")
            .set_format_type("checking")
            .build("my_bank")
        )

        assert fmt.name == "My Bank - Checking"


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_get_format(self) -> None:
        """Test get_format function."""
        fmt = get_format("chase_checking")

        assert fmt is not None
        assert fmt.institution == "Chase"

    def test_list_formats(self) -> None:
        """Test list_formats function."""
        formats = list_formats()

        assert len(formats) >= 50

    def test_list_formats_filtered(self) -> None:
        """Test list_formats with filters."""
        credit_formats = list_formats(format_type="credit")

        assert len(credit_formats) >= 5
        for fmt in credit_formats:
            assert fmt.format_type == "credit"

    def test_detect_format(self) -> None:
        """Test detect_format function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Description", "Amount"])
                writer.writerow(["2024-01-15", "Test", "-50.00"])

            detected = detect_format(csv_path)

            # Should detect generic or similar
            assert detected is not None

    def test_count_formats(self) -> None:
        """Test count_formats function."""
        count = count_formats()

        assert count >= 50
