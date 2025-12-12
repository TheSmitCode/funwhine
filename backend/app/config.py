from __future__ import annotations
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import secrets
import os
from typing import Optional

# Project layout
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = PROJECT_ROOT / "config" / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(DEFAULT_ENV_FILE) if DEFAULT_ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App metadata
    APP_NAME: str = "FunWhine"
    PROJECT_NAME: Optional[str] = None
    VERSION: str = "0.0.1"
    DESCRIPTION: str = "FunWhine API - viticulture & winery management"

    # API version prefix
    API_V1_STR: str = "/api/v1"

    # Debug / runtime mode
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"

    # JWT / security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Cookie / session defaults
    ACCESS_TOKEN_COOKIE_NAME: str = "access_token_cookie"
    COOKIE_HTTPONLY: bool = True
    COOKIE_SECURE: bool = False  # Set to True in production
    COOKIE_SAMESITE: str = "lax"  # Use "none" for dev with cross-site, "lax"/"strict" for prod

    # CORS - Frontend origin (set in .env for production)
    FRONTEND_ORIGIN: Optional[str] = None  # Fallback: http://localhost:3000

    # Bootstrap/admin
    BOOTSTRAP_PASSWORD: Optional[str] = None
    BOOTSTRAP_ADMIN_PASSWORD: Optional[str] = None
    BOOTSTRAP_ADMIN_USERNAME: Optional[str] = None

    # Logging / misc
    LOG_LEVEL: str = "INFO"

    def __init__(self, **values):
        super().__init__(**values)
        if self.PROJECT_NAME is None:
            object.__setattr__(self, "PROJECT_NAME", self.APP_NAME)

        # Normalize bootstrap password
        if not self.BOOTSTRAP_PASSWORD and self.BOOTSTRAP_ADMIN_PASSWORD:
            object.__setattr__(self, "BOOTSTRAP_PASSWORD", self.BOOTSTRAP_ADMIN_PASSWORD)
        if not self.BOOTSTRAP_PASSWORD:
            env_v = os.getenv("BOOTSTRAP_PASSWORD") or os.getenv("BOOTSTRAP_ADMIN_PASSWORD")
            if env_v:
                object.__setattr__(self, "BOOTSTRAP_PASSWORD", env_v)

    @property
    def is_production(self) -> bool:
        return not bool(self.DEBUG)


# Instantiate settings
settings = Settings()

# Normalize sqlite URL to async if needed
if settings.DATABASE_URL.startswith("sqlite:///") and "+aiosqlite" not in settings.DATABASE_URL:
    settings.DATABASE_URL = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

# Debug print
if settings.DEBUG:
    print(
        f"[settings] Loaded config: DEBUG={settings.DEBUG}, "
        f"DB={settings.DATABASE_URL}, API_PREFIX={settings.API_V1_STR}, "
        f"APP={settings.PROJECT_NAME}, VERSION={settings.VERSION}"
    )
