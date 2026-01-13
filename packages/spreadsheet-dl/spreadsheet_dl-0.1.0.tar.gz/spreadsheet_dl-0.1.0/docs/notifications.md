# Notification System

## Overview

The SpreadsheetDL notification system provides a flexible framework for delivering alerts, reminders, and status updates through multiple channels. It supports email, ntfy.sh push notifications, webhooks, and custom notification handlers.

**Key Features:**

- Multiple delivery channels (email, push, webhook, custom)
- Priority levels for urgent vs routine notifications
- Scheduled delivery with rate limiting
- Template-based message formatting
- Delivery confirmation and retry logic
- Integration with alerts and reminders modules
- Async/batch notification support

**Use Cases:**

- Budget alert notifications via email or push
- Bill payment reminders to mobile devices
- Spending threshold warnings
- Monthly report delivery
- Custom workflow notifications
- System status updates

## Architecture

```
┌────────────────────────────────────────────────┐
│         NotificationManager                     │
│  - Handles routing and delivery                │
│  - Manages channels and templates              │
│  - Implements retry logic                      │
└────────────┬───────────────────────────────────┘
             │
             ├──> EmailChannel (SMTP)
             ├──> PushChannel (ntfy.sh)
             ├──> WebhookChannel (HTTP)
             └──> CustomChannel (user-defined)
```

## Core Classes

### NotificationManager

Central manager for all notification operations.

**Initialization:**

```python
from spreadsheet_dl import NotificationManager, NotificationConfig

config = NotificationConfig(
    email_enabled=True,
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_user="your-email@gmail.com",
    smtp_password="app-password",
    push_enabled=True,
    ntfy_topic="budget-alerts"
)

manager = NotificationManager(config)
```

**Methods:**

```python
def send(
    self,
    notification: Notification,
    channels: list[str] | None = None,
) -> NotificationResult:
    """
    Send notification through specified channels.

    Args:
        notification: Notification to send.
        channels: Target channels (None = all enabled).

    Returns:
        Result with delivery status per channel.
    """
```

```python
def send_batch(
    self,
    notifications: list[Notification],
    rate_limit: int = 10,
) -> BatchNotificationResult:
    """
    Send multiple notifications with rate limiting.

    Args:
        notifications: List of notifications to send.
        rate_limit: Max notifications per minute.

    Returns:
        Batch result with individual statuses.
    """
```

```python
def schedule(
    self,
    notification: Notification,
    send_at: datetime,
    channels: list[str] | None = None,
) -> str:
    """
    Schedule notification for future delivery.

    Args:
        notification: Notification to schedule.
        send_at: When to send.
        channels: Target channels.

    Returns:
        Scheduled notification ID.
    """
```

**Example:**

```python
from spreadsheet_dl import NotificationManager, Notification, NotificationPriority
from datetime import datetime, timedelta

manager = NotificationManager(config)

# Send immediate notification
notification = Notification(
    title="Budget Alert",
    message="Groceries category over budget by $45.50",
    priority=NotificationPriority.HIGH
)

result = manager.send(notification, channels=["email", "push"])

if result.success:
    print("Notification sent successfully")
else:
    print(f"Failed channels: {result.failed_channels}")

# Schedule future notification
reminder = Notification(
    title="Bill Reminder",
    message="Rent payment due in 3 days",
    priority=NotificationPriority.NORMAL
)

send_time = datetime.now() + timedelta(days=3)
notification_id = manager.schedule(reminder, send_time)
```

### Notification

Notification message container.

**Attributes:**

- `title` (str): Notification title/subject
- `message` (str): Main notification body
- `priority` (NotificationPriority): Urgency level
- `category` (str | None): Category/tag for filtering
- `data` (dict[str, Any]): Additional structured data
- `template` (str | None): Template name for formatting
- `timestamp` (datetime): Creation timestamp (auto)

**Example:**

```python
from spreadsheet_dl import Notification, NotificationPriority

notification = Notification(
    title="Monthly Budget Report",
    message="Your January budget report is ready",
    priority=NotificationPriority.LOW,
    category="report",
    data={
        "month": "January",
        "total_spent": 2347.89,
        "budget_used_percent": 46.96
    },
    template="monthly_report"
)
```

### NotificationPriority

Priority enumeration for notifications.

```python
class NotificationPriority(Enum):
    LOW = "low"           # Informational
    NORMAL = "normal"     # Standard notifications
    HIGH = "high"         # Important alerts
    URGENT = "urgent"     # Critical/immediate action required
```

**Priority behaviors:**

- **LOW**: Batched, no retry, email only
- **NORMAL**: Standard delivery, 2 retries
- **HIGH**: Priority delivery, 3 retries, all channels
- **URGENT**: Immediate delivery, 5 retries, all channels + fallback

## Notification Channels

### EmailChannel

SMTP email notifications.

**Configuration:**

```python
config = NotificationConfig(
    email_enabled=True,
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_user="your-email@gmail.com",
    smtp_password="app-password",
    smtp_from="Budget Alerts <alerts@example.com>",
    smtp_to=["your-email@gmail.com"],
    smtp_use_tls=True
)
```

**Features:**

- HTML and plain text support
- Template-based formatting
- Attachment support
- CC/BCC options
- Custom headers

**Example:**

```python
from spreadsheet_dl import EmailChannel, Notification

channel = EmailChannel(config)

notification = Notification(
    title="Budget Alert: Overspending Detected",
    message="You've exceeded your dining out budget by $128.",
    priority=NotificationPriority.HIGH,
    template="budget_alert_email"
)

result = channel.send(notification)
```

### PushChannel (ntfy.sh)

Push notifications via ntfy.sh.

**Configuration:**

```python
config = NotificationConfig(
    push_enabled=True,
    ntfy_server="https://ntfy.sh",
    ntfy_topic="my-budget-alerts",
    ntfy_token="tk_xxxxxxxxxxxxx"  # Optional auth
)
```

**Features:**

- Mobile push notifications
- Click actions/links
- Priority levels
- Icons and emojis
- Scheduled delivery

**Example:**

```python
from spreadsheet_dl import PushChannel, Notification

channel = PushChannel(config)

notification = Notification(
    title="Bill Due Today",
    message="Rent payment of $1,500 is due",
    priority=NotificationPriority.URGENT,
    data={
        "click": "https://bank.example.com/pay",
        "icon": "💰"
    }
)

result = channel.send(notification)
```

**Mobile App Setup:**

1. Install ntfy app (iOS/Android)
2. Subscribe to your topic: `my-budget-alerts`
3. Receive notifications instantly

### WebhookChannel

HTTP webhook notifications.

**Configuration:**

```python
config = NotificationConfig(
    webhook_enabled=True,
    webhook_url="https://your-server.com/webhooks/budget",
    webhook_headers={
        "Authorization": "Bearer your-token",
        "Content-Type": "application/json"
    },
    webhook_method="POST"
)
```

**Features:**

- JSON payload delivery
- Custom headers and auth
- Retry with exponential backoff
- Signature verification

**Example:**

```python
from spreadsheet_dl import WebhookChannel, Notification

channel = WebhookChannel(config)

notification = Notification(
    title="Budget Updated",
    message="January budget updated with new expenses",
    data={
        "event": "budget.updated",
        "budget_id": "2026-01",
        "total_spent": 2347.89,
        "timestamp": "2026-01-18T14:32:00Z"
    }
)

result = channel.send(notification)
```

**Webhook Payload:**

```json
{
  "title": "Budget Updated",
  "message": "January budget updated with new expenses",
  "priority": "normal",
  "timestamp": "2026-01-18T14:32:00Z",
  "data": {
    "event": "budget.updated",
    "budget_id": "2026-01",
    "total_spent": 2347.89
  }
}
```

### CustomChannel

User-defined notification channels.

**Example:**

```python
from spreadsheet_dl import NotificationChannel, Notification, NotificationResult

class SlackChannel(NotificationChannel):
    """Custom Slack notification channel."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, notification: Notification) -> NotificationResult:
        import requests

        payload = {
            "text": f"*{notification.title}*\n{notification.message}",
            "username": "Budget Bot",
            "icon_emoji": ":moneybag:"
        }

        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()

            return NotificationResult(
                success=True,
                channel="slack",
                message="Sent to Slack"
            )
        except Exception as e:
            return NotificationResult(
                success=False,
                channel="slack",
                error=str(e)
            )

# Register and use
manager.register_channel("slack", SlackChannel(slack_webhook_url))
result = manager.send(notification, channels=["slack"])
```

## Integration with Alerts

Automatic notifications for budget alerts:

```python
from spreadsheet_dl import AlertMonitor, NotificationManager, AlertSeverity

# Setup
analyzer = BudgetAnalyzer("budget.ods")
alert_monitor = AlertMonitor(analyzer, alert_config)
notification_manager = NotificationManager(notification_config)

# Check alerts and notify
alerts = alert_monitor.check_all()

for alert in alerts:
    # Determine priority from severity
    if alert.severity == AlertSeverity.CRITICAL:
        priority = NotificationPriority.URGENT
    elif alert.severity == AlertSeverity.WARNING:
        priority = NotificationPriority.HIGH
    else:
        priority = NotificationPriority.NORMAL

    # Create notification
    notification = Notification(
        title=alert.title,
        message=alert.message,
        priority=priority,
        category=alert.category,
        data=alert.to_dict()
    )

    # Send based on severity
    if alert.severity == AlertSeverity.CRITICAL:
        # Send via all channels
        notification_manager.send(notification)
    else:
        # Send via email only
        notification_manager.send(notification, channels=["email"])
```

## Integration with Reminders

Bill reminder notifications:

```python
from spreadsheet_dl import BillReminderManager, NotificationManager
from datetime import date

reminder_manager = BillReminderManager("bills.json")
notification_manager = NotificationManager(config)

# Get bills due soon
upcoming = reminder_manager.get_upcoming_bills(days=3)

for bill in upcoming:
    notification = Notification(
        title=f"Bill Reminder: {bill.name}",
        message=f"{bill.name} payment of ${bill.amount} due in {bill.days_until_due} days",
        priority=NotificationPriority.HIGH,
        category="bill_reminder",
        data={
            "bill_id": bill.id,
            "amount": str(bill.amount),
            "due_date": bill.due_date.isoformat(),
            "payee": bill.payee
        }
    )

    # Send notification
    notification_manager.send(notification, channels=["push"])
```

## Templates

Message templates for consistent formatting:

**Template Definition:**

```python
from spreadsheet_dl import NotificationTemplate

budget_alert_template = NotificationTemplate(
    name="budget_alert",
    subject="Budget Alert: {category} Over Budget",
    body_text="""
    Alert: {category} spending has exceeded budget

    Budget: ${budget:.2f}
    Spent: ${spent:.2f}
    Over by: ${over_amount:.2f} ({percent_over:.1f}%)

    Review your spending at: {dashboard_url}
    """,
    body_html="""
    <h2>Budget Alert</h2>
    <p><strong>{category}</strong> spending has exceeded budget</p>
    <table>
        <tr><td>Budget:</td><td>${budget:.2f}</td></tr>
        <tr><td>Spent:</td><td>${spent:.2f}</td></tr>
        <tr><td>Over by:</td><td style="color: red;">${over_amount:.2f} ({percent_over:.1f}%)</td></tr>
    </table>
    <p><a href="{dashboard_url}">Review your spending</a></p>
    """
)

# Register template
manager.register_template(budget_alert_template)

# Use template
notification = Notification(
    title="Budget Alert",
    message="Dining Out over budget",
    template="budget_alert",
    data={
        "category": "Dining Out",
        "budget": 200.00,
        "spent": 328.00,
        "over_amount": 128.00,
        "percent_over": 64.0,
        "dashboard_url": "https://example.com/budget"
    }
)
```

## Configuration

Complete configuration options:

```python
from spreadsheet_dl import NotificationConfig

config = NotificationConfig(
    # Email settings
    email_enabled=True,
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_user="your-email@gmail.com",
    smtp_password="app-password",
    smtp_from="Budget Alerts <alerts@example.com>",
    smtp_to=["recipient@example.com"],
    smtp_use_tls=True,

    # Push notification settings
    push_enabled=True,
    ntfy_server="https://ntfy.sh",
    ntfy_topic="budget-alerts",
    ntfy_token=None,  # Optional

    # Webhook settings
    webhook_enabled=False,
    webhook_url=None,
    webhook_headers=None,
    webhook_method="POST",

    # General settings
    retry_attempts=3,
    retry_delay=5,  # seconds
    rate_limit=10,  # notifications per minute
    batch_enabled=True,
    batch_interval=60,  # seconds
)
```

## Best Practices

1. **Priority Levels**: Use appropriate priority levels to avoid alert fatigue
2. **Rate Limiting**: Enable rate limiting for batch notifications
3. **Templates**: Use templates for consistent messaging
4. **Error Handling**: Always check NotificationResult for delivery failures
5. **Testing**: Test notification channels before production use
6. **Security**: Store credentials securely (use environment variables)
7. **Batching**: Batch low-priority notifications to reduce noise

## Troubleshooting

**Email not sending?**

- Check SMTP credentials and server address
- Verify TLS/SSL settings
- Use app-specific passwords (Gmail)
- Check firewall/network restrictions

**Push notifications not arriving?**

- Verify ntfy topic is subscribed in mobile app
- Check server URL is correct
- Ensure mobile device has internet connection
- Test with ntfy.sh web interface first

**Webhook delivery failing?**

- Verify webhook URL is accessible
- Check authentication headers
- Review webhook endpoint logs
- Test with curl/Postman first

## See Also

- [alerts](api/alerts.md) - Budget alert monitoring
- [reminders](api/reminders.md) - Bill reminder system
- [config](api/config.md) - Configuration management
- [security](api/security.md) - Credential storage

## Example Scripts

### Daily Budget Check with Notifications

```python
#!/usr/bin/env python3
"""Daily budget check with notifications."""

from spreadsheet_dl import (
    BudgetAnalyzer,
    AlertMonitor,
    AlertConfig,
    NotificationManager,
    NotificationConfig,
    Notification,
    NotificationPriority
)

def daily_budget_check():
    # Setup
    analyzer = BudgetAnalyzer("budget.ods")
    alert_config = AlertConfig(
        budget_warning_threshold=80.0,
        budget_critical_threshold=95.0
    )
    alert_monitor = AlertMonitor(analyzer, alert_config)

    notification_config = NotificationConfig(
        email_enabled=True,
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        smtp_user="your-email@gmail.com",
        smtp_password="app-password",
        push_enabled=True,
        ntfy_topic="budget-alerts"
    )
    notification_manager = NotificationManager(notification_config)

    # Check for alerts
    alerts = alert_monitor.check_all()

    if not alerts:
        print("No budget alerts today")
        return

    # Send notifications
    for alert in alerts:
        priority = (
            NotificationPriority.URGENT if alert.severity.value == "critical"
            else NotificationPriority.HIGH if alert.severity.value == "warning"
            else NotificationPriority.NORMAL
        )

        notification = Notification(
            title=alert.title,
            message=alert.message,
            priority=priority,
            category=alert.category
        )

        result = notification_manager.send(notification)
        print(f"Sent: {alert.title} - {result.success}")

if __name__ == "__main__":
    daily_budget_check()
```

### Bill Reminder Automation

```python
#!/usr/bin/env python3
"""Automated bill reminder notifications."""

from spreadsheet_dl import (
    BillReminderManager,
    NotificationManager,
    NotificationConfig,
    Notification,
    NotificationPriority
)

def send_bill_reminders():
    # Setup
    reminder_manager = BillReminderManager("bills.json")
    notification_config = NotificationConfig(
        push_enabled=True,
        ntfy_topic="bill-reminders"
    )
    notification_manager = NotificationManager(notification_config)

    # Get upcoming bills
    upcoming = reminder_manager.get_upcoming_bills(days=7)

    for bill in upcoming:
        notification = Notification(
            title=f"Bill Reminder: {bill.name}",
            message=f"${bill.amount} due in {bill.days_until_due} days to {bill.payee}",
            priority=NotificationPriority.HIGH,
            data={
                "bill_id": bill.id,
                "amount": str(bill.amount),
                "due_date": bill.due_date.isoformat()
            }
        )

        notification_manager.send(notification, channels=["push"])
        print(f"Sent reminder: {bill.name}")

if __name__ == "__main__":
    send_bill_reminders()
```
