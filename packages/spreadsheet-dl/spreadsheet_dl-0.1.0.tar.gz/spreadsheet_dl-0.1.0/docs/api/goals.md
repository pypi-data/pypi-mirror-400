# Goals Module

## Overview

The goals module implements comprehensive financial goal tracking including savings goals and debt payoff planning. It supports multiple goal types, progress tracking, debt payoff strategies (snowball/avalanche), and provides detailed payment schedules and interest calculations.

**Key Features:**

- Savings goal tracking with progress monitoring
- Debt payoff planning with snowball and avalanche strategies
- Automatic status determination (on track, behind, ahead)
- Payment schedule generation
- Interest calculation and savings projections
- Goal and debt CRUD operations
- JSON persistence
- Multiple goal categories (emergency fund, vacation, etc.)
- Debt payment simulation and comparison tools

**Use Cases:**

- Track savings goals with target dates
- Plan debt payoff strategies
- Compare snowball vs avalanche methods
- Monitor goal progress automatically
- Calculate projected completion dates
- Generate payment schedules
- Estimate interest savings

## Enums

### GoalCategory

Categories for financial goals.

```python
class GoalCategory(Enum):
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
```

### GoalStatus

Calculated status of a goal based on progress.

```python
class GoalStatus(Enum):
    NOT_STARTED = "not_started"    # No contributions yet
    IN_PROGRESS = "in_progress"    # Active with contributions
    ON_TRACK = "on_track"          # Meeting expected timeline
    BEHIND = "behind"              # Behind expected timeline
    AHEAD = "ahead"                # Ahead of expected timeline
    COMPLETED = "completed"        # Goal reached
    PAUSED = "paused"              # Temporarily paused
    CANCELLED = "cancelled"        # Cancelled
```

### DebtPayoffMethod

Debt payoff strategy methods.

```python
class DebtPayoffMethod(Enum):
    SNOWBALL = "snowball"      # Pay smallest balance first
    AVALANCHE = "avalanche"    # Pay highest interest rate first
    CUSTOM = "custom"          # User-defined order
```

## Classes

### SavingsGoal

A savings goal with target amount and progress tracking.

**Attributes:**

- `id` (str): Unique identifier (8-character UUID)
- `name` (str): Goal name/description
- `category` (GoalCategory): Goal category
- `target_amount` (Decimal): Target amount to save
- `current_amount` (Decimal): Amount saved so far (default: 0)
- `target_date` (date | None): Optional deadline
- `monthly_contribution` (Decimal | None): Planned monthly contribution
- `priority` (int): Priority order (1 = highest)
- `notes` (str): Additional notes
- `created_at` (date): Creation date
- `completed_at` (date | None): Completion date
- `is_paused` (bool): Whether goal is paused

**Properties:**

- `remaining` (Decimal): Amount remaining to reach goal
- `progress_percent` (Decimal): Progress as percentage (0-100)
- `is_completed` (bool): Whether target is reached
- `status` (GoalStatus): Calculated status
- `expected_progress_percent` (Decimal): Expected progress based on time
- `days_remaining` (int | None): Days until target date
- `projected_completion_date` (date | None): When goal will be reached
- `monthly_needed_to_reach_target` (Decimal | None): Monthly amount needed

**Methods:**

```python
@classmethod
def create(
    cls,
    name: str,
    target_amount: Decimal | float | str,
    category: GoalCategory = GoalCategory.SAVINGS,
    **kwargs: Any,
) -> SavingsGoal:
    """
    Create a new savings goal with auto-generated ID.

    Args:
        name: Goal name.
        target_amount: Target amount to save.
        category: Goal category.
        **kwargs: Additional goal attributes.

    Returns:
        New SavingsGoal instance.
    """
```

```python
def add_contribution(self, amount: Decimal | float | str) -> Decimal:
    """
    Add a contribution to the goal.

    Automatically marks goal as completed when target is reached.

    Args:
        amount: Contribution amount.

    Returns:
        New current amount.
    """
```

```python
def to_dict(self) -> dict[str, Any]:
    """Convert to dictionary for serialization."""
```

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> SavingsGoal:
    """Create from dictionary."""
```

**Example:**

```python
from spreadsheet_dl.domains.finance.goals import SavingsGoal, GoalCategory
from decimal import Decimal
from datetime import date, timedelta

# Create emergency fund goal
goal = SavingsGoal.create(
    name="Emergency Fund",
    target_amount=10000,
    category=GoalCategory.EMERGENCY_FUND,
    monthly_contribution=500,
    target_date=date.today() + timedelta(days=365)
)

# Add contributions
goal.add_contribution(500)  # Month 1
goal.add_contribution(500)  # Month 2

# Check progress
print(f"Progress: {goal.progress_percent}%")
print(f"Status: {goal.status.value}")
print(f"Remaining: ${goal.remaining}")

# Calculate needed contributions
needed = goal.monthly_needed_to_reach_target
if needed:
    print(f"Need ${needed}/month to reach goal by {goal.target_date}")
```

### Debt

A debt to be paid off with interest tracking.

**Attributes:**

- `id` (str): Unique identifier
- `name` (str): Debt name (e.g., "Credit Card A")
- `creditor` (str): Creditor/lender name
- `original_balance` (Decimal): Original amount owed
- `current_balance` (Decimal): Current amount owed
- `interest_rate` (Decimal): Annual interest rate (0.18 = 18%)
- `minimum_payment` (Decimal): Minimum monthly payment
- `due_day` (int): Day of month payment is due (1-31)
- `notes` (str): Additional notes
- `created_at` (date): Creation date
- `paid_off_at` (date | None): Payoff date

**Properties:**

- `is_paid_off` (bool): Whether debt is paid off
- `monthly_interest` (Decimal): Monthly interest charge
- `progress_percent` (Decimal): Progress towards payoff
- `payoff_months_minimum` (int | None): Months to pay off with minimum only

**Methods:**

```python
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
    """Create a new debt with auto-generated ID."""
```

```python
def make_payment(self, amount: Decimal | float | str) -> Decimal:
    """
    Make a payment on the debt.

    Automatically marks debt as paid off when balance reaches zero.

    Args:
        amount: Payment amount.

    Returns:
        New balance.
    """
```

**Example:**

```python
from spreadsheet_dl.domains.finance.goals import Debt
from decimal import Decimal

# Create credit card debt
debt = Debt.create(
    name="Credit Card",
    balance=5000,
    interest_rate=0.18,    # 18% APR
    minimum_payment=100,
    creditor="Bank XYZ"
)

# Check monthly interest
print(f"Monthly interest: ${debt.monthly_interest}")

# Make payment
new_balance = debt.make_payment(150)
print(f"New balance: ${new_balance}")

# Calculate payoff time
months = debt.payoff_months_minimum
if months:
    print(f"Will pay off in {months} months with minimum payments")
else:
    print("Cannot pay off with minimum payment (interest too high)")
```

### DebtPayoffPlan

A debt payoff plan using snowball or avalanche method.

**Attributes:**

- `method` (DebtPayoffMethod): Payoff strategy
- `extra_payment` (Decimal): Extra monthly payment beyond minimums
- `debts` (list[Debt]): List of debts

**Properties:**

- `total_debt` (Decimal): Total remaining debt
- `total_minimum_payment` (Decimal): Sum of all minimum payments
- `monthly_payment` (Decimal): Total payment including extra
- `months_to_payoff` (int): Months until all debt paid off
- `total_interest_paid` (Decimal): Total interest that will be paid

**Methods:**

```python
def get_ordered_debts(self) -> list[Debt]:
    """
    Get debts in payoff priority order.

    Returns:
        Debts sorted by:
        - SNOWBALL: smallest balance first
        - AVALANCHE: highest interest rate first
        - CUSTOM: current order
    """
```

```python
def calculate_payoff_schedule(self) -> list[dict[str, Any]]:
    """
    Calculate month-by-month payoff schedule.

    Returns:
        List of monthly snapshots with:
        - Month number
        - Date
        - Payments per debt
        - Balances per debt
        - Interest charged per debt
        - Total balance and interest
    """
```

```python
def interest_saved_vs_minimum(self) -> Decimal:
    """
    Calculate interest saved compared to minimum payments only.

    Returns:
        Amount of interest saved by paying extra.
    """
```

**Example:**

```python
from spreadsheet_dl.domains.finance.goals import DebtPayoffPlan, Debt, DebtPayoffMethod

# Create debts
debt1 = Debt.create("Credit Card", balance=5000, interest_rate=0.18, minimum_payment=100)
debt2 = Debt.create("Car Loan", balance=15000, interest_rate=0.06, minimum_payment=300)
debt3 = Debt.create("Personal Loan", balance=3000, interest_rate=0.12, minimum_payment=75)

# Create avalanche plan (highest interest first)
plan = DebtPayoffPlan(
    method=DebtPayoffMethod.AVALANCHE,
    extra_payment=Decimal("200"),
    debts=[debt1, debt2, debt3]
)

# Analyze plan
print(f"Total Debt: ${plan.total_debt:,.2f}")
print(f"Monthly Payment: ${plan.monthly_payment:,.2f}")
print(f"Payoff Time: {plan.months_to_payoff} months")
print(f"Total Interest: ${plan.total_interest_paid:,.2f}")
print(f"Interest Saved: ${plan.interest_saved_vs_minimum():,.2f}")

# Get payment schedule
schedule = plan.calculate_payoff_schedule()
print(f"\nFirst month:")
print(f"  Payments: {schedule[0]['payments']}")
print(f"  Balances: {schedule[0]['balances']}")
```

### GoalManager

Manage savings goals and debt payoff with persistence.

**Methods:**

```python
def __init__(self, data_path: Path | str | None = None) -> None:
    """
    Initialize goal manager.

    Args:
        data_path: Path to JSON file for persistence.
    """
```

**Savings Goal Methods:**

```python
def add_goal(self, goal: SavingsGoal) -> None:
    """Add a savings goal."""
```

```python
def remove_goal(self, goal_id: str) -> bool:
    """Remove a goal by ID."""
```

```python
def get_goal(self, goal_id: str) -> SavingsGoal | None:
    """Get a goal by ID."""
```

```python
def list_goals(
    self,
    include_completed: bool = False,
    category: GoalCategory | None = None,
) -> list[SavingsGoal]:
    """
    List goals with optional filtering.

    Args:
        include_completed: Include completed goals.
        category: Filter by category.

    Returns:
        Filtered goals sorted by priority and name.
    """
```

```python
def add_contribution(
    self,
    goal_id: str,
    amount: Decimal | float | str,
) -> SavingsGoal | None:
    """Add contribution to a goal and save."""
```

```python
def get_goals_summary(self) -> dict[str, Any]:
    """
    Get summary of all goals.

    Returns:
        Dictionary with:
        - total_goals, active_goals, completed_goals counts
        - total_saved, total_target amounts
        - overall_progress percentage
        - goals_by_status breakdown
    """
```

**Debt Methods:**

```python
def set_debt_plan(self, plan: DebtPayoffPlan) -> None:
    """Set the debt payoff plan."""
```

```python
def add_debt(self, debt: Debt) -> None:
    """Add a debt to the payoff plan."""
```

```python
def make_debt_payment(
    self,
    debt_id: str,
    amount: Decimal | float | str,
) -> Debt | None:
    """Make payment on a debt and save."""
```

```python
def get_debt_summary(self) -> dict[str, Any]:
    """
    Get summary of debt payoff plan.

    Returns:
        Dictionary with plan details, totals, and progress.
    """
```

**Persistence:**

```python
def load(self, path: Path | str | None = None) -> None:
    """Load goals from JSON file."""
```

```python
def save(self, path: Path | str | None = None) -> Path:
    """Save goals to JSON file."""
```

**Example:**

```python
from spreadsheet_dl.domains.finance.goals import GoalManager, SavingsGoal, GoalCategory

# Create manager with persistence
manager = GoalManager("goals.json")

# Add savings goals
vacation = SavingsGoal.create(
    name="Hawaii Vacation",
    target_amount=5000,
    category=GoalCategory.VACATION
)
manager.add_goal(vacation)

# Add contribution
manager.add_contribution(vacation.id, 500)

# List active goals
active = manager.list_goals()
for goal in active:
    print(f"{goal.name}: {goal.progress_percent}%")

# Get summary
summary = manager.get_goals_summary()
print(f"Total saved: ${summary['total_saved']}")
print(f"Overall progress: {summary['overall_progress']}%")

# Auto-saves to goals.json
```

## Functions

### create_emergency_fund(months=6, monthly_expenses=0, \*\*kwargs) -> SavingsGoal

Create an emergency fund goal based on monthly expenses.

**Parameters:**

- `months` (int): Months of expenses to save (default: 6)
- `monthly_expenses` (Decimal | float | str): Monthly expense amount
- `**kwargs`: Additional goal parameters

**Returns:**

- SavingsGoal configured as emergency fund

**Example:**

```python
from spreadsheet_dl.domains.finance.goals import create_emergency_fund

# Create 6-month emergency fund
goal = create_emergency_fund(months=6, monthly_expenses=3000)
print(f"Target: ${goal.target_amount}")  # $18,000
```

### create_debt_payoff_plan(debts, method=AVALANCHE, extra_payment=0) -> DebtPayoffPlan

Create a debt payoff plan from debt definitions.

**Parameters:**

- `debts` (list[dict]): List of debt dictionaries with name, balance, rate, minimum
- `method` (DebtPayoffMethod): Payoff method (default: AVALANCHE)
- `extra_payment` (Decimal | float | str): Extra monthly payment

**Returns:**

- DebtPayoffPlan ready for simulation

**Example:**

```python
from spreadsheet_dl.domains.finance.goals import create_debt_payoff_plan

plan = create_debt_payoff_plan([
    {"name": "Credit Card", "balance": 5000, "rate": 0.18, "minimum": 100},
    {"name": "Car Loan", "balance": 15000, "rate": 0.06, "minimum": 300},
], extra_payment=200)

print(f"Payoff time: {plan.months_to_payoff} months")
```

### compare_payoff_methods(debts, extra_payment=0) -> dict[str, Any]

Compare snowball vs avalanche debt payoff methods.

**Parameters:**

- `debts` (list[dict]): List of debt dictionaries
- `extra_payment` (Decimal | float | str): Extra monthly payment

**Returns:**

- Comparison dictionary with both methods and recommendation

**Example:**

```python
from spreadsheet_dl.domains.finance.goals import compare_payoff_methods

debts = [
    {"name": "Card A", "balance": 2000, "rate": 0.20, "minimum": 50},
    {"name": "Card B", "balance": 5000, "rate": 0.15, "minimum": 100},
    {"name": "Loan", "balance": 10000, "rate": 0.08, "minimum": 200},
]

comparison = compare_payoff_methods(debts, extra_payment=300)

print(f"Snowball: {comparison['snowball']['months']} months, "
      f"${comparison['snowball']['total_interest']} interest")
print(f"Avalanche: {comparison['avalanche']['months']} months, "
      f"${comparison['avalanche']['total_interest']} interest")
print(f"Recommendation: {comparison['recommendation']}")
print(f"Difference: {comparison['difference']['months']} months, "
      f"${comparison['difference']['interest']} saved")
```

## Usage Examples

See the comprehensive examples throughout the documentation above. Additional patterns:

### Goal Progress Dashboard

```python
from spreadsheet_dl.domains.finance.goals import GoalManager

manager = GoalManager("goals.json")

print("SAVINGS GOALS DASHBOARD")
print("=" * 70)

for goal in manager.list_goals():
    print(f"\n{goal.name} ({goal.category.value})")
    print(f"  Progress: {goal.progress_percent}% (${goal.current_amount} / ${goal.target_amount})")
    print(f"  Status: {goal.status.value}")

    if goal.target_date:
        print(f"  Target Date: {goal.target_date}")
        print(f"  Days Remaining: {goal.days_remaining}")

    if goal.monthly_needed_to_reach_target:
        print(f"  Monthly Needed: ${goal.monthly_needed_to_reach_target}")
```

### Complete Debt Payoff Workflow

```python
from spreadsheet_dl.domains.finance.goals import GoalManager, compare_payoff_methods, create_debt_payoff_plan, DebtPayoffMethod

# Define debts
debts = [
    {"name": "Credit Card", "balance": 3000, "rate": 0.18, "minimum": 75},
    {"name": "Personal Loan", "balance": 8000, "rate": 0.10, "minimum": 150},
    {"name": "Car Loan", "balance": 12000, "rate": 0.06, "minimum": 250},
]

# Compare methods
comparison = compare_payoff_methods(debts, extra_payment=200)
print(f"Best method: {comparison['recommendation']}")

# Create plan with best method
method = DebtPayoffMethod.AVALANCHE if comparison['recommendation'] == 'avalanche' else DebtPayoffMethod.SNOWBALL
plan = create_debt_payoff_plan(debts, method=method, extra_payment=200)

# Save to manager
manager = GoalManager("goals.json")
manager.set_debt_plan(plan)

# Track payments
schedule = plan.calculate_payoff_schedule()
print(f"\nPayoff Schedule ({len(schedule)} months):")
for i, month in enumerate(schedule[:6], 1):  # Show first 6 months
    print(f"Month {i}: Total Balance ${month['total_balance']}, Interest ${month['total_interest']}")
```

## See Also

- [budget_analyzer](budget_analyzer.md) - Budget analysis
- [reminders](reminders.md) - Bill reminders and payment tracking
