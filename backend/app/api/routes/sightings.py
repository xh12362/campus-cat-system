from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.sighting import SightingListItem
from app.services.sighting_service import list_sightings


router = APIRouter(prefix="/sightings")


@router.get("", response_model=list[SightingListItem])
def get_sightings(db: Session = Depends(get_db)) -> list[SightingListItem]:
    return list_sightings(db)
