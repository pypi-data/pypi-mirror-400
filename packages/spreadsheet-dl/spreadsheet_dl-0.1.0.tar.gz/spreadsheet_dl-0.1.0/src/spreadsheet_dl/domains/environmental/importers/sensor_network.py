"""Sensor Network Data Importer.

SensorNetworkImporter for environmental domain
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


@dataclass
class SensorNetworkImporter(BaseImporter[list[dict[str, Any]]]):
    """IoT sensor network data importer.

        SensorNetworkImporter for environmental monitoring

    Supports importing data from:
    - IoT sensor exports (CSV, JSON)
    - Time-series environmental data
    - Multi-parameter sensor readings

    Example:
        >>> importer = SensorNetworkImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("sensor_readings.csv")  # doctest: +SKIP
        >>> print(f"Imported {result.records_imported} sensor readings")  # doctest: +SKIP
    """

    sensor_type: str = "environmental"
    validate_ranges: bool = True

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata."""
        return ImporterMetadata(
            name="Sensor Network Importer",
            description="Import IoT environmental sensor data",
            supported_formats=("csv", "json"),
            category="environmental",
        )

    def import_data(self, source: str | Path) -> ImportResult[list[dict[str, Any]]]:
        """Import sensor data from file."""
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
            elif suffix == ".json":
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
                metadata={"sensor_type": self.sensor_type, "source": str(source_path)},
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

                # Validate ranges if enabled
                if self.validate_ranges:
                    row_warnings = self._validate_reading(record, row_num)
                    warnings.extend(row_warnings)

        return data, errors, warnings

    def _import_json(
        self, path: Path
    ) -> tuple[list[dict[str, Any]], list[str], list[str]]:
        """Import from JSON file."""
        data: list[dict[str, Any]] = []
        errors: list[str] = []
        warnings: list[str] = []

        with open(path, encoding="utf-8") as f:
            content = json.load(f)

        if isinstance(content, list):
            for item in content:
                data.append(self._normalize_record(item))
        elif isinstance(content, dict):
            if "readings" in content:
                for item in content["readings"]:
                    data.append(self._normalize_record(item))
            else:
                data.append(self._normalize_record(content))

        return data, errors, warnings

    def _normalize_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Normalize sensor reading fields."""
        normalized: dict[str, Any] = {}

        field_mappings = {
            "timestamp": "timestamp",
            "time": "timestamp",
            "datetime": "timestamp",
            "sensor_id": "sensor_id",
            "device_id": "sensor_id",
            "temperature": "temperature",
            "temp": "temperature",
            "humidity": "humidity",
            "rh": "humidity",
            "pressure": "pressure",
            "pm25": "pm25",
            "pm2_5": "pm25",
            "pm10": "pm10",
            "co2": "co2",
            "voc": "voc",
        }

        for key, value in record.items():
            normalized_key = field_mappings.get(key.lower(), key.lower())
            normalized[normalized_key] = value

        return normalized

    def _validate_reading(self, record: dict[str, Any], row_num: int) -> list[str]:
        """Validate sensor reading ranges."""
        warnings: list[str] = []

        # Temperature validation
        temp = record.get("temperature")
        if temp is not None:
            try:
                temp_val = float(temp)
                if temp_val < -50 or temp_val > 60:
                    warnings.append(f"Row {row_num}: Unusual temperature {temp_val}C")
            except (ValueError, TypeError):
                pass

        # PM2.5 validation
        pm25 = record.get("pm25")
        if pm25 is not None:
            try:
                pm25_val = float(pm25)
                if pm25_val > 500:
                    warnings.append(f"Row {row_num}: Very high PM2.5 {pm25_val}")
            except (ValueError, TypeError):
                pass

        return warnings

    def validate_source(self, source: str | Path) -> bool:
        """Validate source file."""
        path = Path(source)
        return path.exists() and path.suffix.lower() in (".csv", ".json")


__all__ = ["SensorNetworkImporter"]
