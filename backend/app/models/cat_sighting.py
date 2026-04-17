from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CatSighting(Base):
    __tablename__ = "cat_sighting"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cat_profile_id: Mapped[int | None] = mapped_column(ForeignKey("cat_profile.id"))
    image_id: Mapped[int | None] = mapped_column(ForeignKey("cat_image.id"))
    sighted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location_text: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    reported_by: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    cat_profile = relationship("CatProfile", back_populates="sightings")
    image = relationship("CatImage", back_populates="sightings")
