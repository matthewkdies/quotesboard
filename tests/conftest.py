"""Defines pytest fixtures that are available for all tests. This includes the following.

- session: Creates an in-memory database, creates all models, and yields a session for interaction with it.
- client: Overrides the app's `get_session` function with the above, and configures and yields a `fastapi.testclient.TestClient` for interaction with the app and the temporary test database.
"""  # noqa: E501

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# import the main module before creating engine to ensure all models are in memory first
# per FastAPI docs (https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#import-table-models)
from app.database import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient]:
    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
