from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.session import check_database_connection


app = FastAPI(
    title="Campus Cat Backend",
    version="0.1.0",
    description="Backend API for the campus stray cat recognition and archive system.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def root() -> dict:
    return {
        "service": "backend",
        "status": "ok",
        "message": "Campus Cat backend is running.",
    }


@app.get("/health")
def health() -> dict:
    db_ok, detail = check_database_connection()
    return {
        "service": "backend",
        "status": "ok" if db_ok else "degraded",
        "database": {
            "connected": db_ok,
            "detail": detail,
        },
    }
