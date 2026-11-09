"""
Entité Métier : Incident.
Protège l'invariant R10 (concert existant, description non vide).
"""

from dataclasses import dataclass
from datetime import datetime
from app.domain.exceptions import InvalidIncidentError


@dataclass
class Incident:
    concert_id: int
    description: str
    occurred_at: datetime
    resolved: bool = False
    id: int | None = None

    def __post_init__(self):
        if not self.description or not self.description.strip():
            raise InvalidIncidentError("R10 : La description d'un incident ne peut pas être vide.")
        if self.concert_id is None or self.concert_id <= 0:
            raise InvalidIncidentError("R10 : Un incident doit obligatoirement être rattaché à un concert valide.")

    def resolve(self) -> None:
        self.resolved = True
