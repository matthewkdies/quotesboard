"""Configures the settings for the API based on environment variables and Docker secrets."""

import logging
from enum import Enum
from pathlib import Path
from typing import TypeVar
from uuid import UUID, uuid4

from dotenv import load_dotenv
from environ import Env
from environ.compat import ImproperlyConfigured
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()
env = Env()

APP_NAME: str = "quotesboard"
DEBUG: bool = env.bool("DEBUG", default=False)

logger = logging.getLogger(__name__)


CastType = TypeVar("CastType")


class LogLevel(Enum):
    """An Enum class for Python's logging levels."""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class DBType(Enum):
    """As Enum class for the supported database types for this app."""

    SQLITE = "sqlite"
    POSTGRES = "postgres"


class SettingNotFoundError(Exception):
    """Raised if a given setting can't be found in the environment."""

    def __init__(self, secret_path: Path, env_varname: str) -> None:  # noqa: D107
        super().__init__(f"Could not find secret file at '{secret_path!s}' or environment variable '{env_varname}'.")


def get_from_docker_secret(secret_path: Path) -> str | None:
    """Returns a secret from a Docker secrets file."""
    if not secret_path.exists():
        return None

    logger.debug(f"Attempting to read from Docker secret file at '{secret_path!s}'.")
    if not str(secret_path).startswith("/run/secrets"):
        logger.warning(f"This file doesn't look like a Docker secret file: '{secret_path!s}'.")

    with secret_path.open("r") as infile:
        return infile.read().strip()


def get_from_secret_or_env[CastType](setting_name: str, env_type: type[CastType]) -> CastType:
    """Gets a setting from a Docker secret file or from the environment variables.

    For `setting_name`, this function will try to determine the value from the following, in order:

    1. Reading the contents of `Path(f"/run/secrets/{APP_NAME}_{setting_name}")`.
    2. Reading the value of the `setting_name.upper()` environment variable.

    For example, with `setting_name="db_user"` and `APP_NAME="foo"`, it will check
    `/run/secrets/foo_db_user`, and then the env var `DB_USER` if not found at the file.

    Raises:
        SettingNotFoundError: If the setting is not configured by the filename nor the environment variables.

    Returns:
        The value of the setting from the environment.
    """
    secret_path = Path(f"/run/secrets/{APP_NAME}_{setting_name}")
    secret_value = get_from_docker_secret(secret_path)

    if secret_value is not None:
        # Cast the string from the file to the expected type
        return env_type(secret_value)

    env_varname = setting_name.upper()
    try:
        env_value = env.get_value(env_varname, cast=env_type)
    except ImproperlyConfigured:
        raise SettingNotFoundError(secret_path, env_varname) from None
    return env_value


def get_from_secret_or_env_or_none[CastType](setting_name: str, env_type: type[CastType]) -> CastType | None:
    """Calls `app.core.settings.get_from_secret_or_env` and returns the value if found, otherwise returns `None`."""
    try:
        get_from_secret_or_env(setting_name, env_type)
    except SettingNotFoundError:
        return None


class Settings(BaseSettings):
    """Contains the settings for the FastAPI application, which determine how the app will run."""

    debug: bool
    app_name: str = APP_NAME
    session_id: UUID = Field(default_factory=uuid4)
    logging_level: LogLevel = Field(default=LogLevel.DEBUG if DEBUG else LogLevel.INFO)
    db_type: DBType = Field(default=DBType.SQLITE)
    db_name: str = Field(default_factory=lambda: get_from_secret_or_env("db_name", str))
    db_user: str | None = Field(default_factory=lambda: get_from_secret_or_env_or_none("db_user", str))
    db_password: str | None = Field(default_factory=lambda: get_from_secret_or_env_or_none("db_password", str))
    db_port: int | None = Field(default=5432)
    db_hostname: str | None = Field(default="quotesboard-postgres")

    @property
    def db_url(self) -> str:
        """Generates the database URL based on the current settings."""
        if self.db_type == DBType.SQLITE:
            return f"sqlite:///./{self.db_name}.db"  # TODO: postgres?
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_hostname}:{self.db_port}/{self.db_name}"
        )


settings = Settings(debug=DEBUG)
