from app.adapters.inbound.api.artists import router as artists_router
from app.adapters.inbound.api.concerts import router as concerts_router
from app.adapters.inbound.api.festivals import router as festivals_router
from app.adapters.inbound.api.incidents import router as incidents_router
from app.adapters.inbound.api.stages import router as stages_router

__all__ = [
    "artists_router",
    "concerts_router",
    "festivals_router",
    "incidents_router",
    "stages_router",
]
