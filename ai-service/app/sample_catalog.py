from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path


DATASET_ROOT = Path(os.getenv("DATASET_ROOT", "/workspace/datasets"))
CATALOG_CSV_PATH = DATASET_ROOT / "cat_profiles.csv"
SAMPLE_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CSV_ENCODINGS = ("utf-8-sig", "utf-8", "gb18030", "gbk")


@dataclass(frozen=True)
class SampleCat:
    cat_code: str
    cat_name: str | None
    alias: str | None
    image_folder: Path
    image_paths: tuple[Path, ...]
    area: str | None
    color: str | None
    location: str | None
    sex: str | None
    appearance: str | None
    personality: str | None
    remark: str | None

def load_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Sample catalog not found: {csv_path}")

    last_error: Exception | None = None
    for encoding in CSV_ENCODINGS:
        try:
            with csv_path.open("r", encoding=encoding, newline="") as handle:
                return list(csv.DictReader(handle))
        except UnicodeDecodeError as exc:
            last_error = exc

    raise UnicodeDecodeError(
        "sample_catalog",
        b"",
        0,
        1,
        f"Unable to decode sample catalog with supported encodings: {CSV_ENCODINGS}. Last error: {last_error}",
    )


def list_sample_images(image_folder: Path) -> tuple[Path, ...]:
    if not image_folder.exists():
        return ()

    return tuple(
        path
        for path in sorted(image_folder.iterdir())
        if path.is_file() and path.suffix.lower() in SAMPLE_IMAGE_EXTENSIONS
    )


@lru_cache(maxsize=1)
def load_sample_catalog() -> tuple[SampleCat, ...]:
    rows = load_csv_rows(CATALOG_CSV_PATH)
    catalog: list[SampleCat] = []

    for row in rows:
        cat_code = (row.get("cat_code") or "").strip()
        image_folder_value = (row.get("image_folder") or "").strip()
        if not cat_code or not image_folder_value:
            continue

        image_folder = Path(image_folder_value)
        if not image_folder.is_absolute():
            image_folder = (DATASET_ROOT.parent / image_folder).resolve()

        image_paths = list_sample_images(image_folder)
        if not image_paths:
            continue

        catalog.append(
            SampleCat(
                cat_code=cat_code,
                cat_name=(row.get("cat_name") or "").strip() or None,
                alias=(row.get("alias") or "").strip() or None,
                image_folder=image_folder,
                image_paths=image_paths,
                area=(row.get("area") or "").strip() or None,
                color=(row.get("color") or "").strip() or None,
                location=(row.get("location") or "").strip() or None,
                sex=(row.get("sex") or "").strip() or None,
                appearance=(row.get("appearance") or "").strip() or None,
                personality=(row.get("personality") or "").strip() or None,
                remark=(row.get("remark") or "").strip() or None,
            )
        )

    return tuple(catalog)


def sample_catalog_summary() -> dict[str, int | str]:
    try:
        catalog = load_sample_catalog()
        image_count = sum(len(sample.image_paths) for sample in catalog)
        return {
            "dataset_root": str(DATASET_ROOT),
            "catalog_csv_path": str(CATALOG_CSV_PATH),
            "catalog_ready": "true",
            "sample_cat_count": len(catalog),
            "sample_image_count": image_count,
        }
    except Exception as exc:
        return {
            "dataset_root": str(DATASET_ROOT),
            "catalog_csv_path": str(CATALOG_CSV_PATH),
            "catalog_ready": "false",
            "error": str(exc),
        }
