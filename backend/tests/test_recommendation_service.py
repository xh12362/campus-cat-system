from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from app.models.cat_profile import PROFILE_SOURCE_REAL, PROFILE_SOURCE_SAMPLE, PROFILE_SOURCE_TEST
from app.services.recommendation_service import RecommendationService
from tests.test_support import build_test_session_factory, seed_profile


class RecommendationServiceTests(TestCase):
    def setUp(self) -> None:
        self.session_factory = build_test_session_factory()

    def test_uses_ai_candidates_and_backfills_profile_metadata(self) -> None:
        with self.session_factory() as db:
            seed_profile(
                db,
                profile_id=2,
                dataset_cat_code="CAT-0002",
                name="Bohe",
                created_at=datetime(2026, 4, 1, 10, 0, 0),
                cover_paths=[
                    "/workspace/uploads/original/bohe-old.jpg",
                    "/workspace/uploads/original/bohe-new.jpg",
                ],
                profile_source=PROFILE_SOURCE_REAL,
            )
            seed_profile(
                db,
                profile_id=7,
                dataset_cat_code="CAT-0007",
                name="Sanseqiu",
                created_at=datetime(2026, 4, 2, 10, 0, 0),
                cover_paths=["/workspace/uploads/original/sanseqiu.jpg"],
                profile_source=PROFILE_SOURCE_REAL,
            )

            with patch(
                "app.services.recommendation_service.AIDetectionService.recommend_from_cropped_path",
                return_value=[
                    {
                        "sample_cat_code": "CAT-0007",
                        "cat_name": None,
                        "similarity_score": 0.9335,
                        "reason": "High visual similarity.",
                    },
                    {
                        "sample_cat_code": "CAT-0002",
                        "cat_name": "Bohe",
                        "similarity_score": 0.8451,
                        "reason": "Similar coat pattern.",
                    },
                ],
            ):
                recommendations = RecommendationService(db).recommend_for_image("/workspace/cropped/cat.jpg")

        self.assertEqual([item.cat_profile_id for item in recommendations], [7, 2])
        self.assertEqual([item.sample_cat_code for item in recommendations], ["CAT-0007", "CAT-0002"])
        self.assertEqual(recommendations[0].cat_name, "Sanseqiu")
        self.assertEqual(recommendations[0].cover_image, "/workspace/uploads/original/sanseqiu.jpg")
        self.assertEqual(recommendations[1].cover_image, "/workspace/uploads/original/bohe-new.jpg")
        self.assertEqual(recommendations[1].reason, "Similar coat pattern.")

    def test_falls_back_to_recent_profiles_when_ai_is_unavailable(self) -> None:
        with self.session_factory() as db:
            seed_profile(
                db,
                profile_id=1,
                dataset_cat_code="CAT-0001",
                name="Xiaoxiao",
                created_at=datetime(2026, 4, 1, 10, 0, 0),
                profile_source=PROFILE_SOURCE_REAL,
            )
            seed_profile(
                db,
                profile_id=2,
                dataset_cat_code="CAT-0002",
                name="Bohe",
                created_at=datetime(2026, 4, 2, 10, 0, 0),
                cover_paths=["/workspace/uploads/original/bohe.jpg"],
                profile_source=PROFILE_SOURCE_REAL,
            )
            seed_profile(
                db,
                profile_id=7,
                dataset_cat_code="CAT-0007",
                name="Sanseqiu",
                created_at=datetime(2026, 4, 3, 10, 0, 0),
                cover_paths=["/workspace/uploads/original/sanseqiu.jpg"],
                profile_source=PROFILE_SOURCE_REAL,
            )

            with patch(
                "app.services.recommendation_service.AIDetectionService.recommend_from_cropped_path",
                return_value=[],
            ):
                recommendations = RecommendationService(db).recommend_for_image(
                    "/workspace/cropped/cat.jpg",
                    exclude_profile_id=2,
                )

        self.assertEqual([item.cat_profile_id for item in recommendations], [7, 1])
        self.assertEqual([item.sample_cat_code for item in recommendations], ["CAT-0007", "CAT-0001"])
        self.assertTrue(
            all(
                item.reason == "AI similarity recommendation unavailable. Fallback uses recent profiles."
                for item in recommendations
            )
        )
        self.assertEqual(recommendations[0].cover_image, "/workspace/uploads/original/sanseqiu.jpg")
        self.assertIsNone(recommendations[1].cover_image)

    def test_sample_profiles_can_support_mapping_without_becoming_detail_targets(self) -> None:
        with self.session_factory() as db:
            seed_profile(
                db,
                profile_id=2,
                dataset_cat_code="CAT-0002",
                name="Dataset Sample",
                created_at=datetime(2026, 4, 1, 10, 0, 0),
                cover_paths=["/workspace/uploads/original/sample.jpg"],
                profile_source=PROFILE_SOURCE_SAMPLE,
            )
            seed_profile(
                db,
                profile_id=9,
                dataset_cat_code="CAT-0009",
                name="Internal Test",
                created_at=datetime(2026, 4, 2, 10, 0, 0),
                cover_paths=["/workspace/uploads/original/test.jpg"],
                profile_source=PROFILE_SOURCE_TEST,
            )

            with patch(
                "app.services.recommendation_service.AIDetectionService.recommend_from_cropped_path",
                return_value=[
                    {
                        "sample_cat_code": "CAT-0002",
                        "cat_name": None,
                        "similarity_score": 0.8451,
                        "reason": "Similar coat pattern.",
                    },
                    {
                        "sample_cat_code": "CAT-0009",
                        "cat_name": None,
                        "similarity_score": 0.7211,
                        "reason": "Should ignore test profile.",
                    },
                ],
            ):
                recommendations = RecommendationService(db).recommend_for_image("/workspace/cropped/cat.jpg")

        self.assertEqual(len(recommendations), 2)
        self.assertIsNone(recommendations[0].cat_profile_id)
        self.assertEqual(recommendations[0].sample_cat_code, "CAT-0002")
        self.assertEqual(recommendations[0].cat_name, "Dataset Sample")
        self.assertIsNone(recommendations[0].cover_image)
        self.assertIsNone(recommendations[1].cat_profile_id)
