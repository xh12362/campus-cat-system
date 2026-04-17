from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cat_image import CatImage
from app.models.cat_sighting import CatSighting


def create_image_and_sighting(
    db: Session,
    file_path: str,
    original_filename: str | None,
    file_size: int | None,
    mime_type: str | None,
    ai_feature_path: str | None,
    ai_match_status: str,
    cat_profile_id: int | None,
    uploaded_by: int | None,
    location_text: str,
    sighted_at: datetime | None,
    notes: str | None,
) -> tuple[CatImage, CatSighting]:
    image = CatImage(
        cat_profile_id=cat_profile_id,
        file_path=file_path,
        original_filename=original_filename,
        file_size=file_size,
        mime_type=mime_type,
        ai_feature_path=ai_feature_path,
        ai_match_status=ai_match_status,
        uploaded_by=uploaded_by,
        notes=notes,
    )
    db.add(image)
    db.flush()

    sighting = CatSighting(
        cat_profile_id=cat_profile_id,
        image_id=image.id,
        sighted_at=sighted_at or datetime.utcnow(),
        location_text=location_text,
        notes=notes,
        reported_by=uploaded_by,
    )
    db.add(sighting)
    db.commit()
    db.refresh(image)
    db.refresh(sighting)
    return image, sighting


def list_sightings(db: Session) -> list[CatSighting]:
    statement = select(CatSighting).order_by(CatSighting.sighted_at.desc(), CatSighting.id.desc())
    return list(db.scalars(statement).all())
