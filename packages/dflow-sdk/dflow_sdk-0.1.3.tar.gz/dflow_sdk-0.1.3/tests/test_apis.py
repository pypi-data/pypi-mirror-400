"""Tests for API modules."""

import pytest
from pytest_httpx import HTTPXMock

from dflow import DFlowClient


class TestMarketsAPI:
    """Tests for MarketsAPI."""

    def test_get_market(self, httpx_mock: HTTPXMock, mock_market_data):
        """Test get_market method."""
        httpx_mock.add_response(
            url="https://dev-prediction-markets-api.dflow.net/api/v1/market/BTCD-25DEC0313-T92749.99",
            json=mock_market_data,
        )
        
        with DFlowClient() as client:
            market = client.markets.get_market("BTCD-25DEC0313-T92749.99")
            
            assert market.ticker == "BTCD-25DEC0313-T92749.99"
            assert market.yes_bid == "0.6500"
            assert market.yes_price == 0.65  # computed property
            assert market.status == "active"

    def test_get_markets(self, httpx_mock: HTTPXMock, mock_market_data):
        """Test get_markets method."""
        httpx_mock.add_response(
            url="https://dev-prediction-markets-api.dflow.net/api/v1/markets?status=active",
            json={"markets": [mock_market_data], "cursor": None},
        )
        
        with DFlowClient() as client:
            response = client.markets.get_markets(status="active")
            
            assert len(response.markets) == 1
            assert response.markets[0].ticker == "BTCD-25DEC0313-T92749.99"

    def test_get_markets_batch(self, httpx_mock: HTTPXMock, mock_market_data):
        """Test get_markets_batch method."""
        httpx_mock.add_response(
            url="https://dev-prediction-markets-api.dflow.net/api/v1/markets/batch",
            json={"markets": [mock_market_data]},
        )
        
        with DFlowClient() as client:
            markets = client.markets.get_markets_batch(
                tickers=["BTCD-25DEC0313-T92749.99"]
            )
            
            assert len(markets) == 1
            assert markets[0].ticker == "BTCD-25DEC0313-T92749.99"

    def test_get_markets_batch_exceeds_limit(self):
        """Test get_markets_batch raises error when exceeding limit."""
        with DFlowClient() as client:
            with pytest.raises(ValueError, match="exceeds maximum"):
                client.markets.get_markets_batch(
                    tickers=["t" + str(i) for i in range(101)]
                )


class TestEventsAPI:
    """Tests for EventsAPI."""

    def test_get_event(self, httpx_mock: HTTPXMock, mock_event_data):
        """Test get_event method."""
        httpx_mock.add_response(
            url="https://dev-prediction-markets-api.dflow.net/api/v1/event/BTCD-25DEC0313",
            json=mock_event_data,
        )
        
        with DFlowClient() as client:
            event = client.events.get_event("BTCD-25DEC0313")
            
            assert event.ticker == "BTCD-25DEC0313"
            assert event.series_ticker == "KXBTC"

    def test_get_events(self, httpx_mock: HTTPXMock, mock_event_data):
        """Test get_events method."""
        httpx_mock.add_response(
            url="https://dev-prediction-markets-api.dflow.net/api/v1/events?status=active",
            json={"events": [mock_event_data], "cursor": None},
        )
        
        with DFlowClient() as client:
            response = client.events.get_events(status="active")
            
            assert len(response.events) == 1
            assert response.events[0].ticker == "BTCD-25DEC0313"


class TestOrderbookAPI:
    """Tests for OrderbookAPI."""

    def test_get_orderbook(self, httpx_mock: HTTPXMock, mock_orderbook_data):
        """Test get_orderbook method."""
        httpx_mock.add_response(
            url="https://dev-prediction-markets-api.dflow.net/api/v1/orderbook/BTCD-25DEC0313-T92749.99",
            json=mock_orderbook_data,
        )
        
        with DFlowClient() as client:
            orderbook = client.orderbook.get_orderbook("BTCD-25DEC0313-T92749.99")
            
            assert orderbook.sequence == 1704067200000
            assert len(orderbook.yes_bids) == 2
            yes_levels = orderbook.get_yes_levels()
            assert yes_levels[0].price == 0.65


class TestTradesAPI:
    """Tests for TradesAPI."""

    def test_get_trades(self, httpx_mock: HTTPXMock, mock_trade_data):
        """Test get_trades method."""
        httpx_mock.add_response(
            url="https://dev-prediction-markets-api.dflow.net/api/v1/trades?marketTicker=BTCD-25DEC0313-T92749.99",
            json={"trades": [mock_trade_data], "cursor": None},
        )
        
        with DFlowClient() as client:
            response = client.trades.get_trades(
                market_ticker="BTCD-25DEC0313-T92749.99"
            )
            
            assert len(response.trades) == 1
            assert response.trades[0].side == "yes"  # backwards compat property
            assert response.trades[0].taker_side == "yes"
            assert response.trades[0].price == 65  # price in cents


class TestSwapAPI:
    """Tests for SwapAPI."""

    def test_get_quote(self, httpx_mock: HTTPXMock, mock_quote_data):
        """Test get_quote method."""
        httpx_mock.add_response(
            url="https://dev-quote-api.dflow.net/quote?inputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&outputMint=YesMint123&amount=1000000",
            json=mock_quote_data,
        )
        
        with DFlowClient() as client:
            quote = client.swap.get_quote(
                input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                output_mint="YesMint123",
                amount=1000000,
            )
            
            assert quote.in_amount == "1000000"
            assert quote.out_amount == "1538461"
            assert quote.price_impact_pct == 0.05


class TestSearchAPI:
    """Tests for SearchAPI."""

    def test_search(self, httpx_mock: HTTPXMock, mock_event_data):
        """Test search method."""
        httpx_mock.add_response(
            url="https://dev-prediction-markets-api.dflow.net/api/v1/search?q=bitcoin&limit=10",
            json={"events": [mock_event_data]},
        )
        
        with DFlowClient() as client:
            result = client.search.search("bitcoin", limit=10)
            
            assert len(result.events) == 1
            assert result.events[0].ticker == "BTCD-25DEC0313"
