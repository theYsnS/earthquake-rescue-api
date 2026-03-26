import logging
from datetime import datetime
from typing import Optional

from src.models.schemas import Severity

logger = logging.getLogger(__name__)


class NotificationService:
    """Simulated notification service for push notifications and SMS alerts."""

    PRIORITY_MAP = {
        Severity.CRITICAL: "IMMEDIATE",
        Severity.HIGH: "HIGH",
        Severity.MEDIUM: "NORMAL",
        Severity.LOW: "LOW",
    }

    def __init__(self):
        self.notification_log: list[dict] = []

    def send_push_notification(
        self,
        title: str,
        message: str,
        severity: Severity,
        target_team_id: Optional[int] = None,
    ) -> dict:
        """Send a simulated push notification with priority routing."""
        priority = self.PRIORITY_MAP.get(severity, "NORMAL")

        notification = {
            "type": "push",
            "title": title,
            "message": message,
            "priority": priority,
            "target_team_id": target_team_id,
            "timestamp": datetime.utcnow().isoformat(),
            "delivered": True,
        }

        self.notification_log.append(notification)
        logger.info(
            f"[PUSH][{priority}] -> Team {target_team_id}: {title} - {message}"
        )
        return notification

    def send_sms(
        self,
        phone_number: str,
        message: str,
        severity: Severity,
    ) -> dict:
        """Send a simulated SMS alert."""
        priority = self.PRIORITY_MAP.get(severity, "NORMAL")

        sms = {
            "type": "sms",
            "phone": phone_number,
            "message": message,
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat(),
            "delivered": True,
        }

        self.notification_log.append(sms)
        logger.info(f"[SMS][{priority}] -> {phone_number}: {message}")
        return sms

    def notify_new_report(self, report) -> None:
        """Send notifications for a new rescue report based on severity."""
        title = f"New Rescue Report - {report.severity.value.upper()}"
        message = (
            f"Location: ({report.latitude}, {report.longitude}). "
            f"Estimated victims: {report.estimated_victims}. "
            f"{report.description[:100]}"
        )
        self.send_push_notification(title, message, report.severity)

        if report.severity in (Severity.CRITICAL, Severity.HIGH):
            self.send_sms(
                phone_number="COMMAND_CENTER",
                message=f"URGENT: {title} - {message}",
                severity=report.severity,
            )

    def notify_team_assigned(self, team, report) -> None:
        """Notify a team about their new assignment."""
        title = "New Assignment"
        message = (
            f"Respond to rescue at ({report.latitude}, {report.longitude}). "
            f"Severity: {report.severity.value}. "
            f"Estimated victims: {report.estimated_victims}."
        )
        self.send_push_notification(
            title, message, report.severity, target_team_id=team.id
        )

    def get_recent_notifications(self, limit: int = 50) -> list[dict]:
        """Return recent notifications."""
        return self.notification_log[-limit:]


# Singleton instance
notification_service = NotificationService()
