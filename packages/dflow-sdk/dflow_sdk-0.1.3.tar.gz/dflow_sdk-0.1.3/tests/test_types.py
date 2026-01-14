"""Tests for Pydantic type definitions."""

import pytest

from dflow.types.events import Event
from dflow.types.markets import Market, MarketAccount
from dflow.types.orderbook import Orderbook, OrderbookLevel
from dflow.types.orders import SwapQuote
from dflow.types.trades import Trade


class TestMarketTypes:
    """Tests for market-related types."""

    def test_market_account_parsing(self):
        """Test MarketAccount parsing with alias."""
        data = {
            "yesMint": "YesMint123",
            "noMint": "NoMint123",
            "marketLedger": "Ledger123",
            "redemptionStatus": "open",
            "scalarOutcomePct": 5000,
        }
        account = MarketAccount.model_validate(data)
        assert account.yes_mint == "YesMint123"
        assert account.no_mint == "NoMint123"
        assert account.market_ledger == "Ledger123"
        assert account.redemption_status == "open"
        assert account.scalar_outcome_pct == 5000

    def test_market_parsing(self, mock_market_data):
        """Test Market parsing with nested accounts."""
        market = Market.model_validate(mock_market_data)
        assert market.ticker == "BTCD-25DEC0313-T92749.99"
        assert market.title == "Bitcoin above $92,749.99?"
        assert market.event_ticker == "BTCD-25DEC0313"
        assert market.status == "active"
        assert market.result == ""
        assert market.yes_bid == "0.6500"
        assert market.no_bid == "0.3400"
        assert market.yes_price == 0.65  # computed from yes_bid
        assert market.no_price == 0.34   # computed from no_bid
        assert market.volume == 1000000
        assert "usdc" in market.accounts
        assert market.accounts["usdc"].yes_mint == "YesMint123456789abcdefghijklmnopqrstuvwxyz"

    def test_market_optional_fields(self):
        """Test Market with minimal required fields."""
        data = {
            "ticker": "TEST-MARKET",
            "title": "Test Market",
            "eventTicker": "TEST-EVENT",
            "status": "active",
            "result": "",
            "accounts": {},
        }
        market = Market.model_validate(data)
        assert market.ticker == "TEST-MARKET"
        assert market.yes_price is None
        assert market.volume is None

    def test_market_with_integer_timestamps(self):
        """Test Market parsing with integer timestamps (as returned by real API)."""
        data = {
            "ticker": "TEST-MARKET",
            "title": "Test Market",
            "eventTicker": "TEST-EVENT",
            "status": "active",
            "result": "",
            "accounts": {},
            "openTime": 1731524400,
            "closeTime": 1774969200,
            "expirationTime": 1774969200,
        }
        market = Market.model_validate(data)
        assert market.open_time == 1731524400
        assert market.close_time == 1774969200
        assert market.expiration_time == 1774969200

    def test_market_account_pending_status(self):
        """Test MarketAccount with 'pending' redemption status."""
        data = {
            "yesMint": "YesMint123",
            "noMint": "NoMint123",
            "marketLedger": "Ledger123",
            "redemptionStatus": "pending",
        }
        account = MarketAccount.model_validate(data)
        assert account.redemption_status == "pending"

    def test_market_account_null_status(self):
        """Test MarketAccount with null redemption status."""
        data = {
            "yesMint": "YesMint123",
            "noMint": "NoMint123",
            "marketLedger": "Ledger123",
            "redemptionStatus": None,
        }
        account = MarketAccount.model_validate(data)
        assert account.redemption_status is None


class TestEventTypes:
    """Tests for event-related types."""

    def test_event_parsing(self, mock_event_data):
        """Test Event parsing."""
        event = Event.model_validate(mock_event_data)
        assert event.ticker == "BTCD-25DEC0313"
        assert event.title == "Bitcoin Price on December 31, 2025"
        assert event.series_ticker == "KXBTC"
        assert event.category == "crypto"
        assert event.mutually_exclusive is True

    def test_event_with_markets(self, mock_event_data, mock_market_data):
        """Test Event with nested markets."""
        mock_event_data["markets"] = [mock_market_data]
        event = Event.model_validate(mock_event_data)
        assert event.markets is not None
        assert len(event.markets) == 1
        assert event.markets[0].ticker == "BTCD-25DEC0313-T92749.99"


class TestOrderbookTypes:
    """Tests for orderbook types."""

    def test_orderbook_level(self):
        """Test OrderbookLevel parsing."""
        level = OrderbookLevel(price=0.65, quantity=1000)
        assert level.price == 0.65
        assert level.quantity == 1000

    def test_orderbook_parsing(self, mock_orderbook_data):
        """Test Orderbook parsing (new API format)."""
        orderbook = Orderbook.model_validate(mock_orderbook_data)
        assert orderbook.sequence == 1704067200000
        assert orderbook.timestamp == 1704067200000  # backwards compat
        assert len(orderbook.yes_bids) == 2
        assert len(orderbook.no_bids) == 2
        # Test the helper methods
        yes_levels = orderbook.get_yes_levels()
        assert len(yes_levels) == 2
        assert yes_levels[0].price == 0.65  # sorted descending
        assert yes_levels[0].quantity == 1000


class TestTradeTypes:
    """Tests for trade types."""

    def test_trade_parsing(self, mock_trade_data):
        """Test Trade parsing (new API format)."""
        trade = Trade.model_validate(mock_trade_data)
        assert trade.trade_id == "trade-123"
        assert trade.ticker == "BTCD-25DEC0313-T92749.99"
        assert trade.taker_side == "yes"
        assert trade.price == 65
        assert trade.count == 100
        # Test backwards-compatible properties
        assert trade.id == "trade-123"
        assert trade.market_ticker == "BTCD-25DEC0313-T92749.99"
        assert trade.side == "yes"
        assert trade.quantity == 100


class TestSwapTypes:
    """Tests for swap types."""

    def test_swap_quote_parsing(self, mock_quote_data):
        """Test SwapQuote parsing."""
        quote = SwapQuote.model_validate(mock_quote_data)
        assert quote.input_mint == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        assert quote.output_mint == "YesMint123456789abcdefghijklmnopqrstuvwxyz"
        assert quote.in_amount == "1000000"
        assert quote.out_amount == "1538461"
        assert quote.price_impact_pct == 0.05
