-- ==============================================================================
-- Namma AI — Supabase PostgreSQL Schema & Seed Data
-- ==============================================================================
-- You can run this entire script directly in the Supabase Dashboard SQL Editor
-- (Dashboard -> SQL Editor -> New query -> Paste and click 'Run').
-- ==============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------------------------
-- 1. DEPARTMENTS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS departments (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    contact_email VARCHAR(120),
    default_sla_hours INTEGER NOT NULL DEFAULT 48
);

-- ------------------------------------------------------------------------------
-- 2. COMPLAINT CATEGORIES
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS complaint_categories (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    department_id VARCHAR(50) NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    default_priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM'
);

-- ------------------------------------------------------------------------------
-- 3. SLA RULES
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sla_rules (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    department_id VARCHAR(50) NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    priority VARCHAR(20) NOT NULL,
    max_resolution_hours INTEGER NOT NULL,
    warning_threshold_hours INTEGER NOT NULL
);

-- ------------------------------------------------------------------------------
-- 4. USERS & STAFF
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    phone VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100),
    email VARCHAR(120),
    role VARCHAR(20) NOT NULL DEFAULT 'CITIZEN',
    department_id VARCHAR(50) REFERENCES departments(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);

-- ------------------------------------------------------------------------------
-- 5. INCIDENT CLUSTERS (Spatial-Temporal Grouping)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS incident_clusters (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    center_latitude DOUBLE PRECISION NOT NULL,
    center_longitude DOUBLE PRECISION NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    report_count INTEGER NOT NULL DEFAULT 1,
    first_reported_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_reported_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_cluster_category ON incident_clusters(category);
CREATE INDEX IF NOT EXISTS idx_cluster_status ON incident_clusters(status);
CREATE INDEX IF NOT EXISTS idx_cluster_coords ON incident_clusters(center_latitude, center_longitude);

-- ------------------------------------------------------------------------------
-- 6. COMPLAINTS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS complaints (
    id VARCHAR(30) PRIMARY KEY,
    citizen_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    cluster_id VARCHAR(50) REFERENCES incident_clusters(id) ON DELETE SET NULL,
    department_id VARCHAR(50) REFERENCES departments(id) ON DELETE SET NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'OTHER',
    raw_description TEXT NOT NULL,
    ai_summary TEXT,
    severity VARCHAR(20) DEFAULT 'MEDIUM',
    priority VARCHAR(20) DEFAULT 'MEDIUM',
    priority_score INTEGER DEFAULT 50,
    location_text VARCHAR(255),
    landmark VARCHAR(255),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    status VARCHAR(30) NOT NULL DEFAULT 'REPORTED',
    channel VARCHAR(20) DEFAULT 'WEB',
    sla_deadline TIMESTAMPTZ,
    is_sla_breached BOOLEAN DEFAULT FALSE,
    assigned_officer_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    reopen_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_complaints_citizen ON complaints(citizen_id);
CREATE INDEX IF NOT EXISTS idx_complaints_cluster ON complaints(cluster_id);
CREATE INDEX IF NOT EXISTS idx_complaints_dept ON complaints(department_id);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);
CREATE INDEX IF NOT EXISTS idx_complaints_priority ON complaints(priority);
CREATE INDEX IF NOT EXISTS idx_complaints_category ON complaints(category);
CREATE INDEX IF NOT EXISTS idx_complaints_created ON complaints(created_at);
CREATE INDEX IF NOT EXISTS idx_complaints_sla_breached ON complaints(is_sla_breached);
CREATE INDEX IF NOT EXISTS idx_complaint_geo ON complaints(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_complaint_status_prio ON complaints(status, priority);

-- ------------------------------------------------------------------------------
-- 7. EVIDENCE (Photos & Multimodal Proof)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS evidence (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    complaint_id VARCHAR(30) NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
    evidence_type VARCHAR(30) DEFAULT 'CITIZEN_INITIAL',
    media_url VARCHAR(500) NOT NULL,
    media_type VARCHAR(20) DEFAULT 'IMAGE',
    ai_analysis JSONB,
    ai_confidence DOUBLE PRECISION,
    is_valid_evidence BOOLEAN DEFAULT TRUE,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_evidence_complaint ON evidence(complaint_id);

-- ------------------------------------------------------------------------------
-- 8. RESOLUTIONS & VERIFICATION
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS resolutions (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    complaint_id VARCHAR(30) NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
    officer_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    officer_notes TEXT,
    after_media_url VARCHAR(500),
    ai_verification JSONB,
    ai_verified BOOLEAN DEFAULT FALSE,
    citizen_feedback VARCHAR(30) DEFAULT 'PENDING',
    citizen_rejection_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_resolutions_complaint ON resolutions(complaint_id);

-- ------------------------------------------------------------------------------
-- 9. COMPLAINT EVENTS (Audit Trail)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS complaint_events (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    complaint_id VARCHAR(30) NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    old_status VARCHAR(30),
    new_status VARCHAR(30),
    actor_type VARCHAR(30) DEFAULT 'SYSTEM',
    actor_id VARCHAR(36),
    details TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_events_complaint ON complaint_events(complaint_id);

-- ------------------------------------------------------------------------------
-- 10. NOTIFICATIONS LOG
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    complaint_id VARCHAR(30) REFERENCES complaints(id) ON DELETE CASCADE,
    recipient_phone VARCHAR(20) NOT NULL,
    channel VARCHAR(20) DEFAULT 'WHATSAPP',
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'SENT',
    sent_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_notifications_complaint ON notifications(complaint_id);

-- ==============================================================================
-- SEED MASTER DATA
-- ==============================================================================

-- 1. Departments
INSERT INTO departments (id, name, description, default_sla_hours) VALUES
('ROADS', 'Road Maintenance & Infrastructure', 'Potholes, asphalt damage, road cave-ins, footpaths', 24),
('SANITATION', 'Solid Waste Management', 'Garbage dumps, debris, uncollected waste', 12),
('DRAINAGE', 'Stormwater & Drain Department', 'Blocked drains, open manholes, stormwater flooding', 12),
('WATER', 'Water Supply & Pipeline Maintenance', 'Pipe bursts, contaminated water, leakage', 18),
('ELECTRICAL', 'Street Lighting & Power Grid', 'Broken streetlights, hanging wires, electrical hazards', 24),
('PUBLIC_WORKS', 'Public Works & Parks', 'Fallen trees, broken fences, public property damage', 48)
ON CONFLICT (id) DO NOTHING;

-- 2. SLA Rules
INSERT INTO sla_rules (id, department_id, priority, max_resolution_hours, warning_threshold_hours) VALUES
('sla-roads-crit', 'ROADS', 'CRITICAL', 4, 2),
('sla-roads-high', 'ROADS', 'HIGH', 24, 18),
('sla-roads-med', 'ROADS', 'MEDIUM', 48, 36),
('sla-roads-low', 'ROADS', 'LOW', 72, 60),
('sla-san-crit', 'SANITATION', 'CRITICAL', 4, 2),
('sla-san-high', 'SANITATION', 'HIGH', 24, 18),
('sla-san-med', 'SANITATION', 'MEDIUM', 48, 36),
('sla-san-low', 'SANITATION', 'LOW', 72, 60),
('sla-drain-crit', 'DRAINAGE', 'CRITICAL', 4, 2),
('sla-drain-high', 'DRAINAGE', 'HIGH', 24, 18),
('sla-drain-med', 'DRAINAGE', 'MEDIUM', 48, 36),
('sla-drain-low', 'DRAINAGE', 'LOW', 72, 60),
('sla-water-crit', 'WATER', 'CRITICAL', 4, 2),
('sla-water-high', 'WATER', 'HIGH', 24, 18),
('sla-water-med', 'WATER', 'MEDIUM', 48, 36),
('sla-water-low', 'WATER', 'LOW', 72, 60),
('sla-elec-crit', 'ELECTRICAL', 'CRITICAL', 4, 2),
('sla-elec-high', 'ELECTRICAL', 'HIGH', 24, 18),
('sla-elec-med', 'ELECTRICAL', 'MEDIUM', 48, 36),
('sla-elec-low', 'ELECTRICAL', 'LOW', 72, 60),
('sla-pw-crit', 'PUBLIC_WORKS', 'CRITICAL', 4, 2),
('sla-pw-high', 'PUBLIC_WORKS', 'HIGH', 24, 18),
('sla-pw-med', 'PUBLIC_WORKS', 'MEDIUM', 48, 36),
('sla-pw-low', 'PUBLIC_WORKS', 'LOW', 72, 60)
ON CONFLICT (id) DO NOTHING;

-- 3. Complaint Categories
INSERT INTO complaint_categories (id, name, description, department_id, default_priority) VALUES
('ROAD_DAMAGE', 'Road Damage & Potholes', 'Potholes, cracked asphalt, road cave-ins', 'ROADS', 'HIGH'),
('GARBAGE', 'Garbage & Waste Accumulation', 'Overflowing bins, illegal garbage dumping', 'SANITATION', 'MEDIUM'),
('DRAINAGE', 'Stormwater Drainage & Manholes', 'Blocked storm drains, open hazardous manholes', 'DRAINAGE', 'HIGH'),
('SEWAGE', 'Sewage Leakage & Overflow', 'Sewage line leaks, foul odor, wastewater puddles', 'DRAINAGE', 'HIGH'),
('WATER_LEAK', 'Water Pipeline Leakage', 'Fresh water pipeline bursts, supply disruptions', 'WATER', 'MEDIUM'),
('STREETLIGHT', 'Street Lighting', 'Broken streetlights, unlit stretches, wire issues', 'ELECTRICAL', 'LOW'),
('PUBLIC_INFRA', 'Public Infrastructure & Trees', 'Fallen tree branches, damaged footpaths', 'PUBLIC_WORKS', 'LOW'),
('OTHER', 'General Civic Issues', 'Other municipal and civic grievances', 'PUBLIC_WORKS', 'LOW')
ON CONFLICT (id) DO NOTHING;

-- 4. Demo Staff Accounts
INSERT INTO users (id, name, phone, email, role, department_id) VALUES
('usr-officer-roads', 'Officer Vikram Sharma', '+919876543210', 'vikram.roads@namma.gov.in', 'OFFICER', 'ROADS'),
('usr-supervisor', 'Supervisor Ananya Rao', '+919876543211', 'ananya.sup@namma.gov.in', 'SUPERVISOR', 'ROADS'),
('usr-admin', 'Admin Control', '+919876543212', 'admin@namma.gov.in', 'ADMIN', NULL)
ON CONFLICT (phone) DO NOTHING;
