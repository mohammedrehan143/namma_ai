from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.services.ai import ai_service
from backend.services.ai.vision import vision_ai_service
from backend.services.storage import storage_service
from backend.services.complaint_service import complaint_service
from backend.schemas.ai import AIComplaintAnalysis, AIEvidenceAnalysis
from backend.schemas.evidence import EvidenceResponse

router = APIRouter(prefix="/api/ai", tags=["AI Intelligence & Vision"])

@router.post("/classify", response_model=AIComplaintAnalysis)
def classify_complaint_text(
    description: str = Form(...),
    location_hint: Optional[str] = Form(None)
):
    """Classifies unstructured complaint text using LLM."""
    return ai_service.analyze_complaint(description, location_hint=location_hint)

@router.post("/analyze-evidence", response_model=AIEvidenceAnalysis)
def analyze_uploaded_evidence(
    file: UploadFile = File(...),
    description: str = Form(...)
):
    """Analyzes an uploaded image using Multimodal Vision AI."""
    media_url = storage_service.save_upload_file(file)
    analysis = vision_ai_service.analyze_evidence(
        media_path=media_url,
        complaint_description=description
    )
    return analysis

@router.post("/complaints/{complaint_id}/evidence/{evidence_id}/re-analyze", response_model=EvidenceResponse)
def reanalyze_existing_evidence(
    complaint_id: str,
    evidence_id: str,
    db: Session = Depends(get_db)
):
    """Re-analyzes an existing evidence item for a complaint."""
    complaint = complaint_service.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    target_ev = next((ev for ev in complaint.evidence if ev.id == evidence_id), None)
    if not target_ev:
        raise HTTPException(status_code=404, detail="Evidence not found")

    analysis = vision_ai_service.analyze_evidence(
        media_path=target_ev.media_url,
        complaint_description=complaint.raw_description
    )

    target_ev.ai_analysis = analysis.model_dump()
    target_ev.ai_confidence = analysis.confidence
    db.commit()
    db.refresh(target_ev)
    return target_ev
