"""Configures the logging for the API."""

import logging

from .settings import settings


def setup_logging() -> None:
    """Configures the logging for the API."""
    logging.basicConfig(level=settings.logging_level.value, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
