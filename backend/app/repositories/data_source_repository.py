from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.data_source import DataSourceStatusRecord


class DataSourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_provider_id(self, provider_id: str) -> Optional[DataSourceStatusRecord]:
        return self.db.query(DataSourceStatusRecord).filter(DataSourceStatusRecord.provider_id == provider_id).first()

    def list_all(self) -> List[DataSourceStatusRecord]:
        return self.db.query(DataSourceStatusRecord).order_by(DataSourceStatusRecord.provider_id).all()

    def update_status(
        self,
        provider_id: str,
        name: str,
        status: str,
        is_available: bool,
        requires_auth: bool = False,
        latency_ms: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> DataSourceStatusRecord:
        record = self.get_by_provider_id(provider_id)
        now = datetime.now(timezone.utc)
        if not record:
            record = DataSourceStatusRecord(
                provider_id=provider_id,
                name=name,
                status=status,
                is_available=is_available,
                requires_auth=requires_auth,
                latency_ms=latency_ms,
                last_successful_sync=now if is_available else None,
                last_failure=now if not is_available else None,
                error_message=error_message,
            )
            self.db.add(record)
        else:
            record.status = status
            record.is_available = is_available
            record.latency_ms = latency_ms
            record.error_message = error_message
            if is_available:
                record.last_successful_sync = now
            else:
                record.last_failure = now
            record.updated_at = now

        self.db.commit()
        self.db.refresh(record)
        return record
