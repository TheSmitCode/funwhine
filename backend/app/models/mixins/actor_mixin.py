# app/models/mixins/actor_mixin.py
"""
ActorMixin — robust, SQLAlchemy-2-safe audit mixin.

Features:
- created_by_id / updated_by_id (FK -> users.id)
- created_by / updated_by relationships (explicit foreign_keys + primaryjoin)
- created_at / updated_at timestamps (server-side defaults)
- optional name cache fields created_by_name / updated_by_name
- uses @declared_attr for all mapped attributes so it is safe as a declarative mixin
"""

from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, func
from sqlalchemy.orm import declared_attr, relationship


class ActorMixin:
    """Attach to models to record actor (user) metadata and timestamps."""

    @declared_attr
    def created_by_id(cls):
        return Column(
            Integer,
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        )

    @declared_attr
    def updated_by_id(cls):
        return Column(
            Integer,
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        )

    @declared_attr
    def created_at(cls):
        # server_default so DB can fill value when inserting through sync/async paths
        return Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        # onupdate ensures DB-level timestamp update if possible; SQLAlchemy will set on update too
        return Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    @declared_attr
    def created_by(cls):
        # import inside declared_attr to avoid circular import problems at module import time
        from app.models.user import User  # local import

        # Use explicit foreign_keys and primaryjoin so SQLAlchemy cannot be ambiguous
        return relationship(
            "User",
            foreign_keys="ActorMixin.created_by_id",
            primaryjoin="ActorMixin.created_by_id==User.id",
            back_populates="intakes",
            lazy="joined",
        )

    @declared_attr
    def updated_by(cls):
        from app.models.user import User  # local import

        return relationship(
            "User",
            foreign_keys="ActorMixin.updated_by_id",
            primaryjoin="ActorMixin.updated_by_id==User.id",
            # no back_populates on updated_by to avoid accidental two-way linkage; keep read-only
            lazy="joined",
        )

    # Optional human-readable caches (helpful for UIs and exported logs)
    @declared_attr
    def created_by_name(cls):
        return Column(String(150), nullable=True)

    @declared_attr
    def updated_by_name(cls):
        return Column(String(150), nullable=True)
