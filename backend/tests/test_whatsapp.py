import uuid
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal
from backend.models.entities import Notification, Evidence

client = TestClient(app)

def test_whatsapp_notification_on_complaint_registration():
    phone = f"+9198{uuid.uuid4().hex[:8]}"
    payload = {
        "citizen_name": "Siddharth Verma",
        "citizen_phone": phone,
        "description": "Deep dangerous pothole near BMSIT college gate",
        "location_text": "BMSIT Gate",
        "channel": "WEB"
    }

    res = client.post("/api/complaints", json=payload)
    assert res.status_code == 201
    complaint_id = res.json()["id"]

    # Verify notification record logged in database
    db = SessionLocal()
    try:
        notif = db.query(Notification).filter(Notification.complaint_id == complaint_id).first()
        assert notif is not None
        assert notif.recipient_phone == phone
        assert notif.channel == "WHATSAPP"
        assert complaint_id in notif.message
        assert "Please send photos or videos" in notif.message
    finally:
        db.close()

def test_whatsapp_webhook_media_intake():
    phone = f"+9197{uuid.uuid4().hex[:8]}"
    # 1. Register complaint first
    reg_res = client.post(
        "/api/complaints",
        json={
            "citizen_name": "Meera Rao",
            "citizen_phone": phone,
            "description": "Garbage dump overflowing on footpath",
            "location_text": "Koramangala 4th Block",
            "channel": "WHATSAPP"
        }
    )
    assert reg_res.status_code == 201
    complaint_id = reg_res.json()["id"]

    # 2. Simulate inbound WhatsApp media webhook
    form_data = {
        "From": f"whatsapp:{phone}",
        "Body": "Here is the photo of the garbage pile",
        "NumMedia": "1",
        "MediaUrl0": "https://example.com/evidence-garbage.jpg",
        "MediaContentType0": "image/jpeg",
        "MessageSid": "SM1234567890"
    }

    webhook_res = client.post("/api/whatsapp/webhook", data=form_data)
    assert webhook_res.status_code == 200
    assert "application/xml" in webhook_res.headers["content-type"]
    assert f"Received 1 evidence file(s) for complaint #{complaint_id}" in webhook_res.text
    assert "AI Inspection" in webhook_res.text

    # 3. Verify evidence attached to complaint in DB
    db = SessionLocal()
    try:
        evidence = db.query(Evidence).filter(Evidence.complaint_id == complaint_id).all()
        assert len(evidence) >= 1
        assert evidence[-1].media_type == "IMAGE"
        assert evidence[-1].ai_confidence is not None
    finally:
        db.close()
