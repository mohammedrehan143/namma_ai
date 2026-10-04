You are the lead architect, senior full-stack engineer, AI engineer, and DevOps engineer responsible for building the complete Namma AI platform.

Two Markdown files already exist in the repository:
- PRD.md
- REQUIREMENTS.md

READ BOTH FILES COMPLETELY BEFORE WRITING CODE. They are the primary source of truth. Understand the requirements, identify dependencies, design the architecture, and then build the project incrementally. Do not blindly implement everything at once.

PROJECT:
Namma AI is an AI-powered civic complaint and resolution platform.

TAGLINE:
"Namma AI — Report it. Prove it. Track it. Get it resolved."

CORE IDEA:
Citizens can report civic problems through a website, phone call, or WhatsApp. AI understands the complaint, extracts structured information, classifies it, identifies location, determines severity and priority, routes it to the correct department, collects evidence through WhatsApp, analyzes evidence using multimodal AI, detects duplicate complaints and groups them into incidents, allows officers to resolve the issue, verifies before/after evidence using AI, asks the citizen whether the issue is actually fixed, and reopens/escalates the complaint if the citizen rejects the resolution.

CORE FLOW:

Citizen
→ Website / Phone / WhatsApp
→ Complaint Intake
→ Speech-to-text if voice
→ LLM understanding
→ Classification
→ Location
→ Severity/Priority
→ Department Routing
→ Complaint Created
→ WhatsApp Evidence Request
→ Citizen sends photo/video
→ Vision AI analyzes evidence
→ Duplicate Detection
→ Incident Clustering
→ Officer Dashboard
→ Officer Resolution
→ Resolution Evidence
→ AI Before/After Verification
→ Citizen WhatsApp Verification
→ Resolved OR Reopened
→ SLA Escalation

IMPORTANT AI DECISION:
DO NOT train an LLM from scratch.
Use an existing LLM API.
Use the LLM for natural-language understanding and reasoning.
Use normal backend logic for deterministic operations.
Use multimodal/vision AI for image/evidence analysis.
Use embeddings/vector similarity where useful for duplicate detection.

USE THE LLM FOR:
- Complaint understanding
- Complaint classification
- Information extraction
- Location extraction
- Severity
- Priority
- Department routing
- Complaint summaries
- Missing information detection
- Follow-up questions
- Voice transcript understanding

DO NOT USE THE LLM FOR:
- Database CRUD
- Authentication
- Complaint IDs
- Status transitions
- SLA timers
- File storage
- Permissions
- Notifications
- Basic validation
- API routing

AI MUST RETURN STRUCTURED JSON.
The backend must validate AI output before storing it.
AI must never directly modify the database.
If AI fails, the complaint must still be safely stored and available for manual processing.

VISION AI SHOULD HANDLE:
- Evidence image analysis
- Issue detection
- Evidence relevance
- Severity estimation
- Before/after comparison
- Resolution verification

Example AI complaint output:

{
  "category": "ROAD_DAMAGE",
  "severity": "HIGH",
  "priority": "HIGH",
  "department": "ROADS",
  "location_text": "Near BMSIT main gate",
  "summary": "Large pothole reported near BMSIT main gate",
  "missing_information": []
}

Example evidence output:

{
  "issue_detected": true,
  "issue_type": "POTHOLE",
  "confidence": 0.94,
  "severity": "HIGH",
  "description": "Large pothole visible in submitted image"
}

Example resolution output:

{
  "resolution_likely_complete": true,
  "confidence": 0.91,
  "remaining_issue": null
}

TECH STACK:

Frontend:
- Next.js
- TypeScript
- Tailwind CSS

Backend:
- Python
- FastAPI

Database:
- PostgreSQL / Supabase

Storage:
- Supabase Storage or S3-compatible storage

Communication:
- Twilio Voice
- Twilio WhatsApp

AI:
- LLM API
- Multimodal/Vision AI
- Embeddings where required

Maps:
- Google Maps, Mapbox, or another suitable mapping service

Use a simple modular architecture. Do not create unnecessary microservices or over-engineer the project.

RECOMMENDED STRUCTURE:

namma-ai/
├── frontend/
├── backend/
├── docs/
├── PRD.md
├── REQUIREMENTS.md
├── .env.example
└── README.md

Backend should be logically organized into:
- api
- models
- schemas
- services
- integrations
- tests

AI services should be isolated behind a service layer so the AI provider can be changed later.

DEVELOPMENT PROCESS:

Build the complete project in sequential phases, but this is ONE continuous development task. Do not ask me to provide the next phase manually.

Before each phase:
- Understand what is required.
- Check dependencies.
- Implement only the appropriate scope.

After each phase:
- Run the application.
- Run relevant tests.
- Fix errors.
- Verify database changes.
- Verify APIs.
- Verify frontend/backend integration.
- Update documentation.
- Keep the project runnable before moving forward.

PHASE 0 — ANALYSIS AND ARCHITECTURE:
Read PRD.md and REQUIREMENTS.md.
Create:
- docs/architecture.md
- docs/api.md
- docs/ai.md
- .env.example

Define:
- System architecture
- Database architecture
- API architecture
- AI architecture
- Communication flow
- Storage
- Security
- Environment variables
- Data flow
- Component responsibilities

PHASE 1 — FOUNDATION:
Set up:
- Next.js frontend
- TypeScript
- Tailwind
- FastAPI backend
- Database connection
- Environment configuration
- CORS
- Logging
- Error handling

Create:
GET /health

Make sure frontend and backend run successfully.

PHASE 2 — DATABASE:
Create appropriate tables/models for:
- users
- complaints
- departments
- complaint_categories
- evidence
- complaint_events
- resolutions
- notifications
- sla_rules
- incident_clusters

Complaint should support:
- complaint ID
- citizen
- description
- category
- severity
- priority
- department
- location
- latitude
- longitude
- status
- SLA deadline
- timestamps

Create proper relationships and indexes.

PHASE 3 — WEB COMPLAINT INTAKE:
Create a citizen interface where the user can:
- Describe a civic issue
- Upload evidence
- Provide/select location
- Submit complaint
- Receive complaint ID

Make the basic complaint flow work before adding advanced AI.

PHASE 4 — LLM INTELLIGENCE:
Create a modular AI service.

Implement:
- Classification
- Severity
- Priority
- Department routing
- Summary
- Location extraction
- Missing information detection

Use structured JSON.
Validate the result.
Handle LLM failures gracefully.

PHASE 5 — LOCATION:
Support:
- GPS
- Map-selected location
- Text location
- AI-extracted location

Create map visualization.
Show complaint markers with:
- ID
- Category
- Priority
- Status

PHASE 6 — WHATSAPP:
Integrate Twilio WhatsApp.

After complaint registration:
Send complaint ID and ask for evidence.

Support:
- Images
- Videos where supported
- Multiple evidence files

Store evidence securely and associate it with the complaint.

PHASE 7 — EVIDENCE AI:
Analyze citizen evidence using multimodal AI.

Detect:
- Whether the reported issue is visible
- Issue type
- Severity
- Evidence relevance
- Confidence

Do not automatically reject complaints based solely on low AI confidence. Allow human review.

PHASE 8 — DUPLICATE DETECTION:
Detect whether multiple complaints refer to the same real-world issue.

Use:
- Text embeddings
- Semantic similarity
- Location proximity
- Category
- Time
- Evidence similarity where useful

Create incident clusters.

Example:

INC-102
Pothole near BMSIT main gate
Affected citizens: 17

Show all linked complaints.

PHASE 9 — OFFICER DASHBOARD:
Create an officer/admin dashboard showing:
- Total complaints
- Open complaints
- High priority complaints
- Overdue complaints
- Resolved complaints
- Reopened complaints

Create:
- Complaint table
- Complaint detail page
- Map
- Filters
- Search
- Incident clusters
- Complaint timeline

Complaint details should show:
- Citizen complaint
- AI analysis
- Location
- Evidence
- Duplicate information
- Department
- SLA
- Resolution

PHASE 10 — RESOLUTION:
Officers can:
- Accept complaint
- Assign department
- Update status
- Add notes
- Upload resolution evidence
- Submit resolution

PHASE 11 — AI RESOLUTION VERIFICATION:
Compare before and after evidence using multimodal AI.

Determine:
- Whether the issue is resolved
- Confidence
- Remaining issue

If incomplete or suspicious:
- Flag it
- Explain why
- Send for officer review

Do not automatically close solely based on AI.

PHASE 12 — CITIZEN VERIFICATION:
After officer resolution, send WhatsApp:

"Your complaint #NMA1234 has been marked as resolved. Is the issue actually fixed?"

Provide:
YES — ISSUE FIXED
NO — ISSUE STILL EXISTS

YES → RESOLVED
NO → REOPENED

PHASE 13 — SLA:
Implement configurable SLA rules.

Example:
LOW → 72 hours
MEDIUM → 48 hours
HIGH → 24 hours
CRITICAL → 4 hours

Support:
- SLA warning
- SLA breach
- Overdue status
- Escalation
- Notifications

Do not hardcode SLA values throughout the application.

PHASE 14 — PHONE:
Integrate Twilio Voice.

Flow:

Citizen
→ Twilio
→ Speech-to-text
→ LLM
→ Structured complaint
→ Backend
→ Complaint created

The AI should ask only necessary questions.

Example:
AI: What problem would you like to report?
Citizen: There is a huge pothole near BMSIT.
AI: Can you tell me the exact location?
Citizen: Near the main gate.
AI: Your complaint has been registered.

Send complaint details through WhatsApp afterward where possible.

PHASE 15 — NOTIFICATIONS:
Implement notifications for:
- Complaint registration
- Evidence requests
- Department assignment
- Status changes
- SLA warnings
- SLA breaches
- Resolution submission
- Citizen verification
- Reopening
- Escalation

PHASE 16 — END-TO-END INTEGRATION:
Ensure this entire flow works:

PHONE / WEBSITE
→ COMPLAINT
→ LLM
→ CLASSIFICATION
→ LOCATION
→ PRIORITY
→ WHATSAPP
→ EVIDENCE
→ VISION AI
→ DUPLICATE DETECTION
→ INCIDENT CLUSTER
→ DEPARTMENT
→ OFFICER DASHBOARD
→ RESOLUTION
→ AFTER EVIDENCE
→ AI VERIFICATION
→ CITIZEN VERIFICATION
→ RESOLVED / REOPENED
→ ESCALATION

PHASE 17 — SECURITY:
Implement:
- Environment variables
- Input validation
- File type validation
- File size limits
- Authentication
- Role-based permissions
- Secure storage
- API/webhook verification
- Audit logs
- AI response validation
- Error handling
- Rate limiting where appropriate

Never expose API keys or service-role credentials in frontend code.

PHASE 18 — TESTING:
Create tests for:
- Complaint creation
- AI classification
- AI response validation
- Evidence upload
- Duplicate detection
- Status transitions
- SLA calculations
- Resolution verification
- Citizen verification

Test failure cases:
- LLM unavailable
- Twilio unavailable
- Invalid evidence
- Duplicate complaint
- Missing location
- Missing evidence
- Low AI confidence
- Officer rejection
- Citizen rejection

The system must degrade gracefully.

If LLM fails:
Complaint should still be stored and become available for manual classification.

If WhatsApp fails:
Evidence request should be retryable.

If vision AI fails:
Evidence should remain available for human review.

PHASE 19 — UI/UX:
After core functionality works, polish:
- Dashboard
- Complaint details
- Maps
- Evidence gallery
- Timeline
- Priority indicators
- SLA indicators
- Loading states
- Empty states
- Error states
- Mobile responsiveness
- Accessibility

Do not waste time on animations before functionality works.

PHASE 20 — HACKATHON DEMO:
Prepare one polished end-to-end demonstration.

Scenario:
A citizen calls and reports a dangerous pothole near a college.

Demo flow:
1. Citizen calls.
2. AI understands the complaint.
3. AI asks for location.
4. Complaint is created.
5. Complaint appears on dashboard.
6. WhatsApp asks for evidence.
7. Citizen sends photo.
8. Vision AI detects pothole.
9. AI assigns high priority.
10. Another citizen reports the same pothole.
11. Duplicate detection groups them.
12. Affected citizen count increases.
13. Officer receives the incident.
14. Officer resolves the issue.
15. Officer uploads after-photo.
16. AI verifies resolution.
17. WhatsApp asks citizen for confirmation.
18. Citizen selects NO.
19. Complaint reopens.
20. SLA escalation occurs.

This should be the primary hackathon demo.

IMPORTANT ENGINEERING RULES:

- Do not train an LLM from scratch.
- Do not hardcode AI responses.
- Do not expose API keys.
- Do not build everything in one file.
- Do not create unnecessary microservices.
- Do not over-engineer.
- Do not skip requirements from the Markdown files.
- Do not leave broken code between phases.
- Do not lose complaints because an external AI/API fails.
- Do not let AI directly modify the database.
- Always validate AI outputs.
- Prefer reliable deterministic backend logic over unnecessary agents.
- Keep AI services modular.
- Keep the system easy to demonstrate.

AI AGENTS/SERVICES MAY INCLUDE:
- Complaint Intake
- Classification
- Location
- Priority
- Evidence
- Duplicate Detection
- Routing
- Resolution Verification
- Escalation

But do not create an autonomous agent for every small task.

DATABASE STATUS FLOW:

REPORTED
→ AI_PROCESSING
→ ASSIGNED
→ IN_PROGRESS
→ RESOLUTION_SUBMITTED
→ AI_VERIFICATION
→ CITIZEN_VERIFICATION
→ RESOLVED

If citizen rejects:

CITIZEN_VERIFICATION
→ REOPENED
→ ESCALATED
→ IN_PROGRESS

ENVIRONMENT VARIABLES:

DATABASE_URL=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
LLM_API_KEY=
LLM_MODEL=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
TWILIO_WHATSAPP_NUMBER=
MAPS_API_KEY=

Create .env.example with placeholders only.
Never commit real credentials.

DOCUMENTATION:
Maintain:
- README.md
- docs/architecture.md
- docs/api.md
- docs/ai.md

README must contain:
- Project overview
- Features
- Architecture
- Tech stack
- Setup instructions
- Environment variables
- Frontend setup
- Backend setup
- Database setup
- AI setup
- Twilio setup
- Demo instructions

PRODUCT POSITIONING:
Namma AI is an independent hackathon prototype.

Do not claim official integration with BBMP, GBA, Sahaaya, Karnataka government, or any government organization unless an actual integration exists.

Describe it as:
"An AI-powered civic grievance and resolution platform designed to improve complaint intake, evidence collection, routing, accountability, and citizen-verified resolution."

FINAL ACCEPTANCE CRITERIA:

The project is complete only when a judge can experience:

Citizen reports issue
→ AI understands it
→ Complaint created
→ Location identified
→ Priority assigned
→ WhatsApp evidence requested
→ Citizen sends evidence
→ AI analyzes evidence
→ Duplicate complaints detected
→ Officer sees incident
→ Officer resolves issue
→ Officer uploads proof
→ AI verifies resolution
→ Citizen verifies
→ Complaint closes OR reopens
→ SLA escalation works

FINAL INSTRUCTION:

Start now.

First read PRD.md and REQUIREMENTS.md.
Then analyze the requirements and create the architecture.
Then implement the project phase-by-phase automatically.
After each phase, test, fix errors, update documentation, and continue.
Do not ask me to provide the next phase.
Do not skip phases.
Do not implement everything blindly in one step.
Keep the project runnable throughout development.

The final result must be a polished, functional, hackathon-ready Namma AI application with a working end-to-end civic complaint lifecycle.