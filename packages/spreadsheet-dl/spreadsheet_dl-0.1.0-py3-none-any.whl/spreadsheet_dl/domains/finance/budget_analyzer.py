"""Budget Analyzer - Analyze ODS budget spreadsheets with pandas.

Provides analysis, insights, and trend tracking for family budget data
stored in ODS format.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd

# Try to import pyexcel_ods3 as fallback reader
try:
    import pyexcel_ods3  # noqa: F401

    HAS_PYEXCEL = True
except ImportError:
    HAS_PYEXCEL = False


@dataclass
class CategorySpending:
    """Spending summary for a category."""

    category: str
    budget: Decimal
    actual: Decimal
    remaining: Decimal
    percent_used: float


@dataclass
class BudgetSummary:
    """Overall budget summary."""

    total_budget: Decimal
    total_spent: Decimal
    total_remaining: Decimal
    percent_used: float
    categories: list[CategorySpending]
    top_categories: list[tuple[str, Decimal]]
    alerts: list[str]


@dataclass
class SpendingTrend:
    """Spending trend over time."""

    period: str
    total: Decimal
    by_category: dict[str, Decimal]


class BudgetAnalyzer:
    """Analyze budget ODS files and provide insights.

    Uses pyexcel_ods3 for reliable ODS file reading with pandas
    for data analysis.
    """

    def __init__(self, ods_path: Path | str) -> None:
        """Initialize analyzer with an ODS file.

        Args:
            ods_path: Path to the ODS budget file.
        """
        self.ods_path = Path(ods_path)
        self._expenses_df: pd.DataFrame | None = None
        self._budget_df: pd.DataFrame | None = None

    @property
    def expenses(self) -> pd.DataFrame:
        """Load and return the expense log dataframe."""
        if self._expenses_df is None:
            self._expenses_df = self._load_expenses()
        return self._expenses_df

    @property
    def budget(self) -> pd.DataFrame:
        """Load and return the budget dataframe."""
        if self._budget_df is None:
            self._budget_df = self._load_budget()
        return self._budget_df

    def _read_ods_sheet(self, sheet_name: str) -> list[list[Any]]:
        """Read a sheet from ODS file using odfpy directly.

        This is more reliable than pandas read_excel with odf engine
        and avoids pyexcel-ods3 currency cell bugs.

        Args:
            sheet_name: Name of the sheet to read.

        Returns:
            List of rows, where each row is a list of cell values.
        """
        from odf import opendocument, table, text

        doc = opendocument.load(str(self.ods_path))

        # Find the sheet
        sheets = doc.spreadsheet.getElementsByType(table.Table)
        target_sheet = None
        for sheet in sheets:
            if sheet.getAttribute("name") == sheet_name:
                target_sheet = sheet
                break

        if target_sheet is None:
            raise ValueError(f"Sheet '{sheet_name}' not found in {self.ods_path}")

        # Extract rows
        rows = []
        for row_elem in target_sheet.getElementsByType(table.TableRow):
            row_data: list[Any] = []
            for cell in row_elem.getElementsByType(table.TableCell):
                # Get cell value
                cell_type = cell.getAttribute("valuetype")

                if cell_type in ("float", "currency"):
                    value = cell.getAttribute("value")
                    if value:
                        row_data.append(float(value))
                    else:
                        row_data.append(None)
                elif cell_type == "date":
                    value = cell.getAttribute("datevalue")
                    row_data.append(value if value else None)
                else:
                    # String or other type - get text content
                    paragraphs = cell.getElementsByType(text.P)
                    if paragraphs:
                        cell_text = "".join(str(p) for p in paragraphs)
                        row_data.append(cell_text if cell_text else None)
                    else:
                        row_data.append(None)

                # Handle repeated cells
                repeat = cell.getAttribute("numbercolumnsrepeated")
                if repeat:
                    try:
                        repeat_count = int(repeat) - 1
                        for _ in range(repeat_count):
                            row_data.append(None)
                    except ValueError:
                        pass

            rows.append(row_data)

        return rows

    def _load_expenses(self) -> pd.DataFrame:
        """Load expense log from ODS file."""
        try:
            # Use pyexcel_ods3 for reliable reading
            rows = self._read_ods_sheet("Expense Log")

            if not rows:
                return pd.DataFrame(
                    columns=["Date", "Category", "Description", "Amount", "Notes"]
                )

            # First row is headers
            headers = [
                str(h).strip() if h else f"Column_{i}" for i, h in enumerate(rows[0])
            ]

            # Data rows (skip header, filter empty rows)
            data_rows = []
            for row in rows[1:]:
                # Pad row to match header length
                padded_row = row + [None] * (len(headers) - len(row))
                # Skip completely empty rows
                if any(
                    cell is not None and str(cell).strip() for cell in padded_row[:4]
                ):
                    data_rows.append(padded_row[: len(headers)])

            df = pd.DataFrame(data_rows, columns=headers)

            # Clean and standardize column names
            df.columns = df.columns.str.strip()

            # Ensure Date column is datetime
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

            # Ensure Amount is numeric - handle currency strings
            if "Amount" in df.columns:
                # Remove currency symbols and convert
                df["Amount"] = df["Amount"].apply(self._parse_amount)

            # Drop rows where both Date and Amount are missing/NaN
            df = df.dropna(subset=["Date", "Amount"], how="all")

            return df
        except (OSError, ValueError) as e:
            raise ValueError(f"Failed to load expense log: {e}") from e

    def _parse_amount(self, value: Any) -> float | None:
        """Parse amount value, handling currency symbols and strings."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove currency symbols, commas, and whitespace
            cleaned = value.replace("$", "").replace(",", "").strip()
            if not cleaned:
                return None
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    def _load_budget(self) -> pd.DataFrame:
        """Load budget allocations from ODS file."""
        try:
            # Use pyexcel_ods3 for reliable reading
            rows = self._read_ods_sheet("Budget")

            if not rows:
                return pd.DataFrame(columns=["Category", "Monthly Budget", "Notes"])

            # First row is headers
            headers = [
                str(h).strip() if h else f"Column_{i}" for i, h in enumerate(rows[0])
            ]

            # Data rows (skip header, filter empty rows and TOTAL row)
            data_rows = []
            for row in rows[1:]:
                # Pad row to match header length
                padded_row = row + [None] * (len(headers) - len(row))
                first_cell = str(padded_row[0]).strip() if padded_row[0] else ""
                # Skip empty rows and TOTAL row
                if first_cell and first_cell.upper() != "TOTAL":
                    data_rows.append(padded_row[: len(headers)])

            df = pd.DataFrame(data_rows, columns=headers)
            df.columns = df.columns.str.strip()

            # Ensure Monthly Budget is numeric - handle currency strings
            if "Monthly Budget" in df.columns:
                df["Monthly Budget"] = df["Monthly Budget"].apply(self._parse_amount)

            return df
        except (OSError, ValueError) as e:
            raise ValueError(f"Failed to load budget: {e}") from e

    def get_summary(self) -> BudgetSummary:
        """Get overall budget summary.

        Returns:
            BudgetSummary with totals, category breakdown, and alerts.
        """
        expenses = self.expenses
        budget_df = self.budget

        # Calculate totals
        total_budget = Decimal(str(budget_df["Monthly Budget"].sum()))
        total_spent = (
            Decimal(str(expenses["Amount"].sum()))
            if not expenses.empty
            else Decimal("0")
        )
        total_remaining = total_budget - total_spent
        percent_used = float(total_spent / total_budget * 100) if total_budget else 0

        # Category breakdown
        category_spending = []
        alerts = []

        spending_by_cat = (
            expenses.groupby("Category")["Amount"].sum()
            if not expenses.empty
            else pd.Series(dtype=float)
        )

        for _, row in budget_df.iterrows():
            cat = row["Category"]
            budget_amt = Decimal(str(row["Monthly Budget"]))
            actual_amt = Decimal(str(spending_by_cat.get(cat, 0)))
            remaining = budget_amt - actual_amt
            pct_used = float(actual_amt / budget_amt * 100) if budget_amt else 0

            category_spending.append(
                CategorySpending(
                    category=cat,
                    budget=budget_amt,
                    actual=actual_amt,
                    remaining=remaining,
                    percent_used=pct_used,
                )
            )

            # Alert if over 90%
            if pct_used >= 100:
                alerts.append(f"OVER BUDGET: {cat} ({pct_used:.0f}%)")
            elif pct_used >= 90:
                alerts.append(f"WARNING: {cat} at {pct_used:.0f}% of budget")

        # Top spending categories
        top_cats = (
            [
                (str(cat), Decimal(str(amt)))
                for cat, amt in spending_by_cat.nlargest(5).items()
            ]
            if not spending_by_cat.empty
            else []
        )

        return BudgetSummary(
            total_budget=total_budget,
            total_spent=total_spent,
            total_remaining=total_remaining,
            percent_used=percent_used,
            categories=category_spending,
            top_categories=top_cats,
            alerts=alerts,
        )

    def get_monthly_trend(
        self,
        months: int = 6,
    ) -> list[SpendingTrend]:
        """Get spending trends over recent months.

        Args:
            months: Number of months to analyze.

        Returns:
            List of SpendingTrend for each month.
        """
        expenses = self.expenses

        if expenses.empty or "Date" not in expenses.columns:
            return []

        # Group by month
        expenses = expenses.copy()
        expenses["Month"] = expenses["Date"].dt.to_period("M")
        recent = expenses[
            expenses["Date"] >= (datetime.now() - pd.DateOffset(months=months))
        ]

        trends = []
        for period, group in recent.groupby("Month"):
            total = Decimal(str(group["Amount"].sum()))
            by_cat = {
                str(cat): Decimal(str(amt))
                for cat, amt in group.groupby("Category")["Amount"].sum().items()
            }
            trends.append(
                SpendingTrend(
                    period=str(period),
                    total=total,
                    by_category=by_cat,
                )
            )

        return sorted(trends, key=lambda t: t.period)

    def get_category_breakdown(self) -> dict[str, Decimal]:
        """Get spending breakdown by category.

        Returns:
            Dictionary mapping category to total spent.
        """
        expenses = self.expenses
        if expenses.empty:
            return {}

        return {
            str(cat): Decimal(str(amt))
            for cat, amt in expenses.groupby("Category")["Amount"].sum().items()
        }

    def get_daily_average(self) -> Decimal:
        """Calculate daily average spending.

        Returns:
            Average daily spending amount.
        """
        expenses = self.expenses
        if expenses.empty or "Date" not in expenses.columns:
            return Decimal("0")

        total = expenses["Amount"].sum()
        date_col = expenses["Date"].dropna()
        if date_col.empty:
            return Decimal(str(total)) if total else Decimal("0")

        days = (date_col.max() - date_col.min()).days + 1

        if days <= 0:
            return Decimal(str(total))

        return Decimal(str(total / days))

    def filter_by_category(self, category: str) -> pd.DataFrame:
        """Get expenses for a specific category.

        Args:
            category: Category name to filter.

        Returns:
            DataFrame of expenses in that category.
        """
        expenses = self.expenses
        return expenses[expenses["Category"] == category]

    def filter_by_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> pd.DataFrame:
        """Get expenses within a date range.

        Args:
            start_date: Start of range (inclusive).
            end_date: End of range (inclusive).

        Returns:
            DataFrame of expenses in that range.
        """
        expenses = self.expenses
        mask = (expenses["Date"] >= pd.Timestamp(start_date)) & (
            expenses["Date"] <= pd.Timestamp(end_date)
        )
        return expenses[mask]

    def to_dict(self) -> dict[str, Any]:
        """Export analysis as dictionary (for JSON serialization).

        Returns:
            Dictionary with all analysis data.
        """
        summary = self.get_summary()
        return {
            "file": str(self.ods_path),
            "total_budget": float(summary.total_budget),
            "total_spent": float(summary.total_spent),
            "total_remaining": float(summary.total_remaining),
            "percent_used": summary.percent_used,
            "categories": [
                {
                    "category": c.category,
                    "budget": float(c.budget),
                    "actual": float(c.actual),
                    "remaining": float(c.remaining),
                    "percent_used": c.percent_used,
                }
                for c in summary.categories
            ],
            "top_categories": [
                {"category": cat, "amount": float(amt)}
                for cat, amt in summary.top_categories
            ],
            "alerts": summary.alerts,
            "daily_average": float(self.get_daily_average()),
        }


def analyze_budget(ods_path: Path | str) -> dict[str, Any]:
    """Convenience function to analyze a budget file.

    Args:
        ods_path: Path to ODS budget file.

    Returns:
        Dictionary with analysis results.
    """
    analyzer = BudgetAnalyzer(ods_path)
    return analyzer.to_dict()
