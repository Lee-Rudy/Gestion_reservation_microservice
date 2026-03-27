import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from logging-services.logging.middleware import correlation_middleware


def create_app():
    app = FastAPI()
    app.middleware("http")(correlation_middleware)

    @app.get("/")
    def read_root(request: Request):
        return {"correlation_id": request.state.correlation_id}

    return app


def test_correlation_id_generated():
    app = create_app()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "correlation_id" in response.json()
    assert "X-Correlation-ID" in response.headers