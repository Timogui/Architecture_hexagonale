"""
Événements de domaine (Domain Events) de FestiPlan.
Représentent les faits métier accomplis.
"""

from dataclasses import dataclass, field
from datetime import datetime

from app.domain.value_objects.time_slot import TimeSlot


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, kw_only=True)
class ConcertRescheduled(DomainEvent):
    concert_id: int
    festival_id: int
    artist_id: int
    stage_id: int
    new_time_slot: TimeSlot
    old_time_slot: TimeSlot | None = None


@dataclass(frozen=True, kw_only=True)
class ConcertCancelled(DomainEvent):
    concert_id: int
    festival_id: int


@dataclass(frozen=True, kw_only=True)
class FestivalPublished(DomainEvent):
    festival_id: int
    festival_name: str
