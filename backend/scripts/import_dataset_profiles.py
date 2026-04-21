from __future__ import annotations

import csv
from datetime import datetime
import os
from pathlib import Path
import sys

from sqlalchemy import select

BACKEND_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = Path(os.getenv("DATASET_ROOT", "/workspace/datasets"))
DATASET_CSV_PATH = DATASET_ROOT / "cat_profiles.csv"
CSV_ENCODINGS = ("utf-8-sig", "utf-8", "gb18030", "gbk")

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.session import SessionLocal
from app.models.cat_profile import CatProfile, PROFILE_SOURCE_REAL


def load_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    last_error: Exception | None = None
    for encoding in CSV_ENCODINGS:
        try:
            with csv_path.open("r", encoding=encoding, newline="") as handle:
                return list(csv.DictReader(handle))
        except UnicodeDecodeError as exc:
            last_error = exc

    raise RuntimeError(f"Unable to decode dataset csv: {csv_path}. Last error: {last_error}")


def parse_first_seen(value: str | None) -> datetime | None:
    if not value:
        return None

    text = value.strip()
    if not text:
        return None

    for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d", "%Y.%m", "%Y/%m", "%Y"):
        try:
            parsed = datetime.strptime(text, fmt)
            if fmt == "%Y":
                return parsed.replace(month=1, day=1)
            if fmt in ("%Y.%m", "%Y/%m"):
                return parsed.replace(day=1)
            return parsed
        except ValueError:
            continue

    return None


def combine_notes(row: dict[str, str]) -> str | None:
    parts: list[str] = []
    for label, key in (
        ("Area", "area"),
        ("Status", "status"),
        ("Sterilized", "sterilized"),
        ("SocialRelation", "social_relation"),
        ("Remark", "remark"),
        ("SourceArticle", "source_article"),
        ("ImageFolder", "image_folder"),
    ):
        value = (row.get(key) or "").strip()
        if value:
            parts.append(f"{label}: {value}")

    return "\n".join(parts) if parts else None


def upsert_dataset_profiles() -> None:
    rows = load_csv_rows(DATASET_CSV_PATH)
    session = SessionLocal()

    try:
        imported = 0
        for row in rows:
            cat_code = (row.get("cat_code") or "").strip()
            if not cat_code:
                continue

            profile = session.scalar(
                select(CatProfile).where(CatProfile.dataset_cat_code == cat_code)
            )
            if profile is None:
                profile = CatProfile(
                    dataset_cat_code=cat_code,
                    profile_source=PROFILE_SOURCE_REAL,
                )
                session.add(profile)

            profile.dataset_cat_code = cat_code
            profile.profile_source = PROFILE_SOURCE_REAL
            profile.name = (row.get("cat_name") or "").strip() or profile.name
            profile.gender = (row.get("sex") or "").strip() or None
            profile.coat_color = (row.get("color") or "").strip() or None
            profile.first_seen_location = (row.get("location") or "").strip() or None
            profile.first_seen_at = parse_first_seen(row.get("first_seen"))
            profile.distinguishing_features = (row.get("appearance") or "").strip() or None
            profile.notes = combine_notes(row)
            imported += 1

        session.commit()
        print(f"Imported or updated {imported} dataset profile(s) from {DATASET_CSV_PATH}")
    finally:
        session.close()


if __name__ == "__main__":
    upsert_dataset_profiles()
