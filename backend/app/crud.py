# app/crud.py
"""
Full CRUD layer for FunWhine (async-first).
Now with a working authenticate() that accepts email OR username.
"""

from __future__ import annotations

from typing import Any, Generic, List, Optional, Sequence, Type, TypeVar, Union, Dict
from dataclasses import asdict

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .core.security import get_password_hash, verify_password
from . import models
from . import schemas

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


# -------------------------
# Generic CRUD Base
# -------------------------
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    model: Type[ModelType]

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        return await db.get(self.model, id)

    async def get_with_options(self, db: AsyncSession, *, id: int, options: Sequence[Any]):
        stmt = select(self.model).where(self.model.id == id)
        for opt in options:
            stmt = stmt.options(opt)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        if hasattr(obj_in, "model_dump"):
            data = obj_in.model_dump()
        elif hasattr(obj_in, "dict"):
            data = obj_in.dict()
        elif isinstance(obj_in, dict):
            data = dict(obj_in)
        else:
            try:
                data = asdict(obj_in)
            except Exception:
                raise TypeError("Unsupported obj_in type for create()")

        db_obj = self.model(**data)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        if hasattr(obj_in, "model_dump"):
            update_data = obj_in.model_dump(exclude_none=True)
        elif hasattr(obj_in, "dict"):
            update_data = obj_in.dict(exclude_none=True)
        elif isinstance(obj_in, dict):
            update_data = {k: v for k, v in obj_in.items() if v is not None}
        else:
            try:
                update_data = asdict(obj_in)
            except Exception:
                raise TypeError("Unsupported obj_in type for update()")

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        obj = await self.get(db, id=id)
        if obj is None:
            return None
        await db.delete(obj)
        await db.commit()
        return obj


# -------------------------
# User CRUD — NOW FIXED
# -------------------------
class UserCRUD(CRUDBase[models.User, schemas.UserCreate, schemas.UserRead]):
    def __init__(self, model: type):
        super().__init__(model)

    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[models.User]:
        stmt = select(self.model).where(self.model.username == username)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[models.User]:
        stmt = select(self.model).where(self.model.email == email)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        if hasattr(obj_in, "model_dump"):
            data = obj_in.model_dump()
        elif isinstance(obj_in, dict):
            data = dict(obj_in)
        else:
            data = obj_in.dict()

        password = data.pop("password", None)
        if password is None:
            raise ValueError("Password required to create user")

        data["password_hash"] = get_password_hash(password)

        db_obj = self.model(**data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    # FIXED AUTHENTICATE — accepts email OR username
    async def authenticate(
        self, db: AsyncSession, *, identifier: str, password: str
    ) -> Optional[models.User]:
        """
        Authenticate user by email OR username.
        """
        user = await self.get_by_email(db, email=identifier)
        if not user:
            user = await self.get_by_username(db, username=identifier)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user


# -------------------------
# Block & Intake CRUD — unchanged (your beautiful nested logic stays)
# -------------------------
class BlockCRUD(CRUDBase[models.Block, schemas.BlockCreate, schemas.BlockRead]):
    def __init__(self, model: type):
        super().__init__(model)


class IntakeCRUD(CRUDBase[models.Intake, schemas.IntakeCreate, schemas.IntakeRead]):
    def __init__(self, model: type):
        super().__init__(model)

    async def create(self, db: AsyncSession, *, obj_in: Union[schemas.IntakeCreate, Dict[str, Any]]) -> models.Intake:
        if hasattr(obj_in, "model_dump"):
            data = obj_in.model_dump()
        elif isinstance(obj_in, dict):
            data = dict(obj_in)
        else:
            try:
                data = obj_in.dict()
            except Exception:
                raise TypeError("Unsupported obj_in type for Intake.create()")

        components = data.pop("components", []) or []
        additions = data.pop("additions", []) or []
        fruits = data.pop("fruits", []) or []
        lab_results = data.pop("lab_results", []) or []

        intake_obj = self.model(**data)
        db.add(intake_obj)
        await db.flush()

        for comp in components:
            comp_data = comp.model_dump() if hasattr(comp, "model_dump") else comp.dict() if hasattr(comp, "dict") else comp
            comp_data["intake_id"] = intake_obj.id
            db.add(models.IntakeComponent(**comp_data))

        for add in additions:
            add_data = add.model_dump() if hasattr(add, "model_dump") else add.dict() if hasattr(add, "dict") else add
            add_data["intake_id"] = intake_obj.id
            db.add(models.Addition(**add_data))

        for fr in fruits:
            fr_data = fr.model_dump() if hasattr(fr, "model_dump") else fr.dict() if hasattr(fr, "dict") else fr
            fr_data["intake_id"] = intake_obj.id
            db.add(models.Fruit(**fr_data))

        for lab in lab_results:
            lab_data = lab.model_dump() if hasattr(lab, "model_dump") else lab.dict() if hasattr(lab, "dict") else lab
            lab_data["intake_id"] = intake_obj.id
            db.add(models.LabResult(**lab_data))

        await db.commit()
        await db.refresh(intake_obj)
        return intake_obj

    async def get_multi_by_user(self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Intake]:
        stmt = select(self.model).where(self.model.created_by_id == user_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_multi_by_block(self, db: AsyncSession, *, block_id: int, skip: int = 0, limit: int = 100) -> List[models.Intake]:
        stmt = select(self.model).where(self.model.block_id == block_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()


# -------------------------
# Instances
# -------------------------
user = UserCRUD(models.User)
block = BlockCRUD(models.Block)
intake = IntakeCRUD(models.Intake)

# -------------------------
# Public Helper Functions (for cleaner imports)
# -------------------------
async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[models.User]:
    """Authenticate user by username or email."""
    return await user.authenticate(db, identifier=username, password=password)

async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """Fetch user by ID."""
    return await user.get(db, id=user_id)

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[models.User]:
    """Fetch user by username."""
    return await user.get_by_username(db, username=username)

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    """Fetch user by email."""
    return await user.get_by_email(db, email=email)

def get_crud_for_model(model_cls: Type[ModelType]) -> CRUDBase:
    mapping = {
        models.User: user,
        models.Block: block,
        models.Intake: intake,
    }
    return mapping.get(model_cls)  # type: ignore