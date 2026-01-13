"""MES Data Importer for Manufacturing Execution System data.

MESDataImporter for manufacturing domain
"""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


class MESDataImporter(BaseImporter[list[dict[str, Any]]]):
    """Import MES (Manufacturing Execution System) data (CSV/JSON).

        MESDataImporter with production and quality data

    Features:
    - Production order data import
    - Work center performance metrics
    - Material consumption tracking
    - Quality inspection results
    - Equipment status and downtime
    - CSV and JSON format support

    Example:
        >>> importer = MESDataImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("mes_export.csv")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     print(f"Imported {result.records_imported} MES records")
        ...     for record in result.data:
        ...         print(f"WO: {record['work_order']}, Status: {record['status']}")
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize importer."""
        super().__init__(**kwargs)

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata.

        Returns:
            ImporterMetadata for MES data importer

            Importer metadata
        """
        return ImporterMetadata(
            name="MES Data Importer",
            description="Import MES production and quality data from CSV/JSON",
            supported_formats=("csv", "json"),
            category="manufacturing",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate MES data source file.

        Args:
            source: Path to MES data file

        Returns:
            True if source is valid file

            Source validation
        """
        path = Path(source) if isinstance(source, str) else source
        return (
            path.exists()
            and path.is_file()
            and path.suffix.lower() in (".csv", ".json")
        )

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import data from MES file.

        Args:
            source: Path to MES data file (CSV or JSON)

        Returns:
            ImportResult with parsed MES data

            Data import with error handling

        Raises:
            ValueError: If source is invalid
            IOError: If file cannot be read
        """
        if not self.validate_source(source):
            return ImportResult(
                success=False,
                data=[],
                errors=["Invalid MES data file or file does not exist"],
            )

        path = Path(source) if isinstance(source, str) else source

        try:
            if path.suffix.lower() == ".json":
                return self._import_json(path)
            else:
                return self._import_csv(path)
        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"Error importing MES data: {e!s}"],
            )

    def _import_csv(self, path: Path) -> ImportResult[list[dict[str, Any]]]:
        """Import MES data from CSV file."""
        records = []
        errors = []

        try:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)

                for row_idx, row in enumerate(reader):
                    try:
                        record = self._parse_mes_record(row)
                        records.append(record)
                        self.on_progress(row_idx + 1, len(records))
                    except Exception as e:
                        errors.append(f"Row {row_idx + 1}: {e!s}")
                        continue

            return ImportResult(
                success=True,
                data=records,
                records_imported=len(records),
                errors=errors,
                metadata={
                    "source_file": str(path),
                    "format": "csv",
                    "import_date": datetime.now().isoformat(),
                },
            )
        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"CSV read error: {e!s}"],
            )

    def _import_json(self, path: Path) -> ImportResult[list[dict[str, Any]]]:
        """Import MES data from JSON file."""
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle both array and object with records key
            if isinstance(data, dict) and "records" in data:
                raw_records = data["records"]
            elif isinstance(data, list):
                raw_records = data
            else:
                return ImportResult(
                    success=False,
                    data=[],
                    errors=[
                        "Invalid JSON structure: expected array or {records: [...]}"
                    ],
                )

            records = []
            errors = []

            for idx, raw_record in enumerate(raw_records):
                try:
                    record = self._parse_mes_record(raw_record)
                    records.append(record)
                    self.on_progress(idx + 1, len(raw_records))
                except Exception as e:
                    errors.append(f"Record {idx + 1}: {e!s}")
                    continue

            return ImportResult(
                success=True,
                data=records,
                records_imported=len(records),
                errors=errors,
                metadata={
                    "source_file": str(path),
                    "format": "json",
                    "import_date": datetime.now().isoformat(),
                },
            )
        except json.JSONDecodeError as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"JSON parse error: {e!s}"],
            )
        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"Error reading JSON: {e!s}"],
            )

    def _parse_mes_record(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Parse MES record with type conversion.

        Args:
            raw: Raw record data

        Returns:
            Parsed MES record with standardized fields

            MES record parsing
        """
        # Standardize field names (handle various MES system formats)
        record: dict[str, Any] = {
            "work_order": str(raw.get("work_order", raw.get("wo_number", ""))),
            "product_id": str(raw.get("product_id", raw.get("part_number", ""))),
            "quantity_planned": self._parse_number(raw.get("quantity_planned", 0)),
            "quantity_produced": self._parse_number(raw.get("quantity_produced", 0)),
            "quantity_good": self._parse_number(raw.get("quantity_good", 0)),
            "quantity_scrap": self._parse_number(raw.get("quantity_scrap", 0)),
            "start_time": raw.get("start_time", ""),
            "end_time": raw.get("end_time", ""),
            "status": str(raw.get("status", "unknown")),
            "work_center": str(raw.get("work_center", raw.get("machine", ""))),
            "operator": str(raw.get("operator", "")),
        }

        # Add any additional fields
        for key, value in raw.items():
            if key not in record:
                record[key] = value

        return record

    def _parse_number(self, value: Any) -> float:
        """Parse numeric value safely."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.replace(",", ""))
            except ValueError:
                return 0.0
        return 0.0


__all__ = ["MESDataImporter"]
