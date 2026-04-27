from functools import lru_cache
from io import BytesIO
import os
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from PIL import Image
from PIL import UnidentifiedImageError
from pydantic import BaseModel, Field
from ultralytics import YOLO
import uvicorn

from app.sample_catalog import sample_catalog_summary
from app.sample_matcher import rank_similar_cats


HOST = "0.0.0.0"
PORT = int(os.getenv("AI_SERVICE_PORT", "8001"))
MODEL_PATH = Path(os.getenv("YOLO_MODEL_PATH", "/workspace/models/yolov8m.pt"))
CROPPED_DIR = Path(os.getenv("CROPPED_DIR", "/workspace/uploads/cropped"))

# Detection tuning
DETECTION_CONF = float(os.getenv("DETECTION_CONF", "0.25"))
DETECTION_IOU = float(os.getenv("DETECTION_IOU", "0.45"))
CLAHE_ENABLED = os.getenv("CLAHE_ENABLED", "true").lower() == "true"

app = FastAPI(
    title="Campus Cat AI Service",
    version="0.1.0",
    description="YOLO-powered cat detection service for the campus cat system.",
)


class RecommendRequest(BaseModel):
    cropped_image_path: str
    top_k: int = Field(default=5, ge=1, le=10)


class RecommendCandidate(BaseModel):
    sample_cat_code: str
    cat_name: str | None = None
    similarity_score: float
    reason: str


class RecommendResponse(BaseModel):
    query_image_path: str
    top_k: int
    candidates: list[RecommendCandidate]


@lru_cache(maxsize=1)
def get_model() -> YOLO:
    """Load the YOLO model once. Auto-downloads by name if not found locally."""
    if MODEL_PATH.exists():
        return YOLO(str(MODEL_PATH))
    return YOLO(MODEL_PATH.name)


def normalize_image_path(file_path: str) -> Path:
    """Resolve user-provided paths to reduce cwd-dependent behavior."""
    return Path(file_path).expanduser().resolve()


def apply_clahe(image: Image.Image) -> Image.Image:
    """Enhance contrast for low-light images using CLAHE."""
    img = np.array(image)
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    return Image.fromarray(enhanced)


def load_image(file_path: str | None, file_bytes: bytes | None) -> tuple[Image.Image, str]:
    if file_bytes is not None:
        try:
            return Image.open(BytesIO(file_bytes)).convert("RGB"), ".jpg"
        except UnidentifiedImageError as exc:
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.") from exc

    if not file_path:
        raise HTTPException(status_code=400, detail="Either file or file_path is required.")

    image_path = normalize_image_path(file_path)
    if not image_path.exists():
        raise HTTPException(status_code=404, detail=f"Image file not found: {file_path}")

    suffix = image_path.suffix or ".jpg"
    try:
        return Image.open(image_path).convert("RGB"), suffix
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail=f"Image file is invalid: {file_path}") from exc


def run_detection(image: Image.Image) -> tuple[list[dict], float | None]:
    if CLAHE_ENABLED:
        image = apply_clahe(image)

    model = get_model()
    results = model.predict(image, conf=DETECTION_CONF, iou=DETECTION_IOU, verbose=False)
    if not results:
        return [], None

    result = results[0]
    boxes = result.boxes
    if boxes is None:
        return [], None

    names = result.names
    detections: list[dict] = []
    top_confidence: float | None = None

    for box in boxes:
        class_id = int(box.cls[0].item())
        label = str(names.get(class_id, class_id)).lower()
        if label != "cat":
            continue

        score = float(box.conf[0].item())
        bbox = [int(value) for value in box.xyxy[0].tolist()]
        detections.append({"label": "cat", "score": score, "bbox": bbox})

        if top_confidence is None or score > top_confidence:
            top_confidence = score

    return detections, top_confidence


def save_best_crop(image: Image.Image, detections: list[dict], suffix: str) -> str | None:
    if not detections:
        return None

    CROPPED_DIR.mkdir(parents=True, exist_ok=True)
    best_detection = max(detections, key=lambda item: item["score"])
    left, top, right, bottom = best_detection["bbox"]
    width, height = image.size
    left = max(0, min(left, width))
    top = max(0, min(top, height))
    right = max(left + 1, min(right, width))
    bottom = max(top + 1, min(bottom, height))
    cropped = image.crop((left, top, right, bottom))
    target_path = CROPPED_DIR / f"{uuid4().hex}{suffix or '.jpg'}"
    cropped.save(target_path)
    return str(target_path)


@app.get("/")
def root() -> dict:
    return {
        "service": "ai-service",
        "status": "ok",
        "message": "AI service is running.",
    }


@app.get("/health")
def health() -> dict:
    model_exists = MODEL_PATH.exists()
    dataset_summary = sample_catalog_summary()
    return {
        "service": "ai-service",
        "status": "ok" if model_exists else "degraded",
        "model_path": str(MODEL_PATH),
        "model_exists": model_exists,
        "cropped_dir": str(CROPPED_DIR),
        "cropped_dir_exists": CROPPED_DIR.exists(),
        "dataset": dataset_summary,
    }


@app.post("/api/ai/detect")
async def detect_cat(
    file: UploadFile | None = File(default=None),
    file_path: str | None = Form(default=None),
) -> dict:
    try:
        file_bytes = await file.read() if file is not None else None
        image, suffix = load_image(file_path=file_path, file_bytes=file_bytes)
        detections, confidence = run_detection(image)
        cropped_image_path = save_best_crop(image, detections, suffix)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Detection failed: {exc}") from exc

    has_cat = bool(detections)
    return {
        "model_loaded": True,
        "has_cat": has_cat,
        "confidence": confidence,
        "detections": detections,
        "cropped_image_path": cropped_image_path,
        "message": "Cat detected successfully." if has_cat else "No cat detected in the image.",
    }


@app.post("/api/ai/recommend", response_model=RecommendResponse)
def recommend_similar_cats(payload: RecommendRequest) -> RecommendResponse:
    try:
        candidates = rank_similar_cats(
            query_image_path=payload.cropped_image_path,
            top_k=payload.top_k,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {exc}") from exc

    return RecommendResponse(
        query_image_path=payload.cropped_image_path,
        top_k=payload.top_k,
        candidates=[
            RecommendCandidate(
                sample_cat_code=item.sample_cat_code,
                cat_name=item.cat_name,
                similarity_score=item.similarity_score,
                reason=item.reason,
            )
            for item in candidates
        ],
    )


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, reload=False)
