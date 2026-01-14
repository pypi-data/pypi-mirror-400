from pydantic import BaseModel, Field
from typing import Optional


class RiskMetrics(BaseModel):
    debt_ratio: float = Field(description="Debt ratio (total_debt / total_assets)")
    interest_coverage: float = Field(description="Interest coverage ratio (operating_income / interest_expense)")
    earnings_volatility: float = Field(description="Earnings volatility measure (standard deviation or coefficient of variation)")
    cash_runway_years: Optional[float] = Field(default=None, description="Estimated years of cash runway based on current burn rate")
