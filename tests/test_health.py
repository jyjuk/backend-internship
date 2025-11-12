from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/")

    assert response.status_code == 200

    json_response = response.json()
    assert json_response["status_code"] == 200
    assert json_response["detail"] == "ok"
    assert json_response["result"] == "working"


def test_health_check_response_structure():
    """Test health check response has correct structure"""
    response = client.get("/")
    json_response = response.json()

    assert "status_code" in json_response
    assert "detail" in json_response
    assert "result" in json_response
    assert len(json_response) == 3
