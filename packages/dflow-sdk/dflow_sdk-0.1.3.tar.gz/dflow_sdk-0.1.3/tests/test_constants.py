"""Tests for constants."""

from dflow.utils.constants import (
    DEFAULT_SLIPPAGE_BPS,
    MAX_BATCH_SIZE,
    MAX_FILTER_ADDRESSES,
    METADATA_API_BASE_URL,
    OUTCOME_TOKEN_DECIMALS,
    PROD_METADATA_API_BASE_URL,
    PROD_TRADE_API_BASE_URL,
    PROD_WEBSOCKET_URL,
    SOL_MINT,
    TRADE_API_BASE_URL,
    USDC_MINT,
    WEBSOCKET_URL,
)


class TestAPIURLs:
    """Tests for API URL constants."""

    def test_development_urls(self):
        """Test development environment URLs."""
        assert "dev-" in METADATA_API_BASE_URL
        assert "dev-" in TRADE_API_BASE_URL
        assert "dev-" in WEBSOCKET_URL

    def test_production_urls(self):
        """Test production environment URLs."""
        assert "dev-" not in PROD_METADATA_API_BASE_URL
        assert "dev-" not in PROD_TRADE_API_BASE_URL
        assert "dev-" not in PROD_WEBSOCKET_URL

    def test_urls_are_valid(self):
        """Test URLs have valid format."""
        assert METADATA_API_BASE_URL.startswith("https://")
        assert TRADE_API_BASE_URL.startswith("https://")
        assert WEBSOCKET_URL.startswith("wss://")
        assert PROD_METADATA_API_BASE_URL.startswith("https://")
        assert PROD_TRADE_API_BASE_URL.startswith("https://")
        assert PROD_WEBSOCKET_URL.startswith("wss://")


class TestTokenMints:
    """Tests for token mint constants."""

    def test_usdc_mint(self):
        """Test USDC mint address is valid Solana address."""
        assert len(USDC_MINT) == 44  # Base58 encoded pubkey length
        assert USDC_MINT == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

    def test_sol_mint(self):
        """Test SOL mint address is valid."""
        assert len(SOL_MINT) == 43  # Native SOL wrapped mint
        assert SOL_MINT == "So11111111111111111111111111111111111111112"


class TestTradingDefaults:
    """Tests for trading default constants."""

    def test_default_slippage(self):
        """Test default slippage is reasonable."""
        assert DEFAULT_SLIPPAGE_BPS == 50  # 0.5%
        assert DEFAULT_SLIPPAGE_BPS > 0
        assert DEFAULT_SLIPPAGE_BPS < 1000  # Less than 10%

    def test_outcome_token_decimals(self):
        """Test outcome token decimals matches USDC."""
        assert OUTCOME_TOKEN_DECIMALS == 6


class TestAPILimits:
    """Tests for API limit constants."""

    def test_batch_size_limit(self):
        """Test batch size limit is reasonable."""
        assert MAX_BATCH_SIZE == 100
        assert MAX_BATCH_SIZE > 0

    def test_filter_addresses_limit(self):
        """Test filter addresses limit is reasonable."""
        assert MAX_FILTER_ADDRESSES == 200
        assert MAX_FILTER_ADDRESSES > 0
