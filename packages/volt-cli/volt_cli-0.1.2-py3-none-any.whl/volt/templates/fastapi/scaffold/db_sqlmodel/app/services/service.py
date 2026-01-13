from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.__MODEL_NAME_LOWER__ import __MODEL_NAME__
from app.repositories.__MODEL_NAME_LOWER__ import __MODEL_NAME__Repository
from app.schemas.__MODEL_NAME_LOWER__ import __MODEL_NAME__Create, __MODEL_NAME__Update
from app.services.base import BaseService


class __MODEL_NAME__Service(BaseService[__MODEL_NAME__]):
    model = __MODEL_NAME__

    def __init__(self, repo: __MODEL_NAME__Repository | None = None):
        self.repo = repo or __MODEL_NAME__Repository()

    async def create(
        self, session: AsyncSession, obj_in: __MODEL_NAME__Create
    ) -> __MODEL_NAME__:
        return await self.repo.create(session, obj_in)

    async def get(self, session: AsyncSession, id: int) -> __MODEL_NAME__ | None:
        return await self.repo.get(session, id)

    async def get_multi(self, session: AsyncSession, skip: int = 0, limit: int = 100):
        return await self.repo.get_multi(session, skip, limit)

    async def update(
        self, session: AsyncSession, id: int, obj_in: __MODEL_NAME__Update
    ) -> __MODEL_NAME__ | None:
        return await self.repo.update(
            session, id, obj_in.model_dump(exclude_unset=True)
        )

    async def delete(self, session: AsyncSession, id: int) -> __MODEL_NAME__ | None:
        return await self.repo.delete(session, id)
