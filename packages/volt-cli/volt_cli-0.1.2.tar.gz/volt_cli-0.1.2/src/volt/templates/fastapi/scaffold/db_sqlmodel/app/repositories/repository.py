from app.models.__MODEL_NAME_LOWER__ import __MODEL_NAME__
from app.repositories.base import BaseRepository


class __MODEL_NAME__Repository(BaseRepository[__MODEL_NAME__]):
    model = __MODEL_NAME__
