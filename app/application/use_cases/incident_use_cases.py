"""
Cas d'utilisation relatifs aux incidents (R10) :
- Signalement d'un incident
- Consultation des incidents
"""

from datetime import datetime
from app.application.dtos import CreateIncidentCommand
from app.application.ports.repositories import ConcertRepositoryPort, IncidentRepositoryPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.incident import Incident
from app.domain.exceptions import EntityNotFoundError


class CreateIncidentUseCase:
    def __init__(
        self,
        incident_repo: IncidentRepositoryPort,
        concert_repo: ConcertRepositoryPort,
        uow: UnitOfWorkPort,
    ):
        self.incident_repo = incident_repo
        self.concert_repo = concert_repo
        self.uow = uow

    def execute(self, cmd: CreateIncidentCommand) -> Incident:
        # R10 : Le concert associé doit exister
        concert = self.concert_repo.get_by_id(cmd.concert_id)
        if concert is None:
            raise EntityNotFoundError("Concert introuvable")

        occurred = cmd.occurred_at or datetime.utcnow()
        incident = Incident(
            concert_id=cmd.concert_id,
            description=cmd.description,
            occurred_at=occurred,
        )

        with self.uow:
            saved = self.incident_repo.save(incident)
            self.uow.commit()

        return saved


class ListIncidentsUseCase:
    def __init__(self, incident_repo: IncidentRepositoryPort):
        self.incident_repo = incident_repo

    def execute(self, concert_id: int | None = None) -> list[Incident]:
        return self.incident_repo.list_all(concert_id=concert_id)
