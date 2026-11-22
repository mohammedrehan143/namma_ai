import os
import sys
from pathlib import Path

# Add project root and backend dir to sys.path so imports work regardless of working directory
_BACKEND_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BACKEND_DIR.parent
for _p in [str(_PROJECT_ROOT), str(_BACKEND_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.core.config import settings
from backend.core.logging import logger
from backend.core.errors import NammaAIException, namma_exception_handler, generic_exception_handler
from backend.api.health import router as health_router
from backend.api.complaints import router as complaints_router
from backend.api.location import router as location_router
from backend.api.whatsapp import router as whatsapp_router
from backend.api.ai import router as ai_router
from backend.api.clusters import router as clusters_router
from backend.api.dashboard import router as dashboard_router
from backend.api.sla import router as sla_router
from backend.api.voice import router as voice_router
from backend.api.notifications import router as notifications_router
from backend.api.auth import router as auth_router
from backend.api.demo import router as demo_router
from backend.core.init_db import init_database

# Ensure local upload dir exists
os.makedirs(settings.STORAGE_LOCAL_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Namma AI API starting up in [{settings.ENVIRONMENT}] mode on port {settings.PORT}...")
    try:
        init_database()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    yield
    logger.info("Namma AI API shutting down...")

app = FastAPI(
    title="Namma AI Platform API",
    description="Multimodal civic complaint and outcome-verification platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware — dynamic origins and Vercel preview/production regex support
cors_origins = settings.cors_origins_list
allow_all = "*" in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else cors_origins,
    allow_origin_regex=None if allow_all else (settings.CORS_ORIGIN_REGEX or None),
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(NammaAIException, namma_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Mount local uploads directory for static media retrieval
app.mount("/uploads", StaticFiles(directory=settings.STORAGE_LOCAL_DIR), name="uploads")

@app.get("/")
def root():
    return {
        "status": "online",
        "app_name": "Namma AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Include Core Routers
app.include_router(health_router)
app.include_router(complaints_router)
app.include_router(location_router)
app.include_router(whatsapp_router)
app.include_router(ai_router)
app.include_router(clusters_router)
app.include_router(dashboard_router)
app.include_router(sla_router)
app.include_router(voice_router)
app.include_router(notifications_router)
app.include_router(auth_router)
app.include_router(demo_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
