"""Round-trip serialization for spreadsheet definitions.

Provides conversion between SpreadsheetDL internal representation
and various formats (YAML, JSON) with full fidelity preservation.
"""

from __future__ import annotations

import json
from dataclasses import is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, TypeVar

import yaml

from spreadsheet_dl.builder import (
    CellSpec,
    ColumnSpec,
    NamedRange,
    RangeRef,
    RowSpec,
    SheetSpec,
)
from spreadsheet_dl.charts import (
    AxisConfig,
    ChartPosition,
    ChartSize,
    ChartSpec,
    ChartTitle,
    ChartType,
    DataLabelConfig,
    DataSeries,
    LegendConfig,
    LegendPosition,
)

T = TypeVar("T")


class SpreadsheetEncoder(json.JSONEncoder):
    """JSON encoder for spreadsheet data structures.

    Handles:
    - Dataclass instances
    - Enums
    - Decimal values
    - Date/datetime objects
    - Path objects
    """

    def _encode_value(self, obj: Any) -> Any:
        """Recursively encode a value with type markers."""
        if is_dataclass(obj) and not isinstance(obj, type):
            # Convert dataclass to dict with type marker
            from dataclasses import fields

            result = {"_type": obj.__class__.__name__}
            # Recursively encode fields by accessing attributes directly
            for field in fields(obj):
                field_value = getattr(obj, field.name)
                result[field.name] = self._encode_value(field_value)
            return result
        elif isinstance(obj, Enum):
            return {"_enum": obj.__class__.__name__, "_value": obj.value}
        elif isinstance(obj, Decimal):
            return {"_decimal": str(obj)}
        elif isinstance(obj, datetime):
            return {"_datetime": obj.isoformat()}
        elif isinstance(obj, date):
            return {"_date": obj.isoformat()}
        elif isinstance(obj, Path):
            return {"_path": str(obj)}
        elif isinstance(obj, list):
            return [self._encode_value(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._encode_value(v) for k, v in obj.items()}
        else:
            return obj

    def default(self, obj: Any) -> Any:
        """Encode non-standard types."""
        if is_dataclass(obj) and not isinstance(obj, type):
            return self._encode_value(obj)
        if isinstance(obj, Enum):
            return {"_enum": obj.__class__.__name__, "_value": obj.value}
        if isinstance(obj, Decimal):
            return {"_decimal": str(obj)}
        if isinstance(obj, datetime):
            return {"_datetime": obj.isoformat()}
        if isinstance(obj, date):
            return {"_date": obj.isoformat()}
        if isinstance(obj, Path):
            return {"_path": str(obj)}
        return super().default(obj)


class SpreadsheetDecoder:
    """Decoder for spreadsheet data structures.

    JSON/YAML deserialization support.

    Reconstructs dataclass instances and special types from
    serialized dictionaries.
    """

    # Type registry for reconstruction
    TYPE_REGISTRY: ClassVar[dict[str, type]] = {
        "SheetSpec": SheetSpec,
        "RowSpec": RowSpec,
        "CellSpec": CellSpec,
        "ColumnSpec": ColumnSpec,
        "NamedRange": NamedRange,
        "RangeRef": RangeRef,
        "ChartSpec": ChartSpec,
        "ChartTitle": ChartTitle,
        "DataSeries": DataSeries,
        "AxisConfig": AxisConfig,
        "LegendConfig": LegendConfig,
        "DataLabelConfig": DataLabelConfig,
        "ChartPosition": ChartPosition,
        "ChartSize": ChartSize,
    }

    ENUM_REGISTRY: ClassVar[dict[str, type]] = {
        "ChartType": ChartType,
        "LegendPosition": LegendPosition,
    }

    @classmethod
    def decode(cls, data: Any) -> Any:
        """Decode a value back to proper types.

        Args:
            data: Value to decode (dict, list, or primitive)

        Returns:
            Reconstructed object
        """
        # Handle lists recursively
        if isinstance(data, list):
            return [cls.decode(item) for item in data]

        # Handle non-dict types
        if not isinstance(data, dict):
            return data

        # Make a copy to avoid mutating the original
        data = dict(data)

        # Handle typed objects
        if "_type" in data:
            type_name = data.pop("_type")
            type_cls = cls.TYPE_REGISTRY.get(type_name)
            if type_cls:
                # Recursively decode nested values
                decoded = {k: cls.decode(v) for k, v in data.items()}
                return type_cls(**decoded)
            # Unknown type, return as dict without _type
            return data

        # Handle enums
        if "_enum" in data:
            enum_name = data["_enum"]
            enum_value = data["_value"]
            enum_cls = cls.ENUM_REGISTRY.get(enum_name)
            if enum_cls:
                return enum_cls(enum_value)
            return enum_value

        # Handle special types
        if "_decimal" in data:
            return Decimal(data["_decimal"])
        if "_datetime" in data:
            return datetime.fromisoformat(data["_datetime"])
        if "_date" in data:
            return date.fromisoformat(data["_date"])
        if "_path" in data:
            return Path(data["_path"])

        # Recursively decode nested dicts
        return {k: cls.decode(v) for k, v in data.items()}

    @classmethod
    def decode_list(cls, data: list[Any]) -> list[Any]:
        """Decode a list of items."""
        return [cls.decode(item) for item in data]


class Serializer:
    """Main serialization interface for spreadsheet definitions.

    Round-trip serialization with full fidelity preservation.

    Provides save/load operations in JSON and YAML formats with
    full fidelity preservation of all data types and structures.

    Examples:
        # Save to JSON
        serializer = Serializer()
        serializer.save_json(sheets, "spreadsheet.json")

        # Load from JSON
        sheets = serializer.load_json("spreadsheet.json")

        # Save to YAML (more readable)
        serializer.save_yaml(sheets, "spreadsheet.yaml")

        # Load from YAML
        sheets = serializer.load_yaml("spreadsheet.yaml")
    """

    def __init__(self) -> None:
        """Initialize serializer."""
        self._encoder = SpreadsheetEncoder
        self._decoder = SpreadsheetDecoder()

    # =========================================================================
    # JSON Serialization
    # =========================================================================

    def to_json(
        self,
        data: Any,
        indent: int = 2,
    ) -> str:
        """Serialize data to JSON string.

        Args:
            data: Data to serialize (sheets, charts, etc.)
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        return json.dumps(data, cls=self._encoder, indent=indent)

    def from_json(self, json_str: str) -> Any:
        """Deserialize from JSON string.

        Args:
            json_str: JSON string

        Returns:
            Reconstructed data structures
        """
        data = json.loads(json_str)
        if isinstance(data, list):
            return SpreadsheetDecoder.decode_list(data)
        if isinstance(data, dict):
            return SpreadsheetDecoder.decode(data)
        return data

    def save_json(
        self,
        data: Any,
        file_path: Path | str,
        indent: int = 2,
    ) -> Path:
        """Save data to JSON file.

        Args:
            data: Data to serialize
            file_path: Output file path
            indent: JSON indentation level

        Returns:
            Path to created file
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, cls=self._encoder, indent=indent)

        return path

    def load_json(self, file_path: Path | str) -> Any:
        """Load data from JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Reconstructed data structures
        """
        path = Path(file_path)
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return SpreadsheetDecoder.decode_list(data)
        if isinstance(data, dict):
            return SpreadsheetDecoder.decode(data)
        return data

    # =========================================================================
    # YAML Serialization
    # =========================================================================

    def to_yaml(self, data: Any) -> str:
        """Serialize data to YAML string.

        Args:
            data: Data to serialize

        Returns:
            YAML string representation
        """
        # First convert to JSON-serializable dict
        json_str = self.to_json(data)
        json_data = json.loads(json_str)

        return yaml.dump(json_data, default_flow_style=False, sort_keys=False)

    def from_yaml(self, yaml_str: str) -> Any:
        """Deserialize from YAML string.

        Args:
            yaml_str: YAML string

        Returns:
            Reconstructed data structures
        """
        data = yaml.safe_load(yaml_str)
        if isinstance(data, list):
            return SpreadsheetDecoder.decode_list(data)
        if isinstance(data, dict):
            return SpreadsheetDecoder.decode(data)
        return data

    def save_yaml(
        self,
        data: Any,
        file_path: Path | str,
    ) -> Path:
        """Save data to YAML file.

        Args:
            data: Data to serialize
            file_path: Output file path

        Returns:
            Path to created file
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        yaml_content = self.to_yaml(data)
        path.write_text(yaml_content, encoding="utf-8")

        return path

    def load_yaml(self, file_path: Path | str) -> Any:
        """Load data from YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            Reconstructed data structures
        """
        path = Path(file_path)
        yaml_content = path.read_text(encoding="utf-8")
        return self.from_yaml(yaml_content)


class DefinitionFormat:
    """High-level spreadsheet definition format.

    Complete spreadsheet definition serialization.

    Provides a structured format for saving/loading complete spreadsheet
    definitions including sheets, charts, named ranges, and metadata.

    Format Structure:
        {
            "version": "4.0",
            "metadata": {...},
            "sheets": [...],
            "charts": [...],
            "named_ranges": [...],
            "conditional_formats": [...],
            "validations": [...]
        }
    """

    VERSION = "4.0"

    @classmethod
    def create(
        cls,
        sheets: list[SheetSpec],
        charts: list[ChartSpec] | None = None,
        named_ranges: list[NamedRange] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a complete definition document.

        Args:
            sheets: Sheet specifications
            charts: Optional charts
            named_ranges: Optional named ranges
            metadata: Optional document metadata

        Returns:
            Complete definition dictionary
        """
        return {
            "version": cls.VERSION,
            "metadata": metadata or {},
            "sheets": sheets,
            "charts": charts or [],
            "named_ranges": named_ranges or [],
        }

    @classmethod
    def save(
        cls,
        file_path: Path | str,
        sheets: list[SheetSpec],
        charts: list[ChartSpec] | None = None,
        named_ranges: list[NamedRange] | None = None,
        metadata: dict[str, Any] | None = None,
        format: str = "yaml",
    ) -> Path:
        """Save a complete spreadsheet definition.

        Args:
            file_path: Output file path
            sheets: Sheet specifications
            charts: Optional charts
            named_ranges: Optional named ranges
            metadata: Optional document metadata
            format: Output format ("yaml" or "json")

        Returns:
            Path to created file
        """
        definition = cls.create(sheets, charts, named_ranges, metadata)
        serializer = Serializer()

        if format == "json":
            return serializer.save_json(definition, file_path)
        return serializer.save_yaml(definition, file_path)

    @classmethod
    def load(cls, file_path: Path | str) -> Any:
        """Load a complete spreadsheet definition.

        Args:
            file_path: Path to definition file

        Returns:
            Definition dictionary with reconstructed objects
        """
        path = Path(file_path)
        serializer = Serializer()

        if path.suffix == ".json":
            return serializer.load_json(path)
        return serializer.load_yaml(path)


# Convenience functions


def save_definition(
    file_path: Path | str,
    sheets: list[SheetSpec],
    **kwargs: Any,
) -> Path:
    """Save spreadsheet definition to file.

    Convenience function for DefinitionFormat.save().

    Args:
        file_path: Output file path
        sheets: Sheet specifications
        **kwargs: Additional arguments (charts, named_ranges, metadata, format)

    Returns:
        Path to created file
    """
    return DefinitionFormat.save(file_path, sheets, **kwargs)


def load_definition(file_path: Path | str) -> Any:
    """Load spreadsheet definition from file.

    Convenience function for DefinitionFormat.load().

    Args:
        file_path: Path to definition file

    Returns:
        Definition dictionary with reconstructed objects
    """
    return DefinitionFormat.load(file_path)
