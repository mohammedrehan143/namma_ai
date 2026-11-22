from fastapi import APIRouter, Depends, Request, Response, UploadFile, File, Form, Header
from typing import Optional
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.voice.session_manager import session_manager
from backend.voice.audio_service import audio_service
from backend.core.logging import logger

router = APIRouter(prefix="/api/voice", tags=["Asterisk Telephony Voice Engine"])

GREETING_TEXT = (
    "Namaskara. Welcome to Namma A I Civic Grievance Helpline. "
    "Please state the problem you would like to report and mention the landmark or location."
)

@router.post("/session/start")
@router.get("/session/start")
async def voice_session_start(
    request: Request,
    session_id: Optional[str] = None,
    caller_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Initial handshake when Asterisk receives an inbound SIP call from Exotel."""
    # Support both JSON, Query params, and Form-Data from Asterisk curl
    s_id = session_id
    c_id = caller_id

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            s_id = body.get("session_id", s_id)
            c_id = body.get("caller_id", c_id)
        except Exception:
            pass
    elif "application/x-www-form-urlencoded" in content_type:
        try:
            form = await request.form()
            s_id = form.get("session_id", s_id)
            c_id = form.get("caller_id", c_id)
        except Exception:
            pass

    s_id = s_id or f"sess-{int(request.state._state.get('time', 0) if hasattr(request.state, '_state') else 1000)}"
    c_id = c_id or "+919876540000"

    session = session_manager.get_or_create_session(s_id, c_id)
    session.add_history("assistant", GREETING_TEXT)

    logger.info(f"Started Asterisk voice session: {s_id} for {c_id}")

    accept_header = request.headers.get("accept", "").lower()
    if "application/json" in accept_header:
        return {
            "success": True,
            "session_id": s_id,
            "caller_id": c_id,
            "greeting": GREETING_TEXT,
            "action": "RECORD_CALLER"
        }

    # Return binary WAV audio for Asterisk Playback() / Background()
    audio_wav = await audio_service.synthesize(GREETING_TEXT)
    return Response(
        content=audio_wav,
        media_type="audio/wav",
        headers={"X-Voice-Session": s_id, "X-Voice-Action": "RECORD_CALLER"}
    )

@router.post("/turn")
async def voice_process_turn(
    request: Request,
    db: Session = Depends(get_db)
):
    """Processes caller utterance from Asterisk (via Whisper STT), executes Namma AI, and returns TTS audio."""
    content_type = request.headers.get("content-type", "").lower()
    
    session_id = "default-session"
    caller_id = "+919876540000"
    speech_text = None
    audio_bytes = None

    if "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        session_id = form.get("session_id", session_id)
        caller_id = form.get("caller_id", caller_id)
        speech_text = form.get("speech_text") or form.get("SpeechResult")
        
        audio_file = form.get("audio")
        if audio_file and hasattr(audio_file, "read"):
            audio_bytes = await audio_file.read()
    elif "application/json" in content_type:
        payload = await request.json()
        session_id = payload.get("session_id", session_id)
        caller_id = payload.get("caller_id", caller_id)
        speech_text = payload.get("speech_text") or payload.get("SpeechResult")

    # 1. Transcribe audio via Faster-Whisper STT if audio bytes were sent
    if audio_bytes and not speech_text:
        speech_text = await audio_service.transcribe(audio_bytes)

    speech_text = (speech_text or "").strip()
    logger.info(f"Processing voice turn for session {session_id} ({caller_id}): '{speech_text}'")

    # Ensure session exists
    session = session_manager.get_or_create_session(session_id, caller_id)

    # 2. Advance conversational state & execute Namma AI reasoning
    result = session_manager.process_turn(session_id, speech_text, db)
    reply_text = result["reply_text"]
    action = result["action"]
    complaint_id = result.get("complaint_id")

    # 3. Check if caller or test requested JSON response
    accept_header = request.headers.get("accept", "").lower()
    if "application/json" in accept_header or (not audio_bytes and "application/json" in content_type):
        return {
            "success": True,
            "session_id": session_id,
            "transcript": speech_text,
            "reply_text": reply_text,
            "complaint_id": complaint_id,
            "state": result["state"],
            "action": action
        }

    # 4. Synthesize reply text into WAV audio using Piper TTS for Asterisk
    wav_response = await audio_service.synthesize(reply_text)
    return Response(
        content=wav_response,
        media_type="audio/wav",
        headers={
            "X-Voice-Session": session_id,
            "X-Voice-Action": action,
            "X-Complaint-Id": complaint_id or ""
        }
    )

@router.post("/session/end")
async def voice_session_end(
    request: Request,
    db: Session = Depends(get_db)
):
    """Asterisk Hangup Handler callback to clean up call state and log conversation."""
    session_id = None
    content_type = request.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        try:
            body = await request.json()
            session_id = body.get("session_id")
        except Exception:
            pass
    elif "application/x-www-form-urlencoded" in content_type:
        try:
            form = await request.form()
            session_id = form.get("session_id")
        except Exception:
            pass

    session_id = session_id or request.query_params.get("session_id", "default-session")
    session = session_manager.end_session(session_id, db)

    return {
        "success": True,
        "session_id": session_id,
        "status": "terminated",
        "turns": session.turn_count if session else 0,
        "complaint_id": session.complaint_id if session else None
    }
