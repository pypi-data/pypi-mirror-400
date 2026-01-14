"""Trades API for DFlow SDK."""

from dflow.types import TradesResponse
from dflow.utils.http import HttpClient


class TradesAPI:
    """API for retrieving historical trade data.

    Access past trades for markets to analyze trading activity and price history.

    Example:
        >>> dflow = DFlowClient()
        >>> response = dflow.trades.get_trades(market_ticker="BTCD-25DEC0313-T92749.99")
        >>> for trade in response.trades:
        ...     print(f"{trade.side} {trade.quantity} @ {trade.price}")
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def get_trades(
        self,
        market_ticker: str | None = None,
        start_timestamp: str | None = None,
        end_timestamp: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> TradesResponse:
        """Get historical trades with optional filtering.

        Args:
            market_ticker: Filter by market ticker
            start_timestamp: Filter trades after this timestamp
            end_timestamp: Filter trades before this timestamp
            limit: Maximum number of trades to return
            cursor: Pagination cursor from previous response

        Returns:
            Paginated list of trades

        Example:
            >>> # Get recent trades for a market
            >>> response = dflow.trades.get_trades(
            ...     market_ticker="BTCD-25DEC0313-T92749.99",
            ...     limit=100,
            ... )
            >>>
            >>> # Paginate through results
            >>> next_page = dflow.trades.get_trades(cursor=response.cursor)
        """
        data = self._http.get(
            "/trades",
            {
                "marketTicker": market_ticker,
                "startTimestamp": start_timestamp,
                "endTimestamp": end_timestamp,
                "limit": limit,
                "cursor": cursor,
            },
        )
        return TradesResponse.model_validate(data)

    def get_trades_by_mint(
        self,
        mint_address: str,
        start_timestamp: str | None = None,
        end_timestamp: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> TradesResponse:
        """Get trades for a market by mint address.

        Alternative to get_trades when you have the mint address.

        Args:
            mint_address: The Solana mint address of the market's outcome token
            start_timestamp: Filter trades after this timestamp
            end_timestamp: Filter trades before this timestamp
            limit: Maximum number of trades to return
            cursor: Pagination cursor from previous response

        Returns:
            Paginated list of trades
        """
        data = self._http.get(
            f"/trades/by-mint/{mint_address}",
            {
                "startTimestamp": start_timestamp,
                "endTimestamp": end_timestamp,
                "limit": limit,
                "cursor": cursor,
            },
        )
        return TradesResponse.model_validate(data)
