import io
import uuid
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal
from backend.models.entities import Complaint, Evidence
from backend.services.ai.gemini_service import GeminiAIService

client = TestClient(app)

def test_degradation_when_external_llm_fails():
    """If external LLM throws an exception, complaint must still be safely stored and categorized by fallback."""
    phone = f"+9188{uuid.uuid4().hex[:8]}"
    
    with patch("backend.services.ai.gemini_service.GeminiAIService.analyze_complaint", side_effect=RuntimeError("Simulated LLM API 503 Outage")):
        res = client.post(
            "/api/complaints",
            json={
                "citizen_name": "Resilient Citizen",
                "citizen_phone": phone,
                "description": "Deep asphalt pothole near BMSIT gate during network glitch",
                "location_text": "BMSIT Gate",
                "channel": "WEB"
            }
        )
        assert res.status_code == 201
        data = res.json()
        assert data["id"].startswith("NMA-")
        assert data["status"] == "REPORTED"
        assert data["category"] == "ROAD_DAMAGE"

def test_degradation_when_notification_dispatcher_is_unavailable():
    """If WhatsApp/n8n dispatch fails, complaint creation and status updates must never crash."""
    phone = f"+9187{uuid.uuid4().hex[:8]}"

    with patch("backend.services.whatsapp_dispatcher.WhatsAppDispatcher.send_whatsapp_message", side_effect=Exception("Dispatch Connection Timeout")):
        res = client.post(
            "/api/complaints",
            json={
                "citizen_name": "Telecom Test",
                "citizen_phone": phone,
                "description": "Garbage pile in Indiranagar",
                "location_text": "Indiranagar",
                "channel": "WEB"
            }
        )
        # HTTP call must still succeed with 201
        assert res.status_code == 201
        assert res.json()["status"] == "REPORTED"

def test_degradation_when_vision_ai_encounters_error():
    """If vision AI encounters an issue, evidence is preserved and marked for human review."""
    phone = f"+9186{uuid.uuid4().hex[:8]}"
    reg = client.post(
        "/api/complaints",
        json={
            "citizen_name": "Vision Test",
            "citizen_phone": phone,
            "description": "Streetlight flickering",
            "channel": "WEB"
        }
    )
    cid = reg.json()["id"]

    # Upload corrupt evidence file
    res = client.post(
        f"/api/complaints/{cid}/evidence",
        files={"file": ("glitch.jpg", io.BytesIO(b"garbage-bytes"), "image/jpeg")},
        data={"evidence_type": "CITIZEN_INITIAL"}
    )
    assert res.status_code == 201
    ev_data = res.json()
    assert ev_data["complaint_id"] == cid
    assert ev_data["is_valid_evidence"] is True  # preserved for human inspection

def test_degradation_with_missing_location():
    """When citizen provides zero location, system defaults to city center and marks missing_info."""
    phone = f"+9185{uuid.uuid4().hex[:8]}"
    res = client.post(
        "/api/complaints",
        json={
            "citizen_name": "No Location User",
            "citizen_phone": phone,
            "description": "Pothole somewhere on the street",
            "location_text": "",
            "channel": "WEB"
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert data["latitude"] is not None
    assert data["longitude"] is not None
    assert data["status"] == "REPORTED"
