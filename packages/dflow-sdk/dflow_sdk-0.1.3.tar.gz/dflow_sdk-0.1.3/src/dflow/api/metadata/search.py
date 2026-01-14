"""Search API for DFlow SDK."""

from dflow.types import SearchResult
from dflow.utils.http import HttpClient


class SearchAPI:
    """API for searching events and markets.

    Full-text search across events and markets by keywords.

    Example:
        >>> dflow = DFlowClient()
        >>> results = dflow.search.search("bitcoin")
        >>> print(f"Found {len(results.events)} events")
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def search(self, query: str, limit: int | None = None) -> SearchResult:
        """Search for events and markets by keyword.

        Args:
            query: The search query string
            limit: Maximum number of results to return

        Returns:
            Search results containing matching events

        Example:
            >>> results = dflow.search.search("bitcoin", limit=20)
            >>> for event in results.events:
            ...     print(f"Event: {event.title}")
        """
        data = self._http.get("/search", {"q": query, "limit": limit})
        return SearchResult.model_validate(data)
