"""Notification System Module.

Implements IR-NOTIF-001: Alert Notifications.
Provides email notifications, ntfy.sh integration, and notification templates.
"""

from __future__ import annotations

import json
import smtplib
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from decimal import Decimal


class NotificationPriority(Enum):
    """Priority level for notifications."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationType(Enum):
    """Types of notifications."""

    BILL_DUE = "bill_due"
    BILL_OVERDUE = "bill_overdue"
    BUDGET_WARNING = "budget_warning"
    BUDGET_EXCEEDED = "budget_exceeded"
    GOAL_PROGRESS = "goal_progress"
    GOAL_COMPLETED = "goal_completed"
    LOW_BALANCE = "low_balance"
    RECURRING_REMINDER = "recurring_reminder"
    WEEKLY_SUMMARY = "weekly_summary"
    MONTHLY_SUMMARY = "monthly_summary"
    CUSTOM = "custom"


@dataclass
class Notification:
    """A notification to be sent.

    Attributes:
        type: Type of notification.
        title: Notification title.
        message: Notification body.
        priority: Priority level.
        data: Additional data for templating.
        created_at: When notification was created.
        sent_at: When notification was sent.
        channels: Channels to send through.
    """

    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: datetime | None = None
    channels: list[str] = field(default_factory=lambda: ["email"])

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "priority": self.priority.value,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "channels": self.channels,
        }


class NotificationChannel(Protocol):
    """Protocol for notification channels."""

    def send(self, notification: Notification) -> bool:
        """Send a notification. Returns True on success."""
        ...

    def is_configured(self) -> bool:
        """Check if channel is properly configured."""
        ...


@dataclass
class EmailConfig:
    """Email configuration."""

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    username: str = ""
    password: str = ""
    from_address: str = ""
    to_address: str = ""
    use_tls: bool = True


class EmailChannel:
    """Send notifications via email.

    Supports SMTP with TLS for secure email delivery.
    """

    def __init__(self, config: EmailConfig) -> None:
        """Initialize email channel."""
        self.config = config

    def is_configured(self) -> bool:
        """Check if email is configured."""
        return bool(
            self.config.smtp_host
            and self.config.username
            and self.config.password
            and self.config.to_address
        )

    def send(self, notification: Notification) -> bool:
        """Send notification via email."""
        if not self.is_configured():
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = self._format_subject(notification)
            msg["From"] = self.config.from_address or self.config.username
            msg["To"] = self.config.to_address

            # Plain text version
            text_body = self._format_text_body(notification)
            msg.attach(MIMEText(text_body, "plain"))

            # HTML version
            html_body = self._format_html_body(notification)
            msg.attach(MIMEText(html_body, "html"))

            # Send
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.username, self.config.password)
                server.send_message(msg)

            return True

        except (smtplib.SMTPException, OSError):
            # SMTP errors (auth, connection, send) or network errors
            # Intentionally suppress for graceful degradation - notifications are non-critical
            return False

    def _format_subject(self, notification: Notification) -> str:
        """Format email subject."""
        priority_prefix = {
            NotificationPriority.URGENT: "[URGENT] ",
            NotificationPriority.HIGH: "[!] ",
            NotificationPriority.NORMAL: "",
            NotificationPriority.LOW: "",
        }
        return f"{priority_prefix[notification.priority]}SpreadsheetDL: {notification.title}"

    def _format_text_body(self, notification: Notification) -> str:
        """Format plain text body."""
        lines = [
            notification.title,
            "=" * len(notification.title),
            "",
            notification.message,
            "",
        ]

        if notification.data:
            lines.append("Details:")
            for key, value in notification.data.items():
                lines.append(f"  - {key}: {value}")

        lines.extend(
            [
                "",
                "---",
                f"Sent by SpreadsheetDL at {notification.created_at.strftime('%Y-%m-%d %H:%M')}",
            ]
        )

        return "\n".join(lines)

    def _format_html_body(self, notification: Notification) -> str:
        """Format HTML body."""
        priority_colors = {
            NotificationPriority.URGENT: "#dc3545",
            NotificationPriority.HIGH: "#fd7e14",
            NotificationPriority.NORMAL: "#0d6efd",
            NotificationPriority.LOW: "#6c757d",
        }
        color = priority_colors[notification.priority]

        data_html = ""
        if notification.data:
            items = "".join(
                f"<li><strong>{k}:</strong> {v}</li>"
                for k, v in notification.data.items()
            )
            data_html = f"<h3>Details</h3><ul>{items}</ul>"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {color}; color: white; padding: 15px; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 5px 5px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">{notification.title}</h2>
                </div>
                <div class="content">
                    <p>{notification.message}</p>
                    {data_html}
                </div>
                <div class="footer">
                    <p>Sent by SpreadsheetDL at {notification.created_at.strftime("%Y-%m-%d %H:%M")}</p>
                </div>
            </div>
        </body>
        </html>
        """


@dataclass
class NtfyConfig:
    """Ntfy.sh configuration."""

    server: str = "https://ntfy.sh"
    topic: str = ""
    access_token: str = ""  # Optional authentication


class NtfyChannel:
    """Send notifications via ntfy.sh.

    A simple HTTP-based pub-sub notification service.
    See: https://ntfy.sh
    """

    def __init__(self, config: NtfyConfig) -> None:
        """Initialize ntfy channel."""
        self.config = config

    def is_configured(self) -> bool:
        """Check if ntfy is configured."""
        return bool(self.config.server and self.config.topic)

    def send(self, notification: Notification) -> bool:
        """Send notification via ntfy."""
        if not self.is_configured():
            return False

        try:
            url = f"{self.config.server}/{self.config.topic}"

            # Map priority
            priority_map = {
                NotificationPriority.LOW: "2",
                NotificationPriority.NORMAL: "3",
                NotificationPriority.HIGH: "4",
                NotificationPriority.URGENT: "5",
            }

            headers = {
                "Title": notification.title,
                "Priority": priority_map[notification.priority],
                "Tags": self._get_tags(notification),
            }

            if self.config.access_token:
                headers["Authorization"] = f"Bearer {self.config.access_token}"

            data = notification.message.encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers)

            with urllib.request.urlopen(req, timeout=10) as response:
                return bool(response.status == 200)

        except (urllib.error.URLError, OSError):
            # HTTP errors or network errors
            # Intentionally suppress for graceful degradation - notifications are non-critical
            return False

    def _get_tags(self, notification: Notification) -> str:
        """Get emoji tags for notification type."""
        tag_map = {
            NotificationType.BILL_DUE: "bell,dollar",
            NotificationType.BILL_OVERDUE: "warning,dollar",
            NotificationType.BUDGET_WARNING: "warning,chart_with_downwards_trend",
            NotificationType.BUDGET_EXCEEDED: "x,chart_with_downwards_trend",
            NotificationType.GOAL_PROGRESS: "dart,chart_with_upwards_trend",
            NotificationType.GOAL_COMPLETED: "tada,white_check_mark",
            NotificationType.LOW_BALANCE: "warning,bank",
            NotificationType.RECURRING_REMINDER: "repeat,calendar",
            NotificationType.WEEKLY_SUMMARY: "calendar,memo",
            NotificationType.MONTHLY_SUMMARY: "calendar,memo",
            NotificationType.CUSTOM: "bell",
        }
        return tag_map.get(notification.type, "bell")


class NotificationManager:
    """Manage and send notifications through multiple channels.

    Supports email, ntfy.sh, and custom notification channels.
    """

    def __init__(
        self,
        email_config: EmailConfig | None = None,
        ntfy_config: NtfyConfig | None = None,
        log_path: Path | str | None = None,
    ) -> None:
        """Initialize notification manager.

        Args:
            email_config: Email configuration.
            ntfy_config: Ntfy.sh configuration.
            log_path: Path to notification log file.
        """
        self._channels: dict[str, NotificationChannel] = {}
        self._log_path = Path(log_path) if log_path else None
        self._history: list[Notification] = []

        if email_config:
            self._channels["email"] = EmailChannel(email_config)

        if ntfy_config:
            self._channels["ntfy"] = NtfyChannel(ntfy_config)

    def add_channel(self, name: str, channel: NotificationChannel) -> None:
        """Add a notification channel."""
        self._channels[name] = channel

    def remove_channel(self, name: str) -> bool:
        """Remove a notification channel."""
        if name in self._channels:
            del self._channels[name]
            return True
        return False

    def list_channels(self) -> list[dict[str, Any]]:
        """List configured channels."""
        return [
            {
                "name": name,
                "type": type(channel).__name__,
                "configured": channel.is_configured(),
            }
            for name, channel in self._channels.items()
        ]

    def send(
        self,
        notification: Notification,
        channels: list[str] | None = None,
    ) -> dict[str, bool]:
        """Send a notification through specified channels.

        Args:
            notification: Notification to send.
            channels: Channels to use (defaults to notification's channels).

        Returns:
            Dict mapping channel name to success status.
        """
        channels_to_use = channels or notification.channels
        results = {}

        for channel_name in channels_to_use:
            if channel_name in self._channels:
                channel = self._channels[channel_name]
                if channel.is_configured():
                    results[channel_name] = channel.send(notification)
                else:
                    results[channel_name] = False
            else:
                results[channel_name] = False

        if any(results.values()):
            notification.sent_at = datetime.now()

        self._history.append(notification)
        self._save_log()

        return results

    def send_all(self, notification: Notification) -> dict[str, bool]:
        """Send notification through all configured channels."""
        return self.send(notification, list(self._channels.keys()))

    def get_history(
        self,
        limit: int = 100,
        notification_type: NotificationType | None = None,
    ) -> list[Notification]:
        """Get notification history."""
        history = self._history.copy()

        if notification_type:
            history = [n for n in history if n.type == notification_type]

        return history[-limit:]

    def _save_log(self) -> None:
        """Save notification log."""
        if not self._log_path:
            return

        self._log_path.parent.mkdir(parents=True, exist_ok=True)

        log_data = {
            "notifications": [n.to_dict() for n in self._history[-1000:]],
            "last_updated": datetime.now().isoformat(),
        }

        with open(self._log_path, "w") as f:
            json.dump(log_data, f, indent=2)


# Notification Templates


class NotificationTemplates:
    """Pre-built notification templates."""

    @staticmethod
    def bill_due(
        bill_name: str,
        amount: Decimal | float,
        due_date: date,
        auto_pay: bool = False,
    ) -> Notification:
        """Create bill due notification."""
        days = (due_date - date.today()).days
        message = f"${amount} due to {bill_name}"

        if days == 0:
            message = f"Bill due TODAY: {message}"
            priority = NotificationPriority.HIGH
        elif days == 1:
            message = f"Bill due TOMORROW: {message}"
            priority = NotificationPriority.HIGH
        else:
            message = f"Bill due in {days} days: {message}"
            priority = NotificationPriority.NORMAL

        if auto_pay:
            message += " (auto-pay enabled)"

        return Notification(
            type=NotificationType.BILL_DUE,
            title=f"Bill Reminder: {bill_name}",
            message=message,
            priority=priority,
            data={
                "bill_name": bill_name,
                "amount": str(amount),
                "due_date": due_date.isoformat(),
                "days_until_due": days,
                "auto_pay": auto_pay,
            },
        )

    @staticmethod
    def bill_overdue(
        bill_name: str,
        amount: Decimal | float,
        due_date: date,
        days_overdue: int,
    ) -> Notification:
        """Create overdue bill notification."""
        return Notification(
            type=NotificationType.BILL_OVERDUE,
            title=f"OVERDUE: {bill_name}",
            message=f"Bill is {days_overdue} days overdue! ${amount} was due on {due_date.isoformat()}",
            priority=NotificationPriority.URGENT,
            data={
                "bill_name": bill_name,
                "amount": str(amount),
                "due_date": due_date.isoformat(),
                "days_overdue": days_overdue,
            },
        )

    @staticmethod
    def budget_warning(
        category: str,
        spent: Decimal | float,
        budget: Decimal | float,
        percent_used: float,
    ) -> Notification:
        """Create budget warning notification."""
        remaining = float(budget) - float(spent)
        return Notification(
            type=NotificationType.BUDGET_WARNING,
            title=f"Budget Alert: {category}",
            message=f"You've used {percent_used:.0f}% of your {category} budget. "
            f"${remaining:.2f} remaining.",
            priority=NotificationPriority.HIGH
            if percent_used >= 90
            else NotificationPriority.NORMAL,
            data={
                "category": category,
                "spent": str(spent),
                "budget": str(budget),
                "remaining": f"{remaining:.2f}",
                "percent_used": f"{percent_used:.1f}",
            },
        )

    @staticmethod
    def budget_exceeded(
        category: str,
        spent: Decimal | float,
        budget: Decimal | float,
        over_amount: Decimal | float,
    ) -> Notification:
        """Create budget exceeded notification."""
        return Notification(
            type=NotificationType.BUDGET_EXCEEDED,
            title=f"Budget Exceeded: {category}",
            message=f"You've exceeded your {category} budget by ${over_amount}! "
            f"Budget: ${budget}, Spent: ${spent}",
            priority=NotificationPriority.URGENT,
            data={
                "category": category,
                "spent": str(spent),
                "budget": str(budget),
                "over_amount": str(over_amount),
            },
        )

    @staticmethod
    def goal_progress(
        goal_name: str,
        current: Decimal | float,
        target: Decimal | float,
        percent_complete: float,
    ) -> Notification:
        """Create goal progress notification."""
        milestones = [25, 50, 75, 90]
        milestone = None
        for m in milestones:
            if percent_complete >= m:
                milestone = m

        message = f"You've saved ${current} of ${target} ({percent_complete:.0f}%)"
        if milestone:
            message = f"Milestone reached! {milestone}% complete. {message}"

        return Notification(
            type=NotificationType.GOAL_PROGRESS,
            title=f"Goal Update: {goal_name}",
            message=message,
            priority=NotificationPriority.LOW,
            data={
                "goal_name": goal_name,
                "current": str(current),
                "target": str(target),
                "percent_complete": f"{percent_complete:.1f}",
                "milestone": milestone,
            },
        )

    @staticmethod
    def goal_completed(
        goal_name: str,
        target: Decimal | float,
        days_taken: int,
    ) -> Notification:
        """Create goal completed notification."""
        return Notification(
            type=NotificationType.GOAL_COMPLETED,
            title=f"Goal Achieved: {goal_name}!",
            message=f"Congratulations! You've reached your ${target} goal in {days_taken} days!",
            priority=NotificationPriority.HIGH,
            data={
                "goal_name": goal_name,
                "target": str(target),
                "days_taken": days_taken,
            },
        )

    @staticmethod
    def weekly_summary(
        week_total: Decimal | float,
        top_categories: list[tuple[str, Decimal | float]],
        budget_status: str,
    ) -> Notification:
        """Create weekly spending summary."""
        categories_text = ", ".join(f"{cat}: ${amt}" for cat, amt in top_categories[:3])
        return Notification(
            type=NotificationType.WEEKLY_SUMMARY,
            title="Weekly Spending Summary",
            message=f"This week you spent ${week_total}. "
            f"Top categories: {categories_text}. "
            f"Budget status: {budget_status}",
            priority=NotificationPriority.LOW,
            data={
                "week_total": str(week_total),
                "top_categories": [
                    {"category": cat, "amount": str(amt)} for cat, amt in top_categories
                ],
                "budget_status": budget_status,
            },
        )

    @staticmethod
    def monthly_summary(
        month: str,
        total_spent: Decimal | float,
        total_budget: Decimal | float,
        savings: Decimal | float,
        over_budget_categories: list[str],
    ) -> Notification:
        """Create monthly spending summary."""
        status = "under" if total_spent <= total_budget else "over"
        diff = abs(float(total_budget) - float(total_spent))

        message = (
            f"In {month}, you spent ${total_spent} (${diff:.2f} {status} budget). "
        )
        if savings > 0:
            message += f"You saved ${savings}. "
        if over_budget_categories:
            message += f"Over budget in: {', '.join(over_budget_categories)}"

        return Notification(
            type=NotificationType.MONTHLY_SUMMARY,
            title=f"Monthly Summary: {month}",
            message=message,
            priority=NotificationPriority.LOW,
            data={
                "month": month,
                "total_spent": str(total_spent),
                "total_budget": str(total_budget),
                "savings": str(savings),
                "status": status,
                "over_budget_categories": over_budget_categories,
            },
        )


# Configuration from file


def load_notification_config(
    config_path: Path | str,
) -> tuple[EmailConfig | None, NtfyConfig | None]:
    """Load notification configuration from file.

    Args:
        config_path: Path to config file.

    Returns:
        Tuple of (EmailConfig, NtfyConfig).
    """
    config_path = Path(config_path)
    if not config_path.exists():
        return None, None

    with open(config_path) as f:
        data = json.load(f)

    email_config = None
    if email_data := data.get("email"):
        email_config = EmailConfig(
            smtp_host=email_data.get("smtp_host", "smtp.gmail.com"),
            smtp_port=email_data.get("smtp_port", 587),
            username=email_data.get("username", ""),
            password=email_data.get("password", ""),
            from_address=email_data.get("from_address", ""),
            to_address=email_data.get("to_address", ""),
            use_tls=email_data.get("use_tls", True),
        )

    ntfy_config = None
    if ntfy_data := data.get("ntfy"):
        ntfy_config = NtfyConfig(
            server=ntfy_data.get("server", "https://ntfy.sh"),
            topic=ntfy_data.get("topic", ""),
            access_token=ntfy_data.get("access_token", ""),
        )

    return email_config, ntfy_config
