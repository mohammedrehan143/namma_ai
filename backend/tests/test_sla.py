import uuid
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import SessionLocal
from backend.models.entities import Complaint, User, SLARule, Notification
from backend.services.sla_service import sla_service

client = TestClient(app)

def test_sla_rules_listing():
    res = client.get("/api/sla/rules")
    assert res.status_code == 200
    rules = res.json()
    assert len(rules) >= 4
    critical_rule = next((r for r in rules if r["priority"] == "CRITICAL"), None)
    assert critical_rule is not None
    assert critical_rule["max_resolution_hours"] == 4

def test_sla_breach_detection_and_escalation():
    db = SessionLocal()
    phone = f"+9196{uuid.uuid4().hex[:8]}"
    try:
        # Create user
        citizen = User(phone=phone, name="Suresh Patil", role="CITIZEN")
        db.add(citizen)
        db.commit()

        # Create complaint with past deadline (breached)
        cid = f"NMA-BREACH-{uuid.uuid4().hex[:6]}"
        past_deadline = datetime.now(timezone.utc) - timedelta(hours=2)
        complaint = Complaint(
            id=cid,
            citizen_id=citizen.id,
            category="ROAD_DAMAGE",
            department_id="ROADS",
            raw_description="Dangerous pothole ignored for days",
            priority="HIGH",
            status="IN_PROGRESS",
            sla_deadline=past_deadline,
            is_sla_breached=False
        )
        db.add(complaint)
        db.commit()

        # Trigger SLA check via API
        scan_res = client.post("/api/sla/check-violations")
        assert scan_res.status_code == 200
        scan_data = scan_res.json()
        assert scan_data["breached_count"] >= 1

        # Verify complaint updated in DB
        db.refresh(complaint)
        assert complaint.is_sla_breached is True
        assert complaint.status == "ESCALATED"

        # Verify supervisor notification logged
        supervisor_notif = db.query(Notification).filter(Notification.complaint_id == cid).first()
        assert supervisor_notif is not None
        assert "SLA BREACH ALERT" in supervisor_notif.message

    finally:
        db.close()
