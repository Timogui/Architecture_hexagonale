"""
Entité Métier : Concert.
Encapsule son créneau horaire (TimeSlot) et ses états de cycle de vie.
"""

from dataclasses import dataclass
from app.domain.value_objects.time_slot import TimeSlot
from app.domain.events import ConcertRescheduled
from app.domain.exceptions import ConcertCancelledError


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

    def reschedule(self, new_slot: TimeSlot) -> ConcertRescheduled:
        if self.is_cancelled:
            raise ConcertCancelledError("Un concert annulé ne peut pas être déplacé.")
        old_slot = self.time_slot
        self.time_slot = new_slot
        return ConcertRescheduled(
            concert_id=self.id,
            festival_id=self.festival_id,
            artist_id=self.artist_id,
            stage_id=self.stage_id,
            new_time_slot=new_slot,
            old_time_slot=old_slot,
        )

    def cancel(self) -> None:
        self.status = "cancelled"

    def conflict_reason(self, other: "Concert") -> str | None:
        if self.is_cancelled or other.is_cancelled:
            return None
        if self.id is not None and self.id == other.id:
            return None
        if not self.time_slot.overlaps(other.time_slot):
            return None
        if self.stage_id == other.stage_id:
            return "stage"
        if self.artist_id == other.artist_id:
            return "artist"
        return None

    def conflicts_with(self, other: "Concert") -> bool:
        return self.conflict_reason(other) is not None