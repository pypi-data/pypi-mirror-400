from beanie import PydanticObjectId
from typing import Annotated, List
from fastapi import APIRouter, Depends
from app.dependencies.__MODEL_NAME_LOWER__ import get___MODEL_NAME_LOWER___service
from app.services.__MODEL_NAME_LOWER__ import __MODEL_NAME__Service
from app.schemas.__MODEL_NAME_LOWER__ import (
    __MODEL_NAME__Create,
    __MODEL_NAME__Read,
    __MODEL_NAME__Update,
)

serviceDep = Annotated[__MODEL_NAME__Service, Depends(get___MODEL_NAME_LOWER___service)]
router = APIRouter()


@router.post("", response_model=__MODEL_NAME__Read)
async def create___MODEL_NAME_LOWER__(
    *, obj_in: __MODEL_NAME__Create, service: serviceDep
):
    return await service.create(obj_in=obj_in)


@router.get("/{id}", response_model=__MODEL_NAME__Read)
async def read___MODEL_NAME_LOWER__(*, id: PydanticObjectId, service: serviceDep):
    db_obj = await service.get(id=id)
    return service.ensure_exists(db_obj)


@router.get("", response_model=List[__MODEL_NAME__Read])
async def read_multi___MODEL_NAME_PLURAL__(
    *, skip: int = 0, limit: int = 100, service: serviceDep
):
    obj = await service.get_multi(skip=skip, limit=limit)
    return service.ensure_exists(obj)


@router.patch("/{id}", response_model=__MODEL_NAME__Read)
async def update___MODEL_NAME_LOWER__(
    *, id: PydanticObjectId, obj_in: __MODEL_NAME__Update, service: serviceDep
):
    obj = await service.update(id=id, obj_in=obj_in)
    return service.ensure_exists(obj)


@router.delete("/{id}", response_model=__MODEL_NAME__Read)
async def delete___MODEL_NAME_LOWER__(*, id: PydanticObjectId, service: serviceDep):
    obj = await service.delete(id=id)
    return service.ensure_exists(obj)
