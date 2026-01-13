from beanie import PydanticObjectId
from typing import Optional
from pydantic import BaseModel


class __MODEL_NAME__Base(BaseModel):
    __SCHEMA_BASE_FIELDS__


class __MODEL_NAME__Create(__MODEL_NAME__Base):
    pass


class __MODEL_NAME__Update(__MODEL_NAME__Base):
    __SCHEMA_UPDATE_FIELDS__


class __MODEL_NAME__Read(__MODEL_NAME__Base):
    id: PydanticObjectId
