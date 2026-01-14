import time
import redis.asyncio as redis

from stocklib.rate_limit.interface import RateLimitter
from stocklib.exceptions.rate_limit import RateLimitExceeded

# Thread safe
class TokenBucket(RateLimitter):
    def __init__(
        self,
        redis_url: str,
        capacity: int = 20,
        refill_rate: float = 20/60 # 20 tokens per minute
    ):
        self.client = redis.from_url(redis_url)
        self.capacity = capacity
        self.refill_rate = refill_rate

    async def allow(self, key: str, tokens: int = 1) -> bool:
        now = time.time()

        # create redis pipeline for atomic operations
        async with self.client.pipeline() as pipe:
            while True:
                # if another thread modified the data, we need to retry
                # watcherror occurs for the same
                try:
                    # watch ensures no other process modifies the key while tokens are being updated
                    # if updation happens,, watcherror is raised and we retry the operation
                    # hence, this is a thread safe operation
                    await pipe.watch(key)

                    # Fetch data from Redis
                    await pipe.hgetall(key)
                    data = await pipe.execute()
                    data = data[0] if data else {}
                    
                    current_tokens = (
                        float(data.get(b"tokens", self.capacity))
                    )

                    last_refill = (
                        float(data.get(b"last_refill", now))
                    )

                    # refill tokens
                    elapsed = now - last_refill

                    # core of the algo
                    new_tokens = min(
                        self.capacity,
                        current_tokens + elapsed * self.refill_rate
                    )

                    if new_tokens < tokens:
                        raise RateLimitExceeded("too many requests")
                    
                    new_tokens = new_tokens - tokens
                    last_refill = now

                    # ensures atomicity
                    pipe.multi()

                    # update cache
                    pipe.hset(key, mapping={
                        b"tokens": new_tokens,
                        b"last_refill": last_refill
                    })
                    await pipe.execute()

                    return True

                except redis.WatchError:
                    continue