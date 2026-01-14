from typing import Optional
from stocklib.cache.interface import Cache
import redis.asyncio as redis

from stocklib.models.fundamentals import Fundamentals


class RedisCache(Cache):
    def __init__(self, redis_url: str):
        self.client = redis.from_url(redis_url)
    
    async def get(self, key: str) -> Optional[Fundamentals]:
        data = await self.client.get(key)
        if not data:
            return None
        return Fundamentals.model_validate_json(data)

    async def set(self, key: str, value: Fundamentals, ttl: int) -> bool:
        await self.client.setex(
            key,
            ttl,
            value.model_dump_json().encode("utf-8")
        )
        return True

    async def delete(self, key: str) -> bool:
        await self.client.delete(key)
        return True