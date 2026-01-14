"""Tests for DFlowClient."""

import pytest

from dflow import DFlowClient
from dflow.utils.constants import (
    METADATA_API_BASE_URL,
    PROD_METADATA_API_BASE_URL,
    PROD_TRADE_API_BASE_URL,
    TRADE_API_BASE_URL,
)


class TestDFlowClientInit:
    """Tests for DFlowClient initialization."""

    def test_default_development_environment(self):
        """Test client defaults to development environment."""
        client = DFlowClient()
        assert client._metadata_http.base_url == METADATA_API_BASE_URL + "/"
        assert client._trade_http.base_url == TRADE_API_BASE_URL + "/"
        client.close()

    def test_production_environment(self):
        """Test client with production environment."""
        client = DFlowClient(environment="production", api_key="test-key")
        assert client._metadata_http.base_url == PROD_METADATA_API_BASE_URL + "/"
        assert client._trade_http.base_url == PROD_TRADE_API_BASE_URL + "/"
        client.close()

    def test_custom_base_urls(self):
        """Test client with custom base URLs."""
        custom_metadata = "https://custom-metadata.example.com"
        custom_trade = "https://custom-trade.example.com"
        
        client = DFlowClient(
            metadata_base_url=custom_metadata,
            trade_base_url=custom_trade,
        )
        assert client._metadata_http.base_url == custom_metadata + "/"
        assert client._trade_http.base_url == custom_trade + "/"
        client.close()

    def test_api_modules_initialized(self):
        """Test all API modules are initialized."""
        client = DFlowClient()
        
        # Metadata APIs
        assert client.events is not None
        assert client.markets is not None
        assert client.orderbook is not None
        assert client.trades is not None
        assert client.live_data is not None
        assert client.series is not None
        assert client.tags is not None
        assert client.sports is not None
        assert client.search is not None
        
        # Trade APIs
        assert client.orders is not None
        assert client.swap is not None
        assert client.intent is not None
        assert client.prediction_market is not None
        assert client.tokens is not None
        assert client.venues is not None
        
        # WebSocket
        assert client.ws is not None
        
        client.close()

    def test_set_api_key(self):
        """Test setting API key after initialization."""
        client = DFlowClient()
        assert client._metadata_http.api_key is None
        
        client.set_api_key("new-api-key")
        assert client._metadata_http.api_key == "new-api-key"
        assert client._trade_http.api_key == "new-api-key"
        
        client.close()

    def test_context_manager(self):
        """Test client as context manager."""
        with DFlowClient() as client:
            assert client.markets is not None


class TestDFlowClientAPIs:
    """Tests for DFlowClient API access."""

    def test_markets_api_accessible(self):
        """Test markets API is accessible."""
        with DFlowClient() as client:
            # Just verify the API is accessible - don't make actual requests
            assert hasattr(client.markets, "get_market")
            assert hasattr(client.markets, "get_markets")
            assert hasattr(client.markets, "get_markets_batch")
            assert hasattr(client.markets, "filter_outcome_mints")

    def test_events_api_accessible(self):
        """Test events API is accessible."""
        with DFlowClient() as client:
            assert hasattr(client.events, "get_event")
            assert hasattr(client.events, "get_events")
            assert hasattr(client.events, "get_event_candlesticks")

    def test_swap_api_accessible(self):
        """Test swap API is accessible."""
        with DFlowClient() as client:
            assert hasattr(client.swap, "get_quote")
            assert hasattr(client.swap, "create_swap")
            assert hasattr(client.swap, "get_swap_instructions")

    def test_websocket_accessible(self):
        """Test WebSocket is accessible."""
        with DFlowClient() as client:
            assert hasattr(client.ws, "connect")
            assert hasattr(client.ws, "disconnect")
            assert hasattr(client.ws, "subscribe_prices")
            assert hasattr(client.ws, "on_price")
