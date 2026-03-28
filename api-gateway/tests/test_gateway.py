from fastapi.testclient import TestClient

from api_gateway.main import app


def test_root_returns_gateway_status():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "api-gateway"
    assert "services" in data


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
