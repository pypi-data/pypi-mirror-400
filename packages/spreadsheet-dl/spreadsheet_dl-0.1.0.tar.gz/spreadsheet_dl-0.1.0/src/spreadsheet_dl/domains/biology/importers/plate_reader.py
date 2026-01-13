"""Plate reader data importer.

PlateReaderImporter for microplate data
"""

from __future__ import annotations

import csv
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


class PlateReaderImporter(BaseImporter[dict[str, Any]]):
    """Import plate reader data from various instruments.

        PlateReaderImporter with CSV/XML support

    Features:
    - CSV format support (common export format)
    - XML format support (some instruments)
    - 96-well and 384-well plate layouts
    - Absorbance and fluorescence data
    - Time-series kinetic data
    - Metadata extraction (wavelengths, temperatures)

    Example:
        >>> importer = PlateReaderImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("plate_data.csv")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     plate_data = result.data
        ...     print(f"Wells: {len(plate_data['wells'])}")
        ...     print(f"Type: {plate_data['read_type']}")
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize importer."""
        super().__init__(**kwargs)

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata.

        Returns:
            ImporterMetadata for plate reader importer

            Importer metadata
        """
        return ImporterMetadata(
            name="Plate Reader Importer",
            description="Import microplate reader data (absorbance, fluorescence)",
            supported_formats=("csv", "xml", "txt"),
            category="biology",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate plate reader data file.

        Args:
            source: Path to data file

        Returns:
            True if source is valid

            Source validation
        """
        path = Path(source) if isinstance(source, str) else source
        return (
            path.exists()
            and path.is_file()
            and path.suffix.lower() in (".csv", ".xml", ".txt")
        )

    def import_data(self, source: Path | str) -> ImportResult[dict[str, Any]]:
        """Import plate reader data.

        Args:
            source: Path to data file

        Returns:
            ImportResult with plate data

            Plate reader data import

        Raises:
            ValueError: If source is invalid
            IOError: If file cannot be read
        """
        if not self.validate_source(source):
            return ImportResult(
                success=False,
                data={},
                errors=["Invalid plate reader file or file does not exist"],
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
                data={},
                errors=[f"Error importing plate data: {e!s}"],
            )

    def _import_csv(self, path: Path) -> ImportResult[dict[str, Any]]:
        """Import CSV format plate data.

        Args:
            path: Path to CSV file

        Returns:
            ImportResult with parsed data
        """
        wells: dict[str, float] = {}
        metadata: dict[str, Any] = {
            "read_type": "unknown",
            "wavelength": None,
            "temperature": None,
            "plate_type": "96-well",
        }
        warnings: list[str] = []

        with path.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

            # Try to detect metadata in header
            for _i, line in enumerate(lines[:10]):
                if "wavelength" in line.lower():
                    match = re.search(r"(\d+)\s*nm", line, re.IGNORECASE)
                    if match:
                        metadata["wavelength"] = int(match.group(1))
                if "absorbance" in line.lower():
                    metadata["read_type"] = "absorbance"
                elif "fluorescence" in line.lower():
                    metadata["read_type"] = "fluorescence"
                if "384" in line:
                    metadata["plate_type"] = "384-well"

            # Find data section (look for row labels A, B, C...)
            data_start_idx = 0
            for i, line in enumerate(lines):
                if re.match(r"^\s*[A-H]\s*[,;\t]", line):
                    data_start_idx = i
                    break

            # Parse plate data
            reader = csv.reader(lines[data_start_idx:], delimiter=",")

            for _row_idx, row in enumerate(reader):
                if len(row) < 2:
                    continue

                # First column should be row label (A-H for 96-well, A-P for 384-well)
                row_label = row[0].strip()
                if not re.match(r"^[A-P]$", row_label):
                    continue

                # Parse values for each column
                for col_idx, value in enumerate(row[1:], start=1):
                    if not value or value.strip() == "":
                        continue

                    try:
                        numeric_value = float(value.strip())
                        well_id = f"{row_label}{col_idx}"
                        wells[well_id] = numeric_value
                    except ValueError:
                        # Skip non-numeric values
                        continue

        if not wells:
            warnings.append("No numeric data found in plate layout")

        data = {
            "wells": wells,
            "metadata": metadata,
            "plate_type": metadata["plate_type"],
            "read_type": metadata["read_type"],
        }

        return ImportResult(
            success=True,
            data=data,
            records_imported=len(wells),
            warnings=warnings,
            metadata=metadata,
        )

    def _import_xml(self, path: Path) -> ImportResult[dict[str, Any]]:
        """Import XML format plate data.

        Args:
            path: Path to XML file

        Returns:
            ImportResult with parsed data
        """
        try:
            tree = ET.parse(path)
            root = tree.getroot()

            wells: dict[str, float] = {}
            metadata: dict[str, Any] = {
                "read_type": "unknown",
                "wavelength": None,
                "temperature": None,
                "plate_type": "96-well",
            }

            # Try to extract metadata (format varies by instrument)
            for elem in root.iter():
                if "wavelength" in elem.tag.lower():
                    metadata["wavelength"] = elem.text
                if "temperature" in elem.tag.lower():
                    metadata["temperature"] = elem.text

            # Try to find well data
            for well_elem in root.iter():
                if "well" in well_elem.tag.lower():
                    well_id = well_elem.get("id") or well_elem.get("position")
                    value_text = well_elem.text or well_elem.get("value")

                    if well_id and value_text:
                        try:
                            wells[well_id] = float(value_text)
                        except ValueError:
                            continue

            data = {
                "wells": wells,
                "metadata": metadata,
                "plate_type": metadata["plate_type"],
                "read_type": metadata["read_type"],
            }

            return ImportResult(
                success=True,
                data=data,
                records_imported=len(wells),
                metadata=metadata,
            )

        except ET.ParseError as e:
            return ImportResult(
                success=False,
                data={},
                errors=[f"XML parsing error: {e!s}"],
            )


__all__ = ["PlateReaderImporter"]
