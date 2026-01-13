"""
Custom exceptions for Avanza API client
"""

from typing import Any


class AvanzaError(Exception):
    """Base exception for all Avanza API errors"""

    pass


class AvanzaAPIError(AvanzaError):
    """Exception raised when API returns an error response"""

    def __init__(self, message: str, status_code: int, response: dict[str, Any] | None = None):
        self.status_code = status_code
        self.response = response
        super().__init__(f"{message} (status code: {status_code})")


class AvanzaRateLimitError(AvanzaAPIError):
    """Exception raised when rate limit is exceeded (429)"""

    def __init__(self, response: dict[str, Any] | None = None):
        super().__init__("Rate limit exceeded", 429, response)


class AvanzaNetworkError(AvanzaError):
    """Exception raised when network request fails (timeout or connection error)"""

    def __init__(self, message: str):
        super().__init__(f"Network error: {message}")
