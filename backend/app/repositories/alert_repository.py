from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.alert import AlertRecord
from app.models.location import Location


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, alert_id: str) -> Optional[AlertRecord]:
        return self.db.query(AlertRecord).filter(AlertRecord.id == alert_id).first()

    def create(self, alert: AlertRecord) -> AlertRecord:
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def list_alerts(
        self,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        state: Optional[str] = None,
        district: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[int, List[AlertRecord]]:
        query = self.db.query(AlertRecord).join(Location, AlertRecord.location_id == Location.id)

        if severity:
            query = query.filter(AlertRecord.severity == severity)
        if status:
            query = query.filter(AlertRecord.status == status)
        if state:
            query = query.filter(Location.state.ilike(f"%{state}%"))
        if district:
            query = query.filter(Location.district.ilike(f"%{district}%"))

        total = query.count()
        items = query.order_by(desc(AlertRecord.created_at)).offset(skip).limit(limit).all()
        return total, items

    def update_status(self, alert_id: str, new_status: str, notes: Optional[str] = None) -> Optional[AlertRecord]:
        alert = self.get_by_id(alert_id)
        if not alert:
            return None

        now = datetime.now(timezone.utc)
        alert.status = new_status
        if notes:
            alert.audit_notes = notes

        if new_status == "acknowledged":
            alert.acknowledged_at = now
        elif new_status == "resolved":
            alert.resolved_at = now

        self.db.commit()
        self.db.refresh(alert)
        return alert
