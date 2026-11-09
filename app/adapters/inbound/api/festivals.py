"""
Adaptateur entrant HTTP (FastAPI) pour les festivals.
Délègue aux cas d'utilisation applicatifs.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.application.dtos import CreateFestivalCommand
from app.application.use_cases.festival_use_cases import (
    CreateFestivalUseCase,
    ListFestivalsUseCase,
    PublishFestivalUseCase,
)
from app.dependencies import (
    get_create_festival_use_case,
    get_list_festivals_use_case,
    get_publish_festival_use_case,
)
from app.domain.entities.festival import Festival
from app.domain.exceptions import DomainError, EntityNotFoundError
from app.schemas import FestivalCreate, FestivalRead

router = APIRouter(prefix="/festivals", tags=["festivals"])


def festival_to_dto(f: Festival) -> dict:
    return {
        "id": f.id,
        "name": f.name,
        "location": f.location,
        "start_date": f.period.start_date,
        "end_date": f.period.end_date,
        "status": f.status,
    }


@router.get("", response_model=list[FestivalRead])
def list_festivals(
    use_case: ListFestivalsUseCase = Depends(get_list_festivals_use_case),
):
    festivals = use_case.execute()
    return [festival_to_dto(f) for f in festivals]


@router.post("", response_model=FestivalRead, status_code=201)
def create_festival(
    payload: FestivalCreate,
    use_case: CreateFestivalUseCase = Depends(get_create_festival_use_case),
):
    cmd = CreateFestivalCommand(
        name=payload.name,
        location=payload.location,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    try:
        festival = use_case.execute(cmd)
        return festival_to_dto(festival)
    except (DomainError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{festival_id}/publish", response_model=FestivalRead)
def publish_festival(
    festival_id: int,
    use_case: PublishFestivalUseCase = Depends(get_publish_festival_use_case),
):
    try:
        festival = use_case.execute(festival_id)
        return festival_to_dto(festival)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except (DomainError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
