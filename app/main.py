from fastapi import FastAPI

from app import models  # noqa: F401
from app.adapters.inbound.api import (
    artists_router,
    concerts_router,
    festivals_router,
    incidents_router,
    stages_router,
)
from app.config import settings
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="API FestiPlan refactorisée en Architecture Hexagonale et DDD",
)

for router in (
    festivals_router,
    artists_router,
    stages_router,
    concerts_router,
    incidents_router,
):
    app.include_router(router)


@app.get("/")
def health():
    return {"message": "Bienvenue sur FestiPlan", "status": "ok"}
