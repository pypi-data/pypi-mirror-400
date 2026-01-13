from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.db import get_session
from app.dependencies.__MODEL_NAME_LOWER__ import get___MODEL_NAME_LOWER___service
from app.services.__MODEL_NAME_LOWER__ import __MODEL_NAME__Service
from app.schemas.__MODEL_NAME_LOWER__ import (
    __MODEL_NAME__Create,
    __MODEL_NAME__Read,
    __MODEL_NAME__Update,
)

sessionDep = Annotated[Session, Depends(get_session)]
serviceDep = Annotated[__MODEL_NAME__Service, Depends(get___MODEL_NAME_LOWER___service)]
router = APIRouter()


@router.post("", response_model=__MODEL_NAME__Read)
async def create___MODEL_NAME_LOWER__(
    *, obj_in: __MODEL_NAME__Create, session: sessionDep, service: serviceDep
):
    return await service.create(session=session, obj_in=obj_in)


@router.get("/{id}", response_model=__MODEL_NAME__Read)
async def read___MODEL_NAME_LOWER__(
    *, id: int, session: sessionDep, service: serviceDep
):
    db_obj = await service.get(session=session, id=id)
    return service.ensure_exists(db_obj)


@router.get("", response_model=List[__MODEL_NAME__Read])
async def read_multi___MODEL_NAME_PLURAL__(
    *, skip: int = 0, limit: int = 100, session: sessionDep, service: serviceDep
):
    obj = await service.get_multi(session=session, skip=skip, limit=limit)
    return service.ensure_exists(obj)


@router.patch("/{id}", response_model=__MODEL_NAME__Read)
async def update___MODEL_NAME_LOWER__(
    *, id: int, obj_in: __MODEL_NAME__Update, session: sessionDep, service: serviceDep
):
    obj = await service.update(session=session, id=id, obj_in=obj_in)
    return service.ensure_exists(obj)


@router.delete("/{id}", response_model=__MODEL_NAME__Read)
async def delete___MODEL_NAME_LOWER__(
    *, id: int, session: sessionDep, service: serviceDep
):
    obj = await service.delete(session=session, id=id)
    return service.ensure_exists(obj)
