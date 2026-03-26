import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from user_service.infrastructure.database.database import Base
from user_service.infrastructure.database.models import UserModel
from user_service.infrastructure.security.password_hasher import BcryptPasswordHasher
from user_service.main import app

TEST_DB = "sqlite:///./test_user.db"
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
    from user_service.infrastructure.api.routes import get_db

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_user(client):
    user_data = {
        "name": "Test User",
        "email": "newuser@example.com",
        "password": "SecurePass@123",
        "role": "USER",
    }

    response = client.post("/users/", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "USER"
    assert "id" in data


def test_create_user_duplicate_email(client):
    user_data = {
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "SecurePass@123",
        "role": "USER",
    }

    client.post("/users/", json=user_data)
    response = client.post("/users/", json=user_data)

    assert response.status_code == 409


def test_get_all_users(client):
    client.post(
        "/users/",
        json={
            "name": "User 1",
            "email": "user1@example.com",
            "password": "Pass@123",
            "role": "USER",
        },
    )
    client.post(
        "/users/",
        json={
            "name": "User 2",
            "email": "user2@example.com",
            "password": "Pass@123",
            "role": "ADMIN",
        },
    )

    response = client.get("/users/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_user_by_id(client):
    create_response = client.post(
        "/users/",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "Pass@123",
            "role": "USER",
        },
    )
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == "test@example.com"


def test_get_nonexistent_user(client):
    response = client.get("/users/9999")

    assert response.status_code == 404


def test_update_user(client):
    create_response = client.post(
        "/users/",
        json={
            "name": "Original Name",
            "email": "original@example.com",
            "password": "Pass@123",
            "role": "USER",
        },
    )
    user_id = create_response.json()["id"]

    update_data = {"name": "Updated Name", "role": "ADMIN"}
    response = client.put(f"/users/{user_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["role"] == "ADMIN"


def test_delete_user(client):
    create_response = client.post(
        "/users/",
        json={
            "name": "Delete Me",
            "email": "delete@example.com",
            "password": "Pass@123",
            "role": "USER",
        },
    )
    user_id = create_response.json()["id"]

    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_user(client):
    response = client.delete("/users/9999")

    assert response.status_code == 404


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    if os.path.exists("./test_user.db"):
        os.remove("./test_user.db")
