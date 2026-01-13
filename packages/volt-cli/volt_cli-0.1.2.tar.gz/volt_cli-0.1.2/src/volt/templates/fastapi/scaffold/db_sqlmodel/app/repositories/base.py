from typing import Any, Generic, Mapping, TypeVar, Sequence
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    model: type[T]

    async def get(self, session: AsyncSession, id: int) -> T | None:
        return await session.get(self.model, id)

    async def get_multi(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[T]:
        result = await session.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, session: AsyncSession, obj: T) -> T:
        db_obj = self.model.model_validate(obj)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self, session: AsyncSession, id: int, obj_in: Mapping[str, Any]
    ) -> T:
        obj = await self.get(session, id)
        if not obj:
            return None

        for field, value in obj_in.items():
            setattr(obj, field, value)

        await session.commit()
        await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession, id: int) -> T | None:
        obj = await self.get(session, id)
        if not obj:
            return None
        await session.delete(obj)
        await session.commit()
        return obj
