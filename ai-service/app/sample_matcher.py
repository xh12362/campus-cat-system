from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

from app.sample_catalog import SampleCat, load_sample_catalog


THUMBNAIL_SIZE = (16, 16)


@dataclass(frozen=True)
class MatchCandidate:
    sample_cat_code: str
    cat_name: str | None
    similarity_score: float
    reason: str


def _normalize_vector(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm == 0:
        return vector
    return vector / norm


def _histogram(channel: np.ndarray, bins: int) -> np.ndarray:
    hist, _ = np.histogram(channel, bins=bins, range=(0.0, 1.0))
    return hist.astype(np.float32)


def extract_image_feature(image: Image.Image) -> np.ndarray:
    rgb_image = image.convert("RGB").resize((96, 96))
    rgb_array = np.asarray(rgb_image, dtype=np.float32) / 255.0
    hsv_array = np.asarray(rgb_image.convert("HSV"), dtype=np.float32) / 255.0
    gray_array = np.asarray(image.convert("L").resize(THUMBNAIL_SIZE), dtype=np.float32) / 255.0

    mean_rgb = rgb_array.mean(axis=(0, 1))
    std_rgb = rgb_array.std(axis=(0, 1))
    hue_hist = _histogram(hsv_array[..., 0], bins=12)
    sat_hist = _histogram(hsv_array[..., 1], bins=8)
    val_hist = _histogram(hsv_array[..., 2], bins=8)
    thumbnail = gray_array.flatten()

    feature = np.concatenate(
        [
            mean_rgb,
            std_rgb,
            hue_hist,
            sat_hist,
            val_hist,
            thumbnail,
        ]
    ).astype(np.float32)
    return _normalize_vector(feature)


@lru_cache(maxsize=512)
def extract_feature_from_path(image_path: str) -> np.ndarray:
    with Image.open(image_path) as image:
        return extract_image_feature(image)


@lru_cache(maxsize=1)
def build_sample_index() -> tuple[dict, ...]:
    catalog = load_sample_catalog()
    index: list[dict] = []

    for sample in catalog:
        image_features = [extract_feature_from_path(str(path)) for path in sample.image_paths]
        if not image_features:
            continue

        mean_feature = _normalize_vector(np.mean(np.stack(image_features), axis=0))
        index.append(
            {
                "sample": sample,
                "image_features": tuple(image_features),
                "mean_feature": mean_feature,
            }
        )

    return tuple(index)


def cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.clip(np.dot(left, right), 0.0, 1.0))


def rank_similar_cats(query_image_path: str | Path, top_k: int = 5) -> list[MatchCandidate]:
    query_path = Path(query_image_path).expanduser().resolve()
    if not query_path.exists():
        raise FileNotFoundError(f"Query image not found: {query_image_path}")

    query_feature = extract_feature_from_path(str(query_path))
    ranked: list[MatchCandidate] = []

    for item in build_sample_index():
        sample: SampleCat = item["sample"]
        image_scores = [cosine_similarity(query_feature, feature) for feature in item["image_features"]]
        if not image_scores:
            continue

        best_score = max(image_scores)
        mean_score = cosine_similarity(query_feature, item["mean_feature"])
        final_score = round((best_score * 0.7) + (mean_score * 0.3), 4)

        best_sample_path = sample.image_paths[int(np.argmax(image_scores))]
        sample_count = len(sample.image_paths)
        name = sample.cat_name or sample.alias or sample.cat_code
        reason = (
            f"Visual similarity matched dataset sample {sample.cat_code} "
            f"using {sample_count} reference image(s); best reference: {best_sample_path.name}."
        )
        ranked.append(
            MatchCandidate(
                sample_cat_code=sample.cat_code,
                cat_name=name,
                similarity_score=final_score,
                reason=reason,
            )
        )

    ranked.sort(key=lambda candidate: candidate.similarity_score, reverse=True)
    return ranked[: max(1, top_k)]
