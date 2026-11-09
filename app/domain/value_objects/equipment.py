"""
Objet-Valeur : Ensemble d'équipements techniques (EquipmentSet).
Immuable et auto-validant (R5).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EquipmentSet:
    items: frozenset[str]

    @classmethod
    def from_iterable(cls, items: list[str] | set[str] | str) -> "EquipmentSet":
        if isinstance(items, str):
            parsed = [x.strip() for x in items.split(",") if x.strip()]
            return cls(frozenset(parsed))
        return cls(frozenset(x.strip() for x in items if x and x.strip()))

    def is_satisfied_by(self, available: "EquipmentSet") -> bool:
        """Vérifie si tous les équipements requis sont présents parmi les disponibles (R5)."""
        return self.items.issubset(available.items)

    def to_list(self) -> list[str]:
        return sorted(list(self.items))

    def to_csv(self) -> str:
        return ",".join(sorted(list(self.items)))
