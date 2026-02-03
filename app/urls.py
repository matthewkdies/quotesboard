"""The main backend functionality for the front-end templates and views in the website."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app import TEMPLATES_DIR
from app.api.v1.quote import get_random_quote
from app.database import SessionDep

views_router = APIRouter()

templates = Jinja2Templates(directory=TEMPLATES_DIR)


@views_router.get("/", response_class=HTMLResponse)
def index(request: Request, session: SessionDep) -> HTMLResponse:
    """Routes the index, which displays a random quote from the database."""
    random_quote = get_random_quote(session)
    return templates.TemplateResponse(name="index.html", context={"request": request, "quote": random_quote})
