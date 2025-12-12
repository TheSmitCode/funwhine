# app/models/user.py
from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING, Dict

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLAlchemyEnum, JSON

from ..db.base import Base
from .enums import UserRole

# Type-checker-only imports (prevents circular imports at runtime)
if TYPE_CHECKING:
    from .intake import Intake
    from .audit import AuditLog


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(200), unique=True, index=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)

    display_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    # Role using SQLAlchemy Enum; name provided so DB type is explicit and stable
    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(UserRole, name="user_roles"),
        default=UserRole.WORKER,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # UI preference fields (new)
    ui_theme: Mapped[str] = mapped_column(String(64), default="theme-light", nullable=False)
    ui_sidebar: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ui_navbar: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ui_font_scale: Mapped[str] = mapped_column(String(16), default="normal", nullable=False)
    ui_simple_mode: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ui_features: Mapped[Dict[str, bool]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationship to Intake. Use forward-ref string so runtime doesn't require import order.
    intakes: Mapped[List["Intake"]] = relationship(
        "Intake",
        back_populates="created_by",
        foreign_keys="Intake.created_by_id",
        lazy="selectin",
    )

    # Audit logs created by user
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        role_val = getattr(self.role, "value", None)
        return f"<User id={self.id} username={self.username!r} role={role_val}>"

    def verify_password(self, plain: str) -> bool:
        """
        Verify plaintext password against stored hash using app.core.security.
        Local import avoids circular import issues.
        """
        if not self.password_hash:
            return False
        try:
            from app.core.security import verify_password as _verify_password
            return _verify_password(plain, self.password_hash)
        except Exception:
            return False
