"""
Objet-Valeur : Période de dates (DateRange).
Immuable et auto-validant (R6 & R9).
"""

from dataclasses import dataclass
from datetime import datetime
from app.domain.exceptions import InvalidDateRangeError
from app.domain.value_objects.time_slot import TimeSlot


@dataclass(frozen=True)
class DateRange:
    start_date: datetime
    end_date: datetime

    def __post_init__(self):
        if self.end_date <= self.start_date:
            raise InvalidDateRangeError(
                f"La date de fin ({self.end_date}) doit être postérieure à la date de début ({self.start_date})."
            )

    def contains(self, slot: TimeSlot) -> bool:
        """Vérifie si un créneau est entièrement inclus dans la période (R6)."""
        return self.start_date <= slot.start_time and slot.end_time <= self.end_date
