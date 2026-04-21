from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, TimestampedModel
from app.schemas.image import CatImageRead
from app.schemas.sighting import SightingListItem

ProfileSource = Literal["real", "sample", "test"]


class CatProfileBase(BaseModel):
    dataset_cat_code: str | None = None
    profile_source: ProfileSource = "real"
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
