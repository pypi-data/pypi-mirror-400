"""Lab Results Importer.

LabResultsImporter for environmental domain
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


@dataclass
class LabResultsImporter(BaseImporter[list[dict[str, Any]]]):
    """Laboratory analysis results importer.

        LabResultsImporter for environmental lab data

    Supports importing data from:
    - Environmental lab reports (CSV)
    - Water/soil/air quality analysis
    - Chain of custody records

    Example:
        >>> importer = LabResultsImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("lab_results.csv")  # doctest: +SKIP
        >>> print(f"Imported {result.records_imported} lab results")  # doctest: +SKIP
    """

    lab_name: str = ""
    validate_detection_limits: bool = True

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata."""
        return ImporterMetadata(
            name="Lab Results Importer",
            description="Import environmental laboratory analysis results",
            supported_formats=("csv", "xlsx"),
            category="environmental",
        )

    def import_data(self, source: str | Path) -> ImportResult[list[dict[str, Any]]]:
        """Import lab results from file."""
        source_path = Path(source)
        data: list[dict[str, Any]] = []
        errors: list[str] = []
        warnings: list[str] = []

        if not source_path.exists():
            return ImportResult(
                success=False,
                data=[],
                records_imported=0,
                errors=[f"File not found: {source_path}"],
                warnings=[],
                metadata={},
            )

        suffix = source_path.suffix.lower()

        try:
            if suffix == ".csv":
                data, errors, warnings = self._import_csv(source_path)
            else:
                return ImportResult(
                    success=False,
                    data=[],
                    records_imported=0,
                    errors=[f"Unsupported format: {suffix}"],
                    warnings=[],
                    metadata={},
                )

            return ImportResult(
                success=len(errors) == 0,
                data=data,
                records_imported=len(data),
                errors=errors,
                warnings=warnings,
                metadata={"lab_name": self.lab_name, "source": str(source_path)},
            )

        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                records_imported=0,
                errors=[f"Import error: {e!s}"],
                warnings=[],
                metadata={},
            )

    def _import_csv(
        self, path: Path
    ) -> tuple[list[dict[str, Any]], list[str], list[str]]:
        """Import from CSV file."""
        data: list[dict[str, Any]] = []
        errors: list[str] = []
        warnings: list[str] = []

        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                record = self._normalize_record(row)
                data.append(record)

                # Check for non-detect values
                if self.validate_detection_limits:
                    row_warnings = self._check_detection_limits(record, row_num)
                    warnings.extend(row_warnings)

        return data, errors, warnings

    def _normalize_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Normalize lab result fields."""
        normalized: dict[str, Any] = {}

        field_mappings = {
            "sample_id": "sample_id",
            "sample id": "sample_id",
            "lab_id": "lab_id",
            "lab id": "lab_id",
            "parameter": "parameter",
            "analyte": "parameter",
            "result": "result",
            "value": "result",
            "unit": "unit",
            "units": "unit",
            "detection_limit": "detection_limit",
            "mdl": "detection_limit",
            "method": "method",
            "analysis_date": "analysis_date",
            "date": "analysis_date",
        }

        for key, value in record.items():
            normalized_key = field_mappings.get(key.lower(), key.lower())

            # Handle non-detect markers
            if normalized_key == "result" and isinstance(value, str):
                if value.startswith("<") or value.upper() in ("ND", "BDL"):
                    normalized["non_detect"] = True
                    # Extract numeric value if present
                    if value.startswith("<"):
                        try:
                            normalized["result"] = float(value[1:].strip())
                        except ValueError:
                            normalized["result"] = value
                    else:
                        normalized["result"] = 0
                else:
                    normalized["non_detect"] = False
                    try:
                        normalized["result"] = float(value)
                    except ValueError:
                        normalized["result"] = value
            else:
                normalized[normalized_key] = value

        return normalized

    def _check_detection_limits(
        self, record: dict[str, Any], row_num: int
    ) -> list[str]:
        """Check for detection limit issues."""
        warnings: list[str] = []

        if record.get("non_detect"):
            warnings.append(
                f"Row {row_num}: Non-detect result for {record.get('parameter', 'unknown')}"
            )

        return warnings

    def validate_source(self, source: str | Path) -> bool:
        """Validate source file."""
        path = Path(source)
        return path.exists() and path.suffix.lower() in (".csv", ".xlsx")


__all__ = ["LabResultsImporter"]
