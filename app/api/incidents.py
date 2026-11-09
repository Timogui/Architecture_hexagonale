"""
Point d'entrée de compatibilité pour le routeur incidents.
L'implémentation propre réside dans app.adapters.inbound.api.incidents.
"""

from app.adapters.inbound.api.incidents import router

__all__ = ["router"]
