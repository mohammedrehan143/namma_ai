from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict

class ResolutionSubmitRequest(BaseModel):
    officer_notes: str = Field(..., min_length=5)
    officer_id: Optional[str] = None

class CitizenVerificationRequest(BaseModel):
    is_fixed: bool
    citizen_notes: Optional[str] = None

class ResolutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    complaint_id: str
    officer_id: Optional[str] = None
    officer_notes: Optional[str] = None
    after_media_url: Optional[str] = None
    ai_verified: bool = False
    ai_verification: Optional[Any] = None
    citizen_feedback: str
    citizen_rejection_reason: Optional[str] = None
    created_at: datetime
