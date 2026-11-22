import io
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_web_complaint_intake_flow():
    # 1. Create a complaint via web
    payload = {
        "citizen_name": "Divya Murthy",
        "citizen_phone": "+919876549999",
        "citizen_email": "divya@example.com",
        "description": "Hazardous road pothole right at college entrance causing severe skidding",
        "location_text": "BMSIT Main Gate, Yelahanka",
        "latitude": 13.1345,
        "longitude": 77.5682,
        "category": "ROAD_DAMAGE",
        "channel": "WEB"
    }

    res = client.post("/api/complaints", json=payload)
    assert res.status_code == 201
    complaint_data = res.json()
    assert "id" in complaint_data
    complaint_id = complaint_data["id"]
    assert complaint_id.startswith("NMA-")
    assert complaint_data["status"] == "REPORTED"
    assert complaint_data["category"] == "ROAD_DAMAGE"
    assert complaint_data["department_id"] == "ROADS"

    # 2. Upload photo evidence
    fake_image_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb"
    upload_res = client.post(
        f"/api/complaints/{complaint_id}/evidence",
        files={"file": ("pothole.jpg", io.BytesIO(fake_image_bytes), "image/jpeg")},
        data={"evidence_type": "CITIZEN_INITIAL"}
    )
    assert upload_res.status_code == 201
    evidence_data = upload_res.json()
    assert evidence_data["complaint_id"] == complaint_id
    assert evidence_data["media_type"] == "IMAGE"
    assert "/uploads/" in evidence_data["media_url"]

    # 3. Retrieve complaint details
    detail_res = client.get(f"/api/complaints/{complaint_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == complaint_id
    assert detail["citizen_name"] == "Divya Murthy"
    assert detail["citizen_phone"] == "+919876549999"
    assert len(detail["evidence"]) >= 1
    assert len(detail["events"]) >= 2  # REGISTERED and EVIDENCE_ADDED

    # 4. List complaints
    list_res = client.get("/api/complaints?search=BMSIT")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert any(item["id"] == complaint_id for item in list_data["items"])
