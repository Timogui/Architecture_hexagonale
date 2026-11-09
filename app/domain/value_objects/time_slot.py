"""
Objet-Valeur : Créneau Horaire (TimeSlot).
Immuable et auto-validant selon la règle métier R1.
"""

from dataclasses import dataclass
from datetime import datetime
from app.domain.exceptions import InvalidTimeSlotError


@dataclass(frozen=True)
class TimeSlot:
    start_time: datetime
    end_time: datetime

    def __post_init__(self):
        if self.end_time <= self.start_time:
            raise InvalidTimeSlotError(
                f"L'heure de fin ({self.end_time}) doit être strictement postérieure à l'heure de début ({self.start_time})."
            )

    def overlaps(self, other: "TimeSlot") -> bool:
        """Vérifie si deux créneaux temporels se chevauchent strictement."""
        return self.start_time < other.end_time and other.start_time < self.end_time

    @property
    def duration_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()
