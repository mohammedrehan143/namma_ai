import re
from typing import Optional
from backend.services.ai.base import BaseAIService
from backend.schemas.ai import AIComplaintAnalysis, AIEvidenceAnalysis, AIResolutionVerification
from backend.core.logging import logger

class MockAIService(BaseAIService):
    """Deterministic, high-fidelity AI engine for instant offline execution and demo reliability."""

    def analyze_complaint(self, text: str, location_hint: Optional[str] = None) -> AIComplaintAnalysis:
        logger.info(f"MockAIService analyzing complaint: '{text[:60]}...'")
        text_lower = text.lower()
        loc_hint_lower = (location_hint or "").lower()
        combined = f"{text_lower} {loc_hint_lower}"

        # 1. Category and Department identification
        if any(w in combined for w in ["pothole", "crater", "asphalt", "tar", "road damage", "speed breaker"]):
            category = "ROAD_DAMAGE"
            department = "ROADS"
            base_score = 80
            issue_name = "Road Pothole Hazard"
        elif any(w in combined for w in ["garbage", "trash", "waste", "dump", "debris", "litter", "rubbish"]):
            category = "GARBAGE"
            department = "SANITATION"
            base_score = 65
            issue_name = "Garbage Accumulation"
        elif any(w in combined for w in ["manhole", "drain", "gutter", "waterlogging", "stormwater", "overflow"]):
            category = "DRAINAGE"
            department = "DRAINAGE"
            base_score = 85
            issue_name = "Drainage Overflow / Open Manhole"
        elif any(w in combined for w in ["sewage", "stink", "septic", "foul smell", "black water"]):
            category = "SEWAGE"
            department = "DRAINAGE"
            base_score = 85
            issue_name = "Sewage Contamination"
        elif any(w in combined for w in ["water leak", "pipeline", "pipe burst", "drinking water", "valve"]):
            category = "WATER_LEAK"
            department = "WATER"
            base_score = 70
            issue_name = "Potable Pipeline Burst"
        elif any(w in combined for w in ["streetlight", "street light", "dark", "lamp", "pole", "wire"]):
            category = "STREETLIGHT"
            department = "ELECTRICAL"
            base_score = 50
            issue_name = "Non-functional Street Lighting"
        elif any(w in combined for w in ["tree", "branch", "bench", "park", "footpath", "sidewalk"]):
            category = "PUBLIC_INFRA"
            department = "PUBLIC_WORKS"
            base_score = 45
            issue_name = "Public Infrastructure Damage"
        else:
            category = "OTHER"
            department = "PUBLIC_WORKS"
            base_score = 40
            issue_name = "Civic Grievance"

        # 2. Hazard & Severity Engine
        hazard_keywords = ["danger", "accident", "skid", "fall", "injury", "school", "hospital", "urgent", "huge", "severe", "deep", "children"]
        is_hazard = any(hk in combined for hk in hazard_keywords)
        if is_hazard:
            base_score = min(100, base_score + 18)

        if base_score >= 85:
            severity = "CRITICAL"
            priority = "CRITICAL"
        elif base_score >= 70:
            severity = "HIGH"
            priority = "HIGH"
        elif base_score >= 50:
            severity = "MEDIUM"
            priority = "MEDIUM"
        else:
            severity = "LOW"
            priority = "LOW"

        # 3. Location extraction & landmark identification
        extracted_location = location_hint
        landmark = None
        landmark_match = re.search(
            r"(?:near|opposite|beside|next to|at|behind)\s+([A-Za-z0-9\s\-]+?)(?=\s+(?:causing|where|with|and|is|are|due|facing|,|\.|$))",
            text,
            re.IGNORECASE
        )
        if landmark_match:
            landmark = landmark_match.group(1).strip()
            if not extracted_location:
                extracted_location = landmark
        elif location_hint:
            extracted_location = location_hint

        # 4. Missing Information Detection
        missing = []
        if not extracted_location and not landmark:
            missing.append("Specific street address or nearby landmark")
        if len(text.split()) < 4:
            missing.append("Detailed visual description of defect extent")

        # 5. Summary generation
        summary = f"{issue_name} reported"
        if landmark:
            summary += f" near {landmark}"
        elif extracted_location:
            summary += f" at {extracted_location}"

        return AIComplaintAnalysis(
            category=category,
            department=department,
            severity=severity,
            priority=priority,
            priority_score=base_score,
            summary=summary[:180],
            extracted_location=extracted_location,
            landmark=landmark,
            safety_hazard=is_hazard,
            missing_info=missing,
            confidence=0.96,
            ai_provider="mock_engine"
        )

    def analyze_evidence(self, image_path_or_bytes: str, description: str) -> AIEvidenceAnalysis:
        desc_lower = description.lower()
        if "pothole" in desc_lower or "road" in desc_lower:
            issue_type = "POTHOLE"
            visual_desc = "Large crater with exposed aggregates in active carriage lane."
            sev = "HIGH"
        elif "garbage" in desc_lower or "waste" in desc_lower:
            issue_type = "GARBAGE_DUMP"
            visual_desc = "Accumulated solid municipal waste overflowing onto public walkway."
            sev = "MEDIUM"
        elif "drain" in desc_lower or "manhole" in desc_lower:
            issue_type = "DRAINAGE_CLOG"
            visual_desc = "Clogged drain grating with water stagnation hazard."
            sev = "HIGH"
        else:
            issue_type = "OTHER"
            visual_desc = "Physical civic defect matching reported description."
            sev = "MEDIUM"

        return AIEvidenceAnalysis(
            issue_detected=True,
            issue_type=issue_type,
            matches_complaint=True,
            confidence=0.94,
            severity=sev,
            visual_description=visual_desc,
            quality_score=0.92,
            ai_provider="mock_engine"
        )

    def verify_resolution(self, before_image: str, after_image: str, description: str) -> AIResolutionVerification:
        return AIResolutionVerification(
            resolution_likely_complete=True,
            confidence=0.92,
            remaining_issue=None,
            is_same_location=True,
            notes="Surfacing is restored, compacted and uniform with adjacent road plane.",
            audit_flag="PASSED",
            ai_provider="mock_engine"
        )
