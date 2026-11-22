from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_demo_steps_catalog():
    res = client.get("/api/demo/steps")
    assert res.status_code == 200
    steps = res.json()
    assert len(steps) == 20
    assert steps[0]["title"] == "Citizen Calls Helpline"
    assert steps[-1]["title"] == "SLA Escalation Alert to Supervisor"

def test_full_hackathon_demo_execution():
    res = client.post("/api/demo/run-full-scenario")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["demo_complaint_id"].startswith("NMA-")
    assert data["incident_cluster_id"] is not None
    assert len(data["logs"]) >= 5
    assert any("REOPENED" in log["detail"] for log in data["logs"])
