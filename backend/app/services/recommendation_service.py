from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.cat_image import CatImage
from app.models.cat_profile import (
    CatProfile,
    PROFILE_SOURCE_REAL,
    PROFILE_SOURCE_SAMPLE,
)
from app.schemas.image import MatchRecommendation
from app.services.ai_detection_service import AIDetectionService


class RecommendationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _load_profile_metadata(
        self,
        profile_ids: list[int],
        dataset_codes: list[str],
    ) -> tuple[dict[int, CatProfile], dict[str, CatProfile], dict[int, str]]:
        if not profile_ids and not dataset_codes:
            return {}, {}, {}

        statement = select(CatProfile).where(
            CatProfile.profile_source.in_((PROFILE_SOURCE_REAL, PROFILE_SOURCE_SAMPLE))
        )
        if profile_ids and dataset_codes:
            statement = statement.where(
                or_(CatProfile.id.in_(profile_ids), CatProfile.dataset_cat_code.in_(dataset_codes))
            )
        elif profile_ids:
            statement = statement.where(CatProfile.id.in_(profile_ids))
        else:
            statement = statement.where(CatProfile.dataset_cat_code.in_(dataset_codes))

        profiles = self.db.scalars(statement).all()
        profile_map = {profile.id: profile for profile in profiles}
        profile_by_dataset_code: dict[str, CatProfile] = {}
        for profile in profiles:
            if not profile.dataset_cat_code:
                continue
            existing = profile_by_dataset_code.get(profile.dataset_cat_code)
            if existing is None or (
                existing.profile_source != PROFILE_SOURCE_REAL
                and profile.profile_source == PROFILE_SOURCE_REAL
            ):
                profile_by_dataset_code[profile.dataset_cat_code] = profile
        resolved_profile_ids = [profile.id for profile in profiles]

        images = self.db.scalars(
            select(CatImage)
            .where(CatImage.cat_profile_id.in_(resolved_profile_ids))
            .order_by(CatImage.created_at.desc(), CatImage.id.desc())
        ).all()

        cover_map: dict[int, str] = {}
        for image in images:
            if image.cat_profile_id is not None and image.cat_profile_id not in cover_map:
                cover_map[image.cat_profile_id] = image.file_path

        return profile_map, profile_by_dataset_code, cover_map

    def recommend_for_image(
        self,
        cropped_image_path: str | None,
        exclude_profile_id: int | None = None,
    ) -> list[MatchRecommendation]:
        if cropped_image_path:
            ai_candidates = AIDetectionService().recommend_from_cropped_path(cropped_image_path, top_k=5)
            candidate_ids = [int(candidate["cat_profile_id"]) for candidate in ai_candidates if candidate.get("cat_profile_id")]
            candidate_codes = [
                str(candidate["sample_cat_code"]).strip()
                for candidate in ai_candidates
                if candidate.get("sample_cat_code")
            ]
            _, profile_by_dataset_code, cover_map = self._load_profile_metadata(candidate_ids, candidate_codes)
            recommendations: list[MatchRecommendation] = []

            for candidate in ai_candidates:
                sample_cat_code = (candidate.get("sample_cat_code") or "").strip() or None
                mapped_profile = (
                    profile_by_dataset_code.get(sample_cat_code)
                    if sample_cat_code
                    else None
                )
                mapped_profile_id = (
                    mapped_profile.id
                    if mapped_profile is not None and mapped_profile.profile_source == PROFILE_SOURCE_REAL
                    else None
                )
                if exclude_profile_id is not None and mapped_profile_id == exclude_profile_id:
                    continue

                recommendations.append(
                    MatchRecommendation(
                        cat_profile_id=mapped_profile_id,
                        sample_cat_code=sample_cat_code,
                        cat_name=(
                            candidate.get("cat_name")
                            or (mapped_profile.name if mapped_profile is not None else None)
                        ),
                        similarity_score=candidate.get("similarity_score"),
                        reason=candidate.get("reason", "AI similarity recommendation."),
                        cover_image=(
                            candidate.get("cover_image")
                            or (cover_map.get(mapped_profile_id) if mapped_profile_id is not None else None)
                        ),
                    )
                )
            if recommendations:
                return recommendations

        statement = (
            select(CatProfile)
            .where(CatProfile.profile_source == PROFILE_SOURCE_REAL)
            .order_by(CatProfile.created_at.desc())
            .limit(5)
        )
        candidates = self.db.scalars(statement).all()
        fallback_ids = [cat.id for cat in candidates if cat.id != exclude_profile_id]
        _, _, cover_map = self._load_profile_metadata(fallback_ids, [])
        return [
            MatchRecommendation(
                cat_profile_id=cat.id,
                sample_cat_code=cat.dataset_cat_code,
                cat_name=cat.name,
                similarity_score=None,
                reason="AI similarity recommendation unavailable. Fallback uses recent profiles.",
                cover_image=cover_map.get(cat.id),
            )
            for cat in candidates
            if cat.id != exclude_profile_id
        ]
