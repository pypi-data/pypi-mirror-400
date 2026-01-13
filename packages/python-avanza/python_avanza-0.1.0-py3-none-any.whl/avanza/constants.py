"""
Constants for Avanza API
"""

from enum import Enum


class InstrumentType(str, Enum):
    """Instrument types available on Avanza"""

    STOCK = "stock"
    ETF = "etf"
    FUND = "fund"


class TimePeriod(str, Enum):
    """Time periods for price charts"""

    TODAY = "today"
    ONE_WEEK = "one_week"
    ONE_MONTH = "one_month"
    THREE_MONTHS = "three_months"
    SIX_MONTHS = "six_months"
    THIS_YEAR = "this_year"
    ONE_YEAR = "one_year"
    THREE_YEARS = "three_years"
    FIVE_YEARS = "five_years"
    TEN_YEARS = "ten_years"
    MAX = "infinity"
    THREE_YEARS_ROLLING = "three_years_rolling"
    FIVE_YEARS_ROLLING = "five_years_rolling"


class Endpoints:
    """API endpoint paths

    ETF endpoints reuse INSTRUMENT endpoints with specific instrument_type values:
    - ETF price/chart: use INSTRUMENT_PRICE/INSTRUMENT_CHART with instrument_type="stock"
    - ETF dividends: use INSTRUMENT_DIVIDENDS with instrument_type="etf"

    Note: Avanza doesn't provide dividend payment history for funds.
    """

    BASE_URL = "https://www.avanza.se/_api"
    SEARCH = "/search/filtered-search"
    INSTRUMENT = "/market-guide/{instrument_type}/{orderbook_id}"
    INSTRUMENT_DETAILS = "/market-guide/{instrument_type}/{orderbook_id}/details"
    INSTRUMENT_PRICE = "/market-guide/{instrument_type}/{orderbook_id}/quote"
    INSTRUMENT_CHART = (
        "/price-chart/{instrument_type}/{orderbook_id}?timePeriod={time_period}&resolution=day"
    )
    INSTRUMENT_CHART_CUSTOM = "/price-chart/{instrument_type}/{orderbook_id}?from={from_date}&to={to_date}&resolution=day"  # noqa: E501
    INSTRUMENT_DIVIDENDS = (
        "/price-chart/{instrument_type}/{orderbook_id}/dividends?timePeriod={time_period}"
    )
    ETF = "/market-etf/{orderbook_id}"
    ETF_DETAILS = "/market-etf/{orderbook_id}/details"
    FUND = "/fund-guide/guide/{orderbook_id}"
    FUND_NAV = "/fund-reference/reference/{orderbook_id}"
    FUND_CHART = "/fund-guide/chart/{orderbook_id}/{time_period}?raw=true"
