from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_dashboard_stats_endpoint():
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    stats = res.json()

    assert "total" in stats
    assert "open" in stats
    assert "in_progress" in stats
    assert "resolved" in stats
    assert "reopened" in stats
    assert "critical" in stats
    assert "high" in stats
    assert "sla_breached" in stats
    assert stats["total"] >= 0

def test_dashboard_complaints_filtering():
    # Filter by priority
    res = client.get("/api/complaints?priority=CRITICAL")
    assert res.status_code == 200
    data = res.json()
    assert all(item["priority"] == "CRITICAL" for item in data["items"])

    # Filter by department
    res_dept = client.get("/api/complaints?department_id=ROADS")
    assert res_dept.status_code == 200
    data_dept = res_dept.json()
    assert all(item["department_id"] == "ROADS" for item in data_dept["items"])
