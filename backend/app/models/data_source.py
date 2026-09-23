import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text
from app.db.session import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class DataSourceStatusRecord(Base):
    __tablename__ = "data_source_status"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider_id = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(128), nullable=False)
    status = Column(String(32), default="Operational")
    is_available = Column(Boolean, default=True)
    requires_auth = Column(Boolean, default=False)
    latency_ms = Column(Float, nullable=True)
    last_successful_sync = Column(DateTime(timezone=True), nullable=True)
    last_failure = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)
