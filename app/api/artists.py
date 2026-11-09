"""
Point d'entrée de compatibilité pour le routeur artistes.
L'implémentation propre réside dans app.adapters.inbound.api.artists.
"""

from app.adapters.inbound.api.artists import router

__all__ = ["router"]
