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


def test_board_and_column_lifecycle(client: TestClient) -> None:
    token = register(client, "alice")
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post("/boards", headers=headers, json={"name": "Work"})
    assert created.status_code == 201
    board = created.json()
    assert [column["name"] for column in board["columns"]] == [
        "To Do",
        "In Progress",
        "Done",
    ]

    board_id = board["id"]
    renamed = client.patch(
        f"/boards/{board_id}", headers=headers, json={"name": "Personal"}
    )
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Personal"

    extra = client.post(
        f"/boards/{board_id}/columns", headers=headers, json={"name": "Review"}
    )
    assert extra.status_code == 201
    extra_id = extra.json()["id"]

    column_ids = [column["id"] for column in board["columns"]]
    reordered = client.put(
        f"/boards/{board_id}/columns/reorder",
        headers=headers,
        json={"ids": [extra_id, *column_ids]},
    )
    assert reordered.status_code == 200
    assert reordered.json()[0]["id"] == extra_id

    updated_column = client.patch(
        f"/columns/{extra_id}", headers=headers, json={"name": "Reviewing"}
    )
    assert updated_column.status_code == 200
    assert updated_column.json()["name"] == "Reviewing"

    assert client.delete(f"/columns/{extra_id}", headers=headers).status_code == 204
    assert client.delete(f"/boards/{board_id}", headers=headers).status_code == 204
    assert client.get(f"/boards/{board_id}", headers=headers).status_code == 404


def test_board_list_and_missing_resources(client: TestClient) -> None:
    token = register(client, "alice")
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/boards").status_code == 401
    assert client.get("/boards", headers=headers).json() == []
    assert client.get("/boards/99999", headers=headers).status_code == 404
    assert client.post(
        "/boards/99999/columns", headers=headers, json={"name": "Invalid"}
    ).status_code == 404


def test_board_ownership_and_invalid_column_reorder(client: TestClient) -> None:
    owner_token = register(client, "alice")
    other_token = register(client, "bob")
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    other_headers = {"Authorization": f"Bearer {other_token}"}

    board = client.post("/boards", headers=owner_headers, json={"name": "Private"}).json()
    board_id = board["id"]
    column_id = board["columns"][0]["id"]

    assert client.get(f"/boards/{board_id}", headers=other_headers).status_code == 403
    assert client.patch(
        f"/boards/{board_id}", headers=other_headers, json={"name": "Stolen"}
    ).status_code == 403
    assert client.delete(f"/boards/{board_id}", headers=other_headers).status_code == 403
    assert client.patch(
        f"/columns/{column_id}", headers=other_headers, json={"name": "Stolen"}
    ).status_code == 403
    assert client.delete(f"/columns/{column_id}", headers=other_headers).status_code == 403
    assert client.put(
        f"/boards/{board_id}/columns/reorder",
        headers=other_headers,
        json={"ids": [column["id"] for column in board["columns"]]},
    ).status_code == 403

    invalid_reorder = client.put(
        f"/boards/{board_id}/columns/reorder",
        headers=owner_headers,
        json={"ids": [column_id]},
    )
    assert invalid_reorder.status_code == 422
    assert client.delete(f"/columns/{column_id}", headers=owner_headers).status_code == 204
