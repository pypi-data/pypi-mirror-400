from typing import Generic, TypeVar

T = TypeVar("T")


class BaseService(Generic[T]):
    model: type[T]

    def ensure_exists(self, obj: T | None) -> T:
        if obj is None:
            raise ValueError(f"{self.model.__name__} not found")
        return obj
