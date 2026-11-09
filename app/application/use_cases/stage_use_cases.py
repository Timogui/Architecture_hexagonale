"""
Cas d'utilisation relatifs aux scènes :
- Création d'une scène (R9)
- Liste des scènes d'un festival
"""

from app.application.dtos import CreateStageCommand
from app.application.ports.repositories import (
    FestivalRepositoryPort,
    StageRepositoryPort,
)
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.stage import Stage
from app.domain.exceptions import EntityNotFoundError
from app.domain.value_objects.equipment import EquipmentSet


class CreateStageUseCase:
    def __init__(
        self,
        stage_repo: StageRepositoryPort,
        festival_repo: FestivalRepositoryPort,
        uow: UnitOfWorkPort,
    ):
        self.stage_repo = stage_repo
        self.festival_repo = festival_repo
        self.uow = uow

    def execute(self, cmd: CreateStageCommand) -> Stage:
        festival = self.festival_repo.get_by_id(cmd.festival_id)
        if festival is None:
            raise EntityNotFoundError("Festival introuvable")

        equipment = EquipmentSet.from_iterable(cmd.available_equipment)
        stage = Stage(
            festival_id=cmd.festival_id,
            name=cmd.name,
            capacity=cmd.capacity,
            available_equipment=equipment,
        )

        with self.uow:
            saved = self.stage_repo.save(stage)
            self.uow.commit()

        return saved


class ListStagesUseCase:
    def __init__(self, stage_repo: StageRepositoryPort):
        self.stage_repo = stage_repo

    def execute(self, festival_id: int) -> list[Stage]:
        return self.stage_repo.list_by_festival(festival_id)
