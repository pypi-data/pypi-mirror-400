from typing import Optional


class ProviderError(Exception):
    """
    Base exception for provider-related errors.
    Raised when a provider fails to fetch data.
    
    Args:
        message: Error message describing the provider failure
        provider_name: Optional name of the provider that failed
        symbol: Optional symbol that was being fetched
    """
    def __init__(self, message: str, provider_name: Optional[str] = None, symbol: Optional[str] = None):
        self.message = message
        self.provider_name = provider_name
        self.symbol = symbol
        super().__init__(self.message)


class ProviderAPIError(ProviderError):
    """
    Exception raised when a provider API call fails (HTTP errors, network issues).
    
    Args:
        message: Error message describing the API failure
        status_code: Optional HTTP status code
        provider_name: Optional name of the provider
        symbol: Optional symbol that was being fetched
    """
    def __init__(self, message: str, status_code: Optional[int] = None, provider_name: Optional[str] = None, symbol: Optional[str] = None):
        self.status_code = status_code
        super().__init__(message, provider_name, symbol)


class ProviderAuthenticationError(ProviderError):
    """
    Exception raised when provider authentication fails (invalid API key, expired token).
    
    Args:
        message: Error message describing the authentication failure
        provider_name: Optional name of the provider
    """
    def __init__(self, message: str = "Provider authentication failed", provider_name: Optional[str] = None):
        super().__init__(message, provider_name)


class ProviderBadRequestError(ProviderAPIError):
    """
    Exception raised when a provider API returns 400 Bad Request (invalid parameters, malformed request).
    
    Args:
        message: Error message describing the bad request
        provider_name: Optional name of the provider
        symbol: Optional symbol that was being fetched
    """
    def __init__(self, message: str = "Bad request to provider API", provider_name: Optional[str] = None, symbol: Optional[str] = None):
        super().__init__(message, status_code=400, provider_name=provider_name, symbol=symbol)


class ProviderTimeoutError(ProviderError):
    """
    Exception raised when a provider request times out.
    
    Args:
        message: Error message describing the timeout
        provider_name: Optional name of the provider
        symbol: Optional symbol that was being fetched
    """
    def __init__(self, message: str = "Provider request timed out", provider_name: Optional[str] = None, symbol: Optional[str] = None):
        super().__init__(message, provider_name, symbol)

class ProviderSubscriptionError(ProviderAPIError):
    """
    Exception raised when a provider subscription fails (402 Payment Required).
    
    Args:
        message: Error message describing the subscription failure
        provider_name: Optional name of the provider
        symbol: Optional symbol that was being fetched
    """
    def __init__(self, message: str = "Provider subscription required (402 Payment Required)", provider_name: Optional[str] = None, symbol: Optional[str] = None):
        super().__init__(message, status_code=402, provider_name=provider_name, symbol=symbol)