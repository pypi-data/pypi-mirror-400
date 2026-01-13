"""
Tests for Notification System Module.

Tests IR-NOTIF-001: Alert Notifications.
"""

from __future__ import annotations

import tempfile
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from spreadsheet_dl.notifications import (
    EmailChannel,
    EmailConfig,
    Notification,
    NotificationManager,
    NotificationPriority,
    NotificationTemplates,
    NotificationType,
    NtfyChannel,
    NtfyConfig,
    load_notification_config,
)

pytestmark = [pytest.mark.unit, pytest.mark.finance]


class TestNotification:
    """Tests for Notification dataclass."""

    def test_create_notification(self) -> None:
        """Test creating a notification."""
        notification = Notification(
            type=NotificationType.BILL_DUE,
            title="Bill Reminder",
            message="Your electric bill is due",
            priority=NotificationPriority.HIGH,
        )

        assert notification.type == NotificationType.BILL_DUE
        assert notification.title == "Bill Reminder"
        assert notification.priority == NotificationPriority.HIGH
        assert notification.sent_at is None

    def test_notification_to_dict(self) -> None:
        """Test notification serialization."""
        notification = Notification(
            type=NotificationType.GOAL_COMPLETED,
            title="Goal Achieved!",
            message="You reached your savings goal",
            data={"goal_name": "Vacation", "amount": "5000"},
        )

        data = notification.to_dict()

        assert data["type"] == "goal_completed"
        assert data["title"] == "Goal Achieved!"
        assert data["data"]["goal_name"] == "Vacation"


class TestEmailChannel:
    """Tests for EmailChannel."""

    def test_is_configured_false(self) -> None:
        """Test unconfigured email channel."""
        config = EmailConfig()
        channel = EmailChannel(config)

        assert not channel.is_configured()

    def test_is_configured_true(self) -> None:
        """Test configured email channel."""
        config = EmailConfig(
            smtp_host="smtp.example.com",
            username="user@example.com",
            password="secret",
            to_address="recipient@example.com",
        )
        channel = EmailChannel(config)

        assert channel.is_configured()

    @patch("smtplib.SMTP")
    def test_send_email(self, mock_smtp: MagicMock) -> None:
        """Test sending email notification."""
        config = EmailConfig(
            smtp_host="smtp.example.com",
            smtp_port=587,
            username="sender@example.com",
            password="secret",
            to_address="recipient@example.com",
        )
        channel = EmailChannel(config)

        notification = Notification(
            type=NotificationType.BILL_DUE,
            title="Test",
            message="Test message",
        )

        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = channel.send(notification)

        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()

    def test_format_subject_with_priority(self) -> None:
        """Test subject formatting includes priority prefix."""
        channel = EmailChannel(EmailConfig())

        urgent = Notification(
            type=NotificationType.BILL_OVERDUE,
            title="Test",
            message="",
            priority=NotificationPriority.URGENT,
        )
        normal = Notification(
            type=NotificationType.BILL_DUE,
            title="Test",
            message="",
            priority=NotificationPriority.NORMAL,
        )

        assert "[URGENT]" in channel._format_subject(urgent)
        assert "[URGENT]" not in channel._format_subject(normal)


class TestNtfyChannel:
    """Tests for NtfyChannel."""

    def test_is_configured_false(self) -> None:
        """Test unconfigured ntfy channel."""
        config = NtfyConfig()
        channel = NtfyChannel(config)

        assert not channel.is_configured()

    def test_is_configured_true(self) -> None:
        """Test configured ntfy channel."""
        config = NtfyConfig(
            server="https://ntfy.sh",
            topic="my-topic",
        )
        channel = NtfyChannel(config)

        assert channel.is_configured()

    def test_get_tags(self) -> None:
        """Test emoji tag mapping."""
        channel = NtfyChannel(NtfyConfig())

        bill_due = Notification(
            type=NotificationType.BILL_DUE,
            title="Test",
            message="",
        )
        goal = Notification(
            type=NotificationType.GOAL_COMPLETED,
            title="Test",
            message="",
        )

        assert "dollar" in channel._get_tags(bill_due)
        assert "tada" in channel._get_tags(goal)


class TestNotificationManager:
    """Tests for NotificationManager."""

    def test_add_channel(self) -> None:
        """Test adding custom channel."""
        manager = NotificationManager()
        mock_channel = MagicMock()
        mock_channel.is_configured.return_value = True

        manager.add_channel("custom", mock_channel)

        channels = manager.list_channels()
        assert any(c["name"] == "custom" for c in channels)

    def test_remove_channel(self) -> None:
        """Test removing channel."""
        manager = NotificationManager()
        mock_channel = MagicMock()
        manager.add_channel("test", mock_channel)

        assert manager.remove_channel("test")
        assert not manager.remove_channel("nonexistent")

    def test_send_to_channels(self) -> None:
        """Test sending to specific channels."""
        manager = NotificationManager()

        channel1 = MagicMock()
        channel1.is_configured.return_value = True
        channel1.send.return_value = True

        channel2 = MagicMock()
        channel2.is_configured.return_value = True
        channel2.send.return_value = True

        manager.add_channel("ch1", channel1)
        manager.add_channel("ch2", channel2)

        notification = Notification(
            type=NotificationType.CUSTOM,
            title="Test",
            message="Test",
        )

        results = manager.send(notification, channels=["ch1"])

        assert results["ch1"] is True
        assert "ch2" not in results
        channel1.send.assert_called_once()
        channel2.send.assert_not_called()

    def test_send_all(self) -> None:
        """Test sending to all channels."""
        manager = NotificationManager()

        channel1 = MagicMock()
        channel1.is_configured.return_value = True
        channel1.send.return_value = True

        channel2 = MagicMock()
        channel2.is_configured.return_value = True
        channel2.send.return_value = True

        manager.add_channel("ch1", channel1)
        manager.add_channel("ch2", channel2)

        notification = Notification(
            type=NotificationType.CUSTOM,
            title="Test",
            message="Test",
        )

        results = manager.send_all(notification)

        assert results["ch1"] is True
        assert results["ch2"] is True

    def test_notification_history(self) -> None:
        """Test notification history tracking."""
        manager = NotificationManager()
        mock_channel = MagicMock()
        mock_channel.is_configured.return_value = True
        mock_channel.send.return_value = True
        manager.add_channel("test", mock_channel)

        for i in range(3):
            notification = Notification(
                type=NotificationType.CUSTOM,
                title=f"Test {i}",
                message="Test",
            )
            manager.send(notification, channels=["test"])

        history = manager.get_history()
        assert len(history) == 3

    def test_history_filter_by_type(self) -> None:
        """Test filtering history by type."""
        manager = NotificationManager()

        manager._history.append(
            Notification(
                type=NotificationType.BILL_DUE,
                title="Bill",
                message="",
            )
        )
        manager._history.append(
            Notification(
                type=NotificationType.GOAL_COMPLETED,
                title="Goal",
                message="",
            )
        )
        manager._history.append(
            Notification(
                type=NotificationType.BILL_DUE,
                title="Bill 2",
                message="",
            )
        )

        bills = manager.get_history(notification_type=NotificationType.BILL_DUE)
        assert len(bills) == 2


class TestNotificationTemplates:
    """Tests for notification templates."""

    def test_bill_due_template(self) -> None:
        """Test bill due notification template."""
        notification = NotificationTemplates.bill_due(
            bill_name="Electric",
            amount=Decimal("150"),
            due_date=date.today() + timedelta(days=3),
        )

        assert notification.type == NotificationType.BILL_DUE
        assert "Electric" in notification.title
        assert "$150" in notification.message

    def test_bill_due_today_high_priority(self) -> None:
        """Test bill due today is high priority."""
        notification = NotificationTemplates.bill_due(
            bill_name="Test",
            amount=100,
            due_date=date.today(),
        )

        assert notification.priority == NotificationPriority.HIGH
        assert "TODAY" in notification.message

    def test_bill_overdue_template(self) -> None:
        """Test overdue bill notification."""
        notification = NotificationTemplates.bill_overdue(
            bill_name="Rent",
            amount=Decimal("1500"),
            due_date=date.today() - timedelta(days=5),
            days_overdue=5,
        )

        assert notification.type == NotificationType.BILL_OVERDUE
        assert notification.priority == NotificationPriority.URGENT
        assert "5 days overdue" in notification.message

    def test_budget_warning_template(self) -> None:
        """Test budget warning notification."""
        notification = NotificationTemplates.budget_warning(
            category="Dining Out",
            spent=Decimal("180"),
            budget=Decimal("200"),
            percent_used=90,
        )

        assert notification.type == NotificationType.BUDGET_WARNING
        assert "90%" in notification.message
        assert "Dining Out" in notification.title

    def test_budget_exceeded_template(self) -> None:
        """Test budget exceeded notification."""
        notification = NotificationTemplates.budget_exceeded(
            category="Entertainment",
            spent=Decimal("250"),
            budget=Decimal("200"),
            over_amount=Decimal("50"),
        )

        assert notification.type == NotificationType.BUDGET_EXCEEDED
        assert notification.priority == NotificationPriority.URGENT
        assert "$50" in notification.message

    def test_goal_progress_template(self) -> None:
        """Test goal progress notification."""
        notification = NotificationTemplates.goal_progress(
            goal_name="Vacation Fund",
            current=Decimal("2500"),
            target=Decimal("5000"),
            percent_complete=50,
        )

        assert notification.type == NotificationType.GOAL_PROGRESS
        assert "50%" in notification.message
        assert notification.data.get("milestone") == 50

    def test_goal_completed_template(self) -> None:
        """Test goal completed notification."""
        notification = NotificationTemplates.goal_completed(
            goal_name="Emergency Fund",
            target=Decimal("10000"),
            days_taken=180,
        )

        assert notification.type == NotificationType.GOAL_COMPLETED
        assert notification.priority == NotificationPriority.HIGH
        assert "Congratulations" in notification.message

    def test_weekly_summary_template(self) -> None:
        """Test weekly summary notification."""
        notification = NotificationTemplates.weekly_summary(
            week_total=Decimal("450"),
            top_categories=[
                ("Groceries", Decimal("200")),
                ("Dining Out", Decimal("150")),
                ("Gas", Decimal("100")),
            ],
            budget_status="on track",
        )

        assert notification.type == NotificationType.WEEKLY_SUMMARY
        assert "$450" in notification.message
        assert "Groceries" in notification.message

    def test_monthly_summary_template(self) -> None:
        """Test monthly summary notification."""
        notification = NotificationTemplates.monthly_summary(
            month="January 2025",
            total_spent=Decimal("3500"),
            total_budget=Decimal("4000"),
            savings=Decimal("500"),
            over_budget_categories=["Entertainment"],
        )

        assert notification.type == NotificationType.MONTHLY_SUMMARY
        assert "January 2025" in notification.title
        assert "under" in notification.message


class TestConfigLoading:
    """Tests for configuration loading."""

    def test_load_config_file_not_found(self) -> None:
        """Test loading non-existent config."""
        email, ntfy = load_notification_config("/nonexistent/path.json")
        assert email is None
        assert ntfy is None

    def test_load_config_with_email(self) -> None:
        """Test loading config with email settings."""
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config = {
                "email": {
                    "smtp_host": "smtp.example.com",
                    "smtp_port": 587,
                    "username": "user@example.com",
                    "password": "secret",
                    "to_address": "recipient@example.com",
                }
            }
            config_path.write_text(json.dumps(config))

            email, ntfy = load_notification_config(config_path)

            assert email is not None
            assert email.smtp_host == "smtp.example.com"
            assert email.to_address == "recipient@example.com"
            assert ntfy is None

    def test_load_config_with_ntfy(self) -> None:
        """Test loading config with ntfy settings."""
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config = {
                "ntfy": {
                    "server": "https://ntfy.sh",
                    "topic": "my-bills",
                }
            }
            config_path.write_text(json.dumps(config))

            email, ntfy = load_notification_config(config_path)

            assert email is None
            assert ntfy is not None
            assert ntfy.topic == "my-bills"
