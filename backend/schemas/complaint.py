from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict

class ComplaintCreate(BaseModel):
    citizen_name: str = Field(..., min_length=2, max_length=100)
    citizen_phone: str = Field(..., min_length=10, max_length=20)
    citizen_email: Optional[str] = Field(None, max_length=120)
    description: str = Field(..., min_length=5)
    location_text: Optional[str] = Field(None, max_length=255)
    landmark: Optional[str] = Field(None, max_length=255)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None
    channel: str = Field(default="WEB")

class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    department_id: Optional[str] = None
    assigned_officer_id: Optional[str] = None
    priority: Optional[str] = None
    severity: Optional[str] = None
    notes: Optional[str] = None

class EvidenceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    media_url: str
    media_type: str
    evidence_type: str
    ai_confidence: Optional[float] = None
    ai_analysis: Optional[Any] = None
    uploaded_at: datetime

class ComplaintEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: str
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    actor_type: str
    details: Optional[str] = None
    created_at: datetime

class ComplaintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    category: str
    department_id: Optional[str] = None
    severity: str
    priority: str
    priority_score: int
    raw_description: str
    ai_summary: Optional[str] = None
    location_text: Optional[str] = None
    landmark: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    cluster_id: Optional[str] = None
    channel: str
    sla_deadline: Optional[datetime] = None
    is_sla_breached: bool = False
    assigned_officer_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ComplaintDetailResponse(ComplaintResponse):
    citizen_name: Optional[str] = None
    citizen_phone: Optional[str] = None
    department_name: Optional[str] = None
    evidence: List[EvidenceSummary] = []
    events: List[ComplaintEventResponse] = []
