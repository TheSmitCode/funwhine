# app/models/lab.py
from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Float, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base

if TYPE_CHECKING:
    from .intake import Intake


class LabResult(Base):
    __tablename__ = "lab_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    intake_id: Mapped[int] = mapped_column(ForeignKey("intakes.id"), nullable=True)

    brix: Mapped[Optional[float]] = mapped_column(Float)
    pH: Mapped[Optional[float]] = mapped_column(Float)
    ta: Mapped[Optional[float]] = mapped_column(Float)
    va: Mapped[Optional[float]] = mapped_column(Float)
    rs: Mapped[Optional[float]] = mapped_column(Float)
    alc: Mapped[Optional[float]] = mapped_column(Float)
    malic_acid: Mapped[Optional[float]] = mapped_column(Float)
    yan: Mapped[Optional[float]] = mapped_column(Float)

    notes: Mapped[Optional[str]] = mapped_column(String(500))

    intake = relationship(
        "Intake",
        back_populates="lab_results",
        lazy="selectin",
    )
