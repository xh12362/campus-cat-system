from pydantic import BaseModel

from app.schemas.ai import AIDetectionResult
from app.schemas.image import CatImageRead, MatchRecommendation
from app.schemas.sighting import SightingListItem


class UploadResponse(BaseModel):
    message: str
    cat_profile_id: int | None = None
    profile_created: bool
    image: CatImageRead
    sighting: SightingListItem
    recommendations: list[MatchRecommendation]
    detection: AIDetectionResult | None = None


class CreateProfileFromUploadRequest(BaseModel):
    image_id: int
    sighting_id: int


class CreateProfileFromUploadResponse(BaseModel):
    message: str
    cat_profile_id: int
    profile_created: bool
    image: CatImageRead
    sighting: SightingListItem
