from pydantic import BaseModel, Field
from typing import Optional
from stocklib.models.financials import Financials
from stocklib.models.company import Company
from stocklib.models.market import MarketData
from stocklib.models.ratios import Ratios
from stocklib.models.risk import RiskMetrics
from stocklib.models.growth import GrowthMetrics
from stocklib.models.metadata import Metadata


class Fundamentals(BaseModel):
    company: Company = Field(description="Company information")
    financials: Financials = Field(description="Financial statements data")
    market: MarketData = Field(description="Market data")
    ratios: Ratios = Field(description="Financial ratios")
    growth: Optional[GrowthMetrics] = Field(default=None, description="Growth metrics (optional)")
    risk: Optional[RiskMetrics] = Field(default=None, description="Risk metrics (optional)")
    metadata: Metadata = Field(description="Data metadata")

    class Config:
        frozen = True
        extra = "forbid"
