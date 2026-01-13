"""FEA Results importer for mechanical engineering.

FEAResultsImporter for FEA simulation results
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


@dataclass
class FEANode:
    """FEA node result data.

    Attributes:
        node_id: Node identifier
        x: X coordinate (mm)
        y: Y coordinate (mm)
        z: Z coordinate (mm)
        stress_x: Normal stress in X direction (MPa)
        stress_y: Normal stress in Y direction (MPa)
        stress_z: Normal stress in Z direction (MPa)
        stress_vm: von Mises stress (MPa)
        displacement: Total displacement (mm)
        strain: Equivalent strain
    """

    node_id: int
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    stress_x: float = 0.0
    stress_y: float = 0.0
    stress_z: float = 0.0
    stress_vm: float = 0.0
    displacement: float = 0.0
    strain: float = 0.0


class FEAResultsImporter(BaseImporter[list[dict[str, Any]]]):
    """Import FEA (Finite Element Analysis) results from CSV or JSON files.

        FEAResultsImporter requirements

    Features:
        - Parse FEA results in CSV or JSON format
        - Extract: Node ID, coordinates, stresses, displacement, strain
        - Support common FEA output formats (ANSYS, Abaqus, CalculiX)
        - Map to StressAnalysisTemplate format
        - Handle large result sets efficiently

    Example:
        >>> importer = FEAResultsImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("fea_results.csv")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     for node in result.data:
        ...         print(node["node_id"], node["stress_vm"])
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize FEA results importer."""
        super().__init__(**kwargs)

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata."""
        return ImporterMetadata(
            name="FEA Results Importer",
            description="Import FEA simulation results from CSV or JSON",
            supported_formats=("csv", "json"),
            category="mechanical_engineering",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate FEA results file.

        Args:
            source: Path to FEA results file

        Returns:
            True if file exists and has valid extension
        """
        path = Path(source) if isinstance(source, str) else source
        return path.exists() and path.suffix.lower() in (".csv", ".json")

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import FEA results data.

        Args:
            source: Path to FEA results file

        Returns:
            ImportResult with node data as list of dictionaries

            FEA results parsing and mapping
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
                nodes = self._parse_json(path, errors, warnings)
            else:
                nodes = self._parse_csv(path, errors, warnings)

            # Convert to dictionaries
            data = [
                {
                    "node_id": node.node_id,
                    "x": node.x,
                    "y": node.y,
                    "z": node.z,
                    "stress_x": node.stress_x,
                    "stress_y": node.stress_y,
                    "stress_z": node.stress_z,
                    "stress_vm": node.stress_vm,
                    "displacement": node.displacement,
                    "strain": node.strain,
                }
                for node in nodes
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
    ) -> list[FEANode]:
        """Parse FEA results CSV format.

        Args:
            path: Path to CSV file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of FEANode objects
        """
        nodes: list[FEANode] = []

        try:
            with path.open(encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, start=1):
                    try:
                        # Try various common column name variations
                        node_id = int(
                            row.get("NodeID")
                            or row.get("Node")
                            or row.get("ID")
                            or row.get("node_id")
                            or "0"
                        )

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

                        nodes.append(
                            FEANode(
                                node_id=node_id,
                                x=get_float("X", "x", "CoordX"),
                                y=get_float("Y", "y", "CoordY"),
                                z=get_float("Z", "z", "CoordZ"),
                                stress_x=get_float("StressX", "SX", "stress_x", "sx"),
                                stress_y=get_float("StressY", "SY", "stress_y", "sy"),
                                stress_z=get_float("StressZ", "SZ", "stress_z", "sz"),
                                stress_vm=get_float(
                                    "VonMises",
                                    "VM",
                                    "von_mises",
                                    "stress_vm",
                                    "vonmises",
                                ),
                                displacement=get_float(
                                    "Displacement",
                                    "USUM",
                                    "disp",
                                    "displacement",
                                ),
                                strain=get_float(
                                    "Strain",
                                    "EPEL",
                                    "strain",
                                    "equivalent_strain",
                                ),
                            )
                        )
                    except (ValueError, KeyError) as e:
                        warnings.append(f"Skipping row {row_num}: {e!s}")
                        continue

        except Exception as e:
            errors.append(f"CSV parse error: {e!s}")

        return nodes

    def _parse_json(
        self,
        path: Path,
        errors: list[str],
        warnings: list[str],
    ) -> list[FEANode]:
        """Parse FEA results JSON format.

        Args:
            path: Path to JSON file
            errors: List to append errors to
            warnings: List to append warnings to

        Returns:
            List of FEANode objects
        """
        nodes: list[FEANode] = []

        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)

            # Handle both array of nodes and nested structure
            node_data: list[Any] = []
            if isinstance(data, dict):
                nodes_raw = data.get("nodes", data.get("results", []))
                if isinstance(nodes_raw, list):
                    node_data = nodes_raw
            elif isinstance(data, list):
                node_data = data

            for item in node_data:
                try:
                    nodes.append(
                        FEANode(
                            node_id=item.get("node_id", item.get("id", 0)),
                            x=float(item.get("x", item.get("X", 0.0))),
                            y=float(item.get("y", item.get("Y", 0.0))),
                            z=float(item.get("z", item.get("Z", 0.0))),
                            stress_x=float(item.get("stress_x", item.get("sx", 0.0))),
                            stress_y=float(item.get("stress_y", item.get("sy", 0.0))),
                            stress_z=float(item.get("stress_z", item.get("sz", 0.0))),
                            stress_vm=float(
                                item.get(
                                    "stress_vm",
                                    item.get("von_mises", item.get("vm", 0.0)),
                                )
                            ),
                            displacement=float(
                                item.get("displacement", item.get("disp", 0.0))
                            ),
                            strain=float(item.get("strain", 0.0)),
                        )
                    )
                except (ValueError, KeyError, TypeError) as e:
                    warnings.append(f"Skipping node: {e!s}")
                    continue

        except Exception as e:
            errors.append(f"JSON parse error: {e!s}")

        return nodes


__all__ = ["FEANode", "FEAResultsImporter"]
