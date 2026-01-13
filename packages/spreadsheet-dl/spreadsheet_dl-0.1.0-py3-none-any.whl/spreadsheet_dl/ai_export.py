"""AI-friendly export module for SpreadsheetDL.

Provides dual export functionality that generates both human-readable ODS files
and AI-consumable JSON files with semantic metadata, enabling LLM integration
for financial analysis.

Requirements implemented:

Features:
    - Simultaneous generation of ODS (human) + JSON (AI) formats
    - JSON includes semantic metadata, formula descriptions, business context
    - Cell tagging with semantic meanings
    - Consistency validation between formats
    - Cell relationship graph for dependency analysis
    - Natural language formula descriptions
    - Context-aware serialization
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar

from spreadsheet_dl.exceptions import FileError, SpreadsheetDLError


class SemanticCellType(Enum):
    """Semantic types for spreadsheet cells."""

    # Structural
    HEADER = "header"
    LABEL = "label"
    EMPTY = "empty"

    # Data types
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    DATE = "date"
    TEXT = "text"
    NUMBER = "number"

    # Financial semantics
    BUDGET_AMOUNT = "budget_amount"
    EXPENSE_AMOUNT = "expense_amount"
    INCOME_AMOUNT = "income_amount"
    BALANCE = "balance"
    TOTAL = "total"
    SUBTOTAL = "subtotal"
    VARIANCE = "variance"
    NET_WORTH = "net_worth"
    SAVINGS_RATE = "savings_rate"

    # Account semantics
    ACCOUNT_NAME = "account_name"
    ACCOUNT_TYPE = "account_type"
    ACCOUNT_BALANCE = "account_balance"
    TRANSFER_AMOUNT = "transfer_amount"

    # Categories
    CATEGORY_NAME = "category_name"
    DESCRIPTION = "description"
    TRANSACTION_DATE = "transaction_date"
    MERCHANT_NAME = "merchant_name"

    # Formulas
    SUM_FORMULA = "sum_formula"
    AVERAGE_FORMULA = "average_formula"
    VLOOKUP_FORMULA = "vlookup_formula"
    SUMIF_FORMULA = "sumif_formula"
    CALCULATED = "calculated"

    # Status indicators
    OVER_BUDGET = "over_budget"
    UNDER_BUDGET = "under_budget"
    WARNING = "warning"
    ALERT = "alert"


class SemanticTag(Enum):
    """Semantic tags for enhanced AI understanding.

    These tags provide additional context about the business meaning
    of cells beyond their basic type.

    """

    # Budget tags
    MONTHLY_ALLOCATION = "monthly_allocation"
    ANNUAL_BUDGET = "annual_budget"
    BUDGET_LIMIT = "budget_limit"
    REMAINING_BUDGET = "remaining_budget"

    # Expense tags
    FIXED_EXPENSE = "fixed_expense"
    VARIABLE_EXPENSE = "variable_expense"
    DISCRETIONARY = "discretionary"
    ESSENTIAL = "essential"
    RECURRING = "recurring"
    ONE_TIME = "one_time"

    # Income tags
    PRIMARY_INCOME = "primary_income"
    SECONDARY_INCOME = "secondary_income"
    PASSIVE_INCOME = "passive_income"
    BONUS = "bonus"
    REFUND = "refund"

    # Status tags
    NEEDS_ATTENTION = "needs_attention"
    ON_TRACK = "on_track"
    EXCEEDED = "exceeded"

    # Time tags
    CURRENT_PERIOD = "current_period"
    HISTORICAL = "historical"
    PROJECTED = "projected"


class ExportError(SpreadsheetDLError):
    """Base exception for export errors."""

    error_code = "FT-EXP-1200"


class DualExportError(ExportError):
    """Raised when dual export fails."""

    error_code = "FT-EXP-1201"

    def __init__(
        self,
        message: str = "Dual export failed",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        super().__init__(
            message,
            suggestion="Check that the ODS file is valid and readable.",
            **kwargs,
        )


class ConsistencyError(ExportError):
    """Raised when ODS and JSON exports are inconsistent."""

    error_code = "FT-EXP-1202"

    def __init__(
        self,
        issues: list[str],
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.issues = issues
        details = "Inconsistencies found:\n" + "\n".join(f"  - {i}" for i in issues)
        super().__init__(
            "ODS and JSON exports are inconsistent",
            details=details,
            suggestion="Re-generate the export or check the source file.",
            **kwargs,
        )


@dataclass
class CellRelationship:
    """Represents a relationship between cells.

    Used to build a dependency graph for understanding formula relationships.

    """

    source_ref: str
    target_ref: str
    relationship_type: str  # "depends_on", "sums", "references", "vlookup"
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "source": self.source_ref,
            "target": self.target_ref,
            "type": self.relationship_type,
            "description": self.description,
        }


@dataclass
class SemanticCell:
    """A cell with semantic metadata for AI processing."""

    row: int
    column: int
    column_letter: str
    value: Any
    display_value: str
    semantic_type: SemanticCellType
    formula: str | None = None
    formula_description: str | None = None
    cell_reference: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    tags: list[SemanticTag] = field(default_factory=list)
    relationships: list[CellRelationship] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON export."""
        result = {
            "ref": self.cell_reference or f"{self.column_letter}{self.row}",
            "value": self._serialize_value(),
            "display": self.display_value,
            "type": self.semantic_type.value,
        }

        if self.formula:
            result["formula"] = self.formula
            if self.formula_description:
                result["formula_meaning"] = self.formula_description

        if self.context:
            result["context"] = self.context

        if self.tags:
            result["tags"] = [tag.value for tag in self.tags]

        if self.relationships:
            result["relationships"] = [r.to_dict() for r in self.relationships]

        return result

    def _serialize_value(self) -> Any:
        """Serialize value for JSON."""
        if isinstance(self.value, Decimal):
            return float(self.value)
        if isinstance(self.value, date):
            return self.value.isoformat()
        if isinstance(self.value, datetime):
            return self.value.isoformat()
        return self.value

    def add_tag(self, tag: SemanticTag) -> None:
        """Add a semantic tag to this cell."""
        if tag not in self.tags:
            self.tags.append(tag)

    def add_relationship(
        self,
        target_ref: str,
        relationship_type: str,
        description: str = "",
    ) -> None:
        """Add a relationship to another cell."""
        self.relationships.append(
            CellRelationship(
                source_ref=self.cell_reference,
                target_ref=target_ref,
                relationship_type=relationship_type,
                description=description,
            )
        )


@dataclass
class SemanticSheet:
    """A sheet with semantic metadata."""

    name: str
    purpose: str
    cells: list[SemanticCell] = field(default_factory=list)
    rows: int = 0
    columns: int = 0
    summary: dict[str, Any] = field(default_factory=dict)
    schema: dict[str, Any] = field(default_factory=dict)
    relationship_graph: list[CellRelationship] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON export."""
        result = {
            "name": self.name,
            "purpose": self.purpose,
            "dimensions": {"rows": self.rows, "columns": self.columns},
            "schema": self.schema,
            "summary": self.summary,
            "cells": [cell.to_dict() for cell in self.cells],
        }

        if self.relationship_graph:
            result["relationship_graph"] = [
                r.to_dict() for r in self.relationship_graph
            ]

        return result

    def get_cell(self, ref: str) -> SemanticCell | None:
        """Get a cell by reference (e.g., 'A1')."""
        for cell in self.cells:
            if cell.cell_reference == ref:
                return cell
        return None

    def build_relationship_graph(self) -> None:
        """Build the complete relationship graph from all cells."""
        self.relationship_graph = []
        for cell in self.cells:
            self.relationship_graph.extend(cell.relationships)


@dataclass
class AIExportMetadata:
    """Metadata for AI export."""

    version: str = "2.0"  # Updated for Phase 3 enhancements
    export_time: str = ""
    source_file: str = ""
    format: str = "spreadsheet-dl-ai-export"
    schema_version: str = "2.0"
    business_context: dict[str, Any] = field(default_factory=dict)
    capabilities: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Set default capabilities."""
        if not self.capabilities:
            self.capabilities = [
                "semantic_cell_types",
                "formula_descriptions",
                "cell_relationships",
                "semantic_tags",
                "business_context",
                "natural_language_queries",
            ]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "format": self.format,
            "schema_version": self.schema_version,
            "export_time": self.export_time or datetime.now().isoformat(),
            "source_file": self.source_file,
            "business_context": self.business_context,
            "capabilities": self.capabilities,
        }


class AIExporter:
    """Export ODS files to AI-friendly JSON format.

    Provides semantic tagging of cells, formula descriptions,
    cell relationship graphs, and business context for LLM consumption.

    Enhanced in Phase 3 to include:
    - Full semantic metadata
    - Natural language formula descriptions
    - Cell relationships graph
    - Context-aware serialization
    - Semantic cell tagging

    Example:
        >>> exporter = AIExporter()
        >>> exporter.include_formulas
        True
        >>> exporter.include_relationships
        True
    """

    # Enhanced formula descriptions with natural language
    FORMULA_DESCRIPTIONS: ClassVar[dict[str, str]] = {
        "SUM": "Calculates the total of a range of values",
        "AVERAGE": "Calculates the average of a range of values",
        "MAX": "Returns the maximum value in a range",
        "MIN": "Returns the minimum value in a range",
        "COUNT": "Counts the number of cells with values",
        "IF": "Conditional calculation based on a test",
        "SUMIF": "Sums values that meet a specific condition",
        "VLOOKUP": "Looks up a value in the first column of a table and returns a value from another column",
        "HLOOKUP": "Looks up a value in the first row and returns a value from another row",
        "INDEX": "Returns a value at a specific position in a range",
        "MATCH": "Returns the position of a value in a range",
        "COUNTIF": "Counts cells that meet a specific condition",
        "AVERAGEIF": "Averages values that meet a specific condition",
        "PMT": "Calculates the payment for a loan based on constant payments and a constant interest rate",
        "FV": "Calculates the future value of an investment",
        "PV": "Calculates the present value of an investment",
        "NPV": "Calculates the net present value of an investment",
        "IRR": "Calculates the internal rate of return for an investment",
    }

    # Semantic tag patterns based on context
    TAG_PATTERNS: ClassVar[dict[SemanticTag, list[str]]] = {
        SemanticTag.FIXED_EXPENSE: [
            "rent",
            "mortgage",
            "insurance",
            "subscription",
            "loan",
        ],
        SemanticTag.VARIABLE_EXPENSE: ["groceries", "utilities", "gas", "dining"],
        SemanticTag.ESSENTIAL: [
            "housing",
            "utilities",
            "groceries",
            "healthcare",
            "insurance",
        ],
        SemanticTag.DISCRETIONARY: [
            "entertainment",
            "dining out",
            "shopping",
            "vacation",
        ],
        SemanticTag.RECURRING: ["monthly", "weekly", "annual", "subscription"],
    }

    # Column letter mapping
    COLUMN_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(
        self,
        include_empty_cells: bool = False,
        include_formulas: bool = True,
        include_context: bool = True,
        include_relationships: bool = True,
        include_tags: bool = True,
    ) -> None:
        """Initialize AI exporter.

        Args:
            include_empty_cells: Whether to include empty cells in export.
            include_formulas: Whether to include formula information.
            include_context: Whether to include contextual information.
            include_relationships: Whether to include cell relationships.
            include_tags: Whether to include semantic tags.
        """
        self.include_empty_cells = include_empty_cells
        self.include_formulas = include_formulas
        self.include_context = include_context
        self.include_relationships = include_relationships
        self.include_tags = include_tags

    def export_to_json(
        self,
        ods_path: str | Path,
        output_path: str | Path | None = None,
        business_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Export ODS file to AI-friendly JSON.

        Args:
            ods_path: Path to ODS file.
            output_path: Optional path to write JSON file.
            business_context: Optional business context to include.

        Returns:
            Dictionary with AI-friendly export data.

        Raises:
            FileError: If ODS file doesn't exist.
            DualExportError: If export fails.
        """
        ods_path = Path(ods_path)

        if not ods_path.exists():
            raise FileError(f"ODS file not found: {ods_path}")

        try:
            # Parse ODS file
            sheets = self._parse_ods(ods_path)

            # Build relationship graphs
            if self.include_relationships:
                for sheet in sheets:
                    sheet.build_relationship_graph()

            # Create metadata
            metadata = AIExportMetadata(
                source_file=str(ods_path),
                export_time=datetime.now().isoformat(),
                business_context=business_context
                or self._infer_business_context(sheets),
            )

            # Build export data
            export_data = {
                "metadata": metadata.to_dict(),
                "sheets": [sheet.to_dict() for sheet in sheets],
                "ai_instructions": self._generate_ai_instructions(sheets),
                "semantic_dictionary": self._generate_semantic_dictionary(),
                "query_examples": self._generate_query_examples(),
            }

            # Write to file if path provided
            if output_path:
                output_path = Path(output_path)
                with open(output_path, "w") as f:
                    json.dump(export_data, f, indent=2, default=str)

            return export_data

        except Exception as e:
            if isinstance(e, SpreadsheetDLError):
                raise
            raise DualExportError(f"Failed to export: {e}") from e

    def export_dual(
        self,
        ods_path: str | Path,
        output_dir: str | Path | None = None,
        *,
        validate: bool = True,
    ) -> tuple[Path, Path]:
        """Export to both ODS copy and AI-friendly JSON.

        Args:
            ods_path: Path to source ODS file.
            output_dir: Directory for output files. If None, uses source directory.
            validate: Whether to validate consistency between formats.

        Returns:
            Tuple of (ods_copy_path, json_path).

        Raises:
            FileError: If source file doesn't exist.
            DualExportError: If export fails.
            ConsistencyError: If validation fails.
        """
        import shutil

        ods_path = Path(ods_path)

        if not ods_path.exists():
            raise FileError(f"ODS file not found: {ods_path}")

        # Determine output directory
        if output_dir is None:
            output_dir = ods_path.parent
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate output filenames
        stem = ods_path.stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ods_output = output_dir / f"{stem}_export_{timestamp}.ods"
        json_output = output_dir / f"{stem}_export_{timestamp}.json"

        try:
            # Copy ODS file
            shutil.copy2(ods_path, ods_output)

            # Export to JSON
            export_data = self.export_to_json(ods_path, json_output)

            # Validate consistency if requested
            if validate:
                issues = self._validate_consistency(ods_output, export_data)
                if issues:
                    raise ConsistencyError(issues)

            return ods_output, json_output

        except Exception as e:
            # Clean up on failure
            if ods_output.exists():
                ods_output.unlink()
            if json_output.exists():
                json_output.unlink()

            if isinstance(e, SpreadsheetDLError):
                raise
            raise DualExportError(f"Dual export failed: {e}") from e

    def _parse_ods(self, ods_path: Path) -> list[SemanticSheet]:
        """Parse ODS file and extract semantic data."""
        try:
            from odf.opendocument import load
            from odf.table import Table, TableCell, TableRow
        except ImportError as err:
            raise DualExportError(
                "odfpy library required for ODS parsing. "
                "Install with: pip install odfpy"
            ) from err

        doc = load(str(ods_path))
        sheets: list[SemanticSheet] = []

        for table in doc.spreadsheet.getElementsByType(Table):
            sheet_name = table.getAttribute("name") or "Sheet"
            semantic_sheet = SemanticSheet(
                name=sheet_name,
                purpose=self._infer_sheet_purpose(sheet_name),
            )

            row_num = 0
            max_col = 0

            for row in table.getElementsByType(TableRow):
                row_num += 1
                col_num = 0

                for cell in row.getElementsByType(TableCell):
                    col_num += 1
                    max_col = max(max_col, col_num)

                    # Handle repeated columns
                    repeat = cell.getAttribute("numbercolumnsrepeated")
                    if repeat and int(repeat) > 1:
                        col_num += int(repeat) - 1
                        max_col = max(max_col, col_num)
                        continue

                    # Extract cell value
                    value = self._extract_cell_value(cell)
                    display = self._extract_display_value(cell)

                    # Skip empty cells if configured
                    if value is None and not self.include_empty_cells:
                        continue

                    # Determine semantic type
                    semantic_type = self._determine_semantic_type(
                        cell, value, row_num, col_num, sheet_name
                    )

                    # Extract formula if present
                    formula = None
                    formula_desc = None
                    if self.include_formulas:
                        formula = cell.getAttribute("formula")
                        if formula:
                            formula_desc = self._describe_formula(formula)

                    # Create semantic cell
                    col_letter = self._get_column_letter(col_num)
                    semantic_cell = SemanticCell(
                        row=row_num,
                        column=col_num,
                        column_letter=col_letter,
                        value=value,
                        display_value=display,
                        semantic_type=semantic_type,
                        formula=formula,
                        formula_description=formula_desc,
                        cell_reference=f"{col_letter}{row_num}",
                    )

                    # Add context if configured
                    if self.include_context:
                        semantic_cell.context = self._build_cell_context(
                            semantic_cell, semantic_sheet
                        )

                    # Add semantic tags if configured
                    if self.include_tags:
                        self._apply_semantic_tags(semantic_cell, semantic_sheet)

                    # Extract relationships if configured
                    if self.include_relationships and formula:
                        self._extract_relationships(semantic_cell, formula)

                    semantic_sheet.cells.append(semantic_cell)

            semantic_sheet.rows = row_num
            semantic_sheet.columns = max_col
            semantic_sheet.summary = self._compute_sheet_summary(semantic_sheet)
            semantic_sheet.schema = self._infer_sheet_schema(semantic_sheet)

            sheets.append(semantic_sheet)

        return sheets

    def _extract_cell_value(self, cell: Any) -> Any:
        """Extract value from ODS cell."""
        value_type = cell.getAttribute("valuetype")

        if (
            value_type == "float"
            or value_type == "currency"
            or value_type == "percentage"
        ):
            val = cell.getAttribute("value")
            return Decimal(val) if val else None
        elif value_type == "date":
            return cell.getAttribute("datevalue")
        elif value_type == "boolean":
            return cell.getAttribute("booleanvalue") == "true"
        else:
            # Text or empty
            try:
                from odf import text

                text_content = []
                for p in cell.getElementsByType(text.P):
                    text_content.append(str(p))
                return " ".join(text_content) if text_content else None
            except (ImportError, AttributeError):
                # ODF library not available or cell structure incompatible
                return None

    def _extract_display_value(self, cell: Any) -> str:
        """Extract display value from ODS cell."""
        try:
            from odf import text

            text_content = []
            for p in cell.getElementsByType(text.P):
                text_content.append(str(p))
            return " ".join(text_content) if text_content else ""
        except (ImportError, AttributeError):
            # ODF library not available or cell structure incompatible
            return ""

    def _determine_semantic_type(
        self,
        cell: Any,
        value: Any,
        row: int,
        col: int,
        sheet_name: str,
    ) -> SemanticCellType:
        """Determine semantic type of a cell."""
        value_type = cell.getAttribute("valuetype")
        formula = cell.getAttribute("formula")

        # Empty cell
        if value is None:
            return SemanticCellType.EMPTY

        # Formula-based types
        if formula:
            formula_upper = formula.upper()
            if "SUM" in formula_upper:
                if "SUMIF" in formula_upper:
                    return SemanticCellType.SUMIF_FORMULA
                return SemanticCellType.SUM_FORMULA
            if "AVERAGE" in formula_upper:
                return SemanticCellType.AVERAGE_FORMULA
            if "VLOOKUP" in formula_upper:
                return SemanticCellType.VLOOKUP_FORMULA
            return SemanticCellType.CALCULATED

        # Header detection (first row or column A labels)
        if row == 1:
            return SemanticCellType.HEADER

        # Value type based detection
        if value_type == "currency":
            # Determine if budget, expense, or income based on context
            self._extract_display_value(cell)
            if isinstance(value, Decimal):
                if value < 0:
                    return SemanticCellType.EXPENSE_AMOUNT
                # Check sheet name for context
                sheet_lower = sheet_name.lower()
                if "budget" in sheet_lower:
                    return SemanticCellType.BUDGET_AMOUNT
                if "income" in sheet_lower:
                    return SemanticCellType.INCOME_AMOUNT
                if "account" in sheet_lower:
                    return SemanticCellType.ACCOUNT_BALANCE
            return SemanticCellType.CURRENCY

        if value_type == "percentage":
            return SemanticCellType.PERCENTAGE

        if value_type == "date":
            return SemanticCellType.TRANSACTION_DATE

        if value_type == "float":
            return SemanticCellType.NUMBER

        # Text-based detection
        if isinstance(value, str):
            lower_val = value.lower()
            # Category keywords
            category_keywords = [
                "housing",
                "food",
                "groceries",
                "transport",
                "utilities",
                "entertainment",
                "savings",
                "income",
                "healthcare",
                "insurance",
            ]
            if any(kw in lower_val for kw in category_keywords):
                return SemanticCellType.CATEGORY_NAME

            # Account keywords
            account_keywords = [
                "checking",
                "savings",
                "credit",
                "investment",
                "retirement",
            ]
            if any(kw in lower_val for kw in account_keywords):
                return SemanticCellType.ACCOUNT_TYPE

            # Total/subtotal keywords
            if "total" in lower_val:
                if "sub" in lower_val or "category" in lower_val:
                    return SemanticCellType.SUBTOTAL
                return SemanticCellType.TOTAL

            # Balance keywords
            if "balance" in lower_val or "remaining" in lower_val:
                return SemanticCellType.BALANCE

            # Net worth
            if "net worth" in lower_val:
                return SemanticCellType.NET_WORTH

            # First column is often labels
            if col == 1 and row > 1:
                return SemanticCellType.LABEL

        return SemanticCellType.TEXT

    def _describe_formula(self, formula: str) -> str:
        """Generate human-readable description of a formula."""
        if not formula:
            return ""

        # Remove ODS formula prefix
        if formula.startswith("of:="):
            formula = formula[4:]
        elif formula.startswith("="):
            formula = formula[1:]

        # Identify main function and create natural language description
        formula_upper = formula.upper()

        for func, base_desc in self.FORMULA_DESCRIPTIONS.items():
            if func in formula_upper:
                # Extract range if present
                range_match = re.search(r"\[\.([A-Z]+\d+):\.([A-Z]+\d+)\]", formula)
                if range_match:
                    start, end = range_match.groups()
                    return f"{base_desc} from cells {start} to {end}"

                # Extract single cell references
                cell_refs = re.findall(r"\[\.([A-Z]+\d+)\]", formula)
                if cell_refs:
                    if func == "VLOOKUP":
                        return "Looks up a value and returns data from the matched row"
                    if func == "SUMIF":
                        return "Sums values where condition is met"
                    return f"{base_desc} using cells {', '.join(cell_refs)}"

                return base_desc

        # Arithmetic operations
        if "+" in formula:
            return "Calculates sum of values"
        if "-" in formula and "[." in formula:
            return "Calculates difference between values"
        if "*" in formula:
            return "Calculates product of values"
        if "/" in formula:
            return "Calculates quotient of values"

        return "Calculated value using formula"

    def _extract_relationships(self, cell: SemanticCell, formula: str) -> None:
        """Extract cell relationships from a formula."""
        if not formula:
            return

        # Remove ODS formula prefix
        if formula.startswith("of:="):
            formula = formula[4:]
        elif formula.startswith("="):
            formula = formula[1:]

        # Find all cell references
        # Pattern: [.A1] or [.A1:.Z99] or ['Sheet Name'.A1]
        single_refs = re.findall(r"\[\.([A-Z]+\d+)\]", formula)
        range_refs = re.findall(r"\[\.([A-Z]+\d+):\.([A-Z]+\d+)\]", formula)
        sheet_refs = re.findall(r"\['([^']+)'\.([A-Z]+\d+)\]", formula)

        formula_upper = formula.upper()

        # Determine relationship type based on formula
        if "SUM" in formula_upper:
            rel_type = "sums"
        elif "VLOOKUP" in formula_upper or "LOOKUP" in formula_upper:
            rel_type = "vlookup"
        elif "IF" in formula_upper:
            rel_type = "conditional_on"
        else:
            rel_type = "depends_on"

        # Add single cell references
        for ref in single_refs:
            cell.add_relationship(ref, rel_type, f"Uses value from {ref}")

        # Add range references
        for start, end in range_refs:
            cell.add_relationship(
                f"{start}:{end}",
                rel_type,
                f"Uses range from {start} to {end}",
            )

        # Add cross-sheet references
        for sheet_name, ref in sheet_refs:
            cell.add_relationship(
                f"{sheet_name}!{ref}",
                "cross_sheet_reference",
                f"References cell {ref} in sheet '{sheet_name}'",
            )

    def _apply_semantic_tags(self, cell: SemanticCell, sheet: SemanticSheet) -> None:
        """Apply semantic tags based on cell content and context."""
        # Get text to analyze
        text_to_analyze = ""
        if cell.display_value:
            text_to_analyze += cell.display_value.lower()
        if cell.context.get("row_label"):
            text_to_analyze += " " + cell.context["row_label"].lower()
        if cell.context.get("column_header"):
            text_to_analyze += " " + cell.context["column_header"].lower()

        # Apply pattern-based tags
        for tag, patterns in self.TAG_PATTERNS.items():
            if any(pattern in text_to_analyze for pattern in patterns):
                cell.add_tag(tag)

        # Apply type-based tags
        if cell.semantic_type == SemanticCellType.BUDGET_AMOUNT:
            cell.add_tag(SemanticTag.MONTHLY_ALLOCATION)
        elif cell.semantic_type == SemanticCellType.EXPENSE_AMOUNT and isinstance(
            cell.value, Decimal
        ):
            # Check if over budget
            budget_header = cell.context.get("column_header", "").lower()
            if "remaining" in budget_header and cell.value < 0:
                cell.add_tag(SemanticTag.EXCEEDED)
                cell.add_tag(SemanticTag.NEEDS_ATTENTION)

        # Current period detection
        if sheet.name and "current" in sheet.name.lower():
            cell.add_tag(SemanticTag.CURRENT_PERIOD)

    def _get_column_letter(self, col: int) -> str:
        """Convert column number to letter(s)."""
        result = ""
        while col > 0:
            col, remainder = divmod(col - 1, 26)
            result = self.COLUMN_LETTERS[remainder] + result
        return result

    def _infer_sheet_purpose(self, sheet_name: str) -> str:
        """Infer the purpose of a sheet from its name."""
        name_lower = sheet_name.lower()

        purposes = {
            "budget": "Monthly budget allocation and tracking",
            "expense": "Expense tracking and categorization",
            "income": "Income tracking and sources",
            "summary": "Financial summary and overview",
            "dashboard": "Key financial metrics and indicators",
            "transaction": "Transaction history and details",
            "category": "Spending by category breakdown",
            "account": "Account balances and management",
            "net worth": "Net worth calculation and tracking",
        }

        for key, purpose in purposes.items():
            if key in name_lower:
                return purpose

        return f"Financial data sheet: {sheet_name}"

    def _build_cell_context(
        self, cell: SemanticCell, sheet: SemanticSheet
    ) -> dict[str, Any]:
        """Build contextual information for a cell."""
        context: dict[str, Any] = {}

        # Find header for this column
        for header_cell in sheet.cells:
            if header_cell.row == 1 and header_cell.column == cell.column:
                context["column_header"] = header_cell.display_value
                break

        # Find label for this row (column A)
        for label_cell in sheet.cells:
            if label_cell.column == 1 and label_cell.row == cell.row:
                context["row_label"] = label_cell.display_value
                break

        # Add sheet context
        context["sheet_name"] = sheet.name
        context["sheet_purpose"] = sheet.purpose

        return context

    def _compute_sheet_summary(self, sheet: SemanticSheet) -> dict[str, Any]:
        """Compute summary statistics for a sheet."""
        summary: dict[str, Any] = {
            "total_cells": len(sheet.cells),
            "data_cells": 0,
            "formula_cells": 0,
            "currency_cells": 0,
            "tagged_cells": 0,
        }

        currency_values: list[Decimal] = []
        expense_total = Decimal("0")
        income_total = Decimal("0")
        budget_total = Decimal("0")

        for cell in sheet.cells:
            if cell.semantic_type != SemanticCellType.EMPTY:
                summary["data_cells"] += 1

            if cell.formula:
                summary["formula_cells"] += 1

            if cell.tags:
                summary["tagged_cells"] += 1

            if cell.semantic_type in (
                SemanticCellType.CURRENCY,
                SemanticCellType.BUDGET_AMOUNT,
                SemanticCellType.EXPENSE_AMOUNT,
                SemanticCellType.INCOME_AMOUNT,
            ):
                summary["currency_cells"] += 1
                if isinstance(cell.value, Decimal):
                    currency_values.append(cell.value)

                    if cell.semantic_type == SemanticCellType.EXPENSE_AMOUNT:
                        expense_total += abs(cell.value)
                    elif cell.semantic_type == SemanticCellType.INCOME_AMOUNT:
                        income_total += cell.value
                    elif cell.semantic_type == SemanticCellType.BUDGET_AMOUNT:
                        budget_total += cell.value

        if currency_values:
            summary["currency_total"] = float(sum(currency_values))
            summary["currency_count"] = len(currency_values)

        if expense_total > 0:
            summary["expense_total"] = float(expense_total)
        if income_total > 0:
            summary["income_total"] = float(income_total)
        if budget_total > 0:
            summary["budget_total"] = float(budget_total)

        return summary

    def _infer_sheet_schema(self, sheet: SemanticSheet) -> dict[str, Any]:
        """Infer the schema/structure of a sheet."""
        schema: dict[str, Any] = {
            "columns": {},
            "has_headers": False,
            "data_start_row": 1,
        }

        # Find headers (row 1)
        for cell in sheet.cells:
            if cell.row == 1:
                schema["has_headers"] = True
                schema["data_start_row"] = 2
                schema["columns"][cell.column_letter] = {
                    "name": cell.display_value,
                    "type": "unknown",
                }

        # Infer column types from data
        for cell in sheet.cells:
            if cell.row > 1 and cell.column_letter in schema["columns"]:
                col_schema = schema["columns"][cell.column_letter]
                if col_schema["type"] == "unknown":
                    col_schema["type"] = cell.semantic_type.value

        return schema

    def _infer_business_context(self, sheets: list[SemanticSheet]) -> dict[str, Any]:
        """Infer business context from sheet data."""
        context: dict[str, Any] = {
            "domain": "personal_finance",
            "document_type": "budget_spreadsheet",
            "sheets_count": len(sheets),
            "sheets": [s.name for s in sheets],
            "features_detected": [],
        }

        # Detect specific contexts
        sheet_names = [s.name.lower() for s in sheets]
        if any("budget" in n for n in sheet_names):
            context["has_budget"] = True
            context["features_detected"].append("budget_tracking")
        if any("expense" in n or "transaction" in n for n in sheet_names):
            context["has_transactions"] = True
            context["features_detected"].append("transaction_tracking")
        if any("account" in n for n in sheet_names):
            context["has_accounts"] = True
            context["features_detected"].append("account_management")
        if any("summary" in n or "dashboard" in n for n in sheet_names):
            context["has_summary"] = True
            context["features_detected"].append("financial_summary")

        return context

    def _generate_ai_instructions(self, sheets: list[SemanticSheet]) -> dict[str, Any]:
        """Generate instructions for AI processing."""
        return {
            "purpose": (
                "This JSON export contains financial data from a budget spreadsheet. "
                "Use the semantic types, tags, and context to understand the meaning of values."
            ),
            "semantic_types": {
                "budget_amount": "Allocated budget for a category",
                "expense_amount": "Actual spending/expense",
                "income_amount": "Income received",
                "balance": "Remaining budget or net balance",
                "total": "Sum total of a category or section",
                "variance": "Difference between budget and actual",
                "account_balance": "Current balance of a financial account",
                "net_worth": "Total assets minus total liabilities",
            },
            "semantic_tags": {
                "fixed_expense": "Expense that stays the same each month",
                "variable_expense": "Expense that changes month to month",
                "essential": "Necessary expense (housing, food, etc.)",
                "discretionary": "Optional expense (entertainment, etc.)",
                "recurring": "Regular, repeated expense",
                "needs_attention": "Item that may require action",
            },
            "formula_meanings": (
                "Formulas are described in natural language in the formula_meaning field"
            ),
            "relationships": (
                "The relationships field shows how cells depend on each other. "
                "Use this to understand calculation flows."
            ),
            "context_usage": (
                "The context field contains column headers and row labels "
                "to help understand what each value represents"
            ),
            "analysis_suggestions": [
                "Compare budget_amount vs expense_amount to find over/under spending",
                "Sum income_amount to calculate total income",
                "Check variance values to identify budget issues",
                "Use category_name to group related expenses",
                "Look for 'needs_attention' tags to find potential problems",
                "Use relationships to trace calculation dependencies",
            ],
        }

    def _generate_semantic_dictionary(self) -> dict[str, str]:
        """Generate a dictionary of semantic type meanings."""
        return {
            stype.value: self._get_semantic_type_description(stype)
            for stype in SemanticCellType
        }

    def _get_semantic_type_description(self, stype: SemanticCellType) -> str:
        """Get description for a semantic type."""
        descriptions = {
            SemanticCellType.HEADER: "Column or row header label",
            SemanticCellType.LABEL: "Row label or identifier",
            SemanticCellType.EMPTY: "Empty or blank cell",
            SemanticCellType.CURRENCY: "Monetary value",
            SemanticCellType.PERCENTAGE: "Percentage value",
            SemanticCellType.DATE: "Date value",
            SemanticCellType.TEXT: "Text content",
            SemanticCellType.NUMBER: "Numeric value",
            SemanticCellType.BUDGET_AMOUNT: "Allocated budget amount for a category",
            SemanticCellType.EXPENSE_AMOUNT: "Actual expense or spending amount",
            SemanticCellType.INCOME_AMOUNT: "Income or revenue amount",
            SemanticCellType.BALANCE: "Remaining balance or net amount",
            SemanticCellType.TOTAL: "Total sum of a section or category",
            SemanticCellType.SUBTOTAL: "Partial sum within a section",
            SemanticCellType.VARIANCE: "Difference between budget and actual",
            SemanticCellType.NET_WORTH: "Total assets minus total liabilities",
            SemanticCellType.SAVINGS_RATE: "Percentage of income saved",
            SemanticCellType.ACCOUNT_NAME: "Name of a financial account",
            SemanticCellType.ACCOUNT_TYPE: "Type of account (checking, savings, etc.)",
            SemanticCellType.ACCOUNT_BALANCE: "Current balance of an account",
            SemanticCellType.TRANSFER_AMOUNT: "Amount transferred between accounts",
            SemanticCellType.CATEGORY_NAME: "Name of expense/income category",
            SemanticCellType.DESCRIPTION: "Description or notes",
            SemanticCellType.TRANSACTION_DATE: "Date of a transaction",
            SemanticCellType.MERCHANT_NAME: "Name of merchant or vendor",
            SemanticCellType.SUM_FORMULA: "Cell contains a SUM formula",
            SemanticCellType.AVERAGE_FORMULA: "Cell contains an AVERAGE formula",
            SemanticCellType.VLOOKUP_FORMULA: "Cell contains a VLOOKUP formula",
            SemanticCellType.SUMIF_FORMULA: "Cell contains a SUMIF formula",
            SemanticCellType.CALCULATED: "Cell contains a calculated value",
            SemanticCellType.OVER_BUDGET: "Amount exceeds budget allocation",
            SemanticCellType.UNDER_BUDGET: "Amount is under budget allocation",
            SemanticCellType.WARNING: "Value that may need attention",
            SemanticCellType.ALERT: "Critical value requiring immediate attention",
        }
        return descriptions.get(stype, stype.value)

    def _generate_query_examples(self) -> list[dict[str, str]]:
        """Generate example natural language queries for the data."""
        return [
            {
                "query": "What is my total spending this month?",
                "approach": "Sum all cells with semantic_type 'expense_amount'",
            },
            {
                "query": "Which categories are over budget?",
                "approach": "Find cells with tag 'exceeded' or where expense > budget",
            },
            {
                "query": "What is my savings rate?",
                "approach": "Calculate (income - expenses) / income from totals",
            },
            {
                "query": "What are my largest expenses?",
                "approach": "Sort expense_amount cells by value, get top entries",
            },
            {
                "query": "How much do I spend on essentials?",
                "approach": "Sum expense_amount cells with tag 'essential'",
            },
            {
                "query": "What is my net worth?",
                "approach": "Find cells with semantic_type 'net_worth' or calculate from account balances",
            },
        ]

    def _validate_consistency(
        self, ods_path: Path, export_data: dict[str, Any]
    ) -> list[str]:
        """Validate consistency between ODS and JSON export."""
        issues: list[str] = []

        try:
            from odf.opendocument import load
            from odf.table import Table

            doc = load(str(ods_path))
            ods_sheets = list(doc.spreadsheet.getElementsByType(Table))

            json_sheets = export_data.get("sheets", [])

            # Check sheet count
            if len(ods_sheets) != len(json_sheets):
                issues.append(
                    f"Sheet count mismatch: ODS has {len(ods_sheets)}, "
                    f"JSON has {len(json_sheets)}"
                )

            # Check sheet names
            ods_names = {
                t.getAttribute("name") or f"Sheet{i}" for i, t in enumerate(ods_sheets)
            }
            json_names = {s["name"] for s in json_sheets}

            missing_in_json = ods_names - json_names
            if missing_in_json:
                issues.append(f"Sheets missing in JSON: {missing_in_json}")

        except Exception as e:
            issues.append(f"Validation error: {e}")

        return issues


def export_for_ai(
    ods_path: str | Path,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Convenience function to export ODS to AI-friendly JSON.

    Args:
        ods_path: Path to ODS file.
        output_path: Optional path to write JSON file.

    Returns:
        Dictionary with AI-friendly export data.
    """
    exporter = AIExporter()
    return exporter.export_to_json(ods_path, output_path)


def export_dual(
    ods_path: str | Path,
    output_dir: str | Path | None = None,
) -> tuple[Path, Path]:
    """Convenience function for dual export.

    Args:
        ods_path: Path to source ODS file.
        output_dir: Directory for output files.

    Returns:
        Tuple of (ods_copy_path, json_path).
    """
    exporter = AIExporter()
    return exporter.export_dual(ods_path, output_dir)
