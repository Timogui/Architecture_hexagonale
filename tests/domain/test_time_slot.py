"""
Tests unitaires purs du Domaine : Objet-Valeur TimeSlot (R1).
Aucune dépendance à FastAPI ni à SQLite.
"""

from datetime import datetime
import pytest
from app.domain.exceptions import InvalidTimeSlotError
from app.domain.value_objects.time_slot import TimeSlot


def test_valid_time_slot():
    start = datetime(2027, 6, 18, 14, 0)
    end = datetime(2027, 6, 18, 15, 0)
    slot = TimeSlot(start, end)
    assert slot.start_time == start
    assert slot.end_time == end
    assert slot.duration_seconds == 3600


def test_time_slot_end_before_start_raises_error():
    """R1 : L'heure de fin doit être strictement postérieure à l'heure de début."""
    start = datetime(2027, 6, 18, 15, 0)
    end = datetime(2027, 6, 18, 14, 0)
    with pytest.raises(InvalidTimeSlotError):
        TimeSlot(start, end)


def test_time_slot_equal_start_and_end_raises_error():
    """R1 : Durée nulle interdite."""
    dt = datetime(2027, 6, 18, 14, 0)
    with pytest.raises(InvalidTimeSlotError):
        TimeSlot(dt, dt)


def test_time_slot_overlap_detection():
    """R2/R3 : Détection précise des chevauchements stricts."""
    slot1 = TimeSlot(datetime(2027, 6, 18, 14, 0), datetime(2027, 6, 18, 15, 0))
    # Chevauchement partiel
    slot2 = TimeSlot(datetime(2027, 6, 18, 14, 30), datetime(2027, 6, 18, 15, 30))
    assert slot1.overlaps(slot2) is True
    assert slot2.overlaps(slot1) is True

    # Consécutifs (bord à bord) : ne se chevauchent PAS
    slot3 = TimeSlot(datetime(2027, 6, 18, 15, 0), datetime(2027, 6, 18, 16, 0))
    assert slot1.overlaps(slot3) is False
    assert slot3.overlaps(slot1) is False

    # Disjoints
    slot4 = TimeSlot(datetime(2027, 6, 18, 17, 0), datetime(2027, 6, 18, 18, 0))
    assert slot1.overlaps(slot4) is False
