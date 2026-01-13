"""Pytest configuration and shared fixtures."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl import (
    BudgetAllocation,
    ExpenseCategory,
    ExpenseEntry,
    OdsGenerator,
)

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


def _get_test_base_date() -> date:
    """Get a stable base date for test fixtures.

    Uses first day of current month to ensure consistent test behavior.
    """
    today = date.today()
    return today.replace(day=1)


@pytest.fixture(autouse=True)
def isolate_tests(tmp_path: Path) -> Generator[None, None, None]:
    """Ensure tests are isolated and don't affect real files."""
    # Tests should use tmp_path for any file operations
    yield


@pytest.fixture
def sample_expenses() -> list[ExpenseEntry]:
    """Create sample expense entries for testing.

    Uses relative dates based on current month for stability.
    """
    base_date = _get_test_base_date()
    return [
        ExpenseEntry(
            date=base_date + timedelta(days=4),
            category=ExpenseCategory.GROCERIES,
            description="Weekly groceries",
            amount=Decimal("150.00"),
        ),
        ExpenseEntry(
            date=base_date + timedelta(days=11),
            category=ExpenseCategory.GROCERIES,
            description="Weekly groceries",
            amount=Decimal("125.50"),
        ),
        ExpenseEntry(
            date=base_date + timedelta(days=7),
            category=ExpenseCategory.UTILITIES,
            description="Electric bill",
            amount=Decimal("95.00"),
        ),
        ExpenseEntry(
            date=base_date + timedelta(days=14),
            category=ExpenseCategory.DINING_OUT,
            description="Restaurant",
            amount=Decimal("75.00"),
        ),
        ExpenseEntry(
            date=base_date + timedelta(days=19),
            category=ExpenseCategory.TRANSPORTATION,
            description="Gas",
            amount=Decimal("45.00"),
        ),
    ]


@pytest.fixture
def sample_allocations() -> list[BudgetAllocation]:
    """Create sample budget allocations for testing."""
    return [
        BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("600")),
        BudgetAllocation(ExpenseCategory.UTILITIES, Decimal("200")),
        BudgetAllocation(ExpenseCategory.DINING_OUT, Decimal("200")),
        BudgetAllocation(ExpenseCategory.TRANSPORTATION, Decimal("400")),
        BudgetAllocation(ExpenseCategory.SAVINGS, Decimal("500")),
    ]


@pytest.fixture
def sample_budget_file(
    tmp_path: Path,
    sample_expenses: list[ExpenseEntry],
    sample_allocations: list[BudgetAllocation],
) -> Path:
    """Create a sample budget ODS file for testing."""
    output_path = tmp_path / "test_budget.ods"
    generator = OdsGenerator()
    base_date = _get_test_base_date()

    generator.create_budget_spreadsheet(
        output_path,
        month=base_date.month,
        year=base_date.year,
        expenses=sample_expenses,
        budget_allocations=sample_allocations,
    )

    return output_path


@pytest.fixture
def empty_budget_file(tmp_path: Path) -> Path:
    """Create an empty budget ODS file for testing."""
    output_path = tmp_path / "empty_budget.ods"
    generator = OdsGenerator()
    base_date = _get_test_base_date()

    generator.create_budget_spreadsheet(
        output_path, month=base_date.month, year=base_date.year
    )

    return output_path
