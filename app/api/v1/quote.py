"""Defines endpoints related to interacting with the `Quote` object/table."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import func, select

from app import TEMPLATES_DIR
from app.api.v1.author import get_author_by_id
from app.database import Author, Quote, SessionDep, SingleQuote

quote_router = APIRouter()


templates = Jinja2Templates(directory=TEMPLATES_DIR)


@quote_router.put("/quote", response_model=Quote)
def create_quote(quote: Quote, session: SessionDep) -> Quote:
    """Creates an `Quote` in the database."""
    session.add(quote)
    session.commit()
    session.refresh(quote)
    return quote


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


@quote_router.get("/quote/{quote_id}/single_quotes", response_model=list[SingleQuote])
def get_quote_single_quotes(quote_id: int, session: SessionDep) -> list[SingleQuote]:
    """Gets the `SingleQuote` objects that comprise a `Quote` object."""
    quote: Quote = get_quote_by_id(quote_id, session)
    return quote.single_quotes


@quote_router.get("/quote/{quote_id}/author", response_model=Author)
def get_quote_author(quote_id: int, session: SessionDep) -> Author:
    """Gets a random quote from the database."""
    quote = get_quote_by_id(session, quote_id)
    statement = select(Author).where(Author.id == quote.author_id)
    author = session.exec(statement).one_or_none()
    if not author:
        raise HTTPException(status_code=500, detail="Author not found for quote with id=")
    return author
