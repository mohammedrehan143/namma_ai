import uuid
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal
from backend.models.entities import Complaint, Notification

client = TestClient(app)

def test_voice_inbound_initial_greeting():
    # 1. Test binary WAV audio response for Asterisk Playback
    res_audio = client.get("/api/voice/session/start")
    assert res_audio.status_code == 200
    assert "audio/wav" in res_audio.headers["content-type"]
    assert len(res_audio.content) >= 44  # Valid WAV header

    # 2. Test JSON response for API/monitoring
    res_json = client.get("/api/voice/session/start", headers={"Accept": "application/json"})
    assert res_json.status_code == 200
    data = res_json.json()
    assert data["success"] is True
    assert "Namma A I Civic Grievance Helpline" in data["greeting"]
    assert data["action"] == "RECORD_CALLER"

def test_voice_process_speech_complaint():
    phone = f"+9193{uuid.uuid4().hex[:8]}"
    session_id = f"test-sess-{uuid.uuid4().hex[:6]}"
    
    payload = {
        "session_id": session_id,
        "caller_id": phone,
        "speech_text": "There is a huge dangerous pothole near BMSIT main gate where two-wheelers are almost falling."
    }

    res = client.post("/api/voice/turn", json=payload, headers={"Accept": "application/json"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "Your complaint has been registered" in data["reply_text"]
    assert "road damage" in data["reply_text"].lower()
    assert data["action"] == "HANGUP"
    complaint_id = data["complaint_id"]
    assert complaint_id is not None

    # Verify complaint stored in DB
    db = SessionLocal()
    try:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        assert complaint is not None
        assert complaint.category == "ROAD_DAMAGE"
        assert complaint.priority in ["HIGH", "CRITICAL"]

        # Verify WhatsApp evidence prompt was created
        notif = db.query(Notification).filter(Notification.complaint_id == complaint.id).first()
        assert notif is not None
        assert "Please send photos or videos" in notif.message
    finally:
        db.close()

def test_voice_multi_turn_location_clarification():
    phone = f"+9194{uuid.uuid4().hex[:8]}"
    session_id = f"multi-turn-{uuid.uuid4().hex[:6]}"

    # Turn 1: Problem stated, but landmark omitted
    turn1_res = client.post(
        "/api/voice/turn",
        json={
            "session_id": session_id,
            "caller_id": phone,
            "speech_text": "A street light is completely dark and broken on the road."
        },
        headers={"Accept": "application/json"}
    )
    assert turn1_res.status_code == 200
    turn1_data = turn1_res.json()
    assert turn1_data["state"] == "CLARIFYING_LOCATION"
    assert turn1_data["action"] == "CONTINUE"
    assert "specify the nearest landmark" in turn1_data["reply_text"]
    assert turn1_data["complaint_id"] is None

    # Turn 2: Caller clarifies the landmark
    turn2_res = client.post(
        "/api/voice/turn",
        json={
            "session_id": session_id,
            "caller_id": phone,
            "speech_text": "Opposite Koramangala Police Station on 80 Feet Road."
        },
        headers={"Accept": "application/json"}
    )
    assert turn2_res.status_code == 200
    turn2_data = turn2_res.json()
    assert turn2_data["state"] == "REGISTERED"
    assert turn2_data["action"] == "HANGUP"
    assert "complaint has been registered" in turn2_data["reply_text"]
    assert turn2_data["complaint_id"] is not None

def test_voice_session_teardown():
    session_id = f"teardown-sess-{uuid.uuid4().hex[:6]}"
    res = client.post("/api/voice/session/end", json={"session_id": session_id})
    assert res.status_code == 200
    assert res.json()["status"] == "terminated"
