import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Index
)
from sqlalchemy.orm import relationship
from backend.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    email = Column(String(120), nullable=True)
    role = Column(String(20), default="CITIZEN", nullable=False)  # CITIZEN, OFFICER, SUPERVISOR, ADMIN
    department_id = Column(String(50), ForeignKey("departments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    complaints = relationship("Complaint", back_populates="citizen", foreign_keys="Complaint.citizen_id")
    resolutions = relationship("Resolution", back_populates="officer", foreign_keys="Resolution.officer_id")

class Department(Base):
    __tablename__ = "departments"

    id = Column(String(50), primary_key=True)  # ROADS, SANITATION, DRAINAGE, WATER, ELECTRICAL, PUBLIC_WORKS
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    contact_email = Column(String(120), nullable=True)
    default_sla_hours = Column(Integer, default=48, nullable=False)

    complaints = relationship("Complaint", back_populates="department")
    sla_rules = relationship("SLARule", back_populates="department")
    categories = relationship("ComplaintCategory", back_populates="department")

class ComplaintCategory(Base):
    __tablename__ = "complaint_categories"

    id = Column(String(50), primary_key=True)  # ROAD_DAMAGE, GARBAGE, DRAINAGE, etc.
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    department_id = Column(String(50), ForeignKey("departments.id"), nullable=False)
    default_priority = Column(String(20), default="MEDIUM", nullable=False)

    department = relationship("Department", back_populates="categories")

class IncidentCluster(Base):
    __tablename__ = "incident_clusters"

    id = Column(String(50), primary_key=True)  # e.g., INC-101
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    center_latitude = Column(Float, nullable=False)
    center_longitude = Column(Float, nullable=False)
    status = Column(String(30), default="ACTIVE", index=True)  # ACTIVE, RESOLVED
    report_count = Column(Integer, default=1, nullable=False)
    first_reported_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    last_reported_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    complaints = relationship("Complaint", back_populates="cluster")

    __table_args__ = (
        Index("idx_cluster_coords", "center_latitude", "center_longitude"),
    )

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(30), primary_key=True)  # e.g., NMA-10293
    citizen_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    cluster_id = Column(String(50), ForeignKey("incident_clusters.id"), nullable=True, index=True)
    department_id = Column(String(50), ForeignKey("departments.id"), nullable=True, index=True)
    
    category = Column(String(50), default="OTHER", index=True, nullable=False)
    raw_description = Column(Text, nullable=False)
    ai_summary = Column(Text, nullable=True)
    
    severity = Column(String(20), default="MEDIUM", index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    priority = Column(String(20), default="MEDIUM", index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    priority_score = Column(Integer, default=50)                 # 0 - 100
    
    location_text = Column(String(255), nullable=True)
    landmark = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    status = Column(String(30), default="REPORTED", index=True, nullable=False)
    # REPORTED, AI_PROCESSING, ASSIGNED, IN_PROGRESS, RESOLUTION_SUBMITTED, AI_VERIFICATION, CITIZEN_VERIFICATION, RESOLVED, REOPENED, ESCALATED
    
    channel = Column(String(20), default="WEB")  # WEB, PHONE, WHATSAPP
    sla_deadline = Column(DateTime(timezone=True), nullable=True)
    is_sla_breached = Column(Boolean, default=False, index=True)
    
    assigned_officer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    reopen_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    citizen = relationship("User", foreign_keys=[citizen_id], back_populates="complaints")
    assigned_officer = relationship("User", foreign_keys=[assigned_officer_id])
    department = relationship("Department", back_populates="complaints")
    cluster = relationship("IncidentCluster", back_populates="complaints")
    evidence = relationship("Evidence", back_populates="complaint", cascade="all, delete-orphan")
    events = relationship("ComplaintEvent", back_populates="complaint", cascade="all, delete-orphan")
    resolutions = relationship("Resolution", back_populates="complaint", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="complaint", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_complaint_geo", "latitude", "longitude"),
        Index("idx_complaint_status_prio", "status", "priority"),
    )

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complaint_id = Column(String(30), ForeignKey("complaints.id"), nullable=False, index=True)
    evidence_type = Column(String(30), default="CITIZEN_INITIAL")  # CITIZEN_INITIAL, CITIZEN_FOLLOWUP, OFFICER_RESOLUTION
    media_url = Column(String(500), nullable=False)
    media_type = Column(String(20), default="IMAGE")              # IMAGE, VIDEO
    ai_analysis = Column(JSON, nullable=True)
    ai_confidence = Column(Float, nullable=True)
    is_valid_evidence = Column(Boolean, default=True)
    uploaded_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    complaint = relationship("Complaint", back_populates="evidence")

class Resolution(Base):
    __tablename__ = "resolutions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complaint_id = Column(String(30), ForeignKey("complaints.id"), nullable=False, index=True)
    officer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    officer_notes = Column(Text, nullable=True)
    after_media_url = Column(String(500), nullable=True)
    ai_verification = Column(JSON, nullable=True)
    ai_verified = Column(Boolean, default=False)
    citizen_feedback = Column(String(30), default="PENDING")  # PENDING, CONFIRMED_FIXED, REJECTED
    citizen_rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    complaint = relationship("Complaint", back_populates="resolutions")
    officer = relationship("User", foreign_keys=[officer_id], back_populates="resolutions")

class ComplaintEvent(Base):
    __tablename__ = "complaint_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complaint_id = Column(String(30), ForeignKey("complaints.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # REGISTERED, ASSIGNED, EVIDENCE_ADDED, RESOLVED, REOPENED, ESCALATED
    old_status = Column(String(30), nullable=True)
    new_status = Column(String(30), nullable=True)
    actor_type = Column(String(30), default="SYSTEM")  # CITIZEN, OFFICER, SYSTEM, AI
    actor_id = Column(String(36), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    complaint = relationship("Complaint", back_populates="events")

class SLARule(Base):
    __tablename__ = "sla_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    department_id = Column(String(50), ForeignKey("departments.id"), nullable=False)
    priority = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    max_resolution_hours = Column(Integer, nullable=False)
    warning_threshold_hours = Column(Integer, nullable=False)

    department = relationship("Department", back_populates="sla_rules")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complaint_id = Column(String(30), ForeignKey("complaints.id"), nullable=True, index=True)
    recipient_phone = Column(String(20), nullable=False)
    channel = Column(String(20), default="WHATSAPP")  # WHATSAPP, SMS, IN_APP
    message = Column(Text, nullable=False)
    status = Column(String(20), default="SENT")       # PENDING, SENT, FAILED
    sent_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    complaint = relationship("Complaint", back_populates="notifications")
