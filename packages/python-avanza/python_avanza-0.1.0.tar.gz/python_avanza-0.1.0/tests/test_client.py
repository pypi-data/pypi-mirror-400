"""
Unit tests for Avanza client
"""

import pytest
from unittest.mock import Mock, patch
import requests
from avanza.client import AvanzaClient
from avanza.exceptions import AvanzaAPIError, AvanzaRateLimitError, AvanzaNetworkError


class TestAvanzaClient:
    """Test cases for AvanzaClient"""

    @patch("avanza.client.requests.Session.request")
    def test_make_request_success(self, mock_request):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        client = AvanzaClient()
        result = client._make_request("GET", "/test")

        assert result == {"data": "test"}
        mock_request.assert_called_once()

    @patch("avanza.client.requests.Session.request")
    def test_make_request_timeout(self, mock_request):
        """Test request timeout"""
        mock_request.side_effect = requests.exceptions.Timeout()

        client = AvanzaClient()
        with pytest.raises(AvanzaNetworkError, match="timed out"):
            client._make_request("GET", "/test")

    @patch("avanza.client.requests.Session.request")
    def test_make_request_rate_limit(self, mock_request):
        """Test rate limit error (429)"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_request.side_effect = http_error

        client = AvanzaClient()
        with pytest.raises(AvanzaRateLimitError):
            client._make_request("GET", "/test")

    @patch("avanza.client.requests.Session.request")
    def test_make_request_http_error(self, mock_request):
        """Test HTTP error (404, 500, etc.)"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not found"}
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_request.side_effect = http_error

        client = AvanzaClient()
        with pytest.raises(AvanzaAPIError):
            client._make_request("GET", "/test")

    @patch("avanza.client.requests.Session.request")
    def test_search(self, mock_request):
        """Test search method"""
        mock_response = Mock()
        mock_response.json.return_value = {"hits": [{"name": "Test"}]}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        client = AvanzaClient()
        result = client.search("test", "stock", 5)

        assert "hits" in result
        mock_request.assert_called_once()
