"""
Adaptateur entrant HTTP (FastAPI) pour les artistes.
Délègue aux cas d'utilisation applicatifs.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.application.dtos import CreateArtistCommand
from app.application.use_cases.artist_use_cases import (
    CreateArtistUseCase,
    ListArtistsUseCase,
)
from app.dependencies import get_create_artist_use_case, get_list_artists_use_case
from app.domain.entities.artist import Artist
from app.domain.exceptions import DomainError
from app.schemas import ArtistCreate, ArtistRead

router = APIRouter(prefix="/artists", tags=["artists"])


def artist_to_dto(a: Artist) -> dict:
    return {
        "id": a.id,
        "name": a.name,
        "genre": a.genre,
        "required_equipment": a.required_equipment.to_list(),
    }


@router.get("", response_model=list[ArtistRead])
def list_artists(
    use_case: ListArtistsUseCase = Depends(get_list_artists_use_case),
):
    artists = use_case.execute()
    return [artist_to_dto(a) for a in artists]


@router.post("", response_model=ArtistRead, status_code=201)
def create_artist(
    payload: ArtistCreate,
    use_case: CreateArtistUseCase = Depends(get_create_artist_use_case),
):
    cmd = CreateArtistCommand(
        name=payload.name,
        genre=payload.genre,
        required_equipment=payload.required_equipment,
    )
    try:
        artist = use_case.execute(cmd)
        return artist_to_dto(artist)
    except (DomainError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
