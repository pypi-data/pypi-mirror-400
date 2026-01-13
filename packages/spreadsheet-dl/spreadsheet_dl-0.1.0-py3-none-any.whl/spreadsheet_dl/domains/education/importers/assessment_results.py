"""Assessment Results Importer.

AssessmentResultsImporter for education domain
"""

from __future__ import annotations

import contextlib
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


@dataclass
class AssessmentResultsImporter(BaseImporter[list[dict[str, Any]]]):
    """Assessment and quiz results importer.

        AssessmentResultsImporter for quiz/test results

    Supports importing assessment data from:
    - Quiz/test result exports
    - Online assessment platforms
    - Item analysis reports

    Example:
        >>> importer = AssessmentResultsImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("quiz_results.csv")  # doctest: +SKIP
        >>> print(f"Imported {result.records_imported} assessment results")  # doctest: +SKIP
    """

    include_item_analysis: bool = True
    score_type: str = "percentage"  # percentage, points, raw

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata.

        Returns:
            ImporterMetadata for assessment results importer

            Importer metadata
        """
        return ImporterMetadata(
            name="Assessment Results Importer",
            description="Import quiz and test results with item analysis",
            supported_formats=("csv", "json", "xlsx"),
            category="education",
        )

    def import_data(self, source: str | Path) -> ImportResult[list[dict[str, Any]]]:
        """Import assessment results from file.

        Args:
            source: Path to assessment results file

        Returns:
            ImportResult with assessment data

            Assessment results import
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

            # Calculate item analysis if requested
            item_analysis = {}
            if self.include_item_analysis and data:
                item_analysis = self._calculate_item_analysis(data)

            return ImportResult(
                success=len(errors) == 0,
                data=data,
                records_imported=len(data),
                errors=errors,
                warnings=warnings,
                metadata={
                    "source_file": str(source_path),
                    "format": suffix,
                    "item_analysis": item_analysis,
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

            # Detect question columns (Q1, Q2, etc. or numbered columns)
            question_cols = []
            for header in headers:
                if (
                    header.lower().startswith("q")
                    or header.lower().startswith("question")
                    or header.lower().startswith("item")
                ):
                    question_cols.append(header)

            for row_num, row in enumerate(reader, start=2):
                record = self._parse_row(row, question_cols)
                data.append(record)

                # Validate score
                score = record.get("score")
                if score is not None and (score < 0 or score > 100):
                    warnings.append(
                        f"Row {row_num}: Score {score} out of expected range (0-100)"
                    )

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
            for item in content:
                data.append(self._normalize_record(item))
        elif isinstance(content, dict):
            if "results" in content:
                for item in content["results"]:
                    data.append(self._normalize_record(item))
            else:
                data.append(self._normalize_record(content))

        return data, errors, warnings

    def _parse_row(
        self, row: dict[str, Any], question_cols: list[str]
    ) -> dict[str, Any]:
        """Parse a CSV row into a record."""
        record: dict[str, Any] = {}

        # Student identification
        for key in ["student_id", "id", "ID", "Student ID"]:
            if key in row:
                record["student_id"] = row[key]
                break

        for key in ["name", "student", "Name", "Student"]:
            if key in row:
                record["name"] = row[key]
                break

        # Score
        for key in ["score", "Score", "grade", "Grade", "points", "Points"]:
            if key in row:
                try:
                    record["score"] = float(row[key])
                except (ValueError, TypeError):
                    record["score"] = None
                break

        # Maximum points
        for key in ["max", "max_points", "Max Points", "total"]:
            if key in row:
                with contextlib.suppress(ValueError, TypeError):
                    record["max_points"] = float(row[key])
                break

        # Question/item responses
        responses: dict[str, Any] = {}
        for col in question_cols:
            responses[col] = row.get(col, "")
        record["responses"] = responses

        # Calculate percentage if we have score and max
        if record.get("score") is not None and record.get("max_points"):
            record["percentage"] = (record["score"] / record["max_points"]) * 100

        return record

    def _normalize_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Normalize a JSON record."""
        normalized: dict[str, Any] = {}

        # Copy known fields
        for key in ["student_id", "name", "score", "percentage", "responses"]:
            if key in record:
                normalized[key] = record[key]

        return normalized

    def _calculate_item_analysis(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate item analysis statistics."""
        if not data:
            return {}

        # Collect all questions
        all_questions: set[str] = set()
        for record in data:
            responses = record.get("responses", {})
            all_questions.update(responses.keys())

        # Calculate difficulty and discrimination for each item
        item_stats: dict[str, Any] = {}
        scores = [r.get("score", 0) or 0 for r in data]

        if not scores or not all_questions:
            return {}

        median_score = sorted(scores)[len(scores) // 2]

        for question in all_questions:
            correct_count = 0
            high_group_correct = 0
            low_group_correct = 0
            high_count = 0
            low_count = 0

            for record in data:
                response = record.get("responses", {}).get(question, "")
                score = record.get("score", 0) or 0

                # Check if correct (assuming 1, correct, yes, true = correct)
                is_correct = str(response).lower() in ("1", "correct", "yes", "true")

                if is_correct:
                    correct_count += 1

                if score >= median_score:
                    high_count += 1
                    if is_correct:
                        high_group_correct += 1
                else:
                    low_count += 1
                    if is_correct:
                        low_group_correct += 1

            # Difficulty index (proportion correct)
            difficulty = correct_count / len(data) if data else 0

            # Discrimination index (high group - low group proportion)
            high_prop = high_group_correct / high_count if high_count > 0 else 0
            low_prop = low_group_correct / low_count if low_count > 0 else 0
            discrimination = high_prop - low_prop

            item_stats[question] = {
                "difficulty": round(difficulty, 3),
                "discrimination": round(discrimination, 3),
                "correct_count": correct_count,
                "total_responses": len(data),
            }

        return {
            "items": item_stats,
            "total_students": len(data),
            "average_score": sum(scores) / len(scores) if scores else 0,
        }

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


__all__ = ["AssessmentResultsImporter"]
