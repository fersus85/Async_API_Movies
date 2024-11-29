from typing import Protocol, Any, Optional


class AbstractCache(Protocol):
    """Абстрактый класс для кэша"""

    async def set(self, key: str, value: Any, expire: int) -> None: ...

    async def get(self, key: str) -> Optional[Any]: ...


cacher = Optional[AbstractCache]


async def get_cacher() -> AbstractCache:
    return cacher
