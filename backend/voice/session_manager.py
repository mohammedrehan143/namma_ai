import time
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.services.ai import ai_service
from backend.services.complaint_service import complaint_service
from backend.services.whatsapp_dispatcher import whatsapp_dispatcher
from backend.schemas.complaint import ComplaintCreate
from backend.core.logging import logger

class VoiceSession:
    def __init__(self, session_id: str, caller_phone: str):
        self.session_id = session_id
        self.caller_phone = caller_phone
        self.created_at = time.time()
        self.updated_at = time.time()
        self.turn_count = 0
        self.state = "INITIAL"  # INITIAL -> AWAITING_STATEMENT -> CLARIFYING_LOCATION -> REGISTERED -> COMPLETED
        self.original_statement = ""
        self.extracted_category = ""
        self.extracted_location = ""
        self.extracted_landmark = ""
        self.complaint_id = ""
        self.history = []

    def add_history(self, role: str, text: str):
        self.history.append({"role": role, "text": text, "timestamp": time.time()})
        self.updated_at = time.time()

class VoiceSessionManager:
    def __init__(self):
        self._sessions: Dict[str, VoiceSession] = {}

    def get_or_create_session(self, session_id: str, caller_phone: str) -> VoiceSession:
        clean_phone = caller_phone.replace("client:", "").strip()
        if not clean_phone.startswith("+") and not clean_phone.startswith("0") and len(clean_phone) == 10:
            clean_phone = f"+91{clean_phone}"

        if session_id not in self._sessions:
            logger.info(f"Creating new Asterisk voice session: {session_id} for {clean_phone}")
            self._sessions[session_id] = VoiceSession(session_id, clean_phone)
        return self._sessions[session_id]

    def get_session(self, session_id: str) -> Optional[VoiceSession]:
        return self._sessions.get(session_id)

    def process_turn(self, session_id: str, transcript: str, db: Session) -> Dict[str, Any]:
        """Processes a speech turn from Asterisk, advances state, and returns the AI response text."""
        session = self._sessions.get(session_id)
        if not session:
            session = self.get_or_create_session(session_id, "+919876540000")

        session.turn_count += 1
        clean_transcript = transcript.strip()
        session.add_history("user", clean_transcript)

        # 1. Handle silent or inaudible input
        if not clean_transcript:
            reply = "We could not hear your statement clearly. Please state the problem and the location."
            session.add_history("assistant", reply)
            return {
                "reply_text": reply,
                "state": session.state,
                "complaint_id": session.complaint_id,
                "action": "CONTINUE"
            }

        # 2. State: CLARIFYING_LOCATION (Caller is answering follow-up for missing landmark)
        if session.state == "CLARIFYING_LOCATION":
            session.extracted_location = clean_transcript
            combined_description = f"{session.original_statement}. Location specified by caller: {clean_transcript}"

            # Create complaint with gathered details
            payload = ComplaintCreate(
                citizen_name="Voice Citizen",
                citizen_phone=session.caller_phone,
                description=combined_description,
                location_text=clean_transcript,
                landmark=clean_transcript,
                category=session.extracted_category or "ROAD_DAMAGE",
                channel="PHONE"
            )
            complaint = complaint_service.create_complaint(db, payload)
            session.complaint_id = complaint.id
            session.state = "REGISTERED"

            spoken_id = " ".join(list(complaint.id))
            reply = (
                f"Thank you. Your complaint has been registered with reference ID {spoken_id}. "
                f"It has been categorized as {complaint.category.replace('_', ' ')} with priority {complaint.priority}. "
                f"A WhatsApp message has been sent to your phone where you can upload photos of the defect. "
                f"Thank you for helping keep Bengaluru safe. Goodbye."
            )
            session.add_history("assistant", reply)
            return {
                "reply_text": reply,
                "state": session.state,
                "complaint_id": complaint.id,
                "action": "HANGUP"
            }

        # 3. State: INITIAL / AWAITING_STATEMENT
        session.original_statement = clean_transcript
        ai_analysis = ai_service.analyze_complaint(clean_transcript)
        session.extracted_category = ai_analysis.category

        # Check if location/landmark was omitted
        missing_text = " ".join(ai_analysis.missing_info).lower() if ai_analysis.missing_info else ""
        if any(term in missing_text for term in ["location", "landmark", "address"]):
            session.state = "CLARIFYING_LOCATION"
            reply = (
                f"We noted: {ai_analysis.summary}. "
                f"Could you please specify the nearest landmark, street name, or area?"
            )
            session.add_history("assistant", reply)
            return {
                "reply_text": reply,
                "state": session.state,
                "complaint_id": None,
                "action": "CONTINUE"
            }

        # Complete information: register complaint immediately
        location_val = ai_analysis.extracted_location or ai_analysis.landmark or "Bengaluru"
        payload = ComplaintCreate(
            citizen_name="Voice Citizen",
            citizen_phone=session.caller_phone,
            description=clean_transcript,
            location_text=location_val,
            landmark=ai_analysis.landmark,
            category=ai_analysis.category,
            channel="PHONE"
        )
        complaint = complaint_service.create_complaint(db, payload)
        session.complaint_id = complaint.id
        session.state = "REGISTERED"

        spoken_id = " ".join(list(complaint.id))
        reply = (
            f"Thank you. Your complaint has been registered with reference ID {spoken_id}. "
            f"It has been categorized as {complaint.category.replace('_', ' ')} with priority {complaint.priority}. "
            f"A WhatsApp message has been sent to your phone where you can upload photos of the defect. "
            f"Thank you for helping keep Bengaluru safe. Goodbye."
        )
        session.add_history("assistant", reply)
        return {
            "reply_text": reply,
            "state": session.state,
            "complaint_id": complaint.id,
            "action": "HANGUP"
        }

    def end_session(self, session_id: str, db: Optional[Session] = None) -> Optional[VoiceSession]:
        """Cleans up session and ensures asynchronous post-call notifications."""
        session = self._sessions.pop(session_id, None)
        if session:
            logger.info(f"Closed voice session {session_id}. Total turns: {session.turn_count}. Complaint: {session.complaint_id or 'None'}")
        return session

session_manager = VoiceSessionManager()
