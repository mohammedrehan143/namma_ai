from typing import Optional
from sqlalchemy.orm import Session
from backend.models.entities import Complaint, Notification, User
from backend.services.whatsapp_dispatcher import whatsapp_dispatcher
from backend.core.logging import logger

class NotificationService:
    def dispatch(
        self,
        db: Session,
        phone: str,
        message: str,
        complaint_id: Optional[str] = None,
        channel: str = "WHATSAPP"
    ) -> Notification:
        # Dispatch via WhatsApp dispatcher (n8n async automation)
        whatsapp_dispatcher.send_whatsapp_message(to_phone=phone, message=message, db=db, complaint_id=complaint_id)
        
        notif = db.query(Notification).filter(
            Notification.complaint_id == complaint_id,
            Notification.recipient_phone == phone.replace("whatsapp:", "")
        ).order_by(Notification.sent_at.desc()).first()
        return notif

    def notify_registration(self, db: Session, complaint: Complaint):
        msg = f"🏛️ *Namma AI*: Grievance #{complaint.id} registered successfully for category {complaint.category}. Priority: {complaint.priority}."
        self.dispatch(db, complaint.citizen.phone, msg, complaint.id)

    def notify_evidence_request(self, db: Session, complaint: Complaint):
        whatsapp_dispatcher.send_evidence_request(complaint.citizen.phone, complaint.id, complaint.category, db=db)

    def notify_assignment(self, db: Session, complaint: Complaint, dept_name: str):
        msg = f"📋 *Namma AI Update*: Case #{complaint.id} assigned to {dept_name}. Field investigation is underway."
        self.dispatch(db, complaint.citizen.phone, msg, complaint.id)

    def notify_status_change(self, db: Session, complaint: Complaint, new_status: str):
        msg = f"🔄 *Namma AI Status Update*: Case #{complaint.id} is now in status *{new_status}*."
        self.dispatch(db, complaint.citizen.phone, msg, complaint.id)

    def notify_resolution_submitted(self, db: Session, complaint: Complaint):
        whatsapp_dispatcher.send_verification_request(complaint.citizen.phone, complaint.id, db=db)

    def notify_reopened_and_escalated(self, db: Session, complaint: Complaint, reason: str = ""):
        msg = (
            f"⚠️ *Namma AI Reopening Alert*: Case #{complaint.id} was reopened by citizen confirmation.\n"
            f"Reason: {reason or 'Defect still persists'}.\n"
            f"Supervisor has been alerted for priority re-inspection."
        )
        self.dispatch(db, complaint.citizen.phone, msg, complaint.id)

        # Notify supervisor
        supervisor = db.query(User).filter(User.role == "SUPERVISOR", User.department_id == complaint.department_id).first()
        if supervisor:
            sup_msg = f"🚨 *SUPERVISOR ESCALATION*: Reopened Case #{complaint.id} ({complaint.category}) rejected by citizen. Immediate field review needed."
            self.dispatch(db, supervisor.phone, sup_msg, complaint.id)

notification_service = NotificationService()
