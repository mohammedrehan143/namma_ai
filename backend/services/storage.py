import os
import uuid
import shutil
from fastapi import UploadFile
from backend.core.config import settings
from backend.core.logging import logger

class StorageService:
    def __init__(self):
        self.upload_dir = settings.STORAGE_LOCAL_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
        self.provider = settings.STORAGE_PROVIDER
        self.supabase_client = None

        if (
            self.provider == "supabase"
            and settings.SUPABASE_URL
            and "[YOUR-PROJECT-REF]" not in settings.SUPABASE_URL
            and "your-project" not in settings.SUPABASE_URL
        ):
            try:
                from supabase import create_client
                key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
                if key:
                    self.supabase_client = create_client(settings.SUPABASE_URL, key)
                    logger.info("Initialized Supabase Storage client.")
            except Exception as e:
                logger.warning(f"Could not initialize Supabase Storage client: {e}. Falling back to local storage.")

    def save_upload_file(self, file: UploadFile) -> str:
        """Saves an uploaded file to Supabase Storage or locally and returns the URL."""
        extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        file_id = f"{uuid.uuid4().hex[:12]}{extension}"

        # 1. Attempt Supabase Storage upload if configured
        if self.provider == "supabase" and self.supabase_client:
            try:
                content = file.file.read()
                content_type = file.content_type or "image/jpeg"
                bucket = settings.STORAGE_BUCKET_NAME

                # Upload to Supabase bucket
                self.supabase_client.storage.from_(bucket).upload(
                    path=file_id,
                    file=content,
                    file_options={"content-type": content_type}
                )

                # Retrieve public URL
                public_url = self.supabase_client.storage.from_(bucket).get_public_url(file_id)
                logger.info(f"Saved uploaded evidence file to Supabase Storage: {public_url}")
                return public_url
            except Exception as e:
                logger.warning(f"Supabase Storage upload failed ({e}). Falling back to local storage.")
                file.file.seek(0)

        # 2. Local filesystem storage
        file_path = os.path.join(self.upload_dir, file_id)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.info(f"Saved uploaded evidence file locally: {file_path}")
            return f"/uploads/{file_id}"
        except Exception as e:
            logger.error(f"Failed to save upload file: {e}")
            raise

storage_service = StorageService()
