"""
StockLib - Stock Fundamentals Analysis Library

A Python library for fetching and analyzing stock fundamentals data
from multiple providers with rate limiting, caching, and normalization.
"""

from stocklib.client import StockClient
from stocklib.models.fundamentals import Fundamentals

__version__ = "0.1.0"
__all__ = ["StockClient", "Fundamentals"]

