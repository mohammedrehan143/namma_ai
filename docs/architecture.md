# Namma AI — System Architecture Specification

## 1. Executive Summary

**Namma AI** ("Our AI") is a multimodal civic grievance and outcome-verification platform designed for urban civic bodies. It enables citizens to register complaints effortlessly through Web, Voice (Phone Call), and WhatsApp. It utilizes advanced AI for natural-language understanding, category classification, geocoding, severity and priority estimation, multimodal evidence verification, duplicate detection and incident clustering, officer dispatch, resolution verification, and closed-loop citizen verification.

---

## 2. System Architecture Overview

The system follows a modular, monolithic architecture with distinct service boundaries to ensure operational simplicity, rapid iteration, and maintainability.

```mermaid
graph TB
    subgraph Channels["Citizens & Intake Channels"]
        Web["🌐 Web Portal (Next.js)"]
        Phone["📞 Phone / Twilio Voice"]
        WA["📱 WhatsApp / Twilio Webhook"]
    end

    subgraph Gateway["API Gateway / Backend (FastAPI)"]
        Router["FastAPI Application Router"]
        Auth["Auth & Security Middleware"]
        UploadHandler["Media & Storage Manager"]
    end

    subgraph Services["Core Business Services"]
        ComplaintService["Complaint Engine"]
        AIService["AI Intelligence Layer (LLM/Vision/Embeddings)"]
        LocationService["Location & GIS Engine"]
        DuplicateService["Duplicate & Clustering Engine"]
        ResolutionService["Resolution Verification Engine"]
        SLAService["SLA & Escalation Engine"]
        NotificationService["Notification Dispatcher"]
    end

    subgraph DataTier["Data & Storage Tier"]
        DB[(PostgreSQL / SQLite)]
        ObjectStorage[(Local Storage / Supabase Storage / S3)]
    end

    subgraph Officers["Officer & Admin Workspace"]
        Dashboard["Civic Command Dashboard (Next.js)"]
    end

    Channels --> Gateway
    Gateway --> Services
    Services --> DataTier
    Services --> Officers
```

---

## 3. Component Responsibilities

| Component | Responsibility |
|---|---|
| **Frontend (`/frontend`)** | Next.js 14 App Router, TypeScript, Tailwind CSS. Provides citizen complaint intake form, real-time tracking, interactive map view, and the Officer Command Dashboard. |
| **Backend API (`/backend/api`)** | FastAPI REST endpoints and webhook listeners for Twilio Voice and WhatsApp. Validates incoming requests and coordinates application workflows. |
| **AI Service (`/backend/services/ai`)** | Isolated abstraction layer over LLMs (Gemini / OpenAI / Mock). Responsible for structured text understanding, category routing, severity/priority scoring, and missing information detection. |
| **Vision AI (`/backend/services/ai/vision.py`)** | Multimodal image analysis to detect defects (potholes, garbage, water leaks, etc.), measure confidence, assess severity, and perform Before/After resolution verification. |
| **Clustering Engine (`/backend/services/clustering.py`)** | Geospatial-temporal semantic clustering that groups related complaints into single actionable incidents (e.g. `INC-102`), aggregating affected citizens. |
| **Resolution Engine (`/backend/services/resolution.py`)** | Manages officer resolution submissions, AI proof verification, citizen verification triggers, and automatic reopening logic. |
| **SLA & Escalation Engine (`/backend/services/sla.py`)** | Monitors deadlines based on priority/category, generates warnings, flags breaches, and escalates cases to supervisors. |
| **Notification Engine (`/backend/services/notifications.py`)** | Dispatches SMS, WhatsApp, and in-app updates to citizens and officers at each stage of the lifecycle. |
| **Database & ORM (`/backend/models`)** | SQLAlchemy ORM models with SQLite (zero-config local run) and PostgreSQL/Supabase production support. |

---

## 4. Database Architecture & Schema

The relational schema ensures data integrity, auditability, and fast geospatial indexing.

```mermaid
erDiagram
    USERS ||--o{ COMPLAINTS : reports
    USERS ||--o{ COMPLAINT_EVENTS : triggers
    DEPARTMENTS ||--o{ COMPLAINTS : assigned_to
    INCIDENT_CLUSTERS ||--o{ COMPLAINTS : groups
    COMPLAINTS ||--o{ EVIDENCE : contains
    COMPLAINTS ||--o{ COMPLAINT_EVENTS : tracks
    COMPLAINTS ||--o{ RESOLUTIONS : produces
    COMPLAINTS ||--o{ NOTIFICATIONS : triggers
    DEPARTMENTS ||--o{ SLA_RULES : defines

    USERS {
        uuid id PK
        string phone UK
        string name
        string email
        string role "CITIZEN | OFFICER | SUPERVISOR | ADMIN"
        datetime created_at
    }

    DEPARTMENTS {
        string id PK "ROADS | SANITATION | DRAINAGE | WATER | ELECTRICAL"
        string name
        string description
        string contact_email
        int default_sla_hours
    }

    INCIDENT_CLUSTERS {
        string id PK "INC-101"
        string title
        string category
        float center_latitude
        float center_longitude
        string status "ACTIVE | RESOLVED"
        int report_count
        datetime first_reported_at
        datetime last_reported_at
    }

    COMPLAINTS {
        string id PK "NMA-10293"
        uuid citizen_id FK
        string cluster_id FK
        string category
        string department_id FK
        text raw_description
        text ai_summary
        string severity "LOW | MEDIUM | HIGH | CRITICAL"
        string priority "LOW | MEDIUM | HIGH | CRITICAL"
        int priority_score "0-100"
        string location_text
        float latitude
        float longitude
        string status "REPORTED | AI_PROCESSING | ASSIGNED | IN_PROGRESS | RESOLUTION_SUBMITTED | AI_VERIFICATION | CITIZEN_VERIFICATION | RESOLVED | REOPENED | ESCALATED"
        datetime sla_deadline
        boolean is_sla_breached
        string channel "WEB | PHONE | WHATSAPP"
        datetime created_at
        datetime updated_at
    }

    EVIDENCE {
        uuid id PK
        string complaint_id FK
        string evidence_type "CITIZEN_INITIAL | CITIZEN_FOLLOWUP | OFFICER_RESOLUTION"
        string media_url
        string media_type "IMAGE | VIDEO"
        json ai_analysis
        float ai_confidence
        boolean is_valid_evidence
        datetime uploaded_at
    }

    RESOLUTIONS {
        uuid id PK
        string complaint_id FK
        uuid officer_id FK
        text officer_notes
        string after_media_url
        json ai_verification
        boolean ai_verified
        string citizen_feedback "PENDING | CONFIRMED_FIXED | REJECTED"
        text citizen_rejection_reason
        datetime created_at
    }

    COMPLAINT_EVENTS {
        uuid id PK
        string complaint_id FK
        string event_type
        string old_status
        string new_status
        string actor_type
        uuid actor_id
        text details
        datetime created_at
    }

    SLA_RULES {
        uuid id PK
        string department_id FK
        string priority
        int max_resolution_hours
        int warning_threshold_hours
    }

    NOTIFICATIONS {
        uuid id PK
        string complaint_id FK
        string recipient_phone
        string channel "WHATSAPP | SMS | IN_APP"
        text message
        string status "PENDING | SENT | FAILED"
        datetime sent_at
    }
```

---

## 5. Complaint State Progression

The complaint lifecycle follows strict deterministic transitions. AI assists but never transitions states unilaterally without backend validation.

```mermaid
stateDiagram-v2
    [*] --> REPORTED : Citizen registers via Web/Phone/WA
    REPORTED --> AI_PROCESSING : LLM parses details & extracts geo/category
    AI_PROCESSING --> ASSIGNED : Routed to Dept & assigned SLA deadline
    ASSIGNED --> IN_PROGRESS : Officer acknowledges or evidence added
    IN_PROGRESS --> RESOLUTION_SUBMITTED : Officer uploads repair evidence & notes
    RESOLUTION_SUBMITTED --> AI_VERIFICATION : Vision AI compares Before vs After
    AI_VERIFICATION --> CITIZEN_VERIFICATION : WhatsApp prompt sent to Citizen
    CITIZEN_VERIFICATION --> RESOLVED : Citizen responds "YES, FIXED"
    CITIZEN_VERIFICATION --> REOPENED : Citizen responds "NO, NOT FIXED"
    REOPENED --> ESCALATED : Supervisor alerted & SLA expedited
    ESCALATED --> IN_PROGRESS : Reassigned for immediate action
    RESOLVED --> [*]
```

---

## 6. End-to-End Data & Communication Flow

```mermaid
sequenceDiagram
    autonumber
    actor Citizen
    participant Channel as Intake (Web/Voice/WA)
    participant API as FastAPI Backend
    participant AI as AI Engine (LLM + Vision)
    participant DB as Database
    actor Officer as Civic Officer
    actor Sup as Supervisor

    Citizen->>Channel: Submit complaint (Text/Audio/Image)
    Channel->>API: Ingest payload
    API->>DB: Store initial complaint (REPORTED)
    API->>AI: Analyze text (Classify, Severity, Priority, Location)
    AI-->>API: Return structured JSON
    API->>DB: Update complaint + Link duplicate cluster if exists
    API->>Channel: Dispatch WhatsApp confirmation & request photos
    Citizen->>Channel: Uploads issue photo via WhatsApp
    Channel->>API: Media webhook received
    API->>AI: Vision analysis on evidence
    AI-->>API: Issue confirmed (Confidence 94%)
    API->>DB: Store evidence + promote status to ASSIGNED

    Officer->>API: Views incident on Command Dashboard
    Officer->>API: Accepts and investigates (IN_PROGRESS)
    Officer->>API: Submits resolution with "After" photo
    API->>AI: Multimodal Verification (Compare Before vs After)
    AI-->>API: Verification passed (Likely resolved, 92%)
    API->>Channel: WhatsApp prompt: "Is the issue fixed? 1: Yes, 2: No"

    alt Citizen selects "1: Yes, Fixed"
        Citizen->>Channel: Replies "1"
        Channel->>API: Webhook: Confirmed
        API->>DB: Status -> RESOLVED
        API->>Citizen: Confirmation notification
    else Citizen selects "2: No, Still Exists"
        Citizen->>Channel: Replies "2"
        Channel->>API: Webhook: Rejected
        API->>DB: Status -> REOPENED & ESCALATED
        API->>Sup: Alert Supervisor of rejection
        API->>Officer: Alert Officer for rework
    end
```

---

## 7. Storage & Security Architecture

1. **Storage Subsystem:**
   - Modular storage provider interface (`LocalStorageProvider`, `SupabaseStorageProvider`, `S3StorageProvider`).
   - Content-type validation (JPEG, PNG, MP4, WebM only) and strict file size limits (max 10MB per image, 25MB per video).
   - Media references stored as unique sanitized paths, avoiding public disclosure of filesystem structures.

2. **Security & Authentication:**
   - Role-Based Access Control (RBAC): `CITIZEN`, `OFFICER`, `SUPERVISOR`, `ADMIN`.
   - Officer endpoints protected by JWT bearer authentication.
   - Twilio Webhook signature validation to prevent spoofing.
   - PII protection: Citizen phone numbers masked in general public dashboards, visible only to authorized investigating officers.
   - Strict output sanitation of AI responses to prevent prompt injection or unstructured garbage injection into SQL queries.

---

## 8. Graceful Degradation Strategy

The platform maintains absolute reliability even during external API downtime:
- **LLM Outage:** Complaints fall back to deterministic keyword matching or enter `MANUAL_REVIEW` status. Complaints are never dropped.
- **Vision AI Outage:** Evidence is safely saved and marked as `PENDING_MANUAL_VERIFICATION` for officer inspection.
- **Twilio Outage:** Inbound web complaints and direct web evidence uploads function independently. WhatsApp evidence requests queue for retry.
- **Offline / Local Dev:** Built-in mock AI engines and SQLite database permit complete offline development, testing, and judge demonstrations without external API keys.
