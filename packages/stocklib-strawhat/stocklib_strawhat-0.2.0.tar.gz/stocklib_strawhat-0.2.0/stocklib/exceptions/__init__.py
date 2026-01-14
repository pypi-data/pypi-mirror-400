"""
Exception classes for stocklib.

This module exports all custom exceptions used throughout the library.
"""

from stocklib.exceptions.data import (
    DataError,
    DataValidationError,
    IncompleteDataError,
    DataParsingError,
)
from stocklib.exceptions.provider import (
    ProviderError,
    ProviderAPIError,
    ProviderAuthenticationError,
    ProviderBadRequestError,
    ProviderSubscriptionError,
    ProviderTimeoutError,
)
from stocklib.exceptions.rate_limit import RateLimitExceeded

__all__ = [
    # Data exceptions
    "DataError",
    "DataValidationError",
    "IncompleteDataError",
    "DataParsingError",
    # Provider exceptions
    "ProviderError",
    "ProviderAPIError",
    "ProviderAuthenticationError",
    "ProviderBadRequestError",
    "ProviderSubscriptionError",
    "ProviderTimeoutError",
    # Rate limit exceptions
    "RateLimitExceeded",
]

