from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, TimestampedModel
from app.schemas.image import CatImageRead
from app.schemas.sighting import SightingListItem


class CatProfileBase(BaseModel):
    name: str | None = None
    gender: str | None = None
    coat_color: str | None = None
    age_stage: str | None = None
    sterilization_status: str | None = None
    health_status: str | None = None
    distinguishing_features: str | None = None
    first_seen_at: datetime | None = None
    first_seen_location: str | None = None
    notes: str | None = None
    created_by: int | None = None


class CatProfileCreate(CatProfileBase):
    pass


class CatProfileListItem(TimestampedModel, CatProfileBase):
    updated_at: datetime


class CatProfileDetail(CatProfileListItem):
    images: list[CatImageRead] = Field(default_factory=list)
    sightings: list[SightingListItem] = Field(default_factory=list)
