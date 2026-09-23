import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, JSON, String, Text
from app.db.session import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class FieldReportRecord(Base):
    __tablename__ = "field_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=True, index=True)
    
    reporter_name = Column(String(128), nullable=False)
    reporter_role = Column(String(64), default="citizen", index=True)  # citizen, field_officer, geologist, ddma_staff
    contact_number = Column(String(32), nullable=True)
    
    state = Column(String(64), nullable=False, index=True)
    district = Column(String(64), nullable=False, index=True)
    location_name = Column(String(128), nullable=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    
    observation_category = Column(String(64), nullable=False, index=True)
    # VISIBLE_CRACK, ROCKFALL, ROAD_BLOCKAGE, WATER_SEEPAGE, SOIL_SUBSIDENCE, RETAINING_WALL_DAMAGE, ACTIVE_SLIDE
    severity = Column(String(32), default="Moderate", index=True)  # Low, Moderate, High, Critical
    description = Column(Text, nullable=False)
    
    photo_url = Column(String(512), nullable=True)
    photo_metadata_json = Column(JSON, nullable=True)
    
    verification_status = Column(String(32), default="submitted", index=True)  # submitted, under_review, verified, rejected, resolved
    reviewer_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(128), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, index=True)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)
