"""DFlow Python SDK - Prediction markets and trading on Solana.

This SDK provides a complete Python interface for interacting with the DFlow
prediction markets platform on Solana.

Example:
    >>> from dflow import DFlowClient, USDC_MINT
    >>>
    >>> # Create a client (development mode - no API key required)
    >>> dflow = DFlowClient()
    >>>
    >>> # Get active markets
    >>> response = dflow.markets.get_markets(status="active")
    >>> for market in response.markets:
    ...     print(f"{market.ticker}: YES={market.yes_price}")
    >>>
    >>> # Get a swap quote
    >>> quote = dflow.swap.get_quote(
    ...     input_mint=USDC_MINT,
    ...     output_mint=market.accounts["usdc"].yes_mint,
    ...     amount=1_000_000,
    ... )
    >>> print(f"You'll receive: {quote.out_amount} tokens")
"""

from dflow.client import DFlowClient, DFlowEnvironment

# API classes
from dflow.api import (
    EventsAPI,
    IntentAPI,
    LiveDataAPI,
    MarketsAPI,
    OrderbookAPI,
    OrdersAPI,
    PredictionMarketAPI,
    SearchAPI,
    SeriesAPI,
    SportsAPI,
    SwapAPI,
    TagsAPI,
    TokensAPI,
    TradesAPI,
    VenuesAPI,
)

# Solana utilities
from dflow.solana import (
    calculate_scalar_payout,
    get_token_balances,
    get_user_positions,
    is_redemption_eligible,
    sign_and_send_transaction,
    sign_send_and_confirm,
    wait_for_confirmation,
    wait_for_confirmation_async,
)

# WebSocket
from dflow.websocket import DFlowWebSocket

# Utilities
from dflow.utils import (
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
    DFlowApiError,
    HttpClient,
    collect_all,
    count_all,
    create_retryable,
    default_should_retry,
    find_first,
    paginate,
    paginate_async,
    with_retry,
    with_retry_async,
)

# Types - export the most commonly used ones
from dflow.types import (
    Candlestick,
    Event,
    EventsResponse,
    ForecastHistory,
    IntentQuote,
    IntentResponse,
    LiveData,
    Market,
    MarketAccount,
    MarketsResponse,
    Orderbook,
    OrderbookLevel,
    OrderbookUpdate,
    OrderResponse,
    OrderStatusResponse,
    PredictionMarketInitResponse,
    PriceUpdate,
    PriorityFeeConfig,
    SearchResult,
    Series,
    SportsFilters,
    SwapQuote,
    SwapResponse,
    Token,
    TokenBalance,
    TokenWithDecimals,
    Trade,
    TradeUpdate,
    TradesResponse,
    TransactionConfirmation,
    UserPosition,
    Venue,
    WebSocketOptions,
)

__version__ = "0.1.3"

__all__ = [
    # Main client
    "DFlowClient",
    "DFlowEnvironment",
    # API classes
    "EventsAPI",
    "MarketsAPI",
    "OrderbookAPI",
    "TradesAPI",
    "LiveDataAPI",
    "SeriesAPI",
    "TagsAPI",
    "SportsAPI",
    "SearchAPI",
    "OrdersAPI",
    "SwapAPI",
    "IntentAPI",
    "PredictionMarketAPI",
    "TokensAPI",
    "VenuesAPI",
    # WebSocket
    "DFlowWebSocket",
    # Solana utilities
    "sign_and_send_transaction",
    "wait_for_confirmation",
    "wait_for_confirmation_async",
    "sign_send_and_confirm",
    "get_token_balances",
    "get_user_positions",
    "is_redemption_eligible",
    "calculate_scalar_payout",
    # HTTP utilities
    "HttpClient",
    "DFlowApiError",
    # Retry utilities
    "with_retry",
    "with_retry_async",
    "create_retryable",
    "default_should_retry",
    # Pagination utilities
    "paginate",
    "paginate_async",
    "collect_all",
    "count_all",
    "find_first",
    # Constants
    "METADATA_API_BASE_URL",
    "TRADE_API_BASE_URL",
    "WEBSOCKET_URL",
    "PROD_METADATA_API_BASE_URL",
    "PROD_TRADE_API_BASE_URL",
    "PROD_WEBSOCKET_URL",
    "USDC_MINT",
    "SOL_MINT",
    "DEFAULT_SLIPPAGE_BPS",
    "OUTCOME_TOKEN_DECIMALS",
    "MAX_BATCH_SIZE",
    "MAX_FILTER_ADDRESSES",
    # Types
    "Candlestick",
    "Event",
    "EventsResponse",
    "ForecastHistory",
    "IntentQuote",
    "IntentResponse",
    "LiveData",
    "Market",
    "MarketAccount",
    "MarketsResponse",
    "Orderbook",
    "OrderbookLevel",
    "OrderbookUpdate",
    "OrderResponse",
    "OrderStatusResponse",
    "PredictionMarketInitResponse",
    "PriceUpdate",
    "PriorityFeeConfig",
    "SearchResult",
    "Series",
    "SportsFilters",
    "SwapQuote",
    "SwapResponse",
    "Token",
    "TokenBalance",
    "TokenWithDecimals",
    "Trade",
    "TradeUpdate",
    "TradesResponse",
    "TransactionConfirmation",
    "UserPosition",
    "Venue",
    "WebSocketOptions",
]
