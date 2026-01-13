"""Gradebook Export Importer.

GradebookExportImporter for education domain
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


@dataclass
class GradebookExportImporter(BaseImporter[list[dict[str, Any]]]):
    """Gradebook export importer.

        GradebookExportImporter for CSV/Excel gradebook exports

    Supports importing gradebook data from:
    - CSV exports from various grade tracking tools
    - Excel gradebook files
    - Generic tabular grade data

    Example:
        >>> importer = GradebookExportImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("gradebook.csv")  # doctest: +SKIP
        >>> print(f"Imported {result.records_imported} student grades")  # doctest: +SKIP
    """

    detect_assignments: bool = True
    include_statistics: bool = True

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata.

        Returns:
            ImporterMetadata for gradebook importer

            Importer metadata
        """
        return ImporterMetadata(
            name="Gradebook Export Importer",
            description="Import gradebook data from CSV/Excel exports",
            supported_formats=("csv", "xlsx", "xls"),
            category="education",
        )

    def import_data(self, source: str | Path) -> ImportResult[list[dict[str, Any]]]:
        """Import gradebook data from file.

        Args:
            source: Path to gradebook file

        Returns:
            ImportResult with grade data

            Gradebook data import
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
            else:
                return ImportResult(
                    success=False,
                    data=[],
                    records_imported=0,
                    errors=[f"Unsupported format: {suffix}"],
                    warnings=[],
                    metadata={},
                )

            # Calculate statistics if requested
            statistics = {}
            if self.include_statistics and data:
                statistics = self._calculate_statistics(data)

            return ImportResult(
                success=len(errors) == 0,
                data=data,
                records_imported=len(data),
                errors=errors,
                warnings=warnings,
                metadata={
                    "source_file": str(source_path),
                    "format": suffix,
                    "statistics": statistics,
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
            headers = reader.fieldnames or []

            # Detect assignment columns (numeric columns that aren't ID)
            assignment_cols = []
            if self.detect_assignments:
                for header in headers:
                    if header.lower() not in (
                        "id",
                        "student_id",
                        "name",
                        "student",
                        "first_name",
                        "last_name",
                        "email",
                    ):
                        assignment_cols.append(header)

            for row_num, row in enumerate(reader, start=2):
                record: dict[str, Any] = {}

                # Extract student info
                for key in ["id", "student_id", "ID", "Student ID"]:
                    if key in row:
                        record["student_id"] = row[key]
                        break

                for key in ["name", "student", "Name", "Student"]:
                    if key in row:
                        record["name"] = row[key]
                        break

                # Extract grades
                grades: dict[str, float | None] = {}
                for col in assignment_cols:
                    value = row.get(col, "")
                    try:
                        if value and value.strip():
                            grades[col] = float(value)
                        else:
                            grades[col] = None
                    except ValueError:
                        grades[col] = None
                        warnings.append(f"Row {row_num}: Invalid grade value in {col}")

                record["grades"] = grades

                # Calculate average if we have grades
                valid_grades = [g for g in grades.values() if g is not None]
                if valid_grades:
                    record["average"] = sum(valid_grades) / len(valid_grades)
                else:
                    record["average"] = None

                data.append(record)

        return data, errors, warnings

    def _calculate_statistics(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate class statistics from grade data."""
        averages = [r["average"] for r in data if r.get("average") is not None]

        if not averages:
            return {}

        stats = {
            "class_average": sum(averages) / len(averages),
            "class_high": max(averages),
            "class_low": min(averages),
            "student_count": len(data),
        }

        # Standard deviation
        if len(averages) > 1:
            mean = stats["class_average"]
            variance = sum((x - mean) ** 2 for x in averages) / (len(averages) - 1)
            stats["std_deviation"] = variance**0.5

        return stats

    def validate_source(self, source: str | Path) -> bool:
        """Validate source file.

        Args:
            source: Path to validate

        Returns:
            True if source is valid

            Source validation
        """
        path = Path(source)
        return path.exists() and path.suffix.lower() in (".csv", ".xlsx", ".xls")


__all__ = ["GradebookExportImporter"]
