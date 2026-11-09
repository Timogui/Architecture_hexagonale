from app.domain.entities.concert import Concert
from app.domain.exceptions import ConcertConflictError

_MESSAGES = {
    "stage": "Conflit : la scène est déjà occupée",
    "artist": "Conflit : l'artiste est déjà programmé",
}


def ensure_no_conflict(candidate: Concert, existing: list[Concert]) -> None:
    for other in existing:
        reason = candidate.conflict_reason(other)
        if reason is not None:
            raise ConcertConflictError(_MESSAGES[reason])
