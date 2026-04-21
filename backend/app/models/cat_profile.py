from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

PROFILE_SOURCE_REAL = "real"
PROFILE_SOURCE_SAMPLE = "sample"
PROFILE_SOURCE_TEST = "test"


class CatProfile(Base):
    __tablename__ = "cat_profile"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    dataset_cat_code: Mapped[str | None] = mapped_column(String(30), unique=True)
    profile_source: Mapped[str] = mapped_column(String(16), nullable=False, default=PROFILE_SOURCE_REAL)
    name: Mapped[str | None] = mapped_column(String(100))
    gender: Mapped[str | None] = mapped_column(String(20))
    coat_color: Mapped[str | None] = mapped_column(String(100))
    age_stage: Mapped[str | None] = mapped_column(String(30))
    sterilization_status: Mapped[str | None] = mapped_column(String(30))
    health_status: Mapped[str | None] = mapped_column(String(100))
    distinguishing_features: Mapped[str | None] = mapped_column(Text)
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime)
    first_seen_location: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    images = relationship("CatImage", back_populates="cat_profile")
    sightings = relationship("CatSighting", back_populates="cat_profile")
