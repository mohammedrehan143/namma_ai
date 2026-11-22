import re
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.core.database import get_db
from backend.models.entities import Complaint, User, Evidence, ComplaintEvent
from backend.services.complaint_service import complaint_service
from backend.services.ai import ai_service
from backend.core.logging import logger

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])

def messaging_xml_response(text: str) -> Response:
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{text}</Message>
</Response>"""
    return Response(content=xml_content, media_type="application/xml")

@router.post("/webhook")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "").lower()
    is_json = "application/json" in content_type
    media_items = []

    if is_json:
        payload = await request.json()
        from_number = str(payload.get("phone") or payload.get("from") or payload.get("From") or "")
        body = str(payload.get("message") or payload.get("body") or payload.get("Body") or "").strip()
        raw_media = payload.get("media_url") or payload.get("media_urls") or payload.get("mediaUrl") or payload.get("MediaUrl0")
        if isinstance(raw_media, list):
            for m in raw_media:
                media_items.append((m, "image/jpeg"))
        elif raw_media:
            m_type = payload.get("media_type") or payload.get("MediaContentType0") or "image/jpeg"
            media_items.append((str(raw_media), m_type))
    else:
        form_data = await request.form()
        from_number = form_data.get("From", "")
        body = (form_data.get("Body", "") or "").strip()
        num_media = int(form_data.get("NumMedia", 0) or 0)
        for i in range(num_media):
            media_url = form_data.get(f"MediaUrl{i}")
            media_type_header = form_data.get(f"MediaContentType{i}", "image/jpeg")
            if media_url:
                media_items.append((media_url, media_type_header))

    clean_phone = from_number.replace("whatsapp:", "").strip()
    logger.info(f"Received WhatsApp webhook from {clean_phone}: '{body}' with {len(media_items)} media items")

    def make_reply(reply_text: str, current_complaint=None):
        if is_json:
            return {
                "success": True,
                "reply": reply_text,
                "complaint_id": current_complaint.id if current_complaint else None,
                "status": current_complaint.status if current_complaint else None
            }
        return messaging_xml_response(reply_text)

    # 1. Identify citizen
    citizen = db.query(User).filter(User.phone == clean_phone).first()

    # Check if message mentions a specific complaint ID like NMA-10001
    complaint_match = re.search(r"NMA-\d+", body, re.IGNORECASE)
    complaint = None
    if complaint_match:
        matched_id = complaint_match.group(0).upper()
        complaint = db.query(Complaint).filter(Complaint.id == matched_id).first()

    # Otherwise fetch latest active complaint for this user
    if not complaint and citizen:
        complaint = db.query(Complaint).filter(
            Complaint.citizen_id == citizen.id
        ).order_by(desc(Complaint.created_at)).first()

    # If no complaint exists at all
    if not complaint:
        reply = (
            "Welcome to Namma AI! No active complaint was found for this number.\n"
            "You can register a new grievance by describing the problem here or on our website at http://localhost:3000/report"
        )
        return make_reply(reply, None)

    # 2. Check if this is a Citizen Verification response (Phase 12 preview/integration)
    if body in ["1", "YES", "yes", "Fixed", "fixed", "y", "Y"]:
        if complaint.status in ["RESOLUTION_SUBMITTED", "AI_VERIFICATION", "CITIZEN_VERIFICATION"]:
            old_status = complaint.status  # capture before mutation
            complaint.status = "RESOLVED"
            complaint.resolved_at = complaint.updated_at
            event = ComplaintEvent(
                complaint_id=complaint.id,
                event_type="RESOLVED",
                old_status=old_status,
                new_status="RESOLVED",
                actor_type="CITIZEN",
                details="Citizen verified and confirmed resolution via WhatsApp"
            )
            db.add(event)
            db.commit()
            return make_reply(f"✅ Thank you! Complaint #{complaint.id} has been marked as officially RESOLVED. Thank you for making our city better!", complaint)

    elif body in ["2", "NO", "no", "Not fixed", "still exists", "still there"]:
        if complaint.status in ["RESOLUTION_SUBMITTED", "AI_VERIFICATION", "CITIZEN_VERIFICATION"]:
            complaint.status = "REOPENED"
            complaint.reopen_count += 1
            event = ComplaintEvent(
                complaint_id=complaint.id,
                event_type="REOPENED",
                old_status="CITIZEN_VERIFICATION",
                new_status="REOPENED",
                actor_type="CITIZEN",
                details="Citizen rejected resolution via WhatsApp: Issue still exists"
            )
            db.add(event)
            db.commit()
            return make_reply(f"⚠️ We apologize! Complaint #{complaint.id} has been REOPENED and escalated to the department supervisor for immediate inspection.", complaint)

    # 3. Handle media uploads
    if len(media_items) > 0:
        added_count = 0
        for media_url, media_type_header in media_items:
            media_type = "VIDEO" if "video" in media_type_header else "IMAGE"

            # Run Vision AI analysis on incoming evidence
            vision_analysis = ai_service.analyze_evidence(
                image_path_or_bytes=media_url or "whatsapp_media",
                description=complaint.raw_description
            )

            complaint_service.add_evidence(
                db=db,
                complaint_id=complaint.id,
                media_url=media_url or "/uploads/wa-media.jpg",
                media_type=media_type,
                evidence_type="CITIZEN_FOLLOWUP",
                ai_analysis=vision_analysis.model_dump(),
                ai_confidence=vision_analysis.confidence
            )
            added_count += 1

        reply = (
            f"📸 Received {added_count} evidence file(s) for complaint #{complaint.id}!\n\n"
            f"🔍 *AI Inspection:* Issue verified ({vision_analysis.issue_type}, {int(vision_analysis.confidence * 100)}% confidence).\n"
            f"Your case is active with the {complaint.department_id} department."
        )
        return make_reply(reply, complaint)

    # 4. Standard text acknowledgment
    reply = (
        f"Grievance #{complaint.id} is currently *{complaint.status}*.\n"
        f"Department: {complaint.department_id}\n\n"
        f"You can attach photos or videos by sending them directly to this chat."
    )
    return make_reply(reply, complaint)
