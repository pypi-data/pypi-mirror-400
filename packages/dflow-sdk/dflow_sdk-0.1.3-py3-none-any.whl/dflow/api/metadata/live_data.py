"""Live Data API for DFlow SDK."""

from typing import Any

from dflow.types import LiveDataResponse
from dflow.utils.http import HttpClient


class LiveDataAPI:
    """API for retrieving real-time milestone and progress data.

    Live data provides real-time updates on event milestones and progress
    indicators that can affect market outcomes.

    Example:
        >>> dflow = DFlowClient()
        >>> response = dflow.live_data.get_live_data_by_event("KXSB-26")
        >>> print(f"Live data items: {len(response.live_datas)}")
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def get_live_data(self, milestones: list[str]) -> list[dict[str, Any]]:
        """Get live data for specific milestones.

        Args:
            milestones: Array of milestone identifiers to fetch

        Returns:
            List of live data dicts for the requested milestones

        Example:
            >>> data = dflow.live_data.get_live_data(["btc-price"])
        """
        data = self._http.get("/live_data", {"milestones": ",".join(milestones)})
        return data.get("live_datas", []) if isinstance(data, dict) else []

    def get_live_data_by_event(self, event_ticker: str) -> LiveDataResponse:
        """Get live data for an event by its ticker.

        Args:
            event_ticker: The event ticker

        Returns:
            LiveDataResponse containing live_datas list

        Example:
            >>> response = dflow.live_data.get_live_data_by_event("KXSB-26")
            >>> print(f"Items: {len(response.live_datas)}")
        """
        data = self._http.get(f"/live_data/by-event/{event_ticker}")
        return LiveDataResponse.model_validate(data)

    def get_live_data_by_mint(self, mint_address: str) -> LiveDataResponse:
        """Get live data for a market by mint address.

        Args:
            mint_address: The Solana mint address of the market's outcome token

        Returns:
            LiveDataResponse containing live_datas list
        """
        data = self._http.get(f"/live_data/by-mint/{mint_address}")
        return LiveDataResponse.model_validate(data)
