from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


async def save_upload_file(upload_file: UploadFile) -> dict:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(upload_file.filename or "").suffix or ".jpg"
    filename = f"{uuid4().hex}{suffix}"
    target_path = settings.upload_dir / filename
    content = await upload_file.read()
    target_path.write_bytes(content)
    return {
        "file_path": str(target_path),
        "original_filename": upload_file.filename,
        "file_size": len(content),
        "mime_type": upload_file.content_type,
    }
