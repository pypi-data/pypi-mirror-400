"""Constants for DFlow SDK."""

# ============================================================================
# API URLs
# ============================================================================

# Default metadata API base URL (development environment).
# No API key required. For testing with real capital against Kalshi.
METADATA_API_BASE_URL = "https://dev-prediction-markets-api.dflow.net/api/v1"

# Default trade API base URL (development environment).
# No API key required. For testing with real capital against Kalshi.
TRADE_API_BASE_URL = "https://dev-quote-api.dflow.net"

# Default WebSocket URL (development environment).
# No API key required.
WEBSOCKET_URL = "wss://dev-prediction-markets-api.dflow.net/api/v1/ws"

# Production metadata API base URL.
# Requires API key for access.
PROD_METADATA_API_BASE_URL = "https://prediction-markets-api.dflow.net/api/v1"

# Production trade API base URL.
# Requires API key for access.
PROD_TRADE_API_BASE_URL = "https://quote-api.dflow.net"

# Production WebSocket URL.
# Requires API key for access.
PROD_WEBSOCKET_URL = "wss://prediction-markets-api.dflow.net/api/v1/ws"

# ============================================================================
# Token Mints
# ============================================================================

# USDC token mint address on Solana mainnet.
# Used as the default settlement currency for prediction markets.
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# Native SOL mint address (wrapped SOL).
SOL_MINT = "So11111111111111111111111111111111111111112"

# ============================================================================
# Trading Defaults
# ============================================================================

# Default slippage tolerance in basis points (0.5%).
# 50 bps = 0.5% = multiply price by 1.005 for max acceptable price.
DEFAULT_SLIPPAGE_BPS = 50

# Number of decimal places for outcome tokens.
# All YES/NO tokens use 6 decimals (same as USDC).
OUTCOME_TOKEN_DECIMALS = 6

# ============================================================================
# API Limits
# ============================================================================

# Maximum number of items in a batch request.
# Applies to get_markets_batch and similar batch endpoints.
MAX_BATCH_SIZE = 100

# Maximum number of addresses for filter_outcome_mints.
MAX_FILTER_ADDRESSES = 200
