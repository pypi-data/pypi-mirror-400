"""KiCad BOM importer for electrical engineering.

KiCadBOMImporter for KiCad XML/CSV exports
"""

from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


@dataclass
class KiCadComponent:
    """KiCad component data.

    Attributes:
        ref: Reference designator (e.g., R1, U2)
        value: Component value (e.g., 10k, STM32F4)
        footprint: PCB footprint
        datasheet: Datasheet URL or reference
        quantity: Number of components
        description: Component description
        manufacturer: Manufacturer name
        part_number: Manufacturer part number
    """

    ref: str
    value: str
    footprint: str = ""
    datasheet: str = ""
    quantity: int = 1
    description: str = ""
    manufacturer: str = ""
    part_number: str = ""


class KiCadBOMImporter(BaseImporter[list[dict[str, Any]]]):
    """Import KiCad BOM exports (XML or CSV format).

        KiCadBOMImporter requirements

    Features:
        - Parse KiCad BOM XML/CSV exports
        - Extract: Ref, Value, Footprint, Datasheet, Quantity
        - Map to BOMTemplate format
        - Handle grouped components (R1-R10)

    Example:
        >>> importer = KiCadBOMImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("kicad_bom.xml")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     for component in result.data:
        ...         print(component["ref"], component["value"])
    """

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata."""
        return ImporterMetadata(
            name="KiCad BOM Importer",
            description="Import Bill of Materials from KiCad XML or CSV exports",
            supported_formats=("xml", "csv"),
            category="electrical_engineering",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate KiCad BOM file.

        Args:
            source: Path to KiCad BOM file

        Returns:
            True if file exists and has valid extension
        """
        path = Path(source) if isinstance(source, str) else source
        return path.exists() and path.suffix.lower() in (".xml", ".csv")

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import KiCad BOM data.

        Args:
            source: Path to KiCad BOM file

        Returns:
            ImportResult with component data as list of dictionaries

            KiCad BOM parsing and mapping
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
            if path.suffix.lower() == ".xml":
                components = self._parse_xml(path, errors, warnings)
            else:
                components = self._parse_csv(path, errors, warnings)

            # Convert to dictionaries
            data = [
                {
                    "ref": comp.ref,
                    "value": comp.value,
                    "part_number": comp.part_number or comp.value,
                    "description": comp.description or comp.value,
                    "manufacturer": comp.manufacturer,
                    "quantity": comp.quantity,
                    "footprint": comp.footprint,
                    "datasheet": comp.datasheet,
                }
                for comp in components
            ]

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

    def _parse_xml(
        self,
        path: Path,
        errors: list[str],
        warnings: list[str],
    ) -> list[KiCadComponent]:
        """Parse KiCad XML BOM format.

        Args:
            path: Path to XML file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of KiCadComponent objects
        """
        components: list[KiCadComponent] = []

        try:
            tree = ET.parse(path)
            root = tree.getroot()

            # KiCad XML format: <export><components><comp>...</comp></components></export>
            for comp_elem in root.findall(".//comp"):
                ref = comp_elem.get("ref", "")
                value_elem = comp_elem.find("value")
                footprint_elem = comp_elem.find("footprint")
                datasheet_elem = comp_elem.find("datasheet")

                if not ref:
                    warnings.append("Skipping component with missing reference")
                    continue

                components.append(
                    KiCadComponent(
                        ref=ref,
                        value=(value_elem.text or "") if value_elem is not None else "",
                        footprint=(footprint_elem.text or "")
                        if footprint_elem is not None
                        else "",
                        datasheet=(datasheet_elem.text or "")
                        if datasheet_elem is not None
                        else "",
                        quantity=1,
                    )
                )

        except ET.ParseError as e:
            errors.append(f"XML parse error: {e!s}")

        return components

    def _parse_csv(
        self,
        path: Path,
        errors: list[str],
        warnings: list[str],
    ) -> list[KiCadComponent]:
        """Parse KiCad CSV BOM format.

        Args:
            path: Path to CSV file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of KiCadComponent objects
        """
        components: list[KiCadComponent] = []

        try:
            with path.open(encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    ref = row.get("Ref", row.get("Reference", ""))
                    value = row.get("Value", row.get("Val", ""))

                    if not ref:
                        warnings.append(f"Skipping row with missing reference: {row}")
                        continue

                    components.append(
                        KiCadComponent(
                            ref=ref,
                            value=value,
                            footprint=row.get("Footprint", row.get("Package", "")),
                            datasheet=row.get("Datasheet", ""),
                            quantity=int(row.get("Qty", row.get("Quantity", 1))),
                            description=row.get("Description", ""),
                            manufacturer=row.get("Manufacturer", ""),
                            part_number=row.get("Part", row.get("PartNumber", "")),
                        )
                    )

        except Exception as e:
            errors.append(f"CSV parse error: {e!s}")

        return components


__all__ = ["KiCadBOMImporter", "KiCadComponent"]
