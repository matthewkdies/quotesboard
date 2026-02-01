"""Defines endpoints related to interacting with the `Author` object/table."""

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.database import Author, Quote, SessionDep

author_router = APIRouter()


@author_router.put("/author", response_model=Author)
def create_author(author: Author, session: SessionDep) -> Author:
    """Creates an `Author` in the database."""
    session.add(author)
    session.commit()
    session.refresh(author)
    return author


@author_router.get("/author/{author_id}", response_model=Author)
def get_author_by_id(author_id: int, session: SessionDep) -> Author:
    """Gets the `Author` from the database with the given ID."""
    statement = select(Author).where(Author.id == author_id)
    author = session.exec(statement).one_or_none()
    if not author:
        raise HTTPException(status_code=404, detail=f"Author with id={author_id} not found.")
    return author


@author_router.get("/author/{author_id}/random", response_model=Quote)
def get_random_quote_from_author(author_id: int, session: SessionDep) -> Quote:
    """Gets a random quote from the database said by the given author."""
    author = get_author_by_id(author_id)
    quotes_by_author = select(Quote).where(Quote.author_id == author.id)
    random_quote_by_author = quotes_by_author.order_by(func.random())
    return session.exec(random_quote_by_author).one()
