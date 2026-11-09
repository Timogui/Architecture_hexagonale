"""
Tests des cas d'utilisation Festival, Stage, Artist et Incident avec doubles en mémoire.
"""

from datetime import datetime

import pytest
from app.application.dtos import (
    CreateFestivalCommand,
    CreateIncidentCommand,
    CreateStageCommand,
)
from app.application.use_cases.festival_use_cases import (
    CreateFestivalUseCase,
    PublishFestivalUseCase,
)
from app.application.use_cases.incident_use_cases import (
    CreateIncidentUseCase,
    ListIncidentsUseCase,
)
from app.application.use_cases.stage_use_cases import (
    CreateStageUseCase,
    ListStagesUseCase,
)
from app.domain.entities.concert import Concert
from app.domain.entities.festival import Festival
from app.domain.exceptions import EntityNotFoundError, FestivalCannotBePublishedError
from app.domain.value_objects.date_range import DateRange
from app.domain.value_objects.time_slot import TimeSlot
from tests.application.fakes import (
    FakeUnitOfWork,
    InMemoryConcertRepository,
    InMemoryFestivalRepository,
    InMemoryIncidentRepository,
    InMemoryStageRepository,
    SpyNotificationSender,
)


def test_festival_lifecycle():
    f_repo = InMemoryFestivalRepository()
    c_repo = InMemoryConcertRepository()
    uow = FakeUnitOfWork()
    notif = SpyNotificationSender()

    create_uc = CreateFestivalUseCase(f_repo, uow)
    publish_uc = PublishFestivalUseCase(f_repo, c_repo, notif, uow)

    cmd = CreateFestivalCommand(
        name="Hellfest Open Air",
        location="Clisson",
        start_date=datetime(2027, 6, 18, 10, 0),
        end_date=datetime(2027, 6, 20, 23, 0),
    )
    fest = create_uc.execute(cmd)
    assert fest.id is not None
    assert fest.status == "preparation"

    pub = publish_uc.execute(fest.id)
    assert pub.status == "published"
    assert len(notif.notifications) == 1


def test_stage_creation_and_listing():
    f_repo = InMemoryFestivalRepository()
    s_repo = InMemoryStageRepository()
    uow = FakeUnitOfWork()

    fest = f_repo.save(
        Festival(
            name="Hellfest",
            location="Clisson",
            period=DateRange(
                datetime(2027, 6, 18, 10, 0), datetime(2027, 6, 20, 23, 0)
            ),
        )
    )

    create_stage_uc = CreateStageUseCase(s_repo, f_repo, uow)
    list_stage_uc = ListStagesUseCase(s_repo)

    cmd = CreateStageCommand(
        festival_id=fest.id,
        name="Warzone",
        capacity=8000,
        available_equipment=["Micro", "Guitares"],
    )
    stage = create_stage_uc.execute(cmd)
    assert stage.name == "Warzone"

    stages = list_stage_uc.execute(fest.id)
    assert len(stages) == 1


def test_incident_creation_and_listing():
    c_repo = InMemoryConcertRepository()
    i_repo = InMemoryIncidentRepository()
    uow = FakeUnitOfWork()

    c = c_repo.save(
        Concert(
            festival_id=1,
            artist_id=1,
            stage_id=1,
            time_slot=TimeSlot(
                datetime(2027, 6, 18, 18, 0), datetime(2027, 6, 18, 19, 0)
            ),
        )
    )

    create_uc = CreateIncidentUseCase(i_repo, c_repo, uow)
    list_uc = ListIncidentsUseCase(i_repo)

    cmd = CreateIncidentCommand(
        concert_id=c.id,
        description="Pogo trop intense, barrière endommagée",
    )
    inc = create_uc.execute(cmd)
    assert inc.id is not None
    assert inc.resolved is False

    all_inc = list_uc.execute(c.id)
    assert len(all_inc) == 1
    assert all_inc[0].description == "Pogo trop intense, barrière endommagée"


def test_incident_unknown_concert_raises():
    """R10 : Un incident sur un concert inexistant doit échouer."""
    c_repo = InMemoryConcertRepository()
    i_repo = InMemoryIncidentRepository()
    uow = FakeUnitOfWork()
    create_uc = CreateIncidentUseCase(i_repo, c_repo, uow)

    cmd = CreateIncidentCommand(concert_id=999, description="Incident fantôme")
    with pytest.raises(EntityNotFoundError):
        create_uc.execute(cmd)


def test_publish_refused_if_conflicts_and_no_notification_sent():
    f_repo = InMemoryFestivalRepository()
    c_repo = InMemoryConcertRepository()
    notif = SpyNotificationSender()
    fest = f_repo.save(
        Festival(
            name="Hellforge",
            location="Clisson",
            period=DateRange(
                datetime(2027, 6, 18, 10, 0), datetime(2027, 6, 20, 23, 0)
            ),
        )
    )
    c_repo.save(
        Concert(
            festival_id=fest.id,
            artist_id=1,
            stage_id=1,
            time_slot=TimeSlot(
                datetime(2027, 6, 18, 14, 0), datetime(2027, 6, 18, 15, 0)
            ),
        )
    )
    c_repo.save(
        Concert(
            festival_id=fest.id,
            artist_id=2,
            stage_id=1,
            time_slot=TimeSlot(
                datetime(2027, 6, 18, 14, 30), datetime(2027, 6, 18, 15, 30)
            ),
        )
    )

    with pytest.raises(FestivalCannotBePublishedError):
        PublishFestivalUseCase(f_repo, c_repo, notif, FakeUnitOfWork()).execute(fest.id)

    assert notif.notifications == []
    assert f_repo.get_by_id(fest.id).status == "preparation"
