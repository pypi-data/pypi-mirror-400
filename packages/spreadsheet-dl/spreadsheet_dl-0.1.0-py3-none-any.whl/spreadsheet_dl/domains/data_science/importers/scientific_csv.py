"""Scientific CSV importer with automatic type detection.

ScientificCSVImporter for data science domain
"""

from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


class ScientificCSVImporter(BaseImporter[list[dict[str, Any]]]):
    """Scientific CSV importer with type inference and scientific notation support.

        ScientificCSVImporter with auto-type detection

    Features:
    - Automatic delimiter detection (comma, tab, semicolon)
    - Type inference (int, float, string, datetime)
    - Scientific notation parsing (1.23e-5)
    - Header detection
    - Missing value handling
    - Encoding detection (UTF-8, Latin-1)

    Example:
        >>> importer = ScientificCSVImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("experiment_data.csv")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     print(f"Imported {result.records_imported} records")
        ...     for record in result.data:
        ...         print(record)
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize importer."""
        super().__init__(**kwargs)

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata.

        Returns:
            ImporterMetadata for scientific CSV importer

            Importer metadata
        """
        return ImporterMetadata(
            name="Scientific CSV Importer",
            description="Import CSV files with scientific notation and automatic type detection",
            supported_formats=("csv", "tsv", "txt"),
            category="data_science",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate CSV source file.

        Args:
            source: Path to CSV file

        Returns:
            True if source is valid CSV file

            Source validation
        """
        path = Path(source) if isinstance(source, str) else source
        return (
            path.exists()
            and path.is_file()
            and path.suffix.lower() in (".csv", ".tsv", ".txt")
        )

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import data from CSV file.

        Args:
            source: Path to CSV file

        Returns:
            ImportResult with parsed data

            Data import with type inference

        Raises:
            ValueError: If source is invalid
            IOError: If file cannot be read
        """
        if not self.validate_source(source):
            return ImportResult(
                success=False,
                data=[],
                errors=["Invalid CSV file or file does not exist"],
            )

        path = Path(source) if isinstance(source, str) else source

        try:
            # Detect delimiter
            delimiter = self._detect_delimiter(path)

            # Read CSV with detected delimiter
            records = []
            headers: list[str] = []

            with path.open("r", encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f, delimiter=delimiter)

                # Read header
                try:
                    headers = next(reader)
                except StopIteration:
                    return ImportResult(
                        success=False,
                        data=[],
                        errors=["Empty CSV file"],
                    )

                # Read data rows
                for row_idx, row in enumerate(reader):
                    if len(row) == 0:
                        continue  # Skip empty rows

                    # Pad row if shorter than headers
                    while len(row) < len(headers):
                        row.append("")

                    # Convert row to dict with type inference
                    record = {}
                    for header, value in zip(headers, row, strict=False):
                        record[header] = self._infer_type(value)

                    records.append(record)
                    self.on_progress(row_idx + 1, len(records))

            return ImportResult(
                success=True,
                data=records,
                records_imported=len(records),
                metadata={
                    "delimiter": delimiter,
                    "headers": headers,
                    "columns": len(headers),
                },
            )

        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"Error reading CSV: {e!s}"],
            )

    def _detect_delimiter(self, path: Path) -> str:
        """Detect CSV delimiter.

        Args:
            path: Path to CSV file

        Returns:
            Detected delimiter character
        """
        with path.open("r", encoding="utf-8", errors="replace") as f:
            # Read first line
            first_line = f.readline()

            # Count occurrences of common delimiters
            comma_count = first_line.count(",")
            tab_count = first_line.count("\t")
            semicolon_count = first_line.count(";")

            # Return most common
            if tab_count > comma_count and tab_count > semicolon_count:
                return "\t"
            elif semicolon_count > comma_count:
                return ";"
            else:
                return ","

    def _infer_type(self, value: str) -> Any:
        """Infer type of value and convert.

        Args:
            value: String value to convert

        Returns:
            Converted value (int, float, datetime, or str)

            Type inference with scientific notation support
        """
        # Handle empty values
        if not value or value.strip() in ("", "NA", "N/A", "null", "NULL", "None"):
            return None

        value = value.strip()

        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float (including scientific notation)
        try:
            # Scientific notation pattern: 1.23e-5, 4.56E+10
            if re.match(r"^-?\d+\.?\d*[eE][+-]?\d+$", value):
                return float(value)
            # Regular float
            return float(value)
        except ValueError:
            pass

        # Try datetime (common formats)
        for fmt in (
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
        ):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        # Return as string if no conversion succeeded
        return value


__all__ = ["ScientificCSVImporter"]
