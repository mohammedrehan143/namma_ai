# Namma AI — Requirements Document

> **AI-Powered Civic Complaint, Evidence & Resolution Platform**

---

# 1. Project Overview

**Namma AI** is a multimodal civic complaint management platform that allows citizens to report civic issues through:

- 📞 Phone calls
- 🌐 Website
- 📱 WhatsApp

The system uses AI to understand complaints, classify them, determine severity, collect evidence, detect duplicate complaints, route them to the appropriate department, monitor resolution, and allow citizens to verify whether the issue was actually fixed.

### Core Principle

> **Namma AI does not just track complaints. It tracks outcomes.**

---

# 2. Objectives

The primary objectives are:

1. Make civic complaint registration simple and accessible.
2. Allow citizens to report issues using natural language.
3. Support voice-based complaint registration.
4. Automatically classify complaints using AI.
5. Automatically determine complaint priority.
6. Collect photographic/video evidence through WhatsApp.
7. Detect duplicate complaints for the same underlying issue.
8. Automatically route complaints to the appropriate department.
9. Provide officers with a centralized dashboard.
10. Track complaint status and SLA deadlines.
11. Verify resolution using before/after evidence.
12. Allow citizens to confirm or reject a resolution.
13. Automatically reopen unresolved complaints.
14. Provide transparent complaint tracking.

---

# 3. Target Users

## 3.1 Citizens

Citizens who want to report:

- Potholes
- Garbage
- Sewage problems
- Water leakage
- Streetlight problems
- Road damage
- Drainage problems
- Fallen trees
- Public infrastructure issues

---

## 3.2 Civic Officers

Officials responsible for:

- Receiving complaints
- Investigating issues
- Assigning teams
- Updating complaint status
- Uploading resolution evidence

---

## 3.3 Supervisors

Responsible for:

- Monitoring department performance
- Handling escalations
- Monitoring SLA violations
- Reassigning complaints
- Reviewing unresolved issues

---

## 3.4 System Administrator

Responsible for:

- Managing users
- Managing departments
- Managing complaint categories
- Configuring SLA rules
- Managing system configuration

---

# 4. Functional Requirements

## FR-01 — Citizen Registration

The system shall allow citizens to register using:

- Phone number
- Name
- Optional email

The system should use phone number as the primary identifier for the MVP.

---

# 5. Complaint Registration

## FR-02 — Website Complaint

The website shall allow citizens to submit a complaint.

Required information:

- Description
- Location
- Phone number

Optional:

- Category
- Photo
- Video

The system should automatically determine category and priority using AI.

---

## FR-03 — Phone Complaint

The system shall allow citizens to call a dedicated phone number.

Telephony provider:

**Twilio**

Flow:

```text
Citizen
   ↓
Twilio Number
   ↓
AI Voice Agent
   ↓
Speech Recognition
   ↓
Complaint Understanding
   ↓
Missing Information
   ↓
Complaint Creation
```

The AI shall ask follow-up questions when required information is missing.

---

# 6. AI Complaint Understanding

## FR-04 — Natural Language Understanding

The AI shall convert unstructured citizen statements into structured complaint information.

Example:

> "There is a huge pothole near the college gate and bikes are almost falling."

AI output:

```json
{
  "category": "road_damage",
  "severity": "high",
  "description": "Large pothole causing danger to vehicles",
  "location": "college gate",
  "safety_risk": true
}
```

---

# 7. Complaint Classification

## FR-05 — Automatic Category Classification

The AI shall classify complaints into supported categories.

Initial MVP categories:

```text
Road Damage
Garbage
Drainage
Sewage
Water Leakage
Streetlight
Public Infrastructure
Other
```

The administrator shall be able to modify categories.

---

# 8. Department Routing

## FR-06 — Automatic Department Assignment

The AI shall determine the appropriate department based on complaint category.

Example:

```text
Road Damage
      ↓
Road Maintenance

Garbage
      ↓
Waste Management

Sewage
      ↓
Drainage Department

Water Leakage
      ↓
Water Department

Streetlight
      ↓
Street Lighting
```

Officers/admins shall be able to override AI routing.

---

# 9. Location Management

## FR-07 — Location Capture

The system shall support multiple location methods.

### Website

- Browser GPS
- Manual address

### Phone

- Address
- Landmark
- Nearby location

### WhatsApp

- Shared location
- Address
- Landmark

The system shall convert the information into:

```text
Latitude
Longitude
Address
Landmark
```

---

# 10. Complaint ID

## FR-08 — Unique Complaint ID

Every complaint shall receive a unique identifier.

Example:

```text
SAH-10293
```

For Namma AI, a suitable format could be:

```text
NAM-10293
```

The ID shall be used across:

- Website
- WhatsApp
- Officer dashboard
- Notifications
- Complaint history

---

# 11. WhatsApp Evidence Collection

## FR-09 — Evidence Request

After complaint registration, Namma AI shall automatically send a WhatsApp message.

Example:

> Your complaint #NAM-10293 has been registered.
>
> Please send photos or videos showing the issue here.

---

## FR-10 — Evidence Upload

Citizens shall be able to send:

- Images
- Videos
- Location
- Additional text

through WhatsApp.

---

## FR-11 — Intelligent Evidence Collection

The AI shall determine whether additional evidence is required.

Example:

```text
Citizen sends photo
       ↓
AI analyzes photo
       ↓
Evidence insufficient
       ↓
AI asks for another photo
```

Example:

> Please send a wider photo showing the surrounding area.

---

# 12. Evidence Storage

## FR-12 — Evidence Association

Every uploaded file shall be associated with:

- Complaint ID
- Citizen ID
- Timestamp
- Media type

Example:

```text
Evidence
--------
ID
Complaint ID
Media URL
Media Type
Uploaded By
Timestamp
AI Analysis
```

---

# 13. AI Image Analysis

## FR-13 — Visual Complaint Analysis

The AI shall analyze uploaded images.

Supported MVP detections:

- Potholes
- Garbage
- Water accumulation
- Sewage overflow
- Road damage
- Fallen trees
- Damaged infrastructure

Example:

```text
Object:
Pothole

Size:
Large

Severity:
High

Safety Risk:
High

Evidence Quality:
Good
```

---

# 14. AI Severity Detection

## FR-14 — Severity Classification

The AI shall determine:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

based on:

- Safety risk
- Number of people affected
- Location
- Issue type
- Evidence
- Duplicate reports
- Time unresolved

---

# 15. Priority Engine

## FR-15 — Complaint Priority Score

Each complaint shall receive a priority score.

Example:

```text
Severity            30%
Safety Risk         25%
People Affected     20%
Duplicate Reports   15%
Time Unresolved     10%
```

Final output:

```text
Priority Score: 91/100
Priority: CRITICAL
```

The weighting should be configurable.

---

# 16. Duplicate Detection

## FR-16 — Duplicate Complaint Detection

The system shall identify complaints that may represent the same underlying issue.

The AI should compare:

- Location
- Description
- Category
- Images
- Time
- Existing incidents

Example:

```text
Complaint 101
Complaint 124
Complaint 137
Complaint 151
       ↓
AI clustering
       ↓
ONE INCIDENT
```

---

# 17. Citizen Impact

## FR-17 — Affected Citizen Count

The system shall track how many citizens have reported the same incident.

Example:

```text
Incident:
Pothole on Main Road

Reports:
37

Affected Citizens:
37

Priority:
CRITICAL
```

---

# 18. Officer Dashboard

## FR-18 — Dashboard

Officers shall have access to a dashboard displaying:

```text
Critical
High
Medium
Low

Pending
Assigned
In Progress
Resolved
Reopened
Closed
```

---

# 19. Map Dashboard

## FR-19 — Geographic Complaint View

The dashboard shall display complaints on a map.

Example:

```text
🔴 Critical
🟠 High
🟡 Medium
🟢 Low
```

Officers shall be able to click a marker to view complaint details.

---

# 20. Complaint Detail

## FR-20 — Complaint Details Page

The page shall display:

```text
Complaint ID
Category
Description
Location
Priority
Severity
Citizen
Evidence
AI Analysis
Assigned Department
Assigned Officer
Status
Timeline
```

---

# 21. Complaint Status

## FR-21 — Status Management

Complaints shall support:

```text
REGISTERED
ASSIGNED
ACCEPTED
IN_PROGRESS
RESOLVED
VERIFICATION_PENDING
CLOSED
REOPENED
ESCALATED
```

---

# 22. Officer Resolution

## FR-22 — Mark Complaint Resolved

An officer shall be able to mark a complaint as resolved.

The officer should provide:

- Resolution description
- After-repair photo
- Optional video
- Resolution timestamp

---

# 23. AI Resolution Verification

## FR-23 — Before/After Analysis

The AI shall compare:

```text
Before Image
     +
After Image
     ↓
AI Vision Analysis
```

Possible results:

```text
RESOLUTION LIKELY SUCCESSFUL
```

or:

```text
POSSIBLE INCOMPLETE RESOLUTION
```

The AI shall provide a confidence score.

---

# 24. Citizen Verification

## FR-24 — Citizen Resolution Confirmation

After the officer marks a complaint as resolved, the citizen shall receive a WhatsApp message.

Example:

> Complaint #NAM-10293 has been marked as resolved.
>
> Is the issue actually fixed?
>
> ✅ Yes  
> ❌ No

---

# 25. Complaint Reopening

## FR-25 — Reopen Complaint

If the citizen selects:

> No, the issue is not fixed.

The complaint shall automatically become:

```text
REOPENED
```

The system shall:

- Notify the officer
- Notify supervisor
- Preserve previous evidence
- Record citizen feedback
- Restart the resolution process

---

# 26. SLA Management

## FR-26 — SLA Configuration

Administrators shall be able to define resolution deadlines.

Example:

```text
Critical → 4 hours
High → 24 hours
Medium → 3 days
Low → 7 days
```

---

## FR-27 — SLA Monitoring

The system shall continuously track complaint deadlines.

Example:

```text
Deadline approaching
        ↓
Officer reminder
        ↓
Deadline exceeded
        ↓
Supervisor alert
        ↓
Escalation
```

---

# 27. WhatsApp Notifications

## FR-28 — Automated Notifications

Namma AI shall send notifications for:

- Complaint registration
- Evidence request
- Complaint assignment
- Status changes
- Resolution
- Verification
- Reopening
- Escalation

---

# 28. Citizen Complaint Tracking

## FR-29 — Complaint Tracking

Citizens shall be able to track complaints through:

- Website
- WhatsApp
- Complaint ID

Example:

```text
NAM-10293

Status:
In Progress

Department:
Road Maintenance

Assigned:
Officer #24

Expected Resolution:
Tomorrow, 4:00 PM
```

---

# 29. AI Agents

The platform shall use specialized AI components/agents.

## Agent 1 — Intake Agent

Handles:

- Voice
- Text
- Basic complaint understanding

---

## Agent 2 — Classification Agent

Determines:

- Category
- Department

---

## Agent 3 — Location Agent

Extracts:

- Location
- Address
- Landmark
- Coordinates

---

## Agent 4 — Evidence Agent

Analyzes:

- Images
- Videos
- Evidence quality

---

## Agent 5 — Duplicate Agent

Detects related complaints.

---

## Agent 6 — Priority Agent

Determines:

- Severity
- Safety risk
- Priority score

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
- Overdue cases
- Repeated failures

---

# 30. Notification Requirements

The system shall support:

```text
WhatsApp
SMS
Website notifications
```

For the MVP, prioritize **WhatsApp**.

---

# 31. Non-Functional Requirements

## NFR-01 — Performance

The system should respond to normal API requests within approximately:

```text
< 2 seconds
```

excluding external AI/telephony processing.

---

## NFR-02 — Availability

The MVP should remain available during the hackathon demonstration.

---

## NFR-03 — Security

The system must:

- Authenticate users
- Protect citizen data
- Secure media URLs
- Validate webhooks
- Restrict officer access
- Maintain audit logs

---

## NFR-04 — Scalability

The architecture should allow future expansion to:

- More departments
- More complaint categories
- More citizens
- Multiple cities
- Additional communication channels

---

## NFR-05 — Privacy

The platform must protect:

- Phone numbers
- Citizen identity
- Location information
- Uploaded images/videos
- Complaint history

Only authorized users should access sensitive information.

---

# 32. Technical Requirements

## Frontend

```text
Next.js
TypeScript
Tailwind CSS
```

## Backend

```text
Python
FastAPI
```

## Database

```text
PostgreSQL
Supabase
```

## AI

```text
LLM API
Vision Model
Embeddings
Vector Database
```

## Telephony

```text
Twilio
Speech-to-Text
Text-to-Speech
```

## WhatsApp

```text
Twilio WhatsApp API
Webhooks
```

## Storage

```text
Supabase Storage
```

## Maps

```text
Google Maps API
or
Mapbox
```

## Agent Framework

```text
LangGraph
```

---

# 33. Integration Requirements

## Twilio

Required for:

- Incoming phone calls
- Voice interaction
- WhatsApp messaging
- Webhooks

---

## Maps

Required for:

- Location selection
- GPS
- Geocoding
- Complaint map
- Incident clustering

---

## AI API

Required for:

- Natural language understanding
- Classification
- Priority reasoning
- Duplicate analysis
- Evidence interpretation

---

## Supabase

Required for:

- PostgreSQL database
- Authentication
- File storage
- Realtime updates

---

# 34. Database Requirements

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
severity
priority
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
created_at
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

## Incidents

```text
incidents
---------
id
category
latitude
longitude
severity
priority
affected_citizens
status
created_at
updated_at
```

---

# 35. API Requirements

```text
POST   /api/complaints
GET    /api/complaints/:id
PATCH  /api/complaints/:id

POST   /api/complaints/:id/evidence
GET    /api/complaints/:id/evidence

POST   /api/complaints/:id/resolve
POST   /api/complaints/:id/verify
POST   /api/complaints/:id/reopen

POST   /api/twilio/voice
POST   /api/twilio/whatsapp

POST   /api/ai/classify
POST   /api/ai/analyze-evidence
POST   /api/ai/detect-duplicates
POST   /api/ai/priority

GET    /api/dashboard
GET    /api/dashboard/map
```

---

# 36. MVP Requirements

The following features are mandatory for the hackathon MVP:

- [ ] Website complaint registration
- [ ] Twilio phone complaint
- [ ] AI voice complaint understanding
- [ ] WhatsApp integration
- [ ] Automatic evidence collection
- [ ] Image upload
- [ ] Evidence storage
- [ ] AI image analysis
- [ ] AI complaint classification
- [ ] AI priority scoring
- [ ] Duplicate complaint detection
- [ ] Automatic department routing
- [ ] Officer dashboard
- [ ] Complaint map
- [ ] Complaint status tracking
- [ ] Resolution photo upload
- [ ] AI resolution verification
- [ ] Citizen WhatsApp confirmation
- [ ] Complaint reopening
- [ ] SLA monitoring

---

# 37. Optional Features

If time permits:

- [ ] Kannada voice support
- [ ] Multi-language support
- [ ] Public transparency dashboard
- [ ] Advanced GIS
- [ ] SMS fallback
- [ ] Voice translation
- [ ] Predictive complaint detection
- [ ] Civic analytics
- [ ] Heatmap of recurring issues
- [ ] Automatic weekly government reports

---

# 38. Features NOT Required for MVP

Do not spend hackathon time on:

- Real government backend integration
- Full city-wide deployment
- Training a custom LLM
- 30+ departments
- Every possible complaint category
- Complex payment systems
- Advanced identity verification
- Production-scale infrastructure

The goal is a **working, polished proof of concept**.

---

# 39. Hackathon Demo Requirements

The complete demo should demonstrate:

### 1. Phone

Judge calls the Twilio number.

### 2. AI Conversation

AI understands the complaint.

### 3. Complaint Creation

Complaint appears automatically on the dashboard.

### 4. WhatsApp

Citizen receives evidence request.

### 5. Evidence

Citizen sends an image.

### 6. AI Vision

System analyzes the image.

### 7. Duplicate Detection

Multiple reports are merged into one incident.

### 8. Officer

Officer receives the complaint.

### 9. Resolution

Officer uploads an after-repair image.

### 10. AI Verification

AI analyzes before/after evidence.

### 11. Citizen Verification

Citizen receives WhatsApp confirmation.

### 12. Reopening

Citizen rejects the resolution.

### 13. Escalation

Complaint automatically reopens and escalates.

---

# 40. Success Criteria

The MVP will be considered successful if:

- A citizen can create a complaint through phone or website.
- AI can convert natural language into structured complaint data.
- Evidence can be submitted through WhatsApp.
- Evidence is linked to the correct complaint.
- AI can classify supported complaint types.
- AI can determine priority.
- Duplicate complaints can be clustered.
- Officers can manage complaints.
- Officers can submit resolution evidence.
- AI can assist with resolution verification.
- Citizens can confirm or reject resolution.
- Rejected complaints can automatically reopen.
- The entire flow can be demonstrated end-to-end.

---

# 41. Key Differentiator

Namma AI is not simply a complaint registration system.

Its key innovation is:

> **Every complaint becomes an evidence-backed civic case, and the system follows that case until the citizen has an opportunity to verify the outcome.**

---

# 42. Final Product Flow

```text
                    NAMMA AI
         Civic Intelligence Platform

                    CITIZEN
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
     📞 Phone       🌐 Website      📱 WhatsApp
        │              │              │
        └──────────────┼──────────────┘
                       ↓
                🤖 AI INTAKE
                       ↓
              Complaint Created
                       ↓
              WhatsApp Evidence
                       ↓
                AI Evidence Check
                       ↓
             Location Identification
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
                  ↙         ↘
                YES          NO
                 ↓            ↓
              CLOSED       REOPENED
                              ↓
                          ESCALATION
```

---

# 43. Product Tagline

> **Namma AI — Report it. Prove it. Track it. Get it resolved.**

---

# 44. Product Positioning

Namma AI is an **independent hackathon prototype** inspired by the civic grievance and accountability problem.

It should not be represented as an official Karnataka Government, BBMP, GBA, or Sahaaya platform unless an official integration or partnership exists.

The objective is to demonstrate how **AI, telephony, WhatsApp, computer vision, geospatial intelligence, and workflow automation** can improve civic complaint resolution.