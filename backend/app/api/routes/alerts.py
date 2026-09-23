from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.alert_repository import AlertRepository
from app.schemas.alerts import AlertListResponse, AlertResponse, AlertUpdate

router = APIRouter(prefix="/alerts", tags=["Alerts & Early Warnings"])


@router.get("", response_model=AlertListResponse)
def list_alerts(
    severity: Optional[str] = Query(None, description="Watch, Alert, or Critical"),
    status: Optional[str] = Query(None, description="active, acknowledged, or resolved"),
    state: Optional[str] = Query(None, description="Filter by NER State"),
    district: Optional[str] = Query(None, description="Filter by District"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List early-warning alert records with status and severity filters."""
    repo = AlertRepository(db)
    total, items = repo.list_alerts(
        severity=severity,
        status=status,
        state=state,
        district=district,
        skip=skip,
        limit=limit,
    )
    
    alert_responses = []
    for a in items:
        loc = a.location
        alert_responses.append(
            AlertResponse(
                id=a.id,
                location_id=a.location_id,
                location_name=loc.name if loc else "Unknown",
                state=loc.state if loc else "Unknown",
                district=loc.district if loc else "Unknown",
                severity=a.severity,
                title=a.title,
                message=a.message,
                score=a.score,
                rainfall_24h_mm=a.rainfall_24h_mm,
                status=a.status,
                source_prediction_id=a.source_prediction_id,
                created_at=a.created_at,
                updated_at=a.updated_at,
                acknowledged_at=a.acknowledged_at,
                resolved_at=a.resolved_at,
                audit_notes=a.audit_notes,
            )
        )

    return AlertListResponse(total=total, items=alert_responses)


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    """Get single alert details."""
    repo = AlertRepository(db)
    a = repo.get_by_id(alert_id)
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    loc = a.location
    return AlertResponse(
        id=a.id,
        location_id=a.location_id,
        location_name=loc.name if loc else "Unknown",
        state=loc.state if loc else "Unknown",
        district=loc.district if loc else "Unknown",
        severity=a.severity,
        title=a.title,
        message=a.message,
        score=a.score,
        rainfall_24h_mm=a.rainfall_24h_mm,
        status=a.status,
        source_prediction_id=a.source_prediction_id,
        created_at=a.created_at,
        updated_at=a.updated_at,
        acknowledged_at=a.acknowledged_at,
        resolved_at=a.resolved_at,
        audit_notes=a.audit_notes,
    )


@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert_status(alert_id: str, update_in: AlertUpdate, db: Session = Depends(get_db)):
    """Acknowledge, assign, verify, or resolve an active alert with audit logging."""
    valid_statuses = [
        "active",
        "acknowledged",
        "assigned",
        "field_verification_requested",
        "verified",
        "resolved",
        "archived",
    ]
    if update_in.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of: {', '.join(valid_statuses)}",
        )

    from app.services.alerts.alert_workflow_service import alert_workflow_service

    updated = alert_workflow_service.update_alert_lifecycle(
        db=db,
        alert_id=alert_id,
        new_status=update_in.status,
        notes=update_in.notes,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Alert not found")
    loc = updated.location

    return AlertResponse(
        id=updated.id,
        location_id=updated.location_id,
        location_name=loc.name if loc else "Unknown",
        state=loc.state if loc else "Unknown",
        district=loc.district if loc else "Unknown",
        severity=updated.severity,
        title=updated.title,
        message=updated.message,
        score=updated.score,
        rainfall_24h_mm=updated.rainfall_24h_mm,
        status=updated.status,
        source_prediction_id=updated.source_prediction_id,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
        acknowledged_at=updated.acknowledged_at,
        resolved_at=updated.resolved_at,
        audit_notes=updated.audit_notes,
    )
