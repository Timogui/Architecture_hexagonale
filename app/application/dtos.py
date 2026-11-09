"""
Data Transfer Objects (DTOs) & Commandes applicatives.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateFestivalCommand:
    name: str
    location: str
    start_date: datetime
    end_date: datetime


@dataclass(frozen=True)
class CreateArtistCommand:
    name: str
    genre: str
    required_equipment: list[str]


@dataclass(frozen=True)
class CreateStageCommand:
    festival_id: int
    name: str
    capacity: int
    available_equipment: list[str]


@dataclass(frozen=True)
class CreateConcertCommand:
    festival_id: int
    artist_id: int
    stage_id: int
    start_time: datetime
    end_time: datetime


@dataclass(frozen=True)
class RescheduleConcertCommand:
    start_time: datetime
    end_time: datetime


@dataclass(frozen=True)
class CreateIncidentCommand:
    concert_id: int
    description: str
    occurred_at: datetime | None = None
