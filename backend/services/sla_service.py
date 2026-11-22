from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.entities import Complaint, SLARule, ComplaintEvent, User, Notification
from backend.core.config import settings
from backend.core.logging import logger

class SLAService:
    def get_sla_hours(self, db: Session, department_id: str, priority: str) -> int:
        """Looks up configured SLA resolution hours from database or fallback configuration."""
        rule = db.query(SLARule).filter(
            SLARule.department_id == department_id,
            SLARule.priority == priority
        ).first()
        if rule:
            return rule.max_resolution_hours

        # Fallback to configured settings
        priority_upper = priority.upper()
        if priority_upper == "CRITICAL":
            return settings.SLA_HOURS_CRITICAL
        elif priority_upper == "HIGH":
            return settings.SLA_HOURS_HIGH
        elif priority_upper == "MEDIUM":
            return settings.SLA_HOURS_MEDIUM
        else:
            return settings.SLA_HOURS_LOW

    def check_sla_violations(self, db: Session) -> Dict[str, Any]:
        """Scans all active complaints for SLA warnings, overdue breaches, and supervisor escalations."""
        now = datetime.now(timezone.utc)
        active_complaints = db.query(Complaint).filter(
            Complaint.status.notin_(["RESOLVED", "CLOSED", "CITIZEN_VERIFICATION"])
        ).all()

        breached_count = 0
        warning_count = 0
        escalated_count = 0

        for c in active_complaints:
            if not c.sla_deadline:
                continue

            # Ensure aware datetime
            deadline = c.sla_deadline
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)

            remaining_seconds = (deadline - now).total_seconds()
            remaining_hours = remaining_seconds / 3600.0

            # 1. Breach Check
            if remaining_seconds <= 0:
                breached_count += 1
                if not c.is_sla_breached:
                    c.is_sla_breached = True
                    old_status = c.status
                    c.status = "ESCALATED"
                    escalated_count += 1

                    # Log breach and escalation event
                    event = ComplaintEvent(
                        complaint_id=c.id,
                        event_type="SLA_BREACHED",
                        old_status=old_status,
                        new_status="ESCALATED",
                        actor_type="SYSTEM",
                        details=f"SLA deadline expired on {deadline.isoformat()}. Case escalated to Department Supervisor."
                    )
                    db.add(event)

                    # Alert supervisor via Notification
                    supervisor = db.query(User).filter(
                        User.role == "SUPERVISOR",
                        User.department_id == c.department_id
                    ).first()
                    phone = supervisor.phone if supervisor else "+919876543211"

                    notif = Notification(
                        complaint_id=c.id,
                        recipient_phone=phone,
                        channel="WHATSAPP",
                        message=f"🚨 *SLA BREACH ALERT*: Case #{c.id} ({c.category}) is overdue! Target was {deadline.strftime('%d-%b %H:%M')}. Escalated for supervisory intervention."
                    )
                    db.add(notif)
                    logger.warning(f"SLA breached for complaint {c.id}. Escalated to supervisor.")

            # 2. Warning Check (e.g. < 4 hours remaining and not already breached)
            elif remaining_hours <= 4.0:
                warning_count += 1
                existing_warning = db.query(ComplaintEvent).filter(
                    ComplaintEvent.complaint_id == c.id,
                    ComplaintEvent.event_type == "SLA_WARNING"
                ).first()

                if not existing_warning:
                    event = ComplaintEvent(
                        complaint_id=c.id,
                        event_type="SLA_WARNING",
                        old_status=c.status,
                        new_status=c.status,
                        actor_type="SYSTEM",
                        details=f"SLA Warning: Only {remaining_hours:.1f} hours remaining before breach."
                    )
                    db.add(event)

        db.commit()
        return {
            "scanned_count": len(active_complaints),
            "breached_count": breached_count,
            "warning_count": warning_count,
            "escalated_count": escalated_count,
            "checked_at": now.isoformat()
        }

sla_service = SLAService()
