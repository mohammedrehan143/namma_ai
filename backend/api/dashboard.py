from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.core.database import get_db
from backend.models.entities import Complaint, IncidentCluster
from backend.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard & Analytics"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    total = db.query(Complaint).count()
    open_count = db.query(Complaint).filter(
        Complaint.status.in_(["REPORTED", "AI_PROCESSING", "ASSIGNED", "RESOLUTION_SUBMITTED", "CITIZEN_VERIFICATION"])
    ).count()
    in_progress = db.query(Complaint).filter(Complaint.status == "IN_PROGRESS").count()
    resolved = db.query(Complaint).filter(Complaint.status == "RESOLVED").count()
    reopened = db.query(Complaint).filter(Complaint.status.in_(["REOPENED", "ESCALATED"])).count()

    critical = db.query(Complaint).filter(Complaint.priority == "CRITICAL").count()
    high = db.query(Complaint).filter(Complaint.priority == "HIGH").count()
    medium = db.query(Complaint).filter(Complaint.priority == "MEDIUM").count()
    low = db.query(Complaint).filter(Complaint.priority == "LOW").count()

    sla_breached = db.query(Complaint).filter(
        Complaint.status.notin_(["RESOLVED", "CLOSED"]),
        (Complaint.is_sla_breached == True) | (Complaint.sla_deadline < now)
    ).count()

    return DashboardStats(
        total=total,
        open=open_count,
        in_progress=in_progress,
        resolved=resolved,
        reopened=reopened,
        critical=critical,
        high=high,
        medium=medium,
        low=low,
        sla_breached=sla_breached
    )
