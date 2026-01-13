"""
Avanza API Client Package
A Python package for interacting with Avanza's unofficial APIs
"""

__version__ = "0.1.0"

from .client import AvanzaClient
from .ticker import Stock, ETF, Fund, search
from .constants import TimePeriod, InstrumentType
from .exceptions import (
    AvanzaAPIError,
    AvanzaError,
    AvanzaNetworkError,
    AvanzaRateLimitError,
)

__all__ = [
    "AvanzaClient",
    "Stock",
    "ETF",
    "Fund",
    "search",
    "TimePeriod",
    "InstrumentType",
    "AvanzaError",
    "AvanzaAPIError",
    "AvanzaRateLimitError",
    "AvanzaNetworkError",
]
