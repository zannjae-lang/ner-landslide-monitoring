import re
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.logger import logger
from app.models.field_report import FieldReportRecord
from app.schemas.field_reports import FieldReportCreate, FieldReportUpdate


class CrowdsourceService:
    """Manages ground-truth citizen & field officer evidence collection, sanitization, and triage."""

    def sanitize_text(self, text: str) -> str:
        # Strip script tags and dangerous HTML characters
        cleaned = re.sub(r"<[^>]*>", "", text)
        return cleaned.strip()

    def submit_report(self, db: Session, report_in: FieldReportCreate) -> FieldReportRecord:
        clean_desc = self.sanitize_text(report_in.description)
        clean_name = self.sanitize_text(report_in.reporter_name)

        record = FieldReportRecord(
            location_id=report_in.location_id,
            reporter_name=clean_name,
            reporter_role=report_in.reporter_role,
            contact_number=report_in.contact_number,
            state=report_in.state,
            district=report_in.district,
            location_name=report_in.location_name,
            latitude=report_in.latitude,
            longitude=report_in.longitude,
            observation_category=report_in.observation_category.value,
            severity=report_in.severity,
            description=clean_desc,
            photo_url=report_in.photo_url,
            photo_metadata_json=report_in.photo_metadata_json,
            verification_status="submitted",
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def list_reports(
        self,
        db: Session,
        state: Optional[str] = None,
        district: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[int, List[FieldReportRecord]]:
        query = db.query(FieldReportRecord)

        if state:
            query = query.filter(FieldReportRecord.state.ilike(f"%{state}%"))
        if district:
            query = query.filter(FieldReportRecord.district.ilike(f"%{district}%"))
        if status:
            query = query.filter(FieldReportRecord.verification_status == status)
        if category:
            query = query.filter(FieldReportRecord.observation_category == category)

        total = query.count()
        items = query.order_by(desc(FieldReportRecord.created_at)).offset(skip).limit(limit).all()
        return total, items

    def get_by_id(self, db: Session, report_id: str) -> Optional[FieldReportRecord]:
        return db.query(FieldReportRecord).filter(FieldReportRecord.id == report_id).first()

    def update_verification_status(
        self,
        db: Session,
        report_id: str,
        update_in: FieldReportUpdate,
    ) -> Optional[FieldReportRecord]:
        record = self.get_by_id(db, report_id)
        if not record:
            return None

        record.verification_status = update_in.verification_status.value
        if update_in.reviewer_notes:
            record.reviewer_notes = self.sanitize_text(update_in.reviewer_notes)
        if update_in.reviewed_by:
            record.reviewed_by = self.sanitize_text(update_in.reviewed_by)

        if update_in.verification_status.value in ["verified", "resolved"]:
            record.verified_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(record)
        return record


crowdsource_service = CrowdsourceService()
