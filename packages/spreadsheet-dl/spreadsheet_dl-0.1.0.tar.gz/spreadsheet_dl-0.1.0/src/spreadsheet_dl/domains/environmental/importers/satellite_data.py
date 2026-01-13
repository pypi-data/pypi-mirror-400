"""Satellite Data Importer.

SatelliteDataImporter for environmental domain
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


@dataclass
class SatelliteDataImporter(BaseImporter[list[dict[str, Any]]]):
    """Remote sensing / satellite data importer.

        SatelliteDataImporter for environmental monitoring

    Supports importing data from:
    - Satellite imagery metadata
    - NDVI and vegetation indices
    - Land cover classifications
    - Climate data products

    Example:
        >>> importer = SatelliteDataImporter(data_product="MODIS_NDVI")  # doctest: +SKIP
        >>> result = importer.import_data("ndvi_timeseries.csv")  # doctest: +SKIP
        >>> print(f"Imported {result.records_imported} satellite observations")  # doctest: +SKIP
    """

    data_product: str = "generic"
    coordinate_system: str = "WGS84"

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata."""
        return ImporterMetadata(
            name="Satellite Data Importer",
            description="Import remote sensing and satellite data",
            supported_formats=("csv", "json", "geojson"),
            category="environmental",
        )

    def import_data(self, source: str | Path) -> ImportResult[list[dict[str, Any]]]:
        """Import satellite data from file."""
        source_path = Path(source)
        data: list[dict[str, Any]] = []
        errors: list[str] = []
        warnings: list[str] = []

        if not source_path.exists():
            return ImportResult(
                success=False,
                data=[],
                records_imported=0,
                errors=[f"File not found: {source_path}"],
                warnings=[],
                metadata={},
            )

        suffix = source_path.suffix.lower()

        try:
            if suffix == ".csv":
                data, errors, warnings = self._import_csv(source_path)
            elif suffix in (".json", ".geojson"):
                data, errors, warnings = self._import_json(source_path)
            else:
                return ImportResult(
                    success=False,
                    data=[],
                    records_imported=0,
                    errors=[f"Unsupported format: {suffix}"],
                    warnings=[],
                    metadata={},
                )

            return ImportResult(
                success=len(errors) == 0,
                data=data,
                records_imported=len(data),
                errors=errors,
                warnings=warnings,
                metadata={
                    "data_product": self.data_product,
                    "coordinate_system": self.coordinate_system,
                    "source": str(source_path),
                },
            )

        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                records_imported=0,
                errors=[f"Import error: {e!s}"],
                warnings=[],
                metadata={},
            )

    def _import_csv(
        self, path: Path
    ) -> tuple[list[dict[str, Any]], list[str], list[str]]:
        """Import from CSV file."""
        data: list[dict[str, Any]] = []
        errors: list[str] = []
        warnings: list[str] = []

        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                record = self._normalize_record(row)
                data.append(record)

                # Validate coordinates
                row_warnings = self._validate_coordinates(record, row_num)
                warnings.extend(row_warnings)

        return data, errors, warnings

    def _import_json(
        self, path: Path
    ) -> tuple[list[dict[str, Any]], list[str], list[str]]:
        """Import from JSON/GeoJSON file."""
        data: list[dict[str, Any]] = []
        errors: list[str] = []
        warnings: list[str] = []

        with open(path, encoding="utf-8") as f:
            content = json.load(f)

        # Handle GeoJSON format
        if isinstance(content, dict) and content.get("type") == "FeatureCollection":
            for feature in content.get("features", []):
                record = self._parse_geojson_feature(feature)
                data.append(record)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    data.append(self._normalize_record(item))
        elif isinstance(content, dict):
            if "data" in content:
                for item in content["data"]:
                    if isinstance(item, dict):
                        data.append(self._normalize_record(item))
            else:
                data.append(self._normalize_record(content))

        return data, errors, warnings

    def _parse_geojson_feature(self, feature: dict[str, Any]) -> dict[str, Any]:
        """Parse a GeoJSON feature into a record."""
        record: dict[str, Any] = {}

        # Extract properties
        properties = feature.get("properties", {})
        record.update(properties)

        # Extract geometry
        geometry = feature.get("geometry", {})
        if geometry.get("type") == "Point":
            coords = geometry.get("coordinates", [])
            if len(coords) >= 2:
                record["longitude"] = coords[0]
                record["latitude"] = coords[1]

        return record

    def _normalize_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Normalize satellite data fields."""
        normalized: dict[str, Any] = {}

        field_mappings = {
            "date": "date",
            "acquisition_date": "date",
            "lat": "latitude",
            "latitude": "latitude",
            "lon": "longitude",
            "longitude": "longitude",
            "lng": "longitude",
            "ndvi": "ndvi",
            "evi": "evi",
            "lst": "land_surface_temp",
            "land_cover": "land_cover",
            "cloud_cover": "cloud_cover",
            "quality": "quality_flag",
        }

        for key, value in record.items():
            normalized_key = field_mappings.get(key.lower(), key.lower())
            normalized[normalized_key] = value

        return normalized

    def _validate_coordinates(self, record: dict[str, Any], row_num: int) -> list[str]:
        """Validate coordinate values."""
        warnings: list[str] = []

        lat = record.get("latitude")
        lon = record.get("longitude")

        if lat is not None:
            try:
                lat_val = float(lat)
                if lat_val < -90 or lat_val > 90:
                    warnings.append(f"Row {row_num}: Invalid latitude {lat_val}")
            except (ValueError, TypeError):
                pass

        if lon is not None:
            try:
                lon_val = float(lon)
                if lon_val < -180 or lon_val > 180:
                    warnings.append(f"Row {row_num}: Invalid longitude {lon_val}")
            except (ValueError, TypeError):
                pass

        return warnings

    def validate_source(self, source: str | Path) -> bool:
        """Validate source file."""
        path = Path(source)
        return path.exists() and path.suffix.lower() in (".csv", ".json", ".geojson")


__all__ = ["SatelliteDataImporter"]
