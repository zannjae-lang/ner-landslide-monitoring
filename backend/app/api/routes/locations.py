from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.location_repository import LocationRepository
from app.schemas.locations import LocationCreate, LocationListResponse, LocationResponse

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get("", response_model=LocationListResponse)
def list_locations(
    state: Optional[str] = Query(None, description="Filter by NER State"),
    district: Optional[str] = Query(None, description="Filter by District"),
    search: Optional[str] = Query(None, description="Search name/district/state"),
    min_lat: Optional[float] = Query(None),
    max_lat: Optional[float] = Query(None),
    min_lon: Optional[float] = Query(None),
    max_lon: Optional[float] = Query(None),
    monitored_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List monitored NER locations with filtering and bounding-box spatial support."""
    repo = LocationRepository(db)
    total, items = repo.list_locations(
        state=state,
        district=district,
        search=search,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        monitored_only=monitored_only,
        skip=skip,
        limit=limit,
    )
    return LocationListResponse(total=total, items=items)


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(location_id: str, db: Session = Depends(get_db)):
    """Retrieve details of a specific monitored station."""
    repo = LocationRepository(db)
    loc = repo.get_by_id(location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc


@router.post("", response_model=LocationResponse, status_code=201)
def create_location(location_in: LocationCreate, db: Session = Depends(get_db)):
    """Add a new monitoring location station."""
    repo = LocationRepository(db)
    return repo.create(location_in)
