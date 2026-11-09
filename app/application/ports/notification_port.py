"""
Port sortant pour l'envoi de notifications.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class NotificationPort(Protocol):
    def notify_schedule_change(self, concert_id: int, message: str) -> None: ...
