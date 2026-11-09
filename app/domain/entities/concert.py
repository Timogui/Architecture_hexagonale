"""
Entité Métier : Concert.
Encapsule son créneau horaire (TimeSlot) et ses états de cycle de vie.
"""

from dataclasses import dataclass
from app.domain.value_objects.time_slot import TimeSlot


@dataclass
class Concert:
    festival_id: int
    artist_id: int
    stage_id: int
    time_slot: TimeSlot
    status: str = "scheduled"
    id: int | None = None

    @property
    def is_cancelled(self) -> bool:
        return self.status == "cancelled"

    def reschedule(self, new_slot: TimeSlot) -> None:
        """Modifie le créneau horaire du concert."""
        self.time_slot = new_slot

    def cancel(self) -> None:
        """Annule le concert."""
        self.status = "cancelled"

    def conflicts_with(self, other: "Concert") -> bool:
        """Détecte un conflit de scène ou d'artiste entre deux concerts non annulés (R2 & R3)."""
        if self.is_cancelled or other.is_cancelled:
            return False
        if self.id is not None and other.id is not None and self.id == other.id:
            return False
        if not self.time_slot.overlaps(other.time_slot):
            return False
        return self.stage_id == other.stage_id or self.artist_id == other.artist_id
