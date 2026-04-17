from pydantic import BaseModel


class DetectionBox(BaseModel):
    label: str
    score: float
    bbox: list[int]


class AIDetectionResult(BaseModel):
    model_loaded: bool = False
    has_cat: bool = False
    confidence: float | None = None
    detections: list[DetectionBox] = []
    cropped_image_path: str | None = None
    message: str
