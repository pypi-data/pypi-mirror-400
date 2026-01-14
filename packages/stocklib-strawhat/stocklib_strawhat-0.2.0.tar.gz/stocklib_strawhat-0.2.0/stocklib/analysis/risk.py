from stocklib.models.financials import Financials
from stocklib.models.risk import RiskMetrics


def calculate_risk(financials: Financials) -> RiskMetrics:
    """
    Calculate risk metrics from financial statements.
    Risk metrics help assess financial stability and solvency.
    
    Args:
        financials: Financial statements (income statement, balance sheet, cash flow)
        
    Returns:
        RiskMetrics object with calculated risk indicators
    """
    # Extract data for easier access
    income = financials.income_statement
    balance = financials.balance_sheet
    cash_flow = financials.cash_flow
    
    # ============================================
    # 1. DEBT RATIO
    # ============================================
    # Debt Ratio: Total Debt / Total Assets
    # Measures what percentage of assets are financed by debt
    # Higher ratio = higher financial risk
    debt_ratio = 0.0
    if balance.total_assets > 0:
        debt_ratio = balance.total_debt / balance.total_assets
    
    # ============================================
    # 2. INTEREST COVERAGE RATIO
    # ============================================
    # Interest Coverage: Operating Income / Interest Expense
    # Measures ability to pay interest on debt
    # Note: Interest expense is not directly available in our IncomeStatement model
    # We estimate based on debt levels and operating income
    # Higher ratio = better ability to service debt
    # Typical good coverage: > 1.5, excellent: > 3.0
    interest_coverage = 0.0
    # Since we don't have interest_expense in the model, we estimate it
    # Rough estimation: assume interest expense is ~2-5% of total debt
    # This is a simplification - actual calculation requires: income.operating_income / interest_expense
    if balance.total_debt > 0 and income.operating_income > 0:
        # Estimate interest expense as ~3% of total debt (typical corporate bond rate)
        estimated_interest_expense = balance.total_debt * 0.03
        if estimated_interest_expense > 0:
            interest_coverage = income.operating_income / estimated_interest_expense
    elif income.operating_income <= 0:
        # Negative or zero operating income means cannot cover interest
        interest_coverage = 0.0
    # If no debt, coverage is infinite (no interest to pay), but we'll set to a high value
    elif balance.total_debt == 0:
        interest_coverage = 999.0  # Indicates no debt, excellent coverage
    
    # ============================================
    # 3. EARNINGS VOLATILITY
    # ============================================
    # Earnings Volatility: Measure of earnings stability over time
    # This requires historical data (multiple periods) to calculate standard deviation
    # Since we only have current period data, we use a simplified approach:
    # - If net income is negative, volatility is high
    # - If net income is positive and stable, volatility is lower
    # For a proper calculation, you'd need: std_dev(net_income) / mean(net_income)
    earnings_volatility = 0.0
    if income.net_income < 0:
        # Negative earnings indicate high volatility/risk
        earnings_volatility = abs(income.net_income) / max(abs(income.revenue), 1.0) if income.revenue != 0 else 1.0
    elif income.revenue > 0:
        # Calculate coefficient of variation approximation
        # Using net income margin as a proxy for stability
        net_margin = income.net_income / income.revenue
        # Lower margins suggest higher volatility risk
        earnings_volatility = max(0.0, 1.0 - abs(net_margin))
    
    # ============================================
    # 4. CASH RUNWAY (Optional)
    # ============================================
    # Cash Runway: Estimated years of cash runway based on burn rate
    # Formula: Cash / (Annual Burn Rate)
    # Burn rate = negative free cash flow (if company is burning cash)
    # If FCF is positive, company is generating cash (runway is infinite/not applicable)
    cash_runway_years = None
    if cash_flow.free_cash_flow < 0:
        # Company is burning cash - calculate runway
        annual_burn_rate = abs(cash_flow.free_cash_flow)
        if annual_burn_rate > 0 and balance.cash_and_equivalents > 0:
            cash_runway_years = balance.cash_and_equivalents / annual_burn_rate
    # If FCF is positive, company is generating cash, so runway is not applicable (None)
    
    return RiskMetrics(
        debt_ratio=debt_ratio,
        interest_coverage=interest_coverage,
        earnings_volatility=earnings_volatility,
        cash_runway_years=cash_runway_years
    )