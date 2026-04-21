from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import re
import sys

from sqlalchemy import select, text

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.session import SessionLocal
from app.models.cat_profile import (
    CatProfile,
    PROFILE_SOURCE_REAL,
    PROFILE_SOURCE_TEST,
)

STRONG_TEST_PATTERNS = (
    r"\btest\b",
    r"\bsmoke\b",
    r"\bdemo\b",
    r"\bdebug\b",
    r"\bmock\b",
    r"\bdev\b",
    r"\bqa\b",
    r"\bverification\b",
    "\u6d4b\u8bd5",
    "\u8054\u8c03",
    "\u5192\u70df",
    "\u8c03\u8bd5",
    "\u5f00\u53d1\u9a8c\u8bc1",
    "\u6f14\u793a",
)

WEAK_REVIEW_PATTERNS = (
    r"\btmp\b",
    r"\btemp\b",
    r"\bexample\b",
    r"\bstaging\b",
    "\u6837\u4f8b",
    "\u793a\u4f8b",
    "\u6821\u9a8c",
    "\u9a8c\u8bc1",
)


@dataclass
class ClassificationResult:
    profile_id: int
    proposed_source: str
    reason: str
    needs_manual_review: bool
    review_reason: str = ""


def build_search_text(profile: CatProfile) -> str:
    values = [
        profile.name,
        profile.notes,
        profile.first_seen_location,
        profile.dataset_cat_code,
    ]
    return " ".join(value.strip() for value in values if value).lower()


def matches_any(patterns: tuple[str, ...], text: str) -> str | None:
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return pattern
    return None


def has_profile_source_column() -> bool:
    session = SessionLocal()
    try:
        result = session.execute(
            text(
                """
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'cat_profile'
                  AND COLUMN_NAME = 'profile_source'
                """
            )
        ).scalar_one()
        return bool(result)
    finally:
        session.close()


def has_profile_source_index() -> bool:
    session = SessionLocal()
    try:
        result = session.execute(
            text(
                """
                SELECT COUNT(*)
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'cat_profile'
                  AND INDEX_NAME = 'idx_cat_profile_profile_source'
                """
            )
        ).scalar_one()
        return bool(result)
    finally:
        session.close()


def ensure_profile_source_schema() -> None:
    session = SessionLocal()
    try:
        if not has_profile_source_column():
            session.execute(
                text(
                    """
                    ALTER TABLE cat_profile
                    ADD COLUMN profile_source VARCHAR(16) NOT NULL DEFAULT 'real'
                    """
                )
            )
            session.commit()

        if not has_profile_source_index():
            session.execute(
                text(
                    """
                    CREATE INDEX idx_cat_profile_profile_source
                    ON cat_profile (profile_source)
                    """
                )
            )
            session.commit()
    finally:
        session.close()


def classify_profile(profile: CatProfile) -> ClassificationResult:
    search_text = build_search_text(profile)

    if profile.dataset_cat_code:
        manual_conflict = matches_any(STRONG_TEST_PATTERNS, search_text)
        return ClassificationResult(
            profile_id=profile.id,
            proposed_source=PROFILE_SOURCE_REAL,
            reason="dataset_cat_code is not empty and dataset-imported profiles are treated as real",
            needs_manual_review=manual_conflict is not None,
            review_reason=(
                f"dataset_cat_code suggests real dataset profile, but strong test keyword matched: {manual_conflict}"
                if manual_conflict is not None
                else ""
            ),
        )

    strong_test_match = matches_any(STRONG_TEST_PATTERNS, search_text)
    if strong_test_match is not None:
        return ClassificationResult(
            profile_id=profile.id,
            proposed_source=PROFILE_SOURCE_TEST,
            reason=f"strong test keyword matched: {strong_test_match}",
            needs_manual_review=False,
        )

    weak_review_match = matches_any(WEAK_REVIEW_PATTERNS, search_text)
    return ClassificationResult(
        profile_id=profile.id,
        proposed_source=PROFILE_SOURCE_REAL,
        reason="fallback rule: no dataset_cat_code and no strong test signal",
        needs_manual_review=weak_review_match is not None,
        review_reason=(
            f"fallback classified as real, but weak review keyword matched: {weak_review_match}"
            if weak_review_match is not None
            else ""
        ),
    )


def write_manual_review_csv(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "current_profile_source",
                "proposed_profile_source",
                "reason",
                "review_reason",
                "dataset_cat_code",
                "name",
                "first_seen_location",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill cat_profile.profile_source safely.")
    parser.add_argument("--apply", action="store_true", help="Apply proposed classification to the database.")
    parser.add_argument(
        "--ensure-schema",
        action="store_true",
        help="Ensure the profile_source column and index exist before classification.",
    )
    parser.add_argument(
        "--manual-review-csv",
        default=str(BACKEND_ROOT / "reports" / "profile_source_manual_review.csv"),
        help="Where to write the manual review CSV report.",
    )
    args = parser.parse_args()

    if args.ensure_schema:
        ensure_profile_source_schema()

    if not has_profile_source_column():
        raise SystemExit(
            "Missing column cat_profile.profile_source. Run the profile_source schema migration first."
        )

    session = SessionLocal()
    try:
        profiles = session.scalars(select(CatProfile).order_by(CatProfile.id.asc())).all()
        summary = {
            PROFILE_SOURCE_REAL: 0,
            PROFILE_SOURCE_TEST: 0,
        }
        changed = 0
        manual_review_rows: list[dict[str, str]] = []

        for profile in profiles:
            result = classify_profile(profile)
            summary[result.proposed_source] += 1

            if result.needs_manual_review:
                manual_review_rows.append(
                    {
                        "id": str(profile.id),
                        "current_profile_source": getattr(profile, "profile_source", "") or "",
                        "proposed_profile_source": result.proposed_source,
                        "reason": result.reason,
                        "review_reason": result.review_reason,
                        "dataset_cat_code": profile.dataset_cat_code or "",
                        "name": profile.name or "",
                        "first_seen_location": profile.first_seen_location or "",
                        "notes": profile.notes or "",
                    }
                )

            if args.apply and getattr(profile, "profile_source", None) != result.proposed_source:
                profile.profile_source = result.proposed_source
                changed += 1

        if args.apply:
            session.commit()

        output_path = Path(args.manual_review_csv)
        write_manual_review_csv(manual_review_rows, output_path)

        print("Profile source backfill summary:")
        print(f"  real: {summary[PROFILE_SOURCE_REAL]}")
        print(f"  test: {summary[PROFILE_SOURCE_TEST]}")
        print(f"  manual review rows: {len(manual_review_rows)}")
        print(f"  manual review csv: {output_path}")
        if args.apply:
            print(f"  updated rows: {changed}")
        else:
            print("  dry run only: no database changes applied")
    finally:
        session.close()


if __name__ == "__main__":
    main()
