"""Goals Module - Savings goals and debt payoff tracking.

Provides tracking for financial goals including savings targets,
debt payoff with snowball/avalanche methods, and progress monitoring.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any


class GoalCategory(Enum):
    """Categories for financial goals."""

    SAVINGS = "savings"
    EMERGENCY_FUND = "emergency_fund"
    VACATION = "vacation"
    HOME_DOWN_PAYMENT = "home_down_payment"
    CAR_PURCHASE = "car_purchase"
    EDUCATION = "education"
    RETIREMENT = "retirement"
    WEDDING = "wedding"
    DEBT_PAYOFF = "debt_payoff"
    INVESTMENT = "investment"
    OTHER = "other"


class GoalStatus(Enum):
    """Status of a goal."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ON_TRACK = "on_track"
    BEHIND = "behind"
    AHEAD = "ahead"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class DebtPayoffMethod(Enum):
    """Debt payoff strategy methods."""

    SNOWBALL = "snowball"  # Smallest balance first
    AVALANCHE = "avalanche"  # Highest interest rate first
    CUSTOM = "custom"  # User-defined order


@dataclass
class SavingsGoal:
    """A savings goal with target amount and progress tracking.

    Attributes:
        id: Unique identifier.
        name: Goal name.
        category: Goal category.
        target_amount: Amount to save.
        current_amount: Amount saved so far.
        target_date: Optional deadline.
        monthly_contribution: Planned monthly contribution.
        priority: Priority order (1 = highest).
        notes: Additional notes.
        created_at: When goal was created.
        completed_at: When goal was completed.
    """

    id: str
    name: str
    category: GoalCategory
    target_amount: Decimal
    current_amount: Decimal = Decimal("0")
    target_date: date | None = None
    monthly_contribution: Decimal | None = None
    priority: int = 1
    notes: str = ""
    created_at: date = field(default_factory=date.today)
    completed_at: date | None = None
    is_paused: bool = False

    @classmethod
    def create(
        cls,
        name: str,
        target_amount: Decimal | float | str,
        category: GoalCategory = GoalCategory.SAVINGS,
        **kwargs: Any,
    ) -> SavingsGoal:
        """Create a new savings goal."""
        return cls(
            id=str(uuid.uuid4())[:8],
            name=name,
            category=category,
            target_amount=Decimal(str(target_amount)),
            **kwargs,
        )

    @property
    def remaining(self) -> Decimal:
        """Amount remaining to reach goal."""
        return max(Decimal("0"), self.target_amount - self.current_amount)

    @property
    def progress_percent(self) -> Decimal:
        """Progress as percentage (0-100)."""
        if self.target_amount <= 0:
            return Decimal("100")
        return ((self.current_amount / self.target_amount) * 100).quantize(
            Decimal("0.1")
        )

    @property
    def is_completed(self) -> bool:
        """Check if goal is completed."""
        return self.current_amount >= self.target_amount

    @property
    def status(self) -> GoalStatus:
        """Calculate current status."""
        if self.completed_at or self.is_completed:
            return GoalStatus.COMPLETED
        if self.is_paused:
            return GoalStatus.PAUSED

        # Check progress vs expected progress if we have a target date
        if self.target_date:
            expected = self.expected_progress_percent
            actual = self.progress_percent

            # If time has elapsed and we're behind schedule
            if actual >= expected + 10:
                return GoalStatus.AHEAD
            elif actual <= expected - 10:
                return GoalStatus.BEHIND
            return GoalStatus.ON_TRACK

        # No target date - check if started
        if self.current_amount == 0:
            return GoalStatus.NOT_STARTED

        return GoalStatus.IN_PROGRESS

    @property
    def expected_progress_percent(self) -> Decimal:
        """Calculate expected progress based on time elapsed."""
        if not self.target_date:
            return Decimal("0")

        total_days = (self.target_date - self.created_at).days
        elapsed_days = (date.today() - self.created_at).days

        if total_days <= 0:
            return Decimal("100")
        if elapsed_days <= 0:
            return Decimal("0")

        return (Decimal(str(elapsed_days)) / Decimal(str(total_days)) * 100).quantize(
            Decimal("0.1")
        )

    @property
    def days_remaining(self) -> int | None:
        """Days until target date."""
        if not self.target_date:
            return None
        return max(0, (self.target_date - date.today()).days)

    @property
    def projected_completion_date(self) -> date | None:
        """Projected completion based on monthly contribution."""
        if self.is_completed or not self.monthly_contribution:
            return None
        if self.monthly_contribution <= 0:
            return None

        months_remaining = float(self.remaining / self.monthly_contribution)
        days = int(months_remaining * 30.44)  # Average days per month
        return date.today() + timedelta(days=days)

    @property
    def monthly_needed_to_reach_target(self) -> Decimal | None:
        """Monthly contribution needed to reach target by deadline."""
        if not self.target_date or self.is_completed:
            return None

        months_remaining = self.days_remaining / 30.44 if self.days_remaining else 0
        if months_remaining <= 0:
            return None

        return (self.remaining / Decimal(str(months_remaining))).quantize(
            Decimal("0.01")
        )

    def add_contribution(self, amount: Decimal | float | str) -> Decimal:
        """Add a contribution to the goal.

        Returns:
            New current amount.
        """
        amount = Decimal(str(amount))
        self.current_amount += amount

        if self.current_amount >= self.target_amount and not self.completed_at:
            self.completed_at = date.today()

        return self.current_amount

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "target_amount": str(self.target_amount),
            "current_amount": str(self.current_amount),
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "monthly_contribution": str(self.monthly_contribution)
            if self.monthly_contribution
            else None,
            "priority": self.priority,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "is_paused": self.is_paused,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SavingsGoal:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            category=GoalCategory(data["category"]),
            target_amount=Decimal(data["target_amount"]),
            current_amount=Decimal(data.get("current_amount", "0")),
            target_date=date.fromisoformat(data["target_date"])
            if data.get("target_date")
            else None,
            monthly_contribution=Decimal(data["monthly_contribution"])
            if data.get("monthly_contribution")
            else None,
            priority=data.get("priority", 1),
            notes=data.get("notes", ""),
            created_at=date.fromisoformat(
                data.get("created_at", date.today().isoformat())
            ),
            completed_at=date.fromisoformat(data["completed_at"])
            if data.get("completed_at")
            else None,
            is_paused=data.get("is_paused", False),
        )


@dataclass
class Debt:
    """A debt to be paid off.

    Attributes:
        id: Unique identifier.
        name: Debt name (e.g., "Credit Card A").
        creditor: Name of creditor/lender.
        original_balance: Original amount owed.
        current_balance: Current amount owed.
        interest_rate: Annual interest rate as decimal (0.18 = 18%).
        minimum_payment: Minimum monthly payment.
        due_day: Day of month payment is due (1-31).
        notes: Additional notes.
    """

    id: str
    name: str
    creditor: str
    original_balance: Decimal
    current_balance: Decimal
    interest_rate: Decimal
    minimum_payment: Decimal
    due_day: int = 1
    notes: str = ""
    created_at: date = field(default_factory=date.today)
    paid_off_at: date | None = None

    @classmethod
    def create(
        cls,
        name: str,
        balance: Decimal | float | str,
        interest_rate: Decimal | float | str,
        minimum_payment: Decimal | float | str,
        creditor: str = "",
        **kwargs: Any,
    ) -> Debt:
        """Create a new debt."""
        balance = Decimal(str(balance))
        return cls(
            id=str(uuid.uuid4())[:8],
            name=name,
            creditor=creditor,
            original_balance=balance,
            current_balance=balance,
            interest_rate=Decimal(str(interest_rate)),
            minimum_payment=Decimal(str(minimum_payment)),
            **kwargs,
        )

    @property
    def is_paid_off(self) -> bool:
        """Check if debt is paid off."""
        return self.current_balance <= 0

    @property
    def monthly_interest(self) -> Decimal:
        """Calculate monthly interest charge."""
        return (self.current_balance * self.interest_rate / 12).quantize(
            Decimal("0.01")
        )

    @property
    def progress_percent(self) -> Decimal:
        """Progress as percentage paid off."""
        if self.original_balance <= 0:
            return Decimal("100")
        paid = self.original_balance - self.current_balance
        return ((paid / self.original_balance) * 100).quantize(Decimal("0.1"))

    @property
    def payoff_months_minimum(self) -> int | None:
        """Months to payoff with minimum payment only."""
        if self.is_paid_off:
            return 0
        if self.minimum_payment <= self.monthly_interest:
            return None  # Will never pay off

        balance = float(self.current_balance)
        rate = float(self.interest_rate) / 12
        payment = float(self.minimum_payment)

        months = 0
        while balance > 0 and months < 600:  # Cap at 50 years
            interest = balance * rate
            balance = balance + interest - payment
            months += 1

        return months if balance <= 0 else None

    def make_payment(self, amount: Decimal | float | str) -> Decimal:
        """Make a payment on the debt.

        Returns:
            New balance.
        """
        amount = Decimal(str(amount))
        self.current_balance = max(Decimal("0"), self.current_balance - amount)

        if self.current_balance <= 0 and not self.paid_off_at:
            self.paid_off_at = date.today()

        return self.current_balance

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "creditor": self.creditor,
            "original_balance": str(self.original_balance),
            "current_balance": str(self.current_balance),
            "interest_rate": str(self.interest_rate),
            "minimum_payment": str(self.minimum_payment),
            "due_day": self.due_day,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "paid_off_at": self.paid_off_at.isoformat() if self.paid_off_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Debt:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            creditor=data.get("creditor", ""),
            original_balance=Decimal(data["original_balance"]),
            current_balance=Decimal(data["current_balance"]),
            interest_rate=Decimal(data["interest_rate"]),
            minimum_payment=Decimal(data["minimum_payment"]),
            due_day=data.get("due_day", 1),
            notes=data.get("notes", ""),
            created_at=date.fromisoformat(
                data.get("created_at", date.today().isoformat())
            ),
            paid_off_at=date.fromisoformat(data["paid_off_at"])
            if data.get("paid_off_at")
            else None,
        )


@dataclass
class DebtPayoffPlan:
    """A debt payoff plan using snowball or avalanche method.

    Attributes:
        method: Payoff method (snowball/avalanche).
        extra_payment: Extra monthly payment beyond minimums.
        debts: List of debts in payoff order.
    """

    method: DebtPayoffMethod
    extra_payment: Decimal = Decimal("0")
    debts: list[Debt] = field(default_factory=list)

    def get_ordered_debts(self) -> list[Debt]:
        """Get debts in payoff priority order."""
        active_debts = [d for d in self.debts if not d.is_paid_off]

        if self.method == DebtPayoffMethod.SNOWBALL:
            return sorted(active_debts, key=lambda d: d.current_balance)
        elif self.method == DebtPayoffMethod.AVALANCHE:
            return sorted(active_debts, key=lambda d: d.interest_rate, reverse=True)
        else:
            return active_debts

    @property
    def total_debt(self) -> Decimal:
        """Total remaining debt."""
        return sum((d.current_balance for d in self.debts), Decimal("0"))

    @property
    def total_minimum_payment(self) -> Decimal:
        """Total minimum payments."""
        return sum(
            (d.minimum_payment for d in self.debts if not d.is_paid_off), Decimal("0")
        )

    @property
    def monthly_payment(self) -> Decimal:
        """Total monthly payment including extra."""
        return self.total_minimum_payment + self.extra_payment

    def calculate_payoff_schedule(self) -> list[dict[str, Any]]:
        """Calculate month-by-month payoff schedule.

        Returns:
            List of monthly snapshots showing payments and balances.
        """
        schedule = []
        balances = {d.id: float(d.current_balance) for d in self.debts}
        rates = {d.id: float(d.interest_rate) / 12 for d in self.debts}
        minimums = {d.id: float(d.minimum_payment) for d in self.debts}

        month = 0
        max_months = 600  # 50 year cap

        while any(b > 0 for b in balances.values()) and month < max_months:
            month += 1
            month_data: dict[str, Any] = {
                "month": month,
                "date": date.today() + timedelta(days=month * 30),
                "payments": {},
                "balances": {},
                "interest": {},
                "total_balance": Decimal("0"),
                "total_interest": Decimal("0"),
            }

            # Apply interest first
            for debt_id, balance in balances.items():
                if balance > 0:
                    interest = balance * rates[debt_id]
                    balances[debt_id] += interest
                    month_data["interest"][debt_id] = Decimal(str(interest)).quantize(
                        Decimal("0.01")
                    )

            # Calculate available extra payment
            extra_remaining = float(self.extra_payment)

            # Pay minimums first
            for debt_id, balance in balances.items():
                if balance > 0:
                    payment = min(minimums[debt_id], balance)
                    balances[debt_id] -= payment
                    month_data["payments"][debt_id] = Decimal(str(payment)).quantize(
                        Decimal("0.01")
                    )

            # Apply extra payment using selected method
            if extra_remaining > 0:
                ordered = self.get_ordered_debts()
                for debt in ordered:
                    if balances[debt.id] > 0 and extra_remaining > 0:
                        extra = min(extra_remaining, balances[debt.id])
                        balances[debt.id] -= extra
                        extra_remaining -= extra
                        month_data["payments"][debt.id] += Decimal(str(extra)).quantize(
                            Decimal("0.01")
                        )

            # Record final balances
            for debt_id, balance in balances.items():
                month_data["balances"][debt_id] = Decimal(
                    str(max(0, balance))
                ).quantize(Decimal("0.01"))
                month_data["total_balance"] += month_data["balances"][debt_id]

            month_data["total_interest"] = sum(
                month_data["interest"].values(), Decimal("0")
            )

            schedule.append(month_data)

            # Check if all paid off
            if all(b <= 0 for b in balances.values()):
                break

        return schedule

    @property
    def months_to_payoff(self) -> int:
        """Calculate months until all debt is paid off."""
        schedule = self.calculate_payoff_schedule()
        return len(schedule)

    @property
    def total_interest_paid(self) -> Decimal:
        """Calculate total interest that will be paid."""
        schedule = self.calculate_payoff_schedule()
        return sum((m["total_interest"] for m in schedule), Decimal("0"))

    def interest_saved_vs_minimum(self) -> Decimal:
        """Calculate interest saved compared to minimum payments only."""
        # Calculate with extra payment
        with_extra = self.total_interest_paid

        # Calculate with minimums only
        old_extra = self.extra_payment
        self.extra_payment = Decimal("0")
        minimum_only = self.total_interest_paid
        self.extra_payment = old_extra

        return minimum_only - with_extra

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "method": self.method.value,
            "extra_payment": str(self.extra_payment),
            "debts": [d.to_dict() for d in self.debts],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DebtPayoffPlan:
        """Create from dictionary."""
        return cls(
            method=DebtPayoffMethod(data["method"]),
            extra_payment=Decimal(data.get("extra_payment", "0")),
            debts=[Debt.from_dict(d) for d in data.get("debts", [])],
        )


class GoalManager:
    """Manage savings goals and debt payoff.

    Provides CRUD operations, progress tracking, and persistence
    for financial goals.
    """

    def __init__(self, data_path: Path | str | None = None) -> None:
        """Initialize goal manager.

        Args:
            data_path: Path to goals JSON file.
        """
        self.data_path = Path(data_path) if data_path else None
        self._goals: list[SavingsGoal] = []
        self._debt_plan: DebtPayoffPlan | None = None

        if self.data_path and self.data_path.exists():
            self.load()

    # Savings Goals

    def add_goal(self, goal: SavingsGoal) -> None:
        """Add a savings goal."""
        self._goals.append(goal)
        self._save_if_configured()

    def remove_goal(self, goal_id: str) -> bool:
        """Remove a goal by ID."""
        original_len = len(self._goals)
        self._goals = [g for g in self._goals if g.id != goal_id]
        removed = len(self._goals) < original_len
        if removed:
            self._save_if_configured()
        return removed

    def get_goal(self, goal_id: str) -> SavingsGoal | None:
        """Get a goal by ID."""
        return next((g for g in self._goals if g.id == goal_id), None)

    def get_goal_by_name(self, name: str) -> SavingsGoal | None:
        """Get a goal by name."""
        return next((g for g in self._goals if g.name.lower() == name.lower()), None)

    def list_goals(
        self,
        include_completed: bool = False,
        category: GoalCategory | None = None,
    ) -> list[SavingsGoal]:
        """List goals with optional filtering.

        Args:
            include_completed: Include completed goals.
            category: Filter by category.
        """
        goals = self._goals.copy()

        if not include_completed:
            goals = [g for g in goals if not g.is_completed]

        if category:
            goals = [g for g in goals if g.category == category]

        return sorted(goals, key=lambda g: (g.priority, g.name))

    def add_contribution(
        self,
        goal_id: str,
        amount: Decimal | float | str,
    ) -> SavingsGoal | None:
        """Add contribution to a goal."""
        goal = self.get_goal(goal_id)
        if goal:
            goal.add_contribution(amount)
            self._save_if_configured()
        return goal

    def get_total_saved(self) -> Decimal:
        """Get total amount saved across all goals."""
        return sum((g.current_amount for g in self._goals), Decimal("0"))

    def get_total_target(self) -> Decimal:
        """Get total target amount across all goals."""
        return sum((g.target_amount for g in self._goals), Decimal("0"))

    def get_goals_summary(self) -> dict[str, Any]:
        """Get summary of all goals."""
        active_goals = [g for g in self._goals if not g.is_completed]
        completed_goals = [g for g in self._goals if g.is_completed]

        return {
            "total_goals": len(self._goals),
            "active_goals": len(active_goals),
            "completed_goals": len(completed_goals),
            "total_saved": self.get_total_saved(),
            "total_target": self.get_total_target(),
            "overall_progress": (
                (self.get_total_saved() / self.get_total_target() * 100).quantize(
                    Decimal("0.1")
                )
                if self.get_total_target() > 0
                else Decimal("0")
            ),
            "goals_by_status": {
                status.value: len([g for g in self._goals if g.status == status])
                for status in GoalStatus
            },
        }

    # Debt Payoff

    def set_debt_plan(self, plan: DebtPayoffPlan) -> None:
        """Set the debt payoff plan."""
        self._debt_plan = plan
        self._save_if_configured()

    def get_debt_plan(self) -> DebtPayoffPlan | None:
        """Get the current debt payoff plan."""
        return self._debt_plan

    def add_debt(self, debt: Debt) -> None:
        """Add a debt to the payoff plan."""
        if not self._debt_plan:
            self._debt_plan = DebtPayoffPlan(method=DebtPayoffMethod.AVALANCHE)
        self._debt_plan.debts.append(debt)
        self._save_if_configured()

    def remove_debt(self, debt_id: str) -> bool:
        """Remove a debt by ID."""
        if not self._debt_plan:
            return False
        original_len = len(self._debt_plan.debts)
        self._debt_plan.debts = [d for d in self._debt_plan.debts if d.id != debt_id]
        removed = len(self._debt_plan.debts) < original_len
        if removed:
            self._save_if_configured()
        return removed

    def make_debt_payment(
        self,
        debt_id: str,
        amount: Decimal | float | str,
    ) -> Debt | None:
        """Make payment on a debt."""
        if not self._debt_plan:
            return None
        debt = next((d for d in self._debt_plan.debts if d.id == debt_id), None)
        if debt:
            debt.make_payment(amount)
            self._save_if_configured()
        return debt

    def get_debt_summary(self) -> dict[str, Any]:
        """Get summary of debt payoff plan."""
        if not self._debt_plan:
            return {
                "has_plan": False,
                "total_debt": Decimal("0"),
                "debts": [],
            }

        plan = self._debt_plan
        return {
            "has_plan": True,
            "method": plan.method.value,
            "total_debt": plan.total_debt,
            "total_minimum": plan.total_minimum_payment,
            "extra_payment": plan.extra_payment,
            "monthly_payment": plan.monthly_payment,
            "months_to_payoff": plan.months_to_payoff,
            "total_interest": plan.total_interest_paid,
            "interest_saved": plan.interest_saved_vs_minimum(),
            "debts": [
                {
                    "id": d.id,
                    "name": d.name,
                    "balance": d.current_balance,
                    "rate": d.interest_rate,
                    "minimum": d.minimum_payment,
                    "progress": d.progress_percent,
                }
                for d in plan.get_ordered_debts()
            ],
        }

    # Persistence

    def load(self, path: Path | str | None = None) -> None:
        """Load goals from JSON file."""
        path = Path(path) if path else self.data_path
        if path is None or not path.exists():
            return

        with open(path) as f:
            data = json.load(f)

        self._goals = [SavingsGoal.from_dict(g) for g in data.get("savings_goals", [])]

        if data.get("debt_plan"):
            self._debt_plan = DebtPayoffPlan.from_dict(data["debt_plan"])

    def save(self, path: Path | str | None = None) -> Path:
        """Save goals to JSON file."""
        path = Path(path) if path else self.data_path
        if path is None:
            raise ValueError("No data path specified")

        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "savings_goals": [g.to_dict() for g in self._goals],
            "debt_plan": self._debt_plan.to_dict() if self._debt_plan else None,
            "summary": {
                "goals": self.get_goals_summary(),
                "debt": self.get_debt_summary(),
            },
            "last_updated": date.today().isoformat(),
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        return path

    def _save_if_configured(self) -> None:
        """Save if data path is set."""
        if self.data_path:
            self.save()


# Convenience functions


def create_emergency_fund(
    months: int = 6,
    monthly_expenses: Decimal | float | str = 0,
    **kwargs: Any,
) -> SavingsGoal:
    """Create an emergency fund goal.

    Args:
        months: Months of expenses to save (default 6).
        monthly_expenses: Monthly expense amount.
        **kwargs: Additional goal parameters.
    """
    monthly = Decimal(str(monthly_expenses))
    target = monthly * months

    return SavingsGoal.create(
        name=f"{months}-Month Emergency Fund",
        target_amount=target,
        category=GoalCategory.EMERGENCY_FUND,
        notes=f"Target: {months} months of expenses (${monthly}/month)",
        **kwargs,
    )


def create_debt_payoff_plan(
    debts: list[dict[str, Any]],
    method: DebtPayoffMethod = DebtPayoffMethod.AVALANCHE,
    extra_payment: Decimal | float | str = 0,
) -> DebtPayoffPlan:
    """Create a debt payoff plan from debt definitions.

    Args:
        debts: List of debt dictionaries with name, balance, rate, minimum.
        method: Payoff method (snowball or avalanche).
        extra_payment: Extra monthly payment.

    Example:
        >>> plan = create_debt_payoff_plan([
        ...     {"name": "Credit Card", "balance": 5000, "rate": 0.18, "minimum": 100},
        ...     {"name": "Car Loan", "balance": 15000, "rate": 0.06, "minimum": 300},
        ... ], extra_payment=200)
    """
    debt_objects = [
        Debt.create(
            name=d["name"],
            balance=d["balance"],
            interest_rate=d["rate"],
            minimum_payment=d["minimum"],
            creditor=d.get("creditor", ""),
        )
        for d in debts
    ]

    return DebtPayoffPlan(
        method=method,
        extra_payment=Decimal(str(extra_payment)),
        debts=debt_objects,
    )


def compare_payoff_methods(
    debts: list[dict[str, Any]],
    extra_payment: Decimal | float | str = 0,
) -> dict[str, Any]:
    """Compare snowball vs avalanche methods.

    Args:
        debts: List of debt dictionaries.
        extra_payment: Extra monthly payment.

    Returns:
        Comparison of both methods with months and interest.
    """
    snowball = create_debt_payoff_plan(debts, DebtPayoffMethod.SNOWBALL, extra_payment)
    avalanche = create_debt_payoff_plan(
        debts, DebtPayoffMethod.AVALANCHE, extra_payment
    )

    return {
        "snowball": {
            "method": "Smallest Balance First",
            "months": snowball.months_to_payoff,
            "total_interest": snowball.total_interest_paid,
        },
        "avalanche": {
            "method": "Highest Interest First",
            "months": avalanche.months_to_payoff,
            "total_interest": avalanche.total_interest_paid,
        },
        "difference": {
            "months": snowball.months_to_payoff - avalanche.months_to_payoff,
            "interest": snowball.total_interest_paid - avalanche.total_interest_paid,
        },
        "recommendation": (
            "avalanche"
            if avalanche.total_interest_paid < snowball.total_interest_paid
            else "snowball"
        ),
    }
