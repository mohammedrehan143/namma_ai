from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict

class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    complaint_id: str
    evidence_type: str
    media_url: str
    media_type: str
    ai_confidence: Optional[float] = None
    ai_analysis: Optional[Any] = None
    is_valid_evidence: bool = True
    uploaded_at: datetime
