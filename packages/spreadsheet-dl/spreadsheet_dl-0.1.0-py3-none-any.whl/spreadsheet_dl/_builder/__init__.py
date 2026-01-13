"""Builder package - Fluent API for spreadsheet construction.

Modular structure:
    - exceptions.py: Builder-specific exceptions
    - models.py: Data models (CellSpec, RowSpec, SheetSpec, etc.)
    - references.py: Cell and range references
    - formulas.py: Formula builder and dependency tracking
    - core.py: Main SpreadsheetBuilder class

All public APIs are re-exported here for convenient access.
"""

from __future__ import annotations

# Import from modular structure
from spreadsheet_dl._builder.core import (
    SpreadsheetBuilder,
    create_spreadsheet,
    formula,
)
from spreadsheet_dl._builder.exceptions import (
    BuilderError,
    CircularReferenceError,
    EmptySheetError,
    InvalidRangeError,
    NoRowSelectedError,
    NoSheetSelectedError,
)
from spreadsheet_dl._builder.formulas import (
    FormulaBuilder,
    FormulaDependencyGraph,
)
from spreadsheet_dl._builder.models import (
    CellSpec,
    ColumnSpec,
    RowSpec,
    SheetSpec,
    WorkbookProperties,
)
from spreadsheet_dl._builder.references import (
    CellRef,
    NamedRange,
    RangeRef,
    SheetRef,
)

__all__ = [
    # Exceptions
    "BuilderError",
    # References
    "CellRef",
    # Data models
    "CellSpec",
    "CircularReferenceError",
    "ColumnSpec",
    "EmptySheetError",
    "FormulaBuilder",
    # Formula builder
    "FormulaDependencyGraph",
    "InvalidRangeError",
    "NamedRange",
    "NoRowSelectedError",
    "NoSheetSelectedError",
    "RangeRef",
    "RowSpec",
    "SheetRef",
    "SheetSpec",
    # Core builder
    "SpreadsheetBuilder",
    "WorkbookProperties",
    "create_spreadsheet",
    "formula",
]
