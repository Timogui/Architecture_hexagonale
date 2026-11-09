"""
Point d'entrée de compatibilité pour le routeur concerts.
L'implémentation propre réside dans app.adapters.inbound.api.concerts.
"""

from app.adapters.inbound.api.concerts import router

__all__ = ["router"]
