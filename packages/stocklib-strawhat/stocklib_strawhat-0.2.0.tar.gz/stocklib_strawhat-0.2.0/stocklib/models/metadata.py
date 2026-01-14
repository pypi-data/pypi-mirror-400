from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Metadata(BaseModel):
    provider_name: str = Field(description="Name of the data provider (e.g., 'fmp', 'alpha_vantage', 'yahoo')")
    provider_version: Optional[str] = Field(default=None, description="Provider API version")
    fetched_at: datetime = Field(description="Timestamp when data was fetched")
    cache_hit: bool = Field(description="Whether the data was retrieved from cache")
    cache_ttl_seconds: int = Field(description="Cache time-to-live in seconds")
    data_confidence_score: Optional[float] = Field(default=None, description="Data quality/confidence score (0.0-1.0)")
