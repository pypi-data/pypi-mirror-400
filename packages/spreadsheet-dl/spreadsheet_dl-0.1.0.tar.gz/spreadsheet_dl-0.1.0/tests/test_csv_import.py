"""Tests for CSV import functionality."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl import (
    BANK_FORMATS,
    CSVImporter,
    ExpenseCategory,
    TransactionCategorizer,
    import_bank_csv,
)

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = [pytest.mark.unit, pytest.mark.requires_files]


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """Create a sample CSV file for testing."""
    csv_content = """Date,Description,Amount
2025-01-15,Whole Foods Market,-125.50
2025-01-16,Shell Gas Station,-45.00
2025-01-17,Netflix Monthly,-15.99
2025-01-18,Starbucks Coffee,-6.50
2025-01-19,Amazon.com,-89.99
2025-01-20,Salary Deposit,3500.00
"""
    csv_file = tmp_path / "transactions.csv"
    csv_file.write_text(csv_content)
    return csv_file


@pytest.fixture
def chase_csv(tmp_path: Path) -> Path:
    """Create a Chase-format CSV file."""
    csv_content = """Posting Date,Description,Amount,Type,Balance
01/15/2025,WHOLE FOODS MARKET,-125.50,DEBIT,1000.00
01/16/2025,SHELL OIL,-45.00,DEBIT,955.00
01/17/2025,NETFLIX.COM,-15.99,DEBIT,939.01
"""
    csv_file = tmp_path / "chase.csv"
    csv_file.write_text(csv_content)
    return csv_file


class TestTransactionCategorizer:
    """Tests for TransactionCategorizer."""

    def test_categorize_groceries(self) -> None:
        """Test grocery categorization."""
        categorizer = TransactionCategorizer()
        assert categorizer.categorize("Whole Foods Market") == ExpenseCategory.GROCERIES
        assert categorizer.categorize("Trader Joe's") == ExpenseCategory.GROCERIES
        assert categorizer.categorize("COSTCO WHOLESALE") == ExpenseCategory.GROCERIES

    def test_categorize_dining(self) -> None:
        """Test dining categorization."""
        categorizer = TransactionCategorizer()
        assert categorizer.categorize("McDonald's") == ExpenseCategory.DINING_OUT
        assert categorizer.categorize("Chipotle Mexican") == ExpenseCategory.DINING_OUT
        assert categorizer.categorize("STARBUCKS") == ExpenseCategory.DINING_OUT

    def test_categorize_transportation(self) -> None:
        """Test transportation categorization."""
        categorizer = TransactionCategorizer()
        assert (
            categorizer.categorize("Shell Gas Station")
            == ExpenseCategory.TRANSPORTATION
        )
        assert categorizer.categorize("UBER TRIP") == ExpenseCategory.TRANSPORTATION
        assert categorizer.categorize("PARKING LOT") == ExpenseCategory.TRANSPORTATION

    def test_categorize_entertainment(self) -> None:
        """Test entertainment/subscription categorization."""
        categorizer = TransactionCategorizer()
        # Entertainment
        result = categorizer.categorize("Netflix Monthly")
        assert result in (ExpenseCategory.ENTERTAINMENT, ExpenseCategory.SUBSCRIPTIONS)

    def test_categorize_default(self) -> None:
        """Test default categorization for unknown merchants."""
        categorizer = TransactionCategorizer()
        assert (
            categorizer.categorize("Unknown Store XYZ") == ExpenseCategory.MISCELLANEOUS
        )

    def test_custom_rule(self) -> None:
        """Test adding custom categorization rules."""
        categorizer = TransactionCategorizer()
        categorizer.add_rule(
            r"my special store",
            ExpenseCategory.GIFTS,
            priority=100,
        )
        assert categorizer.categorize("MY SPECIAL STORE") == ExpenseCategory.GIFTS

    def test_categorize_with_confidence(self) -> None:
        """Test categorization with confidence score."""
        categorizer = TransactionCategorizer()
        category, confidence = categorizer.categorize_with_confidence("Whole Foods")
        assert category == ExpenseCategory.GROCERIES
        assert confidence > 0.5


class TestCSVImporter:
    """Tests for CSVImporter."""

    def test_import_generic_csv(self, sample_csv: Path) -> None:
        """Test importing generic CSV format."""
        importer = CSVImporter("generic")
        entries = importer.import_file(sample_csv)

        assert len(entries) == 5  # 5 expenses (excluding income)
        assert all(e.amount > 0 for e in entries)

    def test_import_filters_income(self, sample_csv: Path) -> None:
        """Test that income is filtered out."""
        importer = CSVImporter("generic")
        entries = importer.import_file(sample_csv, filter_expenses_only=True)

        # Salary should be filtered
        descriptions = [e.description for e in entries]
        assert not any("Salary" in d for d in descriptions)

    def test_import_date_range(self, sample_csv: Path) -> None:
        """Test filtering by date range."""
        importer = CSVImporter("generic")
        entries = importer.import_file(
            sample_csv,
            start_date=date(2025, 1, 16),
            end_date=date(2025, 1, 18),
        )

        assert len(entries) >= 1
        assert all(date(2025, 1, 16) <= e.date <= date(2025, 1, 18) for e in entries)

    def test_detect_format(self, chase_csv: Path) -> None:
        """Test automatic format detection."""
        detected = CSVImporter.detect_format(chase_csv)
        assert detected == "chase"

    def test_bank_formats_exist(self) -> None:
        """Test that expected bank formats are defined."""
        expected = ["chase", "bank_of_america", "capital_one", "generic"]
        for bank in expected:
            assert bank in BANK_FORMATS


class TestImportBankCSV:
    """Tests for import_bank_csv convenience function."""

    def test_auto_detect_and_import(self, sample_csv: Path) -> None:
        """Test auto-detection and import."""
        entries = import_bank_csv(sample_csv, bank="auto")
        assert len(entries) > 0

    def test_explicit_bank_format(self, sample_csv: Path) -> None:
        """Test with explicit bank format."""
        entries = import_bank_csv(sample_csv, bank="generic")
        assert len(entries) > 0
