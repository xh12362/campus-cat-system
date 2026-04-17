from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cat_profile import CatProfile
from app.schemas.image import MatchRecommendation


class RecommendationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def recommend_for_image(
        self,
        file_path: str,
        exclude_profile_id: int | None = None,
    ) -> list[MatchRecommendation]:
        # Placeholder for future AI feature extraction and similarity search.
        statement = select(CatProfile).order_by(CatProfile.created_at.desc()).limit(5)
        candidates = self.db.scalars(statement).all()
        return [
            MatchRecommendation(
                cat_profile_id=cat.id,
                cat_name=cat.name,
                similarity_score=None,
                reason=f"AI matching placeholder. Current fallback uses recent profiles for: {file_path}",
            )
            for cat in candidates
            if cat.id != exclude_profile_id
        ]
