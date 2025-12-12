# app/models/fruit.py
from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base

if TYPE_CHECKING:
    from .intake import Intake


class Fruit(Base):
    __tablename__ = "fruit"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    intake_id: Mapped[int] = mapped_column(ForeignKey("intakes.id"), nullable=False)

    component_name: Mapped[str] = mapped_column(String(100), nullable=False)
    volume_litres: Mapped[Optional[float]] = mapped_column(Float)

    intake = relationship(
        "Intake",
        back_populates="fruits",
        lazy="selectin",
    )
