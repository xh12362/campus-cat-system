from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.cat_image import CatImage
from app.models.cat_profile import CatProfile, PROFILE_SOURCE_REAL


def build_test_session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def seed_profile(
    db: Session,
    *,
    profile_id: int,
    name: str,
    created_at: datetime,
    dataset_cat_code: str | None = None,
    cover_paths: list[str] | None = None,
    profile_source: str = PROFILE_SOURCE_REAL,
    first_seen_location: str | None = None,
    notes: str | None = None,
) -> CatProfile:
    profile = CatProfile(
        id=profile_id,
        dataset_cat_code=dataset_cat_code,
        profile_source=profile_source,
        name=name,
        first_seen_location=first_seen_location,
        notes=notes,
        created_at=created_at,
        updated_at=created_at,
    )
    db.add(profile)
    db.flush()

    for index, file_path in enumerate(cover_paths or [], start=1):
        db.add(
            CatImage(
                cat_profile_id=profile_id,
                file_path=file_path,
                ai_match_status="detected",
                created_at=created_at + timedelta(seconds=index),
            )
        )

    db.commit()
    return profile
