# app/models/blocks.py
from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base

# Forward references for Pylance
if TYPE_CHECKING:
    from .intake import Intake
    from .blocks import BlockSubdivision  # self-ref OK


class Block(Base):
    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    cultivar: Mapped[Optional[str]] = mapped_column(String(120))
    supplier: Mapped[Optional[str]] = mapped_column(String(200))
    hectares: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(String(2000))

    subdivisions: Mapped[List["BlockSubdivision"]] = relationship(
        "BlockSubdivision", back_populates="block", lazy="selectin"
    )

    intakes: Mapped[List["Intake"]] = relationship(
        "Intake", back_populates="block", lazy="selectin"
    )


class BlockSubdivision(Base):
    __tablename__ = "block_subdivisions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    block_id: Mapped[int] = mapped_column(ForeignKey("blocks.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    area_hectares: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(String(2000))

    block: Mapped["Block"] = relationship(
        "Block", back_populates="subdivisions", lazy="selectin"
    )
