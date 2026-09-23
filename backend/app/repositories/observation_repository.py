from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.observation import EnvironmentalObservation


class ObservationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_latest_by_location(self, location_id: str) -> Optional[EnvironmentalObservation]:
        return (
            self.db.query(EnvironmentalObservation)
            .filter(EnvironmentalObservation.location_id == location_id)
            .order_by(EnvironmentalObservation.observed_at.desc())
            .first()
        )

    def create(self, obs: EnvironmentalObservation) -> EnvironmentalObservation:
        self.db.add(obs)
        self.db.commit()
        self.db.refresh(obs)
        return obs

    def list_by_location(self, location_id: str, limit: int = 50) -> List[EnvironmentalObservation]:
        return (
            self.db.query(EnvironmentalObservation)
            .filter(EnvironmentalObservation.location_id == location_id)
            .order_by(EnvironmentalObservation.observed_at.desc())
            .limit(limit)
            .all()
        )
