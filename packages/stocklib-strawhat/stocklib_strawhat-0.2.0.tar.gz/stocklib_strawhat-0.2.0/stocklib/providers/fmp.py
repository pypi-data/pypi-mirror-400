import asyncio
from typing import List
import aiohttp
from datetime import datetime
from stocklib.models.company import Company
from stocklib.models.growth import GrowthMetrics
from stocklib.models.ratios import Ratios, Profitability, Valuation, LeverageAndLiquidity
from stocklib.providers.base import BaseProvider
from stocklib.models.fundamentals import Fundamentals
from stocklib.models.market import MarketData
from stocklib.models.financials import Financials, IncomeStatement, BalanceSheet, CashFlow, FinancialsMetadata
from stocklib.utils.config import FMP_FINANCIALS, FMP_GROWTH, FMP_MARKET, FMP_RATIOS, FMP_STOCKS_SEARCH
from stocklib.exceptions.provider import ProviderError, ProviderSubscriptionError


class FMPProvider(BaseProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._cached_profile = None  # Cache profile data to avoid duplicate API calls

    async def get_stocks(self, symbol: str, currency: str = "USD", exchange: str = "NASDAQ") -> List[dict]:
        """
        Search for stocks by name/keyword.
        
        Args:
            symbol: Keyword to search for (company name or ticker)
            currency: Filter by currency (default: "USD")
            exchange: Filter by exchange (default: "NASDAQ")
            
        Returns:
            List of stock dictionaries matching the criteria
        """
        url = f"{FMP_STOCKS_SEARCH['search']}?query={symbol}&apikey={self.api_key}"
        async with aiohttp.ClientSession() as session:
            response = await self._fetch_data(session, url, symbol)
            # Filter stocks by currency and exchange
            stocks = [x for x in response if x.get("currency") == currency and x.get("exchange") == exchange]
            return stocks

    async def _fetch_data(self, session: aiohttp.ClientSession, url: str, symbol: str = None):
        """Simple helper to fetch data from URL."""
        try:
            async with session.get(url) as response:
                # Handle 402 Payment Required
                if response.status == 402:
                    raise ProviderSubscriptionError(
                        f"Subscription required for symbol {symbol}",
                        provider_name=self.__class__.__name__,
                        symbol=symbol
                    )
                response.raise_for_status()
                return await response.json()
        except ProviderSubscriptionError:
            raise
        except Exception as e:
            raise ProviderError(
                f"Failed to fetch data: {str(e)}",
                provider_name=self.__class__.__name__,
                symbol=symbol
            )

    async def get_fundamentals(self, symbol: str) -> Fundamentals:
        pass

    async def get_market_data(self, symbol: str) -> MarketData:
        """ 
        Fetch market data (price, market cap, beta, volume) for a symbol.
        Also caches profile data for company information to avoid duplicate API calls.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            MarketData object containing all market data
        """
        async with aiohttp.ClientSession() as session:
            # Fetch profile data which contains most market data fields and company info
            profile_url = f"{FMP_MARKET['profile']}?symbol={symbol}&apikey={self.api_key}"
            profile_data = await self._fetch_data(session, profile_url, symbol)
            
            # Get the first entry from the response
            profile = profile_data[0] if profile_data and isinstance(profile_data, list) else {}
            
            # Cache profile data for company information (avoid duplicate API calls)
            self._cached_profile = profile
            
            # Extract current price and market cap
            current_price = profile.get("price", 0.0)
            market_cap = profile.get("marketCap", 0.0)
            
            # Calculate shares outstanding: market_cap / price
            shares_outstanding = market_cap / current_price if current_price > 0 else 0.0
            
            # Parse 52-week high/low from range string (format: "164.08-260.1")
            week_52_low = 0.0
            week_52_high = 0.0
            range_str = profile.get("range", "")
            if range_str and "-" in range_str:
                try:
                    low_str, high_str = range_str.split("-")
                    week_52_low = float(low_str.strip())
                    week_52_high = float(high_str.strip())
                except (ValueError, AttributeError):
                    # 52-week range is optional, so we silently fail and use defaults (0.0)
                    pass
            
            return MarketData(
                current_price=current_price,
                market_cap=market_cap,
                shares_outstanding=shares_outstanding,
                beta=profile.get("beta", 0.0),
                volume=profile.get("volume", 0.0),
                average_volume=profile.get("averageVolume", 0.0),
                week_52_high=week_52_high,
                week_52_low=week_52_low
            )
    
    def _get_company_from_cache(self, symbol: str) -> Company:
        """
        Extract company data from cached profile (called after get_market_data).
        This avoids duplicate API calls.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Company object containing all company information
        """
        if not self._cached_profile:
            # Return minimal company if profile not cached
            return Company(
                symbol=symbol,
                name="",
                exchange="",
                sector="",
                industry="",
                country="",
                currency="USD"
            )
        
        profile = self._cached_profile
        
        # Parse IPO date from string to date object
        ipo_date = None
        ipo_date_str = profile.get("ipoDate")
        if ipo_date_str:
            try:
                ipo_date = datetime.strptime(ipo_date_str, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                # IPO date is optional, so we silently fail and keep it as None
                pass
        
        try:
            return Company(
                symbol=profile.get("symbol", symbol),
                name=profile.get("companyName", ""),
                exchange=profile.get("exchange", ""),
                sector=profile.get("sector", ""),
                industry=profile.get("industry", ""),
                country=profile.get("country", ""),
                currency=profile.get("currency", "USD"),
                ipo_date=ipo_date,
                website=profile.get("website")
            )
        except Exception as e:
            raise ProviderError(
                f"Failed to create company data for symbol {symbol}: {str(e)}",
                provider_name=self.__class__.__name__,
                symbol=symbol
            )

    async def get_financials(self, symbol: str) -> Financials:
        """
        Fetch financial statements (balance sheet, income statement, cash flow) for a symbol.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Financials object containing all financial statement data
        """
        async with aiohttp.ClientSession() as session:
            urls = [
                f"{FMP_FINANCIALS['balance_sheet']}?symbol={symbol}&apikey={self.api_key}",
                f"{FMP_FINANCIALS['income_statement']}?symbol={symbol}&apikey={self.api_key}",
                f"{FMP_FINANCIALS['cash_flow']}?symbol={symbol}&apikey={self.api_key}",
            ]
            
            tasks = [self._fetch_data(session, url, symbol) for url in urls]
            results = await asyncio.gather(*tasks)
            
            # Unpack results: [balance_sheet_data, income_statement_data, cash_flow_data]
            balance_sheet_data, income_statement_data, cash_flow_data = results
            
            # Get the most recent (first) entry from each response
            bs = balance_sheet_data[0] if balance_sheet_data and isinstance(balance_sheet_data, list) else {}
            is_stmt = income_statement_data[0] if income_statement_data and isinstance(income_statement_data, list) else {}
            cf = cash_flow_data[0] if cash_flow_data and isinstance(cash_flow_data, list) else {}
            
            # Extract metadata (use from income statement as it's typically most complete)
            fiscal_year = int(is_stmt.get("fiscalYear", bs.get("fiscalYear", cf.get("fiscalYear", 0))))
            period = is_stmt.get("period", bs.get("period", cf.get("period", "FY")))
            
            # Map to IncomeStatement model
            income_statement = IncomeStatement(
                revenue=is_stmt.get("revenue", 0.0),
                gross_profit=is_stmt.get("grossProfit", 0.0),
                operating_income=is_stmt.get("operatingIncome", 0.0),
                net_income=is_stmt.get("netIncome", 0.0),
                eps=is_stmt.get("eps", 0.0)
            )
            
            # Map to BalanceSheet model
            balance_sheet = BalanceSheet(
                total_assets=bs.get("totalAssets", 0.0),
                total_liabilities=bs.get("totalLiabilities", 0.0),
                total_equity=bs.get("totalEquity", 0.0),
                cash_and_equivalents=bs.get("cashAndCashEquivalents", 0.0),
                total_debt=bs.get("totalDebt", 0.0)
            )
            
            # Map to CashFlow model
            cash_flow = CashFlow(
                operating_cash_flow=cf.get("operatingCashFlow", 0.0),
                free_cash_flow=cf.get("freeCashFlow", 0.0),
                capital_expenditure=abs(cf.get("capitalExpenditure", 0.0))  # Make positive as it's typically negative
            )
            
            # Create metadata
            metadata = FinancialsMetadata(
                fiscal_year=fiscal_year,
                period=period
            )
            
            # Return Financials object
            return Financials(
                income_statement=income_statement,
                balance_sheet=balance_sheet,
                cash_flow=cash_flow,
                metadata=metadata
            )
    async def get_growth(self, symbol: str) -> GrowthMetrics:
        """
        Fetch growth metrics (revenue growth, net income growth, free cash flow growth, eps growth) for a symbol.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            GrowthMetrics object containing all growth metrics
        """
        async with aiohttp.ClientSession() as session:
            # Fetch financial-growth endpoint which contains all key growth metrics
            financial_growth_url = f"{FMP_GROWTH['financial_growth']}symbol={symbol}&apikey={self.api_key}"
            financial_growth_data = await self._fetch_data(session, financial_growth_url, symbol)
            
            # Get the first (most recent) entry from the response
            financial_growth = financial_growth_data[0] if financial_growth_data and isinstance(financial_growth_data, list) else {}
            
            return GrowthMetrics(
                revenue_growth_yoy=financial_growth.get("revenueGrowth", 0.0),
                net_income_growth_yoy=financial_growth.get("netIncomeGrowth", 0.0),
                free_cash_flow_growth_yoy=financial_growth.get("freeCashFlowGrowth", 0.0),
                eps_growth_yoy=financial_growth.get("epsgrowth", 0.0)
            )
    
    async def get_ratios(self, symbol: str) -> Ratios:
        """
        Fetch financial ratios (profitability, liquidity, solvency, efficiency) for a symbol.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Ratios object containing all financial ratios
        """
        async with aiohttp.ClientSession() as session:
            # Fetch ratios and key-metrics endpoints concurrently
            urls = [
                f"{FMP_RATIOS['ratios']}?symbol={symbol}&apikey={self.api_key}",
                f"{FMP_RATIOS['key_metrics']}?symbol={symbol}&apikey={self.api_key}",
            ]
            
            tasks = [self._fetch_data(session, url, symbol) for url in urls]
            results = await asyncio.gather(*tasks)
            
            # Unpack results: [ratios_data, key_metrics_data]
            ratios_data, key_metrics_data = results
            
            # Get the first (most recent) entry from each response
            ratios = ratios_data[0] if ratios_data and isinstance(ratios_data, list) else {}
            key_metrics = key_metrics_data[0] if key_metrics_data and isinstance(key_metrics_data, list) else {}
            
            # Build Profitability ratios
            profitability = Profitability(
                gross_margin=ratios.get("grossProfitMargin", 0.0),
                operating_margin=ratios.get("operatingProfitMargin", 0.0),
                net_margin=ratios.get("netProfitMargin", 0.0),
                return_on_equity=key_metrics.get("returnOnEquity", 0.0),
                return_on_assets=key_metrics.get("returnOnAssets", 0.0)
            )
            
            # Build Valuation ratios
            valuation = Valuation(
                price_to_earnings=ratios.get("priceToEarningsRatio", 0.0),
                price_to_book=ratios.get("priceToBookRatio", 0.0),
                price_to_sales=ratios.get("priceToSalesRatio", 0.0)
            )
            
            # Build LeverageAndLiquidity ratios
            leverage_and_liquidity = LeverageAndLiquidity(
                debt_to_equity=ratios.get("debtToEquityRatio", 0.0),
                current_ratio=ratios.get("currentRatio", 0.0)
            )
            
            return Ratios(
                profitability=profitability,
                valuation=valuation,
                leverage_and_liquidity=leverage_and_liquidity
            )