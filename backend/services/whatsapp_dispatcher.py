from typing import Optional
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.core.logging import logger
from backend.models.entities import Notification

class WhatsAppDispatcher:
    """Dispatches asynchronous WhatsApp alerts and citizen follow-ups via n8n.
    
    This keeps the real-time voice call path clean and decoupled from external messaging.
    """
    def __init__(self):
        self.n8n_webhook_url = settings.N8N_WHATSAPP_WEBHOOK_URL

    def send_whatsapp_message(
        self,
        to_phone: str,
        message: str,
        db: Optional[Session] = None,
        complaint_id: Optional[str] = None
    ) -> str:
        """Sends a WhatsApp message via n8n webhook or records it in the system."""
        clean_phone = to_phone.replace("whatsapp:", "").strip()
        logger.info(f"Dispatching WhatsApp notification to {clean_phone}: '{message[:60]}...'")

        msg_sid = f"n8n-wa-{hash(message + clean_phone) % 1000000}"

        # Dispatch to n8n WhatsApp workflow if webhook URL is configured
        if self.n8n_webhook_url:
            try:
                import httpx
                resp = httpx.post(
                    self.n8n_webhook_url,
                    json={
                        "phone": clean_phone,
                        "to": f"whatsapp:{clean_phone}",
                        "message": message,
                        "complaint_id": complaint_id,
                        "channel": "WHATSAPP"
                    },
                    timeout=2.0
                )
                if resp.status_code in [200, 201, 204]:
                    logger.info(f"Successfully dispatched WhatsApp message to n8n: {clean_phone}")
                else:
                    logger.warning(f"n8n WhatsApp webhook returned status {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.error(f"Failed to connect to n8n WhatsApp webhook: {e}")

        # Record in Notification audit log if DB session provided
        if db:
            try:
                notif = Notification(
                    complaint_id=complaint_id,
                    recipient_phone=clean_phone,
                    channel="WHATSAPP",
                    message=message,
                    status="SENT"
                )
                db.add(notif)
                db.commit()
            except Exception as e:
                logger.error(f"Failed to log notification in DB: {e}")

        return msg_sid

    def send_evidence_request(self, to_phone: str, complaint_id: str, category: str, db: Optional[Session] = None) -> str:
        msg = (
            f"🏛️ *Namma AI Civic Response*\n\n"
            f"Your complaint *#{complaint_id}* ({category}) has been registered.\n\n"
            f"📸 *Please send photos or videos of the issue* directly in this chat to provide proof and help officers locate the exact defect.\n\n"
            f"Our Vision AI will inspect the evidence immediately."
        )
        return self.send_whatsapp_message(to_phone, msg, db=db, complaint_id=complaint_id)

    def send_verification_request(self, to_phone: str, complaint_id: str, db: Optional[Session] = None) -> str:
        msg = (
            f"🔔 *Namma AI Resolution Confirmation*\n\n"
            f"Your complaint *#{complaint_id}* has been marked as resolved by the municipal crew.\n\n"
            f"*Is the problem actually fixed?*\n"
            f"Reply with:\n"
            f"1️⃣ — YES, ISSUE FIXED\n"
            f"2️⃣ — NO, STILL EXISTS"
        )
        return self.send_whatsapp_message(to_phone, msg, db=db, complaint_id=complaint_id)

whatsapp_dispatcher = WhatsAppDispatcher()
