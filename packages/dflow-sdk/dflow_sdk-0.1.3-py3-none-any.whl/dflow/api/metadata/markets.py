"""Markets API for DFlow SDK."""

from dflow.types import Candlestick, Market, MarketsResponse
from dflow.utils.constants import MAX_BATCH_SIZE, MAX_FILTER_ADDRESSES
from dflow.utils.http import HttpClient


class MarketsAPI:
    """API for querying prediction market data, pricing, and batch operations.

    Markets represent individual trading instruments within events. Each market
    has YES and NO outcome tokens that can be traded. Markets can be binary
    (yes/no) or scalar (range of values).

    Example:
        >>> dflow = DFlowClient()
        >>>
        >>> # Get a specific market
        >>> market = dflow.markets.get_market("BTCD-25DEC0313-T92749.99")
        >>>
        >>> # Get active markets
        >>> response = dflow.markets.get_markets(status="active")
        >>>
        >>> # Batch query multiple markets
        >>> markets = dflow.markets.get_markets_batch(tickers=["MARKET-1", "MARKET-2"])
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def get_market(self, market_id: str) -> Market:
        """Get a single market by its ticker.

        Args:
            market_id: The market ticker (e.g., 'BTCD-25DEC0313-T92749.99')

        Returns:
            Complete market data including prices, accounts, and status

        Example:
            >>> market = dflow.markets.get_market("BTCD-25DEC0313-T92749.99")
            >>> print(f"YES: {market.yes_price}, NO: {market.no_price}")
            >>> print(f"Volume: {market.volume}")
        """
        data = self._http.get(f"/market/{market_id}")
        return Market.model_validate(data)

    def get_market_by_mint(self, mint_address: str) -> Market:
        """Get a market by its outcome token mint address.

        Useful when you have a mint address from a wallet or transaction
        and need to look up the associated market.

        Args:
            mint_address: The Solana mint address of a YES or NO token

        Returns:
            The market associated with the mint address
        """
        data = self._http.get(f"/market/by-mint/{mint_address}")
        return Market.model_validate(data)

    def get_markets(
        self,
        status: str | None = None,
        event_ticker: str | None = None,
        series_ticker: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> MarketsResponse:
        """List markets with optional filtering.

        Args:
            status: Filter by market status ('active', 'closed', etc.)
            event_ticker: Filter by parent event ticker
            series_ticker: Filter by series ticker
            limit: Maximum number of markets to return
            cursor: Pagination cursor from previous response

        Returns:
            Paginated list of markets

        Example:
            >>> # Get all active markets
            >>> response = dflow.markets.get_markets(status="active")
            >>>
            >>> # Get markets for a specific event
            >>> response = dflow.markets.get_markets(event_ticker="BTCD-25DEC0313")
            >>>
            >>> # Paginate through results
            >>> next_page = dflow.markets.get_markets(cursor=response.cursor)
        """
        data = self._http.get(
            "/markets",
            {
                "status": status,
                "eventTicker": event_ticker,
                "seriesTicker": series_ticker,
                "limit": limit,
                "cursor": cursor,
            },
        )
        return MarketsResponse.model_validate(data)

    def get_markets_batch(
        self,
        tickers: list[str] | None = None,
        mints: list[str] | None = None,
    ) -> list[Market]:
        """Batch query multiple markets by tickers and/or mint addresses.

        More efficient than multiple individual requests when you need
        data for several markets at once.

        Args:
            tickers: Array of market tickers to fetch
            mints: Array of mint addresses to fetch

        Returns:
            Array of market data

        Raises:
            ValueError: If total items exceed MAX_BATCH_SIZE (100)

        Example:
            >>> markets = dflow.markets.get_markets_batch(
            ...     tickers=["MARKET-1", "MARKET-2", "MARKET-3"],
            ...     mints=["mint-address-1"],
            ... )
        """
        total_items = len(tickers or []) + len(mints or [])
        if total_items > MAX_BATCH_SIZE:
            raise ValueError(f"Batch size exceeds maximum of {MAX_BATCH_SIZE} items")

        data = self._http.post(
            "/markets/batch",
            {"tickers": tickers or [], "mints": mints or []},
        )
        markets_data = data.get("markets", []) if isinstance(data, dict) else data
        return [Market.model_validate(m) for m in markets_data]

    def get_outcome_mints(self) -> list[str]:
        """Get all outcome token mint addresses.

        Returns a list of all valid outcome token mints across all markets.
        Useful for filtering wallet tokens to find prediction market positions.

        Returns:
            Array of mint addresses

        Example:
            >>> all_mints = dflow.markets.get_outcome_mints()
            >>> print(f"Total outcome tokens: {len(all_mints)}")
        """
        data = self._http.get("/outcome_mints")
        return data.get("mints", [])

    def filter_outcome_mints(self, addresses: list[str]) -> list[str]:
        """Filter a list of addresses to find which are outcome token mints.

        Given a list of token addresses (e.g., from a wallet), returns only
        those that are prediction market outcome tokens.

        Args:
            addresses: Array of Solana token addresses to check

        Returns:
            Array of addresses that are outcome token mints

        Raises:
            ValueError: If addresses exceed MAX_FILTER_ADDRESSES (200)

        Example:
            >>> wallet_tokens = ["addr1", "addr2", "addr3"]
            >>> prediction_tokens = dflow.markets.filter_outcome_mints(wallet_tokens)
        """
        if len(addresses) > MAX_FILTER_ADDRESSES:
            raise ValueError(
                f"Address count exceeds maximum of {MAX_FILTER_ADDRESSES}"
            )

        data = self._http.post("/filter_outcome_mints", {"addresses": addresses})
        return data.get("outcomeMints", [])

    def get_market_candlesticks(self, ticker: str) -> list[Candlestick]:
        """Get OHLCV candlestick data for a market.

        Returns price history in candlestick format for charting.

        Args:
            ticker: The market ticker

        Returns:
            Array of candlestick data points

        Example:
            >>> candles = dflow.markets.get_market_candlesticks("BTCD-25DEC0313-T92749.99")
            >>> for c in candles:
            ...     print(f"O={c.open} H={c.high} L={c.low} C={c.close}")
        """
        data = self._http.get(f"/market/{ticker}/candlesticks")
        return [Candlestick.model_validate(c) for c in data.get("candlesticks", [])]

    def get_market_candlesticks_by_mint(self, mint_address: str) -> list[Candlestick]:
        """Get OHLCV candlestick data for a market by mint address.

        Alternative to get_market_candlesticks when you have the mint address.

        Args:
            mint_address: The Solana mint address of the market's outcome token

        Returns:
            Array of candlestick data points
        """
        data = self._http.get(f"/market/by-mint/{mint_address}/candlesticks")
        return [Candlestick.model_validate(c) for c in data.get("candlesticks", [])]
