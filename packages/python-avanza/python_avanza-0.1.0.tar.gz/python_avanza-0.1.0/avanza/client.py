"""
Main Avanza API client for handling requests
"""

import logging
import requests
from requests.adapters import HTTPAdapter
from typing import Any
from urllib3.util.retry import Retry

from .constants import Endpoints, InstrumentType, TimePeriod
from .exceptions import AvanzaAPIError, AvanzaNetworkError, AvanzaRateLimitError
from .utils import convert_instrument_type, convert_time_period

logger = logging.getLogger(__name__)


class AvanzaClient:
    """
    Client for interacting with Avanza's unofficial API
    No authentication required for public endpoints
    """

    def __init__(self, timeout: int = 10, max_retries: int = 3) -> None:
        """
        Initialize the Avanza client

        Args:
            timeout: Request timeout in seconds (default: 10)
            max_retries: Maximum number of retry attempts (default: 3)
        """
        self.timeout = timeout
        self.session = requests.Session()
        self._setup_headers()
        self._setup_retry(max_retries)
        logger.info(f"Initialized AvanzaClient (timeout={timeout}s, retries={max_retries})")

    def _setup_headers(self) -> None:
        """Set up default headers for requests"""
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",  # noqa: E501
                "Content-Type": "application/json",
            }
        )

    def _setup_retry(self, max_retries: int) -> None:
        """Configure retry strategy with exponential backoff"""
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,  # Wait 1s, 2s, 4s between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
            allowed_methods=["GET", "POST"],  # Retry safe methods
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _make_request(
        self, method: str, endpoint: str, data: dict | None = None, params: dict | None = None
    ) -> dict[str, Any]:
        """
        Make an API request

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            params: URL parameters

        Returns:
            Dict: Response data

        Raises:
            AvanzaNetworkError: If network request fails (timeout or connection error)
            AvanzaRateLimitError: If rate limit is exceeded (429)
            AvanzaAPIError: For other API errors (includes status_code and response)
        """
        url = f"{Endpoints.BASE_URL}{endpoint}"
        logger.debug(f"Making {method} request to {url}")

        try:
            response = self.session.request(
                method=method, url=url, json=data, params=params, timeout=self.timeout
            )
            response.raise_for_status()
            logger.debug(f"Request successful: {method} {url} - Status {response.status_code}")
            return response.json()
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timed out: {method} {url}")
            raise AvanzaNetworkError(f"Request timed out after {self.timeout} seconds") from e
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection failed: {method} {url} - {str(e)}")
            raise AvanzaNetworkError(str(e)) from e
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            try:
                response_data = e.response.json()
            except Exception:
                response_data = None

            logger.error(f"HTTP error: {method} {url} - Status {status_code}")

            if status_code == 429:
                raise AvanzaRateLimitError(response_data) from e
            else:
                raise AvanzaAPIError(f"HTTP {status_code}", status_code, response_data) from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {method} {url} - {str(e)}")
            raise AvanzaNetworkError(str(e)) from e

    def search(
        self, query: str, instrument_type: InstrumentType | str | None = None, limit: int = 10
    ) -> dict[str, Any]:
        """
        Search for instruments by type

        Args:
            query: Search query
            instrument_type: Type of instrument to search for (stock, fund, etf). If None, searches all types.
            limit: Maximum number of results

        Returns:
            Dict: Search results
        """
        search_types = []
        if instrument_type is not None:
            instrument_type = convert_instrument_type(instrument_type)

            # ETF needs to be mapped to EXCHANGE_TRADED_FUND for the search API
            search_type = (
                "EXCHANGE_TRADED_FUND"
                if instrument_type == InstrumentType.ETF
                else instrument_type.upper()
            )
            search_types = [search_type]

        data = {
            "query": query,
            "searchFilter": {"types": search_types},
            "pagination": {"from": 0, "size": limit},
        }
        return self._make_request("POST", Endpoints.SEARCH, data=data)

    def get_stock_info(self, orderbook_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific stock

        Args:
            orderbook_id: The orderbook identifier

        Returns:
            Dict: Stock information
        """
        return self._make_request(
            "GET",
            Endpoints.INSTRUMENT.format(
                instrument_type=InstrumentType.STOCK.value, orderbook_id=orderbook_id
            ),
        )

    def get_stock_details(self, orderbook_id: str) -> dict[str, Any]:
        """
        Get detailed information (including financials) about a specific stock

        Args:
            orderbook_id: The orderbook identifier

        Returns:
            Dict: Stock detailed information
        """
        return self._make_request(
            "GET",
            Endpoints.INSTRUMENT_DETAILS.format(
                instrument_type=InstrumentType.STOCK.value, orderbook_id=orderbook_id
            ),
        )

    def get_etf_info(self, orderbook_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific ETF

        Args:
            orderbook_id: The orderbook identifier

        Returns:
            Dict: ETF information
        """
        return self._make_request(
            "GET",
            Endpoints.ETF.format(orderbook_id=orderbook_id),
        )

    def get_etf_details(self, orderbook_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific ETF

        Args:
            orderbook_id: The orderbook identifier

        Returns:
            Dict: ETF details
        """
        return self._make_request(
            "GET",
            Endpoints.ETF_DETAILS.format(orderbook_id=orderbook_id),
        )

    def get_instrument_price(self, orderbook_id: str) -> dict[str, Any]:
        """
        Get current price for an instrument (stock or ETF)

        Args:
            orderbook_id: The orderbook identifier

        Returns:
            Dict: Price information
        """
        return self._make_request(
            "GET",
            Endpoints.INSTRUMENT_PRICE.format(
                instrument_type=InstrumentType.STOCK.value, orderbook_id=orderbook_id
            ),
        )

    def get_instrument_chart(
        self, orderbook_id: str, time_period: TimePeriod | str
    ) -> dict[str, Any]:
        """
        Get quote/chart information for an instrument (stock or ETF)

        Args:
            orderbook_id: The orderbook identifier
            time_period: Time period for the chart (e.g., 'one_month', TimePeriod.ONE_MONTH)

        Returns:
            Dict: Quote information with chart data
        """
        time_period = convert_time_period(time_period)
        return self._make_request(
            "GET",
            Endpoints.INSTRUMENT_CHART.format(
                instrument_type=InstrumentType.STOCK.value,
                orderbook_id=orderbook_id,
                time_period=time_period.value,
            ),
        )

    def get_instrument_dividend(
        self, orderbook_id: str, instrument_type: InstrumentType | str
    ) -> dict[str, Any]:
        """
        Get dividend information for a stock or ETF

        Args:
            orderbook_id: The orderbook identifier
            instrument_type: Type of instrument (stock or etf)

        Returns:
            Dict: Dividend information
        """
        instrument_type = convert_instrument_type(instrument_type)

        return self._make_request(
            "GET",
            Endpoints.INSTRUMENT_DIVIDENDS.format(
                instrument_type=instrument_type.value,
                orderbook_id=orderbook_id,
                time_period="infinity",
            ),
        )

    def get_fund_info(self, orderbook_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific fund

        Args:
            orderbook_id: The orderbook identifier

        Returns:
            Dict: Fund information
        """
        return self._make_request("GET", Endpoints.FUND.format(orderbook_id=orderbook_id))

    def get_fund_nav(self, orderbook_id: str) -> dict[str, Any]:
        """
        Get current price (NAV) for a fund

        Args:
            orderbook_id: The orderbook identifier

        Returns:
            Dict: Fund price information
        """
        return self._make_request(
            "GET",
            Endpoints.FUND_NAV.format(orderbook_id=orderbook_id),
        )

    def get_fund_chart(self, orderbook_id: str, time_period: TimePeriod | str) -> dict[str, Any]:
        """
        Get price chart data for a fund

        Args:
            orderbook_id: The orderbook identifier
            time_period: Time period for the chart (e.g., 'one_year', TimePeriod.ONE_YEAR)

        Returns:
            Dict: Fund chart data
        """
        time_period = convert_time_period(time_period)
        return self._make_request(
            "GET",
            Endpoints.FUND_CHART.format(orderbook_id=orderbook_id, time_period=time_period.value),
        )
