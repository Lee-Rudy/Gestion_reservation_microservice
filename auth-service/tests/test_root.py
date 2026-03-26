from fastapi.testclient import TestClient

from auth_service.main import app


def test_root_returns_service_status() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "auth-service"}
