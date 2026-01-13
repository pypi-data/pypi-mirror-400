"""Eagle BOM importer for electrical engineering.

EagleBOMImporter for Eagle CAD exports
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


class EagleBOMImporter(BaseImporter[list[dict[str, Any]]]):
    """Import Eagle BOM exports (text or CSV format).

        EagleBOMImporter requirements

    Features:
        - Parse Eagle BOM text/CSV exports
        - Extract: Part, Value, Device, Package, Description
        - Map to BOMTemplate format
        - Handle multi-board projects

    Example:
        >>> importer = EagleBOMImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("eagle_bom.txt")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     for component in result.data:
        ...         print(component["part"], component["value"])
    """

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata."""
        return ImporterMetadata(
            name="Eagle BOM Importer",
            description="Import Bill of Materials from Eagle CAD text or CSV exports",
            supported_formats=("txt", "csv"),
            category="electrical_engineering",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate Eagle BOM file.

        Args:
            source: Path to Eagle BOM file

        Returns:
            True if file exists and has valid extension
        """
        path = Path(source) if isinstance(source, str) else source
        return path.exists() and path.suffix.lower() in (".txt", ".csv")

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import Eagle BOM data.

        Args:
            source: Path to Eagle BOM file

        Returns:
            ImportResult with component data as list of dictionaries

            Eagle BOM parsing and mapping
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
                data = self._parse_csv(path, errors, warnings)
            else:
                data = self._parse_text(path, errors, warnings)

            return ImportResult(
                success=True,
                data=data,
                records_imported=len(data),
                errors=errors,
                warnings=warnings,
                metadata={"source_format": path.suffix.lower()},
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
        """Parse Eagle CSV BOM format.

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

                for row in reader:
                    # Eagle CSV typically has: Part, Value, Device, Package, Description
                    part = row.get("Part", row.get("Parts", ""))
                    value = row.get("Value", "")
                    device = row.get("Device", "")
                    package = row.get("Package", row.get("Footprint", ""))
                    description = row.get("Description", "")

                    if not part:
                        warnings.append(f"Skipping row with missing part: {row}")
                        continue

                    components.append(
                        {
                            "ref": part,
                            "value": value,
                            "part_number": device or value,
                            "description": description or device,
                            "manufacturer": "",
                            "quantity": int(row.get("Qty", row.get("Quantity", 1))),
                            "footprint": package,
                            "datasheet": "",
                        }
                    )

        except Exception as e:
            errors.append(f"CSV parse error: {e!s}")

        return components

    def _parse_text(
        self,
        path: Path,
        errors: list[str],
        warnings: list[str],
    ) -> list[dict[str, Any]]:
        """Parse Eagle text BOM format.

        Args:
            path: Path to text file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of component dictionaries
        """
        components: list[dict[str, Any]] = []

        try:
            with path.open(encoding="utf-8") as f:
                # Skip header lines until we find the parts list
                # Eagle text format typically has headers, then data lines
                lines = f.readlines()

                in_parts_section = False
                for line in lines:
                    line = line.strip()

                    # Skip empty lines
                    if not line:
                        continue

                    # Look for parts section start
                    if "Part" in line and "Value" in line:
                        in_parts_section = True
                        continue

                    # Skip non-part lines
                    if not in_parts_section or line.startswith("--"):
                        continue

                    # Parse part line (typically space or tab separated)
                    # Format: Part Value Device Package Description
                    parts = line.split(None, 4)  # Split on whitespace, max 5 parts

                    if len(parts) < 2:
                        warnings.append(f"Skipping malformed line: {line}")
                        continue

                    ref = parts[0]
                    value = parts[1] if len(parts) > 1 else ""
                    device = parts[2] if len(parts) > 2 else ""
                    package = parts[3] if len(parts) > 3 else ""
                    description = parts[4] if len(parts) > 4 else ""

                    components.append(
                        {
                            "ref": ref,
                            "value": value,
                            "part_number": device or value,
                            "description": description or device,
                            "manufacturer": "",
                            "quantity": 1,
                            "footprint": package,
                            "datasheet": "",
                        }
                    )

        except Exception as e:
            errors.append(f"Text parse error: {e!s}")

        return components


__all__ = ["EagleBOMImporter"]
