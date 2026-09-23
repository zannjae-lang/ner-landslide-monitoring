from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.location import Location
from app.models.prediction import PredictionRecord


class PredictionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_latest_by_location(self, location_id: str) -> Optional[PredictionRecord]:
        return (
            self.db.query(PredictionRecord)
            .filter(PredictionRecord.location_id == location_id)
            .order_by(PredictionRecord.prediction_timestamp.desc())
            .first()
        )

    def create(self, pred: PredictionRecord) -> PredictionRecord:
        self.db.add(pred)
        self.db.commit()
        self.db.refresh(pred)
        return pred

    def list_predictions(
        self,
        location_id: Optional[str] = None,
        state: Optional[str] = None,
        district: Optional[str] = None,
        risk_level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[int, List[PredictionRecord]]:
        query = self.db.query(PredictionRecord).join(Location, PredictionRecord.location_id == Location.id)

        if location_id:
            query = query.filter(PredictionRecord.location_id == location_id)
        if state:
            query = query.filter(Location.state.ilike(f"%{state}%"))
        if district:
            query = query.filter(Location.district.ilike(f"%{district}%"))
        if risk_level:
            query = query.filter(PredictionRecord.final_risk == risk_level)
        if start_time:
            query = query.filter(PredictionRecord.prediction_timestamp >= start_time)
        if end_time:
            query = query.filter(PredictionRecord.prediction_timestamp <= end_time)

        total = query.count()
        items = query.order_by(desc(PredictionRecord.prediction_timestamp)).offset(skip).limit(limit).all()
        return total, items
