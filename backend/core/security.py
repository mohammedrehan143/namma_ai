import os
import re
import html
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import jwt
from fastapi import HTTPException, status, UploadFile
from backend.core.config import settings
from backend.core.logging import logger

JWT_ALGORITHM = "HS256"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm"}
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024   # 10 MB
MAX_VIDEO_SIZE_BYTES = 25 * 1024 * 1024   # 25 MB

def sanitize_text(text: Optional[str]) -> Optional[str]:
    """Sanitizes user text inputs by stripping HTML and escaping script patterns."""
    if not text:
        return text
    # Strip dangerous HTML tags
    cleaned = re.sub(r"<[^>]*?>", "", text)
    return html.escape(cleaned.strip())

def validate_upload_file(file: UploadFile) -> str:
    """Validates uploaded media file type, extension, and enforces strict security constraints."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file missing filename")

    # Path traversal protection
    sanitized_name = os.path.basename(file.filename)
    if ".." in sanitized_name or "/" in sanitized_name or "\\" in sanitized_name:
        raise HTTPException(status_code=400, detail="Invalid filename format")

    content_type = file.content_type or ""
    extension = os.path.splitext(sanitized_name)[1].lower()

    if content_type in ALLOWED_IMAGE_TYPES or extension in [".jpg", ".jpeg", ".png", ".webp"]:
        return "IMAGE"
    elif content_type in ALLOWED_VIDEO_TYPES or extension in [".mp4", ".webm"]:
        return "VIDEO"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported media type '{content_type}'. Allowed types: JPEG, PNG, WEBP, MP4, WEBM."
        )

def create_access_token(user_id: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=24))
    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials.")
