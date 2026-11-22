from backend.services.ai import ai_service
from backend.schemas.ai import AIComplaintAnalysis

def test_ai_classification_pothole_hazard():
    text = "Huge dangerous pothole near BMSIT main gate causing two-wheelers to fall and skid."
    analysis = ai_service.analyze_complaint(text)

    assert isinstance(analysis, AIComplaintAnalysis)
    assert analysis.category == "ROAD_DAMAGE"
    assert analysis.department == "ROADS"
    assert analysis.priority in ["HIGH", "CRITICAL"]
    assert analysis.priority_score >= 80
    assert analysis.safety_hazard is True
    assert "BMSIT" in (analysis.landmark or analysis.extracted_location or "")

def test_ai_classification_garbage_dump():
    text = "Huge pile of uncollected garbage and rotting waste opposite market complex with bad smell."
    analysis = ai_service.analyze_complaint(text)

    assert analysis.category == "GARBAGE"
    assert analysis.department == "SANITATION"
    assert analysis.priority in ["MEDIUM", "HIGH"]
    assert "market" in (analysis.landmark or analysis.extracted_location or "")

def test_ai_classification_open_manhole_critical():
    text = "Open manhole without cover near primary school. Extreme danger to children walking by."
    analysis = ai_service.analyze_complaint(text)

    assert analysis.category == "DRAINAGE"
    assert analysis.department == "DRAINAGE"
    assert analysis.priority == "CRITICAL"
    assert analysis.severity == "CRITICAL"
    assert analysis.safety_hazard is True

def test_ai_missing_info_detection():
    # Very short vague text without location
    text = "Road bad"
    analysis = ai_service.analyze_complaint(text)

    assert len(analysis.missing_info) > 0
    assert any("landmark" in m.lower() or "address" in m.lower() or "location" in m.lower() for m in analysis.missing_info)

def test_ai_structured_json_validation():
    analysis = ai_service.analyze_complaint("Broken streetlight at 5th cross", location_hint="Yelahanka New Town")
    data = analysis.model_dump()

    assert "category" in data
    assert "department" in data
    assert "priority_score" in data
    assert "summary" in data
    assert 0 <= data["priority_score"] <= 100
