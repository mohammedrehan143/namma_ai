from datetime import datetime, timezone, timedelta
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from backend.models.entities import Complaint, User, ComplaintEvent, Evidence, Department, SLARule
from backend.schemas.complaint import ComplaintCreate, ComplaintUpdate
from backend.services.ai import ai_service
from backend.services.location_service import location_service
from backend.services.clustering_service import clustering_service
from backend.services.whatsapp_dispatcher import whatsapp_dispatcher
from backend.core.logging import logger

def generate_complaint_id(db: Session) -> str:
    """Generates a sequential human-readable complaint ID, e.g. NMA-10293, avoiding collisions."""
    count = db.query(Complaint).count()
    candidate_num = 10000 + count + 1
    candidate_id = f"NMA-{candidate_num}"
    while db.query(Complaint).filter(Complaint.id == candidate_id).first() is not None:
        candidate_num += 1
        candidate_id = f"NMA-{candidate_num}"
    return candidate_id

class ComplaintService:
    def create_complaint(self, db: Session, payload: ComplaintCreate) -> Complaint:
        # 1. Lookup or create citizen
        citizen = db.query(User).filter(User.phone == payload.citizen_phone).first()
        if not citizen:
            citizen = User(
                phone=payload.citizen_phone,
                name=payload.citizen_name,
                email=payload.citizen_email,
                role="CITIZEN"
            )
            db.add(citizen)
            db.flush()
        else:
            if payload.citizen_name and not citizen.name:
                citizen.name = payload.citizen_name
            if payload.citizen_email and not citizen.email:
                citizen.email = payload.citizen_email
            db.flush()

        complaint_id = generate_complaint_id(db)

        # 2. Invoke AI Intelligence Engine
        ai_result = ai_service.analyze_complaint(
            text=payload.description,
            location_hint=payload.location_text
        )

        category = payload.category or ai_result.category
        department_id = ai_result.department
        severity = ai_result.severity
        priority = ai_result.priority
        priority_score = ai_result.priority_score
        ai_summary = ai_result.summary
        landmark = payload.landmark or ai_result.landmark
        location_text = payload.location_text or ai_result.extracted_location

        # Geocode if latitude/longitude are missing
        latitude = payload.latitude
        longitude = payload.longitude
        if latitude is None or longitude is None:
            query_loc = location_text or landmark or payload.description
            geo_lat, geo_lon, formatted_addr = location_service.geocode(query_loc)
            latitude = geo_lat
            longitude = geo_lon
            if not location_text:
                location_text = formatted_addr

        # 3. Calculate SLA deadline from SLA rules
        sla_hours = 48
        rule = db.query(SLARule).filter(
            SLARule.department_id == department_id,
            SLARule.priority == priority
        ).first()
        if rule:
            sla_hours = rule.max_resolution_hours
        else:
            if priority == "CRITICAL":
                sla_hours = 4
            elif priority == "HIGH":
                sla_hours = 24
            elif priority == "MEDIUM":
                sla_hours = 48
            else:
                sla_hours = 72

        now = datetime.now(timezone.utc)
        sla_deadline = now + timedelta(hours=sla_hours)

        complaint = Complaint(
            id=complaint_id,
            citizen_id=citizen.id,
            category=category,
            department_id=department_id,
            raw_description=payload.description,
            ai_summary=ai_summary,
            severity=severity,
            priority=priority,
            priority_score=priority_score,
            location_text=location_text,
            landmark=landmark,
            latitude=latitude,
            longitude=longitude,
            status="REPORTED",
            channel=payload.channel,
            sla_deadline=sla_deadline,
            created_at=now,
            updated_at=now
        )
        db.add(complaint)
        db.flush()

        # Log initial event with AI extraction notes
        details_msg = f"Registered via {payload.channel}. AI categorized as {category} ({priority} priority, score {priority_score}/100)."
        if ai_result.missing_info:
            details_msg += f" Missing info detected: {', '.join(ai_result.missing_info)}"

        # Duplicate detection & Incident clustering
        try:
            cluster = clustering_service.check_and_cluster(db, complaint)
            if cluster:
                complaint.cluster_id = cluster.id
                details_msg += f" Linked to incident cluster {cluster.id} ({cluster.report_count} citizen reports)."
        except Exception as e:
            logger.warning(f"Clustering error: {e}")

        event = ComplaintEvent(
            complaint_id=complaint.id,
            event_type="REGISTERED",
            old_status=None,
            new_status="REPORTED",
            actor_type="AI",
            details=details_msg
        )
        db.add(event)
        db.commit()
        db.refresh(complaint)
        logger.info(f"AI classified complaint {complaint.id} -> {category} [{priority}] for {citizen.phone}")

        # Trigger WhatsApp evidence request to citizen
        try:
            whatsapp_dispatcher.send_evidence_request(
                to_phone=citizen.phone,
                complaint_id=complaint.id,
                category=category,
                db=db
            )
        except Exception as e:
            logger.warning(f"Non-blocking notification dispatch error: {e}")

        return complaint

    def get_complaint(self, db: Session, complaint_id: str) -> Optional[Complaint]:
        return db.query(Complaint).filter(Complaint.id == complaint_id).first()

    def list_complaints(
        self,
        db: Session,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        department_id: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[int, List[Complaint]]:
        query = db.query(Complaint)
        if status:
            query = query.filter(Complaint.status == status)
        if priority:
            query = query.filter(Complaint.priority == priority)
        if department_id:
            query = query.filter(Complaint.department_id == department_id)
        if search:
            search_fmt = f"%{search}%"
            query = query.filter(
                or_(
                    Complaint.id.ilike(search_fmt),
                    Complaint.raw_description.ilike(search_fmt),
                    Complaint.location_text.ilike(search_fmt),
                    Complaint.ai_summary.ilike(search_fmt)
                )
            )

        total = query.count()
        items = query.order_by(desc(Complaint.created_at)).offset(offset).limit(limit).all()
        return total, items

    def add_evidence(
        self,
        db: Session,
        complaint_id: str,
        media_url: str,
        media_type: str = "IMAGE",
        evidence_type: str = "CITIZEN_INITIAL",
        ai_analysis: Optional[dict] = None,
        ai_confidence: Optional[float] = None
    ) -> Evidence:
        evidence = Evidence(
            complaint_id=complaint_id,
            evidence_type=evidence_type,
            media_url=media_url,
            media_type=media_type,
            ai_analysis=ai_analysis,
            ai_confidence=ai_confidence,
            is_valid_evidence=True
        )
        db.add(evidence)

        # Log event
        event = ComplaintEvent(
            complaint_id=complaint_id,
            event_type="EVIDENCE_ADDED",
            old_status=None,
            new_status=None,
            actor_type="CITIZEN",
            details=f"Evidence uploaded ({media_type}) with AI verification"
        )
        db.add(event)
        db.commit()
        db.refresh(evidence)
        return evidence

complaint_service = ComplaintService()
