"""
Unit tests for ticker classes
"""

import pytest
from unittest.mock import Mock, patch
from avanza.ticker import Stock, ETF, Fund, search
from avanza.utils import InfoDict


class TestTickerValidation:
    """Test ticker input validation"""

    def test_valid_orderbook_id(self):
        """Test valid orderbook ID"""
        stock = Stock("5361")
        assert stock.orderbook_id == "5361"

    def test_empty_orderbook_id(self):
        """Test empty orderbook ID raises ValueError"""
        with pytest.raises(ValueError, match="cannot be empty"):
            Stock("")

    def test_non_digit_orderbook_id(self):
        """Test non-digit orderbook ID raises ValueError"""
        with pytest.raises(ValueError, match="must contain only digits"):
            Stock("abc123")

    def test_non_string_orderbook_id(self):
        """Test non-string orderbook ID raises ValueError"""
        with pytest.raises(ValueError, match="must be a string"):
            Stock(12345)


class TestStockTicker:
    """Test Stock ticker class"""

    @patch("avanza.ticker.AvanzaClient")
    def test_stock_info(self, mock_client_class):
        """Test stock info property"""
        mock_client = Mock()
        mock_client.get_stock_info.return_value = {"name": "Test Stock", "currency": "SEK"}
        mock_client_class.return_value = mock_client

        stock = Stock("5361")
        info = stock.info

        assert isinstance(info, InfoDict)
        assert info["name"] == "Test Stock"
        assert info.name == "Test Stock"  # Test attribute access
        mock_client.get_stock_info.assert_called_once_with("5361")

    @patch("avanza.ticker.AvanzaClient")
    def test_stock_price(self, mock_client_class):
        """Test stock price property"""
        mock_client = Mock()
        mock_client.get_instrument_price.return_value = {"last": 125.50}
        mock_client_class.return_value = mock_client

        stock = Stock("5361")
        price = stock.price

        assert price == 125.50
        mock_client.get_instrument_price.assert_called_once_with("5361")

    @patch("avanza.ticker.AvanzaClient")
    def test_stock_history(self, mock_client_class):
        """Test stock history method"""
        mock_client = Mock()
        mock_client.get_instrument_chart.return_value = {
            "ohlc": [
                {
                    "timestamp": 1704326400000,
                    "open": 100,
                    "high": 105,
                    "low": 99,
                    "close": 103,
                    "totalVolumeTraded": 1000,
                }
            ]
        }
        mock_client_class.return_value = mock_client

        stock = Stock("5361")
        df = stock.history("one_week")

        assert len(df) == 1
        assert "Close" in df.columns
        mock_client.get_instrument_chart.assert_called_once()

    @patch("avanza.ticker.AvanzaClient")
    def test_stock_dividend(self, mock_client_class):
        """Test stock dividend property"""
        mock_client = Mock()
        mock_client.get_instrument_dividend.return_value = {
            "dividends": [
                {
                    "timestamp": 1704326400000,
                    "amount": 5.0,
                    "currencyCode": "SEK",
                    "dividendType": "ORDINARY",
                }
            ]
        }
        mock_client_class.return_value = mock_client

        stock = Stock("5361")
        df = stock.dividend

        assert len(df) == 1
        assert "Amount" in df.columns
        assert "Currency" in df.columns
        assert "Type" in df.columns
        mock_client.get_instrument_dividend.assert_called_once()

    @patch("avanza.ticker.AvanzaClient")
    def test_stock_caching(self, mock_client_class):
        """Test that info is cached"""
        mock_client = Mock()
        mock_client.get_stock_info.return_value = {"name": "Test"}
        mock_client_class.return_value = mock_client

        stock = Stock("5361", cache_ttl=60)
        _ = stock.info
        _ = stock.info  # Second call should use cache

        # Should only call API once due to caching
        assert mock_client.get_stock_info.call_count == 1

    @patch("avanza.ticker.AvanzaClient")
    def test_stock_refresh(self, mock_client_class):
        """Test refresh clears cache"""
        mock_client = Mock()
        mock_client.get_stock_info.return_value = {"name": "Test"}
        mock_client_class.return_value = mock_client

        stock = Stock("5361")
        _ = stock.info
        stock.refresh()
        _ = stock.info  # Should fetch again after refresh

        assert mock_client.get_stock_info.call_count == 2


class TestETFTicker:
    """Test ETF ticker class"""

    @patch("avanza.ticker.AvanzaClient")
    def test_etf_initialization(self, mock_client_class):
        """Test ETF initialization"""
        etf = ETF("1063549")
        assert etf.orderbook_id == "1063549"
        assert etf.instrument_type == "etf"


class TestFundTicker:
    """Test Fund ticker class"""

    @patch("avanza.ticker.AvanzaClient")
    def test_fund_info(self, mock_client_class):
        """Test fund info property"""
        mock_client = Mock()
        mock_client.get_fund_info.return_value = {"name": "Test Fund", "nav": 150.75}
        mock_client_class.return_value = mock_client

        fund = Fund("41567")
        info = fund.info

        assert isinstance(info, InfoDict)
        assert info["name"] == "Test Fund"
        mock_client.get_fund_info.assert_called_once_with("41567")

    @patch("avanza.ticker.AvanzaClient")
    def test_fund_price(self, mock_client_class):
        """Test fund NAV (price) property"""
        mock_client = Mock()
        mock_client.get_fund_nav.return_value = {"nav": 150.75}
        mock_client_class.return_value = mock_client

        fund = Fund("41567")
        price = fund.price

        assert price == 150.75
        mock_client.get_fund_nav.assert_called_once_with("41567")

    @patch("avanza.ticker.AvanzaClient")
    def test_fund_history(self, mock_client_class):
        """Test fund history method"""
        mock_client = Mock()
        mock_client.get_fund_chart.return_value = {"dataSerie": [{"x": 1704326400000, "y": 150.5}]}
        mock_client_class.return_value = mock_client

        fund = Fund("41567")
        df = fund.history("one_week")

        assert len(df) == 1
        assert "NAV" in df.columns


class TestSearchFunction:
    """Test standalone search function"""

    @patch("avanza.ticker.AvanzaClient")
    def test_search(self, mock_client_class):
        """Test search function"""
        mock_client = Mock()
        mock_client.search.return_value = {"hits": [{"name": "Test"}]}
        mock_client_class.return_value = mock_client

        result = search("test", "stock", 5)

        assert result == {"hits": [{"name": "Test"}]}
        mock_client.search.assert_called_once_with("test", "stock", 5)
