"""Tests the `/api/v1/author` endpoints."""

from fastapi.testclient import TestClient


def test_create_and_get_author(client: TestClient) -> None:
    """Tests a basic `Author` creation and fetching based on ID."""
    # create a new Author
    first_name = "Leroy"
    last_name = "Jenkins"
    name = f"{first_name} {last_name}"
    response = client.put("/api/v1/author", json={"first_name": first_name, "last_name": last_name})
    assert response.status_code == 200
    created_author = response.json()
    assert created_author["first_name"] == first_name
    assert created_author["last_name"] == last_name
    assert created_author["name"] == name

    # fetch + test the same Author
    get_response = client.get(f"/api/v1/author/{created_author['id']}")
    assert get_response.status_code == 200
    fetched_author = get_response.json()
    assert fetched_author["id"] == created_author["id"]
    assert fetched_author["first_name"] == first_name
    assert fetched_author["last_name"] == last_name
    assert fetched_author["name"] == name
