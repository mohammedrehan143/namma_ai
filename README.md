# Namma AI — Civic Complaint & Verified Resolution Platform

> *"Namma AI — Report it. Prove it. Track it. Get it resolved."*

An AI-powered civic grievance and outcome-verification platform designed to transform unstructured citizen reports into structured, evidence-backed municipal cases—and follow them all the way from initial intake to citizen-verified resolution.

---

## 1. Project Overview

Municipal civic grievance portals often suffer from high rates of false closures, where complaints are arbitrarily marked "resolved" without verifying physical completion or consulting the citizen.

**Namma AI** changes the civic paradigm from **tracking complaints** to **tracking outcomes**:
- **Multi-Channel Ingestion:** Citizens report naturally through Web, Phone Calls (Twilio IVR), or WhatsApp.
- **AI Intelligence:** Converts freeform text/voice into structured categories, severity scores, and location landmarks.
- **Multimodal Evidence Audit:** Computer Vision evaluates citizen photos and measures defect dimensions and safety risk.
- **Duplicate & Incident Clustering:** Spatial-temporal semantic clustering groups related citizen reports into actionable incidents (e.g. `INC-102`), aggregating affected citizen numbers and auto-escalating priority.
- **Officer Command Center:** Real-time dashboard with SLA timers, incident maps, and status controls.
- **Multimodal Before/After Repair Verification:** Compares the initial citizen proof against the officer's repair photo to ensure work was done before closing.
- **Closed-Loop Citizen Verification:** Dispatches a WhatsApp prompt: *"Is the issue actually fixed? 1: Yes / 2: No"*. If rejected, the grievance automatically reopens and escalates to a department supervisor.

---

## 2. Core Architecture & Flow

```
CITIZEN (Phone / Web / WhatsApp)
      ↓
Complaint Intake & Speech-to-Text
      ↓
LLM Natural Language Understanding & Classification
      ↓
Geocoding & Location Extraction
      ↓
Priority Engine & SLA Calculation
      ↓
WhatsApp Evidence Request
      ↓
Citizen Sends Photo Proof
      ↓
Vision AI Evidence Analysis
      ↓
Duplicate Detection & Incident Clustering
      ↓
Department Routing & Officer Command Dashboard
      ↓
Officer Field Repair & After-Photo Proof Upload
      ↓
Vision AI Before/After Resolution Verification
      ↓
WhatsApp Citizen Confirmation ("1: Yes / 2: No")
      ↙                           ↘
  CLOSED (Confirmed)         REOPENED & ESCALATED
```

---

## 3. Tech Stack

- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide Icons
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Pydantic v2
- **Database:** PostgreSQL / Supabase (with SQLite zero-config local fallback)
- **AI & Vision:** Google Gemini 1.5 Flash (`google-genai`), OpenAI (`gpt-4o-mini`), and high-fidelity deterministic Mock engine
- **Telephony & Messaging:** Twilio Voice (TwiML IVR Speech-to-Text), Twilio WhatsApp API
- **Maps & Geospatial:** OpenStreetMap Nominatim, Haversine spatial clustering, SVG Geospatial projection

---

## 4. Setup & Running Instructions

### 4.1 Prerequisites
- Python 3.10+
- Node.js 18+ (Node 20+ recommended)
- Git

### 4.2 Clone and Setup Environment

```bash
git clone https://github.com/your-org/namma-ai.git
cd rotaract

# Copy environment template
cp .env.example .env
```

### 4.3 Backend Setup

```bash
# 1. Install Python dependencies
pip install -r backend/requirements.txt

# 2. Initialize and pre-seed the database (Creates tables, departments, SLA rules, staff accounts)
python -m backend.core.init_db

# 3. Start the FastAPI development server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at: `http://localhost:8000/docs`

> **Live Production Backend**: `https://namma-ai.onrender.com` (API: `https://namma-ai.onrender.com/api`, Swagger: `https://namma-ai.onrender.com/docs`, Health: `https://namma-ai.onrender.com/health`)

### 4.4 Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start the Next.js development server
npm run dev
```
Web Application will be live at: `http://localhost:3000`

---

## 5. Cloud Deployment (Vercel & Render)

Namma AI is pre-configured for instant cloud deployment:
- **Frontend on Vercel**: Zero-config Next.js 14 deployment (`frontend/vercel.json` and root `vercel.json`).
- **Backend on Render**: Blueprint-ready FastAPI service (`render.yaml`).

For full step-by-step instructions and environment variable reference, see [DEPLOYMENT.md](file:///D:/agy/rotaract/DEPLOYMENT.md).

### Quick Deploy:
1. **Backend (Render)**: Connect repo to Render > Select **Blueprint** (`render.yaml`) > Click **Apply**.
2. **Frontend (Vercel)**: Import repo into Vercel > Set Root Directory to `frontend` > Add `NEXT_PUBLIC_API_BASE_URL=https://<your-render-url>/api` > Click **Deploy**.

---

## 6. Environment Variables (`.env`)

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | Database connection string | `sqlite:///./namma_ai.db` |
| `LLM_PROVIDER` | AI provider (`gemini`, `openai`, `mock`) | `mock` |
| `LLM_API_KEY` | API Key for Google Gemini or OpenAI | `(optional for mock)` |
| `LLM_MODEL` | Target LLM model name | `gemini-1.5-flash` |
| `TWILIO_ACCOUNT_SID`| Twilio Account SID | `(optional for local)` |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | `(optional for local)` |
| `TWILIO_PHONE_NUMBER`| Twilio Voice Helpline Phone | `+1234567890` |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp Sender Number | `whatsapp:+14155238886` |
| `SLA_HOURS_CRITICAL`| Hours allowed before critical SLA breach | `4` |
| `SLA_HOURS_HIGH` | Hours allowed before high SLA breach | `24` |
| `STORAGE_PROVIDER` | Media storage (`local`, `supabase`, `s3`)| `local` |

---

## 6. Running Automated Tests

Run the complete test suite covering all 20 phases, error degradation, bug fix regressions, and integrations:

```bash
python -m pytest
```

Output:
```text
42 passed in 2.88s
- test_ai_intelligence.py (5 tests)
- test_bug_fixes_and_edge_cases.py (6 tests)
- test_complaints_intake.py (1 test)
- test_dashboard.py (2 tests)
- test_database.py (1 test)
- test_duplicate_clustering.py (1 test)
- test_end_to_end_integration.py (1 test)
- test_evidence_ai.py (3 tests)
- test_graceful_degradation.py (4 tests)
- test_health.py (1 test)
- test_location.py (4 tests)
- test_notifications.py (1 test)
- test_resolution_verification.py (1 test)
- test_security.py (3 tests)
- test_sla.py (2 tests)
- test_voice_intake.py (2 tests)
- test_whatsapp.py (2 tests)
- test_demo.py (2 tests)
```

---

## 7. Interactive Hackathon Demo Guide (3–5 min Judge Presentation)

Navigate to `http://localhost:3000/demo` in your browser:

1. Click **"Run Complete 20-Step Live Demo"**.
2. Watch the automated real-time progression across:
   - Voice grievance intake & AI understanding
   - Multimodal evidence analysis
   - Duplicate complaint detection & `#INC-102` cluster formation
   - Officer resolution with "After-repair" photo proof
   - Vision AI comparison
   - WhatsApp verification prompt with simulated Citizen rejection
   - Automatic grievance **REOPENING** and **SLA SUPERVISOR ESCALATION**.
3. Click **"Open Case in Dashboard"** to inspect the live audit timeline, geospatial pin, before/after gallery, and supervisor escalation state.

---

## 8. Product Positioning & Disclaimer

*Namma AI is an independent civic technology prototype developed for civic grievance resolution and outcome accountability. It is not officially affiliated with BBMP, GBA, Sahaaya, or the Government of Karnataka unless an official partnership is explicitly formalized.*
