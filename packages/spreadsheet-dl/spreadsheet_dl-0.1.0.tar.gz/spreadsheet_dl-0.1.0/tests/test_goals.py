"""
Tests for Goals Module.

: Savings Goals and : Debt Payoff.
"""

from __future__ import annotations

import tempfile
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from spreadsheet_dl import (
    Debt,
    DebtPayoffMethod,
    DebtPayoffPlan,
    GoalCategory,
    GoalManager,
    GoalStatus,
    SavingsGoal,
    compare_payoff_methods,
    create_debt_payoff_plan,
    create_emergency_fund,
)

pytestmark = [pytest.mark.unit, pytest.mark.finance]


class TestSavingsGoal:
    """Tests for SavingsGoal."""

    def test_create_goal(self) -> None:
        """Test creating a savings goal."""
        goal = SavingsGoal.create(
            name="Vacation Fund",
            target_amount=5000,
            category=GoalCategory.VACATION,
        )

        assert goal.name == "Vacation Fund"
        assert goal.target_amount == Decimal("5000")
        assert goal.category == GoalCategory.VACATION
        assert goal.current_amount == Decimal("0")
        assert goal.id is not None

    def test_goal_progress(self) -> None:
        """Test progress calculation."""
        goal = SavingsGoal.create("Test", 1000)
        goal.current_amount = Decimal("250")

        assert goal.progress_percent == Decimal("25.0")
        assert goal.remaining == Decimal("750")
        assert not goal.is_completed

    def test_goal_completion(self) -> None:
        """Test goal completion."""
        goal = SavingsGoal.create("Test", 1000)
        goal.add_contribution(1000)

        assert goal.is_completed
        assert goal.status == GoalStatus.COMPLETED
        assert goal.completed_at == date.today()

    def test_goal_status_tracking(self) -> None:
        """Test status based on progress vs time."""
        goal = SavingsGoal.create("Test", 1000)
        goal.created_at = date.today() - timedelta(days=30)
        goal.target_date = date.today() + timedelta(days=30)

        # 50% time elapsed, should be at ~50%
        # At 0%, should be behind
        assert goal.status == GoalStatus.BEHIND

        # At 60%, should be on track or ahead
        goal.current_amount = Decimal("600")
        assert goal.status in (GoalStatus.ON_TRACK, GoalStatus.AHEAD)

    def test_monthly_contribution_projection(self) -> None:
        """Test projected completion with monthly contribution."""
        goal = SavingsGoal.create("Test", 1200)
        goal.monthly_contribution = Decimal("100")

        # Should complete in ~12 months
        projected = goal.projected_completion_date
        assert projected is not None
        # Allow some variance for month length
        days_until = (projected - date.today()).days
        assert 350 <= days_until <= 380

    def test_add_contribution(self) -> None:
        """Test adding contributions."""
        goal = SavingsGoal.create("Test", 1000)

        goal.add_contribution(100)
        assert goal.current_amount == Decimal("100")

        goal.add_contribution("200.50")
        assert goal.current_amount == Decimal("300.50")

    def test_serialization(self) -> None:
        """Test goal serialization/deserialization."""
        goal = SavingsGoal.create(
            name="Test Goal",
            target_amount=5000,
            category=GoalCategory.EMERGENCY_FUND,
        )
        goal.current_amount = Decimal("1000")
        goal.notes = "My emergency fund"

        data = goal.to_dict()
        restored = SavingsGoal.from_dict(data)

        assert restored.name == goal.name
        assert restored.target_amount == goal.target_amount
        assert restored.current_amount == goal.current_amount
        assert restored.category == goal.category
        assert restored.notes == goal.notes


class TestDebt:
    """Tests for Debt."""

    def test_create_debt(self) -> None:
        """Test creating a debt."""
        debt = Debt.create(
            name="Credit Card",
            balance=5000,
            interest_rate=0.18,
            minimum_payment=100,
            creditor="Visa",
        )

        assert debt.name == "Credit Card"
        assert debt.current_balance == Decimal("5000")
        assert debt.interest_rate == Decimal("0.18")
        assert debt.minimum_payment == Decimal("100")

    def test_monthly_interest(self) -> None:
        """Test monthly interest calculation."""
        debt = Debt.create("Test", 12000, 0.12, 200)

        # 12% annual = 1% monthly = $120
        assert debt.monthly_interest == Decimal("120.00")

    def test_make_payment(self) -> None:
        """Test making a payment."""
        debt = Debt.create("Test", 1000, 0.18, 50)

        debt.make_payment(500)
        assert debt.current_balance == Decimal("500")

        debt.make_payment(600)
        assert debt.current_balance == Decimal("0")
        assert debt.is_paid_off
        assert debt.paid_off_at == date.today()

    def test_progress_percent(self) -> None:
        """Test progress tracking."""
        debt = Debt.create("Test", 10000, 0.18, 200)
        debt.current_balance = Decimal("7500")

        assert debt.progress_percent == Decimal("25.0")

    def test_payoff_months_calculation(self) -> None:
        """Test months to payoff calculation."""
        debt = Debt.create("Test", 1000, 0.12, 100)

        months = debt.payoff_months_minimum
        assert months is not None
        assert months > 0
        assert months < 15  # Should pay off in under 15 months

    def test_serialization(self) -> None:
        """Test debt serialization/deserialization."""
        debt = Debt.create("Credit Card", 5000, 0.18, 100)
        debt.make_payment(500)

        data = debt.to_dict()
        restored = Debt.from_dict(data)

        assert restored.name == debt.name
        assert restored.current_balance == debt.current_balance
        assert restored.original_balance == debt.original_balance


class TestDebtPayoffPlan:
    """Tests for DebtPayoffPlan."""

    def test_create_plan(self) -> None:
        """Test creating a payoff plan."""
        plan = DebtPayoffPlan(
            method=DebtPayoffMethod.AVALANCHE,
            extra_payment=Decimal("200"),
            debts=[
                Debt.create("Card A", 5000, 0.18, 100),
                Debt.create("Card B", 3000, 0.12, 75),
            ],
        )

        assert plan.total_debt == Decimal("8000")
        assert plan.total_minimum_payment == Decimal("175")
        assert plan.monthly_payment == Decimal("375")

    def test_snowball_ordering(self) -> None:
        """Test snowball method orders by balance."""
        plan = DebtPayoffPlan(
            method=DebtPayoffMethod.SNOWBALL,
            debts=[
                Debt.create("Big", 10000, 0.06, 200),
                Debt.create("Small", 1000, 0.24, 50),
                Debt.create("Medium", 5000, 0.12, 100),
            ],
        )

        ordered = plan.get_ordered_debts()
        balances = [d.current_balance for d in ordered]

        # Should be ordered smallest to largest
        assert balances == sorted(balances)

    def test_avalanche_ordering(self) -> None:
        """Test avalanche method orders by rate."""
        plan = DebtPayoffPlan(
            method=DebtPayoffMethod.AVALANCHE,
            debts=[
                Debt.create("Low", 10000, 0.06, 200),
                Debt.create("High", 1000, 0.24, 50),
                Debt.create("Med", 5000, 0.12, 100),
            ],
        )

        ordered = plan.get_ordered_debts()
        rates = [d.interest_rate for d in ordered]

        # Should be ordered highest to lowest
        assert rates == sorted(rates, reverse=True)

    def test_payoff_schedule(self) -> None:
        """Test payoff schedule generation."""
        plan = DebtPayoffPlan(
            method=DebtPayoffMethod.AVALANCHE,
            extra_payment=Decimal("100"),
            debts=[
                Debt.create("Card", 2000, 0.18, 50),
            ],
        )

        schedule = plan.calculate_payoff_schedule()

        assert len(schedule) > 0
        assert schedule[0]["month"] == 1
        assert schedule[-1]["total_balance"] == Decimal("0")

    def test_interest_comparison(self) -> None:
        """Test interest saved calculation."""
        plan = DebtPayoffPlan(
            method=DebtPayoffMethod.AVALANCHE,
            extra_payment=Decimal("200"),
            debts=[
                Debt.create("Card", 5000, 0.18, 100),
            ],
        )

        saved = plan.interest_saved_vs_minimum()
        assert saved > 0  # Should save money with extra payment


class TestGoalManager:
    """Tests for GoalManager."""

    def test_add_and_list_goals(self) -> None:
        """Test adding and listing goals."""
        manager = GoalManager()

        goal1 = SavingsGoal.create("Goal 1", 1000)
        goal2 = SavingsGoal.create("Goal 2", 2000)

        manager.add_goal(goal1)
        manager.add_goal(goal2)

        goals = manager.list_goals()
        assert len(goals) == 2

    def test_remove_goal(self) -> None:
        """Test removing a goal."""
        manager = GoalManager()
        goal = SavingsGoal.create("Test", 1000)
        manager.add_goal(goal)

        assert manager.remove_goal(goal.id)
        assert manager.get_goal(goal.id) is None

    def test_get_goal_by_name(self) -> None:
        """Test finding goal by name."""
        manager = GoalManager()
        goal = SavingsGoal.create("Emergency Fund", 10000)
        manager.add_goal(goal)

        found = manager.get_goal_by_name("emergency fund")
        assert found is not None
        assert found.id == goal.id

    def test_add_contribution(self) -> None:
        """Test adding contribution through manager."""
        manager = GoalManager()
        goal = SavingsGoal.create("Test", 1000)
        manager.add_goal(goal)

        result = manager.add_contribution(goal.id, 250)
        assert result is not None
        assert result.current_amount == Decimal("250")

    def test_goals_summary(self) -> None:
        """Test goals summary generation."""
        manager = GoalManager()
        manager.add_goal(SavingsGoal.create("Active", 1000))
        completed = SavingsGoal.create("Done", 500)
        completed.current_amount = Decimal("500")
        manager.add_goal(completed)

        summary = manager.get_goals_summary()
        assert summary["total_goals"] == 2
        assert summary["active_goals"] == 1
        assert summary["completed_goals"] == 1

    def test_debt_plan_management(self) -> None:
        """Test debt plan management."""
        manager = GoalManager()

        debt = Debt.create("Card", 5000, 0.18, 100)
        manager.add_debt(debt)

        plan = manager.get_debt_plan()
        assert plan is not None
        assert len(plan.debts) == 1

    def test_persistence(self) -> None:
        """Test saving and loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "goals.json"
            manager = GoalManager(data_path=path)

            goal = SavingsGoal.create("Test Goal", 5000)
            manager.add_goal(goal)

            # Reload
            manager2 = GoalManager(data_path=path)
            loaded = manager2.get_goal(goal.id)

            assert loaded is not None
            assert loaded.name == goal.name
            assert loaded.target_amount == goal.target_amount


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_emergency_fund(self) -> None:
        """Test emergency fund creation."""
        goal = create_emergency_fund(months=3, monthly_expenses=2000)

        assert goal.target_amount == Decimal("6000")
        assert goal.category == GoalCategory.EMERGENCY_FUND
        assert "3" in goal.name

    def test_create_debt_payoff_plan(self) -> None:
        """Test debt plan creation from dicts."""
        debts = [
            {"name": "Card A", "balance": 5000, "rate": 0.18, "minimum": 100},
            {"name": "Card B", "balance": 3000, "rate": 0.12, "minimum": 75},
        ]

        plan = create_debt_payoff_plan(debts, extra_payment=200)

        assert len(plan.debts) == 2
        assert plan.extra_payment == Decimal("200")
        assert plan.method == DebtPayoffMethod.AVALANCHE

    def test_compare_payoff_methods(self) -> None:
        """Test method comparison."""
        debts = [
            {"name": "High Rate", "balance": 5000, "rate": 0.24, "minimum": 100},
            {"name": "Low Rate", "balance": 10000, "rate": 0.06, "minimum": 200},
        ]

        comparison = compare_payoff_methods(debts, extra_payment=200)

        assert "snowball" in comparison
        assert "avalanche" in comparison
        assert "difference" in comparison
        assert "recommendation" in comparison

        # Avalanche should save more interest in this case
        assert (
            comparison["avalanche"]["total_interest"]
            <= comparison["snowball"]["total_interest"]
        )
