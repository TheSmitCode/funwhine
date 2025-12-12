# app/db/__init__.py
"""
Database package initializer for the FunWhine backend.

This module intentionally exposes a clean and stable public interface
for all database-related operations used throughout the application.

It purposely avoids importing models to prevent circular imports.
"""

from .session import (
    engine,
    async_engine,
    SessionLocal,
    AsyncSessionLocal,
    get_db,
    async_get_db,
    init_db,
)

from .base import Base

__all__ = [
    # Engines
    "engine",
    "async_engine",

    # Session factories
    "SessionLocal",
    "AsyncSessionLocal",

    # Dependency injectors
    "get_db",
    "async_get_db",

    # Base metadata
    "Base",

    # Initialization helper
    "init_db",
]
