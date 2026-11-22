import io
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.ai.vision import vision_ai_service

client = TestClient(app)

def test_evidence_vision_service_pothole():
    analysis = vision_ai_service.analyze_evidence(
        media_path="/uploads/test-pothole.jpg",
        complaint_description="Large asphalt pothole causing traffic jam"
    )

    assert analysis.issue_detected is True
    assert analysis.issue_type == "POTHOLE"
    assert analysis.confidence >= 0.85
    assert analysis.severity in ["HIGH", "CRITICAL"]
    assert "pothole" in analysis.visual_description.lower() or "crater" in analysis.visual_description.lower()
    assert analysis.requires_human_review is False

def test_evidence_vision_service_garbage():
    analysis = vision_ai_service.analyze_evidence(
        media_path="/uploads/test-garbage.jpg",
        complaint_description="Illegal garbage pile on sidewalk"
    )

    assert analysis.issue_detected is True
    assert analysis.issue_type == "GARBAGE_DUMP"
    assert analysis.confidence >= 0.80
    assert analysis.severity in ["MEDIUM", "HIGH"]

def test_evidence_ai_endpoint_upload_analysis():
    fake_img = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb"
    res = client.post(
        "/api/ai/analyze-evidence",
        files={"file": ("test.jpg", io.BytesIO(fake_img), "image/jpeg")},
        data={"description": "Deep road crater near college"}
    )

    assert res.status_code == 200
    data = res.json()
    assert data["issue_detected"] is True
    assert data["issue_type"] == "POTHOLE"
    assert data["confidence"] > 0.80
    assert "visual_description" in data
