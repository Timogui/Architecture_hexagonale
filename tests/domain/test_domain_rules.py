"""
Tests unitaires purs du Domaine pour les règles métier R4, R5, R6, R7, R8, R9, R10.
"""

from datetime import datetime
import pytest
from app.domain.entities.artist import Artist
from app.domain.entities.concert import Concert
from app.domain.entities.festival import Festival
from app.domain.entities.incident import Incident
from app.domain.entities.stage import Stage
from app.domain.exceptions import (
    FestivalAlreadyPublishedError,
    FestivalCannotBePublishedError,
    InvalidDateRangeError,
    InvalidIncidentError,
    StageCapacityError,
)
from app.domain.value_objects.date_range import DateRange
from app.domain.value_objects.equipment import EquipmentSet
from app.domain.value_objects.time_slot import TimeSlot


def test_r5_equipment_satisfaction():
    """R5 : Les équipements requis par un artiste doivent être disponibles sur la scène."""
    stage_eq = EquipmentSet.from_iterable(["Micro", "Guitares", "Pyrotechnie"])
    artist_valid = EquipmentSet.from_iterable(["Micro", "Guitares"])
    artist_invalid = EquipmentSet.from_iterable(["Micro", "Synthe"])

    stage = Stage(festival_id=1, name="Mainstage", capacity=5000, available_equipment=stage_eq)
    assert stage.can_host_artist(artist_valid) is True
    assert stage.can_host_artist(artist_invalid) is False


def test_r6_concert_inside_festival_period():
    """R6 : Un concert doit se dérouler entièrement dans la période du festival."""
    period = DateRange(datetime(2027, 6, 18, 10, 0), datetime(2027, 6, 20, 23, 0))
    festival = Festival(name="Hellforge", location="Clisson", period=period)

    slot_ok = TimeSlot(datetime(2027, 6, 19, 14, 0), datetime(2027, 6, 19, 15, 0))
    slot_too_early = TimeSlot(datetime(2027, 6, 18, 8, 0), datetime(2027, 6, 18, 11, 0))
    slot_too_late = TimeSlot(datetime(2027, 6, 20, 22, 0), datetime(2027, 6, 21, 1, 0))

    assert festival.contains_slot(slot_ok) is True
    assert festival.contains_slot(slot_too_early) is False
    assert festival.contains_slot(slot_too_late) is False


def test_r7_published_festival_forbids_modifications():
    """R7 : Un planning publié ne peut pas être modifié par une opération ordinaire (Défaut 3)."""
    period = DateRange(datetime(2027, 6, 18, 10, 0), datetime(2027, 6, 20, 23, 0))
    festival = Festival(name="Hellforge", location="Clisson", period=period, status="published")

    with pytest.raises(FestivalAlreadyPublishedError):
        festival.ensure_can_modify_schedule()


def test_r8_publish_only_if_no_concert_conflicts():
    """R8 : Le planning ne peut être publié que si les concerts respectent les règles."""
    period = DateRange(datetime(2027, 6, 18, 10, 0), datetime(2027, 6, 20, 23, 0))
    festival = Festival(name="Hellforge", location="Clisson", period=period)

    slot1 = TimeSlot(datetime(2027, 6, 18, 14, 0), datetime(2027, 6, 18, 15, 0))
    slot2 = TimeSlot(datetime(2027, 6, 18, 14, 30), datetime(2027, 6, 18, 15, 30))

    # Deux concerts en conflit sur la même scène
    c1 = Concert(id=1, festival_id=1, artist_id=1, stage_id=1, time_slot=slot1)
    c2 = Concert(id=2, festival_id=1, artist_id=2, stage_id=1, time_slot=slot2)

    with pytest.raises(FestivalCannotBePublishedError):
        festival.publish(concerts=[c1, c2])


def test_r9_stage_capacity_strictly_positive():
    """R9 : La capacité d'une scène doit être strictement positive."""
    eq = EquipmentSet.from_iterable(["Micro"])
    with pytest.raises(StageCapacityError):
        Stage(festival_id=1, name="Tiny Stage", capacity=0, available_equipment=eq)

    with pytest.raises(StageCapacityError):
        Stage(festival_id=1, name="Negative Stage", capacity=-10, available_equipment=eq)


def test_r10_incident_invariants():
    """R10 : Un incident doit cibler un concert existant et posséder une description non vide."""
    with pytest.raises(InvalidIncidentError):
        Incident(concert_id=1, description="", occurred_at=datetime.utcnow())

    with pytest.raises(InvalidIncidentError):
        Incident(concert_id=0, description="Crowd surf", occurred_at=datetime.utcnow())
