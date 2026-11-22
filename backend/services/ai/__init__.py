from backend.core.config import settings
from backend.services.ai.base import BaseAIService
from backend.services.ai.mock_service import MockAIService
from backend.services.ai.gemini_service import GeminiAIService

def get_ai_service() -> BaseAIService:
    provider = (settings.LLM_PROVIDER or "mock").lower()
    if provider == "gemini" and settings.LLM_API_KEY:
        return GeminiAIService()
    return MockAIService()

ai_service = get_ai_service()

__all__ = ["BaseAIService", "MockAIService", "GeminiAIService", "get_ai_service", "ai_service"]
