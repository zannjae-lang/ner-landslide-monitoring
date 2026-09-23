from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ObservationCategory(str, Enum):
    VISIBLE_CRACK = "VISIBLE_CRACK"
    ROCKFALL = "ROCKFALL"
    ROAD_BLOCKAGE = "ROAD_BLOCKAGE"
    WATER_SEEPAGE = "WATER_SEEPAGE"
    SOIL_SUBSIDENCE = "SOIL_SUBSIDENCE"
    RETAINING_WALL_DAMAGE = "RETAINING_WALL_DAMAGE"
    ACTIVE_SLIDE = "ACTIVE_SLIDE"


class VerificationStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    RESOLVED = "resolved"


class FieldReportBase(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    location_id: Optional[str] = None
    location_name: Optional[str] = None
    state: str
    district: str
    reporter_name: str = Field(..., max_length=128)
    reporter_role: str = Field("citizen", description="citizen, field_officer, geologist, ddma_staff")
    contact_number: Optional[str] = None
    observation_category: ObservationCategory
    severity: str = Field("Moderate", description="Low, Moderate, High, Critical")
    description: str = Field(..., min_length=10, max_length=2000)
    photo_url: Optional[str] = None


class FieldReportCreate(FieldReportBase):
    photo_metadata_json: Optional[Dict[str, Any]] = None


class FieldReportUpdate(BaseModel):
    verification_status: VerificationStatus
    reviewer_notes: Optional[str] = None
    reviewed_by: Optional[str] = None


class FieldReportResponse(FieldReportBase):
    id: str
    verification_status: str
    reviewer_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    photo_metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    verified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FieldReportListResponse(BaseModel):
    total: int
    items: List[FieldReportResponse]
