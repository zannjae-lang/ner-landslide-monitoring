from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.config.model_config import RiskLevel


class AlertBase(BaseModel):
    location_id: str
    location_name: str
    state: str
    district: str
    severity: RiskLevel
    title: str
    message: str
    score: float
    rainfall_24h_mm: float
    status: str = "active"  # active, acknowledged, resolved
    source_prediction_id: Optional[str] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    status: str = Field(..., description="active, acknowledged, or resolved")
    notes: Optional[str] = None


class AlertResponse(AlertBase):
    id: str
    created_at: datetime
    updated_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    audit_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AlertListResponse(BaseModel):
    total: int
    items: List[AlertResponse]
