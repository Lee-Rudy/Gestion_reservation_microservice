import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from auth_service.infrastructure.database.database import Base
from auth_service.infrastructure.database.models import UserModel
from auth_service.infrastructure.security.password_hasher import BcryptPasswordHasher
from auth_service.main import app

TEST_DB = "sqlite:///./test_auth.db"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    from auth_service.infrastructure.api.routes import get_db

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def create_test_user(test_db):
    db = TestingSessionLocal()
    hasher = BcryptPasswordHasher()

    user = UserModel(
        name="Test User",
        email="test@example.com",
        password_hash=hasher.hash_password("Test@123"),
        role="USER",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def test_login_success(client, create_test_user):
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "Test@123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, create_test_user):
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "WrongPassword"},
    )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_verify_token_success(client, create_test_user):
    login_response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "Test@123"},
    )
    token = login_response.json()["access_token"]

    verify_response = client.get(
        "/auth/verify", headers={"Authorization": f"Bearer {token}"}
    )

    assert verify_response.status_code == 200
    data = verify_response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "USER"


def test_verify_invalid_token(client):
    response = client.get(
        "/auth/verify", headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    if os.path.exists("./test_auth.db"):
        try:
            os.remove("./test_auth.db")
        except PermissionError:
            pass
