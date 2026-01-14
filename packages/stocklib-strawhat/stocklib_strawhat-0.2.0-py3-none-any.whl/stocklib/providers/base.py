from abc import ABC, abstractmethod
from stocklib.models.fundamentals import Fundamentals
from stocklib.models.market import MarketData
from stocklib.models.financials import Financials
from typing import List

class BaseProvider(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @abstractmethod
    async def get_stocks(self, symbol: str, currency: str = "USD", exchange: str = "NASDAQ") -> List[dict]:
        pass

    @abstractmethod
    async def get_fundamentals(self, symbol: str) -> Fundamentals:
        pass

    @abstractmethod
    async def get_market_data(self, symbol: str) -> MarketData:
        pass

    @abstractmethod
    async def get_financials(self, symbol: str) -> Financials:
        pass
