"""
app/db/session.py

Robust DB session management for FunWhine.

Design goals (non-minimalist):
- Async-first: use SQLAlchemy async engine and AsyncSession for FastAPI async routes.
- Sync fallback: provide a sync SessionLocal usable by admin scripts or legacy code.
- Avoid circular imports: only import "settings" and the canonical Declarative Base.
- Safe init_db(): create tables for async or sync engines without crashing under uvicorn reload.
- Expose helpers for Alembic, admin scripts, testing, and background workers.
- Rich logging and sensible defaults for pool sizing and timeouts.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Generator, AsyncGenerator, Optional, Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)

# Relative import of settings and canonical Base
from ..config import settings
from .base import Base  # canonical DeclarativeBase used across the app

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------

DATABASE_URL: str = settings.DATABASE_URL

# Defaults that can be overridden via env vars (useful in Docker/CI)
DEFAULT_POOL_SIZE = int(os.getenv("FW_DB_POOL_SIZE", "5"))
DEFAULT_MAX_OVERFLOW = int(os.getenv("FW_DB_MAX_OVERFLOW", "10"))
DEFAULT_POOL_TIMEOUT = int(os.getenv("FW_DB_POOL_TIMEOUT", "30"))  # seconds

# ---------------------------------------------------------------------
# Utilities: detect async vs sync URL and produce sync mapping
# ---------------------------------------------------------------------

def _is_async_url(url: str) -> bool:
    """Return True if the given SQLAlchemy URL contains an async driver."""
    if not url:
        return False
    u = url.lower()
    return "+aiosqlite" in u or "+asyncpg" in u or u.startswith("postgresql+async") or u.startswith("mysql+async")


def _sync_url_from_async(url: str) -> Optional[str]:
    """
    For certain async drivers (e.g., sqlite+aiosqlite), produce a compatible sync URL
    for admin scripts. Returns None if no safe mapping exists.
    """
    if not url:
        return None
    if "+aiosqlite" in url:
        return url.replace("+aiosqlite", "")
    # Note: asyncpg cannot be trivially converted to a sync driver URL here.
    return None


IS_ASYNC: bool = _is_async_url(DATABASE_URL)

# ---------------------------------------------------------------------
# Engine and sessionmaker containers (exported symbols)
# ---------------------------------------------------------------------

# Async engine (primary in async-first setups)
async_engine: Optional[AsyncEngine] = None

# Sync engine (only present when we can create a sync URL)
engine = None  # type: ignore

# Session factories
AsyncSessionLocal: Optional[async_sessionmaker] = None
SessionLocal: Optional[sessionmaker] = None

# ---------------------------------------------------------------------
# Engine creation
# ---------------------------------------------------------------------

def _make_async_engine(url: str) -> AsyncEngine:
    """
    Create and configure an async engine using the provided DATABASE_URL.
    Tune connect_args for sqlite; otherwise rely on sensible defaults.
    """
    parsed = make_url(url)
    connect_args = {}

    # Special-case SQLite async driver: small adjustments
    if parsed.drivername.startswith("sqlite"):
        # For aiosqlite the check_same_thread is irrelevant for async engine, but keep safe
        connect_args = {"check_same_thread": False}

    engine = create_async_engine(
        url,
        future=True,
        echo=settings.DEBUG,
        connect_args=connect_args,
        pool_pre_ping=True,
    )
    logger.debug("Created async engine: url=%s, echo=%s", url, settings.DEBUG)
    return engine


def _make_sync_engine(sync_url: str):
    """
    Create a synchronous engine suitable for admin scripts or Alembic.
    We use pool sizing options from environment/config when appropriate.
    """
    parsed = make_url(sync_url)
    connect_args = {}
    if parsed.drivername.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    e = create_engine(
        sync_url,
        future=True,
        echo=settings.DEBUG,
        pool_size=DEFAULT_POOL_SIZE,
        max_overflow=DEFAULT_MAX_OVERFLOW,
        pool_timeout=DEFAULT_POOL_TIMEOUT,
        connect_args=connect_args,
        pool_pre_ping=True,
    )
    logger.debug("Created sync engine for admin: url=%s", sync_url)
    return e


# Instantiate engines / sessionmakers depending on config
if IS_ASYNC:
    async_engine = _make_async_engine(DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    )

    # Try to provide a sync fallback for admin scripts if possible
    sync_url = _sync_url_from_async(DATABASE_URL)
    if sync_url:
        engine = _make_sync_engine(sync_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # Pure sync mode — create a sync engine and sessionmaker
    engine = _make_sync_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    AsyncSessionLocal = None
    async_engine = None

# ---------------------------------------------------------------------
# FastAPI dependency helpers
# ---------------------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    """
    Synchronous DB dependency (for scripts or sync endpoints).
    Usage:
        db: Session = Depends(get_db)
    Raises a clear RuntimeError if the sync SessionLocal is not available.
    """
    if SessionLocal is None:
        raise RuntimeError("Synchronous SessionLocal is not available. Are you running in async-only mode?")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async DB dependency for FastAPI endpoints.
    Usage:
        db: AsyncSession = Depends(async_get_db)
    """
    if AsyncSessionLocal is None:
        raise RuntimeError("AsyncSessionLocal is not available. Check DATABASE_URL and settings.")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ---------------------------------------------------------------------
# Initialization helpers: create metadata safely
# ---------------------------------------------------------------------

def _create_tables_sync():
    """Create tables using the sync engine (blocking)."""
    if engine is None:
        raise RuntimeError("Synchronous engine is not configured.")
    logger.info("Creating tables with sync engine...")
    Base.metadata.create_all(bind=engine)


async def _create_tables_async():
    """Create tables using the async engine by running metadata.create_all in a sync context."""
    if async_engine is None:
        raise RuntimeError("Async engine is not configured.")
    logger.info("Creating tables with async engine...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def init_db(wait_for_async_task: bool = False) -> None:
    """
    Initialize DB metadata for configured engine(s).
    Safe to call from:
      - application startup (uvicorn worker)
      - synchronous scripts (create_admin_direct.py)

    If running inside an event loop, the async metadata creation is scheduled rather
    than awaited so the server doesn't block. For scripts, asyncio.run will be used.

    Parameter:
        wait_for_async_task: if True and inside running loop, we will await metadata
            creation (useful in tests). Default False (safest for uvicorn).
    """
    # Sync-only path
    if engine is not None and not IS_ASYNC:
        logger.debug("init_db: detected sync engine; creating tables synchronously.")
        _create_tables_sync()
        return

    # Async path
    if async_engine is not None:
        async def _create_and_return():
            await _create_tables_async()

        try:
            loop = asyncio.get_running_loop()
            # If loop running (e.g., uvicorn), schedule task to avoid blocking startup
            if loop.is_running():
                task = loop.create_task(_create_and_return())
                logger.debug("init_db: scheduled async metadata creation task.")
                if wait_for_async_task:
                    # Optionally wait for the task (tests or special scripts)
                    loop.run_until_complete(task)
                return
        except RuntimeError:
            # No running loop; we'll run it synchronously via asyncio.run
            logger.debug("init_db: no running loop; calling asyncio.run to create tables.")

        asyncio.run(_create_and_return())
        return

    # If we get here, no engine could be created
    raise RuntimeError("No SQLAlchemy engine could be created. Check DATABASE_URL configuration.")


# ---------------------------------------------------------------------
# Convenience helpers for other subsystems (Alembic, CLI, admin scripts)
# ---------------------------------------------------------------------

def get_async_engine() -> AsyncEngine:
    """Return the configured AsyncEngine or raise an informative error."""
    if async_engine is None:
        raise RuntimeError("Async engine is not configured. DATABASE_URL likely points to a sync driver.")
    return async_engine


def get_sync_engine_for_admin(sync_url: Optional[str] = None):
    """
    Return a sync engine suitable for admin scripts:
        - If sync_url provided, create and return a new engine for that URL.
        - If a global sync engine is configured, return it.
        - Else try to derive from async URL (sqlite+aiosqlite -> sqlite:///).
    """
    if sync_url:
        return _make_sync_engine(sync_url)
    if engine:
        return engine
    derived = _sync_url_from_async(DATABASE_URL)
    if derived:
        return _make_sync_engine(derived)
    raise RuntimeError("No sync URL available for admin use. Provide DATABASE_SYNC_URL if needed.")


def dispose_engines() -> None:
    """Dispose both async and sync engines (useful in tests)."""
    if async_engine is not None:
        try:
            async_engine.sync_engine.dispose()
        except Exception:
            # Some async engines may not expose sync_engine; ignore safely
            pass
    if engine is not None:
        try:
            engine.dispose()
        except Exception:
            pass


# ---------------------------------------------------------------------
# Exports for convenience
# ---------------------------------------------------------------------

__all__ = [
    "DATABASE_URL",
    "IS_ASYNC",
    "async_engine",
    "engine",
    "AsyncSessionLocal",
    "SessionLocal",
    "async_get_db",
    "get_db",
    "init_db",
    "get_async_engine",
    "get_sync_engine_for_admin",
    "dispose_engines",
]
