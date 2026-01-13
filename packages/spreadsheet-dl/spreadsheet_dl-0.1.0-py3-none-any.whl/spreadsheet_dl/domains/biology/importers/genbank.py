"""GenBank format sequence file importer.

GenBankImporter for annotated sequences
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


class GenBankImporter(BaseImporter[list[dict[str, Any]]]):
    """Import GenBank format sequence files.

        GenBankImporter for annotated sequence data

    Features:
    - GenBank flat file format parsing
    - Sequence metadata extraction (accession, organism, etc.)
    - Feature annotation parsing (genes, CDS, etc.)
    - Sequence extraction
    - Multi-record file support

    Example:
        >>> importer = GenBankImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("sequence.gb")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     for record in result.data:
        ...         print(f"{record['accession']}: {record['organism']}")
        ...         print(f"Features: {len(record['features'])}")
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize importer."""
        super().__init__(**kwargs)

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata.

        Returns:
            ImporterMetadata for GenBank importer

            Importer metadata
        """
        return ImporterMetadata(
            name="GenBank Importer",
            description="Import GenBank format sequence files with annotations",
            supported_formats=("gb", "gbk", "genbank", "txt"),
            category="biology",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate GenBank file.

        Args:
            source: Path to GenBank file

        Returns:
            True if source is valid GenBank file

            Source validation
        """
        path = Path(source) if isinstance(source, str) else source
        if not path.exists() or not path.is_file():
            return False

        # Check if file contains GenBank format indicators
        try:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                content = f.read(500)  # Read first 500 chars
                return "LOCUS" in content or "ACCESSION" in content
        except OSError:
            # File access errors
            return False

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import GenBank records.

        Args:
            source: Path to GenBank file

        Returns:
            ImportResult with sequence records and annotations

            GenBank data import

        Raises:
            ValueError: If source is invalid
            IOError: If file cannot be read
        """
        if not self.validate_source(source):
            return ImportResult(
                success=False,
                data=[],
                errors=["Invalid GenBank file or file does not exist"],
            )

        path = Path(source) if isinstance(source, str) else source

        try:
            records: list[dict[str, Any]] = []
            warnings: list[str] = []

            with path.open("r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Split into individual records (separated by //)
            raw_records = content.split("//")

            for record_text in raw_records:
                if not record_text.strip():
                    continue

                record = self._parse_genbank_record(record_text)
                if record:
                    records.append(record)

            if not records:
                return ImportResult(
                    success=False,
                    data=[],
                    errors=["No valid GenBank records found"],
                )

            self.on_progress(len(records), len(records))

            return ImportResult(
                success=True,
                data=records,
                records_imported=len(records),
                warnings=warnings,
                metadata={
                    "total_records": len(records),
                },
            )

        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"Error reading GenBank file: {e!s}"],
            )

    def _parse_genbank_record(self, text: str) -> dict[str, Any] | None:
        """Parse a single GenBank record.

        Args:
            text: GenBank record text

        Returns:
            Dictionary with record data or None if parsing fails
        """
        if not text.strip():
            return None

        record: dict[str, Any] = {
            "locus": "",
            "accession": "",
            "version": "",
            "organism": "",
            "definition": "",
            "length": 0,
            "features": [],
            "sequence": "",
        }

        lines = text.split("\n")

        # Parse metadata fields
        current_field = ""
        for line in lines:
            # LOCUS line
            if line.startswith("LOCUS"):
                match = re.search(r"LOCUS\s+(\S+)\s+(\d+)\s+bp", line)
                if match:
                    record["locus"] = match.group(1)
                    record["length"] = int(match.group(2))

            # ACCESSION line
            elif line.startswith("ACCESSION"):
                record["accession"] = line.split(None, 1)[1].strip()

            # VERSION line
            elif line.startswith("VERSION"):
                record["version"] = line.split(None, 1)[1].strip()

            # DEFINITION line (can be multi-line)
            elif line.startswith("DEFINITION"):
                record["definition"] = line.split(None, 1)[1].strip()
                current_field = "definition"

            # ORGANISM line
            elif "ORGANISM" in line:
                parts = line.split("ORGANISM", 1)
                if len(parts) > 1:
                    record["organism"] = parts[1].strip()

            # FEATURES section
            elif line.startswith("FEATURES"):
                current_field = "features"

            # ORIGIN section (sequence data)
            elif line.startswith("ORIGIN"):
                current_field = "sequence"

            # Continuation of multi-line field
            elif current_field == "definition" and line.startswith(" " * 12):
                record["definition"] += " " + line.strip()

            # Parse features (simplified)
            elif current_field == "features" and line.startswith("     "):
                # This is a simplified feature parser
                feature_match = re.match(r"\s+(\w+)\s+(.+)", line)
                if feature_match:
                    feature_type = feature_match.group(1)
                    location = feature_match.group(2)
                    record["features"].append(
                        {
                            "type": feature_type,
                            "location": location,
                        }
                    )

            # Parse sequence
            elif current_field == "sequence" and re.match(r"^\s+\d+", line):
                # Remove numbers and whitespace from sequence lines
                seq_line = re.sub(r"\d+|\s+", "", line)
                record["sequence"] += seq_line.upper()

        return record if record["accession"] or record["locus"] else None


__all__ = ["GenBankImporter"]
