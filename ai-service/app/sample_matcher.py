"""
Cat individual recognition — two-tier feature extraction:

1. Primary:  DNN features via torchvision ResNet18 (512-d embedding).
              Captures ear shape, face structure, body patterns, texture.
2. Fallback:  Improved handcrafted features (color + edge orientation + 64x64
              grayscale thumbnail). Used when PyTorch is unavailable.

The DNN approach dramatically outperforms color-histogram-only methods for
fine-grained individual recognition across varying lighting and pose.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import logging
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from app.sample_catalog import SampleCat, load_sample_catalog


logger = logging.getLogger(__name__)

THUMBNAIL_SIZE = (64, 64)

# ---------------------------------------------------------------------------
# DNN feature extractor (primary)
# ---------------------------------------------------------------------------

try:
    import torch
    import torchvision.transforms as transforms
    import torchvision.models as models

    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    logger.warning(
        "PyTorch not available — falling back to handcrafted features "
        "(less accurate for individual cat recognition). "
        "Install torch + torchvision to enable DNN feature extraction."
    )

_dnn_model: torch.nn.Module | None = None
_dnn_device: str | None = None
_dnn_transform: transforms.Compose | None = None


def _init_dnn() -> None:
    global _dnn_model, _dnn_device, _dnn_transform
    if _dnn_model is not None or not HAS_TORCH:
        return

    _dnn_device = "cuda" if torch.cuda.is_available() else "cpu"
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    # Remove the classification head → keep 512-d pooled features
    model = torch.nn.Sequential(*list(model.children())[:-1])
    model.eval().to(_dnn_device)
    _dnn_model = model
    _dnn_transform = transforms.Compose([
        transforms.Resize(224),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])
    logger.info("DNN feature extractor ready on %s", _dnn_device)


def _extract_dnn(image: Image.Image) -> np.ndarray:
    _init_dnn()
    tensor = _dnn_transform(image.convert("RGB")).unsqueeze(0).to(_dnn_device)
    with torch.no_grad():
        feat = _dnn_model(tensor).squeeze().cpu().numpy()
    return _normalize(feat)


# ---------------------------------------------------------------------------
# Handcrafted feature extractor (fallback)
# ---------------------------------------------------------------------------


def _normalize(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 0 else v


def _hist(ch: np.ndarray, bins: int) -> np.ndarray:
    hist, _ = np.histogram(ch, bins=bins, range=(0.0, 1.0))
    return hist.astype(np.float32)


def _edge_orient(gray: np.ndarray, bins: int = 18) -> np.ndarray:
    """Edge orientation histogram weighted by gradient magnitude."""
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx**2 + gy**2)
    orient = np.arctan2(gy, gx)  # [-pi, pi]
    orient = np.where(orient < 0, orient + 2 * np.pi, orient)  # [0, 2*pi)
    hist, _ = np.histogram(orient, bins=bins, range=(0.0, 2 * np.pi), weights=mag)
    return hist.astype(np.float32)


def _extract_handcrafted(image: Image.Image) -> np.ndarray:
    """Feature vector: color stats + HSV histogram + edge orientation + 64x64 thumbnail."""
    small = image.convert("RGB").resize((128, 128))
    rgb = np.asarray(small, dtype=np.float32) / 255.0
    hsv = np.asarray(small.convert("HSV"), dtype=np.float32) / 255.0
    gray_thumb = np.asarray(
        image.convert("L").resize(THUMBNAIL_SIZE), dtype=np.float32
    ) / 255.0
    gray_edge = rgb.mean(axis=2)  # 128x128 for edge detection

    feat = np.concatenate([
        rgb.mean(axis=(0, 1)),               #  3
        rgb.std(axis=(0, 1)),                #  3
        _hist(hsv[..., 0], 24),              # 24  hue
        _hist(hsv[..., 1], 16),              # 16  saturation
        _hist(hsv[..., 2], 16),              # 16  value
        _edge_orient(gray_edge, 18),         # 18  texture
        gray_thumb.flatten(),                # 4096 (64x64)
    ]).astype(np.float32)
    return _normalize(feat)


# ---------------------------------------------------------------------------
# Unified entry point — method is locked after first successful extraction
# so that every image in the session uses the same feature dimension.
# ---------------------------------------------------------------------------

_FEATURE_METHOD: str | None = None  # "dnn" or "handcrafted"


def extract_image_feature(image: Image.Image) -> np.ndarray:
    global _FEATURE_METHOD

    if _FEATURE_METHOD is None:
        if HAS_TORCH:
            try:
                feat = _extract_dnn(image)
                _FEATURE_METHOD = "dnn"
                logger.info("Feature extraction locked to DNN (512-d)")
                return feat
            except Exception as exc:
                logger.warning("DNN unavailable (%s), locking to handcrafted", exc)
        _FEATURE_METHOD = "handcrafted"
        logger.info("Feature extraction locked to handcrafted (%d-d)", _extract_handcrafted(image).shape[0])

    if _FEATURE_METHOD == "dnn":
        return _extract_dnn(image)
    return _extract_handcrafted(image)


# ---------------------------------------------------------------------------
# Cached helpers
# ---------------------------------------------------------------------------


@lru_cache(maxsize=512)
def _feature_from_path(image_path: str) -> np.ndarray:
    with Image.open(image_path) as img:
        return extract_image_feature(img)


@lru_cache(maxsize=1)
def _build_sample_index() -> tuple[dict, ...]:
    catalog = load_sample_catalog()
    index: list[dict] = []

    for sample in catalog:
        features = [
            _feature_from_path(str(p)) for p in sample.image_paths
        ]
        if not features:
            continue
        mean_feat = _normalize(np.mean(np.stack(features), axis=0))
        index.append({
            "sample": sample,
            "features": tuple(features),
            "mean": mean_feat,
        })

    return tuple(index)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.clip(np.dot(a, b), 0.0, 1.0))


@dataclass(frozen=True)
class MatchCandidate:
    sample_cat_code: str
    cat_name: str | None
    similarity_score: float
    reason: str


def rank_similar_cats(
    query_image_path: str | Path, top_k: int = 5
) -> list[MatchCandidate]:
    qpath = Path(query_image_path).expanduser().resolve()
    if not qpath.exists():
        raise FileNotFoundError(f"Query image not found: {query_image_path}")

    query_feat = _feature_from_path(str(qpath))
    ranked: list[MatchCandidate] = []

    for item in _build_sample_index():
        sample: SampleCat = item["sample"]
        per_image = [
            cosine_similarity(query_feat, f) for f in item["features"]
        ]
        if not per_image:
            continue

        best_score = max(per_image)
        mean_score = cosine_similarity(query_feat, item["mean"])
        final_score = round(best_score * 0.7 + mean_score * 0.3, 4)

        best_idx = int(np.argmax(per_image))
        best_filename = sample.image_paths[best_idx].name
        name = sample.cat_name or sample.alias or sample.cat_code
        ranked.append(
            MatchCandidate(
                sample_cat_code=sample.cat_code,
                cat_name=name,
                similarity_score=final_score,
                reason=(
                    f"Visual similarity matched {sample.cat_code} "
                    f"({len(sample.image_paths)} reference image(s)); "
                    f"best match: {best_filename}."
                ),
            )
        )

    ranked.sort(key=lambda c: c.similarity_score, reverse=True)
    return ranked[: max(1, top_k)]
