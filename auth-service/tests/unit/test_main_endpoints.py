from auth_service.main import health, root


def test_root_returns_auth_status():
    assert root() == {"status": "auth-service"}


def test_health_returns_healthy_status():
    assert health() == {"status": "healthy"}
