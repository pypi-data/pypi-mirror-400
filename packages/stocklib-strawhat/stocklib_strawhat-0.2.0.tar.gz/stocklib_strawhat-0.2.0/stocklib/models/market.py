from pydantic import BaseModel, Field


class MarketData(BaseModel):
    current_price: float = Field(description="Current stock price")
    market_cap: float = Field(description="Market capitalization (current_price × shares_outstanding)")
    shares_outstanding: float = Field(description="Number of shares outstanding")
    beta: float = Field(description="Beta coefficient (market volatility measure)")
    volume: float = Field(description="Trading volume (current period)")
    average_volume: float = Field(description="Average trading volume")
    week_52_high: float = Field(description="52-week high price")
    week_52_low: float = Field(description="52-week low price")
