"""Streaming I/O for large spreadsheet files.

Provides row-by-row reading and chunk-by-chunk writing to handle
spreadsheets with 100k+ rows without excessive memory usage.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Use defusedxml if available for security (protects against XXE/Billion Laughs)
# Falls back to standard library if defusedxml not installed
try:
    from defusedxml import ElementTree as ET
except ImportError:
    import warnings
    import xml.etree.ElementTree as ET

    warnings.warn(
        "defusedxml not installed. XML parsing is vulnerable to XXE and "
        "billion laughs attacks. Install defusedxml: pip install defusedxml",
        UserWarning,
        stacklevel=2,
    )

from spreadsheet_dl.progress import BatchProgress

if TYPE_CHECKING:
    from collections.abc import Iterator

# ODF Namespaces
ODF_NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
}


@dataclass
class StreamingCell:
    """Lightweight cell representation for streaming.

    Memory-efficient cell structure for streaming I/O.

    Attributes:
        value: Cell value (string, number, date string)
        value_type: ODF value type (string, float, date, currency, percentage)
        formula: Optional formula
        style: Optional style name
    """

    value: Any = None
    value_type: str = "string"
    formula: str | None = None
    style: str | None = None

    def is_empty(self) -> bool:
        """Check if cell is empty."""
        return self.value is None and self.formula is None


@dataclass
class StreamingRow:
    """Lightweight row representation for streaming.

    Memory-efficient row structure for streaming I/O.

    Attributes:
        cells: List of cells in the row
        style: Optional row style
        row_index: Row index (0-based)
    """

    cells: list[StreamingCell] = field(default_factory=list)
    style: str | None = None
    row_index: int = 0

    def __len__(self) -> int:
        """Return number of cells."""
        return len(self.cells)

    def __iter__(self) -> Iterator[StreamingCell]:
        """Iterate over cells."""
        return iter(self.cells)


class StreamingReader:
    """Stream-based ODS file reader for large files.

    Reads ODS files row-by-row without loading the entire file into memory.
    Supports files with 100k+ rows efficiently.

    Examples:
        # Read rows one at a time
        with StreamingReader("large_file.ods") as reader:
            for sheet_name in reader.sheet_names():
                for row in reader.rows(sheet_name):
                    process_row(row)

        # Read specific sheet
        reader = StreamingReader("file.ods")
        for row in reader.rows("Data", start_row=1000, limit=100):
            print(row)

        # Get row count without loading all data
        count = reader.row_count("Sheet1")
    """

    def __init__(self, file_path: Path | str) -> None:
        """Initialize streaming reader.

        Args:
            file_path: Path to ODS file
        """
        self._file_path = Path(file_path)
        self._zipfile: zipfile.ZipFile | None = None
        self._content_xml: ET.Element | None = None
        self._sheet_cache: dict[str, ET.Element] = {}

    def __enter__(self) -> StreamingReader:
        """Context manager entry."""
        self.open()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def open(self) -> None:
        """Open the ODS file for reading.

        Implements ZIP bomb detection to prevent denial of service attacks.
        """
        if not self._file_path.exists():
            raise FileNotFoundError(f"File not found: {self._file_path}")

        self._zipfile = zipfile.ZipFile(self._file_path, "r")

        # ZIP bomb detection (prevents DoS attacks)
        self._check_zip_bomb()

        # Parse content.xml
        with self._zipfile.open("content.xml") as content_file:
            self._content_xml = ET.parse(content_file).getroot()

    def _check_zip_bomb(self) -> None:
        """Check for ZIP bomb attack.

        Validates:
        - Total uncompressed size < 100MB
        - Compression ratio < 100:1 for any file
        - File count < 10000

        Raises:
            ValueError: If ZIP file appears to be a ZIP bomb
        """
        if not self._zipfile:
            return

        # Security limits
        MAX_UNCOMPRESSED_SIZE = 100 * 1024 * 1024  # 100MB
        MAX_COMPRESSION_RATIO = 100  # 100:1
        MAX_FILE_COUNT = 10000

        total_size = 0

        for file_count, info in enumerate(self._zipfile.infolist(), start=1):
            total_size += info.file_size

            # Check total uncompressed size
            if total_size > MAX_UNCOMPRESSED_SIZE:
                msg = (
                    f"ZIP file too large: {total_size} bytes uncompressed "
                    f"(max {MAX_UNCOMPRESSED_SIZE}). Possible ZIP bomb attack."
                )
                raise ValueError(msg)

            # Check compression ratio (ZIP bomb detection)
            if info.compress_size > 0:
                ratio = info.file_size / info.compress_size
                if ratio > MAX_COMPRESSION_RATIO:
                    msg = (
                        f"Suspicious compression ratio for {info.filename}: {ratio:.1f}:1 "
                        f"(max {MAX_COMPRESSION_RATIO}:1). Possible ZIP bomb attack."
                    )
                    raise ValueError(msg)

            # Check file count (nested ZIP bomb)
            if file_count > MAX_FILE_COUNT:
                msg = (
                    f"Too many files in ZIP: {file_count} "
                    f"(max {MAX_FILE_COUNT}). Possible nested ZIP bomb."
                )
                raise ValueError(msg)

    def close(self) -> None:
        """Close the ODS file."""
        if self._zipfile:
            self._zipfile.close()
            self._zipfile = None
        self._content_xml = None
        self._sheet_cache.clear()

    def sheet_names(self) -> list[str]:
        """Get list of sheet names.

        Returns:
            List of sheet names in the document
        """
        if self._content_xml is None:
            raise RuntimeError("File not opened. Call open() first.")

        names = []
        for table in self._content_xml.iter(f"{{{ODF_NS['table']}}}table"):
            name = table.get(f"{{{ODF_NS['table']}}}name")
            if name:
                names.append(name)
        return names

    def row_count(self, sheet_name: str) -> int:
        """Get row count for a sheet without loading all rows.

        Args:
            sheet_name: Name of the sheet

        Returns:
            Number of rows in the sheet
        """
        table = self._get_table(sheet_name)
        if table is None:
            return 0

        count = 0
        for _ in table.iter(f"{{{ODF_NS['table']}}}table-row"):
            count += 1
        return count

    def column_count(self, sheet_name: str) -> int:
        """Get column count for a sheet.

        Args:
            sheet_name: Name of the sheet

        Returns:
            Number of columns in the sheet
        """
        table = self._get_table(sheet_name)
        if table is None:
            return 0

        count = 0
        for _ in table.iter(f"{{{ODF_NS['table']}}}table-column"):
            count += 1
        return count

    def rows(
        self,
        sheet_name: str,
        start_row: int = 0,
        limit: int | None = None,
    ) -> Iterator[StreamingRow]:
        """Iterate over rows in a sheet.

        Row-by-row iteration for memory efficiency.

        Args:
            sheet_name: Name of the sheet to read
            start_row: Starting row index (0-based)
            limit: Maximum number of rows to return (None for all)

        Yields:
            StreamingRow for each row in the specified range
        """
        table = self._get_table(sheet_name)
        if table is None:
            return

        row_idx = 0
        yielded = 0

        for row_elem in table.iter(f"{{{ODF_NS['table']}}}table-row"):
            if row_idx < start_row:
                row_idx += 1
                continue

            if limit is not None and yielded >= limit:
                return

            yield self._parse_row(row_elem, row_idx)
            row_idx += 1
            yielded += 1

    def _get_table(self, sheet_name: str) -> ET.Element | None:
        """Get table element by sheet name."""
        if self._content_xml is None:
            raise RuntimeError("File not opened. Call open() first.")

        if sheet_name in self._sheet_cache:
            return self._sheet_cache[sheet_name]

        for table in self._content_xml.iter(f"{{{ODF_NS['table']}}}table"):
            name = table.get(f"{{{ODF_NS['table']}}}name")
            if name == sheet_name:
                self._sheet_cache[sheet_name] = table
                return table
        return None

    def _parse_row(self, row_elem: ET.Element, row_idx: int) -> StreamingRow:
        """Parse a table-row element into a StreamingRow."""
        cells = []
        style = row_elem.get(f"{{{ODF_NS['table']}}}style-name")

        for cell_elem in row_elem:
            tag = cell_elem.tag
            if tag == f"{{{ODF_NS['table']}}}table-cell":
                cells.append(self._parse_cell(cell_elem))
            elif tag == f"{{{ODF_NS['table']}}}covered-table-cell":
                # Covered cell (part of merged region)
                cells.append(StreamingCell())

        return StreamingRow(cells=cells, style=style, row_index=row_idx)

    def _parse_cell(self, cell_elem: ET.Element) -> StreamingCell:
        """Parse a table-cell element into a StreamingCell."""
        # Get value type
        value_type = cell_elem.get(f"{{{ODF_NS['office']}}}value-type", "string")

        # Get value based on type
        value: Any = None
        if value_type == "float":
            value_str = cell_elem.get(f"{{{ODF_NS['office']}}}value")
            if value_str:
                value = float(value_str)
        elif value_type == "date":
            value = cell_elem.get(f"{{{ODF_NS['office']}}}date-value")
        elif value_type == "currency" or value_type == "percentage":
            value_str = cell_elem.get(f"{{{ODF_NS['office']}}}value")
            if value_str:
                value = float(value_str)
        else:
            # String or other - get text content
            text_p = cell_elem.find(f"{{{ODF_NS['text']}}}p")
            if text_p is not None and text_p.text:
                value = text_p.text

        # Get formula if present
        formula = cell_elem.get(f"{{{ODF_NS['table']}}}formula")

        # Get style
        style = cell_elem.get(f"{{{ODF_NS['table']}}}style-name")

        return StreamingCell(
            value=value,
            value_type=value_type,
            formula=formula,
            style=style,
        )


class StreamingWriter:
    """Stream-based ODS file writer for large files.

    Writes ODS files chunk-by-chunk without holding the entire spreadsheet
    in memory. Supports generating files with 100k+ rows efficiently.

    Examples:
        # Write rows in chunks
        with StreamingWriter("large_output.ods") as writer:
            writer.start_sheet("Data", columns=["A", "B", "C"])
            for chunk in data_generator():
                for row in chunk:
                    writer.write_row(row)
            writer.end_sheet()

        # Multiple sheets
        with StreamingWriter("multi_sheet.ods") as writer:
            writer.start_sheet("Sheet1")
            writer.write_rows(rows1)
            writer.end_sheet()

            writer.start_sheet("Sheet2")
            writer.write_rows(rows2)
            writer.end_sheet()
    """

    CHUNK_SIZE = 1000  # Default rows per chunk

    def __init__(
        self,
        file_path: Path | str,
        chunk_size: int = CHUNK_SIZE,
    ) -> None:
        """Initialize streaming writer.

        Args:
            file_path: Path for output ODS file
            chunk_size: Number of rows to buffer before flushing
        """
        self._file_path = Path(file_path)
        self._chunk_size = chunk_size
        self._buffer: list[StreamingRow] = []
        self._current_sheet: str | None = None
        self._sheets: list[dict[str, Any]] = []
        self._row_count = 0

    def __enter__(self) -> StreamingWriter:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - finalize and save."""
        self.close()

    def start_sheet(
        self,
        name: str,
        columns: list[str] | None = None,
    ) -> StreamingWriter:
        """Start a new sheet.

        Args:
            name: Sheet name
            columns: Optional column headers

        Returns:
            Self for chaining
        """
        if self._current_sheet is not None:
            self.end_sheet()

        self._current_sheet = name
        self._buffer = []
        self._row_count = 0

        # Store sheet metadata
        sheet_data: dict[str, Any] = {
            "name": name,
            "columns": columns or [],
            "rows": [],
        }
        self._sheets.append(sheet_data)

        # Add header row if columns provided
        if columns:
            header_cells = [StreamingCell(value=col) for col in columns]
            self._buffer.append(StreamingRow(cells=header_cells))
            self._row_count += 1

        return self

    def end_sheet(self) -> StreamingWriter:
        """End the current sheet.

        Returns:
            Self for chaining
        """
        if self._current_sheet is None:
            return self

        # Flush remaining buffer
        self._flush_buffer()
        self._current_sheet = None
        return self

    def write_row(self, row: StreamingRow | list[Any]) -> StreamingWriter:
        """Write a single row.

        Args:
            row: StreamingRow or list of cell values

        Returns:
            Self for chaining
        """
        if self._current_sheet is None:
            raise RuntimeError("No active sheet. Call start_sheet() first.")

        if isinstance(row, list):
            cells = [
                StreamingCell(value=v) if not isinstance(v, StreamingCell) else v
                for v in row
            ]
            row = StreamingRow(cells=cells, row_index=self._row_count)

        self._buffer.append(row)
        self._row_count += 1

        if len(self._buffer) >= self._chunk_size:
            self._flush_buffer()

        return self

    def write_rows(self, rows: list[StreamingRow] | list[list[Any]]) -> StreamingWriter:
        """Write multiple rows.

        Args:
            rows: List of StreamingRows or lists of cell values

        Returns:
            Self for chaining
        """
        for row in rows:
            self.write_row(row)
        return self

    def _flush_buffer(self) -> None:
        """Flush buffered rows to current sheet data."""
        if not self._buffer or not self._sheets:
            return

        current_sheet = self._sheets[-1]
        current_sheet["rows"].extend(self._buffer)
        self._buffer = []

    def close(self) -> Path:
        """Finalize and save the ODS file.

        Returns:
            Path to the created file
        """
        # End any active sheet
        if self._current_sheet is not None:
            self.end_sheet()

        # Generate ODS file
        self._generate_ods()
        return self._file_path

    def _generate_ods(self) -> None:
        """Generate the ODS file from accumulated data."""
        from spreadsheet_dl.builder import (
            CellSpec,
            ColumnSpec,
            RowSpec,
            SheetSpec,
        )
        from spreadsheet_dl.renderer import render_sheets

        # Convert accumulated data to SheetSpecs
        sheets = []

        # Count total rows for progress
        total_rows = sum(len(sheet_data["rows"]) for sheet_data in self._sheets)
        use_progress = total_rows > 100

        if use_progress:
            with BatchProgress(total_rows, "Generating ODS file") as progress:
                for sheet_data in self._sheets:
                    columns = [ColumnSpec(name=col) for col in sheet_data["columns"]]

                    rows = []
                    for streaming_row in sheet_data["rows"]:
                        cells = []
                        for cell in streaming_row.cells:
                            cells.append(
                                CellSpec(
                                    value=cell.value,
                                    value_type=cell.value_type,
                                    formula=cell.formula,
                                    style=cell.style,
                                )
                            )
                        rows.append(RowSpec(cells=cells, style=streaming_row.style))
                        progress.update()

                    sheets.append(
                        SheetSpec(name=sheet_data["name"], columns=columns, rows=rows)
                    )
        else:
            for sheet_data in self._sheets:
                columns = [ColumnSpec(name=col) for col in sheet_data["columns"]]

                rows = []
                for streaming_row in sheet_data["rows"]:
                    cells = []
                    for cell in streaming_row.cells:
                        cells.append(
                            CellSpec(
                                value=cell.value,
                                value_type=cell.value_type,
                                formula=cell.formula,
                                style=cell.style,
                            )
                        )
                    rows.append(RowSpec(cells=cells, style=streaming_row.style))

                sheets.append(
                    SheetSpec(name=sheet_data["name"], columns=columns, rows=rows)
                )

        # Render to file
        render_sheets(sheets, self._file_path)


def stream_read(file_path: Path | str) -> StreamingReader:
    """Create a streaming reader for an ODS file.

    Convenience function for StreamingReader.

    Args:
        file_path: Path to ODS file

    Returns:
        StreamingReader instance (not opened - use with context manager)
    """
    return StreamingReader(file_path)


def stream_write(file_path: Path | str, chunk_size: int = 1000) -> StreamingWriter:
    """Create a streaming writer for an ODS file.

    Convenience function for StreamingWriter.

    Args:
        file_path: Path for output file
        chunk_size: Rows to buffer before flush

    Returns:
        StreamingWriter instance
    """
    return StreamingWriter(file_path, chunk_size)
