from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.cat_profile import (
    CatProfile,
    PROFILE_SOURCE_REAL,
    PROFILE_SOURCE_SAMPLE,
    PROFILE_SOURCE_TEST,
)
from app.schemas.cat import CatProfileCreate, ProfileSource

ALL_PROFILE_SOURCES: tuple[ProfileSource, ...] = (
    PROFILE_SOURCE_REAL,
    PROFILE_SOURCE_SAMPLE,
    PROFILE_SOURCE_TEST,
)


class CatService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_profiles(
        self,
        *,
        allowed_sources: tuple[ProfileSource, ...] = (PROFILE_SOURCE_REAL,),
    ) -> list[CatProfile]:
        statement = (
            select(CatProfile)
            .where(CatProfile.profile_source.in_(allowed_sources))
            .order_by(CatProfile.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_profile(
        self,
        cat_id: int,
        *,
        allowed_sources: tuple[ProfileSource, ...] = (PROFILE_SOURCE_REAL,),
    ) -> CatProfile | None:
        statement = (
            select(CatProfile)
            .options(
                selectinload(CatProfile.images),
                selectinload(CatProfile.sightings),
            )
            .where(
                CatProfile.id == cat_id,
                CatProfile.profile_source.in_(allowed_sources),
            )
        )
        return self.db.scalars(statement).first()

    def create_profile(self, payload: CatProfileCreate) -> CatProfile:
        payload_data = payload.model_dump()
        payload_data["profile_source"] = payload_data.get("profile_source") or PROFILE_SOURCE_REAL
        cat_profile = CatProfile(**payload_data)
        self.db.add(cat_profile)
        self.db.commit()
        self.db.refresh(cat_profile)
        return self.get_profile(cat_profile.id, allowed_sources=ALL_PROFILE_SOURCES) or cat_profile

    def create_auto_profile(
        self,
        *,
        location_text: str,
        sighted_at: datetime | None,
        notes: str | None,
        created_by: int | None,
        profile_source: ProfileSource = PROFILE_SOURCE_REAL,
    ) -> CatProfile:
        cat_profile = CatProfile(
            name="PENDING",
            profile_source=profile_source,
            first_seen_at=sighted_at or datetime.utcnow(),
            first_seen_location=location_text,
            notes=notes,
            created_by=created_by,
        )
        self.db.add(cat_profile)
        self.db.flush()
        cat_profile.name = f"Cat-{cat_profile.id:04d}"
        self.db.flush()
        return cat_profile
