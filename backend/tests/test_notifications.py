import uuid
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal
from backend.models.entities import Complaint, User, Notification
from backend.services.notification_service import notification_service

client = TestClient(app)

def test_notification_dispatch_and_feed():
    db = SessionLocal()
    phone = f"+9192{uuid.uuid4().hex[:8]}"
    try:
        citizen = User(phone=phone, name="Lakshmi Bai", role="CITIZEN")
        db.add(citizen)
        db.commit()

        cid = f"NMA-NOTIF-{uuid.uuid4().hex[:6]}"
        complaint = Complaint(
            id=cid,
            citizen_id=citizen.id,
            category="WATER_LEAK",
            department_id="WATER",
            raw_description="Freshwater pipeline burst on 1st main",
            priority="HIGH",
            status="REPORTED"
        )
        db.add(complaint)
        db.commit()

        # 1. Test dispatch
        notif = notification_service.dispatch(
            db=db,
            phone=phone,
            message="Test notification for pipe leak",
            complaint_id=cid
        )
        assert notif is not None
        assert notif.complaint_id == cid

        # 2. Test status change notification
        notification_service.notify_status_change(db, complaint, "IN_PROGRESS")

        # 3. Query via API
        res = client.get(f"/api/notifications?complaint_id={cid}")
        assert res.status_code == 200
        items = res.json()
        assert len(items) >= 2
        assert any("IN_PROGRESS" in i["message"] for i in items)
    finally:
        db.close()
