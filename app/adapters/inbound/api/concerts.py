"""
Adaptateur entrant HTTP (FastAPI) pour les concerts.
Délègue exclusivement aux cas d'utilisation applicatifs.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.application.dtos import CreateConcertCommand, RescheduleConcertCommand
from app.application.use_cases.concert_use_cases import (
    CancelConcertUseCase,
    CreateConcertUseCase,
    GetConcertUseCase,
    ListConcertsUseCase,
    RescheduleConcertUseCase,
)
from app.dependencies import (
    get_cancel_concert_use_case,
    get_create_concert_use_case,
    get_get_concert_use_case,
    get_list_concerts_use_case,
    get_reschedule_concert_use_case,
)
from app.domain.entities.concert import Concert
from app.domain.exceptions import DomainError, EntityNotFoundError
from app.schemas import ConcertCreate, ConcertRead, ConcertReschedule

router = APIRouter(prefix="/concerts", tags=["concerts"])


def concert_to_dto(c: Concert) -> dict:
    return {
        "id": c.id,
        "festival_id": c.festival_id,
        "artist_id": c.artist_id,
        "stage_id": c.stage_id,
        "start_time": c.time_slot.start_time,
        "end_time": c.time_slot.end_time,
        "status": c.status,
    }


@router.get("", response_model=list[ConcertRead])
def list_concerts(
    festival_id: int,
    use_case: ListConcertsUseCase = Depends(get_list_concerts_use_case),
):
    concerts = use_case.execute(festival_id)
    return [concert_to_dto(c) for c in concerts]


@router.get("/{concert_id}", response_model=ConcertRead)
def get_concert(
    concert_id: int,
    use_case: GetConcertUseCase = Depends(get_get_concert_use_case),
):
    try:
        c = use_case.execute(concert_id)
        return concert_to_dto(c)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("", response_model=ConcertRead, status_code=201)
def create_concert(
    payload: ConcertCreate,
    use_case: CreateConcertUseCase = Depends(get_create_concert_use_case),
):
    cmd = CreateConcertCommand(
        festival_id=payload.festival_id,
        artist_id=payload.artist_id,
        stage_id=payload.stage_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
    )
    try:
        concert = use_case.execute(cmd)
        return concert_to_dto(concert)
    except (DomainError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/{concert_id}/reschedule", response_model=ConcertRead)
def reschedule_concert(
    concert_id: int,
    payload: ConcertReschedule,
    use_case: RescheduleConcertUseCase = Depends(get_reschedule_concert_use_case),
):
    cmd = RescheduleConcertCommand(
        start_time=payload.start_time,
        end_time=payload.end_time,
    )
    try:
        concert = use_case.execute(concert_id, cmd)
        return concert_to_dto(concert)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except (DomainError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        # Erreur lors d'un effet secondaire (notification)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/{concert_id}/cancel", response_model=ConcertRead)
def cancel_concert(
    concert_id: int,
    use_case: CancelConcertUseCase = Depends(get_cancel_concert_use_case),
):
    try:
        c = use_case.execute(concert_id)
        return concert_to_dto(c)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/schedule/{festival_id}", response_model=list[ConcertRead])
def get_schedule(
    festival_id: int,
    use_case: ListConcertsUseCase = Depends(get_list_concerts_use_case),
):
    concerts = use_case.execute(festival_id)
    return [concert_to_dto(c) for c in concerts]
