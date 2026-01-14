"""Events API for DFlow SDK."""

from dflow.types import Candlestick, Event, EventsResponse, ForecastHistory
from dflow.utils.http import HttpClient


class EventsAPI:
    """API for discovering and querying prediction market events.

    Events are the top-level containers for prediction markets. Each event
    represents a question or outcome to predict (e.g., "Will Bitcoin exceed $100k?")
    and contains one or more markets for trading.

    Example:
        >>> dflow = DFlowClient()
        >>>
        >>> # Get active events
        >>> response = dflow.events.get_events(status="active")
        >>>
        >>> # Get a specific event with its markets
        >>> event = dflow.events.get_event("event-id", with_nested_markets=True)
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def get_event(self, event_id: str, with_nested_markets: bool = False) -> Event:
        """Get a single event by its ID.

        Args:
            event_id: The unique identifier of the event
            with_nested_markets: If True, includes all markets within the event

        Returns:
            The event data, optionally with nested markets

        Example:
            >>> # Get event without markets
            >>> event = dflow.events.get_event("BTCD-25DEC0313")
            >>>
            >>> # Get event with all its markets
            >>> event = dflow.events.get_event("BTCD-25DEC0313", with_nested_markets=True)
            >>> print(event.markets)
        """
        data = self._http.get(
            f"/event/{event_id}",
            {"withNestedMarkets": with_nested_markets} if with_nested_markets else None,
        )
        return Event.model_validate(data)

    def get_events(
        self,
        status: str | None = None,
        series_ticker: str | None = None,
        with_nested_markets: bool | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> EventsResponse:
        """List events with optional filtering.

        Args:
            status: Filter by event status ('active', 'closed', etc.)
            series_ticker: Filter by series ticker (e.g., 'KXBTC')
            with_nested_markets: If True, includes markets within each event
            limit: Maximum number of events to return
            cursor: Pagination cursor from previous response

        Returns:
            Paginated list of events

        Example:
            >>> # Get all active events
            >>> response = dflow.events.get_events(status="active")
            >>>
            >>> # Get events for a specific series
            >>> response = dflow.events.get_events(series_ticker="KXBTC", limit=50)
            >>>
            >>> # Paginate through results
            >>> next_page = dflow.events.get_events(cursor=response.cursor)
        """
        data = self._http.get(
            "/events",
            {
                "status": status,
                "seriesTicker": series_ticker,
                "withNestedMarkets": with_nested_markets,
                "limit": limit,
                "cursor": cursor,
            },
        )
        return EventsResponse.model_validate(data)

    def get_event_forecast_history(
        self, series_ticker: str, event_id: str
    ) -> ForecastHistory:
        """Get forecast percentile history for an event.

        Returns historical forecast data showing how predictions have changed over time.

        Args:
            series_ticker: The series ticker (e.g., 'KXBTC')
            event_id: The event identifier within the series

        Returns:
            Forecast history with percentile data points

        Example:
            >>> history = dflow.events.get_event_forecast_history("KXBTC", "event-123")
            >>> print(history.history)
        """
        data = self._http.get(
            f"/event/{series_ticker}/{event_id}/forecast_percentile_history"
        )
        return ForecastHistory.model_validate(data)

    def get_event_forecast_by_mint(self, mint_address: str) -> ForecastHistory:
        """Get forecast percentile history for an event by its mint address.

        Alternative to get_event_forecast_history when you have the mint address
        instead of series ticker and event ID.

        Args:
            mint_address: The Solana mint address of the event's outcome token

        Returns:
            Forecast history with percentile data points
        """
        data = self._http.get(
            f"/event/by-mint/{mint_address}/forecast_percentile_history"
        )
        return ForecastHistory.model_validate(data)

    def get_event_candlesticks(self, ticker: str) -> list[Candlestick]:
        """Get OHLCV candlestick data for an event.

        Returns price history in candlestick format for charting.

        Args:
            ticker: The event ticker

        Returns:
            Array of candlestick data points

        Example:
            >>> candles = dflow.events.get_event_candlesticks("BTCD-25DEC0313")
            >>> for c in candles:
            ...     print(f"O: {c.open}, H: {c.high}, L: {c.low}, C: {c.close}")
        """
        data = self._http.get(f"/event/{ticker}/candlesticks")
        return [Candlestick.model_validate(c) for c in data.get("candlesticks", [])]
