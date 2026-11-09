"""
Adaptateur sortant de notification par email.
Implémente NotificationPort en appelant send_email.
"""

from app.application.ports.notification_port import NotificationPort
from app.utils.email_sender import send_email


class EmailNotificationAdapter(NotificationPort):
    def notify_schedule_change(self, concert_id: int, message: str) -> None:
        send_email(
            "production@festiplan.test",
            f"Modification du concert #{concert_id}",
            message,
        )
