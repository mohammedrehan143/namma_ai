from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import check_db_connection, get_db
from backend.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    db_ok = check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "app_name": "Namma AI",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_ok else "disconnected",
        "storage_provider": settings.STORAGE_PROVIDER,
        "llm_provider": settings.LLM_PROVIDER,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
