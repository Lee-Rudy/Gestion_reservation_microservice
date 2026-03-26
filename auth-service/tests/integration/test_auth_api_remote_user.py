from fastapi.testclient import TestClient

from auth_service.main import app


class _MockResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class _MockAsyncClientSuccess:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, _url: str):
        return _MockResponse(
            200,
            {
                "email": "remote@example.com",
                "role": "ADMIN",
                # Generated with bcrypt from "Remote@123"
                "password_hash": "$2b$12$RwJfM2z1qR1xJ8I7lR8xm.8bQpVfD4wzq0QNB8qQ6w3C6m5ZZwWwq",
            },
        )


class _MockAsyncClientFailure:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, _url: str):
        raise RuntimeError("network error")


def test_login_uses_remote_user_service_when_local_user_missing(monkeypatch):
    from auth_service.infrastructure.api import routes
    from auth_service.infrastructure.security.password_hasher import BcryptPasswordHasher

    hasher = BcryptPasswordHasher()
    remote_hash = hasher.hash_password("Remote@123")

    class _DynamicMockClient(_MockAsyncClientSuccess):
        async def get(self, _url: str):
            return _MockResponse(
                200,
                {
                    "email": "remote@example.com",
                    "role": "ADMIN",
                    "password_hash": remote_hash,
                },
            )

    monkeypatch.setattr(routes.httpx, "AsyncClient", _DynamicMockClient)
    client = TestClient(app)

    response = client.post(
        "/auth/login",
        data={"username": "remote@example.com", "password": "Remote@123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body


def test_login_remote_exception_falls_back_and_returns_401(monkeypatch):
    from auth_service.infrastructure.api import routes

    monkeypatch.setattr(routes.httpx, "AsyncClient", _MockAsyncClientFailure)
    client = TestClient(app)

    response = client.post(
        "/auth/login",
        data={"username": "absent@example.com", "password": "Wrong@123"},
    )

    assert response.status_code == 401
