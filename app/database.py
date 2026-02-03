"""Defines the database models/tables and contains functionality related to the R/W on these within the API."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from pydantic import computed_field
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine


class Author(SQLModel, table=True):
    """Defines an author, who says a single quote."""

    id: int | None = Field(default=None, primary_key=True)
    raw_name: str = Field(index=True, unique=True)  # will be firstname_lastname

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(id={self.id}, "
            f"raw_name={self.raw_name}, "
            f"first_name='{self.first_name}', "
            f"last_name='{self.last_name}', "
            f"name='{self.name}')"
        )

    def __hash__(self) -> int:
        return hash(self.raw_name)

    @computed_field
    @property
    def first_name(self) -> str:
        """Returns the author's first name."""
        return self.raw_name.split("_")[0]

    @computed_field
    @property
    def last_name(self) -> str:
        """Returns the author's last name."""
        return self.raw_name.split("_")[-1]

    @computed_field
    @property
    def name(self) -> str:
        """Returns the author's last name."""
        return self.raw_name.replace("_", " ").title()


class QuoteLink(SQLModel, table=True):
    """Stores the IDs of a `SingleQuote` object and a `Quote` object, for linking them."""

    single_quote_id: int | None = Field(default=None, foreign_key="singlequote.id", primary_key=True)
    quote_id: int | None = Field(default=None, foreign_key="quote.id", primary_key=True)


class SingleQuote(SQLModel, table=True):
    """Defines a single quote, which was said by a `Author`.

    Every quote is said by a `Author`, so there's an `author_id` attribute linking back to the `Author` table.
    Furthermore, a single quote may be a part of a larger quote, which can involve just one or multiple single quotes.
    Accordingly, there is a `quote` attribute which links to the larger quote object.
    """

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, author_id={self.author_id})"

    id: int | None = Field(default=None, primary_key=True)
    text: str
    author_id: int = Field(foreign_key="author.id")
    # `Relationship` doesn't do anything in the database -- it just tells SQLModel/SQLAlchemy
    # to fetch the list automatically when accessed. The `back_populates="single_quote"` tells
    author: Author = Relationship()
    quote: "Quote" = Relationship(
        back_populates="single_quotes",
        link_model=QuoteLink,
    )  # link_model points to the junction table


class Quote(SQLModel, table=True):
    """A full quote, which is a collection of one or more single quotes.

    One of these objects will link to at least one `SingleQuote` instance, but perhaps more.
    This enables "conversational" quotes, in which there are multiple quotes from a single person.
    For example: `"setup" - person_1; "punchline" - person_2`.

    To do so, there's a `single_quotes: list[SingleQuote]` attribute, which links the tables.
    """

    id: int | None = Field(default=None, primary_key=True)
    single_quotes: list[SingleQuote] = Relationship(back_populates="quote", link_model=QuoteLink)
    before_context: str | None = Field(description="The context that sets the scene for the quote.")
    after_context: str | None = Field(description="The context that for the quote, often as a punchline.")


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
