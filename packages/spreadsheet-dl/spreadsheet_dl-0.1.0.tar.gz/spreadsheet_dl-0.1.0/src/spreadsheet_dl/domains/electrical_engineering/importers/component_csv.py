"""Generic component CSV importer for electrical engineering.

GenericComponentCSVImporter with flexible column mapping
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING, Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult

if TYPE_CHECKING:
    from collections.abc import Sequence


class GenericComponentCSVImporter(BaseImporter[list[dict[str, Any]]]):
    """Import generic component CSV files with flexible column mapping.

        GenericComponentCSVImporter requirements

    Features:
        - Read generic CSV component lists
        - Flexible column mapping (user specifies headers)
        - Type inference for quantities and costs
        - Validation: Required fields present

    Example:
        >>> importer = GenericComponentCSVImporter(  # doctest: +SKIP
        ...     column_mapping={
        ...         "Reference": "ref",
        ...         "Part Number": "part_number",
        ...         "Qty": "quantity",
        ...     }
        ... )
        >>> result = importer.import_data("components.csv")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     for component in result.data:
        ...         print(component["ref"], component["quantity"])
    """

    def __init__(
        self,
        column_mapping: dict[str, str] | None = None,
        required_fields: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize importer with column mapping.

        Args:
            column_mapping: Map CSV column names to output field names
                          e.g., {"Reference": "ref", "Part Number": "part_number"}
            required_fields: List of required output field names
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        self._column_mapping = column_mapping or {}
        self._required_fields = required_fields or ["ref"]

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata."""
        return ImporterMetadata(
            name="Generic Component CSV Importer",
            description="Import component data from CSV files with flexible column mapping",
            supported_formats=("csv",),
            category="electrical_engineering",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate CSV file.

        Args:
            source: Path to CSV file

        Returns:
            True if file exists and has .csv extension
        """
        path = Path(source) if isinstance(source, str) else source
        return path.exists() and path.suffix.lower() == ".csv"

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import component data from CSV.

        Args:
            source: Path to CSV file

        Returns:
            ImportResult with component data as list of dictionaries

            Generic CSV parsing with validation
        """
        if not self.validate_source(source):
            return ImportResult(
                success=False,
                data=[],
                errors=["Invalid source file or not a CSV file"],
            )

        path = Path(source) if isinstance(source, str) else source
        errors: list[str] = []
        warnings: list[str] = []

        try:
            components = self._parse_csv(path, errors, warnings)

            # Validate required fields
            for i, comp in enumerate(components):
                missing = [
                    field for field in self._required_fields if field not in comp
                ]
                if missing:
                    warnings.append(
                        f"Row {i + 1} missing required fields: {', '.join(missing)}"
                    )

            return ImportResult(
                success=True,
                data=components,
                records_imported=len(components),
                errors=errors,
                warnings=warnings,
                metadata={
                    "column_mapping": self._column_mapping,
                    "required_fields": self._required_fields,
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
        """Parse CSV file with column mapping.

        Args:
            path: Path to CSV file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of component dictionaries
        """
        components: list[dict[str, Any]] = []

        try:
            with path.open(encoding="utf-8") as f:
                reader = csv.DictReader(f)

                if reader.fieldnames is None:
                    errors.append("CSV file has no headers")
                    return components

                # Auto-detect mapping if not provided
                if not self._column_mapping:
                    self._column_mapping = self._auto_detect_mapping(reader.fieldnames)
                    warnings.append(
                        f"Auto-detected column mapping: {self._column_mapping}"
                    )

                for _row_num, row in enumerate(reader, start=2):
                    component: dict[str, Any] = {}

                    # Apply column mapping
                    for csv_col, output_field in self._column_mapping.items():
                        if csv_col in row:
                            value = row[csv_col].strip()

                            # Type inference
                            if output_field in ("quantity", "qty"):
                                component[output_field] = self._parse_int(value, 1)
                            elif output_field in ("unit_cost", "cost", "price"):
                                component[output_field] = self._parse_float(value, 0.0)
                            else:
                                component[output_field] = value

                    # Add unmapped columns as-is (preserving original data)
                    for csv_col, value in row.items():
                        if csv_col not in self._column_mapping:
                            # Convert column name to snake_case field name
                            field_name = (
                                csv_col.lower().replace(" ", "_").replace("-", "_")
                            )
                            if field_name not in component:
                                component[field_name] = value.strip()

                    if component:
                        components.append(component)

        except Exception as e:
            errors.append(f"CSV parse error: {e!s}")

        return components

    def _auto_detect_mapping(self, fieldnames: Sequence[str]) -> dict[str, str]:
        """Auto-detect column mapping from CSV headers.

        Args:
            fieldnames: CSV column names

        Returns:
            Dictionary mapping CSV columns to output fields
        """
        mapping: dict[str, str] = {}

        # Common column name variations
        ref_variants = ("ref", "reference", "designator", "part")
        value_variants = ("value", "val")
        part_num_variants = ("part_number", "partnumber", "pn", "mpn")
        desc_variants = ("description", "desc")
        mfr_variants = ("manufacturer", "mfr", "vendor")
        qty_variants = ("quantity", "qty", "count")
        cost_variants = ("unit_cost", "cost", "price", "unit_price")
        footprint_variants = ("footprint", "package", "fp")

        for field in fieldnames:
            field_lower = field.lower().replace(" ", "_").replace("-", "_")

            if any(variant in field_lower for variant in ref_variants):
                mapping[field] = "ref"
            elif any(variant in field_lower for variant in value_variants):
                mapping[field] = "value"
            elif any(variant in field_lower for variant in part_num_variants):
                mapping[field] = "part_number"
            elif any(variant in field_lower for variant in desc_variants):
                mapping[field] = "description"
            elif any(variant in field_lower for variant in mfr_variants):
                mapping[field] = "manufacturer"
            elif any(variant in field_lower for variant in qty_variants):
                mapping[field] = "quantity"
            elif any(variant in field_lower for variant in cost_variants):
                mapping[field] = "unit_cost"
            elif any(variant in field_lower for variant in footprint_variants):
                mapping[field] = "footprint"

        return mapping

    def _parse_int(self, value: str, default: int) -> int:
        """Parse integer value with fallback.

        Args:
            value: String value to parse
            default: Default value if parsing fails

        Returns:
            Parsed integer or default
        """
        try:
            # Remove common non-numeric characters
            cleaned = value.replace(",", "").replace(" ", "")
            return int(float(cleaned))  # Handle "1.0" -> 1
        except (ValueError, AttributeError):
            return default

    def _parse_float(self, value: str, default: float) -> float:
        """Parse float value with fallback.

        Args:
            value: String value to parse
            default: Default value if parsing fails

        Returns:
            Parsed float or default
        """
        try:
            # Remove currency symbols and commas
            cleaned = value.replace("$", "").replace(",", "").replace(" ", "")
            return float(cleaned)
        except (ValueError, AttributeError):
            return default


__all__ = ["GenericComponentCSVImporter"]
