from abc import ABC, abstractmethod

class RateLimitter(ABC):

    @abstractmethod
    async def allow(self, key: str, tokens: int = 1) -> bool:
        pass