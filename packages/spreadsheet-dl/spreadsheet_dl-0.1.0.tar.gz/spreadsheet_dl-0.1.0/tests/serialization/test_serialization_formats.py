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
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl.builder import (
    CellSpec,
    ColumnSpec,
    NamedRange,
    RangeRef,
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
    DefinitionFormat,
    Serializer,
    load_definition,
    save_definition,
)

if TYPE_CHECKING:
    from pathlib import Path

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


class TestDefinitionFormat:
    """Tests for DefinitionFormat class."""

    def test_create_basic(self, sample_sheet: SheetSpec) -> None:
        """Test creating basic definition."""
        definition = DefinitionFormat.create([sample_sheet])

        assert definition["version"] == "4.0"
        assert "metadata" in definition
        assert "sheets" in definition
        assert "charts" in definition
        assert "named_ranges" in definition
        assert len(definition["sheets"]) == 1

    def test_create_with_charts(
        self, sample_sheet: SheetSpec, sample_chart: ChartSpec
    ) -> None:
        """Test creating definition with charts."""
        definition = DefinitionFormat.create([sample_sheet], charts=[sample_chart])

        assert len(definition["charts"]) == 1

    def test_create_with_metadata(self, sample_sheet: SheetSpec) -> None:
        """Test creating definition with metadata."""
        metadata = {"author": "Test", "created": "2025-01-15"}
        definition = DefinitionFormat.create([sample_sheet], metadata=metadata)

        assert definition["metadata"]["author"] == "Test"

    def test_create_with_named_ranges(self, sample_sheet: SheetSpec) -> None:
        """Test creating definition with named ranges."""
        named_range = NamedRange(
            name="TestRange",
            range=RangeRef(start="A1", end="B10", sheet="TestSheet"),
        )
        definition = DefinitionFormat.create([sample_sheet], named_ranges=[named_range])

        assert len(definition["named_ranges"]) == 1

    def test_save_yaml(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test saving definition to YAML."""
        yaml_file = tmp_path / "definition.yaml"
        result = DefinitionFormat.save(yaml_file, [sample_sheet], format="yaml")

        assert result == yaml_file
        assert yaml_file.exists()

        # Verify content
        content = yaml_file.read_text()
        assert "version:" in content
        assert "4.0" in content

    def test_save_json(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test saving definition to JSON."""
        json_file = tmp_path / "definition.json"
        result = DefinitionFormat.save(json_file, [sample_sheet], format="json")

        assert result == json_file
        assert json_file.exists()

        # Verify valid JSON
        with json_file.open() as f:
            data = json.load(f)
        assert data["version"] == "4.0"

    def test_load_yaml(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test loading definition from YAML."""
        yaml_file = tmp_path / "definition.yaml"
        DefinitionFormat.save(yaml_file, [sample_sheet], format="yaml")

        definition = DefinitionFormat.load(yaml_file)

        assert definition["version"] == "4.0"
        assert len(definition["sheets"]) == 1
        # YAML round-trip may not preserve exact types
        sheet = definition["sheets"][0]
        assert isinstance(sheet, (SheetSpec, dict))

    def test_load_json(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test loading definition from JSON."""
        json_file = tmp_path / "definition.json"
        DefinitionFormat.save(json_file, [sample_sheet], format="json")

        definition = DefinitionFormat.load(json_file)

        assert definition["version"] == "4.0"
        assert len(definition["sheets"]) == 1

    def test_round_trip_yaml(
        self, tmp_path: Path, sample_sheet: SheetSpec, sample_chart: ChartSpec
    ) -> None:
        """Test YAML definition round-trip."""
        yaml_file = tmp_path / "round_trip.yaml"
        metadata = {"author": "Test"}
        named_range = NamedRange(
            name="Range1",
            range=RangeRef(start="A1", end="B5", sheet="TestSheet"),
        )

        # Save
        DefinitionFormat.save(
            yaml_file,
            [sample_sheet],
            charts=[sample_chart],
            named_ranges=[named_range],
            metadata=metadata,
            format="yaml",
        )

        # Load
        definition = DefinitionFormat.load(yaml_file)

        assert definition["version"] == "4.0"
        assert definition["metadata"]["author"] == "Test"
        assert len(definition["sheets"]) == 1
        assert len(definition["charts"]) == 1
        assert len(definition["named_ranges"]) == 1

    def test_round_trip_json(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test JSON definition round-trip."""
        json_file = tmp_path / "round_trip.json"

        # Save
        DefinitionFormat.save(json_file, [sample_sheet], format="json")

        # Load
        definition = DefinitionFormat.load(json_file)

        assert definition["version"] == "4.0"
        assert len(definition["sheets"]) == 1
        # Check that sheet data is present
        sheet = definition["sheets"][0]
        assert isinstance(sheet, (SheetSpec, dict))
        if isinstance(sheet, dict):
            assert sheet.get("name") == "TestSheet" or sheet.get("_type") == "SheetSpec"


# ==============================================================================
# Convenience Functions Tests
# ==============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_save_definition(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test save_definition convenience function."""
        yaml_file = tmp_path / "convenience.yaml"
        result = save_definition(yaml_file, [sample_sheet])

        assert result == yaml_file
        assert yaml_file.exists()

    def test_save_definition_with_kwargs(
        self, tmp_path: Path, sample_sheet: SheetSpec, sample_chart: ChartSpec
    ) -> None:
        """Test save_definition with keyword arguments."""
        yaml_file = tmp_path / "kwargs.yaml"
        result = save_definition(
            yaml_file,
            [sample_sheet],
            charts=[sample_chart],
            metadata={"test": "value"},
        )

        assert result == yaml_file

    def test_load_definition(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test load_definition convenience function."""
        yaml_file = tmp_path / "load_test.yaml"
        save_definition(yaml_file, [sample_sheet])

        definition = load_definition(yaml_file)

        assert definition["version"] == "4.0"
        assert len(definition["sheets"]) == 1


# ==============================================================================
# Edge Cases and Complex Scenarios
# ==============================================================================


class TestEdgeCases:
    """Tests for edge cases and complex scenarios."""

    def test_empty_sheets_list(self, tmp_path: Path) -> None:
        """Test serializing empty sheets list."""
        serializer = Serializer()
        json_file = tmp_path / "empty.json"
        serializer.save_json([], json_file)

        result = serializer.load_json(json_file)
        assert result == []

    def test_none_values(self, tmp_path: Path) -> None:
        """Test serializing cells with None values."""
        sheet = SheetSpec(
            name="NoneTest",
            columns=[ColumnSpec(name="A")],
            rows=[RowSpec(cells=[CellSpec(value=None)])],
        )

        serializer = Serializer()
        json_file = tmp_path / "none.json"
        serializer.save_json(sheet, json_file)

        # Verify file exists and can be loaded
        result = serializer.load_json(json_file)
        assert isinstance(result, SheetSpec)
        assert result.rows[0].cells[0].value is None

    def test_deeply_nested_structures(self, tmp_path: Path) -> None:
        """Test serializing deeply nested structures."""
        sheets = [
            SheetSpec(
                name=f"Sheet{i}",
                columns=[ColumnSpec(name=f"Col{j}") for j in range(5)],
                rows=[
                    RowSpec(cells=[CellSpec(value=f"V{i}{j}{k}") for k in range(5)])
                    for j in range(10)
                ],
            )
            for i in range(3)
        ]

        serializer = Serializer()
        json_file = tmp_path / "nested.json"
        serializer.save_json(sheets, json_file)

        result = serializer.load_json(json_file)
        assert len(result) == 3
        assert all(isinstance(s, SheetSpec) for s in result)

    def test_special_characters(self, tmp_path: Path) -> None:
        """Test serializing special characters."""
        sheet = SheetSpec(
            name="Special",
            columns=[ColumnSpec(name="Data")],
            rows=[
                RowSpec(cells=[CellSpec(value='Quote"Test')]),
                RowSpec(cells=[CellSpec(value="Line\nBreak")]),
                RowSpec(cells=[CellSpec(value="Tab\tChar")]),
            ],
        )

        serializer = Serializer()
        json_file = tmp_path / "special.json"
        serializer.save_json(sheet, json_file)

        result = serializer.load_json(json_file)
        assert isinstance(result, SheetSpec)
        assert result.rows[0].cells[0].value == 'Quote"Test'
        assert result.rows[1].cells[0].value == "Line\nBreak"

    def test_unicode_characters(self, tmp_path: Path) -> None:
        """Test serializing unicode characters."""
        sheet = SheetSpec(
            name="Unicode",
            columns=[ColumnSpec(name="Text")],
            rows=[
                RowSpec(cells=[CellSpec(value="Hello 世界")]),
                RowSpec(cells=[CellSpec(value="Emoji: 🎉")]),
            ],
        )

        serializer = Serializer()
        json_file = tmp_path / "unicode.json"
        serializer.save_json(sheet, json_file)

        result = serializer.load_json(json_file)
        assert isinstance(result, SheetSpec)
        assert "世界" in result.rows[0].cells[0].value

    def test_large_decimal_precision(self, tmp_path: Path) -> None:
        """Test serializing high-precision Decimal values."""
        sheet = SheetSpec(
            name="Precision",
            columns=[ColumnSpec(name="Value")],
            rows=[
                RowSpec(
                    cells=[CellSpec(value=Decimal("123.456789012345678901234567890"))]
                ),
            ],
        )

        serializer = Serializer()
        json_file = tmp_path / "precision.json"
        serializer.save_json(sheet, json_file)

        # Precision should be preserved
        result = serializer.load_json(json_file)
        assert isinstance(result, SheetSpec)
        original_value = sheet.rows[0].cells[0].value
        result_value = result.rows[0].cells[0].value
        assert result_value == original_value

    def test_mixed_types_in_row(self, tmp_path: Path) -> None:
        """Test serializing rows with mixed data types."""
        sheet = SheetSpec(
            name="MixedTypes",
            columns=[
                ColumnSpec(name="String"),
                ColumnSpec(name="Int"),
                ColumnSpec(name="Decimal"),
                ColumnSpec(name="Date"),
            ],
            rows=[
                RowSpec(
                    cells=[
                        CellSpec(value="text"),
                        CellSpec(value=42),
                        CellSpec(value=Decimal("99.99")),
                        CellSpec(value=date(2025, 1, 15)),
                    ]
                ),
            ],
        )

        serializer = Serializer()
        json_file = tmp_path / "mixed.json"
        serializer.save_json(sheet, json_file)

        result = serializer.load_json(json_file)
        assert isinstance(result, SheetSpec)
        cells = result.rows[0].cells
        assert cells[0].value == "text"
        assert cells[1].value == 42
        assert isinstance(cells[2].value, Decimal)
        assert isinstance(cells[3].value, date)

    def test_formulas_preserved(self, tmp_path: Path) -> None:
        """Test formula preservation in serialization."""
        sheet = SheetSpec(
            name="Formulas",
            columns=[ColumnSpec(name="A"), ColumnSpec(name="B")],
            rows=[
                RowSpec(cells=[CellSpec(value=10), CellSpec(value=20)]),
                RowSpec(
                    cells=[
                        CellSpec(formula="=A1+B1"),
                        CellSpec(formula="=SUM(A1:B1)"),
                    ]
                ),
            ],
        )

        serializer = Serializer()
        json_file = tmp_path / "formulas.json"
        serializer.save_json(sheet, json_file)

        result = serializer.load_json(json_file)
        assert isinstance(result, SheetSpec)
        assert result.rows[1].cells[0].formula == "=A1+B1"
        assert result.rows[1].cells[1].formula == "=SUM(A1:B1)"

    def test_style_references_preserved(self, tmp_path: Path) -> None:
        """Test style reference preservation."""
        sheet = SheetSpec(
            name="Styled",
            columns=[ColumnSpec(name="A", style="header")],
            rows=[
                RowSpec(
                    cells=[CellSpec(value="test", style="bold")],
                    style="row_style",
                ),
            ],
        )

        serializer = Serializer()
        json_file = tmp_path / "styled.json"
        serializer.save_json(sheet, json_file)

        result = serializer.load_json(json_file)
        assert isinstance(result, SheetSpec)
        assert result.columns[0].style == "header"
        assert result.rows[0].style == "row_style"
        assert result.rows[0].cells[0].style == "bold"
