from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.cat import CatProfileCreate, CatProfileDetail, CatProfileListItem
from app.services.cat_service import CatService


router = APIRouter(prefix="/cats")


@router.get("", response_model=list[CatProfileListItem])
def list_cats(db: Session = Depends(get_db)) -> list[CatProfileListItem]:
    return CatService(db).list_profiles()


@router.get("/{cat_id}", response_model=CatProfileDetail)
def get_cat(cat_id: int, db: Session = Depends(get_db)) -> CatProfileDetail:
    cat = CatService(db).get_profile(cat_id)
    if cat is None:
        raise HTTPException(status_code=404, detail="Cat profile not found.")
    return cat


@router.post("", response_model=CatProfileDetail, status_code=201)
def create_cat(payload: CatProfileCreate, db: Session = Depends(get_db)) -> CatProfileDetail:
    return CatService(db).create_profile(payload)
