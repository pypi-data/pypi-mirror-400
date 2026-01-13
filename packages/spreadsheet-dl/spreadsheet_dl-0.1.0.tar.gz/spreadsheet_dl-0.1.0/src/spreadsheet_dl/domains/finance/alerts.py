"""Alerts System - Budget monitoring and notification alerts.

Provides configurable alerts for budget thresholds, spending patterns,
and anomaly detection.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any

from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer, BudgetSummary

if TYPE_CHECKING:
    from pathlib import Path


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of budget alerts."""

    BUDGET_THRESHOLD = "budget_threshold"
    CATEGORY_OVER = "category_over"
    SPENDING_SPIKE = "spending_spike"
    LARGE_TRANSACTION = "large_transaction"
    DAILY_LIMIT = "daily_limit"
    SAVINGS_GAP = "savings_gap"
    TREND_WARNING = "trend_warning"
    CUSTOM = "custom"


@dataclass
class Alert:
    """Individual alert instance."""

    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    category: str | None = None
    amount: Decimal | None = None
    threshold: float | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    dismissed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "type": self.type.value,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "category": self.category,
            "amount": float(self.amount) if self.amount else None,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
            "dismissed": self.dismissed,
        }


@dataclass
class AlertRule:
    """Configurable alert rule."""

    name: str
    alert_type: AlertType
    threshold: float
    severity: AlertSeverity = AlertSeverity.WARNING
    category: str | None = None  # None = applies to all
    enabled: bool = True


@dataclass
class AlertConfig:
    """Configuration for the alert system."""

    # Budget threshold alerts (percent of budget)
    budget_warning_threshold: float = 80.0
    budget_critical_threshold: float = 95.0

    # Category threshold (percent of category budget)
    category_warning_threshold: float = 85.0
    category_critical_threshold: float = 100.0

    # Large transaction threshold (dollar amount)
    large_transaction_threshold: float = 200.0

    # Daily spending limit (dollar amount)
    daily_limit: float | None = None

    # Spending spike detection (multiplier of average)
    spending_spike_multiplier: float = 2.0

    # Savings alert (percent of savings goal)
    savings_warning_threshold: float = 50.0

    # Categories to monitor closely (lower thresholds)
    watched_categories: list[str] = field(default_factory=list)

    # Custom rules
    custom_rules: list[AlertRule] = field(default_factory=list)


class AlertMonitor:
    """Monitor budget data and generate alerts.

    Checks budget data against configurable thresholds and rules
    to generate actionable alerts.
    """

    def __init__(
        self,
        analyzer: BudgetAnalyzer,
        config: AlertConfig | None = None,
    ) -> None:
        """Initialize alert monitor.

        Args:
            analyzer: Budget analyzer with loaded data.
            config: Alert configuration.
        """
        self.analyzer = analyzer
        self.config = config or AlertConfig()
        self._alerts: list[Alert] = []

    def check_all(self) -> list[Alert]:
        """Run all alert checks.

        Returns:
            List of triggered alerts.
        """
        self._alerts = []

        summary = self.analyzer.get_summary()

        # Run checks
        self._check_budget_threshold(summary)
        self._check_category_thresholds(summary)
        self._check_large_transactions()
        self._check_daily_limit()
        self._check_spending_spikes()
        self._check_savings_gap(summary)
        self._check_custom_rules(summary)

        # Sort by severity
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.WARNING: 1,
            AlertSeverity.INFO: 2,
        }
        self._alerts.sort(key=lambda a: severity_order[a.severity])

        return self._alerts

    def _check_budget_threshold(self, summary: BudgetSummary) -> None:
        """Check overall budget thresholds."""
        pct = summary.percent_used

        if pct >= self.config.budget_critical_threshold:
            self._alerts.append(
                Alert(
                    type=AlertType.BUDGET_THRESHOLD,
                    severity=AlertSeverity.CRITICAL,
                    title="Budget Critical",
                    message=f"Overall budget at {pct:.1f}%. "
                    f"Only ${summary.total_remaining:.2f} remaining.",
                    threshold=self.config.budget_critical_threshold,
                )
            )
        elif pct >= self.config.budget_warning_threshold:
            self._alerts.append(
                Alert(
                    type=AlertType.BUDGET_THRESHOLD,
                    severity=AlertSeverity.WARNING,
                    title="Budget Warning",
                    message=f"Overall budget at {pct:.1f}%. "
                    f"${summary.total_remaining:.2f} remaining.",
                    threshold=self.config.budget_warning_threshold,
                )
            )

    def _check_category_thresholds(self, summary: BudgetSummary) -> None:
        """Check category-level thresholds."""
        for cat in summary.categories:
            # Adjust thresholds for watched categories
            if cat.category in self.config.watched_categories:
                warn_thresh = self.config.category_warning_threshold - 10
                crit_thresh = self.config.category_critical_threshold - 5
            else:
                warn_thresh = self.config.category_warning_threshold
                crit_thresh = self.config.category_critical_threshold

            if cat.percent_used >= crit_thresh:
                self._alerts.append(
                    Alert(
                        type=AlertType.CATEGORY_OVER,
                        severity=AlertSeverity.CRITICAL,
                        title=f"{cat.category} Over Budget",
                        message=f"{cat.category} at {cat.percent_used:.1f}% of budget. "
                        f"${abs(cat.remaining):.2f} over.",
                        category=cat.category,
                        amount=cat.actual,
                        threshold=crit_thresh,
                    )
                )
            elif cat.percent_used >= warn_thresh:
                self._alerts.append(
                    Alert(
                        type=AlertType.CATEGORY_OVER,
                        severity=AlertSeverity.WARNING,
                        title=f"{cat.category} Near Limit",
                        message=f"{cat.category} at {cat.percent_used:.1f}% of budget. "
                        f"${cat.remaining:.2f} remaining.",
                        category=cat.category,
                        amount=cat.actual,
                        threshold=warn_thresh,
                    )
                )

    def _check_large_transactions(self) -> None:
        """Check for unusually large transactions."""
        expenses = self.analyzer.expenses
        if expenses.empty:
            return

        threshold = self.config.large_transaction_threshold
        large = expenses[expenses["Amount"] >= threshold]

        for _, row in large.iterrows():
            self._alerts.append(
                Alert(
                    type=AlertType.LARGE_TRANSACTION,
                    severity=AlertSeverity.INFO,
                    title="Large Transaction",
                    message=f"${row['Amount']:.2f} at {row['Description']} "
                    f"on {row['Date'].strftime('%Y-%m-%d') if hasattr(row['Date'], 'strftime') else row['Date']}.",
                    category=row.get("Category"),
                    amount=Decimal(str(row["Amount"])),
                    threshold=threshold,
                )
            )

    def _check_daily_limit(self) -> None:
        """Check daily spending limits."""
        if self.config.daily_limit is None:
            return

        expenses = self.analyzer.expenses
        if expenses.empty or "Date" not in expenses.columns:
            return

        expenses = expenses.copy()
        daily = expenses.groupby(expenses["Date"].dt.date)["Amount"].sum()

        for day, total in daily.items():
            if total > self.config.daily_limit:
                self._alerts.append(
                    Alert(
                        type=AlertType.DAILY_LIMIT,
                        severity=AlertSeverity.WARNING,
                        title="Daily Limit Exceeded",
                        message=f"Spent ${total:.2f} on {day}, "
                        f"exceeding ${self.config.daily_limit:.2f} limit.",
                        amount=Decimal(str(total)),
                        threshold=self.config.daily_limit,
                    )
                )

    def _check_spending_spikes(self) -> None:
        """Detect unusual spending spikes."""
        expenses = self.analyzer.expenses
        if expenses.empty or len(expenses) < 5:
            return

        # Calculate average transaction
        avg = expenses["Amount"].mean()
        spike_threshold = avg * self.config.spending_spike_multiplier

        # Find recent spikes (last 7 days)
        recent = (
            expenses[expenses["Date"] >= (datetime.now() - timedelta(days=7))]
            if "Date" in expenses.columns
            else expenses
        )

        spikes = recent[recent["Amount"] >= spike_threshold]

        for _, row in spikes.iterrows():
            ratio = row["Amount"] / avg
            self._alerts.append(
                Alert(
                    type=AlertType.SPENDING_SPIKE,
                    severity=AlertSeverity.WARNING
                    if ratio < 3
                    else AlertSeverity.CRITICAL,
                    title="Spending Spike Detected",
                    message=f"${row['Amount']:.2f} is {ratio:.1f}x your average transaction "
                    f"(${avg:.2f}).",
                    category=row.get("Category"),
                    amount=Decimal(str(row["Amount"])),
                    threshold=spike_threshold,
                )
            )

    def _check_savings_gap(self, summary: BudgetSummary) -> None:
        """Check if savings goal is on track."""
        savings = next(
            (c for c in summary.categories if c.category == "Savings"),
            None,
        )

        if savings is None:
            return

        pct_saved = savings.percent_used

        # Calculate expected progress based on day of month
        today = date.today()
        import calendar

        days_in_month = calendar.monthrange(today.year, today.month)[1]
        expected_pct = (today.day / days_in_month) * 100

        # Check if behind on savings
        if pct_saved < expected_pct * 0.5:
            gap = savings.budget - savings.actual
            self._alerts.append(
                Alert(
                    type=AlertType.SAVINGS_GAP,
                    severity=AlertSeverity.WARNING,
                    title="Savings Behind Target",
                    message=f"Savings at {pct_saved:.1f}% of goal "
                    f"(expected ~{expected_pct:.0f}%). "
                    f"${gap:.2f} to reach target.",
                    category="Savings",
                    amount=savings.actual,
                    threshold=self.config.savings_warning_threshold,
                )
            )

    def _check_custom_rules(self, summary: BudgetSummary) -> None:
        """Check custom alert rules."""
        for rule in self.config.custom_rules:
            if not rule.enabled:
                continue

            if rule.alert_type == AlertType.BUDGET_THRESHOLD:
                if summary.percent_used >= rule.threshold:
                    self._alerts.append(
                        Alert(
                            type=rule.alert_type,
                            severity=rule.severity,
                            title=rule.name,
                            message=f"Budget at {summary.percent_used:.1f}% "
                            f"(threshold: {rule.threshold}%).",
                            threshold=rule.threshold,
                        )
                    )
            elif rule.alert_type == AlertType.CATEGORY_OVER and rule.category:
                cat = next(
                    (c for c in summary.categories if c.category == rule.category),
                    None,
                )
                if cat and cat.percent_used >= rule.threshold:
                    self._alerts.append(
                        Alert(
                            type=rule.alert_type,
                            severity=rule.severity,
                            title=rule.name,
                            message=f"{rule.category} at {cat.percent_used:.1f}% "
                            f"(threshold: {rule.threshold}%).",
                            category=rule.category,
                            amount=cat.actual,
                            threshold=rule.threshold,
                        )
                    )

    def get_critical_alerts(self) -> list[Alert]:
        """Get only critical alerts."""
        return [a for a in self._alerts if a.severity == AlertSeverity.CRITICAL]

    def get_alerts_by_category(self, category: str) -> list[Alert]:
        """Get alerts for a specific category."""
        return [a for a in self._alerts if a.category == category]

    def to_json(self) -> str:
        """Export alerts as JSON."""
        return json.dumps([a.to_dict() for a in self._alerts], indent=2)

    def format_text(self) -> str:
        """Format alerts as text for display."""
        if not self._alerts:
            return "No alerts at this time."

        lines = []
        lines.append("=" * 60)
        lines.append(f"BUDGET ALERTS ({len(self._alerts)} total)")
        lines.append("=" * 60)

        for alert in self._alerts:
            icon = {
                AlertSeverity.CRITICAL: "[!!!]",
                AlertSeverity.WARNING: "[!]",
                AlertSeverity.INFO: "[i]",
            }[alert.severity]

            lines.append(f"\n{icon} {alert.title}")
            lines.append(f"    {alert.message}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


def check_budget_alerts(
    ods_path: Path | str,
    config: AlertConfig | None = None,
) -> list[Alert]:
    """Convenience function to check alerts for a budget file.

    Args:
        ods_path: Path to ODS budget file.
        config: Alert configuration.

    Returns:
        List of triggered alerts.
    """
    analyzer = BudgetAnalyzer(ods_path)
    monitor = AlertMonitor(analyzer, config)
    return monitor.check_all()
