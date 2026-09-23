import time
from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config.settings import settings
from app.db.session import get_db
from app.services.ml_models.artifact_loader import model_loader

router = APIRouter(tags=["Health & Status"])

START_TIME = time.time()


@router.get("/health")
def get_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Application and dependency health check endpoint."""
    uptime_sec = round(time.time() - START_TIME, 2)
    
    # Check Database
    db_status = "Healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"Degraded: {str(e)}"

    return {
        "status": "Healthy" if db_status == "Healthy" and model_loader.is_ready else "Degraded",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": uptime_sec,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "model_readiness": model_loader.is_ready,
    }


@router.get("/models/status")
def get_models_status() -> Dict[str, Any]:
    """Model versions, thresholds, artifact availability, and validation flag."""
    return model_loader.get_status_summary()
