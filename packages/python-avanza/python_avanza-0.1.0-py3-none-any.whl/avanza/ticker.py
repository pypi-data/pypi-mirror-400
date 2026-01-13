"""
Ticker classes for yfinance-style interface
"""

import pandas as pd
from time import time
from typing import Any
from .client import AvanzaClient
from .constants import TimePeriod
from .utils import InfoDict


def search(query: str, instrument_type: str = "stock", limit: int = 10) -> dict[str, Any]:
    """
    Search for instruments

    Args:
        query: Search query
        instrument_type: Type of instrument ("stock", "etf", or "fund")
        limit: Maximum number of results

    Returns:
        Search results
    """
    client = AvanzaClient()
    return client.search(query, instrument_type, limit)


class _BaseTicker:
    """Base class for ticker objects with common caching functionality"""

    def __init__(self, orderbook_id: str, cache_ttl: int = 60):
        """
        Initialize ticker

        Args:
            orderbook_id: The orderbook identifier
            cache_ttl: Cache time-to-live in seconds (default: 60). Set to 0 to disable caching.

        Raises:
            ValueError: If orderbook_id is invalid
        """
        self._validate_orderbook_id(orderbook_id)
        self.orderbook_id = orderbook_id
        self._client = AvanzaClient()
        self._cache_ttl = cache_ttl
        self._info = None
        self._info_timestamp = 0.0
        self._price_data = None
        self._price_timestamp = 0.0

    @staticmethod
    def _validate_orderbook_id(orderbook_id: str) -> None:
        """
        Validate orderbook ID format

        Args:
            orderbook_id: The orderbook identifier to validate

        Raises:
            ValueError: If orderbook_id is invalid
        """
        if not orderbook_id:
            raise ValueError("orderbook_id cannot be empty")
        if not isinstance(orderbook_id, str):
            raise ValueError(f"orderbook_id must be a string, got {type(orderbook_id).__name__}")
        if not orderbook_id.isdigit():
            raise ValueError(f"orderbook_id must contain only digits, got '{orderbook_id}'")

    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cached data is still valid"""
        if self._cache_ttl == 0:
            return False
        return (time() - timestamp) < self._cache_ttl

    def refresh(self) -> None:
        """Clear cached data to force fresh API calls on next access"""
        self._info = None
        self._info_timestamp = 0.0
        self._price_data = None
        self._price_timestamp = 0.0


class Instrument(_BaseTicker):
    """
    Generic instrument ticker object for stocks and ETFs

    Usage:
        instrument = Instrument("5479", "stock")
        # Or use convenient aliases:
        stock = Stock("5479")
        etf = ETF("1063549")
    """

    def __init__(self, orderbook_id: str, instrument_type: str = "stock", cache_ttl: int = 60):
        """
        Initialize instrument ticker

        Args:
            orderbook_id: The orderbook identifier
            instrument_type: Type of instrument ("stock" or "etf")
            cache_ttl: Cache time-to-live in seconds (default: 60)

        Raises:
            ValueError: If orderbook_id is invalid or instrument_type is not supported
        """
        super().__init__(orderbook_id, cache_ttl)
        if instrument_type not in ("stock", "etf"):
            raise ValueError(f"instrument_type must be 'stock' or 'etf', got '{instrument_type}'")
        self.instrument_type = instrument_type
        self._details = None
        self._details_timestamp = 0.0

    @property
    def info(self) -> InfoDict:
        """Get detailed instrument information"""
        if self._info is None or not self._is_cache_valid(self._info_timestamp):
            if self.instrument_type == "stock":
                data = self._client.get_stock_info(self.orderbook_id)
            else:  # etf
                data = self._client.get_etf_info(self.orderbook_id)
            self._info = InfoDict(data)
            self._info_timestamp = time()
        return self._info

    @property
    def price(self) -> float:
        """Get current instrument price"""
        if self._price_data is None or not self._is_cache_valid(self._price_timestamp):
            data = self._client.get_instrument_price(self.orderbook_id)
            self._price_data = data.get("last", 0)
            self._price_timestamp = time()
        return self._price_data

    def history(self, period: TimePeriod | str = "one_month") -> pd.DataFrame:
        """
        Get historical price data as a DataFrame

        Args:
            period: Time period (e.g., "one_month", "one_year", or TimePeriod enum)

        Returns:
            DataFrame with columns: Open, High, Low, Close, Volume
            Index: DatetimeIndex
        """
        data = self._client.get_instrument_chart(self.orderbook_id, period)
        ohlc = data.get("ohlc", [])

        if not ohlc:
            return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

        df = pd.DataFrame(ohlc)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.rename(
            columns={
                "timestamp": "Date",
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "totalVolumeTraded": "Volume",
            }
        )
        df = df.set_index("Date")[["Open", "High", "Low", "Close", "Volume"]]
        return df

    @property
    def dividend(self) -> pd.DataFrame:
        """
        Get dividend information as a DataFrame

        Returns:
            DataFrame with columns: Amount, Currency, Type
            Index: DatetimeIndex
        """
        data = self._client.get_instrument_dividend(self.orderbook_id, self.instrument_type)

        # Handle different response formats
        dividends = data if isinstance(data, list) else data.get("dividends", [])

        if not dividends:
            return pd.DataFrame(columns=["Amount", "Currency", "Type"])

        df = pd.DataFrame(dividends)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.rename(
            columns={
                "timestamp": "Date",
                "amount": "Amount",
                "currencyCode": "Currency",
                "dividendType": "Type",
            }
        )
        df = df.set_index("Date")[["Amount", "Currency", "Type"]]
        return df

    def _get_details(self) -> dict:
        """Get instrument details with caching"""
        if self._details is None or not self._is_cache_valid(self._details_timestamp):
            if self.instrument_type == "stock":
                self._details = self._client.get_stock_details(self.orderbook_id)
            else:  # etf
                self._details = self._client.get_etf_details(self.orderbook_id)
            self._details_timestamp = time()
        return self._details

    def __getattr__(self, name: str) -> Any:
        """
        Dynamically access any key from instrument details as an attribute

        Examples:
            stock.stock -> stock details
            stock.company -> company information
            stock.companyEvents -> company events
            etf.category -> ETF category
            ... and any other keys from get_stock_details() or get_etf_details()
        """
        # Avoid infinite recursion for internal attributes
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        details = self._get_details()
        if name in details:
            value = details[name]
            # Wrap dict values in InfoDict for dot notation access
            return InfoDict(value) if isinstance(value, dict) else value

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def refresh(self) -> None:
        """Clear cached data to force fresh API calls on next access"""
        super().refresh()
        self._details = None
        self._details_timestamp = 0.0

    def __repr__(self):
        return f"Instrument(orderbook_id='{self.orderbook_id}', type='{self.instrument_type}')"


class Stock(Instrument):
    """
    Stock ticker object for convenient access to stock data

    Usage:
        stock = Stock("5479")
        print(stock.info)
        print(stock.price)
        print(stock.history("one_month"))
        print(stock.stock)
        print(stock.company)
        print(stock.companyEvents)
    """

    def __init__(self, orderbook_id: str, cache_ttl: int = 60):
        """
        Initialize stock ticker

        Args:
            orderbook_id: The orderbook identifier
            cache_ttl: Cache time-to-live in seconds (default: 60)
        """
        super().__init__(orderbook_id, "stock", cache_ttl)

    def __repr__(self):
        return f"Stock(orderbook_id='{self.orderbook_id}')"


class ETF(Instrument):
    """
    ETF ticker object for convenient access to ETF data

    Usage:
        etf = ETF("1063549")
        print(etf.info)
        print(etf.price)
        print(etf.history("one_year"))
    """

    def __init__(self, orderbook_id: str, cache_ttl: int = 60):
        """
        Initialize ETF ticker

        Args:
            orderbook_id: The orderbook identifier
            cache_ttl: Cache time-to-live in seconds (default: 60)
        """
        super().__init__(orderbook_id, "etf", cache_ttl)

    def __repr__(self) -> str:
        return f"ETF(orderbook_id='{self.orderbook_id}')"


class Fund(_BaseTicker):
    """
    Fund ticker object for convenient access to fund data

    Usage:
        fund = Fund("41567")
        print(fund.info)
        print(fund.price)
        print(fund.history("one_year"))
    """

    @property
    def info(self) -> InfoDict:
        """Get detailed fund information"""
        if self._info is None or not self._is_cache_valid(self._info_timestamp):
            data = self._client.get_fund_info(self.orderbook_id)
            self._info = InfoDict(data)
            self._info_timestamp = time()
        return self._info

    @property
    def price(self) -> float:
        """Get current fund NAV (price)"""
        if self._price_data is None or not self._is_cache_valid(self._price_timestamp):
            data = self._client.get_fund_nav(self.orderbook_id)
            self._price_data = data.get("nav", 0)
            self._price_timestamp = time()
        return self._price_data

    def history(self, period: TimePeriod | str = "one_month") -> pd.DataFrame:
        """
        Get historical NAV data as a DataFrame

        Args:
            period: Time period (e.g., "one_month", "one_year", or TimePeriod enum)

        Returns:
            DataFrame with columns: NAV
            Index: DatetimeIndex
        """
        data = self._client.get_fund_chart(self.orderbook_id, period)
        nav_data = data.get("dataSerie", [])

        if not nav_data:
            return pd.DataFrame(columns=["NAV"])

        df = pd.DataFrame(nav_data)
        df["x"] = pd.to_datetime(df["x"], unit="ms")
        df = df.rename(columns={"x": "Date", "y": "NAV"})
        df = df.set_index("Date")[["NAV"]]
        # Drop rows where NAV is None/null
        df = df.dropna()
        return df

    def __repr__(self) -> str:
        return f"Fund(orderbook_id='{self.orderbook_id}')"
