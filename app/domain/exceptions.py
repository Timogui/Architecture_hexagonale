"""
Exceptions métier du Domaine FestiPlan (Python pur, indépendant de HTTP).
"""


class DomainError(Exception):
    """Exception de base pour toutes les erreurs du domaine."""

    pass


class InvalidTimeSlotError(DomainError):
    """R1 & R9 : Créneau horaire invalide (ex: fin <= début)."""

    pass


class InvalidDateRangeError(DomainError):
    """R6 & R9 : Période de festival invalide."""

    pass


class ConcertConflictError(DomainError):
    """R2 & R3 : Conflit de programmation (scène occupée ou artiste indisponible)."""

    pass


class StageCapacityError(DomainError):
    """R9 : La capacité d'une scène doit être strictement positive."""

    pass


class StageEquipmentMismatchError(DomainError):
    """R5 : La scène ne dispose pas de tous les équipements requis par l'artiste."""

    pass


class StageFestivalMismatchError(DomainError):
    """R4 : La scène n'appartient pas au festival sélectionné."""

    pass


class ConcertOutsideFestivalPeriodError(DomainError):
    """R6 : Le concert doit se dérouler entièrement pendant la période du festival."""

    pass


class FestivalAlreadyPublishedError(DomainError):
    """R7 : Un planning publié ne peut pas être modifié par une opération ordinaire."""

    pass


class FestivalCannotBePublishedError(DomainError):
    """R8 : Un planning ne peut être publié s'il contient des incohérences ou conflits."""

    pass


class InvalidIncidentError(DomainError):
    """R10 : Description vide ou concert associé invalide."""

    pass


class EntityNotFoundError(DomainError):
    """Entité demandée introuvable."""

    pass
