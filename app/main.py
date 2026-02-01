"""The main processing entrypoint for the API. This module will start the API and handle immediate startup tasks."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import author_router, quote_router
from app.core.logging import setup_logging
from app.core.settings import settings
from app.database import create_db_and_tables

setup_logging()

API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:  # noqa: ARG001
    """Creates the database on application startup, then yields to the main application lifecycle."""
    # Load the ML model
    create_db_and_tables()

    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(author_router, prefix=API_PREFIX)
app.include_router(quote_router, prefix=API_PREFIX)
