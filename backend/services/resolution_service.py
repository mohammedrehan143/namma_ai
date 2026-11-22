from datetime import datetime, timezone
from typing import Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from backend.models.entities import Complaint, Resolution, ComplaintEvent
from backend.services.storage import storage_service
from backend.services.ai import ai_service
from backend.services.whatsapp_dispatcher import whatsapp_dispatcher
from backend.core.logging import logger

class ResolutionService:
    def update_complaint_assignment(
        self,
        db: Session,
        complaint_id: str,
        department_id: Optional[str] = None,
        assigned_officer_id: Optional[str] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Complaint:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")

        old_status = complaint.status
        if department_id:
            complaint.department_id = department_id
        if assigned_officer_id:
            complaint.assigned_officer_id = assigned_officer_id
        if status:
            complaint.status = status

        event = ComplaintEvent(
            complaint_id=complaint.id,
            event_type="ASSIGNED" if status == "ASSIGNED" else "STATUS_UPDATED",
            old_status=old_status,
            new_status=complaint.status,
            actor_type="OFFICER",
            details=notes or f"Updated assignment: Dept={complaint.department_id}, Status={complaint.status}"
        )
        db.add(event)
        db.commit()
        db.refresh(complaint)
        logger.info(f"Updated complaint {complaint.id}: Status={complaint.status}, Dept={complaint.department_id}")
        return complaint

    def submit_resolution(
        self,
        db: Session,
        complaint_id: str,
        officer_notes: str,
        officer_id: Optional[str] = None,
        after_media_file: Optional[UploadFile] = None
    ) -> Resolution:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")

        # 1. Save after repair media
        after_media_url = None
        if after_media_file:
            after_media_url = storage_service.save_upload_file(after_media_file)

        # 2. Find original before photo for comparison (None if no evidence uploaded)
        before_image = None
        if complaint.evidence and len(complaint.evidence) > 0:
            before_image = complaint.evidence[0].media_url

        # 3. AI Resolution Verification (Phase 11 integration)
        ai_verification = ai_service.verify_resolution(
            before_image=before_image or after_media_url or "",
            after_image=after_media_url or before_image or "",
            description=complaint.raw_description
        )

        now = datetime.now(timezone.utc)
        resolution = Resolution(
            complaint_id=complaint.id,
            officer_id=officer_id or complaint.assigned_officer_id,
            officer_notes=officer_notes,
            after_media_url=after_media_url,
            ai_verification=ai_verification.model_dump(),
            ai_verified=ai_verification.resolution_likely_complete,
            citizen_feedback="PENDING",
            created_at=now
        )
        db.add(resolution)

        # Transition status to CITIZEN_VERIFICATION
        old_status = complaint.status
        complaint.status = "CITIZEN_VERIFICATION"
        complaint.updated_at = now

        event = ComplaintEvent(
            complaint_id=complaint.id,
            event_type="RESOLUTION_SUBMITTED",
            old_status=old_status,
            new_status="CITIZEN_VERIFICATION",
            actor_type="OFFICER",
            details=f"Officer submitted repair resolution with photo proof. AI Verification: {ai_verification.audit_flag} ({int(ai_verification.confidence*100)}% confidence)."
        )
        db.add(event)
        db.commit()
        db.refresh(resolution)

        # 4. Dispatch WhatsApp verification prompt to citizen (Phase 12 integration)
        try:
            whatsapp_dispatcher.send_verification_request(
                to_phone=complaint.citizen.phone,
                complaint_id=complaint.id,
                db=db
            )
        except Exception as e:
            logger.warning(f"Failed to dispatch citizen verification prompt: {e}")

        logger.info(f"Resolution submitted for {complaint.id}. Verification score: {ai_verification.confidence:.2f}")
        return resolution

resolution_service = ResolutionService()
