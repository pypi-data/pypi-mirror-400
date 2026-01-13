"""Structural analysis results importer for civil engineering.

StructuralResultsImporter for analysis software output
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


class StructuralResultsImporter(BaseImporter[list[dict[str, Any]]]):
    """Import structural analysis results from various software packages.

        StructuralResultsImporter requirements

    Features:
        - Read SAP2000, STAAD, ETABS output files (text/CSV format)
        - Parse member forces, reactions, deflections
        - Support for different output formats
        - Unit conversion support

    Example:
        >>> importer = StructuralResultsImporter(software="SAP2000")  # doctest: +SKIP
        >>> result = importer.import_data("analysis_results.txt")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     for member in result.data:
        ...         print(f"{member['id']}: Axial={member['axial']} kN")
    """

    def __init__(self, software: str = "generic", **kwargs: Any) -> None:
        """Initialize importer with software type.

        Args:
            software: Analysis software type ("SAP2000", "STAAD", "ETABS", "generic")
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        self._software = software.lower()

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata."""
        return ImporterMetadata(
            name="Structural Results Importer",
            description="Import structural analysis results from SAP2000, STAAD, ETABS, and other software",
            supported_formats=("txt", "csv", "out"),
            category="civil_engineering",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate results file.

        Args:
            source: Path to results file

        Returns:
            True if file exists and has supported extension
        """
        path = Path(source) if isinstance(source, str) else source
        return path.exists() and path.suffix.lower() in (".txt", ".csv", ".out")

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import structural analysis results from file.

        Args:
            source: Path to results file

        Returns:
            ImportResult with structural results as list of dictionaries

            Structural results parsing with validation
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
                results = self._parse_csv(path, errors, warnings)
            else:  # .txt or .out
                results = self._parse_text(path, errors, warnings)

            # Validate force magnitudes
            for i, result in enumerate(results):
                if "axial" in result and abs(result["axial"]) > 1e6:
                    warnings.append(
                        f"Member {i + 1}: Very large axial force {result['axial']} kN"
                    )

            return ImportResult(
                success=True,
                data=results,
                records_imported=len(results),
                errors=errors,
                warnings=warnings,
                metadata={
                    "software": self._software,
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
        """Parse CSV results file.

        Args:
            path: Path to CSV file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of structural result dictionaries
        """
        results: list[dict[str, Any]] = []

        try:
            with path.open(encoding="utf-8") as f:
                reader = csv.DictReader(f)

                if reader.fieldnames is None:
                    errors.append("CSV file has no headers")
                    return results

                # Detect column mapping
                column_map = self._detect_columns(list(reader.fieldnames))

                for _row_num, row in enumerate(reader, start=2):
                    result: dict[str, Any] = {}

                    # Extract mapped fields
                    for csv_col, field_name in column_map.items():
                        if csv_col in row:
                            value = row[csv_col].strip()

                            # Parse numeric fields
                            if field_name in (
                                "axial",
                                "shear",
                                "moment",
                                "deflection",
                                "stress",
                            ):
                                result[field_name] = self._parse_float(value, 0.0)
                            else:
                                result[field_name] = value

                    # Add unmapped fields
                    for csv_col, value in row.items():
                        if csv_col not in column_map:
                            field_name = csv_col.lower().replace(" ", "_")
                            if field_name not in result:
                                result[field_name] = value.strip()

                    if result:
                        results.append(result)

        except Exception as e:
            errors.append(f"CSV parse error: {e!s}")

        return results

    def _parse_text(
        self,
        path: Path,
        errors: list[str],
        warnings: list[str],
    ) -> list[dict[str, Any]]:
        """Parse text-based results file.

        Supports various text output formats from structural analysis software.

        Args:
            path: Path to text file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of structural result dictionaries
        """
        results: list[dict[str, Any]] = []

        try:
            with path.open(encoding="utf-8") as f:
                content = f.read()

            # Detect format based on software
            if self._software == "sap2000":
                results = self._parse_sap2000(content, errors, warnings)
            elif self._software == "staad":
                results = self._parse_staad(content, errors, warnings)
            elif self._software == "etabs":
                results = self._parse_etabs(content, errors, warnings)
            else:
                # Generic parsing - look for tabular data
                results = self._parse_generic_text(content, errors, warnings)

        except Exception as e:
            errors.append(f"Text parse error: {e!s}")

        return results

    def _parse_sap2000(
        self,
        content: str,
        errors: list[str],
        warnings: list[str],
    ) -> list[dict[str, Any]]:
        """Parse SAP2000 text output format."""
        results: list[dict[str, Any]] = []

        # Look for member force tables
        # SAP2000 typically has sections like "MEMBER FORCES"
        force_section = re.search(
            r"MEMBER\s+FORCES.*?(?=\n\n|\Z)", content, re.DOTALL | re.IGNORECASE
        )

        if force_section:
            lines = force_section.group(0).split("\n")
            # Skip header lines and parse data rows
            for line in lines[2:]:  # Assuming 2 header lines
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            result = {
                                "id": parts[0],
                                "axial": float(parts[1]),
                                "shear": float(parts[2]) if len(parts) > 2 else 0.0,
                                "moment": float(parts[3]) if len(parts) > 3 else 0.0,
                            }
                            results.append(result)
                        except (ValueError, IndexError):
                            continue

        return results

    def _parse_staad(
        self,
        content: str,
        errors: list[str],
        warnings: list[str],
    ) -> list[dict[str, Any]]:
        """Parse STAAD.Pro text output format."""
        results: list[dict[str, Any]] = []

        # STAAD typically has "MEMBER END FORCES" sections
        force_section = re.search(
            r"MEMBER\s+END\s+FORCES.*?(?=\n\n|\Z)", content, re.DOTALL | re.IGNORECASE
        )

        if force_section:
            lines = force_section.group(0).split("\n")
            for line in lines[2:]:
                if line.strip() and not line.strip().startswith("-"):
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            result = {
                                "id": parts[0],
                                "axial": float(parts[1]),
                                "shear": float(parts[2]) if len(parts) > 2 else 0.0,
                                "moment": float(parts[3]) if len(parts) > 3 else 0.0,
                            }
                            results.append(result)
                        except (ValueError, IndexError):
                            continue

        return results

    def _parse_etabs(
        self,
        content: str,
        errors: list[str],
        warnings: list[str],
    ) -> list[dict[str, Any]]:
        """Parse ETABS text output format (similar to SAP2000)."""
        # ETABS output is similar to SAP2000
        return self._parse_sap2000(content, errors, warnings)

    def _parse_generic_text(
        self,
        content: str,
        errors: list[str],
        warnings: list[str],
    ) -> list[dict[str, Any]]:
        """Parse generic tabular text format.

        Attempts to extract numerical data from any tabular text format.
        """
        results: list[dict[str, Any]] = []
        lines = content.split("\n")

        for line in lines:
            # Look for lines with multiple numbers
            numbers = re.findall(r"-?\d+\.?\d*", line)
            if len(numbers) >= 3:
                try:
                    # Assume first column is ID, rest are forces
                    result = {
                        "id": numbers[0] if "." not in numbers[0] else line.split()[0],
                        "axial": float(numbers[0] if "." in numbers[0] else numbers[1]),
                        "shear": (
                            float(numbers[1] if "." in numbers[0] else numbers[2])
                            if len(numbers) > 1
                            else 0.0
                        ),
                        "moment": (
                            float(numbers[2] if "." in numbers[0] else numbers[3])
                            if len(numbers) > 2
                            else 0.0
                        ),
                    }
                    results.append(result)
                except (ValueError, IndexError):
                    continue

        return results

    def _detect_columns(self, fieldnames: list[str]) -> dict[str, str]:
        """Auto-detect column mapping from CSV headers.

        Args:
            fieldnames: CSV column names

        Returns:
            Dictionary mapping CSV columns to field names
        """
        mapping: dict[str, str] = {}

        # Common column name variations
        id_variants = ("member", "element", "id", "frame")
        axial_variants = ("axial", "p", "fx", "force_x")
        shear_variants = ("shear", "v", "fy", "fz", "force_y", "force_z")
        moment_variants = ("moment", "m", "mx", "my", "mz")
        deflection_variants = ("deflection", "displacement", "delta", "defl")
        stress_variants = ("stress", "sigma", "f")

        for field in fieldnames:
            field_lower = field.lower().replace(" ", "_").replace("-", "_")

            if any(variant in field_lower for variant in id_variants):
                mapping[field] = "id"
            elif any(variant in field_lower for variant in axial_variants):
                mapping[field] = "axial"
            elif any(variant in field_lower for variant in shear_variants):
                mapping[field] = "shear"
            elif any(variant in field_lower for variant in moment_variants):
                mapping[field] = "moment"
            elif any(variant in field_lower for variant in deflection_variants):
                mapping[field] = "deflection"
            elif any(variant in field_lower for variant in stress_variants):
                mapping[field] = "stress"

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


__all__ = ["StructuralResultsImporter"]
