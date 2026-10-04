# Sahaaya AI — Product Requirements Document

> **AI-Powered Civic Complaint, Evidence & Resolution Platform**

**Project Type:** Hackathon MVP  
**Domain:** Civic Tech / AI / Agentic AI  
**Target:** Bengaluru / Karnataka  
**Status:** Prototype

---

## 1. Problem Statement

Citizens often face difficulties when reporting civic issues such as:

- Potholes
- Garbage accumulation
- Sewage overflow
- Broken streetlights
- Water leakage
- Damaged roads
- Illegal dumping
- Blocked drains
- Fallen trees
- Other public infrastructure issues

Citizens may not know:

- Which department is responsible
- How to properly describe the issue
- What evidence is required
- Where to submit the complaint
- How to follow up
- Whether the reported issue was actually fixed

A major problem is that a complaint can be marked **"resolved"** even when the underlying issue has not actually been fixed.

### Core Problem

> How can we build a multimodal civic grievance system where citizens can report problems naturally, provide evidence easily, and ensure that complaints are genuinely resolved?

---

# 2. Proposed Solution

**Sahaaya AI** is a multimodal civic grievance and resolution platform that allows citizens to report civic problems through:

- Phone calls
- Website
- WhatsApp

AI converts unstructured citizen reports into structured complaints, collects evidence through WhatsApp, determines severity, identifies duplicate complaints, routes the complaint to the appropriate department, monitors SLA deadlines, verifies the resolution, and allows citizens to confirm or reject the resolution.

### Core Principle

> **A complaint should not be considered truly resolved until the evidence and citizen confirmation support the resolution.**

---

# 3. Product Vision

Build a civic platform where:

```text
Citizen reports problem
        ↓
AI understands problem
        ↓
AI collects evidence
        ↓
AI identifies location
        ↓
AI determines severity
        ↓
AI detects duplicate complaints
        ↓
AI routes complaint
        ↓
Officer resolves issue
        ↓
AI verifies resolution
        ↓
Citizen confirms
        ↓
Complaint CLOSED
```

If the citizen rejects the resolution:

```text
Citizen rejects
      ↓
Complaint REOPENED
      ↓
Supervisor notified
      ↓
Further action required
```

---

# 4. User Roles

## 4.1 Citizen

Citizens can:

- Register complaints
- Submit complaints through phone
- Submit complaints through website
- Send evidence through WhatsApp
- Share location
- Track complaints
- Receive notifications
- Confirm resolution
- Reject resolution
- Reopen complaints

---

## 4.2 Civic Officer

Officers can:

- View assigned complaints
- View citizen descriptions
- View images/videos
- View AI analysis
- Accept assignments
- Update complaint status
- Upload repair evidence
- Mark complaints as resolved

---

## 4.3 Supervisor

Supervisors can:

- Monitor department complaints
- View overdue complaints
- View SLA violations
- Escalate complaints
- Reassign complaints
- Monitor officer performance

---

## 4.4 Administrator

Administrators can:

- Manage departments
- Manage users
- Manage complaint categories
- Configure SLA rules
- Manage priority rules
- Monitor overall platform performance

---

# 5. Complaint Channels

Sahaaya AI supports three primary complaint channels.

## 5.1 Phone

Citizen calls a dedicated phone number.

Technology:

- Twilio
- Speech-to-Text
- LLM
- Text-to-Speech

Flow:

```text
Citizen calls
     ↓
Twilio
     ↓
Speech-to-Text
     ↓
AI Complaint Agent
     ↓
Extract complaint information
     ↓
Ask missing questions
     ↓
Create complaint
```

---

## 5.2 Website

Citizen can submit a complaint through a web interface.

Basic fields:

- Name
- Phone number
- Description
- Location
- Category
- Photo/video

However, the system should minimize manual fields.

The AI should automatically determine:

- Category
- Department
- Severity
- Location
- Priority

---

## 5.3 WhatsApp

WhatsApp is primarily used for:

- Evidence collection
- Complaint updates
- Resolution confirmation
- Reopening complaints

Technology:

- Twilio WhatsApp API
- Webhooks
- Backend
- Object storage

---

# 6. Phone Complaint Flow

Example:

### Citizen

> There is a huge pothole near the college main gate.

### AI

> I'm sorry about that. Can you tell me the nearest landmark?

### Citizen

> Near the main gate beside the bus stop.

### AI

> Is the pothole causing any immediate danger to vehicles or pedestrians?

### Citizen

> Yes, bikes are almost falling.

AI extracts:

```json
{
  "category": "road_damage",
  "severity": "high",
  "location": "college main gate",
  "landmark": "bus stop",
  "description": "Large pothole causing danger to vehicles"
}
```

System creates:

```text
Complaint ID: SAH-10293
Status: REGISTERED
Priority: HIGH
```

Citizen receives confirmation.

---

# 7. WhatsApp Evidence Collection

Immediately after complaint registration, the citizen receives a WhatsApp message.

Example:

> **Sahaaya AI**
>
> Your complaint **#SAH-10293** has been registered.
>
> 📍 Location: College Main Gate  
> 🏷️ Category: Road Damage  
> 🔴 Priority: High
>
> Please send photos or videos showing the issue here.

---

## 7.1 Evidence Collection Agent

The AI should actively request additional evidence.

Example:

### Citizen sends first photo

AI:

> Thank you. Please send one wider photo showing the surrounding location.

Citizen sends photo.

AI:

> Please send a closer photo of the damaged area.

This makes WhatsApp an **evidence collection channel**, not simply a notification system.

---

# 8. Evidence Storage

All evidence must be linked to the complaint.

### Complaint Table

```text
complaints
-----------
id
citizen_id
category
description
latitude
longitude
address
priority
severity
status
department
created_at
updated_at
```

### Evidence Table

```text
evidence
--------
id
complaint_id
media_url
media_type
uploaded_at
ai_analysis
```

Media can be stored using:

- Supabase Storage
- S3-compatible storage
- Cloud object storage

---

# 9. AI Evidence Analysis

Computer vision analyzes submitted images and videos.

Example:

```text
Object detected:
Pothole

Estimated size:
Large

Severity:
High

Evidence quality:
Good

Safety risk:
High
```

Potential supported categories:

- Potholes
- Garbage
- Sewage overflow
- Water leakage
- Fallen trees
- Damaged roads
- Blocked drains
- Broken infrastructure

For the MVP, only support a limited number of categories.

---

# 10. Location Intelligence

The system can obtain location through multiple methods.

## Website

Request GPS permission.

## Phone

Ask the citizen for:

- Address
- Landmark
- Nearby location

## WhatsApp

Allow:

- Location sharing
- Map location
- Text description

The backend converts this into:

```text
Latitude
Longitude
Address
Landmark
```

---

# 11. AI Complaint Classification

The AI automatically determines the complaint category.

Example:

```text
"There is sewage coming onto the road."

        ↓

Category:
Drainage / Sewage
```

Possible categories:

```text
Road Damage
Garbage
Drainage
Water
Streetlight
Traffic
Public Infrastructure
Other
```

---

# 12. Automatic Department Routing

After classification, the AI determines the responsible department.

Example:

```text
Pothole
    ↓
Road Maintenance

Garbage
    ↓
Solid Waste Management

Water leakage
    ↓
Water Department

Streetlight
    ↓
Street Lighting

Sewage
    ↓
Drainage
```

Administrators must be able to manually override AI classification.

---

# 13. AI Priority Engine

Not every complaint should receive the same priority.

Priority is calculated using:

```text
Severity
+
Safety Risk
+
People Affected
+
Location Importance
+
Duplicate Reports
+
Time Unresolved
```

Example:

### Broken park bench

```text
Priority: LOW
```

### Broken streetlight on residential road

```text
Priority: MEDIUM
```

### Open manhole near school

```text
Priority: CRITICAL
```

---

# 14. Duplicate Complaint Detection

Duplicate detection is a core AI feature.

Suppose multiple citizens report:

> Pothole near the same location.

Instead of creating:

```text
Complaint 101
Complaint 102
Complaint 103
Complaint 104
Complaint 105
```

AI clusters them into:

```text
                5 complaints
                      ↓
               AI clustering
                      ↓
                 ONE INCIDENT
                      ↓
              5 affected citizens
```

The officer sees:

```text
MAJOR ROAD INCIDENT

23 citizens reported this location.

Reports in last 48 hours: 23

Priority: CRITICAL
```

---

# 15. Complaint Dashboard

The main civic command center should display:

```text
CIVIC COMMAND CENTER

Critical        17
High            42
Medium          129
Low             341

Pending         183
In Progress     74
Resolved        291
Reopened        12
```

---

# 16. Map View

Display complaints geographically.

Suggested markers:

```text
🔴 Critical
🟠 High
🟡 Medium
🟢 Low
```

Clicking a marker opens the complaint details.

---

# 17. Complaint Detail Page

Example:

```text
SAH-10293

POTHOLE
HIGH PRIORITY

Location:
College Main Gate

Reported:
2 hours ago

Affected Citizens:
17

Evidence:
6 Photos
1 Video

AI Analysis:
Large pothole
High traffic area
High safety risk

Assigned Department:
Road Maintenance

Status:
IN PROGRESS
```

---

# 18. Officer Workflow

Officer receives assigned complaint.

Status progression:

```text
REGISTERED
      ↓
ASSIGNED
      ↓
ACCEPTED
      ↓
IN PROGRESS
      ↓
RESOLVED
      ↓
CITIZEN VERIFICATION
      ↓
CLOSED
```

If citizen rejects:

```text
RESOLVED
    ↓
CITIZEN REJECTS
    ↓
REOPENED
    ↓
ESCALATED
```

---

# 19. Resolution Verification

When an officer marks a complaint as resolved, they must upload an after-repair photo.

Example:

```text
Before Image
      +
After Image
      ↓
Computer Vision
      ↓
Resolution Verification
```

AI output:

```text
Resolution:
Likely successful

Confidence:
91%
```

or:

```text
Warning:
Possible incomplete resolution

Confidence:
74%
```

The AI should assist verification, not make irreversible decisions by itself.

---

# 20. Citizen Resolution Confirmation

After the officer marks the complaint as resolved, WhatsApp sends:

> **Complaint #SAH-10293**
>
> The reported issue has been marked as resolved.
>
> Is the issue actually fixed?
>
> **1️⃣ Yes, fixed**
>
> **2️⃣ No, still exists**

---

## If YES

```text
Complaint
    ↓
CLOSED
```

---

## If NO

```text
Complaint
    ↓
REOPENED
    ↓
Supervisor notified
```

The citizen can optionally submit new evidence.

---

# 21. SLA Monitoring

Every complaint category can have a resolution SLA.

Example:

```text
Critical → 4 hours
High     → 24 hours
Medium   → 3 days
Low      → 7 days
```

SLA flow:

```text
Complaint assigned
        ↓
Time monitored
        ↓
Deadline approaching
        ↓
Officer reminder
        ↓
Deadline exceeded
        ↓
Supervisor escalation
```

---

# 22. WhatsApp Notification System

WhatsApp notifications include:

### Complaint Registered

> Your complaint #SAH-10293 has been registered successfully.

### Evidence Request

> Please send photos/videos of the issue here.

### Complaint Assigned

> Your complaint has been assigned to the Road Maintenance Department.

### Progress Update

> Your complaint is currently being investigated.

### Resolution

> Your complaint has been marked as resolved.

### Verification

> Is the issue actually fixed?

### Reopened

> Your complaint has been reopened and escalated for further action.

---

# 23. AI Agent Architecture

The system can use multiple specialized AI agents.

## Agent 1 — Complaint Intake Agent

Understands:

- Voice
- Text
- Images

---

## Agent 2 — Classification Agent

Determines:

- Category
- Department

---

## Agent 3 — Location Agent

Determines:

- Latitude
- Longitude
- Address
- Landmark

---

## Agent 4 — Evidence Agent

Analyzes:

- Images
- Videos
- Evidence quality

---

## Agent 5 — Duplicate Detection Agent

Finds related complaints and incidents.

---

## Agent 6 — Priority Agent

Calculates severity and priority.

---

## Agent 7 — Routing Agent

Assigns:

- Department
- Officer/team

---

## Agent 8 — Resolution Agent

Analyzes repair evidence.

---

## Agent 9 — Escalation Agent

Monitors:

- SLA
- Overdue complaints
- Repeated failures

---

# 24. Technical Architecture

```text
                    CITIZEN
                       │
       ┌───────────────┼────────────────┐
       ↓               ↓                ↓
   📞 Twilio       🌐 Next.js       📱 WhatsApp
       │               │                │
       └───────────────┼────────────────┘
                       ↓
                  API Backend
                    FastAPI
                       │
              ┌────────┴────────┐
              ↓                 ↓
          AI Layer          Database
              │              PostgreSQL
       ┌──────┼──────┐           │
       ↓      ↓      ↓           ↓
      LLM   Vision  Agents     Supabase
       │             │
       └──────┬──────┘
              ↓
        Complaint Engine
              │
      ┌───────┼────────┐
      ↓       ↓        ↓
   Priority Routing  Duplicate
      │       │        │
      └───────┼────────┘
              ↓
        Officer Dashboard
              │
              ↓
        Resolution System
              │
              ↓
        Citizen Verification
```

---

# 25. Recommended Technology Stack

## Frontend

- Next.js
- TypeScript
- Tailwind CSS
- Mapbox or Google Maps

## Backend

- Python
- FastAPI

## Database

- PostgreSQL
- Supabase

## AI

- LLM API
- Vision model
- Embeddings
- Vector database where necessary

## Voice / Telephony

- Twilio
- Speech-to-Text
- Text-to-Speech

## WhatsApp

- Twilio WhatsApp API
- Webhooks

## Storage

- Supabase Storage
- S3-compatible object storage

## Agent Orchestration

- LangGraph

---

# 26. API Architecture

Possible endpoints:

```text
POST /api/complaints
GET  /api/complaints/:id
PATCH /api/complaints/:id

POST /api/complaints/:id/evidence
GET  /api/complaints/:id/evidence

POST /api/complaints/:id/resolve
POST /api/complaints/:id/reopen
POST /api/complaints/:id/verify

POST /api/whatsapp/webhook
POST /api/twilio/voice

GET /api/dashboard
GET /api/dashboard/map

POST /api/ai/classify
POST /api/ai/analyze-evidence
POST /api/ai/detect-duplicates
POST /api/ai/priority
```

---

# 27. Database Schema

## Users

```text
users
-----
id
name
phone
email
role
created_at
```

## Complaints

```text
complaints
-----------
id
citizen_id
category
description
latitude
longitude
address
landmark
priority
severity
department
assigned_officer
status
created_at
updated_at
resolved_at
closed_at
```

## Evidence

```text
evidence
--------
id
complaint_id
media_url
media_type
uploaded_by
ai_analysis
created_at
```

## Departments

```text
departments
-----------
id
name
description
sla_hours
```

## Complaint History

```text
complaint_history
-----------------
id
complaint_id
old_status
new_status
changed_by
comment
created_at
```

---

# 28. Security & Privacy

The system should:

- Protect citizen phone numbers
- Restrict officer access by department
- Secure uploaded media
- Use authenticated APIs
- Validate webhook requests
- Encrypt sensitive information
- Avoid exposing private citizen information publicly
- Maintain an audit trail for complaint changes

Citizens should be informed about how their submitted photos, videos and location data are used.

---

# 29. Hackathon MVP Scope

Do NOT attempt to build a complete city-scale system.

## Must Have

- Phone complaint
- Website complaint
- WhatsApp evidence collection
- Complaint database
- AI classification
- AI priority
- Duplicate detection
- Officer dashboard
- Resolution photo
- AI resolution verification
- Citizen confirmation
- Complaint reopening

---

## Optional

- Multiple languages
- Public transparency dashboard
- Advanced GIS
- Voice translation
- Automated reports
- Analytics
- Predictive civic issue detection

---

## Avoid During Hackathon

- Full government integration
- 30+ departments
- Training your own LLM
- City-wide production infrastructure
- Complex payment systems
- Excessive authentication complexity

Focus on a polished end-to-end prototype.

---

# 30. Killer Demo

The complete demonstration should take approximately 3–5 minutes.

## Step 1 — Phone Call

Judge calls the Twilio number.

Judge says:

> "There is an open manhole near the college entrance."

AI asks clarification questions.

---

## Step 2 — Complaint Creation

Dashboard immediately displays:

```text
🚨 CRITICAL

OPEN MANHOLE

Location:
College Entrance

AI Priority:
94/100

Status:
REGISTERED
```

---

## Step 3 — WhatsApp Evidence

Judge receives:

> Please send photos/videos showing the issue.

Judge sends a photo.

---

## Step 4 — AI Evidence Analysis

Dashboard displays:

```text
OPEN MANHOLE DETECTED

Safety Risk:
HIGH

Evidence Quality:
GOOD

AI Confidence:
93%
```

---

## Step 5 — Duplicate Detection

Simulate multiple citizens reporting the same location.

System displays:

```text
11 reports
      ↓
AI clustering
      ↓
1 underlying incident

Affected citizens:
11

Priority:
CRITICAL
```

---

## Step 6 — Officer Resolution

Officer marks:

```text
RESOLVED
```

and uploads an after-repair photo.

---

## Step 7 — AI Verification

System compares:

```text
Before
  +
After
```

AI determines whether the repair appears successful.

---

## Step 8 — Citizen Verification

Citizen receives WhatsApp:

> Is the issue actually fixed?

Judge selects:

> ❌ No

---

## Step 9 — Automatic Reopening

Dashboard immediately shows:

```text
🔴 COMPLAINT REOPENED

Reason:
Citizen rejected resolution

Action:
Supervisor escalation
```

---

# 31. Key Differentiator

namma AI is **not simply another complaint registration portal**.

Its core differentiator is:

> **Every complaint becomes an evidence-backed civic case, and a case cannot be considered truly resolved until the resolution is verified and the citizen gets the opportunity to confirm it.**

---

# 32. Hackathon Pitch

### One-Liner

> **namma AI transforms citizen voices, messages and images into verified civic incidents—and follows them all the way from complaint to confirmed resolution.**

### Short Pitch

> Citizens shouldn't need to understand government departments, fill complicated forms, or repeatedly chase officials to get a civic problem fixed.
>
> Sahaaya AI lets citizens simply call, submit a complaint online, or interact through WhatsApp. AI understands the complaint, identifies its location and severity, collects evidence, detects duplicate reports, routes the case to the right department, monitors deadlines, verifies repair evidence, and asks the citizen whether the issue was actually fixed.
>
> **We don't just track complaints. We track outcomes.**

---

# 33. Success Metrics

For the hackathon prototype, measure:

- Complaint registration time
- AI classification accuracy
- Duplicate detection accuracy
- Evidence analysis accuracy
- Department routing accuracy
- Average time to assign complaint
- SLA violation rate
- Resolution verification accuracy
- Citizen confirmation rate

---

# 34. Future Vision

The platform could eventually evolve from a **reactive complaint system** into a **predictive civic intelligence platform**.

Instead of waiting for citizens to report problems:

```text
Historical Complaints
+
Weather
+
Road Data
+
Infrastructure Data
+
Images
+
IoT Sensors
+
Traffic Data
        ↓
Predictive AI
        ↓
Potential Civic Problems
        ↓
Preventive Action
```

Example:

> "This road segment has a high probability of developing waterlogging during the next heavy rainfall."

The system could alert authorities **before citizens begin reporting the issue.**

---

# 35. Important Positioning

Sahaaya AI should be presented as:

> **An independent hackathon prototype inspired by the civic grievance and accountability problem.**

It should **not** be presented as the official Karnataka Government / BBMP / GBA Sahaaya platform or as an officially integrated government system unless an actual government integration exists.

---

# Final Product

```text
                 namma AI
       Civic Intelligence Platform

                📞 Phone
                   │
                🌐 Web
                   │
               📱 WhatsApp
                   │
                   ↓
              🤖 AI AGENTS
                   │
       ┌───────────┼───────────┐
       ↓           ↓           ↓
   Understand   Evidence    Location
       ↓           ↓           ↓
   Classify     Analyze     Verify
       └───────────┼───────────┘
                   ↓
            Duplicate Detection
                   ↓
             Priority Engine
                   ↓
            Department Routing
                   ↓
             Officer Dashboard
                   ↓
               Resolution
                   ↓
            AI Verification
                   ↓
          Citizen Confirmation
              ↙          ↘
          CLOSED       REOPENED
                         ↓
                    ESCALATION

        "Don't just report it.
             Get it resolved."
```