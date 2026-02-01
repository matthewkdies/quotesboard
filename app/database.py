"""Defines the database models/tables and contains functionality related to the R/W on these within the API."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from pydantic import computed_field
from sqlmodel import Field, Session, SQLModel, create_engine


class Author(SQLModel, table=True):
    """Defines a author."""

    id: int | None = Field(default=None, primary_key=True)
    first_name: str = Field(index=True)
    last_name: str

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"first_name='{self.first_name}', "
            f"last_name='{self.last_name}', "
            f"name='{self.name}')"
        )

    @computed_field
    @property
    def name(self) -> str:
        """Returns the author's full name, useful for display of a author within the templates."""
        return f"{self.first_name} {self.last_name}"


class Quote(SQLModel, table=True):
    """Defines a quote, which was said by a `Author`.

    Every quote is said by a `Author`, so
    """

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, author_id={self.author_id})"

    id: int | None = Field(default=None, primary_key=True)
    quote: str
    author_id: int = Field(foreign_key="author.id")


# TODO: configure how we actually connect to the database... likely Postgres, right?
SQLITE_FILE_NAME = "database.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

CONNECT_ARGS = {"check_same_thread": False}
ENGINE = create_engine(SQLITE_URL, connect_args=CONNECT_ARGS)


def create_db_and_tables() -> None:
    """Initializes the database and tables by creating all of the objects using the database engine."""
    SQLModel.metadata.create_all(ENGINE)


def get_session() -> Generator[Session]:
    """Yield a temporary session from the database engine, useful for making database changes within the API.

    Yields:
        A temporary database session.
    """
    with Session(ENGINE) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session, use_cache=False)]
"""Argument type for a `Session` object and fetches it automatically from `get_session`.

For example:

```python
from app.database import SessionDep

@app.post("/register")
def register_user(username: str, password: str, session: SessionDep):
    hashed = hash_password(password)
    user = User(username=username, hashed_password=hashed)
    session.add(user)
    session.commit()
    return {"msg": "User created"}
```

The underlying type of this object is:
`typing.Annotated[sqlmodel.Session, fastapi.Depends(app.database.get_session, use_cache=False)]`.
"""
