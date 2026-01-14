"""Main DFlow client for Python SDK."""

from typing import Literal

from dflow.api.metadata import (
    EventsAPI,
    LiveDataAPI,
    MarketsAPI,
    OrderbookAPI,
    SearchAPI,
    SeriesAPI,
    SportsAPI,
    TagsAPI,
    TradesAPI,
)
from dflow.api.trade import (
    IntentAPI,
    OrdersAPI,
    PredictionMarketAPI,
    SwapAPI,
    TokensAPI,
    VenuesAPI,
)
from dflow.utils.constants import (
    METADATA_API_BASE_URL,
    PROD_METADATA_API_BASE_URL,
    PROD_TRADE_API_BASE_URL,
    PROD_WEBSOCKET_URL,
    TRADE_API_BASE_URL,
    WEBSOCKET_URL,
)
from dflow.utils.http import HttpClient
from dflow.websocket import DFlowWebSocket

DFlowEnvironment = Literal["development", "production"]


class DFlowClient:
    """Main client for interacting with the DFlow prediction markets platform.

    DFlow is a prediction markets platform built on Solana. This client provides
    access to all DFlow APIs including:
    - Market data (events, markets, orderbook, trades)
    - Trading (orders, swaps, intents)
    - Real-time updates via WebSocket

    Example:
        >>> from dflow import DFlowClient
        >>>
        >>> # Development (default) - no API key required
        >>> # Uses dev-*.dflow.net endpoints for testing with real capital
        >>> dflow = DFlowClient()
        >>> markets = dflow.markets.get_markets()
        >>>
        >>> # Production - API key required
        >>> # Uses *.dflow.net endpoints for production deployments
        >>> dflow = DFlowClient(environment="production", api_key="your-api-key")
        >>>
        >>> # Get a quote and trade
        >>> quote = dflow.swap.get_quote(
        ...     input_mint=USDC_MINT,
        ...     output_mint=yes_mint,
        ...     amount=1000000,
        ... )

    Attributes:
        events: API for discovering and querying prediction events
        markets: API for market data, pricing, and batch queries
        orderbook: API for orderbook snapshots
        trades: API for historical trade data
        live_data: API for real-time milestone data
        series: API for series/category information
        tags: API for tag-based filtering
        sports: API for sports-specific filters
        search: API for searching events and markets
        orders: API for order creation and status (requires API key)
        swap: API for imperative swaps with route preview (requires API key)
        intent: API for declarative intent-based swaps (requires API key)
        prediction_market: API for prediction market initialization (requires API key)
        tokens: API for token information
        venues: API for trading venue information
        ws: WebSocket client for real-time price, trade, and orderbook updates
    """

    def __init__(
        self,
        environment: DFlowEnvironment = "development",
        api_key: str | None = None,
        metadata_base_url: str | None = None,
        trade_base_url: str | None = None,
        ws_url: str | None = None,
    ):
        """Create a new DFlow client instance.

        Args:
            environment: Environment to use. Defaults to 'development'.
                - 'development': No API key required, uses dev-*.dflow.net endpoints
                - 'production': API key required, uses *.dflow.net endpoints
            api_key: API key for authenticated endpoints (required for production)
            metadata_base_url: Custom base URL for the metadata API (overrides environment)
            trade_base_url: Custom base URL for the trade API (overrides environment)
            ws_url: Custom WebSocket URL (overrides environment)
        """
        is_prod = environment == "production"

        # Determine URLs based on environment (custom URLs override environment)
        metadata_url = metadata_base_url or (
            PROD_METADATA_API_BASE_URL if is_prod else METADATA_API_BASE_URL
        )
        trade_url = trade_base_url or (
            PROD_TRADE_API_BASE_URL if is_prod else TRADE_API_BASE_URL
        )
        websocket_url = ws_url or (PROD_WEBSOCKET_URL if is_prod else WEBSOCKET_URL)

        self._metadata_http = HttpClient(metadata_url, api_key)
        self._trade_http = HttpClient(trade_url, api_key)

        # Metadata APIs
        self.events = EventsAPI(self._metadata_http)
        self.markets = MarketsAPI(self._metadata_http)
        self.orderbook = OrderbookAPI(self._metadata_http)
        self.trades = TradesAPI(self._metadata_http)
        self.live_data = LiveDataAPI(self._metadata_http)
        self.series = SeriesAPI(self._metadata_http)
        self.tags = TagsAPI(self._metadata_http)
        self.sports = SportsAPI(self._metadata_http)
        self.search = SearchAPI(self._metadata_http)

        # Trade APIs
        self.orders = OrdersAPI(self._trade_http)
        self.swap = SwapAPI(self._trade_http)
        self.intent = IntentAPI(self._trade_http)
        self.prediction_market = PredictionMarketAPI(self._trade_http)
        self.tokens = TokensAPI(self._trade_http)
        self.venues = VenuesAPI(self._trade_http)

        # WebSocket
        self.ws = DFlowWebSocket(url=websocket_url)

    def set_api_key(self, api_key: str) -> None:
        """Update the API key for both metadata and trade HTTP clients.

        Useful for setting the key after initialization or rotating keys.

        Args:
            api_key: The new API key to use

        Example:
            >>> dflow = DFlowClient()
            >>>
            >>> # Browse markets without auth
            >>> markets = dflow.markets.get_markets()
            >>>
            >>> # Set API key when user logs in
            >>> dflow.set_api_key("user-api-key")
            >>>
            >>> # Now can use authenticated endpoints
            >>> quote = dflow.swap.get_quote(params)
        """
        self._metadata_http.set_api_key(api_key)
        self._trade_http.set_api_key(api_key)

    def close(self) -> None:
        """Close all connections.

        Closes HTTP clients and disconnects WebSocket.
        """
        self._metadata_http.close()
        self._trade_http.close()
        self.ws.disconnect()

    def __enter__(self) -> "DFlowClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()
