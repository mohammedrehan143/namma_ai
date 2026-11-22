import json
from typing import Optional
from backend.services.ai.base import BaseAIService
from backend.services.ai.mock_service import MockAIService
from backend.services.ai.prompts import SYSTEM_COMPLAINT_PARSER, SYSTEM_VISION_ANALYZER, SYSTEM_RESOLUTION_VERIFIER
from backend.schemas.ai import AIComplaintAnalysis, AIEvidenceAnalysis, AIResolutionVerification
from backend.core.config import settings
from backend.core.logging import logger

class GeminiAIService(BaseAIService):
    """Google Gemini AI integration with automatic fallback to deterministic MockAIService."""

    def __init__(self):
        self.mock = MockAIService()
        self.api_key = settings.LLM_API_KEY
        self.model_name = settings.LLM_MODEL or "gemini-1.5-flash"
        self._client = None

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                logger.info("Initialized Google GenAI Gemini client.")
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI SDK: {e}. Falling back to mock engine.")

    def analyze_complaint(self, text: str, location_hint: Optional[str] = None) -> AIComplaintAnalysis:
        if not self._client:
            return self.mock.analyze_complaint(text, location_hint)

        try:
            prompt = f"{SYSTEM_COMPLAINT_PARSER}\n\nCitizen Report: {text}\nLocation Hint: {location_hint or 'None'}"
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            data["ai_provider"] = "gemini"
            return AIComplaintAnalysis.model_validate(data)
        except Exception as e:
            logger.warning(f"Gemini API complaint analysis failed: {e}. Utilizing graceful fallback.")
            return self.mock.analyze_complaint(text, location_hint)

    def analyze_evidence(self, image_path_or_bytes: str, description: str) -> AIEvidenceAnalysis:
        if not self._client:
            return self.mock.analyze_evidence(image_path_or_bytes, description)

        try:
            # When multimodal images are provided with API key, process via client
            prompt = f"{SYSTEM_VISION_ANALYZER}\nComplaint: {description}"
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            data["ai_provider"] = "gemini"
            return AIEvidenceAnalysis.model_validate(data)
        except Exception as e:
            logger.warning(f"Gemini Vision analysis error: {e}. Graceful degradation.")
            return self.mock.analyze_evidence(image_path_or_bytes, description)

    def verify_resolution(self, before_image: str, after_image: str, description: str) -> AIResolutionVerification:
        if not self._client:
            return self.mock.verify_resolution(before_image, after_image, description)

        try:
            prompt = f"{SYSTEM_RESOLUTION_VERIFIER}\nDescription: {description}"
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            data["ai_provider"] = "gemini"
            return AIResolutionVerification.model_validate(data)
        except Exception as e:
            logger.warning(f"Gemini Resolution Verification error: {e}. Graceful degradation.")
            return self.mock.verify_resolution(before_image, after_image, description)
