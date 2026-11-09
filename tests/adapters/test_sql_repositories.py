"""
Tests d'intégration des adaptateurs de persistance SQLAlchemy.
"""

import pytest
from datetime import datetime
from app.adapters.outbound.persistence import (
    SqlArtistRepository, SqlConcertRepository, SqlFestivalRepository, SqlStageRepository,
)
from app.database import Base, SessionLocal
from app.domain.entities.artist import Artist
from app.domain.entities.concert import Concert
from app.domain.entities.festival import Festival
from app.domain.entities.stage import Stage
from app.domain.value_objects.date_range import DateRange
from app.domain.value_objects.equipment import EquipmentSet
from app.domain.value_objects.time_slot import TimeSlot

@pytest.fixture
def session():
    db = SessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    yield db
    db.rollback()
    db.close()

@pytest.fixture
def base_data(session):
    fest = SqlFestivalRepository(session).save(Festival(
        name="Hellforge", location="Clisson",
        period=DateRange(datetime(2027, 6, 18, 10, 0), datetime(2027, 6, 20, 23, 0)),
    ))
    artist = SqlArtistRepository(session).save(Artist(
        name="Iron Vow", genre="Heavy",
        required_equipment=EquipmentSet.from_iterable(["Micro", "Guitares"]),
    ))
    stage = SqlStageRepository(session).save(Stage(
        festival_id=fest.id, name="Mainstage", capacity=1000,
        available_equipment=EquipmentSet.from_iterable(["Micro", "Guitares"]),
    ))
    return fest, artist, stage

def _concert(fest, artist, stage, h_start, h_end, status="scheduled"):
    return Concert(festival_id=fest.id, artist_id=artist.id, stage_id=stage.id,
                   time_slot=TimeSlot(datetime(2027, 6, 18, h_start), datetime(2027, 6, 18, h_end)),
                   status=status)

def test_concert_save_and_get_roundtrip(session, base_data):
    repo = SqlConcertRepository(session)
    saved = repo.save(_concert(*base_data, 18, 19))
    loaded = repo.get_by_id(saved.id)
    assert loaded.time_slot == saved.time_slot
    assert loaded.status == "scheduled"

def test_list_by_festival_excludes_cancelled_and_is_sorted(session, base_data):
    fest = base_data[0]
    repo = SqlConcertRepository(session)
    late = repo.save(_concert(*base_data, 20, 21))
    early = repo.save(_concert(*base_data, 14, 15))
    repo.save(_concert(*base_data, 16, 17, status="cancelled"))
    ids = [c.id for c in repo.list_by_festival(fest.id)]
    assert ids == [early.id, late.id]

def test_equipment_survives_csv_roundtrip(session, base_data):
    artist = base_data[1]
    loaded = SqlArtistRepository(session).get_by_id(artist.id)
    assert loaded.required_equipment.to_list() == ["Guitares", "Micro"]