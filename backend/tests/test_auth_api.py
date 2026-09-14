import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    def override_get_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_register_login_duplicate_and_logout(client: TestClient) -> None:
    registered = client.post(
        "/auth/register", json={"username": "alice", "password": "password123"}
    )
    assert registered.status_code == 201
    body = registered.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["username"] == "alice"

    duplicate = client.post(
        "/auth/register", json={"username": "alice", "password": "password123"}
    )
    assert duplicate.status_code == 409

    login = client.post(
        "/auth/login", json={"username": "alice", "password": "password123"}
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    logout = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout.status_code == 204


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    client.post("/auth/register", json={"username": "alice", "password": "password123"})

    response = client.post(
        "/auth/login", json={"username": "alice", "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_logout_rejects_missing_token(client: TestClient) -> None:
    response = client.post("/auth/logout")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_logout_rejects_invalid_token(client: TestClient) -> None:
    response = client.post(
        "/auth/logout", headers={"Authorization": "Bearer definitely-invalid"}
    )

    assert response.status_code == 401
