from typing import Generic, TypeVar

T = TypeVar("T")


class BaseService(Generic[T]):
    model: type[T]

    def ensure_exists(self, obj: T | None) -> T:
        if obj is None:
            from app.core.exception import NotFoundError

            raise NotFoundError(self.model.__name__)
        return obj
