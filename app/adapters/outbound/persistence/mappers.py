"""
Mappers entre les modèles SQLAlchemy (BD) et les Entités du Domaine (DDD).
"""

from app.domain.entities.artist import Artist
from app.domain.entities.concert import Concert
from app.domain.entities.festival import Festival
from app.domain.entities.incident import Incident
from app.domain.entities.stage import Stage
from app.domain.value_objects.date_range import DateRange
from app.domain.value_objects.equipment import EquipmentSet
from app.domain.value_objects.time_slot import TimeSlot
from app.models import (
    Artist as SqlArtist,
    Concert as SqlConcert,
    Festival as SqlFestival,
    Incident as SqlIncident,
    Stage as SqlStage,
)


def festival_to_domain(row: SqlFestival) -> Festival:
    return Festival(
        id=row.id,
        name=row.name,
        location=row.location,
        period=DateRange(start_date=row.start_date, end_date=row.end_date),
        status=row.status,
    )


def artist_to_domain(row: SqlArtist) -> Artist:
    return Artist(
        id=row.id,
        name=row.name,
        genre=row.genre,
        required_equipment=EquipmentSet.from_iterable(row.required_equipment),
    )


def stage_to_domain(row: SqlStage) -> Stage:
    return Stage(
        id=row.id,
        festival_id=row.festival_id,
        name=row.name,
        capacity=row.capacity,
        available_equipment=EquipmentSet.from_iterable(row.available_equipment),
    )


def concert_to_domain(row: SqlConcert) -> Concert:
    return Concert(
        id=row.id,
        festival_id=row.festival_id,
        artist_id=row.artist_id,
        stage_id=row.stage_id,
        time_slot=TimeSlot(start_time=row.start_time, end_time=row.end_time),
        status=row.status,
    )


def incident_to_domain(row: SqlIncident) -> Incident:
    return Incident(
        id=row.id,
        concert_id=row.concert_id,
        description=row.description,
        occurred_at=row.occurred_at,
        resolved=row.resolved,
    )
