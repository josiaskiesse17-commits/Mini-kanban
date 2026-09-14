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


def register(client: TestClient, username: str) -> str:
    response = client.post(
        "/auth/register", json={"username": username, "password": "password123"}
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def test_card_lifecycle_move_and_reorder(client: TestClient) -> None:
    token = register(client, "alice")
    headers = {"Authorization": f"Bearer {token}"}
    board = client.post("/boards", headers=headers, json={"name": "Work"}).json()
    first_column, second_column = board["columns"][:2]

    first = client.post(
        f"/columns/{first_column['id']}/cards",
        headers=headers,
        json={"title": "First", "priority": "high", "due_date": "2026-09-14"},
    )
    second = client.post(
        f"/columns/{first_column['id']}/cards",
        headers=headers,
        json={"title": "Second", "position": 0},
    )
    assert first.status_code == 201
    assert second.status_code == 201
    first_id = first.json()["id"]
    second_id = second.json()["id"]
    assert second.json()["position"] == 0

    updated = client.patch(
        f"/cards/{first_id}", headers=headers, json={"title": "Updated", "position": 0}
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated"

    reordered = client.put(
        f"/columns/{first_column['id']}/cards/reorder",
        headers=headers,
        json={"ids": [first_id, second_id]},
    )
    assert reordered.status_code == 200
    assert [card["id"] for card in reordered.json()] == [first_id, second_id]

    moved = client.post(
        f"/cards/{first_id}/move",
        headers=headers,
        json={"column_id": second_column["id"], "position": 0},
    )
    assert moved.status_code == 200
    assert moved.json()["column_id"] == second_column["id"]
    assert moved.json()["position"] == 0

    fetched = client.get(f"/cards/{first_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["priority"] == "high"
    assert client.delete(f"/cards/{first_id}", headers=headers).status_code == 204
    assert client.get(f"/cards/{first_id}", headers=headers).status_code == 404


def test_card_relationship_and_ownership_checks(client: TestClient) -> None:
    owner_token = register(client, "alice")
    other_token = register(client, "bob")
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    other_headers = {"Authorization": f"Bearer {other_token}"}
    board = client.post("/boards", headers=owner_headers, json={"name": "Private"}).json()
    column_id = board["columns"][0]["id"]
    card = client.post(
        f"/columns/{column_id}/cards", headers=owner_headers, json={"title": "Private card"}
    ).json()

    assert client.post(
        "/columns/99999/cards", headers=owner_headers, json={"title": "Invalid"}
    ).status_code == 404
    assert client.post(
        f"/columns/{column_id}/cards", headers=other_headers, json={"title": "Stolen"}
    ).status_code == 403
    assert client.get(f"/cards/{card['id']}", headers=other_headers).status_code == 403
    assert client.patch(
        f"/cards/{card['id']}", headers=other_headers, json={"title": "Stolen"}
    ).status_code == 403
    assert client.delete(f"/cards/{card['id']}", headers=other_headers).status_code == 403
    assert client.post(
        f"/cards/{card['id']}/move",
        headers=owner_headers,
        json={"column_id": 99999, "position": 0},
    ).status_code == 404
    assert client.put(
        f"/columns/{column_id}/cards/reorder",
        headers=owner_headers,
        json={"ids": [99999]},
    ).status_code == 422
    assert client.get("/cards/99999", headers=owner_headers).status_code == 404
