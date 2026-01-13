# Alerts Module

## Overview

The alerts module provides a comprehensive budget monitoring and notification system. It automatically checks budget data against configurable thresholds and generates actionable alerts for various scenarios including budget overruns, category spending limits, large transactions, spending spikes, and savings gaps.

**Key Features:**

- Configurable alert thresholds for overall budget and categories
- Multiple alert types (budget threshold, category overrun, large transactions, etc.)
- Severity levels (INFO, WARNING, CRITICAL)
- Category-specific monitoring with watched categories
- Spending spike detection based on historical averages
- Savings goal progress tracking
- Custom alert rules support
- JSON export and text formatting

**Use Cases:**

- Monitor budget health in real-time
- Detect overspending before it becomes critical
- Track unusual spending patterns
- Alert on large transactions
- Monitor savings goal progress
- Custom budget monitoring rules

## Enums

### AlertSeverity

Alert severity levels for prioritization.

```python
class AlertSeverity(Enum):
    INFO = "info"           # Informational alerts
    WARNING = "warning"     # Warnings requiring attention
    CRITICAL = "critical"   # Critical alerts requiring immediate action
```

### AlertType

Types of budget alerts that can be triggered.

```python
class AlertType(Enum):
    BUDGET_THRESHOLD = "budget_threshold"   # Overall budget threshold exceeded
    CATEGORY_OVER = "category_over"         # Category over budget
    SPENDING_SPIKE = "spending_spike"       # Unusual spending spike detected
    LARGE_TRANSACTION = "large_transaction" # Large single transaction
    DAILY_LIMIT = "daily_limit"             # Daily spending limit exceeded
    SAVINGS_GAP = "savings_gap"             # Behind on savings goal
    TREND_WARNING = "trend_warning"         # Spending trend warning
    CUSTOM = "custom"                       # Custom alert rule
```

## Classes

### Alert

Individual alert instance with details about a triggered condition.

**Attributes:**

- `type` (AlertType): The type of alert
- `severity` (AlertSeverity): Severity level
- `title` (str): Alert title/summary
- `message` (str): Detailed alert message
- `category` (str | None): Associated category (if applicable)
- `amount` (Decimal | None): Associated amount (if applicable)
- `threshold` (float | None): Threshold that triggered the alert
- `timestamp` (datetime): When the alert was created
- `dismissed` (bool): Whether the alert has been dismissed

**Methods:**

```python
def to_dict(self) -> dict[str, Any]:
    """
    Convert alert to dictionary for serialization.

    Returns:
        Dictionary with all alert data, suitable for JSON export.
    """
```

**Example:**

```python
from spreadsheet_dl.domains.finance.alerts import Alert, AlertType, AlertSeverity
from decimal import Decimal
from datetime import datetime

alert = Alert(
    type=AlertType.CATEGORY_OVER,
    severity=AlertSeverity.CRITICAL,
    title="Groceries Over Budget",
    message="Groceries at 105% of budget. $50.00 over.",
    category="Groceries",
    amount=Decimal("550.00"),
    threshold=100.0
)

# Convert to dict for storage/export
alert_data = alert.to_dict()
print(alert_data["message"])  # "Groceries at 105% of budget. $50.00 over."
```

### AlertRule

Configurable alert rule for custom monitoring.

**Attributes:**

- `name` (str): Rule name/description
- `alert_type` (AlertType): Type of alert to generate
- `threshold` (float): Threshold value (percentage or amount)
- `severity` (AlertSeverity): Severity level for triggered alerts
- `category` (str | None): Category to monitor (None = all categories)
- `enabled` (bool): Whether the rule is active

**Example:**

```python
from spreadsheet_dl.domains.finance.alerts import AlertRule, AlertType, AlertSeverity

# Create custom rule to alert at 75% of dining budget
dining_rule = AlertRule(
    name="Dining Budget Watch",
    alert_type=AlertType.CATEGORY_OVER,
    threshold=75.0,
    severity=AlertSeverity.WARNING,
    category="Dining Out",
    enabled=True
)
```

### AlertConfig

Configuration for the alert system with all thresholds and rules.

**Attributes:**

- `budget_warning_threshold` (float): Overall budget warning threshold % (default: 80.0)
- `budget_critical_threshold` (float): Overall budget critical threshold % (default: 95.0)
- `category_warning_threshold` (float): Category warning threshold % (default: 85.0)
- `category_critical_threshold` (float): Category critical threshold % (default: 100.0)
- `large_transaction_threshold` (float): Large transaction amount threshold (default: 200.0)
- `daily_limit` (float | None): Daily spending limit (default: None)
- `spending_spike_multiplier` (float): Spike detection multiplier (default: 2.0)
- `savings_warning_threshold` (float): Savings goal warning % (default: 50.0)
- `watched_categories` (list[str]): Categories to monitor with lower thresholds
- `custom_rules` (list[AlertRule]): Custom alert rules

**Example:**

```python
from spreadsheet_dl.domains.finance.alerts import AlertConfig, AlertRule, AlertType, AlertSeverity

config = AlertConfig(
    budget_warning_threshold=75.0,      # Alert at 75% instead of 80%
    large_transaction_threshold=100.0,  # Alert on transactions over $100
    daily_limit=150.0,                  # Alert if daily spending exceeds $150
    watched_categories=["Dining Out", "Entertainment"],  # Monitor these closely
    custom_rules=[
        AlertRule(
            name="Transportation Alert",
            alert_type=AlertType.CATEGORY_OVER,
            threshold=70.0,
            category="Transportation"
        )
    ]
)
```

### AlertMonitor

Monitor budget data and generate alerts based on configured rules.

**Methods:**

```python
def __init__(
    self,
    analyzer: BudgetAnalyzer,
    config: AlertConfig | None = None,
) -> None:
    """
    Initialize alert monitor.

    Args:
        analyzer: BudgetAnalyzer with loaded budget data.
        config: Alert configuration (uses defaults if None).
    """
```

```python
def check_all(self) -> list[Alert]:
    """
    Run all alert checks and return triggered alerts.

    Performs:
    - Budget threshold checks
    - Category threshold checks
    - Large transaction detection
    - Daily limit monitoring
    - Spending spike detection
    - Savings gap analysis
    - Custom rule evaluation

    Returns:
        List of alerts sorted by severity (Critical first).
    """
```

```python
def get_critical_alerts(self) -> list[Alert]:
    """
    Get only critical severity alerts.

    Returns:
        List of critical alerts.
    """
```

```python
def get_alerts_by_category(self, category: str) -> list[Alert]:
    """
    Get all alerts for a specific category.

    Args:
        category: Category name to filter.

    Returns:
        List of alerts for the category.
    """
```

```python
def to_json(self) -> str:
    """
    Export alerts as JSON string.

    Returns:
        JSON formatted string of all alerts.
    """
```

```python
def format_text(self) -> str:
    """
    Format alerts as human-readable text.

    Returns:
        Formatted text report of all alerts.
    """
```

**Example:**

```python
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer
from spreadsheet_dl.domains.finance.alerts import AlertMonitor, AlertConfig

# Load budget data
analyzer = BudgetAnalyzer("budget.ods")

# Configure alert system
config = AlertConfig(
    budget_warning_threshold=75.0,
    large_transaction_threshold=100.0,
    watched_categories=["Dining Out"]
)

# Create monitor and check for alerts
monitor = AlertMonitor(analyzer, config)
alerts = monitor.check_all()

# Display critical alerts
critical = monitor.get_critical_alerts()
for alert in critical:
    print(f"[CRITICAL] {alert.title}: {alert.message}")

# Format as text report
print(monitor.format_text())

# Export to JSON
json_data = monitor.to_json()

# Get alerts for specific category
dining_alerts = monitor.get_alerts_by_category("Dining Out")
```

## Functions

### check_budget_alerts(ods_path, config=None) -> list[Alert]

Convenience function to check alerts for a budget file.

**Parameters:**

- `ods_path` (Path | str): Path to ODS budget file
- `config` (AlertConfig | None): Alert configuration (optional)

**Returns:**

- List of triggered Alert objects

**Example:**

```python
from spreadsheet_dl.domains.finance.alerts import check_budget_alerts, AlertConfig

# Simple check with defaults
alerts = check_budget_alerts("budget.ods")

# With custom configuration
config = AlertConfig(budget_warning_threshold=70.0)
alerts = check_budget_alerts("budget.ods", config)

for alert in alerts:
    if alert.severity.value == "critical":
        print(f"URGENT: {alert.message}")
```

## Usage Examples

### Basic Alert Monitoring

```python
from spreadsheet_dl.domains.finance.alerts import check_budget_alerts

# Quick alert check
alerts = check_budget_alerts("my_budget.ods")

if alerts:
    print(f"Found {len(alerts)} alerts!")
    for alert in alerts:
        print(f"[{alert.severity.value.upper()}] {alert.title}")
        print(f"  {alert.message}")
else:
    print("No alerts - budget looks good!")
```

### Custom Alert Configuration

```python
from spreadsheet_dl.domains.finance.alerts import (
    AlertMonitor, AlertConfig, AlertRule,
    AlertType, AlertSeverity
)
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

# Custom configuration
config = AlertConfig(
    # Lower thresholds for tighter monitoring
    budget_warning_threshold=70.0,
    budget_critical_threshold=90.0,

    # Alert on transactions over $50
    large_transaction_threshold=50.0,

    # Set daily spending limit
    daily_limit=100.0,

    # Monitor these categories closely
    watched_categories=["Dining Out", "Shopping", "Entertainment"],

    # Custom rules
    custom_rules=[
        AlertRule(
            name="Gas Budget Strict",
            alert_type=AlertType.CATEGORY_OVER,
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            category="Transportation"
        )
    ]
)

# Run with custom config
analyzer = BudgetAnalyzer("budget.ods")
monitor = AlertMonitor(analyzer, config)
alerts = monitor.check_all()
```

### Filtering and Displaying Alerts

```python
from spreadsheet_dl.domains.finance.alerts import AlertMonitor, AlertSeverity
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

analyzer = BudgetAnalyzer("budget.ods")
monitor = AlertMonitor(analyzer)
alerts = monitor.check_all()

# Get critical alerts only
critical = monitor.get_critical_alerts()
print(f"Critical alerts: {len(critical)}")

# Get alerts for specific category
dining_alerts = monitor.get_alerts_by_category("Dining Out")
print(f"Dining alerts: {len(dining_alerts)}")

# Format as text report
text_report = monitor.format_text()
print(text_report)

# Export to JSON for web app
json_data = monitor.to_json()
```

### Integration with Notifications

```python
from spreadsheet_dl.domains.finance.alerts import check_budget_alerts, AlertSeverity

alerts = check_budget_alerts("budget.ods")

# Send notifications for critical alerts
critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]

for alert in critical_alerts:
    # Send email, SMS, or push notification
    send_notification(
        title=alert.title,
        message=alert.message,
        priority="high"
    )

# Log all warnings
warnings = [a for a in alerts if a.severity == AlertSeverity.WARNING]
for alert in warnings:
    log_warning(alert.message)
```

## See Also

- [budget_analyzer](budget_analyzer.md) - Budget analysis engine
- [analytics](analytics.md) - Advanced analytics and insights
- [notifications](../notifications.md) - Notification delivery system
