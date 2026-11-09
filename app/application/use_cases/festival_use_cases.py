"""
Cas d'utilisation relatifs aux festivals :
- Création d'un festival
- Publication du planning officiel (R8)
- Consultation des festivals
"""

from app.application.dtos import CreateFestivalCommand
from app.application.ports.notification_port import NotificationPort
from app.application.ports.repositories import (
    ConcertRepositoryPort,
    FestivalRepositoryPort,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.festival import Festival
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.date_range import DateRange


class CreateFestivalUseCase:
    def __init__(self, festival_repo: FestivalRepositoryPort, uow: UnitOfWorkPort):
        self.festival_repo = festival_repo
        self.uow = uow

    def execute(self, cmd: CreateFestivalCommand) -> Festival:
        period = DateRange(start_date=cmd.start_date, end_date=cmd.end_date)
        festival = Festival(
            name=cmd.name,
            location=cmd.location,
            period=period,
            status="preparation",
        )
        with self.uow:
            saved = self.festival_repo.save(festival)
            self.uow.commit()
        return saved


class PublishFestivalUseCase:
    def __init__(
        self,
        festival_repo: FestivalRepositoryPort,
        concert_repo: ConcertRepositoryPort,
        notification_sender: NotificationPort,
        uow: UnitOfWorkPort,
    ):
        self.festival_repo = festival_repo
        self.concert_repo = concert_repo
        self.notification_sender = notification_sender
        self.uow = uow

    def execute(self, festival_id: int) -> Festival:
        festival = self.festival_repo.get_by_id(festival_id)
        if festival is None:
            raise EntityNotFoundError("Festival introuvable")

        concerts = self.concert_repo.list_by_festival(festival_id)
        festival.publish(concerts)

        with self.uow:
            saved = self.festival_repo.save(festival)
            self.notification_sender.notify_schedule_change(
                festival.id,
                f"Le planning du festival {festival.name} a été publié.",
            )
            self.uow.commit()

        return saved


class ListFestivalsUseCase:
    def __init__(self, festival_repo: FestivalRepositoryPort):
        self.festival_repo = festival_repo

    def execute(self) -> list[Festival]:
        return self.festival_repo.list_all()


class GetFestivalUseCase:
    def __init__(self, festival_repo: FestivalRepositoryPort):
        self.festival_repo = festival_repo

    def execute(self, festival_id: int) -> Festival:
        festival = self.festival_repo.get_by_id(festival_id)
        if festival is None:
            raise EntityNotFoundError("Festival introuvable")
        return festival
