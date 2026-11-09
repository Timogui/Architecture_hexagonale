"""
Cas d'utilisation relatifs aux concerts :
- Reprogrammer un concert (Correction Défauts 1, 2, 3)
- Créer un concert
- Annuler un concert
- Consulter un concert et le planning
"""

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
    ConcertConflictError,
    ConcertOutsideFestivalPeriodError,
    EntityNotFoundError,
    StageEquipmentMismatchError,
    StageFestivalMismatchError,
)
from app.domain.value_objects.time_slot import TimeSlot


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

        # 2. Récupération du concert
        concert = self.concert_repo.get_by_id(concert_id)
        if concert is None:
            raise EntityNotFoundError("Concert introuvable")

        # 3. Récupération du festival et contrôle du statut publié (R7 - Défaut 3)
        festival = self.festival_repo.get_by_id(concert.festival_id)
        if festival is None:
            raise EntityNotFoundError("Festival introuvable")
        festival.ensure_can_modify_schedule()

        # 4. Vérification que le créneau est inclus dans le festival (R6)
        if not festival.contains_slot(new_slot):
            raise ConcertOutsideFestivalPeriodError("Le concert doit se dérouler pendant le festival")

        # 5. Contrôle des conflits de programmation (R2 & R3 - Défaut 1)
        existing_concerts = self.concert_repo.list_by_festival(concert.festival_id)
        for other in existing_concerts:
            if other.id == concert.id or other.is_cancelled:
                continue
            if other.time_slot.overlaps(new_slot):
                if other.stage_id == concert.stage_id:
                    raise ConcertConflictError("Conflit : la scène est déjà occupée")
                if other.artist_id == concert.artist_id:
                    raise ConcertConflictError("Conflit : l'artiste est déjà programmé")

        # 6. Contrôle des équipements requis (R5)
        artist = self.artist_repo.get_by_id(concert.artist_id)
        stage = self.stage_repo.get_by_id(concert.stage_id)
        if artist and stage and not stage.can_host_artist(artist.required_equipment):
            raise StageEquipmentMismatchError("La scène ne dispose pas de tous les équipements requis")

        # 7. Application de la modification
        concert.reschedule(new_slot)

        # 8. Persistance atomique et notification (Défaut 2)
        # Si la notification échoue, la transaction est annulée et rien n'est persisté en BD.
        with self.uow:
            saved = self.concert_repo.save(concert)
            self.notification_sender.notify_schedule_change(
                concert.id,
                f"Concert déplacé au {concert.time_slot.start_time.isoformat()}",
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

        if stage.festival_id != festival.id:
            raise StageFestivalMismatchError("La scène n'appartient pas à ce festival")

        if not festival.contains_slot(slot):
            raise ConcertOutsideFestivalPeriodError("Le concert doit se dérouler pendant le festival")

        # Vérification des conflits (R2 & R3)
        existing = self.concert_repo.list_by_festival(festival.id)
        for c in existing:
            if not c.is_cancelled and c.time_slot.overlaps(slot):
                if c.stage_id == cmd.stage_id:
                    raise ConcertConflictError("Conflit : la scène est déjà occupée")
                if c.artist_id == cmd.artist_id:
                    raise ConcertConflictError("Conflit : l'artiste est déjà programmé")

        # Vérification des équipements (R5)
        if not stage.can_host_artist(artist.required_equipment):
            raise StageEquipmentMismatchError("La scène ne dispose pas de tous les équipements requis")

        concert = Concert(
            festival_id=cmd.festival_id,
            artist_id=cmd.artist_id,
            stage_id=cmd.stage_id,
            time_slot=slot,
            status="scheduled",
        )

        with self.uow:
            saved = self.concert_repo.save(concert)
            self.uow.commit()

        return saved


class CancelConcertUseCase:
    def __init__(self, concert_repo: ConcertRepositoryPort, uow: UnitOfWorkPort):
        self.concert_repo = concert_repo
        self.uow = uow

    def execute(self, concert_id: int) -> Concert:
        concert = self.concert_repo.get_by_id(concert_id)
        if concert is None:
            raise EntityNotFoundError("Concert introuvable")

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
