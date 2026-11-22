import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = Field(default="development")
    PORT: int = Field(default=8000)
    HOST: str = Field(default="0.0.0.0")
    SECRET_KEY: str = Field(default="namma-ai-super-secret-key-change-in-production-2026")
    
    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000")
    CORS_ORIGIN_REGEX: str = Field(default=r"https://.*\.vercel\.app")

    # Integrations & Admin Security
    TELEGRAM_INGESTION_SECRET: str = Field(default="namma-telegram-n8n-secret-2026")
    ADMIN_API_KEY: str = Field(default="namma-admin-secret-key-2026")
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./namma_ai.db")
    
    # Storage
    STORAGE_PROVIDER: str = Field(default="local")
    STORAGE_LOCAL_DIR: str = Field(default="./uploads")
    STORAGE_BUCKET_NAME: str = Field(default="namma-evidence")
    
    # Supabase (Optional)
    SUPABASE_URL: str = Field(default="")
    SUPABASE_ANON_KEY: str = Field(default="")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="")
    
    # AI Providers (gemini | openai | mock)
    LLM_PROVIDER: str = Field(default="mock")
    LLM_API_KEY: str = Field(default="")
    LLM_MODEL: str = Field(default="gemini-1.5-flash")
    VISION_MODEL: str = Field(default="gemini-1.5-flash")
    EMBEDDINGS_MODEL: str = Field(default="text-embedding-004")
    
    # Telephony — Exotel & Asterisk
    EXOTEL_ACCOUNT_SID: str = Field(default="")
    EXOTEL_API_KEY: str = Field(default="")
    EXOTEL_API_TOKEN: str = Field(default="")
    EXOTEL_VIRTUAL_NUMBER: str = Field(default="")
    EXOTEL_SIP_GATEWAY: str = Field(default="")
    ASTERISK_HOST: str = Field(default="127.0.0.1")
    ASTERISK_PORT: int = Field(default=5060)

    # Voice Processing (STT & TTS)
    STT_PROVIDER: str = Field(default="mock")  # faster-whisper | mock
    STT_SERVICE_URL: str = Field(default="http://127.0.0.1:8000/v1/audio/transcriptions")
    TTS_PROVIDER: str = Field(default="mock")  # piper | mock
    TTS_SERVICE_URL: str = Field(default="http://127.0.0.1:5000/api/tts")

    # WhatsApp Automation via n8n
    N8N_WHATSAPP_WEBHOOK_URL: str = Field(default="")
    
    # Maps
    MAPS_PROVIDER: str = Field(default="osm")
    MAPS_API_KEY: str = Field(default="")
    
    # SLA Defaults (in hours)
    SLA_HOURS_CRITICAL: int = Field(default=4)
    SLA_HOURS_HIGH: int = Field(default=24)
    SLA_HOURS_MEDIUM: int = Field(default=48)
    SLA_HOURS_LOW: int = Field(default=72)

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
