# Namma AI — API Specification

Base URL: `http://localhost:8000/api`

---

## 1. System & Health

### `GET /health`
Returns the operational health of the application, database, and background services.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "database": "connected",
  "storage": "local",
  "timestamp": "2026-10-04T13:30:00Z"
}
```

---

## 2. Complaint Intake & Lifecycle

### `POST /api/complaints`
Submit a new civic complaint (Web channel). Triggers synchronous or background AI classification and evidence dispatch.

**Request Body**:
```json
{
  "citizen_name": "Ramesh Kumar",
  "citizen_phone": "+919876543210",
  "citizen_email": "ramesh@example.com",
  "description": "Large dangerous pothole right outside BMSIT main gate, 2-wheelers skidding.",
  "location_text": "Near BMSIT main gate, Doddaballapur Road",
  "latitude": 13.1345,
  "longitude": 77.5682,
  "category": null,
  "channel": "WEB"
}
```

**Response `201 Created`**:
```json
{
  "id": "NMA-10293",
  "status": "REPORTED",
  "category": "ROAD_DAMAGE",
  "department": "ROADS",
  "severity": "HIGH",
  "priority": "HIGH",
  "priority_score": 88,
  "location_text": "Near BMSIT main gate, Doddaballapur Road",
  "latitude": 13.1345,
  "longitude": 77.5682,
  "cluster_id": "INC-102",
  "sla_deadline": "2026-10-05T13:30:00Z",
  "ai_summary": "High-risk pothole causing skidding near college main gate",
  "created_at": "2026-10-04T13:30:00Z"
}
```

---

### `GET /api/complaints`
List complaints with filtering, search, pagination, and sorting.

**Query Parameters**:
- `status`: `REPORTED`, `ASSIGNED`, `IN_PROGRESS`, `RESOLUTION_SUBMITTED`, `RESOLVED`, `REOPENED`, etc.
- `priority`: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- `department`: `ROADS`, `SANITATION`, `WATER`, etc.
- `search`: string query across description and location
- `limit`: integer (default: 20)
- `offset`: integer (default: 0)

**Response `200 OK`**:
```json
{
  "total": 42,
  "limit": 20,
  "offset": 0,
  "items": [
    {
      "id": "NMA-10293",
      "category": "ROAD_DAMAGE",
      "department": "ROADS",
      "status": "IN_PROGRESS",
      "priority": "HIGH",
      "location_text": "Near BMSIT main gate",
      "latitude": 13.1345,
      "longitude": 77.5682,
      "evidence_count": 2,
      "created_at": "2026-10-04T13:30:00Z"
    }
  ]
}
```

---

### `GET /api/complaints/{id}`
Retrieve full complaint details including timeline events, evidence files, and resolution verification state.

**Response `200 OK`**:
```json
{
  "id": "NMA-10293",
  "citizen": {
    "name": "Ramesh Kumar",
    "phone": "+919876543210"
  },
  "category": "ROAD_DAMAGE",
  "department": "ROADS",
  "severity": "HIGH",
  "priority": "HIGH",
  "priority_score": 88,
  "status": "IN_PROGRESS",
  "raw_description": "Large dangerous pothole right outside BMSIT main gate, 2-wheelers skidding.",
  "ai_summary": "High-risk pothole causing skidding near college main gate",
  "location": {
    "text": "Near BMSIT main gate, Doddaballapur Road",
    "latitude": 13.1345,
    "longitude": 77.5682
  },
  "cluster": {
    "id": "INC-102",
    "title": "Pothole hazard at BMSIT Gate",
    "total_affected_citizens": 17
  },
  "sla": {
    "deadline": "2026-10-05T13:30:00Z",
    "is_breached": false,
    "remaining_hours": 23.5
  },
  "evidence": [
    {
      "id": "ev-1",
      "media_url": "/uploads/ev-1.jpg",
      "media_type": "IMAGE",
      "type": "CITIZEN_INITIAL",
      "ai_analysis": {
        "issue_detected": true,
        "issue_type": "POTHOLE",
        "confidence": 0.94,
        "severity": "HIGH"
      }
    }
  ],
  "timeline": [
    {
      "event": "COMPLAINT_REGISTERED",
      "actor": "CITIZEN",
      "timestamp": "2026-10-04T13:30:00Z",
      "details": "Registered via Web portal"
    },
    {
      "event": "EVIDENCE_ATTACHED",
      "actor": "SYSTEM",
      "timestamp": "2026-10-04T13:32:00Z",
      "details": "Citizen uploaded initial photo via WhatsApp"
    }
  ]
}
```

---

## 3. Evidence Management

### `POST /api/complaints/{id}/evidence`
Upload photographic or video evidence for a complaint. Triggers Multimodal AI inspection.

**Form Data / Multipart**:
- `file`: binary media
- `evidence_type`: `CITIZEN_INITIAL` | `CITIZEN_FOLLOWUP` | `OFFICER_RESOLUTION`

**Response `201 Created`**:
```json
{
  "id": "ev-88",
  "complaint_id": "NMA-10293",
  "media_url": "/uploads/ev-88.jpg",
  "media_type": "IMAGE",
  "ai_analysis": {
    "issue_detected": true,
    "issue_type": "POTHOLE",
    "confidence": 0.95,
    "severity": "HIGH",
    "description": "Large deep asphalt crater visible on active road lane."
  }
}
```

---

## 4. Officer Workflow & Resolution

### `POST /api/complaints/{id}/assign`
Assign complaint to an officer or update department.

**Request Body**:
```json
{
  "department_id": "ROADS",
  "assigned_officer_id": "usr-officer-12",
  "notes": "Assigned to Ward 12 road maintenance crew"
}
```

---

### `POST /api/complaints/{id}/resolve`
Officer submits resolution details and "after-repair" photographic proof.

**Request Body / Multipart**:
```json
{
  "officer_notes": "Pothole filled with cold asphalt mix and roller compacted.",
  "after_media_file": "(binary)"
}
```

**Response `200 OK`**:
```json
{
  "complaint_id": "NMA-10293",
  "status": "CITIZEN_VERIFICATION",
  "ai_verification": {
    "resolution_likely_complete": true,
    "confidence": 0.92,
    "details": "Road surface is repaired and level; no open void detected.",
    "remaining_issue": null
  },
  "citizen_prompt_dispatched": true
}
```

---

## 5. Citizen Verification & Feedback

### `POST /api/complaints/{id}/verify`
Process citizen verification outcome (typically triggered by WhatsApp interaction or web confirmation).

**Request Body**:
```json
{
  "is_fixed": false,
  "citizen_notes": "Only half filled, loose gravel flying everywhere."
}
```

**Response `200 OK`**:
```json
{
  "complaint_id": "NMA-10293",
  "status": "REOPENED",
  "escalated": true,
  "message": "Complaint reopened and flagged for supervisor review."
}
```

---

## 6. Incident Clusters & Duplicates

### `GET /api/clusters`
List aggregated incident clusters.

**Response `200 OK`**:
```json
[
  {
    "id": "INC-102",
    "title": "Severe road cavity near BMSIT Gate",
    "category": "ROAD_DAMAGE",
    "department": "ROADS",
    "status": "IN_PROGRESS",
    "affected_citizens_count": 17,
    "latitude": 13.1345,
    "longitude": 77.5682,
    "complaint_ids": ["NMA-10293", "NMA-10304", "NMA-10311"]
  }
]
```

---

## 7. Webhooks (Telephony & WhatsApp)

### `POST /api/twilio/voice`
Twilio Voice TwiML webhook to handle conversational complaint calls.

### `POST /api/whatsapp/webhook`
Twilio WhatsApp incoming message and media webhook. Handles photo evidence and "1: Yes, Fixed / 2: No" verification responses.

---

## 8. Dashboard Statistics

### `GET /api/dashboard/stats`
Summary indicators for the command center.

**Response `200 OK`**:
```json
{
  "total": 520,
  "open": 183,
  "in_progress": 74,
  "resolved": 251,
  "reopened": 12,
  "critical": 17,
  "high": 42,
  "medium": 129,
  "low": 332,
  "sla_breached": 6
}
```
