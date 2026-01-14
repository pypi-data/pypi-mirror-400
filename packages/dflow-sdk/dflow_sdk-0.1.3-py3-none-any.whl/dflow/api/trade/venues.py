"""Venues API for DFlow SDK."""

from dflow.utils.http import HttpClient


class VenuesAPI:
    """API for retrieving trading venue information.

    Venues represent the underlying exchanges or liquidity sources
    where trades are executed (e.g., 'Whirlpools', 'Raydium AMM').

    Example:
        >>> dflow = DFlowClient()
        >>> venues = dflow.venues.get_venues()
        >>> for venue in venues:
        ...     print(venue)
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def get_venues(self) -> list[str]:
        """Get all available trading venue names.

        Returns:
            List of venue names

        Example:
            >>> venues = dflow.venues.get_venues()
            >>> print(venues)  # ['Whirlpools', 'Raydium AMM', ...]
        """
        data = self._http.get("/venues")
        return data
