import asyncio
from datetime import datetime
from io import BytesIO
from unittest import TestCase
from unittest.mock import patch

from fastapi import UploadFile

from app.api.routes.upload import create_profile_from_upload
from app.schemas.upload import CreateProfileFromUploadRequest
from app.models.cat_profile import CatProfile
from app.models.cat_profile import PROFILE_SOURCE_REAL
from app.api.routes.upload import upload_image
from tests.test_support import build_test_session_factory, seed_profile


class UploadRouteTests(TestCase):
    def setUp(self) -> None:
        self.session_factory = build_test_session_factory()

    def test_upload_returns_ai_recommendations_with_stable_fields(self) -> None:
        with self.session_factory() as db:
            seed_profile(
                db,
                profile_id=2,
                dataset_cat_code="CAT-0002",
                name="Bohe",
                created_at=datetime(2026, 4, 1, 10, 0, 0),
                cover_paths=["/workspace/uploads/original/bohe.jpg"],
            )
            seed_profile(
                db,
                profile_id=7,
                dataset_cat_code="CAT-0007",
                name="Sanseqiu",
                created_at=datetime(2026, 4, 2, 10, 0, 0),
                cover_paths=["/workspace/uploads/original/sanseqiu.jpg"],
            )

            with patch(
                "app.api.routes.upload.save_upload_file",
                return_value={
                    "file_path": "/workspace/uploads/original/upload.jpg",
                    "original_filename": "upload.jpg",
                    "file_size": 123,
                    "mime_type": "image/jpeg",
                },
            ), patch(
                "app.api.routes.upload.AIDetectionService.detect_from_file_path",
                return_value={
                    "model_loaded": True,
                    "has_cat": True,
                    "confidence": 0.98,
                    "detections": [{"label": "cat", "score": 0.98, "bbox": [0, 0, 100, 100]}],
                    "cropped_image_path": "/workspace/uploads/cropped/cat.jpg",
                    "message": "Detection completed.",
                },
            ), patch(
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
                response = asyncio.run(
                    upload_image(
                        photo=UploadFile(filename="cat.jpg", file=BytesIO(b"fake-image-bytes")),
                        location_text="North campus",
                        sighted_at=None,
                        notes="Seen near the library",
                        cat_profile_id=None,
                        uploaded_by=None,
                        db=db,
                    )
                )

        self.assertFalse(response.profile_created)
        self.assertTrue(response.detection.has_cat)
        self.assertEqual(response.image.ai_match_status, "detected")
        self.assertIsNone(response.cat_profile_id)
        self.assertIsNone(response.image.cat_profile_id)
        self.assertIsNone(response.sighting.cat_profile_id)
        self.assertEqual(len(response.recommendations), 2)
        self.assertEqual(response.recommendations[0].cat_profile_id, 7)
        self.assertEqual(response.recommendations[0].sample_cat_code, "CAT-0007")
        self.assertEqual(response.recommendations[0].cat_name, "Sanseqiu")
        self.assertEqual(response.recommendations[0].cover_image, "/workspace/uploads/original/sanseqiu.jpg")
        self.assertEqual(response.recommendations[1].cover_image, "/workspace/uploads/original/bohe.jpg")

    def test_upload_falls_back_to_recent_profiles_when_ai_recommendation_fails(self) -> None:
        with self.session_factory() as db:
            seed_profile(
                db,
                profile_id=2,
                dataset_cat_code="CAT-0002",
                name="Bohe",
                created_at=datetime(2026, 4, 1, 10, 0, 0),
                cover_paths=["/workspace/uploads/original/bohe.jpg"],
            )
            seed_profile(
                db,
                profile_id=7,
                dataset_cat_code="CAT-0007",
                name="Sanseqiu",
                created_at=datetime(2026, 4, 2, 10, 0, 0),
            )

            with patch(
                "app.api.routes.upload.save_upload_file",
                return_value={
                    "file_path": "/workspace/uploads/original/upload.jpg",
                    "original_filename": "upload.jpg",
                    "file_size": 123,
                    "mime_type": "image/jpeg",
                },
            ), patch(
                "app.api.routes.upload.AIDetectionService.detect_from_file_path",
                return_value={
                    "model_loaded": True,
                    "has_cat": True,
                    "confidence": 0.91,
                    "detections": [{"label": "cat", "score": 0.91, "bbox": [1, 2, 3, 4]}],
                    "cropped_image_path": "/workspace/uploads/cropped/cat.jpg",
                    "message": "Detection completed.",
                },
            ), patch(
                "app.services.recommendation_service.AIDetectionService.recommend_from_cropped_path",
                return_value=[],
            ):
                response = asyncio.run(
                    upload_image(
                        photo=UploadFile(filename="cat.jpg", file=BytesIO(b"fake-image-bytes")),
                        location_text="North campus",
                        sighted_at=None,
                        notes=None,
                        cat_profile_id=None,
                        uploaded_by=None,
                        db=db,
                    )
                )

        self.assertFalse(response.profile_created)
        self.assertIsNone(response.cat_profile_id)
        self.assertGreaterEqual(len(response.recommendations), 1)
        self.assertTrue(
            all(
                item.reason == "AI similarity recommendation unavailable. Fallback uses recent profiles."
                for item in response.recommendations
            )
        )
        self.assertEqual(response.recommendations[0].cat_profile_id, 7)
        self.assertEqual(response.recommendations[0].sample_cat_code, "CAT-0007")
        self.assertTrue(hasattr(response.recommendations[0], "cover_image"))

    def test_create_profile_from_upload_links_existing_records_without_reuploading(self) -> None:
        with self.session_factory() as db:
            with patch(
                "app.api.routes.upload.save_upload_file",
                return_value={
                    "file_path": "/workspace/uploads/original/upload.jpg",
                    "original_filename": "upload.jpg",
                    "file_size": 123,
                    "mime_type": "image/jpeg",
                },
            ), patch(
                "app.api.routes.upload.AIDetectionService.detect_from_file_path",
                return_value={
                    "model_loaded": True,
                    "has_cat": True,
                    "confidence": 0.91,
                    "detections": [{"label": "cat", "score": 0.91, "bbox": [1, 2, 3, 4]}],
                    "cropped_image_path": "/workspace/uploads/cropped/cat.jpg",
                    "message": "Detection completed.",
                },
            ), patch(
                "app.services.recommendation_service.AIDetectionService.recommend_from_cropped_path",
                return_value=[],
            ):
                upload_response = asyncio.run(
                    upload_image(
                        photo=UploadFile(filename="cat.jpg", file=BytesIO(b"fake-image-bytes")),
                        location_text="North campus",
                        sighted_at=None,
                        notes="pending profile decision",
                        cat_profile_id=None,
                        uploaded_by=None,
                        db=db,
                    )
                )

            create_response = create_profile_from_upload(
                CreateProfileFromUploadRequest(
                    image_id=upload_response.image.id,
                    sighting_id=upload_response.sighting.id,
                ),
                db=db,
            )
            created_profile = db.get(CatProfile, create_response.cat_profile_id)

        self.assertTrue(create_response.profile_created)
        self.assertIsNotNone(created_profile)
        self.assertEqual(created_profile.profile_source, PROFILE_SOURCE_REAL)
        self.assertEqual(create_response.image.cat_profile_id, create_response.cat_profile_id)
        self.assertEqual(create_response.sighting.cat_profile_id, create_response.cat_profile_id)
