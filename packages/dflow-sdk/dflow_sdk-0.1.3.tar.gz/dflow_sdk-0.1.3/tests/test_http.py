"""Tests for HTTP client."""

import pytest
from pytest_httpx import HTTPXMock

from dflow.utils.http import DFlowApiError, HttpClient


class TestHttpClient:
    """Tests for HttpClient."""

    def test_init_adds_trailing_slash(self):
        """Test that base URL gets trailing slash."""
        client = HttpClient("https://api.example.com")
        assert client.base_url == "https://api.example.com/"
        client.close()

    def test_init_preserves_trailing_slash(self):
        """Test that existing trailing slash is preserved."""
        client = HttpClient("https://api.example.com/")
        assert client.base_url == "https://api.example.com/"
        client.close()

    def test_get_request(self, httpx_mock: HTTPXMock):
        """Test GET request."""
        httpx_mock.add_response(
            url="https://api.example.com/markets",
            json={"markets": []},
        )
        
        client = HttpClient("https://api.example.com")
        result = client.get("/markets")
        
        assert result == {"markets": []}
        client.close()

    def test_get_request_with_params(self, httpx_mock: HTTPXMock):
        """Test GET request with query parameters."""
        httpx_mock.add_response(
            url="https://api.example.com/markets?status=active&limit=10",
            json={"markets": []},
        )
        
        client = HttpClient("https://api.example.com")
        result = client.get("/markets", {"status": "active", "limit": 10})
        
        assert result == {"markets": []}
        client.close()

    def test_get_request_filters_none_params(self, httpx_mock: HTTPXMock):
        """Test GET request filters out None parameters."""
        httpx_mock.add_response(
            url="https://api.example.com/markets?status=active",
            json={"markets": []},
        )
        
        client = HttpClient("https://api.example.com")
        result = client.get("/markets", {"status": "active", "cursor": None})
        
        assert result == {"markets": []}
        client.close()

    def test_post_request(self, httpx_mock: HTTPXMock):
        """Test POST request."""
        httpx_mock.add_response(
            url="https://api.example.com/swap",
            json={"transaction": "base64..."},
        )
        
        client = HttpClient("https://api.example.com")
        result = client.post("/swap", {"amount": 1000000})
        
        assert result == {"transaction": "base64..."}
        client.close()

    def test_api_key_header(self, httpx_mock: HTTPXMock):
        """Test API key is included in headers."""
        httpx_mock.add_response(
            url="https://api.example.com/markets",
            json={"markets": []},
        )
        
        client = HttpClient("https://api.example.com", api_key="test-api-key")
        client.get("/markets")
        
        request = httpx_mock.get_request()
        assert request.headers["x-api-key"] == "test-api-key"
        client.close()

    def test_error_response_raises_exception(self, httpx_mock: HTTPXMock):
        """Test error response raises DFlowApiError."""
        httpx_mock.add_response(
            url="https://api.example.com/markets",
            status_code=404,
            json={"error": "Not found"},
        )
        
        client = HttpClient("https://api.example.com")
        
        with pytest.raises(DFlowApiError) as exc_info:
            client.get("/markets")
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.response == {"error": "Not found"}
        client.close()

    def test_rate_limit_error(self, httpx_mock: HTTPXMock):
        """Test rate limit error."""
        httpx_mock.add_response(
            url="https://api.example.com/markets",
            status_code=429,
            json={"error": "Rate limit exceeded"},
        )
        
        client = HttpClient("https://api.example.com")
        
        with pytest.raises(DFlowApiError) as exc_info:
            client.get("/markets")
        
        assert exc_info.value.status_code == 429
        client.close()

    def test_set_api_key(self):
        """Test setting API key after initialization."""
        client = HttpClient("https://api.example.com")
        assert client.api_key is None
        
        client.set_api_key("new-key")
        assert client.api_key == "new-key"
        client.close()


class TestDFlowApiError:
    """Tests for DFlowApiError."""

    def test_error_message(self):
        """Test error message."""
        error = DFlowApiError("HTTP 404: Not Found", 404, {"error": "Not found"})
        assert str(error) == "HTTP 404: Not Found"
        assert error.status_code == 404
        assert error.response == {"error": "Not found"}

    def test_error_without_response(self):
        """Test error without response body."""
        error = DFlowApiError("HTTP 500: Internal Server Error", 500)
        assert str(error) == "HTTP 500: Internal Server Error"
        assert error.status_code == 500
        assert error.response is None
