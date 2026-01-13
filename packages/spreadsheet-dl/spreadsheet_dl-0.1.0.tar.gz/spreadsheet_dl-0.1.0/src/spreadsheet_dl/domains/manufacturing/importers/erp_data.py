"""ERP Data Importer for production and inventory data.

ERPDataImporter for manufacturing domain
"""

from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


class ERPDataImporter(BaseImporter[list[dict[str, Any]]]):
    """Import ERP production/inventory data (CSV/XML).

        ERPDataImporter with production and inventory data

    Features:
    - Production order data
    - Inventory levels and transactions
    - Purchase orders
    - Material requirements
    - Cost data
    - CSV and XML format support

    Example:
        >>> importer = ERPDataImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("erp_export.xml")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     print(f"Imported {result.records_imported} ERP records")
        ...     for record in result.data:
        ...         print(f"Part: {record['part_number']}, Qty: {record['quantity']}")
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize importer."""
        super().__init__(**kwargs)

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata.

        Returns:
            ImporterMetadata for ERP data importer

            Importer metadata
        """
        return ImporterMetadata(
            name="ERP Data Importer",
            description="Import ERP production and inventory data from CSV/XML",
            supported_formats=("csv", "xml"),
            category="manufacturing",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate ERP data source file.

        Args:
            source: Path to ERP data file

        Returns:
            True if source is valid file

            Source validation
        """
        path = Path(source) if isinstance(source, str) else source
        return (
            path.exists() and path.is_file() and path.suffix.lower() in (".csv", ".xml")
        )

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import data from ERP file.

        Args:
            source: Path to ERP data file (CSV or XML)

        Returns:
            ImportResult with parsed ERP data

            Data import with error handling

        Raises:
            ValueError: If source is invalid
            IOError: If file cannot be read
        """
        if not self.validate_source(source):
            return ImportResult(
                success=False,
                data=[],
                errors=["Invalid ERP data file or file does not exist"],
            )

        path = Path(source) if isinstance(source, str) else source

        try:
            if path.suffix.lower() == ".xml":
                return self._import_xml(path)
            else:
                return self._import_csv(path)
        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"Error importing ERP data: {e!s}"],
            )

    def _import_csv(self, path: Path) -> ImportResult[list[dict[str, Any]]]:
        """Import ERP data from CSV file."""
        records = []
        errors = []

        try:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)

                for row_idx, row in enumerate(reader):
                    try:
                        record = self._parse_erp_record(row)
                        records.append(record)
                        self.on_progress(row_idx + 1, len(records))
                    except Exception as e:
                        errors.append(f"Row {row_idx + 1}: {e!s}")
                        continue

            return ImportResult(
                success=True,
                data=records,
                records_imported=len(records),
                errors=errors,
                metadata={
                    "source_file": str(path),
                    "format": "csv",
                    "import_date": datetime.now().isoformat(),
                },
            )
        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"CSV read error: {e!s}"],
            )

    def _import_xml(self, path: Path) -> ImportResult[list[dict[str, Any]]]:
        """Import ERP data from XML file."""
        try:
            tree = ET.parse(path)
            root = tree.getroot()

            records = []
            errors = []

            # Handle different XML structures
            # Try common ERP XML formats
            record_elements = (
                root.findall(".//record")
                or root.findall(".//item")
                or root.findall(".//row")
                or list(root)
            )

            for idx, element in enumerate(record_elements):
                try:
                    # Convert XML element to dict
                    raw_record = self._xml_element_to_dict(element)
                    record = self._parse_erp_record(raw_record)
                    records.append(record)
                    self.on_progress(idx + 1, len(record_elements))
                except Exception as e:
                    errors.append(f"Record {idx + 1}: {e!s}")
                    continue

            return ImportResult(
                success=True,
                data=records,
                records_imported=len(records),
                errors=errors,
                metadata={
                    "source_file": str(path),
                    "format": "xml",
                    "import_date": datetime.now().isoformat(),
                },
            )
        except ET.ParseError as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"XML parse error: {e!s}"],
            )
        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"Error reading XML: {e!s}"],
            )

    def _xml_element_to_dict(self, element: ET.Element) -> dict[str, Any]:
        """Convert XML element to dictionary."""
        result: dict[str, Any] = {}

        # Add attributes
        result.update(element.attrib)

        # Add child elements
        for child in element:
            # Use tag name as key (remove namespace if present)
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

            if child.text and child.text.strip():
                result[tag] = child.text.strip()
            elif len(child) > 0:
                result[tag] = self._xml_element_to_dict(child)
            else:
                result[tag] = child.attrib if child.attrib else ""

        # If no children, use element text
        if not result and element.text:
            return {"value": element.text.strip()}

        return result

    def _parse_erp_record(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Parse ERP record with type conversion.

        Args:
            raw: Raw record data

        Returns:
            Parsed ERP record with standardized fields

            ERP record parsing
        """
        # Standardize field names (handle various ERP system formats)
        record: dict[str, Any] = {
            "part_number": str(
                raw.get("part_number", raw.get("item_id", raw.get("sku", "")))
            ),
            "description": str(raw.get("description", raw.get("item_name", ""))),
            "quantity": self._parse_number(raw.get("quantity", raw.get("qty", 0))),
            "unit_cost": self._parse_number(raw.get("unit_cost", raw.get("cost", 0))),
            "location": str(raw.get("location", raw.get("warehouse", ""))),
            "supplier": str(raw.get("supplier", raw.get("vendor", ""))),
            "lead_time": self._parse_number(raw.get("lead_time", 0)),
            "reorder_point": self._parse_number(raw.get("reorder_point", 0)),
            "order_quantity": self._parse_number(raw.get("order_quantity", 0)),
        }

        # Add any additional fields
        for key, value in raw.items():
            if key not in record:
                record[key] = value

        return record

    def _parse_number(self, value: Any) -> float:
        """Parse numeric value safely."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.replace(",", ""))
            except ValueError:
                return 0.0
        return 0.0


__all__ = ["ERPDataImporter"]
