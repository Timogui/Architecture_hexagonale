"""
Entité Métier : Scène (Stage).
Protège l'invariant R9 (capacité > 0).
"""

from dataclasses import dataclass
from app.domain.exceptions import StageCapacityError, DomainError
from app.domain.value_objects.equipment import EquipmentSet


@dataclass
class Stage:
    festival_id: int
    name: str
    capacity: int
    available_equipment: EquipmentSet
    id: int | None = None

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise DomainError("Le nom de la scène ne peut pas être vide.")
        if self.capacity <= 0:
            raise StageCapacityError(
                f"R9 : La capacité de la scène '{self.name}' doit être strictement positive (reçu: {self.capacity})."
            )

    def can_host_artist(self, artist_equipment: EquipmentSet) -> bool:
        """Vérifie si la scène a l'équipement nécessaire pour l'artiste (R5)."""
        return artist_equipment.is_satisfied_by(self.available_equipment)
