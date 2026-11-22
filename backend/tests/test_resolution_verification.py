import io
import uuid
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_officer_resolution_and_ai_verification_workflow():
    phone = f"+9194{uuid.uuid4().hex[:8]}"

    # 1. Citizen registers complaint
    reg_res = client.post(
        "/api/complaints",
        json={
            "citizen_name": "Deepak Joshi",
            "citizen_phone": phone,
            "description": "Deep asphalt pothole near BMSIT gate causing danger",
            "location_text": "BMSIT Gate, Yelahanka",
            "channel": "WEB"
        }
    )
    assert reg_res.status_code == 201
    complaint_id = reg_res.json()["id"]

    # 2. Upload initial "before" photo evidence
    fake_before_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdbbefore"
    upload_res = client.post(
        f"/api/complaints/{complaint_id}/evidence",
        files={"file": ("before.jpg", io.BytesIO(fake_before_bytes), "image/jpeg")},
        data={"evidence_type": "CITIZEN_INITIAL"}
    )
    assert upload_res.status_code == 201

    # 3. Officer accepts complaint and sets IN_PROGRESS
    assign_res = client.post(
        f"/api/complaints/{complaint_id}/assign",
        json={
            "department_id": "ROADS",
            "status": "IN_PROGRESS",
            "notes": "Crew dispatched with asphalt patch truck."
        }
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["status"] == "IN_PROGRESS"

    # 4. Officer finishes repair and uploads "after" proof photo
    fake_after_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdbafter"
    resolve_res = client.post(
        f"/api/complaints/{complaint_id}/resolve",
        data={"officer_notes": "Pothole filled with bitumen mix, leveled and compacted."},
        files={"after_media_file": ("after.jpg", io.BytesIO(fake_after_bytes), "image/jpeg")}
    )
    assert resolve_res.status_code == 200
    res_data = resolve_res.json()
    assert res_data["ai_verified"] is True
    assert res_data["ai_verification"]["resolution_likely_complete"] is True
    assert res_data["ai_verification"]["confidence"] >= 0.85
    assert res_data["citizen_feedback"] == "PENDING"

    # Verify complaint status transitioned to CITIZEN_VERIFICATION
    detail_res = client.get(f"/api/complaints/{complaint_id}")
    assert detail_res.json()["status"] == "CITIZEN_VERIFICATION"

    # 5. Citizen Rejects Resolution -> Complaint must auto-reopen and escalate
    verify_reject_res = client.post(
        f"/api/complaints/{complaint_id}/verify",
        json={"is_fixed": False, "citizen_notes": "Rough edges remaining, gravel is loose"}
    )
    assert verify_reject_res.status_code == 200
    assert verify_reject_res.json()["status"] == "REOPENED"
    assert verify_reject_res.json()["escalated"] is True

    # Check complaint in DB has reopen count and status REOPENED
    reopened_detail = client.get(f"/api/complaints/{complaint_id}").json()
    assert reopened_detail["status"] == "REOPENED"

    # 6. Second resolution and Citizen Confirms
    resolve_res_2 = client.post(
        f"/api/complaints/{complaint_id}/resolve",
        data={"officer_notes": "Additional roller compaction and seal coat applied."},
        files={"after_media_file": ("after2.jpg", io.BytesIO(fake_after_bytes), "image/jpeg")}
    )
    assert resolve_res_2.status_code == 200

    # Citizen confirms fixed via WhatsApp or Web
    verify_approve_res = client.post(
        f"/api/complaints/{complaint_id}/verify",
        json={"is_fixed": True}
    )
    assert verify_approve_res.status_code == 200
    assert verify_approve_res.json()["status"] == "RESOLVED"

    final_detail = client.get(f"/api/complaints/{complaint_id}").json()
    assert final_detail["status"] == "RESOLVED"
