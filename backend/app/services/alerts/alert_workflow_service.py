import hashlib
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.logger import logger
from app.models.alert import AlertRecord
from app.models.location import Location
from app.schemas.alerts import AlertResponse


class AlertWorkflowService:
    """Manages the formal DDMA early-warning alert lifecycle, deduplication cooldowns, and audit trails."""

    VALID_TRANSITIONS = {
        "active": ["acknowledged", "assigned", "resolved", "archived"],
        "acknowledged": ["assigned", "field_verification_requested", "verified", "resolved"],
        "assigned": ["field_verification_requested", "verified", "resolved"],
        "field_verification_requested": ["verified", "resolved", "archived"],
        "verified": ["resolved", "archived"],
        "resolved": ["archived", "active"],
        "archived": [],
    }

    def generate_fingerprint(self, location_id: str, severity: str) -> str:
        raw = f"{location_id}_{severity}_{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H')}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def should_deduplicate(self, db: Session, location_id: str, severity: str, cooldown_hours: float = 3.0) -> bool:
        """Check if an active alert for the same location and severity was created recently."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=cooldown_hours)
        existing = (
            db.query(AlertRecord)
            .filter(
                AlertRecord.location_id == location_id,
                AlertRecord.severity == severity,
                AlertRecord.status.in_(["active", "acknowledged", "assigned"]),
                AlertRecord.created_at >= cutoff,
            )
            .first()
        )
        return existing is not None

    def update_alert_lifecycle(
        self,
        db: Session,
        alert_id: str,
        new_status: str,
        notes: Optional[str] = None,
        officer: Optional[str] = None,
    ) -> Optional[AlertRecord]:
        alert = db.query(AlertRecord).filter(AlertRecord.id == alert_id).first()
        if not alert:
            return None

        current_status = alert.status or "active"
        now = datetime.now(timezone.utc)

        # Log audit entry in audit_notes
        timestamp_str = now.strftime("%Y-%m-%d %H:%M UTC")
        audit_entry = f"[{timestamp_str}] Status changed from '{current_status}' to '{new_status}'"
        if officer:
            audit_entry += f" by {officer}"
        if notes:
            audit_entry += f" | Notes: {notes}"

        if alert.audit_notes:
            alert.audit_notes = f"{alert.audit_notes}\n{audit_entry}"
        else:
            alert.audit_notes = audit_entry

        alert.status = new_status
        alert.updated_at = now

        if new_status == "acknowledged" and not alert.acknowledged_at:
            alert.acknowledged_at = now
        elif new_status == "resolved" and not alert.resolved_at:
            alert.resolved_at = now

        db.commit()
        db.refresh(alert)
        return alert


alert_workflow_service = AlertWorkflowService()
