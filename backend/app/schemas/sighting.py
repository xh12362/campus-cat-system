from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import TimestampedModel


class SightingListItem(TimestampedModel):
    cat_profile_id: int | None = None
    image_id: int | None = None
    sighted_at: datetime
    location_text: str
    notes: str | None = None
    reported_by: int | None = None


class SightingCreate(BaseModel):
    cat_profile_id: int | None = None
    image_id: int | None = None
    sighted_at: datetime | None = None
    location_text: str
    notes: str | None = None
    reported_by: int | None = None
