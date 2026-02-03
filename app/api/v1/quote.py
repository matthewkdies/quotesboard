"""Defines endpoints related to interacting with the `Quote` object/table."""

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.database import Author, Quote, SessionDep

quote_router = APIRouter()


# @quote_router.put("/quote", response_model=Quote)
# def create_quote(quote: Quote, session: SessionDep) -> Quote:
#     """Creates an `Quote` in the database."""
#     session.add(quote)
#     session.commit()
#     session.refresh(quote)
#     return quote


def get_random_quote(session: SessionDep) -> Quote:
    """Gets a random quote from the database."""
    random_quote_statement = select(Quote).order_by(func.random())
    quote: Quote | None = session.exec(random_quote_statement).first()
    if not quote:
        raise HTTPException(status_code=500, detail="This isn't supposed to happen. Please try again!")
    return quote


@quote_router.get("/quote/random", response_class=HTMLResponse)
def get_random_quote_fragment(request: Request, session: SessionDep) -> HTMLResponse:
    """Corresponds with the `partials/quote_fragment.html` template to create the quote fragment HTML."""
    quote = get_random_quote(session)
    author: Author = get_author_by_id(quote.single_quotes[-1].author_id, session)
    return templates.TemplateResponse(
        "partials/quote_fragment.html",
        {"request": request, "quote": quote, "author": author},
    )


@quote_router.get("/quote/{quote_id}", response_model=Quote)
def get_quote_by_id(quote_id: int, session: SessionDep) -> Quote:
    """Gets the `Quote` from the database with the given ID."""
    statement = select(Quote).where(Quote.id == quote_id)
    quote: Quote | None = session.exec(statement).one_or_none()
    if not quote:
        raise HTTPException(status_code=404, detail=f"Quote with id={quote_id} not found.")
    return quote


@quote_router.get("/quote/{quote_id}/author", response_model=Author)
def get_quote_author(quote_id: int, session: SessionDep) -> Author:
    """Gets a random quote from the database."""
    quote = get_quote_by_id(session, quote_id)
    statement = select(Author).where(Author.id == quote.author_id)
    author = session.exec(statement).one_or_none()
    if not author:
        raise HTTPException(status_code=500, detail="Author not found for quote with id=")
    return author
