"""Survey data importer for civil engineering.

SurveyDataImporter for CSV/XML surveying data
"""

from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


class SurveyDataImporter(BaseImporter[list[dict[str, Any]]]):
    """Import survey data from CSV or XML files.

        SurveyDataImporter requirements

    Features:
        - Read CSV and XML survey data formats
        - Parse station, northing, easting, elevation, description
        - Validate coordinate ranges
        - Support multiple survey data formats

    Example:
        >>> importer = SurveyDataImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("survey_points.csv")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     for point in result.data:
        ...         print(f"{point['station']}: {point['elevation']}m")
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize importer.

        Args:
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata."""
        return ImporterMetadata(
            name="Survey Data Importer",
            description="Import survey points from CSV or XML files",
            supported_formats=("csv", "xml"),
            category="civil_engineering",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate survey data file.

        Args:
            source: Path to survey data file

        Returns:
            True if file exists and has supported extension
        """
        path = Path(source) if isinstance(source, str) else source
        return path.exists() and path.suffix.lower() in (".csv", ".xml")

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import survey data from file.

        Args:
            source: Path to survey data file

        Returns:
            ImportResult with survey points as list of dictionaries

            Survey data parsing with validation
        """
        if not self.validate_source(source):
            return ImportResult(
                success=False,
                data=[],
                errors=["Invalid source file or unsupported format"],
            )

        path = Path(source) if isinstance(source, str) else source
        errors: list[str] = []
        warnings: list[str] = []

        try:
            if path.suffix.lower() == ".csv":
                points = self._parse_csv(path, errors, warnings)
            else:  # .xml
                points = self._parse_xml(path, errors, warnings)

            # Validate coordinate ranges
            for i, point in enumerate(points):
                if "elevation" in point:
                    elev = point["elevation"]
                    if elev < -500 or elev > 10000:
                        warnings.append(f"Point {i + 1}: Unusual elevation {elev}m")

            return ImportResult(
                success=True,
                data=points,
                records_imported=len(points),
                errors=errors,
                warnings=warnings,
                metadata={
                    "file_format": path.suffix.lower(),
                    "coordinate_fields": ["northing", "easting", "elevation"],
                },
            )

        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"Import failed: {e!s}"],
            )

    def _parse_csv(
        self,
        path: Path,
        errors: list[str],
        warnings: list[str],
    ) -> list[dict[str, Any]]:
        """Parse CSV survey data file.

        Args:
            path: Path to CSV file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of survey point dictionaries
        """
        points: list[dict[str, Any]] = []

        try:
            with path.open(encoding="utf-8") as f:
                reader = csv.DictReader(f)

                if reader.fieldnames is None:
                    errors.append("CSV file has no headers")
                    return points

                # Detect column mapping
                column_map = self._detect_columns(list(reader.fieldnames))

                for _row_num, row in enumerate(reader, start=2):
                    point: dict[str, Any] = {}

                    # Extract mapped fields
                    for csv_col, field_name in column_map.items():
                        if csv_col in row:
                            value = row[csv_col].strip()

                            # Parse numeric fields
                            if field_name in ("northing", "easting", "elevation"):
                                point[field_name] = self._parse_float(value, 0.0)
                            else:
                                point[field_name] = value

                    # Add unmapped fields
                    for csv_col, value in row.items():
                        if csv_col not in column_map:
                            field_name = csv_col.lower().replace(" ", "_")
                            if field_name not in point:
                                point[field_name] = value.strip()

                    if point:
                        points.append(point)

        except Exception as e:
            errors.append(f"CSV parse error: {e!s}")

        return points

    def _parse_xml(
        self,
        path: Path,
        errors: list[str],
        warnings: list[str],
    ) -> list[dict[str, Any]]:
        """Parse XML survey data file.

        Supports LandXML and generic survey XML formats.

        Args:
            path: Path to XML file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of survey point dictionaries
        """
        points: list[dict[str, Any]] = []

        try:
            tree = ET.parse(path)
            root = tree.getroot()

            # Try LandXML format first
            namespace = {"landxml": "http://www.landxml.org/schema/LandXML-1.2"}
            survey_points = root.findall(".//landxml:CgPoint", namespace)

            if survey_points:
                # LandXML format
                for sp in survey_points:
                    point: dict[str, Any] = {}

                    # Get point attributes
                    point["station"] = sp.get("name", "")
                    point["description"] = sp.get("desc", "")

                    # Get coordinates
                    coords = sp.text.strip().split() if sp.text else []
                    if len(coords) >= 2:
                        point["northing"] = float(coords[0])
                        point["easting"] = float(coords[1])
                    if len(coords) >= 3:
                        point["elevation"] = float(coords[2])

                    points.append(point)
            else:
                # Try generic XML format
                for point_elem in root.findall(".//point"):
                    pt: dict[str, Any] = {}

                    # Extract common fields
                    for child in point_elem:
                        tag = child.tag.lower()
                        text = child.text.strip() if child.text else ""

                        if tag in ("northing", "easting", "elevation"):
                            pt[tag] = self._parse_float(text, 0.0)
                        else:
                            pt[tag] = text

                    if pt:
                        points.append(pt)

        except ET.ParseError as e:
            errors.append(f"XML parse error: {e!s}")
        except Exception as e:
            errors.append(f"XML processing error: {e!s}")

        return points

    def _detect_columns(self, fieldnames: list[str]) -> dict[str, str]:
        """Auto-detect column mapping from CSV headers.

        Args:
            fieldnames: CSV column names

        Returns:
            Dictionary mapping CSV columns to field names
        """
        mapping: dict[str, str] = {}

        # Common column name variations
        station_variants = ("station", "sta", "point", "pt", "id")
        northing_variants = ("northing", "north", "y", "lat", "latitude")
        easting_variants = ("easting", "east", "x", "lon", "longitude")
        elevation_variants = ("elevation", "elev", "z", "height", "alt", "altitude")
        description_variants = ("description", "desc", "code", "feature")

        for field in fieldnames:
            field_lower = field.lower().replace(" ", "_").replace("-", "_")

            if any(variant in field_lower for variant in station_variants):
                mapping[field] = "station"
            elif any(variant in field_lower for variant in northing_variants):
                mapping[field] = "northing"
            elif any(variant in field_lower for variant in easting_variants):
                mapping[field] = "easting"
            elif any(variant in field_lower for variant in elevation_variants):
                mapping[field] = "elevation"
            elif any(variant in field_lower for variant in description_variants):
                mapping[field] = "description"

        return mapping

    def _parse_float(self, value: str, default: float) -> float:
        """Parse float value with fallback.

        Args:
            value: String value to parse
            default: Default value if parsing fails

        Returns:
            Parsed float or default
        """
        try:
            # Remove common non-numeric characters
            cleaned = value.replace(",", "").replace(" ", "")
            return float(cleaned)
        except (ValueError, AttributeError):
            return default


__all__ = ["SurveyDataImporter"]
