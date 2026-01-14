class RateLimitExceeded(Exception):
    """
    Exception raised when rate limit is exceeded (429 Too Many Requests).
    """
    def __init__(self, message: str = "too many requests"):
        self.message = message
        self.status_code = 429
        super().__init__(self.message)

