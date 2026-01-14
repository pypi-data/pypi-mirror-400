from pydantic import BaseModel, Field


class GrowthMetrics(BaseModel):
    revenue_growth_yoy: float = Field(description="Revenue growth year-over-year (YoY) percentage")
    net_income_growth_yoy: float = Field(description="Net income growth year-over-year (YoY) percentage")
    free_cash_flow_growth_yoy: float = Field(description="Free cash flow growth year-over-year (YoY) percentage")
    eps_growth_yoy: float = Field(description="Earnings per share growth year-over-year (YoY) percentage")
