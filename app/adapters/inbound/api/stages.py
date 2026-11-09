"""
Adaptateur entrant HTTP (FastAPI) pour les scènes.
Délègue aux cas d'utilisation applicatifs.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.application.dtos import CreateStageCommand
from app.application.use_cases.stage_use_cases import (
    CreateStageUseCase,
    ListStagesUseCase,
)
from app.dependencies import get_create_stage_use_case, get_list_stages_use_case
from app.domain.entities.stage import Stage
from app.domain.exceptions import DomainError, EntityNotFoundError
from app.schemas import StageCreate, StageRead

router = APIRouter(prefix="/stages", tags=["stages"])


def stage_to_dto(s: Stage) -> dict:
    return {
        "id": s.id,
        "festival_id": s.festival_id,
        "name": s.name,
        "capacity": s.capacity,
        "available_equipment": s.available_equipment.to_list(),
    }


@router.get("", response_model=list[StageRead])
def list_stages(
    festival_id: int,
    use_case: ListStagesUseCase = Depends(get_list_stages_use_case),
):
    stages = use_case.execute(festival_id)
    return [stage_to_dto(s) for s in stages]


@router.post("", response_model=StageRead, status_code=201)
def create_stage(
    payload: StageCreate,
    use_case: CreateStageUseCase = Depends(get_create_stage_use_case),
):
    cmd = CreateStageCommand(
        festival_id=payload.festival_id,
        name=payload.name,
        capacity=payload.capacity,
        available_equipment=payload.available_equipment,
    )
    try:
        stage = use_case.execute(cmd)
        return stage_to_dto(stage)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except (DomainError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
