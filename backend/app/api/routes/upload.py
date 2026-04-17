from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.upload import UploadResponse
from app.services.ai_detection_service import AIDetectionService
from app.services.cat_service import CatService
from app.services.file_storage import save_upload_file
from app.services.recommendation_service import RecommendationService
from app.services.sighting_service import create_image_and_sighting


router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_image(
    photo: UploadFile = File(...),
    location_text: str = Form(...),
    sighted_at: datetime | None = Form(default=None),
    notes: str | None = Form(default=None),
    cat_profile_id: int | None = Form(default=None),
    uploaded_by: int | None = Form(default=None),
    db: Session = Depends(get_db),
) -> UploadResponse:
    saved_file = await save_upload_file(photo)
    detection = AIDetectionService().detect_from_file_path(saved_file["file_path"])
    profile_created = False

    if cat_profile_id is None:
        created_profile = CatService(db).create_auto_profile(
            location_text=location_text,
            sighted_at=sighted_at,
            notes=notes,
            created_by=uploaded_by,
        )
        cat_profile_id = created_profile.id
        profile_created = True

    image, sighting = create_image_and_sighting(
        db=db,
        file_path=saved_file["file_path"],
        original_filename=saved_file["original_filename"],
        file_size=saved_file["file_size"],
        mime_type=saved_file["mime_type"],
        ai_feature_path=detection.get("cropped_image_path"),
        ai_match_status="detected" if detection.get("has_cat") else "pending",
        cat_profile_id=cat_profile_id,
        uploaded_by=uploaded_by,
        location_text=location_text,
        sighted_at=sighted_at,
        notes=notes,
    )
    recommendations = RecommendationService(db).recommend_for_image(
        saved_file["file_path"],
        exclude_profile_id=cat_profile_id if profile_created else None,
    )
    return UploadResponse(
        message="Upload completed successfully.",
        cat_profile_id=cat_profile_id,
        profile_created=profile_created,
        image=image,
        sighting=sighting,
        recommendations=recommendations,
        detection=detection,
    )
