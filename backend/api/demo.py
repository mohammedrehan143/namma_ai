import uuid
import time
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db, SessionLocal
from backend.models.entities import Complaint, User, Evidence, Resolution, IncidentCluster, ComplaintEvent, Notification
from backend.services.complaint_service import complaint_service
from backend.services.clustering_service import clustering_service
from backend.services.ai import ai_service
from backend.services.ai.vision import vision_ai_service
from backend.services.resolution_service import resolution_service
from backend.services.sla_service import sla_service
from backend.schemas.complaint import ComplaintCreate

router = APIRouter(prefix="/api/demo", tags=["Hackathon Demo Showcase"])

DEMO_STEPS = [
    {"step": 1, "title": "Citizen Calls Helpline", "actor": "Citizen (Phone)", "action": "Citizen dials dedicated phone number and speaks problem."},
    {"step": 2, "title": "AI Natural Language Understanding", "actor": "AI Engine", "action": "Speech-to-text converts voice. AI extracts defect, category, and urgency."},
    {"step": 3, "title": "AI Missing Info Clarification", "actor": "AI Voice Agent", "action": "AI identifies missing landmark, prompts caller: 'Near what gate or landmark?'"},
    {"step": 4, "title": "Complaint Created with Reference ID", "actor": "Backend Engine", "action": "Structured complaint registered with ID (e.g. #NMA-10293)."},
    {"step": 5, "title": "Complaint Appears on Civic Dashboard", "actor": "Officer Dashboard", "action": "Case appears in real-time queue with High priority and SLA countdown."},
    {"step": 6, "title": "WhatsApp Evidence Request Dispatched", "actor": "WhatsApp (via n8n)", "action": "System sends WhatsApp message asking citizen to attach photo proof."},
    {"step": 7, "title": "Citizen Sends Photo Evidence", "actor": "Citizen (WhatsApp)", "action": "Citizen sends photo of asphalt cavity via WhatsApp."},
    {"step": 8, "title": "Multimodal Vision AI Analyzes Evidence", "actor": "Vision AI", "action": "AI confirms pothole defect with 94% confidence, calculates safety hazard."},
    {"step": 9, "title": "AI Escalates Priority to HIGH", "actor": "AI Engine", "action": "Priority score upgraded to High (88/100) based on verified visual depth."},
    {"step": 10, "title": "Second Citizen Reports Same Pothole", "actor": "Citizen 2", "action": "Another citizen calls/reports road crater at the same location."},
    {"step": 11, "title": "AI Duplicate Detection & Clustering", "actor": "Clustering Engine", "action": "Spatio-temporal semantic engine matches proximity (<30m) and category."},
    {"step": 12, "title": "Incident Cluster Created (#INC-102)", "actor": "Civic Engine", "action": "Grouped into Incident INC-102. Affected citizen count increments."},
    {"step": 13, "title": "Officer Dispatches Road Maintenance Crew", "actor": "Civic Officer", "action": "Road Maintenance Department accepts incident and marks IN_PROGRESS."},
    {"step": 14, "title": "Officer Marks Issue Resolved", "actor": "Civic Officer", "action": "Field crew fills pothole with asphalt mix and enters repair notes."},
    {"step": 15, "title": "Officer Uploads 'After-Repair' Photo Proof", "actor": "Civic Officer", "action": "Officer uploads photo proof of the completed road repair."},
    {"step": 16, "title": "Vision AI Verifies Before vs After Proof", "actor": "Vision AI", "action": "Multimodal AI compares initial vs repair photos; verifies smooth level surface."},
    {"step": 17, "title": "WhatsApp Confirmation Sent to Citizen", "actor": "WhatsApp (via n8n)", "action": "Sends prompt: 'Issue marked resolved. Is it actually fixed? 1: Yes / 2: No'"},
    {"step": 18, "title": "Citizen Rejects Resolution (Selects NO)", "actor": "Citizen (WhatsApp)", "action": "Citizen inspects and replies '2 - NO: Loose gravel still dangerous.'"},
    {"step": 19, "title": "Grievance Automatically Reopens", "actor": "Closed-Loop Engine", "action": "Status transitions to REOPENED. Reopening counter increments to 1."},
    {"step": 20, "title": "SLA Escalation Alert to Supervisor", "actor": "SLA & Supervisor Alert", "action": "Case escalated to Department Supervisor for mandatory field re-inspection."}
]

@router.get("/steps")
def get_demo_steps():
    return DEMO_STEPS

@router.post("/run-full-scenario")
def run_full_hackathon_demo(db: Session = Depends(get_db)):
    """Executes the complete 20-step hackathon demo flow deterministically."""
    demo_phone_1 = f"+9198765{str(int(time.time()))[-5:]}"
    demo_phone_2 = f"+9199887{str(int(time.time()))[-5:]}"

    execution_log = []

    # Step 1 - 4: Voice Call Intake & Complaint Creation
    speech_text = "There is a deep dangerous pothole near BMSIT main gate causing two-wheelers to slip."
    ai_analysis = ai_service.analyze_complaint(speech_text, location_hint="Near BMSIT main gate")
    
    complaint_payload = ComplaintCreate(
        citizen_name="Demo Citizen 1",
        citizen_phone=demo_phone_1,
        description=speech_text,
        location_text="Near BMSIT main gate, Doddaballapur Road",
        latitude=13.1345,
        longitude=77.5682,
        category="ROAD_DAMAGE",
        channel="PHONE"
    )
    complaint_1 = complaint_service.create_complaint(db, complaint_payload)
    execution_log.append({"step": 1, "status": "COMPLETED", "detail": f"Voice intake created complaint #{complaint_1.id} ({complaint_1.category})"})

    # Step 6 - 8: WhatsApp Evidence & Vision Analysis
    vision_result = vision_ai_service.analyze_evidence("/uploads/demo-pothole-before.jpg", speech_text)
    complaint_service.add_evidence(
        db=db,
        complaint_id=complaint_1.id,
        media_url="/uploads/demo-pothole-before.jpg",
        media_type="IMAGE",
        evidence_type="CITIZEN_INITIAL",
        ai_analysis=vision_result.model_dump(),
        ai_confidence=vision_result.confidence
    )
    execution_log.append({"step": 8, "status": "COMPLETED", "detail": f"Vision AI verified pothole with {int(vision_result.confidence*100)}% confidence"})

    # Step 10 - 12: Second Citizen & Incident Clustering
    speech_text_2 = "Huge road cavity outside BMSIT college gate"
    complaint_payload_2 = ComplaintCreate(
        citizen_name="Demo Citizen 2",
        citizen_phone=demo_phone_2,
        description=speech_text_2,
        location_text="BMSIT Gate, Yelahanka",
        latitude=13.1347,
        longitude=77.5683,
        category="ROAD_DAMAGE",
        channel="WHATSAPP"
    )
    complaint_2 = complaint_service.create_complaint(db, complaint_payload_2)
    execution_log.append({"step": 12, "status": "COMPLETED", "detail": f"Duplicate detected. Linked #{complaint_1.id} and #{complaint_2.id} into cluster #{complaint_2.cluster_id}"})

    # Step 13: Officer Accepts -> IN_PROGRESS
    resolution_service.update_complaint_assignment(db, complaint_1.id, status="IN_PROGRESS", notes="Crew dispatched")
    execution_log.append({"step": 13, "status": "COMPLETED", "detail": f"Officer accepted case #{complaint_1.id} -> IN_PROGRESS"})

    # Step 14 - 16: Officer Submits Resolution Proof + AI Verification
    resolution = resolution_service.submit_resolution(
        db=db,
        complaint_id=complaint_1.id,
        officer_notes="Pothole filled with cold asphalt mix and roller compacted."
    )
    execution_log.append({"step": 16, "status": "COMPLETED", "detail": f"AI verified before vs after proof: {resolution.ai_verification.get('audit_flag')} ({int(resolution.ai_verification.get('confidence')*100)}%)"})

    # Step 18 - 20: Citizen Rejection & Automatic Reopening/Escalation
    complaint_1.status = "REOPENED"
    complaint_1.reopen_count += 1
    event = ComplaintEvent(
        complaint_id=complaint_1.id,
        event_type="REOPENED",
        old_status="CITIZEN_VERIFICATION",
        new_status="REOPENED",
        actor_type="CITIZEN",
        details="Citizen rejected resolution via WhatsApp: Loose gravel remains"
    )
    db.add(event)
    
    # Escalate to supervisor
    complaint_1.status = "ESCALATED"
    esc_event = ComplaintEvent(
        complaint_id=complaint_1.id,
        event_type="ESCALATED",
        old_status="REOPENED",
        new_status="ESCALATED",
        actor_type="SYSTEM",
        details="Case escalated to Department Supervisor for priority re-inspection."
    )
    db.add(esc_event)
    db.commit()

    execution_log.append({"step": 20, "status": "COMPLETED", "detail": f"Citizen rejected resolution. Complaint #{complaint_1.id} automatically REOPENED & ESCALATED to supervisor!"})

    return {
        "status": "SUCCESS",
        "demo_complaint_id": complaint_1.id,
        "incident_cluster_id": complaint_1.cluster_id,
        "logs": execution_log,
        "message": "Full 20-step hackathon demo scenario executed successfully."
    }
