from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CatImage(Base):
    __tablename__ = "cat_image"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cat_profile_id: Mapped[int | None] = mapped_column(ForeignKey("cat_profile.id"))
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255))
    mime_type: Mapped[str | None] = mapped_column(String(100))
    file_size: Mapped[int | None] = mapped_column(Integer)
    ai_feature_path: Mapped[str | None] = mapped_column(String(255))
    ai_match_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    uploaded_by: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    cat_profile = relationship("CatProfile", back_populates="images")
    sightings = relationship("CatSighting", back_populates="image")
