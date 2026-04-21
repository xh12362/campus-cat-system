from datetime import datetime
from unittest import TestCase

from app.models.cat_profile import PROFILE_SOURCE_REAL, PROFILE_SOURCE_SAMPLE, PROFILE_SOURCE_TEST
from app.services.cat_service import ALL_PROFILE_SOURCES, CatService
from tests.test_support import build_test_session_factory, seed_profile


class CatServiceVisibilityTests(TestCase):
    def setUp(self) -> None:
        self.session_factory = build_test_session_factory()

    def test_list_profiles_returns_only_real_by_default(self) -> None:
        with self.session_factory() as db:
            seed_profile(
                db,
                profile_id=1,
                name="Real Cat",
                created_at=datetime(2026, 4, 1, 10, 0, 0),
                profile_source=PROFILE_SOURCE_REAL,
            )
            seed_profile(
                db,
                profile_id=2,
                name="Sample Cat",
                created_at=datetime(2026, 4, 2, 10, 0, 0),
                profile_source=PROFILE_SOURCE_SAMPLE,
            )
            seed_profile(
                db,
                profile_id=3,
                name="Test Cat",
                created_at=datetime(2026, 4, 3, 10, 0, 0),
                profile_source=PROFILE_SOURCE_TEST,
            )

            profiles = CatService(db).list_profiles()
            all_profiles = CatService(db).list_profiles(allowed_sources=ALL_PROFILE_SOURCES)

        self.assertEqual([item.id for item in profiles], [1])
        self.assertEqual([item.id for item in all_profiles], [3, 2, 1])

    def test_get_profile_blocks_non_real_by_default(self) -> None:
        with self.session_factory() as db:
            seed_profile(
                db,
                profile_id=1,
                name="Sample Cat",
                created_at=datetime(2026, 4, 1, 10, 0, 0),
                profile_source=PROFILE_SOURCE_SAMPLE,
            )

            hidden = CatService(db).get_profile(1)
            visible = CatService(db).get_profile(1, allowed_sources=ALL_PROFILE_SOURCES)

        self.assertIsNone(hidden)
        self.assertIsNotNone(visible)
