from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.location import Location
from app.schemas.locations import LocationCreate


class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, location_id: str) -> Optional[Location]:
        return self.db.query(Location).filter(Location.id == location_id).first()

    def get_by_name(self, name: str) -> Optional[Location]:
        return self.db.query(Location).filter(Location.name == name).first()

    def list_locations(
        self,
        state: Optional[str] = None,
        district: Optional[str] = None,
        search: Optional[str] = None,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        monitored_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[int, List[Location]]:
        query = self.db.query(Location)

        if state:
            query = query.filter(Location.state.ilike(f"%{state}%"))
        if district:
            query = query.filter(Location.district.ilike(f"%{district}%"))
        if search:
            query = query.filter(
                or_(
                    Location.name.ilike(f"%{search}%"),
                    Location.district.ilike(f"%{search}%"),
                    Location.state.ilike(f"%{search}%"),
                )
            )
        if monitored_only:
            query = query.filter(Location.monitored == True)

        if min_lat is not None and max_lat is not None:
            query = query.filter(Location.latitude.between(min_lat, max_lat))
        if min_lon is not None and max_lon is not None:
            query = query.filter(Location.longitude.between(min_lon, max_lon))

        total = query.count()
        items = query.order_by(Location.state, Location.district, Location.name).offset(skip).limit(limit).all()
        return total, items

    def create(self, location_in: LocationCreate) -> Location:
        loc = Location(**location_in.model_dump())
        self.db.add(loc)
        self.db.commit()
        self.db.refresh(loc)
        return loc

    def bulk_create(self, locations: List[Location]) -> List[Location]:
        self.db.add_all(locations)
        self.db.commit()
        return locations
