"""Fixtures for XLSX renderer tests."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl.builder import CellSpec, ColumnSpec, RowSpec, SheetSpec

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def sample_sheet() -> SheetSpec:
    """Create a sample sheet for testing."""
    return SheetSpec(
        name="TestSheet",
        columns=[
            ColumnSpec(name="Name"),
            ColumnSpec(name="Age"),
            ColumnSpec(name="Salary"),
        ],
        rows=[
            RowSpec(
                cells=[
                    CellSpec(value="Alice"),
                    CellSpec(value=30),
                    CellSpec(value=Decimal("75000.50")),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Bob"),
                    CellSpec(value=25),
                    CellSpec(value=Decimal("65000.00")),
                ]
            ),
        ],
    )


@pytest.fixture
def empty_sheet() -> SheetSpec:
    """Create an empty sheet for testing."""
    return SheetSpec(name="EmptySheet", columns=[], rows=[])


@pytest.fixture
def numeric_sheet() -> SheetSpec:
    """Create a sheet with numeric data for conditional formatting tests."""
    return SheetSpec(
        name="NumericData",
        columns=[
            ColumnSpec(name="Value"),
            ColumnSpec(name="Percent"),
            ColumnSpec(name="Score"),
        ],
        rows=[
            RowSpec(
                cells=[CellSpec(value=10), CellSpec(value=0.1), CellSpec(value=85)]
            ),
            RowSpec(
                cells=[CellSpec(value=50), CellSpec(value=0.5), CellSpec(value=72)]
            ),
            RowSpec(
                cells=[CellSpec(value=90), CellSpec(value=0.9), CellSpec(value=95)]
            ),
            RowSpec(
                cells=[CellSpec(value=30), CellSpec(value=0.3), CellSpec(value=60)]
            ),
            RowSpec(
                cells=[CellSpec(value=70), CellSpec(value=0.7), CellSpec(value=88)]
            ),
        ],
    )


@pytest.fixture
def formula_sheet() -> SheetSpec:
    """Create a sheet with formulas."""
    return SheetSpec(
        name="FormulaSheet",
        columns=[
            ColumnSpec(name="A"),
            ColumnSpec(name="B"),
            ColumnSpec(name="Sum"),
        ],
        rows=[
            RowSpec(
                cells=[
                    CellSpec(value=10),
                    CellSpec(value=20),
                    CellSpec(formula="=A2+B2"),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value=30),
                    CellSpec(value=40),
                    CellSpec(formula="=A3+B3"),
                ]
            ),
        ],
    )


@pytest.fixture
def xlsx_output_path(tmp_path: Path) -> Path:
    """Create a temporary output path for XLSX files."""
    return tmp_path / "test_output.xlsx"
