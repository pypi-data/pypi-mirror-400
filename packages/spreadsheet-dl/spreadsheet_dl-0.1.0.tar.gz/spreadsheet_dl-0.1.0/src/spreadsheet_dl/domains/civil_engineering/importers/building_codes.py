"""Building codes importer for civil engineering.

BuildingCodesImporter for load tables from standards
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


class BuildingCodesImporter(BaseImporter[list[dict[str, Any]]]):
    """Import building code load tables (wind, snow, seismic coefficients).

        BuildingCodesImporter requirements

    Features:
        - Read CSV and JSON files with code tables
        - Parse wind, snow, seismic load coefficients
        - Support ASCE 7, Eurocode, and other standards
        - Validate coefficient ranges

    Example:
        >>> importer = BuildingCodesImporter(code_standard="ASCE_7")  # doctest: +SKIP
        >>> result = importer.import_data("wind_coefficients.csv")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     for coeff in result.data:
        ...         print(f"{coeff['zone']}: {coeff['wind_speed']} mph")
    """

    def __init__(self, code_standard: str = "ASCE_7", **kwargs: Any) -> None:
        """Initialize importer with code standard.

        Args:
            code_standard: Building code standard ("ASCE_7", "Eurocode", "IBC", etc.)
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        self._code_standard = code_standard

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata."""
        return ImporterMetadata(
            name="Building Codes Importer",
            description="Import load tables and coefficients from building codes (ASCE 7, Eurocode, etc.)",
            supported_formats=("csv", "json"),
            category="civil_engineering",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate code table file.

        Args:
            source: Path to code table file

        Returns:
            True if file exists and has supported extension
        """
        path = Path(source) if isinstance(source, str) else source
        return path.exists() and path.suffix.lower() in (".csv", ".json")

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import building code tables from file.

        Args:
            source: Path to code table file

        Returns:
            ImportResult with code tables as list of dictionaries

            Building code table parsing with validation
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
                tables = self._parse_csv(path, errors, warnings)
            else:  # .json
                tables = self._parse_json(path, errors, warnings)

            # Validate coefficient ranges
            for i, table in enumerate(tables):
                # Wind speed validation (typically 85-200 mph for ASCE 7)
                if "wind_speed" in table:
                    speed = table["wind_speed"]
                    if speed < 50 or speed > 250:
                        warnings.append(
                            f"Entry {i + 1}: Unusual wind speed {speed} mph"
                        )

                # Snow load validation (typically 0-300 psf)
                if "snow_load" in table:
                    load = table["snow_load"]
                    if load < 0 or load > 500:
                        warnings.append(f"Entry {i + 1}: Unusual snow load {load} psf")

                # Seismic coefficient validation (typically 0-2.5)
                if "seismic_coefficient" in table or "Cs" in table:
                    coeff = table.get("seismic_coefficient", table.get("Cs", 0))
                    if coeff < 0 or coeff > 3.0:
                        warnings.append(
                            f"Entry {i + 1}: Unusual seismic coefficient {coeff}"
                        )

            return ImportResult(
                success=True,
                data=tables,
                records_imported=len(tables),
                errors=errors,
                warnings=warnings,
                metadata={
                    "code_standard": self._code_standard,
                    "file_format": path.suffix.lower(),
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
        """Parse CSV code table file.

        Args:
            path: Path to CSV file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of code table entry dictionaries
        """
        tables: list[dict[str, Any]] = []

        try:
            with path.open(encoding="utf-8") as f:
                reader = csv.DictReader(f)

                if reader.fieldnames is None:
                    errors.append("CSV file has no headers")
                    return tables

                # Detect column mapping
                column_map = self._detect_columns(list(reader.fieldnames))

                for _row_num, row in enumerate(reader, start=2):
                    entry: dict[str, Any] = {}

                    # Extract mapped fields
                    for csv_col, field_name in column_map.items():
                        if csv_col in row:
                            value = row[csv_col].strip()

                            # Parse numeric fields
                            if field_name in (
                                "wind_speed",
                                "snow_load",
                                "seismic_coefficient",
                                "Cs",
                                "importance_factor",
                                "exposure_factor",
                            ):
                                entry[field_name] = self._parse_float(value, 0.0)
                            else:
                                entry[field_name] = value

                    # Add unmapped fields
                    for csv_col, value in row.items():
                        if csv_col not in column_map:
                            field_name = csv_col.lower().replace(" ", "_")
                            if field_name not in entry:
                                # Try to parse as number
                                try:
                                    entry[field_name] = float(value.strip())
                                except ValueError:
                                    entry[field_name] = value.strip()

                    if entry:
                        tables.append(entry)

        except Exception as e:
            errors.append(f"CSV parse error: {e!s}")

        return tables

    def _parse_json(
        self,
        path: Path,
        errors: list[str],
        warnings: list[str],
    ) -> list[dict[str, Any]]:
        """Parse JSON code table file.

        Args:
            path: Path to JSON file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of code table entry dictionaries
        """
        tables: list[dict[str, Any]] = []

        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)

            # Handle both array and object formats
            if isinstance(data, list):
                tables = data
            elif isinstance(data, dict):
                # Check for common top-level keys
                if "tables" in data:
                    tables = data["tables"]
                elif "coefficients" in data:
                    tables = data["coefficients"]
                elif "data" in data:
                    tables = data["data"]
                else:
                    # Treat each key-value pair as an entry
                    tables = [{"name": k, **v} for k, v in data.items()]

        except json.JSONDecodeError as e:
            errors.append(f"JSON parse error: {e!s}")
        except Exception as e:
            errors.append(f"JSON processing error: {e!s}")

        return tables

    def _detect_columns(self, fieldnames: list[str]) -> dict[str, str]:
        """Auto-detect column mapping from CSV headers.

        Args:
            fieldnames: CSV column names

        Returns:
            Dictionary mapping CSV columns to field names
        """
        mapping: dict[str, str] = {}

        # Common column name variations
        zone_variants = ("zone", "region", "location", "area")
        wind_variants = ("wind", "v", "basic_wind")
        snow_variants = ("snow", "ground_snow", "pg")
        seismic_variants = (
            "seismic",
            "Cs",
            "Sd1",
            "Sds",
            "earthquake",
            "seismic_coefficient",
        )
        importance_variants = ("importance", "I", "Ie")
        exposure_variants = ("exposure", "category", "terrain")

        for field in fieldnames:
            field_lower = field.lower().replace(" ", "_").replace("-", "_")

            if any(variant in field_lower for variant in zone_variants):
                mapping[field] = "zone"
            elif any(variant in field_lower for variant in wind_variants):
                mapping[field] = "wind_speed"
            elif any(variant in field_lower for variant in snow_variants):
                mapping[field] = "snow_load"
            elif any(variant in field_lower for variant in seismic_variants):
                if "Cs" in field:
                    mapping[field] = "Cs"
                else:
                    mapping[field] = "seismic_coefficient"
            elif any(variant in field_lower for variant in importance_variants):
                mapping[field] = "importance_factor"
            elif any(variant in field_lower for variant in exposure_variants):
                mapping[field] = "exposure_category"

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


__all__ = ["BuildingCodesImporter"]
