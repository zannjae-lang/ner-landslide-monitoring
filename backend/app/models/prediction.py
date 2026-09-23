import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=False, index=True)
    prediction_timestamp = Column(DateTime(timezone=True), default=get_utc_now, index=True)
    
    # Model 1 Output
    model1_probability = Column(Float, nullable=True)
    model1_class = Column(String(32), nullable=True)
    
    # Model 2 Output
    model2_probability = Column(Float, nullable=True)
    warning_candidate = Column(Boolean, default=False)
    
    # Environmental Context
    rainfall_24h_mm = Column(Float, default=0.0)
    rainfall_class = Column(String(32), nullable=True)
    rainfall_adjustment = Column(Float, default=0.0)
    
    # Fused Risk Engine Output
    combined_risk_score = Column(Float, nullable=False)
    final_risk = Column(String(32), nullable=False, index=True)
    engine_version = Column(String(16), default="2.0")
    model1_version = Column(String(64), default="model1_v1.0")
    model2_version = Column(String(64), default="model2_v1.0_temporal_candidate")
    
    # Freshness & Prototype
    data_status = Column(String(32), default="Fresh")
    data_age_hours = Column(Float, default=0.0)
    is_stale = Column(Boolean, default=False)
    prototype_flag = Column(Boolean, default=True)
    operational_validation = Column(Boolean, default=False)
    
    details_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    location = relationship("Location", back_populates="predictions")
    alerts = relationship("AlertRecord", back_populates="prediction")
