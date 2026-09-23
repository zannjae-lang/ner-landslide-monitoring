from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ProviderTelemetry(BaseModel):
    provider_id: str
    name: str
    status: str
    is_available: bool
    requires_auth: bool
    latency_ms: Optional[float] = None
    success_rate_pct: float = 100.0
    total_calls: int = 0
    last_sync_time: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ModelTelemetry(BaseModel):
    model_id: str
    name: str
    version: str
    is_ready: bool
    threshold: float
    total_inferences: int = 0
    mean_inference_time_ms: float = 0.0
    operational_validation: bool = False


class SystemTelemetryResponse(BaseModel):
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    uptime_seconds: float
    environment: str
    overall_status: str  # Healthy, Degraded, Critical
    overall_health_grade: str  # A, B, C, D
    database_status: str
    providers: List[ProviderTelemetry] = Field(default_factory=list)
    models: List[ModelTelemetry] = Field(default_factory=list)
    scheduler_running: bool = True
    active_background_jobs_count: int = 0
