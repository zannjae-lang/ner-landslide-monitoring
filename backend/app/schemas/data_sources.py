from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DataSourceStatusResponse(BaseModel):
    provider_id: str
    name: str
    description: str
    status: str  # Operational, Degraded, Inactive, Auth Required
    is_available: bool
    requires_auth: bool
    latency_ms: Optional[float] = None
    last_successful_sync: Optional[datetime] = None
    coverage: str
    update_cadence: str
    error_message: Optional[str] = None


class DataSourceListResponse(BaseModel):
    total: int
    providers: List[DataSourceStatusResponse]
