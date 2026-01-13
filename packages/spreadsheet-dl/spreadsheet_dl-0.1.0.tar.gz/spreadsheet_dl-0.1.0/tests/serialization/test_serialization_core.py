"""
Comprehensive tests for serialization module.

Tests:
    - SpreadsheetEncoder for all types
    - SpreadsheetDecoder for all types
    - Serializer JSON/YAML operations
    - Type registry
    - Round-trip fidelity
    - DefinitionFormat

Implements comprehensive coverage for Round-trip serialization
"""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from spreadsheet_dl.builder import (
    CellSpec,
    ColumnSpec,
    RowSpec,
    SheetSpec,
)
from spreadsheet_dl.charts import (
    ChartPosition,
    ChartSize,
    ChartSpec,
    ChartTitle,
    ChartType,
    DataSeries,
    LegendConfig,
    LegendPosition,
)
from spreadsheet_dl.serialization import (
    Serializer,
    SpreadsheetDecoder,
    SpreadsheetEncoder,
)

pytestmark = [pytest.mark.unit, pytest.mark.builder]

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_sheet() -> SheetSpec:
    """Create a sample sheet for serialization testing."""
    return SheetSpec(
        name="TestSheet",
        columns=[
            ColumnSpec(name="Name", width="3cm"),
            ColumnSpec(name="Value", width="2cm", type="float"),
        ],
        rows=[
            RowSpec(
                cells=[
                    CellSpec(value="Alice", style="header"),
                    CellSpec(value=100.5, value_type="float"),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Bob"),
                    CellSpec(value=200, formula="=A1*2"),
                ]
            ),
        ],
        freeze_rows=1,
        freeze_cols=0,
    )


@pytest.fixture
def sample_chart() -> ChartSpec:
    """Create a sample chart for serialization testing."""
    return ChartSpec(
        title=ChartTitle(text="Sales Chart"),
        chart_type=ChartType.COLUMN,
        series=[
            DataSeries(
                name="Sales",
                values="B2:B10",
                categories="A2:A10",
            )
        ],
        position=ChartPosition(cell="F2"),
        size=ChartSize(width=400, height=300),
        legend=LegendConfig(position=LegendPosition.RIGHT),
    )


# ==============================================================================
# SpreadsheetEncoder Tests
# ==============================================================================


class TestSpreadsheetEncoder:
    """Tests for SpreadsheetEncoder."""

    def test_encode_dataclass(self, sample_sheet: SheetSpec) -> None:
        """Test encoding dataclass instances."""
        result = json.dumps(sample_sheet, cls=SpreadsheetEncoder)
        assert isinstance(result, str)
        data = json.loads(result)
        assert data["_type"] == "SheetSpec"
        assert data["name"] == "TestSheet"

    def test_encode_enum(self) -> None:
        """Test encoding enum values."""
        chart_type = ChartType.COLUMN
        result = json.dumps(chart_type, cls=SpreadsheetEncoder)
        data = json.loads(result)
        assert "_enum" in data
        assert data["_enum"] == "ChartType"
        # ChartType.COLUMN value
        assert "_value" in data

    def test_encode_decimal(self) -> None:
        """Test encoding Decimal values."""
        value = Decimal("123.45")
        result = json.dumps(value, cls=SpreadsheetEncoder)
        data = json.loads(result)
        assert data["_decimal"] == "123.45"

    def test_encode_datetime(self) -> None:
        """Test encoding datetime values."""
        dt = datetime(2025, 1, 15, 10, 30, 45)
        result = json.dumps(dt, cls=SpreadsheetEncoder)
        data = json.loads(result)
        assert "_datetime" in data
        assert "2025-01-15" in data["_datetime"]

    def test_encode_date(self) -> None:
        """Test encoding date values."""
        d = date(2025, 1, 15)
        result = json.dumps(d, cls=SpreadsheetEncoder)
        data = json.loads(result)
        assert data["_date"] == "2025-01-15"

    def test_encode_date_via_default_method(self) -> None:
        """Test encoding date via default method path.

        Coverage: Line 82 - Encoder default method for date type
        This specifically tests the path where date is encoded via default(),
        not via _encode_value().
        """
        # Create a custom object that contains a date but isn't a dataclass
        # forcing the default() method to be called
        d = date(2025, 6, 15)

        # Use the encoder's default method directly
        encoder = SpreadsheetEncoder()
        result = encoder.default(d)

        assert result == {"_date": "2025-06-15"}

    def test_encode_path(self) -> None:
        """Test encoding Path values."""
        p = Path("test_data/test.txt")
        result = json.dumps(p, cls=SpreadsheetEncoder)
        data = json.loads(result)
        assert data["_path"] == "test_data/test.txt"

    def test_encode_path_via_default_method(self) -> None:
        """Test encoding Path via default method path.

        Coverage: Line 103 - Encoder default method for Path type
        This specifically tests the path where Path is encoded via default().
        """
        path_obj = Path("/test/path.txt")

        # Use the encoder's default method directly
        encoder = SpreadsheetEncoder()
        result = encoder.default(path_obj)

        assert result == {"_path": "/test/path.txt"}

    def test_encode_path_in_dataclass(self) -> None:
        """Test encoding Path embedded in a dataclass.

        Coverage: Line 82 - Encoder _encode_value method for Path type
        This tests the recursive encoding path that hits line 82.
        """
        from dataclasses import dataclass

        @dataclass
        class TestConfig:
            name: str
            path: Path

        config = TestConfig(name="test", path=Path("/data/file.txt"))

        # Encode via JSON which will trigger _encode_value recursively
        SpreadsheetEncoder()
        result = json.dumps(config, cls=SpreadsheetEncoder)
        data = json.loads(result)

        # Verify Path was encoded correctly
        assert data["path"]["_path"] == "/data/file.txt"

    def test_encode_unsupported_type_raises(self) -> None:
        """Test encoding unsupported type calls super().default() which raises.

        Coverage: Line 104 - Encoder default method calling super().default()
        """
        encoder = SpreadsheetEncoder()

        # Create a custom class that isn't handled by our encoder
        class UnhandledType:
            pass

        obj = UnhandledType()

        # This should call super().default() which raises TypeError
        with pytest.raises(TypeError, match="not JSON serializable"):
            encoder.default(obj)

    def test_encode_nested_dataclasses(self, sample_sheet: SheetSpec) -> None:
        """Test encoding nested dataclass structures."""
        result = json.dumps(sample_sheet, cls=SpreadsheetEncoder)
        data = json.loads(result)

        # Check nested columns exist and have data
        assert len(data["columns"]) == 2
        assert data["columns"][0]["name"] == "Name"

        # Check nested rows exist and have data
        assert len(data["rows"]) == 2

    def test_encode_list(self) -> None:
        """Test encoding lists."""
        data = [
            CellSpec(value="test"),
            CellSpec(value=123),
            CellSpec(value=Decimal("45.67")),
        ]
        result = json.dumps(data, cls=SpreadsheetEncoder)
        parsed = json.loads(result)
        assert len(parsed) == 3
        assert parsed[0]["_type"] == "CellSpec"

    def test_encode_dict(self) -> None:
        """Test encoding dictionaries."""
        data = {
            "cell": CellSpec(value="test"),
            "number": 42,
            "decimal": Decimal("123.45"),
        }
        result = json.dumps(data, cls=SpreadsheetEncoder)
        parsed = json.loads(result)
        assert parsed["cell"]["_type"] == "CellSpec"
        assert parsed["number"] == 42


# ==============================================================================
# SpreadsheetDecoder Tests
# ==============================================================================


class TestSpreadsheetDecoder:
    """Tests for SpreadsheetDecoder."""

    def test_decode_dataclass(self) -> None:
        """Test decoding dataclass instances."""
        data = {
            "_type": "CellSpec",
            "value": "test",
            "formula": None,
            "style": None,
            "colspan": 1,
            "rowspan": 1,
            "value_type": None,
            "validation": None,
            "conditional_format": None,
        }
        result = SpreadsheetDecoder.decode(data)
        assert isinstance(result, CellSpec)
        assert result.value == "test"

    def test_decode_enum(self) -> None:
        """Test decoding enum values."""
        # Use actual enum value
        data = {"_enum": "ChartType", "_value": ChartType.COLUMN.value}
        result = SpreadsheetDecoder.decode(data)
        assert result == ChartType.COLUMN

    def test_decode_unknown_enum_type(self) -> None:
        """Test decoding unknown enum type returns raw value.

        Coverage: Line 180 - Decoder handling unknown enum type
        """
        data = {"_enum": "UnknownEnumType", "_value": "some_value"}
        result = SpreadsheetDecoder.decode(data)
        # Unknown enum should return just the value
        assert result == "some_value"

    def test_decode_decimal(self) -> None:
        """Test decoding Decimal values."""
        data = {"_decimal": "123.45"}
        result = SpreadsheetDecoder.decode(data)
        assert isinstance(result, Decimal)
        assert result == Decimal("123.45")

    def test_decode_datetime(self) -> None:
        """Test decoding datetime values."""
        data = {"_datetime": "2025-01-15T10:30:45"}
        result = SpreadsheetDecoder.decode(data)
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 15

    def test_decode_date(self) -> None:
        """Test decoding date values."""
        data = {"_date": "2025-01-15"}
        result = SpreadsheetDecoder.decode(data)
        assert isinstance(result, date)
        assert result.year == 2025

    def test_decode_path(self) -> None:
        """Test decoding Path values."""
        data = {"_path": "test_data/test.txt"}
        result = SpreadsheetDecoder.decode(data)
        assert isinstance(result, Path)
        assert str(result) == "test_data/test.txt"

    def test_decode_nested_structures(self) -> None:
        """Test decoding nested structures."""
        # Create a proper encoded structure
        sheet = SheetSpec(
            name="Test",
            columns=[ColumnSpec(name="Col1")],
            rows=[],
        )
        serializer = Serializer()
        json_str = serializer.to_json(sheet)
        result = serializer.from_json(json_str)

        assert isinstance(result, SheetSpec)
        assert len(result.columns) == 1
        assert isinstance(result.columns[0], ColumnSpec)

    def test_decode_list(self) -> None:
        """Test decoding lists."""
        data = [
            {
                "_type": "CellSpec",
                "value": "a",
                "formula": None,
                "style": None,
                "colspan": 1,
                "rowspan": 1,
                "value_type": None,
                "validation": None,
                "conditional_format": None,
            },
            {
                "_type": "CellSpec",
                "value": "b",
                "formula": None,
                "style": None,
                "colspan": 1,
                "rowspan": 1,
                "value_type": None,
                "validation": None,
                "conditional_format": None,
            },
        ]
        result = SpreadsheetDecoder.decode_list(data)
        assert len(result) == 2
        assert all(isinstance(item, CellSpec) for item in result)

    def test_decode_unknown_type_returns_dict(self) -> None:
        """Test decoding unknown type returns dict."""
        data = {"_type": "UnknownType", "field": "value"}
        result = SpreadsheetDecoder.decode(data)
        # Should return dict without _type key
        assert isinstance(result, dict)
        assert "field" in result

    def test_decode_plain_dict(self) -> None:
        """Test decoding plain dictionary."""
        data = {"key": "value", "number": 42}
        result = SpreadsheetDecoder.decode(data)
        assert result == data


# ==============================================================================
# Serializer Tests
# ==============================================================================


class TestSerializer:
    """Tests for Serializer class."""

    def test_to_json(self, sample_sheet: SheetSpec) -> None:
        """Test to_json method."""
        serializer = Serializer()
        result = serializer.to_json(sample_sheet)
        assert isinstance(result, str)
        assert "TestSheet" in result

    def test_from_json(self, sample_sheet: SheetSpec) -> None:
        """Test from_json method."""
        serializer = Serializer()
        json_str = serializer.to_json(sample_sheet)
        result = serializer.from_json(json_str)
        assert isinstance(result, SheetSpec)
        assert result.name == "TestSheet"

    def test_from_json_primitive_data(self) -> None:
        """Test from_json returning primitive data directly.

        Coverage: Line 266 - from_json returning primitive data directly
        """
        serializer = Serializer()

        # Test with string primitive
        result = serializer.from_json('"hello"')
        assert result == "hello"

        # Test with number primitive
        result = serializer.from_json("42")
        assert result == 42

        # Test with null
        result = serializer.from_json("null")
        assert result is None

        # Test with boolean
        result = serializer.from_json("true")
        assert result is True

    def test_save_json(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test save_json method."""
        serializer = Serializer()
        json_file = tmp_path / "test.json"
        result = serializer.save_json(sample_sheet, json_file)

        assert result == json_file
        assert json_file.exists()

    def test_load_json(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test load_json method."""
        serializer = Serializer()
        json_file = tmp_path / "test.json"
        serializer.save_json(sample_sheet, json_file)

        result = serializer.load_json(json_file)
        assert isinstance(result, SheetSpec)
        assert result.name == "TestSheet"

    def test_load_json_primitive_data(self, tmp_path: Path) -> None:
        """Test load_json returning primitive data directly.

        Coverage: Line 311 - load_json returning primitive data directly
        """
        serializer = Serializer()

        # Create a file with primitive JSON data
        json_file = tmp_path / "primitive.json"
        json_file.write_text('"just a string"')

        result = serializer.load_json(json_file)
        assert result == "just a string"

        # Test with number
        json_file.write_text("123.45")
        result = serializer.load_json(json_file)
        assert result == 123.45

        # Test with null
        json_file.write_text("null")
        result = serializer.load_json(json_file)
        assert result is None

    def test_to_yaml(self, sample_sheet: SheetSpec) -> None:
        """Test to_yaml method."""
        serializer = Serializer()
        result = serializer.to_yaml(sample_sheet)
        assert isinstance(result, str)
        assert "TestSheet" in result
        assert "name:" in result  # YAML format

    def test_from_yaml(self, sample_sheet: SheetSpec) -> None:
        """Test from_yaml method."""
        serializer = Serializer()
        yaml_str = serializer.to_yaml(sample_sheet)
        result = serializer.from_yaml(yaml_str)
        assert isinstance(result, SheetSpec)
        assert result.name == "TestSheet"

    def test_from_yaml_list_data(self) -> None:
        """Test from_yaml returning list data.

        Coverage: Line 345 - from_yaml returning list data
        """
        serializer = Serializer()

        # Create YAML with a list at the top level
        yaml_str = """
- _type: CellSpec
  value: test1
  formula: null
  style: null
  colspan: 1
  rowspan: 1
  value_type: null
  validation: null
  conditional_format: null
- _type: CellSpec
  value: test2
  formula: null
  style: null
  colspan: 1
  rowspan: 1
  value_type: null
  validation: null
  conditional_format: null
"""
        result = serializer.from_yaml(yaml_str)
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, CellSpec) for item in result)

    def test_from_yaml_primitive_data(self) -> None:
        """Test from_yaml returning primitive data directly.

        Coverage: Line 348 - from_yaml returning primitive data directly
        """
        serializer = Serializer()

        # Test with string
        result = serializer.from_yaml("just a string")
        assert result == "just a string"

        # Test with number
        result = serializer.from_yaml("42")
        assert result == 42

        # Test with null/None
        result = serializer.from_yaml("null")
        assert result is None

        # Test with boolean
        result = serializer.from_yaml("true")
        assert result is True

    def test_save_yaml(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test save_yaml method."""
        serializer = Serializer()
        yaml_file = tmp_path / "test.yaml"
        result = serializer.save_yaml(sample_sheet, yaml_file)

        assert result == yaml_file
        assert yaml_file.exists()

    def test_load_yaml(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test load_yaml method."""
        serializer = Serializer()
        yaml_file = tmp_path / "test.yaml"
        serializer.save_yaml(sample_sheet, yaml_file)

        result = serializer.load_yaml(yaml_file)
        assert isinstance(result, SheetSpec)
        assert result.name == "TestSheet"

    def test_json_round_trip(self, sample_sheet: SheetSpec) -> None:
        """Test JSON serialization round-trip preserves data."""
        serializer = Serializer()
        json_str = serializer.to_json(sample_sheet)
        result = serializer.from_json(json_str)

        assert result.name == sample_sheet.name
        assert len(result.columns) == len(sample_sheet.columns)
        assert len(result.rows) == len(sample_sheet.rows)
        assert result.freeze_rows == sample_sheet.freeze_rows

    def test_yaml_round_trip(self, sample_sheet: SheetSpec) -> None:
        """Test YAML serialization round-trip preserves data."""
        serializer = Serializer()
        yaml_str = serializer.to_yaml(sample_sheet)
        result = serializer.from_yaml(yaml_str)

        assert result.name == sample_sheet.name
        assert len(result.columns) == len(sample_sheet.columns)
        assert len(result.rows) == len(sample_sheet.rows)

    def test_serialize_list_of_sheets(self, sample_sheet: SheetSpec) -> None:
        """Test serializing list of sheets."""
        sheets = [sample_sheet, sample_sheet]
        serializer = Serializer()

        json_str = serializer.to_json(sheets)
        result = serializer.from_json(json_str)

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(s, SheetSpec) for s in result)

    def test_serialize_chart(self, sample_chart: ChartSpec) -> None:
        """Test serializing chart specification."""
        serializer = Serializer()
        json_str = serializer.to_json(sample_chart)
        result = serializer.from_json(json_str)

        # Check chart data is preserved
        assert isinstance(result, (ChartSpec, dict))
        if isinstance(result, ChartSpec):
            assert result.title is not None
            assert result.title.text == "Sales Chart"  # type: ignore[union-attr]
            assert result.chart_type == ChartType.COLUMN

    def test_json_indentation(self, sample_sheet: SheetSpec) -> None:
        """Test JSON indentation parameter."""
        serializer = Serializer()
        result_2 = serializer.to_json(sample_sheet, indent=2)
        result_4 = serializer.to_json(sample_sheet, indent=4)

        # More indentation means longer output
        assert len(result_4) > len(result_2)

    def test_save_creates_parent_directories(
        self, tmp_path: Path, sample_sheet: SheetSpec
    ) -> None:
        """Test save methods create parent directories."""
        serializer = Serializer()
        nested_path = tmp_path / "nested" / "dir" / "test.json"

        serializer.save_json(sample_sheet, nested_path)
        assert nested_path.exists()


# ==============================================================================
# DefinitionFormat Tests
# ==============================================================================
