"""
Cas d'utilisation relatifs aux concerts :
- Reprogrammer un concert (Correction Défauts 1, 2, 3)
- Créer un concert
- Annuler un concert
- Consulter un concert et le planning
"""

from dataclasses import replace
from app.application.dtos import CreateConcertCommand, RescheduleConcertCommand
from app.application.ports.notification_port import NotificationPort
from app.application.ports.repositories import (
    ArtistRepositoryPort,
    ConcertRepositoryPort,
    FestivalRepositoryPort,
    StageRepositoryPort,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.concert import Concert
from app.domain.exceptions import (
    ConcertOutsideFestivalPeriodError,
    EntityNotFoundError,
    StageEquipmentMismatchError,
    StageFestivalMismatchError,
)
from app.domain.value_objects.time_slot import TimeSlot
from app.domain.services.scheduling_policy import ensure_no_conflict


class RescheduleConcertUseCase:
    def __init__(
        self,
        concert_repo: ConcertRepositoryPort,
        festival_repo: FestivalRepositoryPort,
        stage_repo: StageRepositoryPort,
        artist_repo: ArtistRepositoryPort,
        notification_sender: NotificationPort,
        uow: UnitOfWorkPort,
    ):
        self.concert_repo = concert_repo
        self.festival_repo = festival_repo
        self.stage_repo = stage_repo
        self.artist_repo = artist_repo
        self.notification_sender = notification_sender
        self.uow = uow

    def execute(self, concert_id: int, cmd: RescheduleConcertCommand) -> Concert:
        # 1. Validation de la validité du créneau (R1)
        new_slot = TimeSlot(cmd.start_time, cmd.end_time)

        concert = self.concert_repo.get_by_id(concert_id)
        if concert is None:
            raise EntityNotFoundError("Concert introuvable")

        # 2. Récupération du festival et contrôle du statut publié (R7 - Défaut 3)
        festival = self.festival_repo.get_by_id(concert.festival_id)
        if festival is None:
            raise EntityNotFoundError("Festival introuvable")
        festival.ensure_can_modify_schedule()

        # 3. Vérification que le créneau est inclus dans le festival (R6)
        if not festival.contains_slot(new_slot):
            raise ConcertOutsideFestivalPeriodError("Le concert doit se dérouler pendant le festival")

        # 4. Contrôle des conflits de programmation (R2 & R3 - Défaut 1)
        candidate = replace(concert, time_slot=new_slot)
        existing_concerts = self.concert_repo.list_by_festival(concert.festival_id)
        ensure_no_conflict(candidate, existing_concerts)

        # 5. Contrôle des équipements requis (R5)
        artist = self.artist_repo.get_by_id(concert.artist_id)
        stage = self.stage_repo.get_by_id(concert.stage_id)
        if artist and stage and not stage.can_host_artist(artist.required_equipment):
            raise StageEquipmentMismatchError("La scène ne dispose pas de tous les équipements requis")

        event = concert.reschedule(new_slot)

        # 6. Persistance atomique et notification (Défaut 2)
        # Si la notification échoue, la transaction est annulée et rien n'est persisté en BD.
        with self.uow:
            saved = self.concert_repo.save(concert)
            self.notification_sender.notify_schedule_change(
                event.concert_id,
                f"Concert déplacé du {event.old_time_slot.start_time.isoformat()} "
                f"au {event.new_time_slot.start_time.isoformat()}",
            )
            self.uow.commit()

        return saved


class CreateConcertUseCase:
    def __init__(
        self,
        concert_repo: ConcertRepositoryPort,
        festival_repo: FestivalRepositoryPort,
        stage_repo: StageRepositoryPort,
        artist_repo: ArtistRepositoryPort,
        uow: UnitOfWorkPort,
    ):
        self.concert_repo = concert_repo
        self.festival_repo = festival_repo
        self.stage_repo = stage_repo
        self.artist_repo = artist_repo
        self.uow = uow

    def execute(self, cmd: CreateConcertCommand) -> Concert:
        slot = TimeSlot(cmd.start_time, cmd.end_time)

        festival = self.festival_repo.get_by_id(cmd.festival_id)
        artist = self.artist_repo.get_by_id(cmd.artist_id)
        stage = self.stage_repo.get_by_id(cmd.stage_id)

        if festival is None or artist is None or stage is None:
            raise EntityNotFoundError("Festival, artiste ou scène introuvable")
        festival.ensure_can_modify_schedule()

        if stage.festival_id != festival.id:
            raise StageFestivalMismatchError("La scène n'appartient pas à ce festival")

        if not festival.contains_slot(slot):
            raise ConcertOutsideFestivalPeriodError("Le concert doit se dérouler pendant le festival")


        concert = Concert(
            festival_id=cmd.festival_id,
            artist_id=cmd.artist_id,
            stage_id=cmd.stage_id,
            time_slot=slot,
            status="scheduled",
        )

        ensure_no_conflict(concert, self.concert_repo.list_by_festival(festival.id))

        # Vérification des équipements (R5)
        if not stage.can_host_artist(artist.required_equipment):
            raise StageEquipmentMismatchError("La scène ne dispose pas de tous les équipements requis")

        with self.uow:
            saved = self.concert_repo.save(concert)
            self.uow.commit()

        return saved


class CancelConcertUseCase:
    def __init__(
        self,
        concert_repo: ConcertRepositoryPort,
        festival_repo: FestivalRepositoryPort,
        uow: UnitOfWorkPort,
    ):
        self.concert_repo = concert_repo
        self.festival_repo = festival_repo
        self.uow = uow

    def execute(self, concert_id: int) -> Concert:
        concert = self.concert_repo.get_by_id(concert_id)
        if concert is None:
            raise EntityNotFoundError("Concert introuvable")

        festival = self.festival_repo.get_by_id(concert.festival_id)
        if festival is None:
            raise EntityNotFoundError("Festival introuvable")
        festival.ensure_can_modify_schedule()  # R7

        concert.cancel()

        with self.uow:
            saved = self.concert_repo.save(concert)
            self.uow.commit()

        return saved


class GetConcertUseCase:
    def __init__(self, concert_repo: ConcertRepositoryPort):
        self.concert_repo = concert_repo

    def execute(self, concert_id: int) -> Concert:
        concert = self.concert_repo.get_by_id(concert_id)
        if concert is None:
            raise EntityNotFoundError("Concert introuvable")
        return concert


class ListConcertsUseCase:
    def __init__(self, concert_repo: ConcertRepositoryPort):
        self.concert_repo = concert_repo

    def execute(self, festival_id: int) -> list[Concert]:
        return self.concert_repo.list_by_festival(festival_id)
