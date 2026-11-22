from fastapi.testclient import TestClient
from backend.main import app
from backend.core.security import sanitize_text, create_access_token, verify_access_token

client = TestClient(app)

def test_security_input_sanitization():
    dirty_text = "<script>alert('xss')</script>Pothole outside <b>gate</b>"
    cleaned = sanitize_text(dirty_text)
    assert "<script>" not in cleaned
    assert "<b>" not in cleaned
    assert "Pothole outside gate" in cleaned

def test_jwt_token_creation_and_verification():
    token = create_access_token(user_id="usr-test-123", role="OFFICER")
    payload = verify_access_token(token)
    assert payload["sub"] == "usr-test-123"
    assert payload["role"] == "OFFICER"

def test_auth_login_and_me_endpoints():
    # Login as seeded officer
    login_res = client.post("/api/auth/login", json={"phone": "+919876543210"})
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    assert data["role"] == "OFFICER"
    token = data["access_token"]

    # Verify protected /api/auth/me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    user_info = me_res.json()
    assert user_info["phone"] == "+919876543210"
    assert user_info["role"] == "OFFICER"

    # Reject invalid token
    bad_res = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid-garbage-token"})
    assert bad_res.status_code == 401
