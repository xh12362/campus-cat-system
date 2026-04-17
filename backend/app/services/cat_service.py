from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.cat_profile import CatProfile
from app.schemas.cat import CatProfileCreate


class CatService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_profiles(self) -> list[CatProfile]:
        statement = select(CatProfile).order_by(CatProfile.created_at.desc())
        return list(self.db.scalars(statement).all())

    def get_profile(self, cat_id: int) -> CatProfile | None:
        statement = (
            select(CatProfile)
            .options(
                selectinload(CatProfile.images),
                selectinload(CatProfile.sightings),
            )
            .where(CatProfile.id == cat_id)
        )
        return self.db.scalars(statement).first()

    def create_profile(self, payload: CatProfileCreate) -> CatProfile:
        cat_profile = CatProfile(**payload.model_dump())
        self.db.add(cat_profile)
        self.db.commit()
        self.db.refresh(cat_profile)
        return self.get_profile(cat_profile.id) or cat_profile

    def create_auto_profile(
        self,
        *,
        location_text: str,
        sighted_at: datetime | None,
        notes: str | None,
        created_by: int | None,
    ) -> CatProfile:
        cat_profile = CatProfile(
            name="PENDING",
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
