from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.field_reports import (
    FieldReportCreate,
    FieldReportListResponse,
    FieldReportResponse,
    FieldReportUpdate,
)
from app.services.evidence.crowdsource_service import crowdsource_service

router = APIRouter(prefix="/field-reports", tags=["Field Evidence & Citizen Reports"])


@router.post("", response_model=FieldReportResponse)
def submit_field_report(report_in: FieldReportCreate, db: Session = Depends(get_db)):
    """Submit a ground-truth field evidence or citizen landslide hazard report."""
    try:
        return crowdsource_service.submit_report(db, report_in)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit field report: {str(e)}",
        )


@router.get("", response_model=FieldReportListResponse)
def list_field_reports(
    state: Optional[str] = Query(None, description="Filter by NER State"),
    district: Optional[str] = Query(None, description="Filter by District"),
    status: Optional[str] = Query(None, description="submitted, under_review, verified, rejected, resolved"),
    category: Optional[str] = Query(None, description="VISIBLE_CRACK, ROCKFALL, ROAD_BLOCKAGE, etc."),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve field evidence and citizen reports with filtering for DDMA verification review."""
    total, items = crowdsource_service.list_reports(
        db=db,
        state=state,
        district=district,
        status=status,
        category=category,
        skip=skip,
        limit=limit,
    )
    return FieldReportListResponse(total=total, items=items)


@router.get("/{report_id}", response_model=FieldReportResponse)
def get_field_report_by_id(report_id: str, db: Session = Depends(get_db)):
    """Get single field report details."""
    report = crowdsource_service.get_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Field report not found")
    return report


@router.patch("/{report_id}", response_model=FieldReportResponse)
def update_report_verification_status(
    report_id: str,
    update_in: FieldReportUpdate,
    db: Session = Depends(get_db),
):
    """Update field report status during DDMA triage review (e.g. mark verified, rejected, or resolved)."""
    updated = crowdsource_service.update_verification_status(db, report_id, update_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Field report not found")
    return updated
