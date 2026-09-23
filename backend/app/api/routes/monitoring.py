from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.schemas.telemetry import SystemTelemetryResponse
from app.services.monitoring.health_telemetry_service import health_telemetry_service

router = APIRouter(prefix="/monitoring", tags=["Operational Observability & Telemetry"])


@router.get("/telemetry", response_model=SystemTelemetryResponse)
async def get_system_operational_telemetry(db: Session = Depends(get_db)):
    """Retrieve operational telemetry metrics across data streams, model latencies, and uptime grades."""
    db_status = "Healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"Degraded: {str(e)}"

    return await health_telemetry_service.get_system_telemetry(db_status=db_status)
