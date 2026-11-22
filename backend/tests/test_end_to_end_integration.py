import io
import uuid
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal
from backend.models.entities import Complaint, IncidentCluster, Evidence, Resolution, Notification

client = TestClient(app)

def test_complete_end_to_end_civic_lifecycle():
    phone1 = f"+9198{uuid.uuid4().hex[:8]}"
    phone2 = f"+9199{uuid.uuid4().hex[:8]}"

    # Step 1: Voice / Speech Complaint Registration via Asterisk Telephony Engine
    voice_payload = {
        "session_id": f"e2e-sess-{uuid.uuid4().hex[:6]}",
        "caller_id": phone1,
        "speech_text": "There is a massive dangerous road cave-in and pothole near BMSIT main gate where bikes are skidding."
    }
    voice_res = client.post("/api/voice/turn", json=voice_payload, headers={"Accept": "application/json"})
    assert voice_res.status_code == 200
    assert "Your complaint has been registered" in voice_res.json()["reply_text"]

    # Retrieve registered complaint
    db = SessionLocal()
    try:
        complaint = db.query(Complaint).filter(Complaint.citizen.has(phone=phone1)).order_by(Complaint.created_at.desc()).first()
        assert complaint is not None
        c1_id = complaint.id
        assert complaint.category == "ROAD_DAMAGE"
        assert complaint.department_id == "ROADS"
        assert complaint.priority in ["HIGH", "CRITICAL"]
        assert complaint.latitude is not None
        assert complaint.longitude is not None
    finally:
        db.close()

    # Step 2: Citizen uploads initial photo evidence via WhatsApp webhook
    fake_photo_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdbpothole_evidence"
    wa_payload = {
        "From": f"whatsapp:{phone1}",
        "Body": f"Photo proof for #{c1_id}",
        "NumMedia": "1",
        "MediaUrl0": "/uploads/test-e2e-pothole.jpg",
        "MediaContentType0": "image/jpeg"
    }
    wa_res = client.post("/api/whatsapp/webhook", data=wa_payload)
    assert wa_res.status_code == 200
    assert "AI Inspection" in wa_res.text

    # Step 3: Duplicate Citizen Report at same location -> Incident Clustering
    web_res2 = client.post(
        "/api/complaints",
        json={
            "citizen_name": "Second Witness",
            "citizen_phone": phone2,
            "description": "Hazardous road crater outside BMSIT college gate causing accidents",
            "location_text": "BMSIT Gate, Yelahanka",
            "latitude": complaint.latitude + 0.0001,
            "longitude": complaint.longitude + 0.0001,
            "category": "ROAD_DAMAGE",
            "channel": "WEB"
        }
    )
    assert web_res2.status_code == 201
    c2 = web_res2.json()
    assert c2["cluster_id"] is not None
    cluster_id = c2["cluster_id"]

    # Step 4: Officer Dashboard verification
    dashboard_res = client.get("/api/dashboard/stats")
    assert dashboard_res.status_code == 200
    stats = dashboard_res.json()
    assert stats["total"] >= 2

    # Step 5: Officer Accepts and Updates Status to IN_PROGRESS
    assign_res = client.post(
        f"/api/complaints/{c1_id}/assign",
        json={
            "status": "IN_PROGRESS",
            "department_id": "ROADS",
            "notes": "Ward 12 road maintenance crew dispatched."
        }
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["status"] == "IN_PROGRESS"

    # Step 6: Officer Completes Repair and Submits Resolution with After Photo
    fake_after_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdbafter_repair"
    resolve_res = client.post(
        f"/api/complaints/{c1_id}/resolve",
        data={"officer_notes": "Filled with bituminous asphalt and roller compacted."},
        files={"after_media_file": ("after.jpg", io.BytesIO(fake_after_bytes), "image/jpeg")}
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["ai_verified"] is True

    # Complaint is now in CITIZEN_VERIFICATION
    detail_res = client.get(f"/api/complaints/{c1_id}")
    assert detail_res.json()["status"] == "CITIZEN_VERIFICATION"

    # Step 7: Citizen rejects resolution via WhatsApp ("2")
    reject_wa = {
        "From": f"whatsapp:{phone1}",
        "Body": "2",
        "NumMedia": "0"
    }
    reject_res = client.post("/api/whatsapp/webhook", data=reject_wa)
    assert reject_res.status_code == 200
    assert "REOPENED and escalated" in reject_res.text

    # Verify status is REOPENED
    reopened_detail = client.get(f"/api/complaints/{c1_id}").json()
    assert reopened_detail["status"] == "REOPENED"

    # Step 8: Officer fixes completely and Citizen approves ("1")
    approve_wa = {
        "From": f"whatsapp:{phone1}",
        "Body": "1",
        "NumMedia": "0"
    }
    # Reset status to verification for second resolution round
    client.post(
        f"/api/complaints/{c1_id}/assign",
        json={"status": "CITIZEN_VERIFICATION", "notes": "Re-inspection complete"}
    )
    approve_res = client.post("/api/whatsapp/webhook", data=approve_wa)
    assert approve_res.status_code == 200
    assert "RESOLVED" in approve_res.text

    # Step 9: Final status is RESOLVED
    final_detail = client.get(f"/api/complaints/{c1_id}").json()
    assert final_detail["status"] == "RESOLVED"
