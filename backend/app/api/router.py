from fastapi import APIRouter

from app.api.routes import cats, sightings, upload


api_router = APIRouter()
api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(cats.router, tags=["cats"])
api_router.include_router(sightings.router, tags=["sightings"])
