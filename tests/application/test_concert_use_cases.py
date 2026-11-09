"""
Tests unitaires applicatifs des cas d'utilisation Concerts avec doubles en mémoire.
"""

from datetime import datetime

import pytest
from app.application.dtos import CreateConcertCommand, RescheduleConcertCommand
from app.application.use_cases.concert_use_cases import (
    CancelConcertUseCase,
    CreateConcertUseCase,
    RescheduleConcertUseCase,
)
from app.domain.entities.artist import Artist
from app.domain.entities.concert import Concert
from app.domain.entities.festival import Festival
from app.domain.entities.stage import Stage
from app.domain.exceptions import (
    ConcertConflictError,
    ConcertOutsideFestivalPeriodError,
    FestivalAlreadyPublishedError,
    StageEquipmentMismatchError,
    StageFestivalMismatchError,
)
from app.domain.value_objects.date_range import DateRange
from app.domain.value_objects.equipment import EquipmentSet
from app.domain.value_objects.time_slot import TimeSlot
from tests.application.fakes import (
    FakeUnitOfWork,
    InMemoryArtistRepository,
    InMemoryConcertRepository,
    InMemoryFestivalRepository,
    InMemoryStageRepository,
    SpyNotificationSender,
)


@pytest.fixture
def context():
    festival_repo = InMemoryFestivalRepository()
    artist_repo = InMemoryArtistRepository()
    stage_repo = InMemoryStageRepository()
    concert_repo = InMemoryConcertRepository()
    uow = FakeUnitOfWork()
    notif = SpyNotificationSender()

    fest = festival_repo.save(
        Festival(
            name="Hellforge",
            location="Clisson",
            period=DateRange(
                datetime(2027, 6, 18, 10, 0), datetime(2027, 6, 20, 23, 0)
            ),
        )
    )
    art1 = artist_repo.save(
        Artist(
            name="Iron Vow",
            genre="Heavy",
            required_equipment=EquipmentSet.from_iterable(["Micro"]),
        )
    )
    art2 = artist_repo.save(
        Artist(
            name="Crimson Engine",
            genre="Thrash",
            required_equipment=EquipmentSet.from_iterable(["Micro"]),
        )
    )
    stage1 = stage_repo.save(
        Stage(
            festival_id=fest.id,
            name="Mainstage",
            capacity=10000,
            available_equipment=EquipmentSet.from_iterable(["Micro", "Guitares"]),
        )
    )
    stage2 = stage_repo.save(
        Stage(
            festival_id=fest.id,
            name="Warzone",
            capacity=5000,
            available_equipment=EquipmentSet.from_iterable(["Micro"]),
        )
    )

    c1 = concert_repo.save(
        Concert(
            festival_id=fest.id,
            artist_id=art1.id,
            stage_id=stage1.id,
            time_slot=TimeSlot(
                datetime(2027, 6, 18, 18, 0), datetime(2027, 6, 18, 19, 0)
            ),
        )
    )

    return {
        "festival": fest,
        "artist1": art1,
        "artist2": art2,
        "stage1": stage1,
        "stage2": stage2,
        "concert1": c1,
        "festival_repo": festival_repo,
        "artist_repo": artist_repo,
        "stage_repo": stage_repo,
        "concert_repo": concert_repo,
        "uow": uow,
        "notif": notif,
    }


def test_reschedule_concert_success(context):
    use_case = RescheduleConcertUseCase(
        concert_repo=context["concert_repo"],
        festival_repo=context["festival_repo"],
        stage_repo=context["stage_repo"],
        artist_repo=context["artist_repo"],
        notification_sender=context["notif"],
        uow=context["uow"],
    )

    new_start = datetime(2027, 6, 18, 20, 0)
    new_end = datetime(2027, 6, 18, 21, 0)
    cmd = RescheduleConcertCommand(start_time=new_start, end_time=new_end)

    res = use_case.execute(context["concert1"].id, cmd)
    assert res.time_slot.start_time == new_start
    assert context["uow"].committed is True
    assert len(context["notif"].notifications) == 1


def test_reschedule_conflict_on_same_stage_rejected(context):
    """Défaut 1 & R2 : Rejeter un chevauchement sur la même scène."""
    c2 = context["concert_repo"].save(
        Concert(
            festival_id=context["festival"].id,
            artist_id=context["artist2"].id,
            stage_id=context["stage1"].id,
            time_slot=TimeSlot(
                datetime(2027, 6, 18, 20, 0), datetime(2027, 6, 18, 21, 0)
            ),
        )
    )
    use_case = RescheduleConcertUseCase(
        concert_repo=context["concert_repo"],
        festival_repo=context["festival_repo"],
        stage_repo=context["stage_repo"],
        artist_repo=context["artist_repo"],
        notification_sender=context["notif"],
        uow=context["uow"],
    )
    # Tenter de déplacer c2 sur le créneau de c1 (18h00 - 19h00)
    cmd = RescheduleConcertCommand(
        start_time=datetime(2027, 6, 18, 18, 30),
        end_time=datetime(2027, 6, 18, 19, 30),
    )
    with pytest.raises(ConcertConflictError, match="la scène est déjà occupée"):
        use_case.execute(c2.id, cmd)


def test_reschedule_conflict_on_same_artist_rejected(context):
    """Défaut 1 & R3 : Rejeter un chevauchement pour le même artiste sur 2 scènes."""
    c2 = context["concert_repo"].save(
        Concert(
            festival_id=context["festival"].id,
            artist_id=context["artist1"].id,
            stage_id=context["stage2"].id,
            time_slot=TimeSlot(
                datetime(2027, 6, 18, 21, 0), datetime(2027, 6, 18, 22, 0)
            ),
        )
    )
    use_case = RescheduleConcertUseCase(
        concert_repo=context["concert_repo"],
        festival_repo=context["festival_repo"],
        stage_repo=context["stage_repo"],
        artist_repo=context["artist_repo"],
        notification_sender=context["notif"],
        uow=context["uow"],
    )
    cmd = RescheduleConcertCommand(
        start_time=datetime(2027, 6, 18, 18, 30),
        end_time=datetime(2027, 6, 18, 19, 30),
    )
    with pytest.raises(ConcertConflictError, match="l'artiste est déjà programmé"):
        use_case.execute(c2.id, cmd)


def test_reschedule_rejected_if_festival_published(context):
    """Défaut 3 & R7 : Refuser la modification si le festival est publié."""
    context["festival"].status = "published"
    use_case = RescheduleConcertUseCase(
        concert_repo=context["concert_repo"],
        festival_repo=context["festival_repo"],
        stage_repo=context["stage_repo"],
        artist_repo=context["artist_repo"],
        notification_sender=context["notif"],
        uow=context["uow"],
    )
    cmd = RescheduleConcertCommand(
        start_time=datetime(2027, 6, 18, 20, 0),
        end_time=datetime(2027, 6, 18, 21, 0),
    )
    with pytest.raises(FestivalAlreadyPublishedError):
        use_case.execute(context["concert1"].id, cmd)


def test_reschedule_rolls_back_if_notification_fails(context):
    """Défaut 2 : Annuler l'écriture si la notification échoue dans l'UoW."""
    failing_notif = SpyNotificationSender(should_fail=True)
    use_case = RescheduleConcertUseCase(
        concert_repo=context["concert_repo"],
        festival_repo=context["festival_repo"],
        stage_repo=context["stage_repo"],
        artist_repo=context["artist_repo"],
        notification_sender=failing_notif,
        uow=context["uow"],
    )
    cmd = RescheduleConcertCommand(
        start_time=datetime(2027, 6, 18, 20, 0),
        end_time=datetime(2027, 6, 18, 21, 0),
    )
    with pytest.raises(RuntimeError):
        use_case.execute(context["concert1"].id, cmd)

    assert context["uow"].rolled_back is True


def test_create_concert_equipment_mismatch(context):
    """R5 : Refuser la programmation si l'équipement manque sur la scène."""
    art_with_pyro = context["artist_repo"].save(
        Artist(
            name="Pyro Metal",
            genre="Industrial",
            required_equipment=EquipmentSet.from_iterable(["Micro", "Pyrotechnie"]),
        )
    )
    use_case = CreateConcertUseCase(
        concert_repo=context["concert_repo"],
        festival_repo=context["festival_repo"],
        stage_repo=context["stage_repo"],
        artist_repo=context["artist_repo"],
        uow=context["uow"],
    )
    cmd = CreateConcertCommand(
        festival_id=context["festival"].id,
        artist_id=art_with_pyro.id,
        stage_id=context["stage2"].id,  # Stage 2 n'a pas "Pyrotechnie"
        start_time=datetime(2027, 6, 19, 14, 0),
        end_time=datetime(2027, 6, 19, 15, 0),
    )
    with pytest.raises(StageEquipmentMismatchError):
        use_case.execute(cmd)


def _create_uc(ctx):
    return CreateConcertUseCase(
        concert_repo=ctx["concert_repo"],
        festival_repo=ctx["festival_repo"],
        stage_repo=ctx["stage_repo"],
        artist_repo=ctx["artist_repo"],
        uow=ctx["uow"],
    )


def _cmd(ctx, stage_id, artist_id, start, end):
    return CreateConcertCommand(
        festival_id=ctx["festival"].id,
        artist_id=artist_id,
        stage_id=stage_id,
        start_time=start,
        end_time=end,
    )


def test_create_concert_conflict_on_same_stage(context):
    cmd = _cmd(
        context,
        context["stage1"].id,
        context["artist2"].id,
        datetime(2027, 6, 18, 18, 30),
        datetime(2027, 6, 18, 19, 30),
    )
    with pytest.raises(ConcertConflictError, match="la scène est déjà occupée"):
        _create_uc(context).execute(cmd)


def test_create_concert_r4_stage_of_other_festival(context):
    other = context["festival_repo"].save(
        Festival(
            name="Autre",
            location="Ailleurs",
            period=DateRange(datetime(2027, 7, 1, 10, 0), datetime(2027, 7, 3, 23, 0)),
        )
    )
    foreign_stage = context["stage_repo"].save(
        Stage(
            festival_id=other.id,
            name="Ailleurs Stage",
            capacity=100,
            available_equipment=EquipmentSet.from_iterable(["Micro"]),
        )
    )
    cmd = _cmd(
        context,
        foreign_stage.id,
        context["artist2"].id,
        datetime(2027, 6, 19, 14, 0),
        datetime(2027, 6, 19, 15, 0),
    )
    with pytest.raises(StageFestivalMismatchError):
        _create_uc(context).execute(cmd)


def test_create_concert_r6_outside_period(context):
    cmd = _cmd(
        context,
        context["stage2"].id,
        context["artist2"].id,
        datetime(2027, 6, 21, 14, 0),
        datetime(2027, 6, 21, 15, 0),
    )
    with pytest.raises(ConcertOutsideFestivalPeriodError):
        _create_uc(context).execute(cmd)


def test_create_concert_refused_if_festival_published(context):
    context["festival"].status = "published"
    cmd = _cmd(
        context,
        context["stage2"].id,
        context["artist2"].id,
        datetime(2027, 6, 19, 14, 0),
        datetime(2027, 6, 19, 15, 0),
    )
    with pytest.raises(FestivalAlreadyPublishedError):
        _create_uc(context).execute(cmd)


def test_cancel_concert_success(context):
    uc = CancelConcertUseCase(
        concert_repo=context["concert_repo"],
        festival_repo=context["festival_repo"],
        uow=context["uow"],
    )
    res = uc.execute(context["concert1"].id)
    assert res.is_cancelled
    assert context["uow"].committed is True


def test_cancel_concert_refused_if_festival_published(context):
    context["festival"].status = "published"
    uc = CancelConcertUseCase(
        concert_repo=context["concert_repo"],
        festival_repo=context["festival_repo"],
        uow=context["uow"],
    )
    with pytest.raises(FestivalAlreadyPublishedError):
        uc.execute(context["concert1"].id)


def test_reschedule_notification_mentions_old_and_new_time(context):
    uc = RescheduleConcertUseCase(
        concert_repo=context["concert_repo"],
        festival_repo=context["festival_repo"],
        stage_repo=context["stage_repo"],
        artist_repo=context["artist_repo"],
        notification_sender=context["notif"],
        uow=context["uow"],
    )
    uc.execute(
        context["concert1"].id,
        RescheduleConcertCommand(
            start_time=datetime(2027, 6, 18, 20, 0),
            end_time=datetime(2027, 6, 18, 21, 0),
        ),
    )
    _, message = context["notif"].notifications[0]
    assert "2027-06-18T18:00:00" in message and "2027-06-18T20:00:00" in message
