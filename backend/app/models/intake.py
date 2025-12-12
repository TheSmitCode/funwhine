# app/models/intake.py
from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Import the canonical Declarative Base (relative import to avoid duplication)
from ..db.base import Base

# TYPE_CHECKING imports so static type checkers / Pylance see forward refs without runtime imports
if TYPE_CHECKING:
    from .blocks import Block
    from .user import User
    from .fruit import Fruit
    from .lab import LabResult


# ---------------------------------------------------------------------
# Intake (the primary grape intake / crush event)
# ---------------------------------------------------------------------
class Intake(Base):
    __tablename__ = "intakes"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign keys
    block_id: Mapped[Optional[int]] = mapped_column(ForeignKey("blocks.id"), nullable=True, index=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Core data
    weight_kg: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    # block.intakes <-> Intake.block
    block = relationship("Block", back_populates="intakes", lazy="selectin")

    # user.intakes <-> Intake.created_by
    created_by = relationship(
        "User",
        back_populates="intakes",
        foreign_keys=[created_by_id],
        lazy="selectin",
    )

    # Components (Upper / Middle / Bottom etc)
    components: Mapped[List["IntakeComponent"]] = relationship(
        "IntakeComponent",
        back_populates="intake",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Additions (SO2, nutrients, enzymes...)
    additions: Mapped[List["Addition"]] = relationship(
        "Addition",
        back_populates="intake",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Fruit components (smaller granular records)
    fruits: Mapped[List["Fruit"]] = relationship(
        "Fruit",
        back_populates="intake",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Lab results attached to this intake
    lab_results: Mapped[List["LabResult"]] = relationship(
        "LabResult",
        back_populates="intake",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Intake id={self.id} block_id={self.block_id} weight_kg={self.weight_kg} created_by={self.created_by_id}>"


# ---------------------------------------------------------------------
# IntakeComponent (sub-parts of the intake)
# ---------------------------------------------------------------------
class IntakeComponent(Base):
    __tablename__ = "intake_components"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    intake_id: Mapped[int] = mapped_column(ForeignKey("intakes.id"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float)

    intake = relationship(
        "Intake",
        back_populates="components",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<IntakeComponent id={self.id} name={self.name} intake_id={self.intake_id}>"


# ---------------------------------------------------------------------
# Addition (e.g. SO2, yeast nutrients, tannin additions)
# ---------------------------------------------------------------------
class Addition(Base):
    __tablename__ = "additions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    intake_id: Mapped[int] = mapped_column(ForeignKey("intakes.id"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[Optional[float]] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String(50))

    intake = relationship(
        "Intake",
        back_populates="additions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        unit = f" {self.unit}" if self.unit else ""
        return f"<Addition id={self.id} name={self.name} amount={self.amount}{unit} intake_id={self.intake_id}>"
