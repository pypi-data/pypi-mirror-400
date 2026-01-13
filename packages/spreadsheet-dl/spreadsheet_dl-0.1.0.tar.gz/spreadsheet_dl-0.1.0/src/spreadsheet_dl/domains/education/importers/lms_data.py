"""LMS Data Importer.

LMSDataImporter for education domain
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


@dataclass
class LMSDataImporter(BaseImporter[list[dict[str, Any]]]):
    """Learning Management System data importer.

        LMSDataImporter for Canvas, Moodle, Blackboard exports

    Supports importing data from various LMS platforms:
    - Canvas CSV exports
    - Moodle gradebook exports
    - Blackboard data dumps
    - Generic LMS JSON/CSV formats

    Example:
        >>> importer = LMSDataImporter(platform="canvas")  # doctest: +SKIP
        >>> result = importer.import_data("grades_export.csv")  # doctest: +SKIP
        >>> print(f"Imported {result.records_imported} student records")  # doctest: +SKIP
    """

    platform: str = "generic"
    normalize_names: bool = True
    date_format: str = "%Y-%m-%d"

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata.

        Returns:
            ImporterMetadata for LMS data importer

            Importer metadata
        """
        return ImporterMetadata(
            name="LMS Data Importer",
            description="Import data from Learning Management Systems",
            supported_formats=("csv", "json", "xlsx"),
            category="education",
        )

    def import_data(self, source: str | Path) -> ImportResult[list[dict[str, Any]]]:
        """Import LMS data from file.

        Args:
            source: Path to LMS export file

        Returns:
            ImportResult with student data

            LMS data import
        """
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
            elif suffix == ".json":
                data, errors, warnings = self._import_json(source_path)
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
                metadata={
                    "platform": self.platform,
                    "source_file": str(source_path),
                    "format": suffix,
                },
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

                # Validate record
                if not record.get("student_id") and not record.get("name"):
                    warnings.append(f"Row {row_num}: Missing student identifier")

        return data, errors, warnings

    def _import_json(
        self, path: Path
    ) -> tuple[list[dict[str, Any]], list[str], list[str]]:
        """Import from JSON file."""
        data: list[dict[str, Any]] = []
        errors: list[str] = []
        warnings: list[str] = []

        with open(path, encoding="utf-8") as f:
            content = json.load(f)

        if isinstance(content, list):
            for record in content:
                data.append(self._normalize_record(record))
        elif isinstance(content, dict):
            # Handle wrapped data
            if "students" in content:
                for record in content["students"]:
                    data.append(self._normalize_record(record))
            elif "data" in content:
                for record in content["data"]:
                    data.append(self._normalize_record(record))
            else:
                data.append(self._normalize_record(content))

        return data, errors, warnings

    def _normalize_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Normalize field names across different LMS platforms."""
        normalized: dict[str, Any] = {}

        # Field mappings for different platforms
        field_mappings = {
            # Canvas
            "Student": "name",
            "ID": "student_id",
            "SIS User ID": "sis_id",
            "SIS Login ID": "login_id",
            "Section": "section",
            # Moodle
            "First name": "first_name",
            "Last name": "last_name",
            "Email address": "email",
            "ID number": "student_id",
            # Blackboard
            "Username": "username",
            "Student ID": "student_id",
            "Last Name": "last_name",
            "First Name": "first_name",
            # Generic
            "student_name": "name",
            "grade": "grade",
            "score": "score",
            "points": "points",
        }

        for key, value in record.items():
            # Apply mapping if exists, handling None keys gracefully
            if key is None:
                continue
            normalized_key = field_mappings.get(key, key.lower().replace(" ", "_"))
            normalized[normalized_key] = value

        # Combine first/last name if needed
        if (
            "first_name" in normalized
            and "last_name" in normalized
            and "name" not in normalized
        ):
            normalized["name"] = (
                f"{normalized['last_name']}, {normalized['first_name']}"
            )

        return normalized

    def validate_source(self, source: str | Path) -> bool:
        """Validate source file.

        Args:
            source: Path to validate

        Returns:
            True if source is valid

            Source validation
        """
        path = Path(source)
        return path.exists() and path.suffix.lower() in (".csv", ".json", ".xlsx")


__all__ = ["LMSDataImporter"]
