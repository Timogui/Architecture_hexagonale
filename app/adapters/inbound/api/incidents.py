"""
Adaptateur entrant HTTP (FastAPI) pour les incidents.
Délègue aux cas d'utilisation applicatifs.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.application.dtos import CreateIncidentCommand
from app.application.use_cases.incident_use_cases import (
    CreateIncidentUseCase,
    ListIncidentsUseCase,
)
from app.dependencies import get_create_incident_use_case, get_list_incidents_use_case
from app.domain.entities.incident import Incident
from app.domain.exceptions import DomainError, EntityNotFoundError
from app.schemas import IncidentCreate, IncidentRead

router = APIRouter(prefix="/incidents", tags=["incidents"])


def incident_to_dto(i: Incident) -> dict:
    return {
        "id": i.id,
        "concert_id": i.concert_id,
        "description": i.description,
        "occurred_at": i.occurred_at,
        "resolved": i.resolved,
    }


@router.post("", response_model=IncidentRead, status_code=201)
def create_incident(
    payload: IncidentCreate,
    use_case: CreateIncidentUseCase = Depends(get_create_incident_use_case),
):
    cmd = CreateIncidentCommand(
        concert_id=payload.concert_id,
        description=payload.description,
        occurred_at=payload.occurred_at,
    )
    try:
        incident = use_case.execute(cmd)
        return incident_to_dto(incident)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except (DomainError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("", response_model=list[IncidentRead])
def list_incidents(
    concert_id: int | None = None,
    use_case: ListIncidentsUseCase = Depends(get_list_incidents_use_case),
):
    incidents = use_case.execute(concert_id=concert_id)
    return [incident_to_dto(i) for i in incidents]
