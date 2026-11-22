from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class AIComplaintAnalysis(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: str = Field(..., description="ROAD_DAMAGE, GARBAGE, DRAINAGE, SEWAGE, WATER_LEAK, STREETLIGHT, PUBLIC_INFRA, OTHER")
    department: str = Field(..., description="ROADS, SANITATION, DRAINAGE, WATER, ELECTRICAL, PUBLIC_WORKS")
    severity: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    priority: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    priority_score: int = Field(..., ge=0, le=100)
    summary: str = Field(..., min_length=5, max_length=200)
    extracted_location: Optional[str] = None
    landmark: Optional[str] = None
    safety_hazard: bool = False
    missing_info: List[str] = []
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    ai_provider: str = Field(default="mock")

class AIEvidenceAnalysis(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    issue_detected: bool
    issue_type: str = Field(..., description="POTHOLE, GARBAGE_DUMP, DRAINAGE_CLOG, SEWAGE_LEAK, WATER_BURST, BROKEN_LIGHT, TREE_FALL, OTHER")
    matches_complaint: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    severity: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    visual_description: str
    quality_score: float = Field(default=0.9, ge=0.0, le=1.0)
    requires_human_review: bool = Field(default=False)
    ai_provider: str = Field(default="mock")

class AIResolutionVerification(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resolution_likely_complete: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    remaining_issue: Optional[str] = None
    is_same_location: bool = True
    notes: str
    audit_flag: str = Field(default="PASSED", description="PASSED, SUSPICIOUS, INCOMPLETE")
    ai_provider: str = Field(default="mock")
