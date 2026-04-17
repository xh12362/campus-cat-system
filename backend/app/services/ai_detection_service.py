import json
from urllib import error, parse, request


class AIDetectionService:
    def __init__(self, base_url: str = "http://ai-service:8001") -> None:
        self.base_url = base_url.rstrip("/")

    def detect_from_file_path(self, file_path: str) -> dict:
        try:
            data = parse.urlencode({"file_path": file_path}).encode("utf-8")
            req = request.Request(
                f"{self.base_url}/api/ai/detect",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            return {
                "model_loaded": False,
                "has_cat": False,
                "confidence": None,
                "detections": [],
                "cropped_image_path": None,
                "message": f"AI detection unavailable: {exc}",
            }
