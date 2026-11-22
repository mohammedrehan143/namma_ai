import uuid
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_duplicate_detection_and_incident_clustering():
    p1 = f"+9191{uuid.uuid4().hex[:8]}"
    p2 = f"+9192{uuid.uuid4().hex[:8]}"
    p3 = f"+9193{uuid.uuid4().hex[:8]}"

    # 1. Citizen 1 reports pothole near BMSIT gate
    res1 = client.post(
        "/api/complaints",
        json={
            "citizen_name": "Citizen One",
            "citizen_phone": p1,
            "description": "Deep pothole right near BMSIT main gate, vehicles skidding badly",
            "location_text": "Near BMSIT Main Gate",
            "latitude": 13.1345,
            "longitude": 77.5682,
            "category": "ROAD_DAMAGE",
            "channel": "WEB"
        }
    )
    assert res1.status_code == 201
    c1 = res1.json()
    id1 = c1["id"]

    # 2. Citizen 2 reports same issue at same location
    res2 = client.post(
        "/api/complaints",
        json={
            "citizen_name": "Citizen Two",
            "citizen_phone": p2,
            "description": "Hazardous road crater outside BMSIT college gate causing bike falls",
            "location_text": "BMSIT Gate, Yelahanka",
            "latitude": 13.1347,  # ~25 meters away
            "longitude": 77.5683,
            "category": "ROAD_DAMAGE",
            "channel": "WHATSAPP"
        }
    )
    assert res2.status_code == 201
    c2 = res2.json()
    id2 = c2["id"]

    # Both complaints should be clustered
    assert c2["cluster_id"] is not None
    cluster_id = c2["cluster_id"]
    assert cluster_id.startswith("INC-")

    # Verify Complaint 1 also has this cluster ID
    res1_updated = client.get(f"/api/complaints/{id1}")
    assert res1_updated.json()["cluster_id"] == cluster_id

    # 3. Citizen 3 reports same issue (should join existing cluster and increment count)
    res3 = client.post(
        "/api/complaints",
        json={
            "citizen_name": "Citizen Three",
            "citizen_phone": p3,
            "description": "Huge pothole at BMSIT entrance, water filled and dangerous",
            "location_text": "Opposite BMSIT gate",
            "latitude": 13.1346,
            "longitude": 77.5681,
            "category": "ROAD_DAMAGE",
            "channel": "PHONE"
        }
    )
    assert res3.status_code == 201
    c3 = res3.json()
    id3 = c3["id"]
    assert c3["cluster_id"] == cluster_id
    assert c3["priority"] == "CRITICAL"  # Priority escalated due to 3+ citizens affected

    # 4. Check Clusters API
    clusters_res = client.get("/api/clusters")
    assert clusters_res.status_code == 200
    clusters = clusters_res.json()
    assert len(clusters) >= 1
    target_cluster = next((c for c in clusters if c["id"] == cluster_id), None)
    assert target_cluster is not None
    assert target_cluster["report_count"] >= 3
    assert id1 in target_cluster["complaint_ids"]
    assert id2 in target_cluster["complaint_ids"]
    assert id3 in target_cluster["complaint_ids"]
