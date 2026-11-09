"""
Point d'entrée de compatibilité pour le routeur festivals.
L'implémentation propre réside dans app.adapters.inbound.api.festivals.
"""

from app.adapters.inbound.api.festivals import router

__all__ = ["router"]
