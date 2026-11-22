import uuid
import xml.etree.ElementTree as ET
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal
from backend.models.entities import Complaint, ComplaintEvent, Resolution, IncidentCluster
from backend.services.complaint_service import generate_complaint_id
from backend.services.sla_service import sla_service
from backend.api.auth import AuthResponse

client = TestClient(app)

def test_whatsapp_old_status_audit_event_accurately_recorded():
    """Verify that when a citizen approves resolution via WhatsApp, the old_status is captured BEFORE mutation to RESOLVED."""
    phone = f"+9198{uuid.uuid4().hex[:8]}"
    reg = client.post("/api/complaints", json={
        "citizen_name": "Audit Test",
        "citizen_phone": phone,
        "description": "Pothole for audit trail verification",
        "location_text": "BMSIT Gate",
        "channel": "WEB"
    })
    assert reg.status_code == 201
    cid = reg.json()["id"]

    # Transition to CITIZEN_VERIFICATION
    client.post(f"/api/complaints/{cid}/assign", json={
        "status": "CITIZEN_VERIFICATION",
        "notes": "Crew finished work"
    })

    # Citizen confirms resolution via WhatsApp
    wa_res = client.post("/api/whatsapp/webhook", data={
        "From": f"whatsapp:{phone}",
        "Body": "y",
        "NumMedia": "0"
    })
    assert wa_res.status_code == 200
    assert "RESOLVED" in wa_res.text

    db = SessionLocal()
    try:
        resolved_event = db.query(ComplaintEvent).filter(
            ComplaintEvent.complaint_id == cid,
            ComplaintEvent.event_type == "RESOLVED"
        ).first()
        assert resolved_event is not None
        assert resolved_event.old_status == "CITIZEN_VERIFICATION", f"Expected CITIZEN_VERIFICATION, got {resolved_event.old_status}"
        assert resolved_event.new_status == "RESOLVED"
    finally:
        db.close()

def test_voice_special_characters_handled_safely():
    """Verify that dynamic content from speech transcription containing special characters is safely processed."""
    res = client.post("/api/voice/turn", json={
        "caller_id": "+919876543299",
        "session_id": "special-char-sess",
        "speech_text": "Dangerous wires & broken poles near shop <alert> and \"hazard\""
    }, headers={"Accept": "application/json"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["reply_text"]) > 0

def test_dashboard_open_count_includes_active_statuses():
    """Verify open queue count in dashboard includes cases in RESOLUTION_SUBMITTED and CITIZEN_VERIFICATION."""
    phone = f"+9198{uuid.uuid4().hex[:8]}"
    reg = client.post("/api/complaints", json={
        "citizen_name": "Queue Test",
        "citizen_phone": phone,
        "description": "Drainage overflowing on road",
        "channel": "WEB"
    })
    cid = reg.json()["id"]

    # Mark as CITIZEN_VERIFICATION
    client.post(f"/api/complaints/{cid}/assign", json={
        "status": "CITIZEN_VERIFICATION",
        "notes": "Pending confirmation"
    })

    stats = client.get("/api/dashboard/stats").json()
    assert stats["open"] >= 1, "CITIZEN_VERIFICATION complaints must count towards open queue"

def test_sla_scanner_skips_citizen_verification():
    """Verify that complaints awaiting citizen verification are not escalated by the SLA scanner."""
    phone = f"+9198{uuid.uuid4().hex[:8]}"
    reg = client.post("/api/complaints", json={
        "citizen_name": "SLA Exclude Test",
        "citizen_phone": phone,
        "description": "Water pipe leak near park",
        "channel": "WEB"
    })
    cid = reg.json()["id"]

    # Assign to CITIZEN_VERIFICATION
    client.post(f"/api/complaints/{cid}/assign", json={
        "status": "CITIZEN_VERIFICATION",
        "notes": "Work done, awaiting citizen"
    })

    db = SessionLocal()
    try:
        # Run SLA scanner
        scan_result = sla_service.check_sla_violations(db)
        # The complaint should still be in CITIZEN_VERIFICATION, not escalated to ESCALATED
        c = db.query(Complaint).filter(Complaint.id == cid).first()
        assert c.status == "CITIZEN_VERIFICATION"
    finally:
        db.close()

def test_complaint_id_collision_prevention():
    """Verify generate_complaint_id skips existing IDs and avoids primary key collisions."""
    db = SessionLocal()
    try:
        id1 = generate_complaint_id(db)
        # Create a complaint with id1
        c = Complaint(
            id=id1,
            citizen_id="usr-test",
            category="ROAD_DAMAGE",
            department_id="ROADS",
            severity="LOW",
            priority="LOW",
            priority_score=30,
            raw_description="Collision test"
        )
        db.add(c)
        db.commit()

        # Generating again must produce a different ID even before count query would refresh
        id2 = generate_complaint_id(db)
        assert id1 != id2
        assert not db.query(Complaint).filter(Complaint.id == id2).first()
    finally:
        db.close()

def test_resolution_missing_before_image_graceful():
    """Verify resolution submit succeeds when complaint has no citizen before photo."""
    phone = f"+9198{uuid.uuid4().hex[:8]}"
    reg = client.post("/api/complaints", json={
        "citizen_name": "No Photo Citizen",
        "citizen_phone": phone,
        "description": "Streetlight not working on main junction",
        "channel": "WEB"
    })
    cid = reg.json()["id"]

    # Resolve without any before evidence uploaded
    res = client.post(f"/api/complaints/{cid}/resolve", data={
        "officer_notes": "Replaced sodium lamp with new LED fixture."
    })
    assert res.status_code == 200
    data = res.json()
    assert data["complaint_id"] == cid
    assert data["ai_verified"] is True
