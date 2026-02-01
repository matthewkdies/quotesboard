"""Tests the `/api/v1/quote` endpoints."""

from fastapi.testclient import TestClient

from app.database import Author


def create_author(client: TestClient) -> Author:
    """Creates a standard `Author` to use as the author for the test quotes."""
    response = client.put("/api/v1/author", json={"first_name": "Leroy", "last_name": "Jenkins"})
    response.raise_for_status()
    return Author(**response.json())


def test_create_and_get_quote(client: TestClient) -> None:
    """Tests a basic `Quote` creation and fetching based on ID."""
    # create a new user
    author = create_author(client)
    quote_string = "Test quote."
    response = client.put("/api/v1/quote", json={"quote": quote_string, "author_id": author.id})
    assert response.status_code == 200
    created_quote = response.json()
    assert created_quote["quote"] == quote_string
    assert created_quote["author_id"] == author.id

    # Fetch the same user
    get_response = client.get(f"/api/v1/quote/{created_quote['id']}")
    assert get_response.status_code == 200
    fetched_quote = get_response.json()
    assert fetched_quote["id"] == created_quote["id"]
    assert fetched_quote["quote"] == quote_string
    assert fetched_quote["author_id"] == author.id
