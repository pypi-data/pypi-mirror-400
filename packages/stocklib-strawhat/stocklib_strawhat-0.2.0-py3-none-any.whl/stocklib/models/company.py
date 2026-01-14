from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class Company(BaseModel):
    symbol: str = Field(description="Ticker symbol (e.g., AAPL)")
    name: str = Field(description="Company name (e.g., Apple Inc.)")
    exchange: str = Field(description="Stock exchange (e.g., NASDAQ)")
    sector: str = Field(description="Business sector (e.g., Technology)")
    industry: str = Field(description="Industry classification (e.g., Consumer Electronics)")
    country: str = Field(description="Country of operation (e.g., USA)")
    currency: str = Field(description="Trading currency (e.g., USD)")
    ipo_date: Optional[date] = Field(default=None, description="Initial public offering date")
    website: Optional[str] = Field(default=None, description="Company website URL")
