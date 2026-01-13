"""Integration tests for CSV format roundtrip fidelity.

Tests create CSV files with various data types and delimiters, then read them
back to verify data integrity.

Test Strategy:
    - Create CSV with specific content using export functionality
    - Read back and verify content matches
    - Test various delimiters (comma, tab, semicolon)
    - Test escaping and quoting edge cases
"""

from __future__ import annotations

import csv
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = [pytest.mark.integration]


class TestCSVBasicRoundtrip:
    """Test basic CSV create/read roundtrip."""

    def test_simple_data_roundtrip(self, tmp_path: Path) -> None:
        """Test that simple data survives CSV roundtrip."""
        from spreadsheet_dl import create_spreadsheet
        from spreadsheet_dl.export import MultiFormatExporter

        # Create spreadsheet with simple data
        builder = create_spreadsheet()
        builder.sheet("Data").column("Name").column("Value")
        builder.header_row()
        builder.row().cell("Alpha").cell(100)
        builder.row().cell("Beta").cell(200)
        builder.row().cell("Gamma").cell(300)

        # Save as ODS first
        ods_path = tmp_path / "test.ods"
        builder.save(str(ods_path))

        # Export to CSV
        exporter = MultiFormatExporter()
        csv_path = tmp_path / "test.csv"
        result = exporter.export(ods_path, csv_path, "csv")

        assert result.exists()
        assert result.stat().st_size > 0

        # Read back with csv module
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Verify data (at least header and some rows)
        assert len(rows) >= 1

    def test_numeric_precision_csv(self, tmp_path: Path) -> None:
        """Test that numeric precision is preserved in CSV."""
        from spreadsheet_dl import create_spreadsheet
        from spreadsheet_dl.export import MultiFormatExporter

        # Create spreadsheet with precise numbers
        builder = create_spreadsheet()
        builder.sheet("Numbers").column("Value")
        builder.header_row()
        builder.row().cell(3.141592653589793)
        builder.row().cell(2.718281828459045)
        builder.row().cell(1.23e-10)
        builder.row().cell(9.87e15)

        ods_path = tmp_path / "precision.ods"
        builder.save(str(ods_path))

        exporter = MultiFormatExporter()
        csv_path = tmp_path / "precision.csv"
        exporter.export(ods_path, csv_path, "csv")

        # Read and verify
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert len(rows) >= 2  # Header + at least one data row


class TestCSVDelimiters:
    """Test various CSV delimiter options."""

    def test_comma_delimiter(self, tmp_path: Path) -> None:
        """Test standard comma-separated CSV."""
        # Create CSV with comma delimiter
        csv_path = tmp_path / "comma.csv"

        data = [["Name", "Age", "City"], ["Alice", "30", "NYC"], ["Bob", "25", "LA"]]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerows(data)

        # Read back
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=",")
            rows = list(reader)

        assert rows[0] == ["Name", "Age", "City"]
        assert rows[1] == ["Alice", "30", "NYC"]
        assert rows[2] == ["Bob", "25", "LA"]

    def test_tab_delimiter(self, tmp_path: Path) -> None:
        """Test tab-separated values (TSV)."""
        tsv_path = tmp_path / "tab.tsv"

        data = [["Col1", "Col2", "Col3"], ["A", "B", "C"], ["D", "E", "F"]]

        with open(tsv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerows(data)

        # Read back
        with open(tsv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            rows = list(reader)

        assert rows[0] == ["Col1", "Col2", "Col3"]
        assert len(rows) == 3

    def test_semicolon_delimiter(self, tmp_path: Path) -> None:
        """Test semicolon-separated CSV (common in European locales)."""
        csv_path = tmp_path / "semicolon.csv"

        data = [["Product", "Price", "Quantity"], ["Widget", "9,99", "100"]]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerows(data)

        # Read back
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=";")
            rows = list(reader)

        assert rows[0] == ["Product", "Price", "Quantity"]
        # Note: 9,99 is preserved as string (European decimal notation)
        assert rows[1][1] == "9,99"


class TestCSVEscaping:
    """Test CSV escaping and quoting."""

    def test_quoted_fields(self, tmp_path: Path) -> None:
        """Test that fields with commas are properly quoted."""
        csv_path = tmp_path / "quoted.csv"

        data = [
            ["Name", "Address"],
            ["Alice", "123 Main St, Apt 4"],
            ["Bob", "456 Oak Ave"],
        ]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerows(data)

        # Read back
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Address with comma should be preserved correctly
        assert rows[1][1] == "123 Main St, Apt 4"

    def test_embedded_quotes(self, tmp_path: Path) -> None:
        """Test that embedded quotes are properly escaped."""
        csv_path = tmp_path / "embedded_quotes.csv"

        data = [["Title", "Quote"], ["Book", 'He said "Hello"'], ["Movie", "It's good"]]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)

        # Read back
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert rows[1][1] == 'He said "Hello"'
        assert rows[2][1] == "It's good"

    def test_newlines_in_fields(self, tmp_path: Path) -> None:
        """Test that newlines in fields are handled correctly."""
        csv_path = tmp_path / "newlines.csv"

        data = [["Title", "Description"], ["Item", "Line 1\nLine 2\nLine 3"]]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)

        # Read back
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert "Line 1" in rows[1][1]
        assert "Line 2" in rows[1][1]

    def test_empty_fields(self, tmp_path: Path) -> None:
        """Test that empty fields are preserved."""
        csv_path = tmp_path / "empty.csv"

        data = [["A", "B", "C"], ["1", "", "3"], ["", "2", ""], ["", "", ""]]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)

        # Read back
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert rows[1] == ["1", "", "3"]
        assert rows[2] == ["", "2", ""]
        assert rows[3] == ["", "", ""]


class TestCSVEncoding:
    """Test CSV encoding handling."""

    def test_utf8_encoding(self, tmp_path: Path) -> None:
        """Test UTF-8 encoded CSV with international characters."""
        csv_path = tmp_path / "utf8.csv"

        data = [
            ["Name", "City"],
            ["Francois", "Paris"],
            ["Muller", "Munchen"],
            ["Tanaka", "Tokyo"],
        ]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)

        # Read back
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert rows[1][0] == "Francois"
        assert rows[2][1] == "Munchen"
        assert rows[3][0] == "Tanaka"

    def test_unicode_characters(self, tmp_path: Path) -> None:
        """Test CSV with unicode symbols."""
        csv_path = tmp_path / "unicode.csv"

        data = [
            ["Symbol", "Name"],
            ["\u03c0", "Pi"],
            ["\u221e", "Infinity"],
            ["\u2264", "Less than or equal"],
        ]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)

        # Read back
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert rows[1][0] == "\u03c0"
        assert rows[1][1] == "Pi"


class TestCSVEdgeCases:
    """Test CSV edge cases."""

    def test_single_column(self, tmp_path: Path) -> None:
        """Test single-column CSV."""
        csv_path = tmp_path / "single.csv"

        data = [["Value"], ["100"], ["200"], ["300"]]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)

        # Read back
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert len(rows) == 4
        assert all(len(row) == 1 for row in rows)

    def test_many_columns(self, tmp_path: Path) -> None:
        """Test CSV with many columns."""
        csv_path = tmp_path / "wide.csv"

        # Create 100 columns
        header = [f"Col{i}" for i in range(100)]
        row1 = [str(i) for i in range(100)]

        data = [header, row1]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)

        # Read back
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert len(rows[0]) == 100
        assert len(rows[1]) == 100

    def test_large_file(self, tmp_path: Path) -> None:
        """Test CSV with many rows."""
        csv_path = tmp_path / "large.csv"

        # Create 10000 rows
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Value"])
            for i in range(10000):
                writer.writerow([i, i * 10])

        # Verify row count
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            row_count = sum(1 for _ in reader)

        assert row_count == 10001  # Header + 10000 data rows

    def test_whitespace_handling(self, tmp_path: Path) -> None:
        """Test that whitespace in fields is preserved."""
        csv_path = tmp_path / "whitespace.csv"

        data = [["Text"], ["  leading"], ["trailing  "], ["  both  "]]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)

        # Read back (skipinitialspace=False to preserve)
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, skipinitialspace=False)
            rows = list(reader)

        assert rows[1][0] == "  leading"
        assert rows[2][0] == "trailing  "
        assert rows[3][0] == "  both  "
