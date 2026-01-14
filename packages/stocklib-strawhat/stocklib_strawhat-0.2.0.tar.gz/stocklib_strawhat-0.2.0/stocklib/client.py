from stocklib.cache.redis import RedisCache
from stocklib.core.orchestrator import Orchestrator
from stocklib.core.pipeline import Pipeline
from stocklib.models.fundamentals import Fundamentals
from stocklib.providers.fmp import FMPProvider
from stocklib.rate_limit.token_bucket import TokenBucket
from stocklib.utils.config import config

# this is the only part exposed as a lib
# all calls go through this to an orchestratot which decides
class StockClient:
    def __init__(self):

        # infra
        redis = RedisCache(config["REDIS_URL"])
        rate_limitter = TokenBucket(config["REDIS_URL"])

        # providers
        providers = [
            FMPProvider(
                api_key=config["FMP_API_KEY"]
            ),
        ]

        self.orchestrator = Orchestrator(
            providers=providers,
            rate_limitter=rate_limitter
        )
        # pipeline
        self.pipeline = Pipeline(
            providers=providers,
            cache=redis,
            rate_limitter=rate_limitter,
            orchestrator=self.orchestrator
        )
    
    # public api for consumers
    async def get_fundamentals(self, symbol: str, currency: str = "USD", exchange: str = "NASDAQ") -> Fundamentals:
        return await self.pipeline.run_pipeline(symbol, currency, exchange)