# Namma AI — AI & Vision Engineering Specification

## 1. Principles & Architectural Guardrails

1. **Deterministic Separation of Concerns:**
   - **AI performs understanding, extraction, classification, and visual scoring.**
   - **Deterministic Backend performs DB CRUD, state machines, SLA clocks, authorization, and notifications.**
   - AI outputs are **strictly advisory** until validated by backend Pydantic schemas.
   - AI is **never** granted database write credentials or autonomous mutation permissions.

2. **Strict Output Schema Enforcement:**
   - All LLM queries demand structured JSON conforming to formal JSON schemas.
   - Outputs are validated using Pydantic models before saving.
   - When external LLM APIs fail or return malformed JSON, deterministic fallback rules (rule-based keyword classification and manual queueing) automatically take over.

3. **Provider Agnostic Abstraction:**
   - The AI subsystem resides behind the `BaseAIService` interface in `backend/services/ai/`.
   - Supports Google Gemini (`gemini-1.5-flash`), OpenAI (`gpt-4o-mini`), and a deterministic `MockAIService` designed for zero-API-key testing and offline hackathon judging.

---

## 2. AI Tasks & Prompt Specifications

### 2.1 Complaint Understanding & Classification

**Purpose:** Converts conversational, fragmented citizen utterances (text or voice transcript) into structured categorization, department assignment, and urgency scoring.

**Prompt Schema (`backend/services/ai/prompts.py`):**
```text
System: You are Namma AI's civic grievance parsing engine for urban infrastructure.
Analyze the citizen's complaint report. Return a valid JSON object matching the exact schema below.

JSON Schema:
{
  "category": "ROAD_DAMAGE" | "GARBAGE" | "DRAINAGE" | "SEWAGE" | "WATER_LEAK" | "STREETLIGHT" | "PUBLIC_INFRA" | "OTHER",
  "department": "ROADS" | "SANITATION" | "DRAINAGE" | "WATER" | "ELECTRICAL" | "PUBLIC_WORKS",
  "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "priority": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "priority_score": integer (0 to 100),
  "summary": string (concise 1-sentence title),
  "extracted_location": string or null,
  "landmark": string or null,
  "safety_hazard": boolean,
  "missing_info": [string]
}
```

---

### 2.2 Multimodal Vision AI for Citizen Evidence

**Purpose:** Validates whether the submitted photo shows a genuine civic issue, matches the reported category, and determines defect dimensions/severity.

**Input:** Raw image binary + citizen description.

**Vision Prompt Schema:**
```text
System: Analyze this civic evidence photograph.
Citizen Report: "{description}"

Return a valid JSON object:
{
  "issue_detected": boolean,
  "issue_type": "POTHOLE" | "GARBAGE_DUMP" | "SEWAGE_LEAK" | "BROKEN_LIGHT" | "FALLEN_TREE" | "WATER_BURST" | "OTHER",
  "matches_complaint": boolean,
  "confidence": float (0.0 to 1.0),
  "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "visual_description": string,
  "quality_score": float (0.0 to 1.0)
}
```

---

### 2.3 Multimodal Before / After Resolution Verification

**Purpose:** Compares the original citizen evidence photo with the civic officer's uploaded "after-repair" photo to verify if the physical issue was rectified.

**Vision Prompt Schema:**
```text
System: You are an independent civic quality auditor.
Compare the BEFORE photo (citizen complaint) with the AFTER photo (officer repair proof).

Return a valid JSON object:
{
  "resolution_likely_complete": boolean,
  "confidence": float (0.0 to 1.0),
  "remaining_issue": string or null,
  "is_same_location": boolean,
  "notes": string,
  "audit_flag": "PASSED" | "SUSPICIOUS" | "INCOMPLETE"
}
```

---

### 2.4 Duplicate & Incident Clustering Engine

**Algorithm:** Hybrid Spatio-Temporal Semantic Clustering:
1. **Spatial Filtering:** Candidate complaints within 200 meters of each other (Haversine formula).
2. **Temporal Window:** Reported within the last 72 hours.
3. **Category Match:** Identical category (`ROAD_DAMAGE`).
4. **Semantic Similarity:** Cosine similarity of text embeddings (`> 0.82`) or text embedding cluster threshold.
5. **Cluster Creation:** If a match is found, link new complaint to the existing `INC-xxx` cluster and increment `affected_citizens_count`. If not, create a new cluster.

---

## 3. Fallback & Graceful Degradation Matrix

| Component | Failure Scenario | Fallback Mechanism |
|---|---|---|
| **LLM Classification** | Rate limit / Network timeout / Invalid JSON | Rule-based keyword dictionary (`pothole` -> `ROADS`, `garbage` -> `SANITATION`). Marked as `AI_FALLBACK_USED`. |
| **Vision Analysis** | API failure / Unsupported media format | File saved safely; marked `ai_analysis: { "status": "MANUAL_REVIEW_REQUIRED" }`. Alert sent to officer to inspect visually. |
| **Resolution Verification** | Vision verification error | Flagged as `AUDIT_MANUAL_CHECK`, citizen verification still triggered directly to guarantee democratic verification. |
| **Geocoding** | Maps API quota exceeded | Retain raw user string and nearest landmark text; allow officer to pin on dashboard. |
