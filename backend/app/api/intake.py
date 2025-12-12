# app/api/intake.py
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Use the async DB dependency
from ..db.session import async_get_db
from .. import schemas
from ..crud import block as block_crud, intake as intake_crud

router = APIRouter(tags=["Intake", "Blocks"], prefix="/intake")


# -----------------------------------------------------------
# Block Endpoints (async)
# -----------------------------------------------------------
@router.post("/blocks", response_model=schemas.BlockRead, status_code=status.HTTP_201_CREATED)
async def create_block_endpoint(block_in: schemas.BlockCreate, db: AsyncSession = Depends(async_get_db)) -> Any:
    """
    Create a Block (async). Returns the created Block.
    """
    created = await block_crud.create(db, obj_in=block_in)
    return created


@router.get("/blocks/{block_id}", response_model=schemas.BlockRead)
async def get_block_endpoint(block_id: int, db: AsyncSession = Depends(async_get_db)) -> Any:
    block = await block_crud.get(db, id=block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block


# -----------------------------------------------------------
# Intake Endpoints (async)
# -----------------------------------------------------------
@router.post("/intakes", response_model=schemas.IntakeRead, status_code=status.HTTP_201_CREATED)
async def create_intake_endpoint(intake_in: schemas.IntakeCreate, db: AsyncSession = Depends(async_get_db)) -> Any:
    """
    Create an Intake with nested components/additions/fruits/lab_results.
    """
    created = await intake_crud.create(db, obj_in=intake_in)
    return created


@router.get("/intakes", response_model=List[schemas.IntakeRead])
async def list_intakes_endpoint(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(async_get_db)) -> Any:
    """
    List intakes (paginated). Returns IntakeRead list.
    """
    objs = await intake_crud.get_multi(db, skip=skip, limit=limit)
    return objs
