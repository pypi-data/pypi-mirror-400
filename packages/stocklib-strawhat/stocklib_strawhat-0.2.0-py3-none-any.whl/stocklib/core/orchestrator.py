from typing import List
from stocklib.exceptions.provider import ProviderError, ProviderSubscriptionError
from stocklib.exceptions.rate_limit import RateLimitExceeded
from stocklib.models.growth import GrowthMetrics
from stocklib.models.ratios import Ratios
from stocklib.models.financials import Financials
from stocklib.models.market import MarketData
from stocklib.models.company import Company
from stocklib.rate_limit.interface import RateLimitter

class ProviderResult:
    """
    Simple container for raw provider outputs.
    """
    def __init__(self, market: MarketData, financials: Financials, growth: GrowthMetrics, ratios: Ratios, company: Company):
        self.market = market
        self.financials = financials
        self.growth = growth
        self.ratios = ratios
        self.company = company

class Orchestrator:
    def __init__(self, providers: List, rate_limitter: RateLimitter):
        self.providers = providers
        self.rate_limitter = rate_limitter

    async def fetch_providers(self, symbol: str, currency: str = "USD", exchange: str = "NASDAQ"):
        last_error = None
        
        for provider in self.providers:
            provider_name = provider.__class__.__name__

            # Rate limiting
            try:
                await self.rate_limitter.allow(provider_name)
            except RateLimitExceeded:
                continue

            try:
                # Get stocks
                stocks = await provider.get_stocks(symbol, currency, exchange)
                if not stocks or len(stocks) == 0:
                    continue
                
                # Use first matching stock
                stock = stocks[0]
                stock_symbol = stock.get("symbol", symbol) if isinstance(stock, dict) else symbol
                
                # Fetch all data
                market = await provider.get_market_data(stock_symbol)
                financials = await provider.get_financials(stock_symbol)
                growth = await provider.get_growth(stock_symbol)
                ratios = await provider.get_ratios(stock_symbol)
                
                # Get company data
                if hasattr(provider, "_get_company_from_cache"):
                    company = provider._get_company_from_cache(stock_symbol)
                else:
                    from stocklib.models.company import Company
                    company = Company(
                        symbol=stock_symbol,
                        name=stock.get("name", "") if isinstance(stock, dict) else "",
                        exchange=stock.get("exchange", "") if isinstance(stock, dict) else "",
                        sector="",
                        industry="",
                        country="",
                        currency="",
                        ipo_date=None,
                        website=""
                    )
                
                return ProviderResult(
                    market=market,
                    financials=financials,
                    growth=growth,
                    ratios=ratios,
                    company=company
                )

            except ProviderSubscriptionError:
                # Subscription errors should be propagated immediately
                raise
            except Exception as exc:
                last_error = exc
                continue

        # All providers failed
        raise ProviderError(
            f"All providers failed for symbol {symbol}"
        ) from last_error