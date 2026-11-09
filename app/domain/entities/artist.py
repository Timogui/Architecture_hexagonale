"""
Entité Métier : Artiste.
"""

from dataclasses import dataclass
from app.domain.exceptions import DomainError
from app.domain.value_objects.equipment import EquipmentSet


@dataclass
class Artist:
    name: str
    genre: str
    required_equipment: EquipmentSet
    id: int | None = None

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise DomainError("Le nom de l'artiste ne peut pas être vide.")
        if not self.genre or not self.genre.strip():
            raise DomainError("Le genre musical de l'artiste ne peut pas être vide.")
