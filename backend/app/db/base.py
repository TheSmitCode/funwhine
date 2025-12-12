# app/db/base.py
"""
Modern SQLAlchemy 2.0 Declarative Base
with automatic __tablename__ and timestamps.
"""

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy import DateTime, func


class Base(DeclarativeBase):
    """Base class used for all models with timestamps."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
