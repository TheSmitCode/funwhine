# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import asyncio
import os
import sys

# ----------------------------------------------------------------------
# FIX FOR ModuleNotFoundError: No module named 'app'
# This block adds the project root to the system path so Python can find 
# the 'app' package when running Alembic from the FunWhine directory.
# ----------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
# ----------------------------------------------------------------------

# --- Project-Specific Imports ---
# Import the settings module to configure the database URL
from app.config import settings
# FIX: Circular import fix. We import Base directly from its definition source.
from app.db.base import Base  # The canonical Base definition
# Import all models to ensure they are discovered by Alembic
import app.models
from app.db.session import async_engine, engine, IS_ASYNC, DATABASE_URL

# This is the Base class that our models inherit from. Alembic will use the .metadata
# attribute of this object to determine the current state of the database models.
target_metadata = Base.metadata

# --- Standard Alembic Configuration ---
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# set the SQLAlchemy URL here, overridden by settings
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here translate to
    outputting SQL statements to standard output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        as_version_batch=True, # Recommended for PostgreSQL when running offline
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario, we need to create an Engine
    and associate a connection with the context.
    """
    connectable = async_engine if IS_ASYNC else engine

    if connectable is None:
        raise Exception("Database engine is not initialized.")

    if IS_ASYNC:
        # Async mode
        async def run_async_migrations():
            async with connectable.begin() as connection:
                await connection.run_sync(do_run_migrations)

        asyncio.run(run_async_migrations())
    else:
        # Sync mode
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata
            )
            with context.begin_transaction():
                context.run_migrations()


def do_run_migrations(connection):
    """Configuration for running migrations."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()