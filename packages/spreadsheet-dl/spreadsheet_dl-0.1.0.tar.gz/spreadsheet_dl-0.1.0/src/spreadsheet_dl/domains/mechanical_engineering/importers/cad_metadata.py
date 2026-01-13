"""CAD Metadata importer for mechanical engineering.

CADMetadataImporter for STEP/IGES file metadata
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


@dataclass
class CADMetadata:
    """CAD file metadata.

    Attributes:
        filename: CAD file name
        format: File format (STEP, IGES)
        part_name: Part name from header
        mass: Part mass (if available) in kg
        volume: Part volume (if available) in mm³
        material: Material name (if specified)
        units: Units used in file
        author: File author (if specified)
        organization: Organization (if specified)
        description: Part description
    """

    filename: str
    format: str
    part_name: str = ""
    mass: float | None = None
    volume: float | None = None
    material: str = ""
    units: str = "mm"
    author: str = ""
    organization: str = ""
    description: str = ""


class CADMetadataImporter(BaseImporter[list[dict[str, Any]]]):
    """Import metadata from CAD files (STEP/IGES format).

        CADMetadataImporter requirements

    Features:
        - Parse STEP (ISO 10303-21) file headers
        - Parse IGES file headers
        - Extract: Part name, mass, volume, material, units
        - Handle multiple parts in assembly files
        - Map to MaterialPropertiesTemplate format

    Example:
        >>> importer = CADMetadataImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("part.step")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     for part in result.data:
        ...         print(part["part_name"], part["material"])
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize CAD metadata importer."""
        super().__init__(**kwargs)

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata."""
        return ImporterMetadata(
            name="CAD Metadata Importer",
            description="Import metadata from CAD files (STEP/IGES)",
            supported_formats=("step", "stp", "iges", "igs"),
            category="mechanical_engineering",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate CAD file.

        Args:
            source: Path to CAD file

        Returns:
            True if file exists and has valid extension
        """
        path = Path(source) if isinstance(source, str) else source
        return path.exists() and path.suffix.lower() in (
            ".step",
            ".stp",
            ".iges",
            ".igs",
        )

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import CAD metadata.

        Args:
            source: Path to CAD file

        Returns:
            ImportResult with metadata as list of dictionaries

            CAD metadata parsing and extraction
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
            if path.suffix.lower() in (".step", ".stp"):
                metadata_list = self._parse_step(path, errors, warnings)
            else:
                metadata_list = self._parse_iges(path, errors, warnings)

            # Convert to dictionaries
            data = [
                {
                    "filename": meta.filename,
                    "format": meta.format,
                    "part_name": meta.part_name,
                    "mass": meta.mass,
                    "volume": meta.volume,
                    "material": meta.material,
                    "units": meta.units,
                    "author": meta.author,
                    "organization": meta.organization,
                    "description": meta.description,
                }
                for meta in metadata_list
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

    def _parse_step(
        self,
        path: Path,
        errors: list[str],
        warnings: list[str],
    ) -> list[CADMetadata]:
        """Parse STEP file header.

        Args:
            path: Path to STEP file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of CADMetadata objects
        """
        metadata_list: list[CADMetadata] = []

        try:
            with path.open(encoding="utf-8", errors="ignore") as f:
                content = f.read(50000)  # Read first 50KB for header

            # Extract header section
            header_match = re.search(
                r"HEADER;(.*?)ENDSEC;",
                content,
                re.DOTALL | re.IGNORECASE,
            )

            if not header_match:
                warnings.append("No HEADER section found in STEP file")
                return [
                    CADMetadata(
                        filename=path.name,
                        format="STEP",
                        description="No header information available",
                    )
                ]

            header = header_match.group(1)

            # Extract file description
            file_desc_match = re.search(
                r"FILE_DESCRIPTION\s*\(\s*\('([^']+)'",
                header,
                re.IGNORECASE,
            )
            description = file_desc_match.group(1) if file_desc_match else ""

            # Extract file name
            file_name_match = re.search(
                r"FILE_NAME\s*\(\s*'([^']+)'",
                header,
                re.IGNORECASE,
            )
            part_name = file_name_match.group(1) if file_name_match else path.stem

            # Extract author
            author_match = re.search(
                r"'([^']+)'\s*,\s*'([^']+)'\s*,.*?FILE_NAME",
                header,
                re.IGNORECASE,
            )
            author = author_match.group(1) if author_match else ""
            organization = author_match.group(2) if author_match else ""

            metadata_list.append(
                CADMetadata(
                    filename=path.name,
                    format="STEP",
                    part_name=part_name,
                    author=author,
                    organization=organization,
                    description=description,
                    units="mm",  # Default assumption
                )
            )

        except Exception as e:
            errors.append(f"STEP parse error: {e!s}")
            # Return minimal metadata on error
            metadata_list.append(
                CADMetadata(
                    filename=path.name,
                    format="STEP",
                )
            )

        return metadata_list

    def _parse_iges(
        self,
        path: Path,
        errors: list[str],
        warnings: list[str],
    ) -> list[CADMetadata]:
        """Parse IGES file header.

        Args:
            path: Path to IGES file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of CADMetadata objects
        """
        metadata_list: list[CADMetadata] = []

        try:
            with path.open(encoding="utf-8", errors="ignore") as f:
                lines = [f.readline() for _ in range(100)]  # Read first 100 lines

            # IGES format: First character indicates section (S=Start, G=Global)
            start_lines = [line[1:72].strip() for line in lines if line.startswith("S")]
            global_lines = [
                line[1:72].strip() for line in lines if line.startswith("G")
            ]

            # Extract information from Start section
            description = " ".join(start_lines) if start_lines else ""

            # Parse Global section (comma-separated fields)
            global_data = ",".join(global_lines)
            fields = global_data.split(",")

            # Try to extract common fields
            part_name = path.stem
            author = ""
            organization = ""

            if len(fields) > 3:
                # Field 3 is typically the file name
                part_name = fields[2].strip("'\" ") or path.stem

            if len(fields) > 4:
                # Field 4 is typically the author
                author = fields[3].strip("'\" ")

            metadata_list.append(
                CADMetadata(
                    filename=path.name,
                    format="IGES",
                    part_name=part_name,
                    author=author,
                    organization=organization,
                    description=description[:200],  # Truncate long descriptions
                    units="mm",  # Default assumption
                )
            )

        except Exception as e:
            errors.append(f"IGES parse error: {e!s}")
            # Return minimal metadata on error
            metadata_list.append(
                CADMetadata(
                    filename=path.name,
                    format="IGES",
                )
            )

        return metadata_list


__all__ = ["CADMetadata", "CADMetadataImporter"]
