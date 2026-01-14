from stocklib.rate_limit.interface import RateLimitter
import redis


class RedisRateLimitter(RateLimitter):
    def __init__(
        self,
        redis_url: str,
        max_requests: int = 100,
        time_window: int = 60
    ):
        self.client = redis.from_url(redis_url)
        self.max_requests = max_requests
        self.time_window = time_window

    def allow(self, key: str) -> bool:
        current = self.client.incr(key)

        if current == 1:
            self.client.expire(key, self.time_window)
        return current <= self.max_requests