from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.cat_profile import PROFILE_SOURCE_REAL
from app.schemas.upload import (
    CreateProfileFromUploadRequest,
    CreateProfileFromUploadResponse,
    UploadResponse,
)
from app.services.ai_detection_service import AIDetectionService
from app.services.cat_service import CatService
from app.services.file_storage import save_upload_file
from app.services.recommendation_service import RecommendationService
from app.services.sighting_service import (
    assign_image_and_sighting_to_profile,
    create_image_and_sighting,
    get_image_and_sighting,
)


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
        detection.get("cropped_image_path"),
        exclude_profile_id=cat_profile_id,
    )
    return UploadResponse(
        message="Upload completed successfully.",
        cat_profile_id=cat_profile_id,
        profile_created=False,
        image=image,
        sighting=sighting,
        recommendations=recommendations,
        detection=detection,
    )


@router.post("/upload/create-profile", response_model=CreateProfileFromUploadResponse)
def create_profile_from_upload(
    payload: CreateProfileFromUploadRequest,
    db: Session = Depends(get_db),
) -> CreateProfileFromUploadResponse:
    image, sighting = get_image_and_sighting(
        db,
        image_id=payload.image_id,
        sighting_id=payload.sighting_id,
    )
    if image is None or sighting is None:
        raise HTTPException(status_code=404, detail="Upload record not found.")
    if sighting.image_id != image.id:
        raise HTTPException(status_code=400, detail="Image and sighting do not belong to the same upload.")
    if image.cat_profile_id is not None or sighting.cat_profile_id is not None:
        raise HTTPException(status_code=409, detail="This upload has already been linked to a cat profile.")

    created_profile = CatService(db).create_auto_profile(
        location_text=sighting.location_text,
        sighted_at=sighting.sighted_at,
        notes=sighting.notes,
        created_by=sighting.reported_by,
        profile_source=PROFILE_SOURCE_REAL,
    )
    image, sighting = assign_image_and_sighting_to_profile(
        db,
        image=image,
        sighting=sighting,
        cat_profile_id=created_profile.id,
    )
    return CreateProfileFromUploadResponse(
        message="Cat profile created successfully from this upload.",
        cat_profile_id=created_profile.id,
        profile_created=True,
        image=image,
        sighting=sighting,
    )
