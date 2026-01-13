from typing import Optional
from sqlmodel import Field, SQLModel


class __MODEL_NAME__(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    __MODEL_FIELDS__
