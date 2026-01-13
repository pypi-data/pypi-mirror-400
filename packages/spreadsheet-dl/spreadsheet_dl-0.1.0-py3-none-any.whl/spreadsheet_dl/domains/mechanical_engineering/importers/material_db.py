"""Material Database importer for mechanical engineering.

MaterialDatabaseImporter for material property databases
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


@dataclass
class MaterialProperties:
    """Material properties data.

    Attributes:
        name: Material name
        specification: Material specification (e.g., ASTM, ISO)
        yield_strength: Yield strength (MPa)
        ultimate_strength: Ultimate tensile strength (MPa)
        youngs_modulus: Young's modulus (GPa)
        poissons_ratio: Poisson's ratio (dimensionless)
        density: Density (kg/m³)
        cte: Coefficient of thermal expansion (10⁻⁶/°C)
        hardness: Hardness (HV, HRC, etc.)
        category: Material category (steel, aluminum, etc.)
    """

    name: str
    specification: str = ""
    yield_strength: float = 0.0
    ultimate_strength: float = 0.0
    youngs_modulus: float = 0.0
    poissons_ratio: float = 0.0
    density: float = 0.0
    cte: float = 0.0
    hardness: str = ""
    category: str = ""


class MaterialDatabaseImporter(BaseImporter[list[dict[str, Any]]]):
    """Import material property databases from CSV or JSON files.

        MaterialDatabaseImporter requirements

    Features:
        - Parse material databases in CSV or JSON format
        - Extract: Name, yield strength, ultimate strength, Young's modulus, etc.
        - Support common material database formats
        - Map to MaterialPropertiesTemplate format
        - Handle multiple material categories

    Example:
        >>> importer = MaterialDatabaseImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("materials.csv")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     for material in result.data:
        ...         print(material["name"], material["yield_strength"])
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize material database importer."""
        super().__init__(**kwargs)

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata."""
        return ImporterMetadata(
            name="Material Database Importer",
            description="Import material properties from CSV or JSON database",
            supported_formats=("csv", "json"),
            category="mechanical_engineering",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate material database file.

        Args:
            source: Path to material database file

        Returns:
            True if file exists and has valid extension
        """
        path = Path(source) if isinstance(source, str) else source
        return path.exists() and path.suffix.lower() in (".csv", ".json")

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import material database.

        Args:
            source: Path to material database file

        Returns:
            ImportResult with material data as list of dictionaries

            Material database parsing and mapping
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
            if path.suffix.lower() == ".json":
                materials = self._parse_json(path, errors, warnings)
            else:
                materials = self._parse_csv(path, errors, warnings)

            # Convert to dictionaries
            data = [
                {
                    "name": mat.name,
                    "specification": mat.specification,
                    "yield_strength": mat.yield_strength,
                    "ultimate_strength": mat.ultimate_strength,
                    "youngs_modulus": mat.youngs_modulus,
                    "poissons_ratio": mat.poissons_ratio,
                    "density": mat.density,
                    "cte": mat.cte,
                    "hardness": mat.hardness,
                    "category": mat.category,
                }
                for mat in materials
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

    def _parse_csv(
        self,
        path: Path,
        errors: list[str],
        warnings: list[str],
    ) -> list[MaterialProperties]:
        """Parse material database CSV format.

        Args:
            path: Path to CSV file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of MaterialProperties objects
        """
        materials: list[MaterialProperties] = []

        try:
            with path.open(encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, start=1):
                    try:
                        # Get material name (required)
                        name = (
                            row.get("Name")
                            or row.get("Material")
                            or row.get("name")
                            or ""
                        )
                        if not name:
                            warnings.append(f"Skipping row {row_num}: No material name")
                            continue

                        def get_float(
                            *keys: str,
                            default: float = 0.0,
                            row_data: dict[str, Any] = row,
                        ) -> float:
                            for key in keys:
                                if row_data.get(key):
                                    try:
                                        return float(row_data[key])
                                    except ValueError:
                                        continue
                            return default

                        def get_str(
                            *keys: str,
                            default: str = "",
                            row_data: dict[str, Any] = row,
                        ) -> str:
                            for key in keys:
                                if row_data.get(key):
                                    return str(row_data[key])
                            return default

                        materials.append(
                            MaterialProperties(
                                name=name,
                                specification=get_str(
                                    "Specification", "Spec", "spec", "standard"
                                ),
                                yield_strength=get_float(
                                    "YieldStrength",
                                    "Yield",
                                    "yield_strength",
                                    "Sy",
                                ),
                                ultimate_strength=get_float(
                                    "UltimateStrength",
                                    "Ultimate",
                                    "ultimate_strength",
                                    "Su",
                                    "UTS",
                                ),
                                youngs_modulus=get_float(
                                    "YoungsModulus",
                                    "Modulus",
                                    "youngs_modulus",
                                    "E",
                                ),
                                poissons_ratio=get_float(
                                    "PoissonsRatio",
                                    "Poisson",
                                    "poissons_ratio",
                                    "nu",
                                ),
                                density=get_float("Density", "density", "rho"),
                                cte=get_float(
                                    "CTE", "cte", "alpha", "ThermalExpansion"
                                ),
                                hardness=get_str("Hardness", "hardness"),
                                category=get_str(
                                    "Category", "category", "Type", "type"
                                ),
                            )
                        )
                    except Exception as e:
                        warnings.append(f"Error parsing row {row_num}: {e!s}")
                        continue

        except Exception as e:
            errors.append(f"CSV parse error: {e!s}")

        return materials

    def _parse_json(
        self,
        path: Path,
        errors: list[str],
        warnings: list[str],
    ) -> list[MaterialProperties]:
        """Parse material database JSON format.

        Args:
            path: Path to JSON file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of MaterialProperties objects
        """
        materials: list[MaterialProperties] = []

        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)

            # Handle both array of materials and nested structure
            material_data: list[Any] = []
            if isinstance(data, dict):
                materials_raw = data.get("materials", data.get("data", []))
                if isinstance(materials_raw, list):
                    material_data = materials_raw
            elif isinstance(data, list):
                material_data = data

            for item in material_data:
                try:
                    name = item.get("name", item.get("Name", ""))
                    if not name:
                        warnings.append("Skipping material without name")
                        continue

                    materials.append(
                        MaterialProperties(
                            name=name,
                            specification=item.get(
                                "specification", item.get("spec", "")
                            ),
                            yield_strength=float(
                                item.get("yield_strength", item.get("Sy", 0.0))
                            ),
                            ultimate_strength=float(
                                item.get("ultimate_strength", item.get("Su", 0.0))
                            ),
                            youngs_modulus=float(
                                item.get("youngs_modulus", item.get("E", 0.0))
                            ),
                            poissons_ratio=float(
                                item.get("poissons_ratio", item.get("nu", 0.0))
                            ),
                            density=float(item.get("density", item.get("rho", 0.0))),
                            cte=float(item.get("cte", item.get("alpha", 0.0))),
                            hardness=str(item.get("hardness", "")),
                            category=str(item.get("category", item.get("type", ""))),
                        )
                    )
                except (ValueError, KeyError, TypeError) as e:
                    warnings.append(f"Skipping material: {e!s}")
                    continue

        except Exception as e:
            errors.append(f"JSON parse error: {e!s}")

        return materials


__all__ = ["MaterialDatabaseImporter", "MaterialProperties"]
