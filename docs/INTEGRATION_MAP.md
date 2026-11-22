# Namma AI — Comprehensive Integration & Architecture Map

> **Analysis & Integration Blueprint for Twilio Voice, Twilio STT/TTS, LLM, FastAPI, Supabase, n8n, WhatsApp, and Vision AI**  
> *Generated after static code inspection of all backend routes, services, schemas, models, frontend components, PRD, and Requirements.*  
> **Rule Adherence:** No project files have been modified or rewritten. This document serves as the exact blueprint for connecting all services.

---

# 1. Current Architecture

The actual architecture discovered in the existing codebase is a **modular, monolithic FastAPI backend** paired with a **Next.js 14 App Router frontend** and an extensible **AI & Telephony service layer**.

```text
                                  CITIZEN / USER
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 │ (Phone Call)          │ (Web Portal)          │ (WhatsApp)
                 ▼                       ▼                       ▼
           Twilio Voice            Next.js Frontend        Twilio WhatsApp
           (Webhook)               (Port 3000)             (Webhook)
                 │                       │                       │
                 ▼                       ▼                       ▼
     POST /api/twilio/voice      POST /api/complaints    POST /api/whatsapp/webhook
                 │                       │                       │
                 └───────────────────────┼───────────────────────┘
                                         ▼
                                  FastAPI Backend
                                    (Port 8000)
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
           AI Intelligence Layer                      Complaint Engine
        (backend/services/ai/)                 (backend/services/complaint_service.py)
                    │                                         │
       ┌────────────┼────────────┐               ┌────────────┼────────────┐
       ▼            ▼            ▼               ▼            ▼            ▼
  Gemini 1.5    Vision AI    Mock Fallback   Geocoding   Clustering    SLA Engine
  (LLM Parser) (Auditor)     (Deterministic) (Location)  (INC-xxx)    (Deadlines)
       │            │            │               │            │            │
       └────────────┼────────────┘               └────────────┼────────────┘
                    │                                         │
                    └────────────────────┬────────────────────┘
                                         ▼
                             Data & Storage Tier
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
         SQLAlchemy Models                               Storage Service
     (backend/models/entities.py)                  (backend/services/storage.py)
                 │                                               │
         DATABASE_URL                                   STORAGE_PROVIDER
    (SQLite local / Supabase PG)                    (Local ./uploads / Supabase Bucket)
```

### Discovered Communication Topology:
1. **Citizen Phone Intake:** Citizen calls Twilio number → Twilio issues HTTP POST to FastAPI `/api/twilio/voice` → returns TwiML with Amazon Polly TTS → collects voice statement via `<Gather input="speech">` (Twilio STT) → posts transcript to `/api/twilio/voice/process` → LLM classifies and structures complaint → Complaint saved to DB → Dispatches WhatsApp evidence request to caller.
2. **Citizen Web Intake:** Citizen visits `http://localhost:3000/report` → submits form with optional photo → `POST /api/complaints` → AI categorizes and geocodes → Evidence uploaded to `POST /api/complaints/{id}/evidence`.
3. **Citizen WhatsApp Intake & Evidence:** Citizen replies on WhatsApp → Twilio sends webhook to `/api/whatsapp/webhook` → Vision AI analyzes uploaded media → Evidence saved to DB.
4. **Officer Command Center:** Officers access `http://localhost:3000/dashboard` → inspect incidents, spatial map, and clusters → update status → submit resolution notes with "after-repair" proof photo at `POST /api/complaints/{id}/resolve` → Vision AI verifies before/after repair images.
5. **Closed-Loop Citizen Verification:** Backend dispatches WhatsApp verification prompt ("1: YES, FIXED / 2: NO, STILL EXISTS") → citizen response at `/api/whatsapp/webhook` or `/api/complaints/{id}/verify` either finalizes complaint to `RESOLVED` or triggers `REOPENED` and escalates to department supervisor.

---

# 2. Twilio Voice Integration

### Configuration & Placement
- **Twilio Phone Number Configuration:** Stored in `.env` as `TWILIO_PHONE_NUMBER` and accessed in `backend/core/config.py` (`settings.TWILIO_PHONE_NUMBER`).
- **Twilio Console Settings Required:**
  - Navigate to: **Twilio Console → Phone Numbers → Manage → Active Numbers** → Click the purchased number.
  - Under **Voice Configuration**:
    - **A CALL COMES IN:** Select `Webhook`
    - **URL:** `https://<YOUR-PUBLIC-DOMAIN-OR-NGROK>/api/twilio/voice`
    - **HTTP Method:** `POST`
  - Under **Call Status Changes**:
    - **Status Callback URL:** `https://<YOUR-PUBLIC-DOMAIN-OR-NGROK>/api/twilio/voice/status` (Optional)
    - **Method:** `POST`

### Endpoint & Flow Details
- **Exact Webhook URL:** `https://<DOMAIN>/api/twilio/voice`
- **Backend File:** [`backend/api/twilio_voice.py`](file:///D:/agy/rotaract/backend/api/twilio_voice.py)
- **Exact Function:** `voice_inbound(request: Request)`
- **HTTP Method:** `POST` (also accepts `GET`)
- **Expected Twilio Request:**
  Form URL-encoded payload including:
  `CallSid`, `From` (caller phone), `To` (Twilio number), `CallStatus` (`ringing`), `Direction` (`inbound`).
- **Expected Response:** `Response(content=xml, media_type="application/xml")` containing TwiML:
  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <Response>
      <Say voice="Polly.Aditi" language="en-IN">
          Namaskara. Welcome to Namma A I Civic Grievance Helpline.
          Please state the problem you would like to report and mention the landmark or location.
      </Say>
      <Gather input="speech" action="/api/twilio/voice/process" method="POST" timeout="4" speechTimeout="auto">
          <Say voice="Polly.Aditi" language="en-IN">We are listening.</Say>
      </Gather>
      <Say voice="Polly.Aditi" language="en-IN">We did not receive your statement. Please call back. Goodbye.</Say>
  </Response>
  ```
- **How the Conversation Starts:** Caller hears Amazon Polly's Indian English voice (`Polly.Aditi`) greeting them, followed by an immediate voice prompt.
- **How Speech is Collected:** `<Gather input="speech">` opens the audio stream for up to 4 seconds of silence or auto-detection of completed sentence.
- **How the Transcript Reaches the Backend:** Twilio STT transcribes the speech and posts the result to `action="/api/twilio/voice/process"`.
- **How the Backend Sends the Next Response:**
  - `voice_process_speech` in `backend/api/twilio_voice.py` receives `SpeechResult` and caller `From`.
  - Runs `ai_service.analyze_complaint(speech_result)`.
  - If landmark/location is missing: Returns follow-up `<Gather action="/api/twilio/voice/process-followup?context={safe_category}">` asking for landmark.
  - If complete: Calls `complaint_service.create_complaint(...)`, spells out the generated ID (`N M A - 1 0 2 9 3`), informs the caller that a WhatsApp photo link was sent, and terminates.
- **How the Call Ends:** Twilio reaches the end of the `<Response>` without another `<Gather>` or `<Dial>`, playing the goodbye message and cleanly hanging up.
- **Where Call SID is Stored:** Currently received in `form_data.get("CallSid")` inside `voice_process_speech`. It is logged in memory. *To persist it, add a `twilio_call_sid = Column(String(50), nullable=True)` to `Complaint` in `backend/models/entities.py`.*

---

# 3. Speech-to-Text (STT)

### Analysis of Current STT
- **Current STT Provider:** **Twilio Native STT** via `<Gather input="speech">`.
- **Configuration Mechanism:** Handled declaratively in TwiML inside `backend/api/twilio_voice.py`.

```text
Citizen speaks into phone
       ↓
Twilio Telephony Gateway
       ↓
Twilio Automated Speech Recognition (ASR / STT engine)
       ↓
HTTP POST with application/x-www-form-urlencoded
       ↓
FastAPI: POST /api/twilio/voice/process
       ↓
request.form().get("SpeechResult")
```

### Exact Files & Endpoints
- **Source Config:** `backend/api/twilio_voice.py`
  - Tag: `<Gather input="speech" action="/api/twilio/voice/process" method="POST" timeout="4" speechTimeout="auto">`
  - Language: Inherits Indian English from `<Say language="en-IN">` context.
- **Consumer Endpoint:** `POST /api/twilio/voice/process`
  - Param: `SpeechResult` (string)
  - Param: `Confidence` (float, e.g. `0.91`)
  - Caller Phone: `From` (string, e.g. `+919876543210`)

---

# 4. Text-to-Speech (TTS)

### Analysis of Current TTS
- **Current TTS Provider:** **Twilio Polly Neural/Standard TTS Engine**.
- **Exact Code File:** [`backend/api/twilio_voice.py`](file:///D:/agy/rotaract/backend/api/twilio_voice.py)
- **Functions:** `voice_inbound()` and `voice_process_speech()`
- **Voice Configuration:** `voice="Polly.Aditi"`
- **Language Configuration:** `language="en-IN"` (Indian English accent with natural local cadence)
- **Where Final Confirmation is Generated:**
  In `voice_process_speech` (lines 80-92):
  ```python
  spoken_id = " ".join(list(complaint.id))  # Spells: "N M A - 1 0 2 9 3"
  safe_spoken_id = xml_escape(spoken_id)
  safe_category = xml_escape(complaint.category.replace('_', ' '))
  safe_priority = xml_escape(complaint.priority)
  xml = f"""<?xml version="1.0" encoding="UTF-8"?>
  <Response>
      <Say voice="Polly.Aditi" language="en-IN">
          Thank you. Your complaint has been registered with reference ID {safe_spoken_id}.
          It has been categorized as {safe_category} with priority {safe_priority}.
          A WhatsApp message has been sent to your phone where you can upload photos of the defect.
          Thank you for helping keep Bengaluru safe. Goodbye.
      </Say>
  </Response>"""
  ```

---

# 5. LLM

### Current LLM Engine Identification
- **Configured Providers:**
  - Primary: **Google Gemini** (`gemini-1.5-flash`) via official `google-genai` SDK.
  - Fallback: **Deterministic Mock Engine** (`MockAIService`) with regex entities and keyword scoring.
- **Where the API Key is Read:** `backend/core/config.py` (line 32: `LLM_API_KEY: str = Field(default="")`). Loaded from `.env`.
- **Where the Model is Called:** `backend/services/ai/gemini_service.py` (lines 33-37 in `analyze_complaint`).
- **Service Layer Files:**
  - [`backend/services/ai/base.py`](file:///D:/agy/rotaract/backend/services/ai/base.py): Abstract contract `BaseAIService`.
  - [`backend/services/ai/gemini_service.py`](file:///D:/agy/rotaract/backend/services/ai/gemini_service.py): Google GenAI implementation with JSON response mode.
  - [`backend/services/ai/mock_service.py`](file:///D:/agy/rotaract/backend/services/ai/mock_service.py): Keyword & regex rules engine.
  - [`backend/services/ai/prompts.py`](file:///D:/agy/rotaract/backend/services/ai/prompts.py): System prompts with JSON schema contracts.
  - [`backend/schemas/ai.py`](file:///D:/agy/rotaract/backend/schemas/ai.py): Pydantic v2 schemas validating all AI output.

### Flow: Citizen Speech → Structured Complaint
```text
Citizen Speech Transcript ("There is a deep pothole near BMSIT gate...")
       ↓
GeminiAIService.analyze_complaint(text, location_hint)
       ↓
Prompt sent to gemini-1.5-flash with config={"response_mime_type": "application/json"}
       ↓
Gemini returns structured JSON
       ↓
Pydantic Validation: AIComplaintAnalysis.model_validate(data)
       ↓
Validated Python Object returned to ComplaintService
```

### Expected Pydantic Schema (`AIComplaintAnalysis`):
```json
{
  "category": "ROAD_DAMAGE",
  "department": "ROADS",
  "severity": "HIGH",
  "priority": "HIGH",
  "priority_score": 88,
  "summary": "Road Pothole Hazard reported near BMSIT gate",
  "extracted_location": "BMSIT gate",
  "landmark": "BMSIT gate",
  "safety_hazard": true,
  "missing_info": [],
  "confidence": 0.95,
  "ai_provider": "gemini"
}
```

### Error Handling:
If `LLM_API_KEY` is missing, quota is exceeded, or invalid JSON is returned, `GeminiAIService` catches the exception and immediately invokes `MockAIService`. The request never fails.

---

# 6. Complaint Creation

### Logic Breakdown
- **APIs Creating Complaints:**
  1. `POST /api/complaints` in [`backend/api/complaints.py`](file:///D:/agy/rotaract/backend/api/complaints.py) (Web channel).
  2. `POST /api/twilio/voice/process` in [`backend/api/twilio_voice.py`](file:///D:/agy/rotaract/backend/api/twilio_voice.py) (Voice channel).
  3. `POST /api/demo/run-full-scenario` in [`backend/api/demo.py`](file:///D:/agy/rotaract/backend/api/demo.py) (Demo simulation).
- **Service Function:** `complaint_service.create_complaint(db: Session, payload: ComplaintCreate)` in [`backend/services/complaint_service.py`](file:///D:/agy/rotaract/backend/services/complaint_service.py).
- **Database Table:** `complaints` table (defined in [`backend/models/entities.py`](file:///D:/agy/rotaract/backend/models/entities.py)).
- **How Complaint ID is Generated:**
  Function `generate_complaint_id(db: Session)` counts existing records and formats a sequential ID:
  `NMA-{10000 + count + 1}` (e.g., `NMA-10001`, `NMA-10293`). Collisions are prevented via a `while` check.
- **Required Fields:**
  - `description`: Text statement from citizen.
  - `citizen_phone`: Mobile number of reporting citizen.
- **How Phone Number is Associated:**
  1. Lookup in `users` table: `db.query(User).filter(User.phone == payload.citizen_phone).first()`.
  2. If missing, auto-creates: `User(phone=payload.citizen_phone, name=payload.citizen_name, role="CITIZEN")`.
  3. Links foreign key `Complaint.citizen_id = citizen.id`.
- **How Twilio Call SID is Associated:**
  Currently extracted from `form_data.get("CallSid")` in voice intake. Currently stored in log files and can be attached to `ComplaintEvent.details`.

---

# 7. Twilio → Backend Webhooks

### Complete Webhook Matrix

| # | Webhook Route | Method | Backend File | Function | Purpose | Request Data | Response | Database Changes |
|---|---|---|---|---|---|---|---|---|
| **1** | `/api/twilio/voice` | `POST` / `GET` | `backend/api/twilio_voice.py` | `voice_inbound` | Inbound voice call entry point | `CallSid`, `From`, `To`, `CallStatus` | TwiML XML with `<Gather>` | None |
| **2** | `/api/twilio/voice/process` | `POST` | `backend/api/twilio_voice.py` | `voice_process_speech` | Speech transcript processing & complaint creation | `SpeechResult`, `From`, `CallSid` | TwiML XML with spoken ID & confirmation | Inserts `users`, `complaints`, `complaint_events`, `incident_clusters`, `notifications` |
| **3** | `/api/whatsapp/webhook` | `POST` | `backend/api/whatsapp.py` | `whatsapp_webhook` | Citizen WhatsApp messages, photos & YES/NO verification | `From`, `Body`, `NumMedia`, `MediaUrl0`, `MediaContentType0` | TwiML XML `<Message>...</Message>` | Adds `evidence`, updates `complaint.status` to `RESOLVED` or `REOPENED`, logs `complaint_events` |

### Missing Webhook Endpoints Identified
1. **`POST /api/twilio/voice/process-followup`**:
   - In `backend/api/twilio_voice.py` line 61, the TwiML references `<Gather action="/api/twilio/voice/process-followup?context={safe_category}">`.
   - *Finding:* The route handler for this followup endpoint is currently missing from `twilio_voice.py`.
2. **`POST /api/twilio/voice/status`**:
   - Optional call status callback to track call duration, ringing, and hangup.
3. **`POST /api/whatsapp/status`**:
   - Optional message delivery receipt webhook (`sent`, `delivered`, `read`).

---

# 8. n8n Integration

### Connection Strategy: Backend ↔ n8n ↔ WhatsApp
To enable flexible messaging workflows without bloating FastAPI, n8n acts as the **Visual Workflow Orchestrator** for WhatsApp and multi-channel alerts.

```text
                     Namma AI (FastAPI)
                       │             ▲
        HTTP Webhook   │             │  HTTP API Call
    (Outbound events)  │             │  (Evidence & Verification)
                       ▼             │
                  ┌──────────────────────┐
                  │      n8n Server      │
                  │  (Workflow Engine)   │
                  └──────────────────────┘
                       │             ▲
       Send WhatsApp   │             │  Inbound Webhook
                       ▼             │
                      Twilio / WhatsApp
```

### Outbound Webhook from FastAPI → n8n
When events happen in FastAPI, the backend dispatches a webhook to n8n:
- **Target n8n Webhook URL:** `https://<YOUR-N8N-DOMAIN>/webhook/namma-events`
- **HTTP Method:** `POST`
- **Authentication:** Header `X-N8N-Webhook-Secret: <SECRET_KEY>`
- **Dispatched JSON Payload:**
  ```json
  {
    "event": "COMPLAINT_REGISTERED",
    "complaint_id": "NMA-10293",
    "citizen_phone": "+919876543210",
    "citizen_name": "Ramesh Kumar",
    "category": "ROAD_DAMAGE",
    "priority": "HIGH",
    "summary": "Deep pothole near BMSIT gate",
    "location": "Doddaballapur Road, Yelahanka",
    "timestamp": "2026-10-04T15:00:00Z"
  }
  ```
- **What Triggers It:**
  - Complaint registration in `complaint_service.py`.
  - Officer submits resolution in `resolution_service.py` (`event: "RESOLUTION_VERIFICATION_REQUEST"`).
  - SLA breach in `sla_service.py` (`event: "SLA_BREACH_ALERT"`).
- **What n8n Does:**
  1. Receives webhook payload.
  2. Formats WhatsApp template.
  3. Sends interactive message to citizen or supervisor via Twilio or Meta WhatsApp node.
  4. Returns `{"status": "queued", "message_id": "..."}` back to FastAPI.

---

# 9. WhatsApp Flow

```text
[Citizen reports issue via Phone/Web]
                 ↓
[FastAPI creates Complaint #NMA-10293]
                 ↓
[FastAPI sends Outbound Webhook to n8n]
                 ↓
[n8n Workflow 1: Registration & Evidence Request]
                 ↓
  WhatsApp message sent to Citizen:
  "🏛️ Namma AI: Your complaint #NMA-10293 has been registered.
   📸 Please reply with photos or videos of the issue."
                 ↓
[Citizen takes photo and replies on WhatsApp]
                 ↓
[Twilio / WhatsApp forwards to n8n Workflow 2]
                 ↓
[n8n downloads media & forwards to FastAPI POST /api/complaints/NMA-10293/evidence]
                 ↓
[FastAPI Vision AI verifies photo -> Saves to Evidence table -> Promotes status]
                 ↓
[Municipal Crew resolves issue -> Officer uploads After Photo on Dashboard]
                 ↓
[FastAPI sends Outbound Webhook to n8n: "RESOLUTION_VERIFICATION_REQUEST"]
                 ↓
[n8n Workflow 3: Resolution Prompt]
                 ↓
  WhatsApp message sent to Citizen:
  "🔔 Namma AI: Case #NMA-10293 is marked fixed.
   Is the problem actually resolved?
   1️⃣ — YES, ISSUE FIXED
   2️⃣ — NO, STILL EXISTS"
                 ↓
   ┌───────────────────────────┴───────────────────────────┐
   ▼ (Citizen replies "1")                                 ▼ (Citizen replies "2")
[n8n calls POST /api/complaints/{id}/verify]             [n8n calls POST /api/complaints/{id}/verify]
   body: {"is_fixed": true}                                body: {"is_fixed": false, "notes": "Not fixed"}
                 ↓                                                       ↓
[Complaint status: RESOLVED]                             [Complaint status: REOPENED & ESCALATED]
[Citizen gets thank-you note]                            [Supervisor notified immediately]
```

### Where Each Action is Triggered in the Code
- **Registration & Evidence Request Trigger:** `complaint_service.py` line 144 (`twilio_service.send_evidence_request`).
- **Evidence Reception:** `backend/api/whatsapp.py` line 89 (`if num_media > 0:`).
- **Resolution Verification Trigger:** `backend/services/resolution_service.py` line 108 (`twilio_service.send_verification_request`).
- **Citizen YES/NO Handling:** `backend/api/whatsapp.py` lines 55-87 and `backend/api/complaints.py` lines 162-210 (`POST /api/complaints/{id}/verify`).

---

# 10. Evidence Upload

### Travel Path
```text
Citizen WhatsApp
       ↓
Twilio WhatsApp Gateway (generates public media URL)
       ↓
n8n Inbound Webhook (receives MediaUrl0)
       ↓
n8n HTTP Request node: downloads media binary
       ↓
POST /api/complaints/{id}/evidence (multipart/form-data)
       ↓
FastAPI Security Validation (validate_upload_file in security.py)
       ↓
Storage Service (saves locally or uploads to Supabase Storage bucket)
       ↓
Vision AI Analysis (analyzes image and returns JSON defect analysis)
       ↓
Database Record created in `evidence` table linked to `complaint_id`
```

### Endpoint Details
- **Endpoint:** `POST /api/complaints/{complaint_id}/evidence`
- **File:** [`backend/api/complaints.py`](file:///D:/agy/rotaract/backend/api/complaints.py)
- **Data Sent:** `multipart/form-data` with:
  - `file`: binary image
  - `evidence_type`: `"CITIZEN_INITIAL"` or `"CITIZEN_FOLLOWUP"`
- **Storage Destination:**
  - Local mode: Saves to `./uploads/<uuid>.jpg`
  - Supabase mode: Uploads to bucket `namma-evidence` via Supabase Storage API.
- **Database Record Created:**
  ```python
  Evidence(
      id=generate_uuid(),
      complaint_id=complaint_id,
      evidence_type="CITIZEN_FOLLOWUP",
      media_url="/uploads/0170af07869d.jpg",
      media_type="IMAGE",
      ai_analysis={
          "issue_detected": True,
          "issue_type": "POTHOLE",
          "severity": "HIGH",
          "visual_description": "Large crater with exposed aggregates in active carriage lane."
      },
      ai_confidence=0.94,
      is_valid_evidence=True
  )
  ```

---

# 11. Vision AI

### Current Integration Details
- **Files:**
  - [`backend/services/ai/vision.py`](file:///D:/agy/rotaract/backend/services/ai/vision.py) (`VisionAIService`)
  - [`backend/services/ai/gemini_service.py`](file:///D:/agy/rotaract/backend/services/ai/gemini_service.py) (`analyze_evidence`)
  - [`backend/services/ai/mock_service.py`](file:///D:/agy/rotaract/backend/services/ai/mock_service.py) (`analyze_evidence`)
- **Model:** `gemini-1.5-flash` (or deterministic mock if API key is absent)
- **Input:** Image binary or local file path + complaint description.
- **Output:** Pydantic object `AIEvidenceAnalysis`:
  - `issue_detected`: bool
  - `issue_type`: `"POTHOLE" | "GARBAGE_DUMP" | "DRAINAGE_CLOG" | "SEWAGE_LEAK" | "WATER_BURST" | "BROKEN_LIGHT" | "TREE_FALL" | "OTHER"`
  - `matches_complaint`: bool
  - `confidence`: float (0.0 to 1.0)
  - `severity`: `"LOW" | "MEDIUM" | "HIGH" | "CRITICAL"`
  - `visual_description`: string
  - `quality_score`: float
- **Database Destination:** Saved directly in `evidence.ai_analysis` (JSON column) and `evidence.ai_confidence` (Float column).

---

# 12. Resolution Verification

### Before/After Verification Logic
- **File:** [`backend/services/resolution_service.py`](file:///D:/agy/rotaract/backend/services/resolution_service.py) (function: `submit_resolution`)
- **API Endpoint:** `POST /api/complaints/{complaint_id}/resolve` in [`backend/api/complaints.py`](file:///D:/agy/rotaract/backend/api/complaints.py)
- **Input:**
  - `officer_notes`: Text explanation of repair work.
  - `after_media_file`: Uploaded photo of completed repair.
- **Comparison Flow:**
  1. Resolves `before_image` from initial citizen evidence (`complaint.evidence[0].media_url`).
  2. Saves `after_media_file` via `storage_service.save_upload_file(...)`.
  3. Calls `ai_service.verify_resolution(before_image, after_image, description)`.
  4. Returns `AIResolutionVerification`:
     - `resolution_likely_complete`: boolean (`true`)
     - `confidence`: float (`0.92`)
     - `notes`: `"Surfacing is restored, compacted and uniform with adjacent road plane."`
     - `audit_flag`: `"PASSED"` (or `"SUSPICIOUS"` / `"INCOMPLETE"`)
  5. Inserts record into `resolutions` table.
  6. Changes `complaint.status` to `"CITIZEN_VERIFICATION"`.
  7. Triggers n8n / Twilio WhatsApp verification prompt to citizen.

---

# 13. Citizen Verification

### Closed-Loop Decision Engine
- **WhatsApp Prompt Sent:**
  ```text
  🔔 Namma AI Resolution Confirmation
  Your complaint #NMA-10293 has been marked as resolved by the municipal crew.
  Is the problem actually fixed?
  Reply with:
  1️⃣ — YES, ISSUE FIXED
  2️⃣ — NO, STILL EXISTS
  ```

### Handling YES:
- **Triggered via:**
  - Citizen WhatsApp reply: `"1"`, `"YES"`, `"yes"`, `"Fixed"` in `backend/api/whatsapp.py`
  - Or web call: `POST /api/complaints/{id}/verify` with `{"is_fixed": true}`
- **Execution:**
  - `complaint.status = "RESOLVED"`
  - `complaint.resolved_at = datetime.now(timezone.utc)`
  - `resolution.citizen_feedback = "CONFIRMED_FIXED"`
  - `ComplaintEvent` logged with `event_type="RESOLVED"` and `actor_type="CITIZEN"`
  - Confirmation response sent back to citizen.

### Handling NO:
- **Triggered via:**
  - Citizen WhatsApp reply: `"2"`, `"NO"`, `"no"`, `"Not fixed"`, `"still exists"`
  - Or web call: `POST /api/complaints/{id}/verify` with `{"is_fixed": false, "citizen_notes": "..."}`
- **Execution:**
  - `complaint.status = "REOPENED"`
  - `complaint.reopen_count += 1`
  - `resolution.citizen_feedback = "REJECTED"`
  - `ComplaintEvent` logged with `event_type="REOPENED"`
  - Automatic escalation event `ESCALATED` dispatched to department supervisor.
  - Alert notification logged and sent to supervisor's phone.

---

# 14. Supabase

The platform uses SQLAlchemy ORM which connects to PostgreSQL (Supabase) via standard connection strings.

### Supabase Relational Tables (`backend/models/entities.py`)

| Table Name | Purpose | Key Columns | Written By | Read By |
|---|---|---|---|---|
| **`users`** | Citizen & officer directory | `id`, `phone`, `name`, `role`, `department_id`, `created_at` | `complaint_service`, `auth.py`, `init_db.py` | `auth.py`, `complaint_service`, `sla_service` |
| **`departments`** | Municipal department master | `id`, `name`, `description`, `default_sla_hours` | `init_db.py` | `complaints.py`, `dashboard.py` |
| **`complaint_categories`** | Category catalog | `id`, `name`, `department_id`, `default_priority` | `init_db.py` | `ai_service`, `complaints.py` |
| **`complaints`** | Central grievance entity | `id`, `citizen_id`, `department_id`, `cluster_id`, `category`, `raw_description`, `ai_summary`, `severity`, `priority`, `priority_score`, `location_text`, `latitude`, `longitude`, `status`, `sla_deadline`, `is_sla_breached`, `channel` | `complaint_service`, `resolution_service`, `sla_service` | `complaints.py`, `dashboard.py`, `location.py`, `track/page.tsx` |
| **`evidence`** | Photo and video files | `id`, `complaint_id`, `evidence_type`, `media_url`, `media_type`, `ai_analysis`, `ai_confidence`, `is_valid_evidence`, `uploaded_at` | `complaint_service.add_evidence`, `whatsapp.py` | `complaints.py`, `track/page.tsx`, `dashboard/[id]/page.tsx` |
| **`resolutions`** | Officer repair proofs | `id`, `complaint_id`, `officer_id`, `officer_notes`, `after_media_url`, `ai_verification`, `ai_verified`, `citizen_feedback`, `created_at` | `resolution_service.submit_resolution` | `complaints.py`, `dashboard/[id]/page.tsx` |
| **`complaint_events`** | Immutable audit log | `id`, `complaint_id`, `event_type`, `old_status`, `new_status`, `actor_type`, `details`, `created_at` | All services on status change | `complaints.py`, `dashboard/[id]/page.tsx` |
| **`incident_clusters`** | Duplicate grouping | `id`, `title`, `category`, `center_latitude`, `center_longitude`, `status`, `report_count`, `first_reported_at`, `last_reported_at` | `clustering_service.py` | `clusters.py`, `dashboard/page.tsx` |
| **`sla_rules`** | Configured SLA targets | `id`, `department_id`, `priority`, `max_resolution_hours`, `warning_threshold_hours` | `init_db.py` | `sla_service.py`, `sla.py` |
| **`notifications`** | Outbound dispatch log | `id`, `complaint_id`, `recipient_phone`, `channel`, `message`, `status`, `sent_at` | `twilio_service.py`, `notification_service.py` | `notifications.py` |

### Supabase Storage Bucket
- **Bucket Name:** `namma-evidence`
- **Access Level:** Public read (for web display of photos), authenticated write via Service Role Key.
- **Path Structure:**
  - Citizen evidence: `evidence/{complaint_id}/initial_{uuid}.jpg`
  - Officer resolution: `resolutions/{complaint_id}/repair_{uuid}.jpg`

---

# 15. Environment Variables

| Variable | Used By | Where Read | Purpose |
|---|---|---|---|
| `ENVIRONMENT` | Backend Runtime | `backend/core/config.py` | Sets environment mode (`development`, `production`). |
| `PORT` | Uvicorn Server | `backend/core/config.py` | Port number for FastAPI backend (default: `8000`). |
| `HOST` | Uvicorn Server | `backend/core/config.py` | Host binding interface (default: `0.0.0.0`). |
| `SECRET_KEY` | JWT Auth | `backend/core/security.py` | Secret key used to sign and verify officer access tokens. |
| `CORS_ORIGINS` | FastAPI Middleware | `backend/main.py` | Comma-delimited list of allowed frontend origins (e.g. `http://localhost:3000`). |
| `DATABASE_URL` | SQLAlchemy Engine | `backend/core/database.py` | SQLite or PostgreSQL/Supabase database connection URI. |
| `SUPABASE_URL` | Supabase Client | `backend/core/config.py` | Base REST endpoint for Supabase project (`https://<REF>.supabase.co`). |
| `SUPABASE_ANON_KEY` | Frontend / Supabase Client | `backend/core/config.py` | Public anonymous key for client operations. |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend Storage Service | `backend/core/config.py` | Privileged secret key to upload files to Supabase Storage. |
| `STORAGE_PROVIDER` | Storage Subsystem | `backend/services/storage.py` | Storage driver (`local` or `supabase`). |
| `STORAGE_LOCAL_DIR` | Storage Subsystem | `backend/core/config.py` | Directory path for local uploads (default: `./uploads`). |
| `STORAGE_BUCKET_NAME` | Storage Subsystem | `backend/core/config.py` | Supabase object storage bucket name (`namma-evidence`). |
| `LLM_PROVIDER` | AI Subsystem | `backend/services/ai/__init__.py`| Selected AI engine (`gemini` or `mock`). |
| `LLM_API_KEY` | AI Subsystem | `backend/services/ai/gemini_service.py` | Google AI Studio Gemini API key. |
| `LLM_MODEL` | AI Subsystem | `backend/services/ai/gemini_service.py` | Foundation model name (default: `gemini-1.5-flash`). |
| `TWILIO_ACCOUNT_SID` | Twilio Integration | `backend/integrations/twilio_service.py` | Twilio Account SID identifier (`AC...`). |
| `TWILIO_AUTH_TOKEN` | Twilio Integration | `backend/integrations/twilio_service.py` | Twilio Auth Token for REST API authentication. |
| `TWILIO_PHONE_NUMBER` | Twilio Voice | `backend/core/config.py` | Dedicated phone number for incoming citizen calls. |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp | `backend/integrations/twilio_service.py` | Twilio WhatsApp sender (e.g. `whatsapp:+14155238886`). |
| `TWILIO_WEBHOOK_BASE_URL`| Twilio Callbacks | `backend/core/config.py` | Public domain or ngrok tunnel URL for incoming webhooks. |
| `N8N_WEBHOOK_URL` | n8n Dispatcher | `backend/core/config.py` (Planned) | Outbound webhook URL to trigger n8n workflows. |
| `N8N_WEBHOOK_SECRET` | n8n Middleware | `backend/core/config.py` (Planned) | Shared secret validating communication with n8n. |
| `NEXT_PUBLIC_API_BASE_URL` | Next.js Frontend | `frontend/src/app/...` | Backend API base URL (`http://localhost:8000/api`). |

---

# 16. External Console Configuration

### 1. TWILIO
1. **Phone Number:**
   - Go to **Console → Phone Numbers → Manage → Active Numbers**.
   - Select your number.
2. **Voice Webhook:**
   - Under "Voice & Fax", set "A CALL COMES IN" to `Webhook`.
   - URL: `https://<YOUR-NGROK-OR-DOMAIN>/api/twilio/voice`
   - Method: `POST`
3. **WhatsApp Sandbox / Business Number:**
   - Go to **Messaging → Try it out → Send a WhatsApp message**.
   - Under "Sandbox Configuration":
   - "WHEN A MESSAGE COMES IN": `https://<YOUR-NGROK-OR-DOMAIN>/api/whatsapp/webhook`
   - Method: `POST`
4. **Speech-to-Text & Text-to-Speech:**
   - No external plugin purchase required. Twilio executes STT via `<Gather input="speech">` and Indian English TTS via `<Say voice="Polly.Aditi" language="en-IN">`.

### 2. n8n
1. **Webhook Trigger Node:**
   - Create a new workflow: `Namma AI Citizen WhatsApp Bridge`.
   - Add a `Webhook` node:
     - Method: `POST`
     - Path: `namma-events`
     - Authentication: Header Auth (`X-N8N-Webhook-Secret`)
2. **WhatsApp Node:**
   - Add a `Twilio` or `WhatsApp Business Cloud` node.
   - Map `To: {{ $json.citizen_phone }}`.
   - Message: Format using the incident summary, ID, and category.
3. **Interactive Buttons / Response Listener:**
   - Create a second Webhook node for incoming citizen WhatsApp replies (`1: YES` / `2: NO`).
   - Branch response:
     - If `1`: Call `POST https://<FASTAPI-DOMAIN>/api/complaints/{{ $json.complaint_id }}/verify` with `{"is_fixed": true}`.
     - If `2`: Call `POST https://<FASTAPI-DOMAIN>/api/complaints/{{ $json.complaint_id }}/verify` with `{"is_fixed": false}`.

### 3. SUPABASE
1. **Database:**
   - Create a new Supabase Project.
   - Go to **Project Settings → Database → Connection string → URI**.
   - Copy connection string and paste into `.env` as `DATABASE_URL`:
     `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`
2. **Storage Bucket:**
   - Go to **Storage → New Bucket**.
   - Name: `namma-evidence`
   - Set to **Public Bucket** (toggle ON).
3. **Database Schema:**
   - Run the initialization script: `python -m backend.core.init_db`. This creates all 10 tables and seeds master departments.

### 4. LLM (Google Gemini)
1. Go to **Google AI Studio** (`aistudio.google.com`).
2. Generate an API Key.
3. In `.env`:
   ```bash
   LLM_PROVIDER=gemini
   LLM_API_KEY=AIzaSy...
   LLM_MODEL=gemini-1.5-flash
   ```

---

# 17. Complete End-to-End Flow

```text
CITIZEN (Phone)             TWILIO VOICE            FASTAPI BACKEND             GEMINI AI               SUPABASE (DB)
      │                          │                         │                         │                        │
      │── 1. Dials Helpline ────►│                         │                         │                        │
      │                          │── 2. POST /voice ──────►│                         │                        │
      │                          │◄── 3. TwiML <Gather> ───│                         │                        │
      │◄── 4. Spoken Greeting ───│                         │                         │                        │
      │── 5. Speaks Pothole ────►│                         │                         │                        │
      │                          │── 6. POST /process ────►│                         │                        │
      │                          │   (with SpeechResult)   │── 7. Parse Text ───────►│                        │
      │                          │                         │◄── 8. AI Analysis ──────│                        │
      │                          │                         │── 9. Save Complaint ────────────────────────────►│
      │                          │                         │── 10. Check Duplicates ─────────────────────────►│
      │                          │◄── 11. TwiML Confirm ───│                         │                        │
      │◄── 12. Hears Spoken ID ──│                         │                         │                        │
      │   ("N-M-A-1-0-2-9-3")    │                         │                         │                        │
```

```text
FASTAPI BACKEND                 N8N / WHATSAPP              CITIZEN (Mobile)        OFFICER DASHBOARD
      │                                │                           │                        │
      │── 13. Dispatch Evidence Prompt►│                           │                        │
      │                                │── 14. Send WhatsApp ─────►│                        │
      │                                │   "Please send photo"     │                        │
      │                                │◄── 15. Replies with Photo─│                        │
      │◄── 16. Ingests Photo Evidence ─│                           │                        │
      │    (Vision AI Inspects)        │                           │                        │
      │── 17. Updates DB with Evidence ────────────────────────────────────────────────────►│
      │                                                                                     │ (18. Displays on CAD)
      │                                                                                     │ (19. Crew Repairs)
      │                                                                                     │ (20. Submits After Photo)
      │◄── 21. POST /resolve ───────────────────────────────────────────────────────────────│
      │    (Vision AI Compares Before vs After)                                             │
      │── 22. Dispatch Verification ──►│                                                    │
      │                                │── 23. Send Prompt ───────►│                        │
      │                                │   "Is issue fixed? 1/2"   │                        │
      │                                │◄── 24. Citizen replies "2"│                        │
      │◄── 25. Status: REOPENED ───────│    ("Still exists")       │                        │
      │── 26. Escalate to Supervisor ──────────────────────────────────────────────────────►│
```

---

# 18. Missing Pieces

### ALREADY IMPLEMENTED ✅
- Next.js 14 citizen reporting page (`/report`), tracking page (`/track`), GIS map (`/map`), command center (`/dashboard`), case detail view (`/dashboard/[id]`), and interactive hackathon demo (`/demo`).
- FastAPI server with CORS, error middleware, and health diagnostics (`/health`).
- Complete SQLAlchemy entity schemas (`User`, `Department`, `Complaint`, `Evidence`, `Resolution`, `ComplaintEvent`, `SLARule`, `IncidentCluster`, `Notification`).
- AI Intelligence layer with Pydantic validation schemas (`AIComplaintAnalysis`, `AIEvidenceAnalysis`, `AIResolutionVerification`).
- High-fidelity offline deterministic engine (`MockAIService`) and live Google Gemini engine (`GeminiAIService`).
- Location service with landmark dictionary, coordinate offset generator, and Haversine distance.
- Spatio-temporal duplicate clustering creating `INC-xxx` cluster records.
- Twilio Voice inbound TwiML endpoint (`/api/twilio/voice`) and speech processor (`/api/twilio/voice/process`).
- Twilio WhatsApp webhook for photo intake and status acknowledgment (`/api/whatsapp/webhook`).
- SLA rules, deadline calculation, warning generators, and breach escalation scan (`/api/sla/check-violations`).
- 36 passing automated unit and integration tests.

### PARTIALLY IMPLEMENTED ⚠️
1. **Supabase Integration:**
   - *Current State:* SQLAlchemy connects seamlessly to any PostgreSQL / Supabase URL, but default `.env` points to `sqlite:///./namma_ai.db`.
   - *Requirement:* To use Supabase, set `DATABASE_URL` to Supabase connection string.
2. **Supabase Storage:**
   - *Current State:* Storage service (`backend/services/storage.py`) only writes to local disk `./uploads`.
   - *Requirement:* Add a storage adapter branch in `storage.py` that uploads to the Supabase `namma-evidence` bucket when `STORAGE_PROVIDER=supabase`.
3. **Twilio Media Download:**
   - *Current State:* `backend/api/whatsapp.py` reads `MediaUrl0` from Twilio, but does not fetch the binary file from Twilio CDN to store in local or Supabase storage.
   - *Requirement:* Add an HTTP fetch using `httpx` with Twilio basic auth to download the media binary and pass to `storage_service.save_upload_file(...)`.
4. **Twilio Call SID Persistence:**
   - *Current State:* `CallSid` is received in `backend/api/twilio_voice.py` but is not persisted in a dedicated column on the `complaints` table.

### MISSING ❌
1. **Voice Followup Endpoint (`POST /api/twilio/voice/process-followup`):**
   - *Current State:* `backend/api/twilio_voice.py` line 61 references `action="/api/twilio/voice/process-followup?context={safe_category}"`, but this endpoint does not exist.
   - *Requirement:* Add `@router.post("/process-followup")` to `backend/api/twilio_voice.py` to capture the caller's landmark answer and complete complaint creation.
2. **n8n Outbound Webhook Dispatcher:**
   - *Current State:* FastAPI calls `twilio_service.send_whatsapp_message` directly.
   - *Requirement:* Add an outbound webhook call to `N8N_WEBHOOK_URL` when complaints are created or resolved, enabling n8n to orchestrate WhatsApp messaging.
3. **n8n Dedicated Inbound Endpoint:**
   - *Current State:* Webhooks arrive directly from Twilio form-data.
   - *Requirement:* Add a dedicated JSON webhook endpoint (e.g., `POST /api/webhooks/n8n/verify` and `POST /api/webhooks/n8n/evidence`) with header secret validation.

### MISCONFIGURED 🔧
1. **Missing Route for Follow-up Landmark in TwiML:**
   - In `backend/api/twilio_voice.py`, line 61 specifies `action="/api/twilio/voice/process-followup"`. Calling this currently returns a 404.

### DUPLICATED 🔄
1. **Citizen Verification Logic:**
   - Handled in `backend/api/whatsapp.py` (lines 55-87) AND in `backend/api/complaints.py` (lines 162-210).
   - *Remedy:* Consolidate into a single method `resolution_service.process_citizen_verification(...)`.

### NOT REQUIRED 🚫
- Training a custom LLM from scratch.
- Complex multi-tenancy or municipal payment gateways.
- 30+ government department hierarchies (MVP intentionally focuses on the 6 core municipal departments).

---

# 19. Exact Setup Checklist

### Step 1: Twilio Console
- [ ] Log in to [console.twilio.com](https://console.twilio.com).
- [ ] Active Phone Numbers → Select phone number.
- [ ] Set **Voice Webhook URL** to `https://<YOUR-DOMAIN>/api/twilio/voice` (Method: `POST`).
- [ ] Set **WhatsApp Sandbox Webhook** to `https://<YOUR-DOMAIN>/api/whatsapp/webhook` (Method: `POST`).
- [ ] Copy `Account SID` and `Auth Token` into `.env`.

### Step 2: Supabase Console
- [ ] Log in to [supabase.com](https://supabase.com) and create project `namma-ai`.
- [ ] Go to **Project Settings → Database → Connection String → URI**.
- [ ] Copy URI and set `DATABASE_URL` in `.env`.
- [ ] Go to **Storage → Create New Bucket** → Name: `namma-evidence` → Public: `ON`.
- [ ] Copy `Project URL` and `service_role` key into `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `.env`.

### Step 3: Google Gemini API
- [ ] Log in to [aistudio.google.com](https://aistudio.google.com) and click **Get API Key**.
- [ ] Set `LLM_PROVIDER=gemini` and `LLM_API_KEY=<YOUR-API-KEY>` in `.env`.

### Step 4: n8n Workflow Configuration
- [ ] In n8n, create workflow `Namma AI Dispatcher`.
- [ ] Add `Webhook` node with path `namma-events`.
- [ ] Add `Twilio` / `WhatsApp` node mapped to citizen phone and text body.
- [ ] Add interactive reply branching (`1: Fixed` -> calls `/api/complaints/{id}/verify`).
- [ ] Set `N8N_WEBHOOK_URL` and `N8N_WEBHOOK_SECRET` in `.env`.

### Step 5: Backend & Database Initialization
- [ ] Run `python -m backend.core.init_db` to create tables and seed departments.
- [ ] Start backend: `python -m uvicorn backend.main:app --port 8000 --reload`.
- [ ] Verify health: Open `http://localhost:8000/health`.

### Step 6: Frontend Launch
- [ ] Start frontend: `npm run dev` inside `frontend/`.
- [ ] Verify dashboard: Open `http://localhost:3000/dashboard`.
- [ ] Verify demo runner: Open `http://localhost:3000/demo`.

---

# 20. DO NOT CHANGE CODE YET / IMPLEMENTATION PLAN

When you explicitly instruct me to implement the connections, the work will be executed in this exact order to prevent breaking changes:

1. **Step 1: Environment & Config Synchronization**
   - Add `N8N_WEBHOOK_URL`, `N8N_WEBHOOK_SECRET`, and Supabase storage keys to `backend/core/config.py` and `.env.example`.
2. **Step 2: Voice Followup Webhook Fix**
   - Add missing `@router.post("/process-followup")` in `backend/api/twilio_voice.py` to handle landmark clarification without 404 errors.
   - Add `twilio_call_sid` to `Complaint` model in `backend/models/entities.py`.
3. **Step 3: Twilio Media Download & Supabase Storage Adapter**
   - Implement authenticating media downloader in `backend/api/whatsapp.py` to pull media from Twilio CDN.
   - Add Supabase Storage provider branch to `backend/services/storage.py` uploading to bucket `namma-evidence`.
4. **Step 4: n8n Outbound Event Dispatcher & Inbound Webhooks**
   - Implement `backend/integrations/n8n_service.py` to dispatch lifecycle webhooks (`COMPLAINT_REGISTERED`, `EVIDENCE_REQUEST`, `RESOLUTION_VERIFY`, `SLA_BREACH`).
   - Create `backend/api/n8n_webhooks.py` with endpoint `POST /api/webhooks/n8n/callback` protected by `X-N8N-Webhook-Secret`.
5. **Step 5: Verification Logic Consolidation**
   - Consolidate citizen verification handling between `whatsapp.py` and `complaints.py` into `resolution_service.process_citizen_verification(...)`.
6. **Step 6: End-to-End Verification & Automated Test Suite Run**
   - Add tests for new webhooks in `backend/tests/`.
   - Run `python -m pytest` and verify 100% pass rate.
