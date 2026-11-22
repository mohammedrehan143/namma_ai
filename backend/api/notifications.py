from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.core.database import get_db
from backend.models.entities import Notification

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("")
def list_notifications(
    complaint_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Notification)
    if complaint_id:
        query = query.filter(Notification.complaint_id == complaint_id)

    items = query.order_by(desc(Notification.sent_at)).limit(limit).all()
    return [
        {
            "id": n.id,
            "complaint_id": n.complaint_id,
            "recipient_phone": n.recipient_phone,
            "channel": n.channel,
            "message": n.message,
            "status": n.status,
            "sent_at": n.sent_at
        }
        for n in items
    ]
