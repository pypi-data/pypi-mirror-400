"""Sensor Data Importer for IoT sensor data.

SensorDataImporter for manufacturing domain
"""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


class SensorDataImporter(BaseImporter[list[dict[str, Any]]]):
    """Import IoT sensor data (CSV/JSON time series).

        SensorDataImporter with time series data

    Features:
    - Equipment sensor readings
    - Temperature, pressure, vibration data
    - Timestamp parsing
    - Time series data handling
    - Anomaly detection support
    - CSV and JSON format support

    Example:
        >>> importer = SensorDataImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("sensor_data.csv")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     print(f"Imported {result.records_imported} sensor readings")
        ...     for record in result.data:
        ...         print(f"Time: {record['timestamp']}, Temp: {record['temperature']}")
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize importer."""
        super().__init__(**kwargs)

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata.

        Returns:
            ImporterMetadata for sensor data importer

            Importer metadata
        """
        return ImporterMetadata(
            name="Sensor Data Importer",
            description="Import IoT sensor data time series from CSV/JSON",
            supported_formats=("csv", "json"),
            category="manufacturing",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate sensor data source file.

        Args:
            source: Path to sensor data file

        Returns:
            True if source is valid file

            Source validation
        """
        path = Path(source) if isinstance(source, str) else source
        return (
            path.exists()
            and path.is_file()
            and path.suffix.lower() in (".csv", ".json")
        )

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import data from sensor data file.

        Args:
            source: Path to sensor data file (CSV or JSON)

        Returns:
            ImportResult with parsed sensor data

            Data import with error handling

        Raises:
            ValueError: If source is invalid
            IOError: If file cannot be read
        """
        if not self.validate_source(source):
            return ImportResult(
                success=False,
                data=[],
                errors=["Invalid sensor data file or file does not exist"],
            )

        path = Path(source) if isinstance(source, str) else source

        try:
            if path.suffix.lower() == ".json":
                return self._import_json(path)
            else:
                return self._import_csv(path)
        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"Error importing sensor data: {e!s}"],
            )

    def _import_csv(self, path: Path) -> ImportResult[list[dict[str, Any]]]:
        """Import sensor data from CSV file."""
        records = []
        errors = []

        try:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)

                for row_idx, row in enumerate(reader):
                    try:
                        record = self._parse_sensor_record(row)
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
                    "time_range": self._get_time_range(records),
                },
            )
        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"CSV read error: {e!s}"],
            )

    def _import_json(self, path: Path) -> ImportResult[list[dict[str, Any]]]:
        """Import sensor data from JSON file."""
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle both array and object with readings/data key
            if isinstance(data, dict):
                raw_records = (
                    data.get("readings")
                    or data.get("data")
                    or data.get("samples")
                    or []
                )
            elif isinstance(data, list):
                raw_records = data
            else:
                return ImportResult(
                    success=False,
                    data=[],
                    errors=[
                        "Invalid JSON structure: expected array or {readings/data: [...]}"
                    ],
                )

            records = []
            errors = []

            for idx, raw_record in enumerate(raw_records):
                try:
                    record = self._parse_sensor_record(raw_record)
                    records.append(record)
                    self.on_progress(idx + 1, len(raw_records))
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
                    "format": "json",
                    "import_date": datetime.now().isoformat(),
                    "time_range": self._get_time_range(records),
                },
            )
        except json.JSONDecodeError as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"JSON parse error: {e!s}"],
            )
        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"Error reading JSON: {e!s}"],
            )

    def _parse_sensor_record(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Parse sensor record with type conversion.

        Args:
            raw: Raw sensor record data

        Returns:
            Parsed sensor record with standardized fields

            Sensor record parsing
        """
        # Standardize field names (handle various sensor formats)
        record: dict[str, Any] = {
            "timestamp": self._parse_timestamp(
                raw.get("timestamp", raw.get("time", raw.get("datetime", "")))
            ),
            "sensor_id": str(raw.get("sensor_id", raw.get("device_id", ""))),
            "equipment": str(raw.get("equipment", raw.get("machine", ""))),
            "temperature": self._parse_number(raw.get("temperature", raw.get("temp"))),
            "pressure": self._parse_number(raw.get("pressure")),
            "vibration": self._parse_number(raw.get("vibration")),
            "rpm": self._parse_number(raw.get("rpm", raw.get("speed"))),
            "current": self._parse_number(raw.get("current", raw.get("amperage"))),
            "voltage": self._parse_number(raw.get("voltage")),
        }

        # Add any additional sensor fields
        for key, value in raw.items():
            if key not in record:
                # Try to parse as number if looks numeric
                if isinstance(value, (int, float)):
                    record[key] = float(value)
                elif isinstance(value, str):
                    try:
                        record[key] = float(value)
                    except ValueError:
                        record[key] = value
                else:
                    record[key] = value

        return record

    def _parse_timestamp(self, value: Any) -> str:
        """Parse timestamp value."""
        if not value:
            return ""

        if isinstance(value, str):
            # Try to parse and standardize timestamp
            try:
                # Try ISO format
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt.isoformat()
            except (ValueError, AttributeError):
                # Return as-is if can't parse
                return value

        if isinstance(value, (int, float)):
            # Assume Unix timestamp
            try:
                dt = datetime.fromtimestamp(value)
                return dt.isoformat()
            except (ValueError, OSError):
                return str(value)

        return str(value)

    def _parse_number(self, value: Any) -> float | None:
        """Parse numeric value safely."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.replace(",", ""))
            except ValueError:
                return None
        return None

    def _get_time_range(self, records: list[dict[str, Any]]) -> dict[str, str]:
        """Get time range from records."""
        if not records:
            return {"start": "", "end": ""}

        timestamps: list[str] = [
            str(r.get("timestamp")) for r in records if r.get("timestamp")
        ]
        if not timestamps:
            return {"start": "", "end": ""}

        return {
            "start": min(timestamps),
            "end": max(timestamps),
        }


__all__ = ["SensorDataImporter"]
