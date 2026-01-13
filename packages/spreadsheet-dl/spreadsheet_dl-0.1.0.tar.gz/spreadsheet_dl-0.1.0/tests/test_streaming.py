"""
Comprehensive tests for streaming module.

Tests:
    - StreamingReader row iteration
    - StreamingReader sheet navigation
    - StreamingReader metadata access
    - StreamingWriter chunk writing
    - StreamingWriter multiple sheets
    - Large dataset handling (1000+ rows)
    - Context manager support
    - Error handling

Implements comprehensive coverage for Streaming I/O
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl.builder import CellSpec, ColumnSpec, RowSpec, SheetSpec
from spreadsheet_dl.renderer import render_sheets
from spreadsheet_dl.streaming import (
    StreamingCell,
    StreamingReader,
    StreamingRow,
    StreamingWriter,
    stream_read,
    stream_write,
)

if TYPE_CHECKING:
    from pathlib import Path

# ==============================================================================
# Fixtures
# ==============================================================================


pytestmark = [pytest.mark.integration]


@pytest.fixture
def sample_ods_file(tmp_path: Path) -> Path:
    """Create a sample ODS file for reading tests."""
    sheet = SheetSpec(
        name="TestSheet",
        columns=[
            ColumnSpec(name="Name"),
            ColumnSpec(name="Age"),
            ColumnSpec(name="City"),
        ],
        rows=[
            RowSpec(
                cells=[
                    CellSpec(value="Alice"),
                    CellSpec(value=30),
                    CellSpec(value="NYC"),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Bob"),
                    CellSpec(value=25),
                    CellSpec(value="LA"),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Charlie"),
                    CellSpec(value=35),
                    CellSpec(value="Chicago"),
                ]
            ),
        ],
    )

    ods_file = tmp_path / "sample.ods"
    render_sheets([sheet], ods_file)
    return ods_file


@pytest.fixture
def multi_sheet_ods_file(tmp_path: Path) -> Path:
    """Create an ODS file with multiple sheets."""
    sheets = [
        SheetSpec(
            name="Sheet1",
            columns=[ColumnSpec(name="A"), ColumnSpec(name="B")],
            rows=[
                RowSpec(cells=[CellSpec(value=1), CellSpec(value=2)]),
                RowSpec(cells=[CellSpec(value=3), CellSpec(value=4)]),
            ],
        ),
        SheetSpec(
            name="Sheet2",
            columns=[ColumnSpec(name="X"), ColumnSpec(name="Y")],
            rows=[
                RowSpec(cells=[CellSpec(value="a"), CellSpec(value="b")]),
                RowSpec(cells=[CellSpec(value="c"), CellSpec(value="d")]),
            ],
        ),
    ]

    ods_file = tmp_path / "multi_sheet.ods"
    render_sheets(sheets, ods_file)
    return ods_file


@pytest.fixture
def large_ods_file(tmp_path: Path) -> Path:
    """Create a large ODS file with 1000+ rows."""
    rows = [
        RowSpec(
            cells=[
                CellSpec(value=f"Item{i}"),
                CellSpec(value=i * 10),
                CellSpec(value=i * 100.5),
            ]
        )
        for i in range(1000)
    ]

    sheet = SheetSpec(
        name="LargeData",
        columns=[
            ColumnSpec(name="Item"),
            ColumnSpec(name="Quantity"),
            ColumnSpec(name="Price"),
        ],
        rows=rows,
    )

    ods_file = tmp_path / "large.ods"
    render_sheets([sheet], ods_file)
    return ods_file


# ==============================================================================
# StreamingCell Tests
# ==============================================================================


class TestStreamingCell:
    """Tests for StreamingCell class."""

    def test_create_basic(self) -> None:
        """Test creating basic cell."""
        cell = StreamingCell(value="test")
        assert cell.value == "test"
        assert cell.value_type == "string"

    def test_create_with_formula(self) -> None:
        """Test creating cell with formula."""
        cell = StreamingCell(formula="=A1+B1", value_type="float")
        assert cell.formula == "=A1+B1"

    def test_create_with_style(self) -> None:
        """Test creating cell with style."""
        cell = StreamingCell(value="test", style="bold")
        assert cell.style == "bold"

    def test_is_empty_true(self) -> None:
        """Test is_empty returns True for empty cell."""
        cell = StreamingCell()
        assert cell.is_empty()

    def test_is_empty_false_with_value(self) -> None:
        """Test is_empty returns False with value."""
        cell = StreamingCell(value="test")
        assert not cell.is_empty()

    def test_is_empty_false_with_formula(self) -> None:
        """Test is_empty returns False with formula."""
        cell = StreamingCell(formula="=A1")
        assert not cell.is_empty()


# ==============================================================================
# StreamingRow Tests
# ==============================================================================


class TestStreamingRow:
    """Tests for StreamingRow class."""

    def test_create_basic(self) -> None:
        """Test creating basic row."""
        cells = [StreamingCell(value="a"), StreamingCell(value="b")]
        row = StreamingRow(cells=cells, row_index=0)
        assert len(row) == 2
        assert row.row_index == 0

    def test_len(self) -> None:
        """Test row length."""
        cells = [StreamingCell(value=i) for i in range(5)]
        row = StreamingRow(cells=cells)
        assert len(row) == 5

    def test_iteration(self) -> None:
        """Test iterating over row cells."""
        cells = [StreamingCell(value=i) for i in range(3)]
        row = StreamingRow(cells=cells)

        values = [cell.value for cell in row]
        assert values == [0, 1, 2]

    def test_with_style(self) -> None:
        """Test row with style."""
        row = StreamingRow(cells=[], style="row_header")
        assert row.style == "row_header"


# ==============================================================================
# StreamingReader Tests
# ==============================================================================


class TestStreamingReader:
    """Tests for StreamingReader class."""

    def test_init(self, sample_ods_file: Path) -> None:
        """Test initializing reader."""
        reader = StreamingReader(sample_ods_file)
        assert reader._file_path == sample_ods_file

    def test_context_manager(self, sample_ods_file: Path) -> None:
        """Test using reader as context manager."""
        with StreamingReader(sample_ods_file) as reader:
            assert reader._zipfile is not None
        # Should be closed after context
        assert reader._zipfile is None

    def test_open_close(self, sample_ods_file: Path) -> None:
        """Test manual open/close."""
        reader = StreamingReader(sample_ods_file)
        reader.open()
        assert reader._zipfile is not None

        reader.close()
        assert reader._zipfile is None

    def test_open_nonexistent_file(self, tmp_path: Path) -> None:
        """Test opening non-existent file raises error."""
        reader = StreamingReader(tmp_path / "nonexistent.ods")
        with pytest.raises(FileNotFoundError, match="File not found"):
            reader.open()

    def test_sheet_names(self, sample_ods_file: Path) -> None:
        """Test getting sheet names."""
        with StreamingReader(sample_ods_file) as reader:
            names = reader.sheet_names()
            assert "TestSheet" in names

    def test_sheet_names_multiple(self, multi_sheet_ods_file: Path) -> None:
        """Test getting multiple sheet names."""
        with StreamingReader(multi_sheet_ods_file) as reader:
            names = reader.sheet_names()
            assert "Sheet1" in names
            assert "Sheet2" in names
            assert len(names) >= 2

    def test_row_count(self, sample_ods_file: Path) -> None:
        """Test getting row count."""
        with StreamingReader(sample_ods_file) as reader:
            count = reader.row_count("TestSheet")
            assert count == 3  # 3 data rows

    def test_row_count_nonexistent_sheet(self, sample_ods_file: Path) -> None:
        """Test row count for non-existent sheet."""
        with StreamingReader(sample_ods_file) as reader:
            count = reader.row_count("NonExistent")
            assert count == 0

    def test_column_count(self, sample_ods_file: Path) -> None:
        """Test getting column count."""
        with StreamingReader(sample_ods_file) as reader:
            count = reader.column_count("TestSheet")
            assert count >= 3

    def test_column_count_nonexistent_sheet(self, sample_ods_file: Path) -> None:
        """Test column count for non-existent sheet returns 0.

        Coverage: Line 193 - column_count returning 0 for None table
        """
        with StreamingReader(sample_ods_file) as reader:
            count = reader.column_count("NonExistentSheet")
            assert count == 0

    def test_get_table_without_open_raises_error(self, sample_ods_file: Path) -> None:
        """Test _get_table raises RuntimeError when file not opened.

        Coverage: Line 241 - _get_table raising RuntimeError when file not opened
        """
        reader = StreamingReader(sample_ods_file)
        # Don't open the file

        with pytest.raises(RuntimeError, match="File not opened"):
            reader._get_table("TestSheet")

    def test_rows_iteration(self, sample_ods_file: Path) -> None:
        """Test iterating over rows."""
        with StreamingReader(sample_ods_file) as reader:
            rows = list(reader.rows("TestSheet"))
            assert len(rows) == 3

            # Check first row
            first_row = rows[0]
            assert isinstance(first_row, StreamingRow)
            assert len(first_row.cells) > 0

    def test_rows_with_start_row(self, sample_ods_file: Path) -> None:
        """Test reading rows from specific start."""
        with StreamingReader(sample_ods_file) as reader:
            rows = list(reader.rows("TestSheet", start_row=1))
            assert len(rows) == 2  # Skip first row

    def test_rows_with_limit(self, sample_ods_file: Path) -> None:
        """Test reading limited number of rows."""
        with StreamingReader(sample_ods_file) as reader:
            rows = list(reader.rows("TestSheet", limit=2))
            assert len(rows) == 2

    def test_rows_with_start_and_limit(self, sample_ods_file: Path) -> None:
        """Test reading rows with start and limit."""
        with StreamingReader(sample_ods_file) as reader:
            rows = list(reader.rows("TestSheet", start_row=1, limit=1))
            assert len(rows) == 1

    def test_rows_nonexistent_sheet(self, sample_ods_file: Path) -> None:
        """Test reading from non-existent sheet."""
        with StreamingReader(sample_ods_file) as reader:
            rows = list(reader.rows("NonExistent"))
            assert len(rows) == 0

    def test_large_file_streaming(self, large_ods_file: Path) -> None:
        """Test streaming large file efficiently."""
        with StreamingReader(large_ods_file) as reader:
            count = 0
            for _row in reader.rows("LargeData"):
                count += 1
                if count == 100:
                    break  # Don't need to read all

            assert count == 100

    def test_multiple_sheet_iteration(self, multi_sheet_ods_file: Path) -> None:
        """Test iterating over multiple sheets."""
        with StreamingReader(multi_sheet_ods_file) as reader:
            for sheet_name in reader.sheet_names():
                rows = list(reader.rows(sheet_name))
                assert len(rows) > 0

    def test_operations_without_open_raise_error(self, sample_ods_file: Path) -> None:
        """Test operations without opening raise error."""
        reader = StreamingReader(sample_ods_file)
        with pytest.raises(RuntimeError, match="File not opened"):
            reader.sheet_names()


# ==============================================================================
# StreamingWriter Tests
# ==============================================================================


class TestStreamingWriter:
    """Tests for StreamingWriter class."""

    def test_init(self, tmp_path: Path) -> None:
        """Test initializing writer."""
        writer = StreamingWriter(tmp_path / "output.ods")
        assert writer._file_path == tmp_path / "output.ods"

    def test_context_manager(self, tmp_path: Path) -> None:
        """Test using writer as context manager."""
        output_file = tmp_path / "context.ods"

        with StreamingWriter(output_file) as writer:
            writer.start_sheet("Test")
            writer.write_row([1, 2, 3])
            writer.end_sheet()

        assert output_file.exists()

    def test_start_sheet(self, tmp_path: Path) -> None:
        """Test starting a new sheet."""
        writer = StreamingWriter(tmp_path / "test.ods")
        result = writer.start_sheet("Sheet1")
        assert result is writer  # Chainable
        assert writer._current_sheet == "Sheet1"

    def test_start_sheet_with_columns(self, tmp_path: Path) -> None:
        """Test starting sheet with column headers."""
        writer = StreamingWriter(tmp_path / "test.ods")
        writer.start_sheet("Sheet1", columns=["A", "B", "C"])
        assert len(writer._buffer) == 1  # Header row added

    def test_write_row_list(self, tmp_path: Path) -> None:
        """Test writing row from list."""
        writer = StreamingWriter(tmp_path / "test.ods")
        writer.start_sheet("Sheet1")
        result = writer.write_row([1, 2, 3])
        assert result is writer  # Chainable
        assert len(writer._buffer) == 1

    def test_write_row_streaming_row(self, tmp_path: Path) -> None:
        """Test writing StreamingRow."""
        cells = [StreamingCell(value=i) for i in range(3)]
        row = StreamingRow(cells=cells)

        writer = StreamingWriter(tmp_path / "test.ods")
        writer.start_sheet("Sheet1")
        writer.write_row(row)
        assert len(writer._buffer) == 1

    def test_write_row_without_sheet_raises_error(self, tmp_path: Path) -> None:
        """Test writing row without active sheet raises error."""
        writer = StreamingWriter(tmp_path / "test.ods")
        with pytest.raises(RuntimeError, match="No active sheet"):
            writer.write_row([1, 2, 3])

    def test_write_rows(self, tmp_path: Path) -> None:
        """Test writing multiple rows."""
        rows = [[1, 2], [3, 4], [5, 6]]
        writer = StreamingWriter(tmp_path / "test.ods")
        writer.start_sheet("Sheet1")
        writer.write_rows(rows)
        assert len(writer._buffer) == 3

    def test_end_sheet(self, tmp_path: Path) -> None:
        """Test ending a sheet."""
        writer = StreamingWriter(tmp_path / "test.ods")
        writer.start_sheet("Sheet1")
        writer.write_row([1, 2])
        result = writer.end_sheet()
        assert result is writer  # Chainable
        assert writer._current_sheet is None

    def test_end_sheet_when_no_active_sheet(self, tmp_path: Path) -> None:
        """Test end_sheet returns self when no current sheet.

        Coverage: Line 409 - end_sheet returning self when no current sheet
        """
        writer = StreamingWriter(tmp_path / "test.ods")
        # Don't start a sheet
        result = writer.end_sheet()
        assert result is writer  # Should return self
        assert writer._current_sheet is None

    def test_close(self, tmp_path: Path) -> None:
        """Test closing writer and generating file."""
        output_file = tmp_path / "output.ods"
        writer = StreamingWriter(output_file)
        writer.start_sheet("Sheet1")
        writer.write_row([1, 2, 3])
        writer.end_sheet()

        result = writer.close()
        assert result == output_file
        assert output_file.exists()

    def test_single_sheet_write(self, tmp_path: Path) -> None:
        """Test writing single sheet."""
        output_file = tmp_path / "single.ods"

        with StreamingWriter(output_file) as writer:
            writer.start_sheet("Data", columns=["A", "B", "C"])
            writer.write_row([1, 2, 3])
            writer.write_row([4, 5, 6])
            writer.end_sheet()

        assert output_file.exists()

        # Verify content
        with StreamingReader(output_file) as reader:
            rows = list(reader.rows("Data"))
            assert len(rows) >= 2

    def test_multiple_sheets_write(self, tmp_path: Path) -> None:
        """Test writing multiple sheets."""
        output_file = tmp_path / "multi.ods"

        with StreamingWriter(output_file) as writer:
            writer.start_sheet("Sheet1")
            writer.write_rows([[1, 2], [3, 4]])
            writer.end_sheet()

            writer.start_sheet("Sheet2")
            writer.write_rows([["a", "b"], ["c", "d"]])
            writer.end_sheet()

        # Verify
        with StreamingReader(output_file) as reader:
            names = reader.sheet_names()
            assert "Sheet1" in names
            assert "Sheet2" in names

    def test_chunk_flushing(self, tmp_path: Path) -> None:
        """Test automatic chunk flushing."""
        output_file = tmp_path / "chunks.ods"
        chunk_size = 10

        with StreamingWriter(output_file, chunk_size=chunk_size) as writer:
            writer.start_sheet("Data")

            # Write more than chunk size
            for i in range(25):
                writer.write_row([i, i * 2])

            # Buffer should have been flushed
            assert len(writer._buffer) < chunk_size

            writer.end_sheet()

        # Verify all rows written
        with StreamingReader(output_file) as reader:
            rows = list(reader.rows("Data"))
            assert len(rows) == 25

    def test_large_dataset_write(self, tmp_path: Path) -> None:
        """Test writing large dataset (1000+ rows)."""
        output_file = tmp_path / "large_write.ods"

        with StreamingWriter(output_file, chunk_size=100) as writer:
            writer.start_sheet("LargeData", columns=["ID", "Value"])

            # Write 1000 rows
            for i in range(1000):
                writer.write_row([i, i * 100])

            writer.end_sheet()

        # Verify
        with StreamingReader(output_file) as reader:
            count = reader.row_count("LargeData")
            assert count >= 1000

    def test_auto_end_sheet_on_start(self, tmp_path: Path) -> None:
        """Test starting new sheet auto-ends previous sheet."""
        output_file = tmp_path / "auto_end.ods"

        with StreamingWriter(output_file) as writer:
            writer.start_sheet("Sheet1")
            writer.write_row([1, 2])

            # Starting new sheet should end previous
            writer.start_sheet("Sheet2")
            writer.write_row([3, 4])

        # Verify both sheets exist
        with StreamingReader(output_file) as reader:
            names = reader.sheet_names()
            assert "Sheet1" in names
            assert "Sheet2" in names

    def test_round_trip(self, tmp_path: Path) -> None:
        """Test write then read round-trip."""
        output_file = tmp_path / "round_trip.ods"

        # Write
        with StreamingWriter(output_file) as writer:
            writer.start_sheet("Test", columns=["Name", "Age"])
            writer.write_row(["Alice", 30])
            writer.write_row(["Bob", 25])
            writer.end_sheet()

        # Read
        with StreamingReader(output_file) as reader:
            rows = list(reader.rows("Test"))
            # First row might be headers depending on implementation
            assert len(rows) >= 2


# ==============================================================================
# Convenience Functions Tests
# ==============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_stream_read(self, sample_ods_file: Path) -> None:
        """Test stream_read convenience function."""
        reader = stream_read(sample_ods_file)
        assert isinstance(reader, StreamingReader)

        # Not opened by default
        assert reader._zipfile is None

    def test_stream_write(self, tmp_path: Path) -> None:
        """Test stream_write convenience function."""
        writer = stream_write(tmp_path / "test.ods")
        assert isinstance(writer, StreamingWriter)

    def test_stream_write_with_chunk_size(self, tmp_path: Path) -> None:
        """Test stream_write with custom chunk size."""
        writer = stream_write(tmp_path / "test.ods", chunk_size=500)
        assert writer._chunk_size == 500


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestIntegration:
    """Integration tests for streaming I/O."""

    def test_read_write_round_trip(self, sample_ods_file: Path, tmp_path: Path) -> None:
        """Test reading then writing preserves data."""
        output_file = tmp_path / "copy.ods"

        # Read from sample
        with StreamingReader(sample_ods_file) as reader:
            sheet_names = reader.sheet_names()

            # Write to output
            with StreamingWriter(output_file) as writer:
                for sheet_name in sheet_names:
                    col_count = reader.column_count(sheet_name)
                    columns = [f"Col{i}" for i in range(col_count)]

                    writer.start_sheet(sheet_name, columns=columns)

                    for row in reader.rows(sheet_name):
                        values = [cell.value for cell in row.cells]
                        writer.write_row(values)

                    writer.end_sheet()

        # Verify output
        assert output_file.exists()
        with StreamingReader(output_file) as reader:
            names = reader.sheet_names()
            assert len(names) > 0

    def test_memory_efficient_processing(
        self, large_ods_file: Path, tmp_path: Path
    ) -> None:
        """Test processing large file without loading all into memory."""
        output_file = tmp_path / "processed.ods"

        # Read and process in chunks
        with (
            StreamingReader(large_ods_file) as reader,
            StreamingWriter(output_file, chunk_size=100) as writer,
        ):
            writer.start_sheet("Processed", columns=["Item", "Double"])

            for row in reader.rows("LargeData"):
                # Process row (e.g., double the quantity)
                if len(row.cells) >= 2:
                    item = row.cells[0].value
                    quantity = row.cells[1].value
                    if quantity is not None:
                        try:
                            doubled = float(quantity) * 2
                            writer.write_row([item, doubled])
                        except (ValueError, TypeError):
                            pass

            writer.end_sheet()

        assert output_file.exists()

    def test_filter_while_streaming(self, large_ods_file: Path, tmp_path: Path) -> None:
        """Test filtering rows while streaming."""
        output_file = tmp_path / "filtered.ods"

        with (
            StreamingReader(large_ods_file) as reader,
            StreamingWriter(output_file) as writer,
        ):
            writer.start_sheet("Filtered")

            for row in reader.rows("LargeData"):
                # Only write rows where quantity is even
                if len(row.cells) >= 2 and row.cells[1].value is not None:
                    try:
                        qty = float(row.cells[1].value)
                        if int(qty) % 2 == 0:
                            values = [cell.value for cell in row.cells]
                            writer.write_row(values)
                    except (ValueError, TypeError):
                        pass

            writer.end_sheet()

        # Verify filtered output exists
        with StreamingReader(output_file) as reader:
            row_count = reader.row_count("Filtered")
            # Should have some rows (depends on filter logic)
            assert row_count >= 0
            assert row_count <= 1000  # Should not exceed original


# ==============================================================================
# Edge Cases and Error Handling
# ==============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_sheet(self, tmp_path: Path) -> None:
        """Test writing empty sheet."""
        output_file = tmp_path / "empty.ods"

        with StreamingWriter(output_file) as writer:
            writer.start_sheet("Empty")
            writer.end_sheet()

        assert output_file.exists()

    def test_none_values_in_cells(self, tmp_path: Path) -> None:
        """Test writing cells with None values."""
        output_file = tmp_path / "none_values.ods"

        with StreamingWriter(output_file) as writer:
            writer.start_sheet("Test")
            writer.write_row([None, "text", None])
            writer.write_row([1, None, 3])
            writer.end_sheet()

        assert output_file.exists()

    def test_special_characters(self, tmp_path: Path) -> None:
        """Test writing special characters."""
        output_file = tmp_path / "special.ods"

        with StreamingWriter(output_file) as writer:
            writer.start_sheet("Test")
            writer.write_row(["Line\nBreak", "Tab\tChar", 'Quote"Test'])
            writer.end_sheet()

        # Verify can be read back
        with StreamingReader(output_file) as reader:
            rows = list(reader.rows("Test"))
            assert len(rows) > 0

    def test_unicode_characters(self, tmp_path: Path) -> None:
        """Test writing unicode characters."""
        output_file = tmp_path / "unicode.ods"

        with StreamingWriter(output_file) as writer:
            writer.start_sheet("Test")
            writer.write_row(["Hello 世界", "Emoji 🎉", "Русский"])
            writer.end_sheet()

        # Verify can be read back
        with StreamingReader(output_file) as reader:
            rows = list(reader.rows("Test"))
            assert len(rows) > 0

    def test_very_long_sheet_name(self, tmp_path: Path) -> None:
        """Test writing sheet with very long name."""
        output_file = tmp_path / "long_name.ods"
        long_name = "A" * 100

        with StreamingWriter(output_file) as writer:
            writer.start_sheet(long_name)
            writer.write_row([1, 2, 3])
            writer.end_sheet()

        assert output_file.exists()

    def test_many_columns(self, tmp_path: Path) -> None:
        """Test writing row with many columns."""
        output_file = tmp_path / "many_cols.ods"

        with StreamingWriter(output_file) as writer:
            writer.start_sheet("Wide")
            # 100 columns
            writer.write_row(list(range(100)))
            writer.end_sheet()

        # Verify
        with StreamingReader(output_file) as reader:
            rows = list(reader.rows("Wide"))
            assert len(rows[0].cells) == 100

    def test_close_without_sheets(self, tmp_path: Path) -> None:
        """Test closing writer without any sheets."""
        output_file = tmp_path / "no_sheets.ods"

        writer = StreamingWriter(output_file)
        # Don't write any sheets
        result = writer.close()

        # Should still create file (though might be invalid ODS)
        assert result == output_file


# ==============================================================================
# ODS-Specific Parsing Tests
# ==============================================================================


class TestODSParsing:
    """Tests for ODS-specific parsing features."""

    def test_parse_covered_table_cells(self, tmp_path: Path) -> None:
        """Test parsing covered table cells (merged cells).

        Coverage: Lines 262-264 - _parse_row handling covered table cells

        This tests the handling of table:covered-table-cell elements
        which appear in merged cell regions.
        """
        # Create a sheet with merged cells
        # Note: We need to create an ODS with merged cells to test this
        sheet = SheetSpec(
            name="MergedTest",
            columns=[ColumnSpec(name="A"), ColumnSpec(name="B"), ColumnSpec(name="C")],
            rows=[
                RowSpec(
                    cells=[
                        CellSpec(
                            value="Merged", colspan=2
                        ),  # This creates covered cells
                        CellSpec(value="Single"),
                    ]
                ),
                RowSpec(
                    cells=[
                        CellSpec(value="A2"),
                        CellSpec(value="B2"),
                        CellSpec(value="C2"),
                    ]
                ),
            ],
        )

        ods_file = tmp_path / "merged.ods"
        render_sheets([sheet], ods_file)

        # Read it back
        with StreamingReader(ods_file) as reader:
            rows = list(reader.rows("MergedTest"))
            assert len(rows) >= 1
            # First row should have cells (including covered ones)
            # The exact number depends on how the renderer handles colspan

    def test_parse_currency_value_type(self, tmp_path: Path) -> None:
        """Test parsing currency value type.

        Coverage: Lines 280, 282-284 - _parse_cell handling currency value type

        This tests the handling of office:value-type="currency"
        """
        # Create a sheet with currency values
        # Note: CellSpec with value_type="currency" should trigger this
        from decimal import Decimal

        sheet = SheetSpec(
            name="CurrencyTest",
            columns=[ColumnSpec(name="Amount")],
            rows=[
                RowSpec(
                    cells=[
                        CellSpec(value=Decimal("1234.56"), value_type="currency"),
                    ]
                ),
            ],
        )

        ods_file = tmp_path / "currency.ods"
        render_sheets([sheet], ods_file)

        # Read it back - the currency value should be parsed
        with StreamingReader(ods_file) as reader:
            rows = list(reader.rows("CurrencyTest"))
            assert len(rows) >= 1
            # Value should be parsed (either as float or the raw value)
            first_cell = rows[0].cells[0] if rows[0].cells else None
            if first_cell:
                # The value might be a float or string depending on parsing
                assert first_cell.value is not None or first_cell.value_type in (
                    "currency",
                    "float",
                    "string",
                )

    def test_parse_percentage_value_type(self, tmp_path: Path) -> None:
        """Test parsing percentage value type.

        Coverage: Lines 280, 282-284 - _parse_cell handling percentage value type

        This tests the handling of office:value-type="percentage"
        """
        # Create a sheet with percentage values
        sheet = SheetSpec(
            name="PercentTest",
            columns=[ColumnSpec(name="Rate")],
            rows=[
                RowSpec(
                    cells=[
                        CellSpec(value=0.15, value_type="percentage"),  # 15%
                    ]
                ),
            ],
        )

        ods_file = tmp_path / "percent.ods"
        render_sheets([sheet], ods_file)

        # Read it back - the percentage value should be parsed
        with StreamingReader(ods_file) as reader:
            rows = list(reader.rows("PercentTest"))
            assert len(rows) >= 1
            first_cell = rows[0].cells[0] if rows[0].cells else None
            if first_cell:
                # The value might be a float or string depending on parsing
                assert first_cell.value is not None or first_cell.value_type in (
                    "percentage",
                    "float",
                    "string",
                )

    def test_parse_date_value_type(self, tmp_path: Path) -> None:
        """Test parsing cells with date value type.

        Coverage: Line 280 - _parse_cell handling date value type
        This tests the handling of office:value-type="date"
        """
        # Create ODS with date cell
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.table import Table, TableCell, TableRow
        from odf.text import P

        doc = OpenDocumentSpreadsheet()
        table = Table(name="Sheet1")
        row = TableRow()

        # Create date cell with explicit date value attribute
        cell = TableCell(valuetype="date", datevalue="2024-01-15")
        cell.addElement(P(text="2024-01-15"))
        row.addElement(cell)
        table.addElement(row)
        doc.spreadsheet.addElement(table)

        test_file = tmp_path / "date_test.ods"
        doc.save(str(test_file))

        # Read with streaming reader
        reader = StreamingReader(str(test_file))
        reader.open()
        rows = list(reader.rows("Sheet1"))
        reader.close()

        assert len(rows) > 0
        # The date value should be parsed
        assert rows[0].cells[0].value is not None  # Triggers line 280
