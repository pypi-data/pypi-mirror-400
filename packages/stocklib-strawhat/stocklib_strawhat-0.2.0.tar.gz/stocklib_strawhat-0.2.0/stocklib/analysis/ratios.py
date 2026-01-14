from stocklib.models.financials import Financials
from stocklib.models.market import MarketData
from stocklib.models.ratios import Ratios, Profitability, Valuation, LeverageAndLiquidity


def calculate_ratios(financials: Financials, market: MarketData, ratios: Ratios) -> Ratios:
    """
    Calculate financial ratios from raw financial and market data.
    Uses provider ratios as fallback when calculations fail or data is missing.
    
    Args:
        financials: Financial statements (income statement, balance sheet, cash flow)
        market: Market data (price, market cap, shares outstanding)
        ratios: Provider-calculated ratios (used as fallback)
        
    Returns:
        Ratios object with calculated profitability, valuation, and leverage/liquidity ratios
    """
    # Extract data for easier access
    income = financials.income_statement
    balance = financials.balance_sheet
    market_price = market.current_price
    market_cap = market.market_cap
    
    # ============================================
    # 1. PROFITABILITY RATIOS
    # ============================================
    # Calculate from raw financial data, fallback to provider ratios if calculation fails
    
    # Gross Margin: (Gross Profit / Revenue) × 100
    gross_margin = ratios.profitability.gross_margin  # Default to provider value
    if income.revenue > 0:
        calculated_gross_margin = (income.gross_profit / income.revenue) * 100
        gross_margin = calculated_gross_margin
    
    # Operating Margin: (Operating Income / Revenue) × 100
    operating_margin = ratios.profitability.operating_margin  # Default to provider value
    if income.revenue > 0:
        calculated_operating_margin = (income.operating_income / income.revenue) * 100
        operating_margin = calculated_operating_margin
    
    # Net Margin: (Net Income / Revenue) × 100
    net_margin = ratios.profitability.net_margin  # Default to provider value
    if income.revenue > 0:
        calculated_net_margin = (income.net_income / income.revenue) * 100
        net_margin = calculated_net_margin
    
    # Return on Equity (ROE): (Net Income / Total Equity) × 100
    return_on_equity = ratios.profitability.return_on_equity  # Default to provider value
    if balance.total_equity > 0:
        calculated_roe = (income.net_income / balance.total_equity) * 100
        return_on_equity = calculated_roe
    
    # Return on Assets (ROA): (Net Income / Total Assets) × 100
    return_on_assets = ratios.profitability.return_on_assets  # Default to provider value
    if balance.total_assets > 0:
        calculated_roa = (income.net_income / balance.total_assets) * 100
        return_on_assets = calculated_roa
    
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
    # Calculate from market data and financials, fallback to provider ratios if calculation fails
    
    # Price-to-Earnings (P/E): Current Price / Earnings Per Share
    price_to_earnings = ratios.valuation.price_to_earnings  # Default to provider value
    if income.eps > 0:
        calculated_pe = market_price / income.eps
        price_to_earnings = calculated_pe
    
    # Price-to-Book (P/B): Market Cap / Total Equity
    price_to_book = ratios.valuation.price_to_book  # Default to provider value
    if balance.total_equity > 0:
        calculated_pb = market_cap / balance.total_equity
        price_to_book = calculated_pb
    
    # Price-to-Sales (P/S): Market Cap / Revenue
    price_to_sales = ratios.valuation.price_to_sales  # Default to provider value
    if income.revenue > 0:
        calculated_ps = market_cap / income.revenue
        price_to_sales = calculated_ps
    
    valuation = Valuation(
        price_to_earnings=price_to_earnings,
        price_to_book=price_to_book,
        price_to_sales=price_to_sales
    )
    
    # ============================================
    # 3. LEVERAGE AND LIQUIDITY RATIOS
    # ============================================
    # Calculate from balance sheet, fallback to provider ratios if calculation fails
    
    # Debt-to-Equity: Total Debt / Total Equity
    debt_to_equity = ratios.leverage_and_liquidity.debt_to_equity  # Default to provider value
    if balance.total_equity > 0:
        calculated_dte = balance.total_debt / balance.total_equity
        debt_to_equity = calculated_dte
    
    # Current Ratio: Current Assets / Current Liabilities
    # Note: Current assets and current liabilities are not directly available in our BalanceSheet model
    # So we use the provider's calculated value as it has access to more detailed balance sheet data
    current_ratio = ratios.leverage_and_liquidity.current_ratio
    
    leverage_and_liquidity = LeverageAndLiquidity(
        debt_to_equity=debt_to_equity,
        current_ratio=current_ratio
    )
    
    # ============================================
    # 4. RETURN COMPLETE RATIOS OBJECT
    # ============================================
    return Ratios(
        profitability=profitability,
        valuation=valuation,
        leverage_and_liquidity=leverage_and_liquidity
    )