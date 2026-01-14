from datetime import datetime
from stocklib.analysis.growth import calculate_growth
from stocklib.analysis.ratios import calculate_ratios
from stocklib.core.orchestrator import Orchestrator
from stocklib.models.fundamentals import Fundamentals
from stocklib.models.metadata import Metadata
from stocklib.rate_limit.interface import RateLimitter


class Pipeline:
    def __init__(self,providers, cache, rate_limitter: RateLimitter, orchestrator: Orchestrator):
        self.providers = providers
        self.cache = cache
        self.rate_limitter = rate_limitter
        self.orchestrator = orchestrator

    async def run_pipeline(self, symbol: str, currency: str = "USD", exchange: str = "NASDAQ"):
        cache_key = f"stock:fundamentals:{symbol}:{currency}:{exchange}"

        # Check cache first
        cached = await self.cache.get(cache_key)
        if cached:
            # Update metadata to reflect cache hit
            # Since Fundamentals is frozen, use model_copy to create new instance with updated metadata
            updated_metadata = Metadata(
                provider_name=cached.metadata.provider_name,
                provider_version=cached.metadata.provider_version,
                fetched_at=datetime.now(),  # Update to current time when retrieved from cache
                cache_hit=True,  # Mark as cache hit
                cache_ttl_seconds=cached.metadata.cache_ttl_seconds,
                data_confidence_score=cached.metadata.data_confidence_score
            )
            # Return cached data with updated metadata using model_copy
            return cached.model_copy(update={"metadata": updated_metadata})

        # Cache miss - fetch from provider
        # provider orchestrator
        provider_result = await self.orchestrator.fetch_providers(symbol, currency, exchange)
        
        # analysis
        ratios = calculate_ratios(
            provider_result.financials,
            provider_result.market,
            provider_result.ratios,
            )
        growth = calculate_growth(provider_result.growth)

        # Create fundamentals with cache_miss metadata
        fundamentals = Fundamentals(
            company=provider_result.company,
            financials=provider_result.financials,
            market=provider_result.market,
            ratios=ratios,
            growth=growth,
            metadata=Metadata(
                provider_name="auto",
                fetched_at=datetime.now(),
                cache_hit=False,
                cache_ttl_seconds=3600
            )
        )

        # Cache the result
        await self.cache.set(cache_key, fundamentals, ttl=3600)

        return fundamentals