#backend/app/schemas.py
from __future__ import annotations
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, EmailStr

from .models.enums import UserRole


# Pydantic Base
class SchemaBase(BaseModel):
    class Config:
        from_attributes = True


# ============================================================
# USERS
# ============================================================

class UserBase(SchemaBase):
    username: str
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = True

    # UI preference fields (optional on base so forms can include them)
    ui_theme: Optional[str] = None
    ui_sidebar: Optional[bool] = None
    ui_navbar: Optional[bool] = None
    ui_font_scale: Optional[str] = None
    ui_simple_mode: Optional[bool] = None
    ui_features: Optional[Dict[str, bool]] = None


class UserCreate(SchemaBase):
    username: str
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    password: str

    # allow initial UI preferences (optional)
    ui_theme: Optional[str] = None
    ui_sidebar: Optional[bool] = None
    ui_navbar: Optional[bool] = None
    ui_font_scale: Optional[str] = None
    ui_simple_mode: Optional[bool] = None
    ui_features: Optional[Dict[str, bool]] = None


class UserUpdate(SchemaBase):
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

    ui_theme: Optional[str] = None
    ui_sidebar: Optional[bool] = None
    ui_navbar: Optional[bool] = None
    ui_font_scale: Optional[str] = None
    ui_simple_mode: Optional[bool] = None
    ui_features: Optional[Dict[str, bool]] = None


class UserRead(UserBase):
    id: int
    created_at: Optional[datetime] = None

    # Ensure returned user includes UI preferences with concrete types
    ui_theme: str = "theme-light"
    ui_sidebar: bool = True
    ui_navbar: bool = True
    ui_font_scale: str = "normal"
    ui_simple_mode: bool = False
    ui_features: Dict[str, bool] = {}

    class Config:
        orm_mode = True


# ------------------------------------------------------------
# NEW: UserLogin (for /login endpoint)
# ------------------------------------------------------------
class UserLogin(SchemaBase):
    username: str
    password: str


# Token
class TokenResponse(SchemaBase):
    access_token: str
    token_type: str = "bearer"
    user_id: Optional[int] = None
    username: Optional[str] = None


# ============================================================
# BLOCKS & SUBDIVISIONS
# ============================================================

class BlockBase(SchemaBase):
    name: str
    cultivar: Optional[str] = None
    supplier: Optional[str] = None
    hectares: Optional[float] = None
    notes: Optional[str] = None


class BlockCreate(BlockBase):
    pass


class BlockUpdate(SchemaBase):
    name: Optional[str] = None
    cultivar: Optional[str] = None
    supplier: Optional[str] = None
    hectares: Optional[float] = None
    notes: Optional[str] = None


class BlockRead(BlockBase):
    id: int


# Subdivisions
class SubdivisionBase(SchemaBase):
    name: str
    area_hectares: Optional[float] = None
    notes: Optional[str] = None


class SubdivisionCreate(SubdivisionBase):
    block_id: int


class SubdivisionUpdate(SchemaBase):
    name: Optional[str] = None
    area_hectares: Optional[float] = None
    notes: Optional[str] = None


class SubdivisionRead(SubdivisionBase):
    id: int
    block_id: int


# ============================================================
# INTAKES
# ============================================================

class IntakeComponentBase(SchemaBase):
    name: str
    weight_kg: Optional[float] = None


class IntakeComponentCreate(IntakeComponentBase):
    pass


class IntakeComponentRead(IntakeComponentBase):
    id: int
    intake_id: int


class AdditionBase(SchemaBase):
    name: str
    amount: Optional[float]
    unit: Optional[str]


class AdditionCreate(AdditionBase):
    pass


class AdditionRead(AdditionBase):
    id: int
    intake_id: int


class FruitBase(SchemaBase):
    component_name: str
    volume_litres: Optional[float]


class FruitCreate(FruitBase):
    pass


class FruitRead(FruitBase):
    id: int
    intake_id: int


class LabResultBase(SchemaBase):
    brix: Optional[float] = None
    pH: Optional[float] = None
    ta: Optional[float] = None
    va: Optional[float] = None
    rs: Optional[float] = None
    alc: Optional[float] = None
    malic_acid: Optional[float] = None
    yan: Optional[float] = None
    notes: Optional[str] = None


class LabResultCreate(LabResultBase):
    pass


class LabResultRead(LabResultBase):
    id: int
    intake_id: int


# Intake Core
class IntakeBase(SchemaBase):
    block_id: Optional[int] = None
    weight_kg: Optional[float] = None
    notes: Optional[str] = None


class IntakeCreate(IntakeBase):
    components: Optional[List[IntakeComponentCreate]] = None
    additions: Optional[List[AdditionCreate]] = None
    fruits: Optional[List[FruitCreate]] = None
    lab_results: Optional[List[LabResultCreate]] = None


class IntakeRead(IntakeBase):
    id: int
    created_at: datetime

    # Flat read = identifiers only — no nested JSON
    created_by_id: int


# List wrappers
class BlockList(SchemaBase):
    blocks: List[BlockRead]


class IntakeList(SchemaBase):
    intakes: List[IntakeRead]
