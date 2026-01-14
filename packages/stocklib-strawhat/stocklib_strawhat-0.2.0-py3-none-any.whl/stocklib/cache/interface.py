from abc import ABC, abstractmethod
from typing import Optional

from stocklib.models.fundamentals import Fundamentals

class Cache(ABC):

    @abstractmethod
    async def get(self, key: str) -> Optional[Fundamentals]:
        pass

    @abstractmethod
    async def set(self, key: str, value: Fundamentals, ttl: int) -> bool:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass