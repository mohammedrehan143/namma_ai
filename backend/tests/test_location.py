from fastapi.testclient import TestClient
from backend.main import app
from backend.services.location_service import location_service

client = TestClient(app)

def test_location_geocoding_service():
    lat, lon, addr = location_service.geocode("Near BMSIT main gate, Yelahanka")
    assert round(lat, 2) == 13.13
    assert round(lon, 2) == 77.57
    assert "BMS" in addr

def test_haversine_distance_calculation():
    # Distance from BMSIT gate to BMSIT gate should be 0
    dist_zero = location_service.haversine_distance_meters(13.1345, 77.5682, 13.1345, 77.5682)
    assert dist_zero == 0.0

    # Distance between BMSIT and Yelahanka (approx 4-5 km)
    dist_km = location_service.haversine_distance_meters(13.1345, 77.5682, 13.1007, 77.5963) / 1000.0
    assert 3.0 < dist_km < 6.0

def test_location_api_geocode_endpoint():
    res = client.get("/api/location/geocode?query=Indiranagar 100ft road")
    assert res.status_code == 200
    data = res.json()
    assert "latitude" in data
    assert "longitude" in data
    assert round(data["latitude"], 2) == 12.98
    assert round(data["longitude"], 2) == 77.64

def test_location_api_markers_endpoint():
    # Submit complaint with location text only
    payload = {
        "citizen_name": "Kavitha Reddy",
        "citizen_phone": "+919876541111",
        "description": "Sewage leaking onto the road near Hebbal flyover",
        "location_text": "Hebbal flyover junction",
        "channel": "WEB"
    }
    post_res = client.post("/api/complaints", json=payload)
    assert post_res.status_code == 201
    created_id = post_res.json()["id"]

    # Verify markers contains this complaint with geocoded coordinates
    res = client.get("/api/location/markers")
    assert res.status_code == 200
    markers = res.json()
    assert isinstance(markers, list)
    target = next((m for m in markers if m["id"] == created_id), None)
    assert target is not None
    assert target["latitude"] is not None
    assert target["longitude"] is not None
    assert target["category"] == "SEWAGE"
    assert target["status"] == "REPORTED"
