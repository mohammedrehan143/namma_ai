import uuid
from datetime import datetime, timezone, timedelta
from backend.core.database import SessionLocal
from backend.models.entities import (
    User,
    Department,
    ComplaintCategory,
    Complaint,
    Evidence,
    Resolution,
    ComplaintEvent,
    SLARule,
    IncidentCluster,
    Notification
)

def test_database_models_and_relationships():
    db = SessionLocal()
    try:
        # 1. Verify seeded master data
        dept = db.query(Department).filter(Department.id == "ROADS").first()
        assert dept is not None
        assert dept.name == "Road Maintenance & Infrastructure"

        category = db.query(ComplaintCategory).filter(ComplaintCategory.id == "ROAD_DAMAGE").first()
        assert category is not None
        assert category.department_id == "ROADS"

        sla_rule = db.query(SLARule).filter(SLARule.department_id == "ROADS", SLARule.priority == "CRITICAL").first()
        assert sla_rule is not None
        assert sla_rule.max_resolution_hours == 4

        # 2. Create citizen
        unique_phone = f"+9199{uuid.uuid4().hex[:8]}"
        citizen = User(
            phone=unique_phone,
            name="Aarav Patel",
            role="CITIZEN"
        )
        db.add(citizen)
        db.commit()
        db.refresh(citizen)
        assert citizen.id is not None

        # 3. Create incident cluster
        cluster_id = f"INC-{uuid.uuid4().hex[:6]}"
        cluster = IncidentCluster(
            id=cluster_id,
            title="Road Sinkhole Test",
            category="ROAD_DAMAGE",
            center_latitude=13.1345,
            center_longitude=77.5682,
            report_count=1
        )
        db.add(cluster)
        db.commit()

        # 4. Create complaint
        test_complaint_id = f"NMA-{uuid.uuid4().hex[:6]}"
        now = datetime.now(timezone.utc)
        complaint = Complaint(
            id=test_complaint_id,
            citizen_id=citizen.id,
            cluster_id=cluster.id,
            department_id="ROADS",
            category="ROAD_DAMAGE",
            raw_description="Deep sinkhole appeared on road",
            ai_summary="Hazardous road cavity",
            severity="CRITICAL",
            priority="CRITICAL",
            priority_score=95,
            location_text="BMSIT Gate",
            latitude=13.1345,
            longitude=77.5682,
            status="REPORTED",
            channel="WEB",
            sla_deadline=now + timedelta(hours=4)
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        assert complaint.id == test_complaint_id
        assert complaint.citizen.phone == unique_phone
        assert complaint.cluster.id == cluster_id

        # 5. Add evidence
        ev = Evidence(
            complaint_id=complaint.id,
            evidence_type="CITIZEN_INITIAL",
            media_url="/uploads/test-sinkhole.jpg",
            media_type="IMAGE",
            ai_confidence=0.96,
            ai_analysis={"issue_detected": True, "issue_type": "POTHOLE"}
        )
        db.add(ev)
        db.commit()
        assert len(complaint.evidence) == 1

        # 6. Add complaint event
        event = ComplaintEvent(
            complaint_id=complaint.id,
            event_type="REGISTERED",
            old_status=None,
            new_status="REPORTED",
            actor_type="CITIZEN",
            details="Registered via test"
        )
        db.add(event)
        db.commit()
        assert len(complaint.events) == 1

        # 7. Add notification
        notif = Notification(
            complaint_id=complaint.id,
            recipient_phone=citizen.phone,
            channel="WHATSAPP",
            message="Your complaint #NMA-99901 has been registered"
        )
        db.add(notif)
        db.commit()
        assert len(complaint.notifications) == 1

        # 8. Add resolution
        resolution = Resolution(
            complaint_id=complaint.id,
            officer_notes="Road repaired using asphalt",
            after_media_url="/uploads/test-fixed.jpg",
            ai_verified=True,
            citizen_feedback="PENDING"
        )
        db.add(resolution)
        db.commit()
        assert len(complaint.resolutions) == 1

    finally:
        db.close()
