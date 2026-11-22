from abc import ABC, abstractmethod
from typing import Optional
from backend.schemas.ai import AIComplaintAnalysis, AIEvidenceAnalysis, AIResolutionVerification

class BaseAIService(ABC):
    @abstractmethod
    def analyze_complaint(self, text: str, location_hint: Optional[str] = None) -> AIComplaintAnalysis:
        pass

    @abstractmethod
    def analyze_evidence(self, image_path_or_bytes: str, description: str) -> AIEvidenceAnalysis:
        pass

    @abstractmethod
    def verify_resolution(self, before_image: str, after_image: str, description: str) -> AIResolutionVerification:
        pass
