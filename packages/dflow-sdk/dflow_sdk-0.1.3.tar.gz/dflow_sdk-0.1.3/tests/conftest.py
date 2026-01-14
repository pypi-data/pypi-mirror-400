"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def mock_market_data():
    """Sample market data for testing (matches actual API format)."""
    return {
        "ticker": "BTCD-25DEC0313-T92749.99",
        "title": "Bitcoin above $92,749.99?",
        "subtitle": "Will Bitcoin be above $92,749.99 on December 31, 2025?",
        "eventTicker": "BTCD-25DEC0313",
        "marketType": "binary",
        "status": "active",
        "result": "",
        "yesBid": "0.6500",
        "yesAsk": "0.6600",
        "noBid": "0.3400",
        "noAsk": "0.3500",
        "volume": 1000000,
        "volume24h": 50000,
        "openInterest": 250000,
        "liquidity": 100000,
        "openTime": 1704067200,
        "closeTime": 1735689600,
        "expirationTime": 1735689600,
        "accounts": {
            "usdc": {
                "yesMint": "YesMint123456789abcdefghijklmnopqrstuvwxyz",
                "noMint": "NoMint123456789abcdefghijklmnopqrstuvwxyz",
                "marketLedger": "Ledger123456789abcdefghijklmnopqrstuvwxyz",
                "isInitialized": True,
                "redemptionStatus": "closed",
            }
        },
    }


@pytest.fixture
def mock_event_data():
    """Sample event data for testing."""
    return {
        "ticker": "BTCD-25DEC0313",
        "title": "Bitcoin Price on December 31, 2025",
        "subtitle": "Daily Bitcoin price prediction",
        "seriesTicker": "KXBTC",
        "category": "crypto",
        "mutuallyExclusive": True,
    }


@pytest.fixture
def mock_quote_data():
    """Sample swap quote data for testing."""
    return {
        "inputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "outputMint": "YesMint123456789abcdefghijklmnopqrstuvwxyz",
        "inAmount": "1000000",
        "outAmount": "1538461",
        "priceImpactPct": 0.05,
    }


@pytest.fixture
def mock_orderbook_data():
    """Sample orderbook data for testing (matches actual API format)."""
    return {
        "yes_bids": {"0.6400": 800, "0.6500": 1000},
        "no_bids": {"0.3400": 700, "0.3600": 900},
        "sequence": 1704067200000,
    }


@pytest.fixture
def mock_trade_data():
    """Sample trade data for testing (matches actual API format)."""
    return {
        "tradeId": "trade-123",
        "ticker": "BTCD-25DEC0313-T92749.99",
        "price": 65,
        "count": 100,
        "yesPrice": 6500,
        "noPrice": 3500,
        "yesPriceDollars": "0.65",
        "noPriceDollars": "0.35",
        "takerSide": "yes",
        "createdTime": 1704067200,
    }
