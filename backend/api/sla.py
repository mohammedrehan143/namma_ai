from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.entities import SLARule, Complaint
from backend.services.sla_service import sla_service
from backend.schemas.complaint import ComplaintResponse

router = APIRouter(prefix="/api/sla", tags=["SLA & Escalation"])

@router.get("/rules")
def list_sla_rules(db: Session = Depends(get_db)):
    rules = db.query(SLARule).all()
    return [
        {
            "id": r.id,
            "department_id": r.department_id,
            "priority": r.priority,
            "max_resolution_hours": r.max_resolution_hours,
            "warning_threshold_hours": r.warning_threshold_hours
        }
        for r in rules
    ]

@router.post("/check-violations")
def trigger_sla_scan(db: Session = Depends(get_db)):
    """Triggers an SLA violation scan to mark overdue cases and escalate to supervisors."""
    result = sla_service.check_sla_violations(db)
    return result

@router.get("/overdue", response_model=List[ComplaintResponse])
def get_overdue_complaints(db: Session = Depends(get_db)):
    overdue = db.query(Complaint).filter(
        Complaint.status.notin_(["RESOLVED", "CLOSED"]),
        Complaint.is_sla_breached == True
    ).all()
    return [ComplaintResponse.model_validate(c) for c in overdue]
