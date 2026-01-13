from pathlib import Path
from typing import Optional
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

from contextvars import ContextVar

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    # Made optional for hosted MCP where users provide credentials per-call
    AZDO_ORG_URL: Optional[str] = None
    AZDO_PAT: Optional[str] = None
    AZDO_PROJECT: Optional[str] = None
    AZDO_REPO_ID: Optional[str] = Field(
        default=None, validation_alias=AliasChoices("AZDO_REPO_ID", "AZDO_REPO")
    )
    AZDO_DEFAULT_BRANCH: Optional[str] = "main"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore"
    )


# ContextVar to hold settings, initialized with default env vars
_settings_ctx: ContextVar[Settings] = ContextVar("settings", default=Settings())


def get_settings() -> Settings:
    """Get the current settings from context."""
    return _settings_ctx.get()

