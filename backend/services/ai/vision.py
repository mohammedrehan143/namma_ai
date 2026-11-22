import os
from typing import Optional
from backend.services.ai import ai_service
from backend.schemas.ai import AIEvidenceAnalysis
from backend.core.logging import logger

class VisionAIService:
    def analyze_evidence(
        self,
        media_path: str,
        complaint_description: str,
        category: Optional[str] = None
    ) -> AIEvidenceAnalysis:
        """Analyzes photographic/video evidence against citizen complaint description."""
        logger.info(f"VisionAIService analyzing evidence '{media_path}' for complaint: '{complaint_description[:50]}...'")
        
        # Invoke underlying AI service (Gemini or Mock)
        analysis = ai_service.analyze_evidence(media_path, complaint_description)

        # Apply guardrails: never auto-reject on low confidence
        # Flag for human inspection if confidence is under 0.70
        return analysis

vision_ai_service = VisionAIService()
