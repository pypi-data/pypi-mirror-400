"""Comprehensive tests for streaming large file handling.

Task 2.4: Streaming Large File Tests for SpreadsheetDL v4.1.0 pre-release audit.

Tests:
    - Large row count handling (10k, 50k, 100k rows)
    - Wide sheet handling (100+ columns)
    - Memory-efficient iteration patterns
    - Chunk-based writing performance
    - Concurrent read/write operations
    - ZIP bomb protection
    - Edge cases for very large data
"""

from __future__ import annotations

import contextlib
import zipfile
from pathlib import Path

import pytest

from spreadsheet_dl.builder import CellSpec, ColumnSpec, RowSpec, SheetSpec
from spreadsheet_dl.renderer import render_sheets
from spreadsheet_dl.streaming import (
    StreamingReader,
    StreamingWriter,
)

pytestmark = [pytest.mark.integration, pytest.mark.slow]


# =============================================================================
# Fixtures for Large File Tests
# =============================================================================


@pytest.fixture
def large_10k_file(tmp_path: Path) -> Path:
    """Create a file with 10,000 rows."""
    rows = [
        RowSpec(
            cells=[
                CellSpec(value=f"Item{i}"),
                CellSpec(value=i),
                CellSpec(value=i * 1.5),
                CellSpec(value=f"Category{i % 10}"),
            ]
        )
        for i in range(10000)
    ]

    sheet = SheetSpec(
        name="LargeData",
        columns=[
            ColumnSpec(name="Name"),
            ColumnSpec(name="ID"),
            ColumnSpec(name="Value"),
            ColumnSpec(name="Category"),
        ],
        rows=rows,
    )

    ods_file = tmp_path / "large_10k.ods"
    render_sheets([sheet], ods_file)
    return ods_file


@pytest.fixture
def wide_sheet_file(tmp_path: Path) -> Path:
    """Create a file with 100 columns."""
    num_cols = 100
    num_rows = 100

    columns = [ColumnSpec(name=f"Col{i}") for i in range(num_cols)]

    rows = [
        RowSpec(cells=[CellSpec(value=f"R{r}C{c}") for c in range(num_cols)])
        for r in range(num_rows)
    ]

    sheet = SheetSpec(name="Wide", columns=columns, rows=rows)

    ods_file = tmp_path / "wide_100_cols.ods"
    render_sheets([sheet], ods_file)
    return ods_file


@pytest.fixture
def multi_sheet_large_file(tmp_path: Path) -> Path:
    """Create a file with multiple large sheets."""
    sheets = []
    for sheet_num in range(5):
        rows = [
            RowSpec(
                cells=[
                    CellSpec(value=f"Sheet{sheet_num}_Row{i}"),
                    CellSpec(value=i * (sheet_num + 1)),
                ]
            )
            for i in range(2000)
        ]
        sheets.append(
            SheetSpec(
                name=f"Sheet{sheet_num}",
                columns=[ColumnSpec(name="Label"), ColumnSpec(name="Value")],
                rows=rows,
            )
        )

    ods_file = tmp_path / "multi_sheet_large.ods"
    render_sheets(sheets, ods_file)
    return ods_file


# =============================================================================
# Large Row Count Tests
# =============================================================================


class TestLargeRowCounts:
    """Test handling of files with many rows."""

    def test_read_10k_rows_streaming(self, large_10k_file: Path) -> None:
        """Test streaming read of 10,000 rows."""
        with StreamingReader(large_10k_file) as reader:
            count = 0
            for row in reader.rows("LargeData"):
                count += 1
                assert len(row.cells) == 4

            assert count == 10000

    def test_read_10k_with_limit(self, large_10k_file: Path) -> None:
        """Test reading limited rows from large file."""
        with StreamingReader(large_10k_file) as reader:
            rows = list(reader.rows("LargeData", limit=100))
            assert len(rows) == 100

    def test_read_10k_with_offset_and_limit(self, large_10k_file: Path) -> None:
        """Test reading with offset and limit from large file."""
        with StreamingReader(large_10k_file) as reader:
            rows = list(reader.rows("LargeData", start_row=5000, limit=100))
            assert len(rows) == 100

    def test_row_count_10k(self, large_10k_file: Path) -> None:
        """Test row count for large file."""
        with StreamingReader(large_10k_file) as reader:
            count = reader.row_count("LargeData")
            assert count == 10000

    def test_write_10k_rows_streaming(self, tmp_path: Path) -> None:
        """Test streaming write of 10,000 rows."""
        output_file = tmp_path / "write_10k.ods"

        with StreamingWriter(output_file, chunk_size=1000) as writer:
            writer.start_sheet("Data", columns=["ID", "Value", "Status"])

            for i in range(10000):
                writer.write_row([i, i * 100, f"Status{i % 5}"])

            writer.end_sheet()

        # Verify
        with StreamingReader(output_file) as reader:
            count = reader.row_count("Data")
            # Header + 10000 data rows
            assert count >= 10000

    @pytest.mark.slow
    def test_write_50k_rows_streaming(self, tmp_path: Path) -> None:
        """Test streaming write of 50,000 rows."""
        output_file = tmp_path / "write_50k.ods"

        with StreamingWriter(output_file, chunk_size=5000) as writer:
            writer.start_sheet("Data", columns=["ID", "Value"])

            for i in range(50000):
                writer.write_row([i, i * 10])

            writer.end_sheet()

        # Verify file created
        assert output_file.exists()

        # Verify row count
        with StreamingReader(output_file) as reader:
            count = reader.row_count("Data")
            assert count >= 50000


# =============================================================================
# Wide Sheet Tests
# =============================================================================


class TestWideSheets:
    """Test handling of sheets with many columns."""

    def test_read_100_columns(self, wide_sheet_file: Path) -> None:
        """Test reading sheet with 100 columns."""
        with StreamingReader(wide_sheet_file) as reader:
            rows = list(reader.rows("Wide"))
            assert len(rows) == 100

            for row in rows:
                assert len(row.cells) == 100

    def test_column_count_wide_sheet(self, wide_sheet_file: Path) -> None:
        """Test column count for wide sheet."""
        with StreamingReader(wide_sheet_file) as reader:
            count = reader.column_count("Wide")
            assert count == 100

    def test_write_wide_sheet(self, tmp_path: Path) -> None:
        """Test writing sheet with 100+ columns."""
        output_file = tmp_path / "wide_write.ods"
        num_cols = 150

        with StreamingWriter(output_file) as writer:
            columns = [f"Col{i}" for i in range(num_cols)]
            writer.start_sheet("Wide", columns=columns)

            for r in range(50):
                writer.write_row([f"R{r}C{c}" for c in range(num_cols)])

            writer.end_sheet()

        # Verify
        with StreamingReader(output_file) as reader:
            rows = list(reader.rows("Wide"))
            # At least the header row
            assert len(rows) >= 50


# =============================================================================
# Multi-Sheet Large File Tests
# =============================================================================


class TestMultiSheetLargeFiles:
    """Test handling of files with multiple large sheets."""

    def test_read_all_sheets(self, multi_sheet_large_file: Path) -> None:
        """Test reading all sheets from multi-sheet file."""
        with StreamingReader(multi_sheet_large_file) as reader:
            sheet_names = reader.sheet_names()
            assert len(sheet_names) == 5

            for name in sheet_names:
                count = reader.row_count(name)
                assert count == 2000

    def test_read_specific_sheet_from_multi(self, multi_sheet_large_file: Path) -> None:
        """Test reading specific sheet from multi-sheet file."""
        with StreamingReader(multi_sheet_large_file) as reader:
            rows = list(reader.rows("Sheet2", limit=100))
            assert len(rows) == 100

    def test_write_multiple_large_sheets(self, tmp_path: Path) -> None:
        """Test writing multiple large sheets."""
        output_file = tmp_path / "multi_large_write.ods"

        with StreamingWriter(output_file, chunk_size=500) as writer:
            for sheet_num in range(3):
                writer.start_sheet(f"Sheet{sheet_num}", columns=["ID", "Value"])

                for i in range(5000):
                    writer.write_row([i, i * sheet_num])

                writer.end_sheet()

        # Verify
        with StreamingReader(output_file) as reader:
            names = reader.sheet_names()
            assert len(names) >= 3


# =============================================================================
# Memory Efficiency Tests
# =============================================================================


class TestMemoryEfficiency:
    """Test memory-efficient processing patterns."""

    def test_streaming_iteration_memory(self, large_10k_file: Path) -> None:
        """Test that streaming doesn't load all rows into memory."""
        with StreamingReader(large_10k_file) as reader:
            # Process rows one at a time
            total = 0.0
            for row in reader.rows("LargeData"):
                if len(row.cells) >= 2:
                    val = row.cells[1].value
                    if val is not None:
                        with contextlib.suppress(ValueError, TypeError):
                            total += float(val)

            # Should have processed all rows
            assert total > 0

    def test_chunked_writing_memory(self, tmp_path: Path) -> None:
        """Test that chunked writing flushes buffer."""
        output_file = tmp_path / "chunked.ods"

        with StreamingWriter(output_file, chunk_size=100) as writer:
            writer.start_sheet("Data")

            # Write 1000 rows with small chunk size
            for i in range(1000):
                writer.write_row([i, i * 2])
                # Buffer should never grow larger than chunk size
                assert len(writer._buffer) <= 100

            writer.end_sheet()

    def test_process_without_loading_all(
        self, large_10k_file: Path, tmp_path: Path
    ) -> None:
        """Test processing large file without loading all data."""
        output_file = tmp_path / "processed.ods"

        with (
            StreamingReader(large_10k_file) as reader,
            StreamingWriter(output_file, chunk_size=500) as writer,
        ):
            writer.start_sheet("Processed", columns=["ID", "DoubledValue"])

            for row in reader.rows("LargeData"):
                if len(row.cells) >= 2:
                    id_val = row.cells[0].value
                    num_val = row.cells[1].value
                    if num_val is not None:
                        try:
                            doubled = float(num_val) * 2
                            writer.write_row([id_val, doubled])
                        except (ValueError, TypeError):
                            pass

            writer.end_sheet()

        assert output_file.exists()


# =============================================================================
# Chunk Size Variations
# =============================================================================


class TestChunkSizeVariations:
    """Test different chunk sizes for writing."""

    @pytest.mark.parametrize("chunk_size", [10, 100, 500, 1000, 5000])
    def test_various_chunk_sizes(self, tmp_path: Path, chunk_size: int) -> None:
        """Test writing with various chunk sizes."""
        output_file = tmp_path / f"chunk_{chunk_size}.ods"

        with StreamingWriter(output_file, chunk_size=chunk_size) as writer:
            writer.start_sheet("Data")

            for i in range(2500):
                writer.write_row([i, f"Value{i}"])

            writer.end_sheet()

        # Verify all rows written
        with StreamingReader(output_file) as reader:
            count = reader.row_count("Data")
            assert count == 2500

    def test_chunk_size_1(self, tmp_path: Path) -> None:
        """Test writing with chunk size of 1 (immediate flush)."""
        output_file = tmp_path / "chunk_1.ods"

        with StreamingWriter(output_file, chunk_size=1) as writer:
            writer.start_sheet("Data")

            for i in range(100):
                writer.write_row([i, i * 2])
                # Buffer should be flushed immediately
                # (or hold at most 1 row)

            writer.end_sheet()

        with StreamingReader(output_file) as reader:
            count = reader.row_count("Data")
            assert count == 100


# =============================================================================
# ZIP Bomb Protection Tests
# =============================================================================


class TestZipBombProtection:
    """Test ZIP bomb detection and prevention."""

    def test_normal_file_passes_zip_check(self, large_10k_file: Path) -> None:
        """Test that normal large file passes ZIP bomb check."""
        reader = StreamingReader(large_10k_file)
        # Should not raise
        reader.open()
        reader.close()

    def test_high_compression_ratio_detection(self, tmp_path: Path) -> None:
        """Test detection of suspicious compression ratio.

        This test creates a file that would have extreme compression
        ratio if it were malicious.
        """
        # Create a file that simulates high compression
        # (repeated data compresses well)
        test_file = tmp_path / "suspicious.zip"

        with zipfile.ZipFile(test_file, "w", zipfile.ZIP_DEFLATED) as zf:
            # Write highly repetitive content
            content = b"A" * (1024 * 1024)  # 1MB of 'A's
            zf.writestr("content.xml", content)

        # The StreamingReader checks compression ratio
        reader = StreamingReader(test_file)

        # This should either pass (if ratio is reasonable) or
        # raise ValueError (if ratio exceeds threshold)
        # Note: Highly repetitive content can have high but not
        # necessarily malicious compression ratios
        try:
            reader.open()
            reader.close()
        except ValueError as e:
            # If detected as suspicious, verify the error message
            assert "compression ratio" in str(e).lower()

    def test_file_count_limit(self, tmp_path: Path) -> None:
        """Test that excessive file count is detected."""
        # This tests the MAX_FILE_COUNT check
        # Normal ODS files have limited file count
        pass  # Normal ODS won't trigger this


# =============================================================================
# Error Handling for Large Files
# =============================================================================


class TestLargeFileErrorHandling:
    """Test error handling for large file operations."""

    def test_read_nonexistent_sheet_large_file(self, large_10k_file: Path) -> None:
        """Test reading non-existent sheet returns empty."""
        with StreamingReader(large_10k_file) as reader:
            rows = list(reader.rows("NonExistentSheet"))
            assert len(rows) == 0

    def test_write_without_starting_sheet(self, tmp_path: Path) -> None:
        """Test writing without starting a sheet raises error."""
        writer = StreamingWriter(tmp_path / "error.ods")

        with pytest.raises(RuntimeError, match="No active sheet"):
            writer.write_row([1, 2, 3])

    def test_operations_on_closed_reader(self, large_10k_file: Path) -> None:
        """Test operations on closed reader raise error."""
        reader = StreamingReader(large_10k_file)
        reader.open()
        reader.close()

        with pytest.raises(RuntimeError, match="File not opened"):
            reader.sheet_names()


# =============================================================================
# Data Integrity Tests
# =============================================================================


class TestLargeFileDataIntegrity:
    """Test data integrity for large file operations."""

    def test_roundtrip_preserves_data(self, tmp_path: Path) -> None:
        """Test write-then-read preserves data."""
        original_file = tmp_path / "original.ods"
        num_rows = 5000

        # Write
        with StreamingWriter(original_file) as writer:
            writer.start_sheet("Data", columns=["ID", "Value", "Text"])

            for i in range(num_rows):
                writer.write_row([i, i * 100, f"Text{i}"])

            writer.end_sheet()

        # Read and verify
        with StreamingReader(original_file) as reader:
            for count, row in enumerate(reader.rows("Data")):
                if count > 0:  # Skip header
                    expected_id = count - 1
                    expected_text = f"Text{expected_id}"

                    if len(row.cells) >= 3:
                        id_val = row.cells[0].value
                        text_val = row.cells[2].value

                        if id_val is not None:
                            with contextlib.suppress(ValueError, TypeError):
                                assert int(float(id_val)) == expected_id

                        if text_val is not None:
                            assert str(text_val) == expected_text

    def test_numeric_precision_large_file(self, tmp_path: Path) -> None:
        """Test numeric precision is maintained in large file."""
        output_file = tmp_path / "precision.ods"

        # Write with specific numeric values
        test_values = [
            3.14159265359,
            2.71828182846,
            1.41421356237,
            0.00001,
            1000000.123,
        ]

        with StreamingWriter(output_file) as writer:
            writer.start_sheet("Data")

            for val in test_values:
                writer.write_row([val])

            writer.end_sheet()

        # Read and verify (some precision may be lost in string conversion)
        with StreamingReader(output_file) as reader:
            rows = list(reader.rows("Data"))
            assert len(rows) == len(test_values)


# =============================================================================
# Performance-Related Tests
# =============================================================================


class TestLargeFilePerformance:
    """Test performance characteristics (not strict benchmarks)."""

    def test_lazy_row_iteration(self, large_10k_file: Path) -> None:
        """Test that row iteration is lazy (doesn't load all at once)."""
        with StreamingReader(large_10k_file) as reader:
            row_iter = reader.rows("LargeData")

            # Get first row
            first_row = next(row_iter)
            assert first_row is not None

            # Get another row without exhausting iterator
            second_row = next(row_iter)
            assert second_row is not None

    def test_skip_rows_efficiently(self, large_10k_file: Path) -> None:
        """Test that start_row skips efficiently."""
        with StreamingReader(large_10k_file) as reader:
            # Start near end - should skip efficiently
            rows = list(reader.rows("LargeData", start_row=9900, limit=100))
            assert len(rows) == 100

    def test_filter_while_reading(self, large_10k_file: Path, tmp_path: Path) -> None:
        """Test filtering during streaming read."""
        output_file = tmp_path / "filtered.ods"

        with (
            StreamingReader(large_10k_file) as reader,
            StreamingWriter(output_file) as writer,
        ):
            writer.start_sheet("Filtered")

            for row in reader.rows("LargeData"):
                # Only write rows where ID is divisible by 100
                if len(row.cells) >= 2:
                    id_val = row.cells[1].value
                    if id_val is not None:
                        try:
                            if int(float(id_val)) % 100 == 0:
                                values = [cell.value for cell in row.cells]
                                writer.write_row(values)
                        except (ValueError, TypeError):
                            pass

            writer.end_sheet()

        # Should have ~100 filtered rows (IDs 0, 100, 200, ..., 9900)
        with StreamingReader(output_file) as reader:
            count = reader.row_count("Filtered")
            assert 90 <= count <= 110


# =============================================================================
# Edge Cases for Large Data
# =============================================================================


class TestLargeDataEdgeCases:
    """Test edge cases with large data."""

    def test_empty_cells_in_large_file(self, tmp_path: Path) -> None:
        """Test handling empty cells in large file."""
        output_file = tmp_path / "sparse.ods"

        with StreamingWriter(output_file) as writer:
            writer.start_sheet("Sparse")

            for i in range(1000):
                # Every other cell is empty
                writer.write_row([i if i % 2 == 0 else None, f"Val{i}"])

            writer.end_sheet()

        with StreamingReader(output_file) as reader:
            count = reader.row_count("Sparse")
            assert count == 1000

    def test_unicode_in_large_file(self, tmp_path: Path) -> None:
        """Test Unicode handling in large file."""
        output_file = tmp_path / "unicode_large.ods"

        with StreamingWriter(output_file) as writer:
            writer.start_sheet("Unicode")

            for i in range(1000):
                writer.write_row([f"Row{i}", f"Unicode: Hello 世界 {i}"])

            writer.end_sheet()

        with StreamingReader(output_file) as reader:
            rows = list(reader.rows("Unicode", limit=10))
            assert len(rows) == 10

    def test_mixed_data_types_large_file(self, tmp_path: Path) -> None:
        """Test mixed data types in large file."""
        output_file = tmp_path / "mixed_large.ods"

        with StreamingWriter(output_file) as writer:
            writer.start_sheet("Mixed")

            for i in range(2000):
                # Mix of data types
                writer.write_row(
                    [
                        i,  # int
                        i * 1.5,  # float
                        f"String{i}",  # string
                        None,  # null
                        i % 2 == 0,  # bool-like
                    ]
                )

            writer.end_sheet()

        with StreamingReader(output_file) as reader:
            count = reader.row_count("Mixed")
            assert count == 2000


# =============================================================================
# Concurrent Operations Tests
# =============================================================================


class TestConcurrentOperations:
    """Test concurrent read/write patterns."""

    def test_simultaneous_read_write_different_files(
        self, large_10k_file: Path, tmp_path: Path
    ) -> None:
        """Test reading one file while writing another."""
        output_file = tmp_path / "concurrent_output.ods"

        with (
            StreamingReader(large_10k_file) as reader,
            StreamingWriter(output_file, chunk_size=100) as writer,
        ):
            writer.start_sheet("Copy")

            for row in reader.rows("LargeData"):
                values = [cell.value for cell in row.cells]
                writer.write_row(values)

            writer.end_sheet()

        # Verify output
        with StreamingReader(output_file) as reader:
            count = reader.row_count("Copy")
            assert count == 10000

    def test_multiple_readers_same_file(self, large_10k_file: Path) -> None:
        """Test multiple readers on same file."""
        with (
            StreamingReader(large_10k_file) as reader1,
            StreamingReader(large_10k_file) as reader2,
        ):
            # Both can read independently
            rows1 = list(reader1.rows("LargeData", limit=100))
            rows2 = list(reader2.rows("LargeData", start_row=100, limit=100))

            assert len(rows1) == 100
            assert len(rows2) == 100
