import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class EnvironmentalObservation(Base):
    __tablename__ = "environmental_observations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=False, index=True)
    source = Column(String(64), nullable=False)
    observed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    received_at = Column(DateTime(timezone=True), default=get_utc_now)
    
    # Rainfall Accumulations
    rainfall_1h_mm = Column(Float, default=0.0)
    rainfall_3h_mm = Column(Float, default=0.0)
    rainfall_6h_mm = Column(Float, default=0.0)
    rainfall_12h_mm = Column(Float, default=0.0)
    rainfall_24h_mm = Column(Float, default=0.0)
    rainfall_3day_mm = Column(Float, default=0.0)
    rainfall_7day_mm = Column(Float, default=0.0)
    
    # Soil Moisture
    soil_moisture_layer_1 = Column(Float, nullable=True)
    soil_moisture_layer_2 = Column(Float, nullable=True)
    
    # Atmospheric
    temperature_c = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)
    
    quality_status = Column(String(32), default="Fresh")
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    location = relationship("Location", back_populates="observations")
