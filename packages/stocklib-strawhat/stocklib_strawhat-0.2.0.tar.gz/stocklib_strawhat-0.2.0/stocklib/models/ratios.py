from pydantic import BaseModel, Field


class Profitability(BaseModel):
    gross_margin: float = Field(description="Gross margin percentage (gross_profit / revenue)")
    operating_margin: float = Field(description="Operating margin percentage (operating_income / revenue)")
    net_margin: float = Field(description="Net margin percentage (net_income / revenue)")
    return_on_equity: float = Field(description="Return on equity (ROE) percentage")
    return_on_assets: float = Field(description="Return on assets (ROA) percentage")


class Valuation(BaseModel):
    price_to_earnings: float = Field(description="Price-to-earnings ratio (P/E)")
    price_to_book: float = Field(description="Price-to-book ratio (P/B)")
    price_to_sales: float = Field(description="Price-to-sales ratio (P/S)")


class LeverageAndLiquidity(BaseModel):
    debt_to_equity: float = Field(description="Debt-to-equity ratio")
    current_ratio: float = Field(description="Current ratio (current_assets / current_liabilities)")


class Ratios(BaseModel):
    profitability: Profitability = Field(description="Profitability ratios")
    valuation: Valuation = Field(description="Valuation ratios")
    leverage_and_liquidity: LeverageAndLiquidity = Field(description="Leverage and liquidity ratios")
