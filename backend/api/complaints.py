from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.core.database import get_db
from backend.schemas.complaint import ComplaintCreate, ComplaintUpdate, ComplaintResponse, ComplaintDetailResponse
from backend.schemas.evidence import EvidenceResponse
from backend.schemas.resolution import ResolutionResponse
from backend.services.complaint_service import complaint_service
from backend.services.storage import storage_service
from backend.core.security import validate_upload_file

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])

@router.post("", response_model=ComplaintResponse, status_code=201)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    complaint = complaint_service.create_complaint(db, payload)
    return complaint

@router.get("", response_model=dict)
def list_complaints(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    department_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    total, items = complaint_service.list_complaints(
        db, status=status, priority=priority, department_id=department_id, search=search, limit=limit, offset=offset
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [ComplaintResponse.model_validate(c) for c in items]
    }

@router.get("/{complaint_id}", response_model=ComplaintDetailResponse)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = complaint_service.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Map details
    response = ComplaintDetailResponse(
        id=complaint.id,
        status=complaint.status,
        category=complaint.category,
        department_id=complaint.department_id,
        severity=complaint.severity,
        priority=complaint.priority,
        priority_score=complaint.priority_score,
        raw_description=complaint.raw_description,
        ai_summary=complaint.ai_summary,
        location_text=complaint.location_text,
        landmark=complaint.landmark,
        latitude=complaint.latitude,
        longitude=complaint.longitude,
        cluster_id=complaint.cluster_id,
        channel=complaint.channel,
        sla_deadline=complaint.sla_deadline,
        is_sla_breached=complaint.is_sla_breached,
        assigned_officer_id=complaint.assigned_officer_id,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
        citizen_name=complaint.citizen.name if complaint.citizen else None,
        citizen_phone=complaint.citizen.phone if complaint.citizen else None,
        department_name=complaint.department.name if complaint.department else None,
        evidence=[
            {
                "id": ev.id,
                "media_url": ev.media_url,
                "media_type": ev.media_type,
                "evidence_type": ev.evidence_type,
                "ai_confidence": ev.ai_confidence,
                "ai_analysis": ev.ai_analysis,
                "uploaded_at": ev.uploaded_at
            }
            for ev in complaint.evidence
        ],
        events=[
            {
                "id": ev.id,
                "event_type": ev.event_type,
                "old_status": ev.old_status,
                "new_status": ev.new_status,
                "actor_type": ev.actor_type,
                "details": ev.details,
                "created_at": ev.created_at
            }
            for ev in complaint.events
        ]
    )
    return response

@router.post("/{complaint_id}/evidence", response_model=EvidenceResponse, status_code=201)
def upload_evidence(
    complaint_id: str,
    file: UploadFile = File(...),
    evidence_type: str = Form("CITIZEN_INITIAL"),
    db: Session = Depends(get_db)
):
    complaint = complaint_service.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Security: validate file type, extension, and filename safety
    media_type = validate_upload_file(file)

    media_url = storage_service.save_upload_file(file)

    evidence = complaint_service.add_evidence(
        db=db,
        complaint_id=complaint_id,
        media_url=media_url,
        media_type=media_type,
        evidence_type=evidence_type,
        ai_confidence=0.92,
        ai_analysis={"initial_intake": True, "filename": file.filename}
    )
    return evidence

@router.post("/{complaint_id}/assign", response_model=ComplaintResponse)
def assign_or_update_complaint(
    complaint_id: str,
    payload: ComplaintUpdate,
    db: Session = Depends(get_db)
):
    from backend.services.resolution_service import resolution_service
    complaint = resolution_service.update_complaint_assignment(
        db=db,
        complaint_id=complaint_id,
        department_id=payload.department_id,
        assigned_officer_id=payload.assigned_officer_id,
        status=payload.status,
        notes=payload.notes
    )
    return complaint

@router.post("/{complaint_id}/resolve", response_model=ResolutionResponse)
def submit_complaint_resolution(
    complaint_id: str,
    officer_notes: str = Form(...),
    officer_id: Optional[str] = Form(None),
    after_media_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    from backend.services.resolution_service import resolution_service
    resolution = resolution_service.submit_resolution(
        db=db,
        complaint_id=complaint_id,
        officer_notes=officer_notes,
        officer_id=officer_id,
        after_media_file=after_media_file
    )
    return resolution

@router.post("/{complaint_id}/verify")
def citizen_verify_complaint(
    complaint_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    is_fixed = payload.get("is_fixed", True)
    citizen_notes = payload.get("citizen_notes", "")

    complaint = complaint_service.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    from backend.models.entities import ComplaintEvent, Resolution
    res = db.query(Resolution).filter(Resolution.complaint_id == complaint_id).order_by(desc(Resolution.created_at)).first()

    if is_fixed:
        complaint.status = "RESOLVED"
        complaint.resolved_at = datetime.now(timezone.utc)
        if res:
            res.citizen_feedback = "CONFIRMED_FIXED"
        event = ComplaintEvent(
            complaint_id=complaint.id,
            event_type="RESOLVED",
            old_status="CITIZEN_VERIFICATION",
            new_status="RESOLVED",
            actor_type="CITIZEN",
            details="Citizen verified and approved resolution."
        )
        db.add(event)
        db.commit()
        return {"id": complaint.id, "status": "RESOLVED", "message": "Resolution confirmed by citizen."}
    else:
        complaint.status = "REOPENED"
        complaint.reopen_count += 1
        if res:
            res.citizen_feedback = "REJECTED"
            res.citizen_rejection_reason = citizen_notes
        event = ComplaintEvent(
            complaint_id=complaint.id,
            event_type="REOPENED",
            old_status="CITIZEN_VERIFICATION",
            new_status="REOPENED",
            actor_type="CITIZEN",
            details=f"Citizen rejected resolution: {citizen_notes or 'Issue still exists'}. Escalated to supervisor."
        )
        db.add(event)
        db.commit()
        return {"id": complaint.id, "status": "REOPENED", "escalated": True, "message": "Grievance reopened and escalated."}
