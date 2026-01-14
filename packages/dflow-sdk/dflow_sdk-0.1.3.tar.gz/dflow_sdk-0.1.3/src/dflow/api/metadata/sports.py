"""Sports API for DFlow SDK."""

from dflow.types import SportsFilters
from dflow.utils.http import HttpClient


class SportsAPI:
    """API for retrieving sports-specific filters.

    Get available filters for sports-related prediction markets
    (leagues, teams, event types, etc.).

    Example:
        >>> dflow = DFlowClient()
        >>> filters = dflow.sports.get_filters_by_sports()
        >>> for sport in filters.sports:
        ...     print(f"{sport.sport}: {sport.leagues}")
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def get_filters_by_sports(self) -> SportsFilters:
        """Get all available sports filters.

        Returns:
            Sports filters including leagues, teams, and event types

        Example:
            >>> filters = dflow.sports.get_filters_by_sports()
            >>> for sport in filters.sports:
            ...     print(f"{sport.sport}: {sport.leagues}")
        """
        data = self._http.get("/filters_by_sports")
        return SportsFilters.model_validate(data)
