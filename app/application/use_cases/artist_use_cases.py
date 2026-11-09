"""
Cas d'utilisation relatifs aux artistes :
- Création d'un artiste
- Liste des artistes
"""

from app.application.dtos import CreateArtistCommand
from app.application.ports.repositories import ArtistRepositoryPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities.artist import Artist
from app.domain.value_objects.equipment import EquipmentSet


class CreateArtistUseCase:
    def __init__(self, artist_repo: ArtistRepositoryPort, uow: UnitOfWorkPort):
        self.artist_repo = artist_repo
        self.uow = uow

    def execute(self, cmd: CreateArtistCommand) -> Artist:
        equipment = EquipmentSet.from_iterable(cmd.required_equipment)
        artist = Artist(
            name=cmd.name,
            genre=cmd.genre,
            required_equipment=equipment,
        )
        with self.uow:
            saved = self.artist_repo.save(artist)
            self.uow.commit()
        return saved


class ListArtistsUseCase:
    def __init__(self, artist_repo: ArtistRepositoryPort):
        self.artist_repo = artist_repo

    def execute(self) -> list[Artist]:
        return self.artist_repo.list_all()
