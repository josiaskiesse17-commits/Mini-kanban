from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    engine = create_engine(f"sqlite:///{tmp_path / 'integration.db'}")
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


def auth(client: TestClient, username: str) -> dict[str, str]:
    response = client.post(
        "/auth/register", json={"username": username, "password": "password123"}
    )
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_complete_persistence_flow_and_ownership(client: TestClient) -> None:
    owner_headers = auth(client, "alice")

    board = client.post("/boards", headers=owner_headers, json={"name": "Release"}).json()
    board_id = board["id"]
    todo, progress, done = board["columns"]
    extra = client.post(
        f"/boards/{board_id}/columns", headers=owner_headers, json={"name": "Review"}
    ).json()
    renamed = client.patch(
        f"/columns/{extra['id']}", headers=owner_headers, json={"name": "QA"}
    ).json()
    assert renamed["name"] == "QA"
    column_order = client.put(
        f"/boards/{board_id}/columns/reorder",
        headers=owner_headers,
        json={"ids": [progress["id"], todo["id"], done["id"], extra["id"]]},
    )
    assert column_order.status_code == 200, column_order.text

    first = client.post(
        f"/columns/{todo['id']}/cards",
        headers=owner_headers,
        json={"title": "Ship API", "priority": "high", "due_date": "2026-09-20"},
    ).json()
    second = client.post(
        f"/columns/{todo['id']}/cards",
        headers=owner_headers,
        json={"title": "Write notes", "priority": "low", "due_date": "2026-09-22"},
    ).json()
    updated = client.patch(
        f"/cards/{first['id']}",
        headers=owner_headers,
        json={"title": "Ship API v1", "description": "Ready", "priority": "medium"},
    )
    assert updated.status_code == 200
    moved = client.post(
        f"/cards/{first['id']}/move",
        headers=owner_headers,
        json={"column_id": progress["id"], "position": 0},
    )
    assert moved.status_code == 200
    reordered = client.put(
        f"/columns/{todo['id']}/cards/reorder",
        headers=owner_headers,
        json={"ids": [second["id"]]},
    )
    assert reordered.status_code == 200

    assert client.post("/auth/logout", headers=owner_headers).status_code == 204
    login = client.post(
        "/auth/login", json={"username": "alice", "password": "password123"}
    )
    assert login.status_code == 200
    logged_in_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    persisted = client.get(f"/boards/{board_id}", headers=logged_in_headers)
    assert persisted.status_code == 200
    persisted_cards = [card for column in persisted.json()["columns"] for card in column["cards"]]
    assert {card["title"] for card in persisted_cards} == {"Ship API v1", "Write notes"}
    assert {card["priority"] for card in persisted_cards} == {"medium", "low"}

    other_headers = auth(client, "bob")
    assert client.get(f"/boards/{board_id}", headers=other_headers).status_code == 403
    assert client.get(f"/cards/{first['id']}", headers=other_headers).status_code == 403
