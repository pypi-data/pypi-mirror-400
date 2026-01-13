from typing import Any, Generic, Mapping, TypeVar, Sequence

T = TypeVar("T")


class BaseRepository(Generic[T]):
    model: type[T]

    async def get(self, id: int) -> T | None:
        return await self.model.get(id)

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[T]:
        return await self.model.find().skip(skip).limit(limit).to_list()

    async def create(self, obj: Mapping[str, Any]) -> T:
        doc = self.model(**obj)
        await doc.insert()
        return doc

    async def update(self, id: int, obj_in: Mapping[str, Any]) -> T:
        obj = await self.get(id)
        if not obj:
            return None

        for field, value in obj_in.items():
            setattr(obj, field, value)

        await obj.replace()
        return obj

    async def delete(self, id: int) -> T | None:
        obj = await self.get(id)
        if not obj:
            return None
        await obj.delete()
        return obj
