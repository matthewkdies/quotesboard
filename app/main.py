"""The main processing entrypoint for the API. This module will start the API and handle immediate startup tasks."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1 import author_router, quote_router
from app.core.logging import setup_logging
from app.core.settings import settings
from app.database import create_db_and_tables
from app.urls import views_router

setup_logging()

logger = logging.getLogger(__name__)

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
app.include_router(views_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc) -> JSONResponse:  # noqa: ANN001, ARG001
    """Logs the request validation exception to the console."""
    logger.error("Validation Error: '%s'", exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})
