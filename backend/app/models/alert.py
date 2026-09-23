import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class AlertRecord(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=False, index=True)
    source_prediction_id = Column(String(36), ForeignKey("predictions.id"), nullable=True, index=True)
    
    severity = Column(String(32), nullable=False, index=True)  # Watch, Alert, Critical
    title = Column(String(256), nullable=False)
    message = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    rainfall_24h_mm = Column(Float, default=0.0)
    
    status = Column(String(32), default="active", index=True)  # active, acknowledged, resolved
    audit_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, index=True)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    location = relationship("Location", back_populates="alerts")
    prediction = relationship("PredictionRecord", back_populates="alerts")
