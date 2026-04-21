from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.cat import CatProfileCreate, CatProfileDetail, CatProfileListItem
from app.services.cat_service import ALL_PROFILE_SOURCES, CatService


router = APIRouter(prefix="/cats")


@router.get("", response_model=list[CatProfileListItem])
def list_cats(
    include_all: bool = Query(default=False, description="Internal mode: include sample and test profiles."),
    db: Session = Depends(get_db),
) -> list[CatProfileListItem]:
    allowed_sources = ALL_PROFILE_SOURCES if include_all else ("real",)
    return CatService(db).list_profiles(allowed_sources=allowed_sources)


@router.get("/{cat_id}", response_model=CatProfileDetail)
def get_cat(
    cat_id: int,
    include_all: bool = Query(default=False, description="Internal mode: allow sample and test profiles."),
    db: Session = Depends(get_db),
) -> CatProfileDetail:
    allowed_sources = ALL_PROFILE_SOURCES if include_all else ("real",)
    cat = CatService(db).get_profile(cat_id, allowed_sources=allowed_sources)
    if cat is None:
        raise HTTPException(status_code=404, detail="Cat profile not found.")
    return cat


@router.post("", response_model=CatProfileDetail, status_code=201)
def create_cat(payload: CatProfileCreate, db: Session = Depends(get_db)) -> CatProfileDetail:
    return CatService(db).create_profile(payload)
