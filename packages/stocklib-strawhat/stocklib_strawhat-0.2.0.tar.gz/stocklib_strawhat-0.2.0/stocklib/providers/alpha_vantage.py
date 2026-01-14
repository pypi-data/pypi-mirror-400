import asyncio
import logging
from typing import List, Optional
import aiohttp
from pydantic import ValidationError
from stocklib.exceptions.data import DataValidationError, IncompleteDataError
from stocklib.exceptions.provider import ProviderSubscriptionError
from stocklib.providers.base import BaseProvider
from stocklib.models.fundamentals import Fundamentals
from stocklib.models.market import MarketData
from stocklib.models.financials import Financials, IncomeStatement, BalanceSheet, CashFlow, FinancialsMetadata
from stocklib.models.growth import GrowthMetrics
from stocklib.models.ratios import Ratios, Profitability, Valuation, LeverageAndLiquidity
from stocklib.utils import config

logger = logging.getLogger(__name__)


class AlphaVantageProvider(BaseProvider):
    """
    Alpha Vantage provider for fetching stock market data.
    Supports keyword search to find stocks and fetch their financial data.
    """
    
    market_data_list = []
    financials_list = []
    stocks_list = []
    
    def __init__(self, api_key: str):
        """
        Initialize Alpha Vantage provider.
        
        Args:
            api_key: Alpha Vantage API key
        """
        logger.debug(f"[AlphaVantageProvider.__init__] Initializing provider with API key: {api_key[:8]}...")
        self.api_key = api_key
        logger.debug("[AlphaVantageProvider.__init__] Provider initialized successfully")

    # ============================================
    # PRIVATE HELPER METHODS
    # ============================================
    
    async def _fetch_data(self, session: aiohttp.ClientSession, url: str, symbol: str = None):
        """
        Fetch data from a URL using the provided session.
        
        Args:
            session: aiohttp ClientSession
            url: URL to fetch data from
            symbol: Optional symbol for logging purposes
            
        Returns:
            JSON data from the API response
        """
        logger.debug(f"[AlphaVantageProvider._fetch_data] Fetching data from URL: {url[:100]}...")
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
                data = await response.json()
                logger.debug(f"[AlphaVantageProvider._fetch_data] Successfully fetched data for symbol: {symbol}")
                return data
        except ProviderSubscriptionError:
            raise
        except Exception as e:
            logger.error(f"[AlphaVantageProvider._fetch_data] Error fetching data for symbol {symbol}: {str(e)}")
            raise

    async def _fetch_company_overview(self, symbol: str) -> dict:
        """
        Fetch company overview data for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Company overview data dictionary
        """
        logger.debug(f"[AlphaVantageProvider._fetch_company_overview] Fetching company overview for symbol: {symbol}")
        get_company_overview_url = config.ALPHA_VANTAGE["overview"].format(symbol=symbol, apikey=self.api_key)

        async with aiohttp.ClientSession() as session:
            company_overview_response = await session.get(get_company_overview_url)
            company_overview_data = await company_overview_response.json()
            logger.debug(f"[AlphaVantageProvider._fetch_company_overview] Successfully fetched company overview for symbol: {symbol}")
            return company_overview_data

    def _extract_most_recent_report(self, data: dict, report_type: str) -> Optional[dict]:
        """
        Extract the most recent report from Alpha Vantage response.
        Alpha Vantage returns data in format: {"annualReports": [...]} or {"quarterlyReports": [...]}
        
        Args:
            data: Raw API response data
            report_type: Type of report (for logging)
            
        Returns:
            Most recent report dictionary or None if not found
        """
        logger.debug(f"[AlphaVantageProvider._extract_most_recent_report] Extracting most recent {report_type} report")
        
        if not data or not isinstance(data, dict):
            logger.warning(f"[AlphaVantageProvider._extract_most_recent_report] Invalid data format for {report_type}")
            return None
        
        # Try annual reports first (most recent), then quarterly
        reports = data.get("annualReports") or data.get("quarterlyReports")
        if not reports or not isinstance(reports, list) or len(reports) == 0:
            logger.warning(f"[AlphaVantageProvider._extract_most_recent_report] No reports found for {report_type}")
            return None
        
        logger.debug(f"[AlphaVantageProvider._extract_most_recent_report] Found {len(reports)} reports for {report_type}, using most recent")
        # Return the first (most recent) report
        return reports[0]

    def _parse_financials_from_symbol(self, symbol: str, income_statement_raw: dict, balance_sheet_raw: dict, cash_flow_raw: dict) -> Financials:
        """
        Parse financial statements from Alpha Vantage API responses for a single symbol.
        
        Args:
            symbol: Stock ticker symbol
            income_statement_raw: Raw income statement API response
            balance_sheet_raw: Raw balance sheet API response
            cash_flow_raw: Raw cash flow API response
            
        Returns:
            Financials object
        """
        logger.debug(f"[AlphaVantageProvider._parse_financials_from_symbol] Parsing financials for symbol: {symbol}")
        
        # Extract most recent reports from Alpha Vantage nested structure
        is_stmt = self._extract_most_recent_report(income_statement_raw, "income_statement")
        bs = self._extract_most_recent_report(balance_sheet_raw, "balance_sheet")
        cf = self._extract_most_recent_report(cash_flow_raw, "cash_flow")
        
        if not is_stmt or not bs or not cf:
            logger.error(f"[AlphaVantageProvider._parse_financials_from_symbol] Incomplete financial data for symbol {symbol}")
            raise IncompleteDataError(
                f"Incomplete financial data for symbol {symbol}",
                missing_fields=["income_statement", "balance_sheet", "cash_flow"]
            )
        
        logger.debug(f"[AlphaVantageProvider._parse_financials_from_symbol] Successfully extracted reports for symbol: {symbol}")
        
        # Extract metadata (Alpha Vantage uses fiscalDateEnding)
        fiscal_year = 0
        period = "FY"
        if is_stmt.get("fiscalDateEnding"):
            try:
                date_str = is_stmt.get("fiscalDateEnding", "")
                fiscal_year = int(date_str.split("-")[0]) if date_str else 0
            except (ValueError, AttributeError):
                pass
        
        # Map to IncomeStatement model (Alpha Vantage uses camelCase)
        income_statement = IncomeStatement(
            revenue=float(is_stmt.get("totalRevenue", 0)),
            gross_profit=float(is_stmt.get("grossProfit", 0)),
            operating_income=float(is_stmt.get("operatingIncome", 0)),
            net_income=float(is_stmt.get("netIncome", 0)),
            eps=float(is_stmt.get("reportedEPS", 0)),
            # Additional fields
            cost_of_revenue=float(is_stmt.get("costOfRevenue", 0)) if is_stmt.get("costOfRevenue") else None,
            ebit=float(is_stmt.get("ebit", 0)) if is_stmt.get("ebit") else None,
            ebitda=float(is_stmt.get("ebitda", 0)) if is_stmt.get("ebitda") else None,
            income_before_tax=float(is_stmt.get("incomeBeforeTax", 0)) if is_stmt.get("incomeBeforeTax") else None,
            income_tax_expense=float(is_stmt.get("incomeTaxExpense", 0)) if is_stmt.get("incomeTaxExpense") else None,
            depreciation_and_amortization=float(is_stmt.get("depreciation", 0)) if is_stmt.get("depreciation") else None,
            interest_income=float(is_stmt.get("interestIncome", 0)) if is_stmt.get("interestIncome") else None,
            interest_expense=float(is_stmt.get("interestExpense", 0)) if is_stmt.get("interestExpense") else None,
            net_interest_income=float(is_stmt.get("netInterestIncome", 0)) if is_stmt.get("netInterestIncome") else None,
            operating_expenses=float(is_stmt.get("operatingExpenses", 0)) if is_stmt.get("operatingExpenses") else None,
            research_and_development=float(is_stmt.get("researchAndDevelopment", 0)) if is_stmt.get("researchAndDevelopment") else None,
            selling_general_and_administrative=float(is_stmt.get("sellingGeneralAndAdministrative", 0)) if is_stmt.get("sellingGeneralAndAdministrative") else None
        )
        
        # Map to BalanceSheet model
        balance_sheet = BalanceSheet(
            total_assets=float(bs.get("totalAssets", 0)),
            total_liabilities=float(bs.get("totalLiabilities", 0)),
            total_equity=float(bs.get("totalShareholderEquity", 0)),
            cash_and_equivalents=float(bs.get("cashAndCashEquivalentsAtCarryingValue", 0)),
            total_debt=float(bs.get("shortLongTermDebtTotal", 0)),
            # Additional fields
            total_current_assets=float(bs.get("totalCurrentAssets", 0)) if bs.get("totalCurrentAssets") else None,
            total_non_current_assets=float(bs.get("totalNonCurrentAssets", 0)) if bs.get("totalNonCurrentAssets") else None,
            total_current_liabilities=float(bs.get("totalCurrentLiabilities", 0)) if bs.get("totalCurrentLiabilities") else None,
            total_non_current_liabilities=float(bs.get("totalNonCurrentLiabilities", 0)) if bs.get("totalNonCurrentLiabilities") else None,
            inventory=float(bs.get("inventory", 0)) if bs.get("inventory") else None,
            accounts_receivables=float(bs.get("currentNetReceivables", 0)) if bs.get("currentNetReceivables") else None,
            long_term_debt=float(bs.get("longTermDebt", 0)) if bs.get("longTermDebt") else None,
            short_term_debt=float(bs.get("shortTermDebt", 0)) if bs.get("shortTermDebt") else None,
            goodwill=float(bs.get("goodwill", 0)) if bs.get("goodwill") else None,
            intangible_assets=float(bs.get("intangibleAssetsExcludingGoodwill", 0)) if bs.get("intangibleAssetsExcludingGoodwill") else None,
            property_plant_equipment=float(bs.get("propertyPlantEquipment", 0)) if bs.get("propertyPlantEquipment") else None,
            retained_earnings=float(bs.get("retainedEarnings", 0)) if bs.get("retainedEarnings") else None,
            common_stock=float(bs.get("commonStock", 0)) if bs.get("commonStock") else None,
            common_stock_shares_outstanding=float(bs.get("commonStockSharesOutstanding", 0)) if bs.get("commonStockSharesOutstanding") else None
        )
        
        # Map to CashFlow model
        cash_flow = CashFlow(
            operating_cash_flow=float(cf.get("operatingCashflow", 0)),
            free_cash_flow=float(cf.get("operatingCashflow", 0)) - abs(float(cf.get("capitalExpenditures", 0))),
            capital_expenditure=abs(float(cf.get("capitalExpenditures", 0))),
            # Additional fields
            net_income=float(cf.get("netIncome", 0)) if cf.get("netIncome") else None,
            depreciation_depletion_and_amortization=float(cf.get("depreciationDepletionAndAmortization", 0)) if cf.get("depreciationDepletionAndAmortization") else None,
            dividend_payout=float(cf.get("dividendPayout", 0)) if cf.get("dividendPayout") else None,
            cashflow_from_investment=float(cf.get("cashflowFromInvestment", 0)) if cf.get("cashflowFromInvestment") else None,
            cashflow_from_financing=float(cf.get("cashflowFromFinancing", 0)) if cf.get("cashflowFromFinancing") else None,
            change_in_cash_and_cash_equivalents=float(cf.get("changeInCashAndCashEquivalents", 0)) if cf.get("changeInCashAndCashEquivalents") else None
        )
        
        # Create metadata
        metadata = FinancialsMetadata(
            fiscal_year=fiscal_year,
            period=period
        )
        
        # Return Financials object
        try:
            financials = Financials(
                income_statement=income_statement,
                balance_sheet=balance_sheet,
                cash_flow=cash_flow,
                metadata=metadata
            )
            logger.debug(f"[AlphaVantageProvider._parse_financials_from_symbol] Successfully created Financials object for symbol: {symbol}")
            return financials
        except ValidationError as e:
            logger.error(f"[AlphaVantageProvider._parse_financials_from_symbol] Validation error for symbol {symbol}: {str(e)}")
            raise DataValidationError(
                f"Financials data validation failed for symbol {symbol}: {str(e)}",
                field="financials"
            ) from e

    def _extract_most_recent_report(self, data: dict, report_type: str) -> Optional[dict]:
        """
        Extract the most recent report from Alpha Vantage response.
        Alpha Vantage returns data in format: {"annualReports": [...]} or {"quarterlyReports": [...]}
        """
        if not data or not isinstance(data, dict):
            return None
        
        # Try annual reports first (most recent), then quarterly
        reports = data.get("annualReports") or data.get("quarterlyReports")
        if not reports or not isinstance(reports, list) or len(reports) == 0:
            return None
        
        # Return the first (most recent) report
        return reports[0]

    def _parse_financials_from_symbol(self, symbol: str, income_statement_raw: dict, balance_sheet_raw: dict, cash_flow_raw: dict) -> Financials:
        """
        Parse financial statements from Alpha Vantage API responses for a single symbol.
        
        Args:
            symbol: Stock ticker symbol
            income_statement_raw: Raw income statement API response
            balance_sheet_raw: Raw balance sheet API response
            cash_flow_raw: Raw cash flow API response
            
        Returns:
            Financials object
        """
        logger.debug(f"[AlphaVantageProvider._parse_financials_from_symbol] Parsing financials for symbol: {symbol}")
        
        # Extract most recent reports from Alpha Vantage nested structure
        is_stmt = self._extract_most_recent_report(income_statement_raw, "income_statement")
        bs = self._extract_most_recent_report(balance_sheet_raw, "balance_sheet")
        cf = self._extract_most_recent_report(cash_flow_raw, "cash_flow")
        
        if not is_stmt or not bs or not cf:
            logger.error(f"[AlphaVantageProvider._parse_financials_from_symbol] Incomplete financial data for symbol {symbol}")
            raise IncompleteDataError(
                f"Incomplete financial data for symbol {symbol}",
                missing_fields=["income_statement", "balance_sheet", "cash_flow"]
            )
        
        logger.debug(f"[AlphaVantageProvider._parse_financials_from_symbol] Successfully extracted reports for symbol: {symbol}")
        
        # Extract metadata (Alpha Vantage uses fiscalDateEnding)
        fiscal_year = 0
        period = "FY"
        if is_stmt.get("fiscalDateEnding"):
            try:
                date_str = is_stmt.get("fiscalDateEnding", "")
                fiscal_year = int(date_str.split("-")[0]) if date_str else 0
            except (ValueError, AttributeError):
                pass
        
        # Map to IncomeStatement model (Alpha Vantage uses camelCase)
        income_statement = IncomeStatement(
            revenue=float(is_stmt.get("totalRevenue", 0)),
            gross_profit=float(is_stmt.get("grossProfit", 0)),
            operating_income=float(is_stmt.get("operatingIncome", 0)),
            net_income=float(is_stmt.get("netIncome", 0)),
            eps=float(is_stmt.get("reportedEPS", 0)),
            # Additional fields
            cost_of_revenue=float(is_stmt.get("costOfRevenue", 0)) if is_stmt.get("costOfRevenue") else None,
            ebit=float(is_stmt.get("ebit", 0)) if is_stmt.get("ebit") else None,
            ebitda=float(is_stmt.get("ebitda", 0)) if is_stmt.get("ebitda") else None,
            income_before_tax=float(is_stmt.get("incomeBeforeTax", 0)) if is_stmt.get("incomeBeforeTax") else None,
            income_tax_expense=float(is_stmt.get("incomeTaxExpense", 0)) if is_stmt.get("incomeTaxExpense") else None,
            depreciation_and_amortization=float(is_stmt.get("depreciation", 0)) if is_stmt.get("depreciation") else None,
            interest_income=float(is_stmt.get("interestIncome", 0)) if is_stmt.get("interestIncome") else None,
            interest_expense=float(is_stmt.get("interestExpense", 0)) if is_stmt.get("interestExpense") else None,
            net_interest_income=float(is_stmt.get("netInterestIncome", 0)) if is_stmt.get("netInterestIncome") else None,
            operating_expenses=float(is_stmt.get("operatingExpenses", 0)) if is_stmt.get("operatingExpenses") else None,
            research_and_development=float(is_stmt.get("researchAndDevelopment", 0)) if is_stmt.get("researchAndDevelopment") else None,
            selling_general_and_administrative=float(is_stmt.get("sellingGeneralAndAdministrative", 0)) if is_stmt.get("sellingGeneralAndAdministrative") else None
        )
        
        # Map to BalanceSheet model
        balance_sheet = BalanceSheet(
            total_assets=float(bs.get("totalAssets", 0)),
            total_liabilities=float(bs.get("totalLiabilities", 0)),
            total_equity=float(bs.get("totalShareholderEquity", 0)),
            cash_and_equivalents=float(bs.get("cashAndCashEquivalentsAtCarryingValue", 0)),
            total_debt=float(bs.get("shortLongTermDebtTotal", 0)),
            # Additional fields
            total_current_assets=float(bs.get("totalCurrentAssets", 0)) if bs.get("totalCurrentAssets") else None,
            total_non_current_assets=float(bs.get("totalNonCurrentAssets", 0)) if bs.get("totalNonCurrentAssets") else None,
            total_current_liabilities=float(bs.get("totalCurrentLiabilities", 0)) if bs.get("totalCurrentLiabilities") else None,
            total_non_current_liabilities=float(bs.get("totalNonCurrentLiabilities", 0)) if bs.get("totalNonCurrentLiabilities") else None,
            inventory=float(bs.get("inventory", 0)) if bs.get("inventory") else None,
            accounts_receivables=float(bs.get("currentNetReceivables", 0)) if bs.get("currentNetReceivables") else None,
            long_term_debt=float(bs.get("longTermDebt", 0)) if bs.get("longTermDebt") else None,
            short_term_debt=float(bs.get("shortTermDebt", 0)) if bs.get("shortTermDebt") else None,
            goodwill=float(bs.get("goodwill", 0)) if bs.get("goodwill") else None,
            intangible_assets=float(bs.get("intangibleAssetsExcludingGoodwill", 0)) if bs.get("intangibleAssetsExcludingGoodwill") else None,
            property_plant_equipment=float(bs.get("propertyPlantEquipment", 0)) if bs.get("propertyPlantEquipment") else None,
            retained_earnings=float(bs.get("retainedEarnings", 0)) if bs.get("retainedEarnings") else None,
            common_stock=float(bs.get("commonStock", 0)) if bs.get("commonStock") else None,
            common_stock_shares_outstanding=float(bs.get("commonStockSharesOutstanding", 0)) if bs.get("commonStockSharesOutstanding") else None
        )
        
        # Map to CashFlow model
        cash_flow = CashFlow(
            operating_cash_flow=float(cf.get("operatingCashflow", 0)),
            free_cash_flow=float(cf.get("operatingCashflow", 0)) - abs(float(cf.get("capitalExpenditures", 0))),
            capital_expenditure=abs(float(cf.get("capitalExpenditures", 0))),
            # Additional fields
            net_income=float(cf.get("netIncome", 0)) if cf.get("netIncome") else None,
            depreciation_depletion_and_amortization=float(cf.get("depreciationDepletionAndAmortization", 0)) if cf.get("depreciationDepletionAndAmortization") else None,
            dividend_payout=float(cf.get("dividendPayout", 0)) if cf.get("dividendPayout") else None,
            cashflow_from_investment=float(cf.get("cashflowFromInvestment", 0)) if cf.get("cashflowFromInvestment") else None,
            cashflow_from_financing=float(cf.get("cashflowFromFinancing", 0)) if cf.get("cashflowFromFinancing") else None,
            change_in_cash_and_cash_equivalents=float(cf.get("changeInCashAndCashEquivalents", 0)) if cf.get("changeInCashAndCashEquivalents") else None
        )
        
        # Create metadata
        metadata = FinancialsMetadata(
            fiscal_year=fiscal_year,
            period=period
        )
        
        # Return Financials object
        try:
            financials = Financials(
                income_statement=income_statement,
                balance_sheet=balance_sheet,
                cash_flow=cash_flow,
                metadata=metadata
            )
            logger.debug(f"[AlphaVantageProvider._parse_financials_from_symbol] Successfully created Financials object for symbol: {symbol}")
            return financials
        except ValidationError as e:
            logger.error(f"[AlphaVantageProvider._parse_financials_from_symbol] Validation error for symbol {symbol}: {str(e)}")
            raise DataValidationError(
                f"Financials data validation failed for symbol {symbol}: {str(e)}",
                field="financials"
            ) from e

    # ============================================
    # PUBLIC API METHODS
    # ============================================
    
    async def _fetch_stocks(self, symbol: str) -> List[dict]:
        """
        Fetch stock matches for a keyword search.
        
        Args:
            symbol: Keyword to search for (can be company name or ticker)
            
        Returns:
            List of stock match dictionaries
        """
        logger.debug(f"[AlphaVantageProvider._fetch_stocks] Searching for stocks with keyword: {symbol}")
        get_keyword_search_url = config.ALPHA_VANTAGE["keyword_search"].format(keyword=symbol, apikey=self.api_key)

        async with aiohttp.ClientSession() as session:
            keyword_search_response = await session.get(get_keyword_search_url)
            keyword_search_data = await keyword_search_response.json()

            stocks = keyword_search_data.get("bestMatches")
            
            if not stocks or len(stocks) == 0:
                logger.warning(f"[AlphaVantageProvider._fetch_stocks] No matches found for keyword: {symbol}")
                raise DataValidationError(
                    f"No keyword search data found for symbol {symbol}",
                    field="keyword_search"
                )
            
            logger.debug(f"[AlphaVantageProvider._fetch_stocks] Found {len(stocks)} stock matches for keyword: {symbol}")
            self.stocks_list = stocks
            return stocks

    async def get_market_data(self) -> List[MarketData]:
        """
        Fetch market data for multiple stocks from keyword search results.
        Uses stocks_list stored from _fetch_stocks.
        
        Returns:
            List of MarketData objects
        """
        logger.debug(f"[AlphaVantageProvider.get_market_data] Fetching market data for {len(self.stocks_list)} stocks")
        market_data_list = []
        
        if not self.stocks_list:
            logger.warning("[AlphaVantageProvider.get_market_data] No stocks in stocks_list, returning empty list")
            return market_data_list
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            symbols = []
            for stock in self.stocks_list:
                # Handle both dict format {"1. symbol": "SAIC"} and object format with .symbol attribute
                symbol = stock.get("1. symbol") if isinstance(stock, dict) else getattr(stock, "symbol", None)
                if symbol:
                    symbols.append(symbol)
                    url = config.ALPHA_VANTAGE["overview"].format(symbol=symbol, apikey=self.api_key)
                    tasks.append(self._fetch_data(session, url, symbol))
            
            logger.debug(f"[AlphaVantageProvider.get_market_data] Fetching {len(tasks)} company overviews concurrently")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.debug(f"[AlphaVantageProvider.get_market_data] Processing {len(results)} results")
            for i, (stock, overview) in enumerate(zip(self.stocks_list, results)):
                # Handle both dict format and object format
                symbol = stock.get("1. symbol") if isinstance(stock, dict) else getattr(stock, "symbol", f"stock_{i}")
                
                if isinstance(overview, Exception):
                    logger.warning(f"[AlphaVantageProvider.get_market_data] Error fetching overview for {symbol}: {str(overview)}")
                    continue
                
                if not overview or not isinstance(overview, dict):
                    logger.warning(f"[AlphaVantageProvider.get_market_data] Invalid overview data for {symbol}")
                    continue
                
                logger.debug(f"[AlphaVantageProvider.get_market_data] Processing market data for {symbol}")
                
                # Extract market data from Alpha Vantage company overview
                market_cap_str = overview.get("MarketCapitalization", "0")
                market_cap = float(market_cap_str) if market_cap_str and market_cap_str != "None" else 0.0
                
                shares_outstanding_str = overview.get("SharesOutstanding", "0")
                shares_outstanding = float(shares_outstanding_str) if shares_outstanding_str and shares_outstanding_str != "None" else 0.0
                
                # Calculate current price from market cap and shares outstanding
                current_price = market_cap / shares_outstanding if shares_outstanding > 0 else 0.0
                
                beta_str = overview.get("Beta", "0")
                beta = float(beta_str) if beta_str and beta_str != "None" else 0.0
                
                week_52_high_str = overview.get("52WeekHigh", "0")
                week_52_high = float(week_52_high_str) if week_52_high_str and week_52_high_str != "None" else 0.0
                
                week_52_low_str = overview.get("52WeekLow", "0")
                week_52_low = float(week_52_low_str) if week_52_low_str and week_52_low_str != "None" else 0.0
                
                try:
                    market_data = MarketData(
                        current_price=current_price,
                        market_cap=market_cap,
                        shares_outstanding=shares_outstanding,
                        beta=beta,
                        volume=0.0,  # Alpha Vantage overview doesn't include volume
                        average_volume=0.0,  # Alpha Vantage overview doesn't include average volume
                        week_52_high=week_52_high,
                        week_52_low=week_52_low
                    )
                    market_data_list.append(market_data)
                    logger.debug(f"[AlphaVantageProvider.get_market_data] Successfully created MarketData for {symbol}")
                except ValidationError as e:
                    logger.warning(f"[AlphaVantageProvider.get_market_data] Validation error for {symbol}: {str(e)}")
                    continue
        
        logger.debug(f"[AlphaVantageProvider.get_market_data] Successfully fetched market data for {len(market_data_list)} stocks")
        self.market_data_list = market_data_list
        return market_data_list

    async def get_financials(self) -> List[Financials]:
        """
        Fetch financial statements (income statement, balance sheet, cash flow) for multiple stocks.
        Uses stocks_list stored from _fetch_stocks.
        
        Returns:
            List of Financials objects
        """
        logger.debug(f"[AlphaVantageProvider.get_financials] Fetching financials for {len(self.stocks_list)} stocks")
        financials_list = []
        
        if not self.stocks_list:
            logger.warning("[AlphaVantageProvider.get_financials] No stocks in stocks_list, returning empty list")
            return financials_list
        
        async with aiohttp.ClientSession() as session:
            # Prepare all URLs for all stocks
            all_urls = []
            symbols = []
            for stock in self.stocks_list:
                # Handle both dict format and object format
                symbol = stock.get("1. symbol") if isinstance(stock, dict) else getattr(stock, "symbol", None)
                if symbol:
                    symbols.append(symbol)
                    all_urls.extend([
                        config.ALPHA_VANTAGE["income_statement"].format(symbol=symbol, apikey=self.api_key),
                        config.ALPHA_VANTAGE["balance_sheet"].format(symbol=symbol, apikey=self.api_key),
                        config.ALPHA_VANTAGE["cash_flow"].format(symbol=symbol, apikey=self.api_key),
                    ])
            
            logger.debug(f"[AlphaVantageProvider.get_financials] Fetching {len(all_urls)} financial statements concurrently for {len(symbols)} symbols")
            
            # Fetch all data concurrently
            tasks = [self._fetch_data(session, url) for url in all_urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.debug(f"[AlphaVantageProvider.get_financials] Processing {len(results)} results in groups of 3 per symbol")
            
            # Process results in groups of 3 (income, balance, cash flow) per symbol
            for i, symbol in enumerate(symbols):
                idx = i * 3
                income_statement_raw = results[idx] if not isinstance(results[idx], Exception) else {}
                balance_sheet_raw = results[idx + 1] if not isinstance(results[idx + 1], Exception) else {}
                cash_flow_raw = results[idx + 2] if not isinstance(results[idx + 2], Exception) else {}
                
                try:
                    financials = self._parse_financials_from_symbol(symbol, income_statement_raw, balance_sheet_raw, cash_flow_raw)
                    financials_list.append(financials)
                    logger.debug(f"[AlphaVantageProvider.get_financials] Successfully parsed financials for {symbol}")
                except (IncompleteDataError, DataValidationError, Exception) as e:
                    logger.warning(f"[AlphaVantageProvider.get_financials] Error parsing financials for {symbol}: {str(e)}")
                    continue
        
        logger.debug(f"[AlphaVantageProvider.get_financials] Successfully fetched financials for {len(financials_list)} stocks")
        self.financials_list = financials_list
        return financials_list

    async def get_growth(self) -> List[GrowthMetrics]:
        """
        Fetch growth metrics for multiple stocks.
        Currently not implemented for Alpha Vantage.
        
        Returns:
            List of GrowthMetrics objects
        """
        logger.debug(f"[AlphaVantageProvider.get_growth] get_growth called (not implemented)")
        return []

    async def get_ratios(self) -> List[Ratios]:
        """
        Calculate financial ratios from market_data_list and financials_list.
        Uses stored market_data_list and financials_list from previous API calls.
        
        Returns:
            List of Ratios objects calculated from stored market_data_list and financials_list
        """
        logger.debug(f"[AlphaVantageProvider.get_ratios] Calculating ratios from {len(self.market_data_list)} market data and {len(self.financials_list)} financials")
        ratios_list = []
        
        # Ensure we have matching data for market and financials
        min_length = min(len(self.market_data_list), len(self.financials_list))
        logger.debug(f"[AlphaVantageProvider.get_ratios] Processing ratios for {min_length} stocks")
        
        for i in range(min_length):
            market = self.market_data_list[i]
            financials = self.financials_list[i]
            
            logger.debug(f"[AlphaVantageProvider.get_ratios] Calculating ratios for stock {i+1}/{min_length}")
            
            try:
                # Extract data for easier access
                income = financials.income_statement
                balance = financials.balance_sheet
                market_price = market.current_price
                market_cap = market.market_cap
                
                logger.debug(f"[AlphaVantageProvider.get_ratios] Extracted data - Revenue: {income.revenue}, Market Cap: {market_cap}, Price: {market_price}")
                
                # ============================================
                # 1. PROFITABILITY RATIOS
                # ============================================
                # Gross Margin: (Gross Profit / Revenue) × 100
                gross_margin = 0.0
                if income.revenue > 0:
                    gross_margin = (income.gross_profit / income.revenue) * 100
                
                # Operating Margin: (Operating Income / Revenue) × 100
                operating_margin = 0.0
                if income.revenue > 0:
                    operating_margin = (income.operating_income / income.revenue) * 100
                
                # Net Margin: (Net Income / Revenue) × 100
                net_margin = 0.0
                if income.revenue > 0:
                    net_margin = (income.net_income / income.revenue) * 100
                
                # Return on Equity (ROE): (Net Income / Total Equity) × 100
                return_on_equity = 0.0
                if balance.total_equity > 0:
                    return_on_equity = (income.net_income / balance.total_equity) * 100
                
                # Return on Assets (ROA): (Net Income / Total Assets) × 100
                return_on_assets = 0.0
                if balance.total_assets > 0:
                    return_on_assets = (income.net_income / balance.total_assets) * 100
                
                profitability = Profitability(
                    gross_margin=gross_margin,
                    operating_margin=operating_margin,
                    net_margin=net_margin,
                    return_on_equity=return_on_equity,
                    return_on_assets=return_on_assets
                )
                
                # ============================================
                # 2. VALUATION RATIOS
                # ============================================
                # Price-to-Earnings (P/E): Current Price / Earnings Per Share
                price_to_earnings = 0.0
                if income.eps > 0:
                    price_to_earnings = market_price / income.eps
                
                # Price-to-Book (P/B): Market Cap / Total Equity
                price_to_book = 0.0
                if balance.total_equity > 0:
                    price_to_book = market_cap / balance.total_equity
                
                # Price-to-Sales (P/S): Market Cap / Revenue
                price_to_sales = 0.0
                if income.revenue > 0:
                    price_to_sales = market_cap / income.revenue
                
                valuation = Valuation(
                    price_to_earnings=price_to_earnings,
                    price_to_book=price_to_book,
                    price_to_sales=price_to_sales
                )
                
                # ============================================
                # 3. LEVERAGE AND LIQUIDITY RATIOS
                # ============================================
                # Debt-to-Equity: Total Debt / Total Equity
                debt_to_equity = 0.0
                if balance.total_equity > 0:
                    debt_to_equity = balance.total_debt / balance.total_equity
                
                # Current Ratio: Current Assets / Current Liabilities
                current_ratio = 0.0
                if balance.total_current_assets is not None and balance.total_current_liabilities is not None:
                    if balance.total_current_liabilities > 0:
                        current_ratio = balance.total_current_assets / balance.total_current_liabilities
                
                leverage_and_liquidity = LeverageAndLiquidity(
                    debt_to_equity=debt_to_equity,
                    current_ratio=current_ratio
                )
                
                # Create and return Ratios object
                ratios = Ratios(
                    profitability=profitability,
                    valuation=valuation,
                    leverage_and_liquidity=leverage_and_liquidity
                )
                
                ratios_list.append(ratios)
                logger.debug(f"[AlphaVantageProvider.get_ratios] Successfully calculated ratios for stock {i+1}")
                
            except (ZeroDivisionError, ValueError, AttributeError, TypeError) as e:
                logger.warning(f"[AlphaVantageProvider.get_ratios] Calculation error for stock {i+1}: {str(e)}, using default ratios")
                # Skip stocks with calculation errors but continue processing others
                # Create default ratios with zeros
                try:
                    default_ratios = Ratios(
                        profitability=Profitability(
                            gross_margin=0.0,
                            operating_margin=0.0,
                            net_margin=0.0,
                            return_on_equity=0.0,
                            return_on_assets=0.0
                        ),
                        valuation=Valuation(
                            price_to_earnings=0.0,
                            price_to_book=0.0,
                            price_to_sales=0.0
                        ),
                        leverage_and_liquidity=LeverageAndLiquidity(
                            debt_to_equity=0.0,
                            current_ratio=0.0
                        )
                    )
                    ratios_list.append(default_ratios)
                    logger.debug(f"[AlphaVantageProvider.get_ratios] Created default ratios for stock {i+1}")
                except Exception as e2:
                    logger.error(f"[AlphaVantageProvider.get_ratios] Failed to create default ratios for stock {i+1}: {str(e2)}")
                    continue
        
        logger.debug(f"[AlphaVantageProvider.get_ratios] Successfully calculated ratios for {len(ratios_list)} stocks")
        return ratios_list

    async def get_fundamentals(self, symbol: str) -> List[Fundamentals]:
        """
        Fetch complete fundamentals data for a symbol.
        Currently not implemented for Alpha Vantage (use _fetch_stocks + get_market_data + get_financials + get_ratios instead).
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            List of Fundamentals objects
        """
        logger.debug(f"[AlphaVantageProvider.get_fundamentals] get_fundamentals called for {symbol} (not implemented)")
        return []