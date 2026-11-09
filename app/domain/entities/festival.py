"""
Entité Métier & Racine d'agrégat : Festival.
Gère son cycle de vie (préparation -> publié) et garantit les invariants R7 & R8.
"""

from dataclasses import dataclass
from app.domain.exceptions import (
    FestivalAlreadyPublishedError,
    FestivalCannotBePublishedError,
    DomainError,
)
from app.domain.value_objects.date_range import DateRange
from app.domain.value_objects.time_slot import TimeSlot


@dataclass
class Festival:
    name: str
    location: str
    period: DateRange
    status: str = "preparation"
    id: int | None = None

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise DomainError("Le nom du festival ne peut pas être vide.")
        if not self.location or not self.location.strip():
            raise DomainError("Le lieu du festival ne peut pas être vide.")

    @property
    def is_published(self) -> bool:
        return self.status == "published"

    def ensure_can_modify_schedule(self) -> None:
        """Vérifie si le planning peut être modifié (R7 - Défaut 3)."""
        if self.is_published:
            raise FestivalAlreadyPublishedError(
                f"R7 : Le festival '{self.name}' est déjà publié. "
                "Le déplacement ou la modification de concerts nécessite une procédure explicite."
            )

    def publish(self, concerts: list = None) -> None:
        """Publie le festival après vérification des règles de programmation (R8)."""
        if concerts:
            for c in concerts:
                if not self.contains_slot(c.time_slot):
                    raise FestivalCannotBePublishedError(
                        f"R8 : Impossible de publier : le concert {c.id} est hors de la période du festival."
                    )
            # Vérifier qu'aucun concert ne conflite avant publication
            for i, c1 in enumerate(concerts):
                for c2 in concerts[i + 1 :]:
                    if c1.conflicts_with(c2):
                        raise FestivalCannotBePublishedError(
                            f"R8 : Impossible de publier le planning : conflit détecté entre concerts ({c1.id} et {c2.id})."
                        )
        self.status = "published"

    def contains_slot(self, slot: TimeSlot) -> bool:
        """Vérifie si un créneau s'inscrit dans la période du festival (R6)."""
        return self.period.contains(slot)
