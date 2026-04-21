from pydantic import BaseModel

from app.schemas.common import TimestampedModel


class CatImageRead(TimestampedModel):
    cat_profile_id: int | None = None
    file_path: str
    original_filename: str | None = None
    mime_type: str | None = None
    file_size: int | None = None
    ai_feature_path: str | None = None
    ai_match_status: str
    notes: str | None = None
    uploaded_by: int | None = None


class MatchRecommendation(BaseModel):
    cat_profile_id: int | None = None
    sample_cat_code: str | None = None
    cat_name: str | None = None
    similarity_score: float | None = None
    reason: str
    cover_image: str | None = None
