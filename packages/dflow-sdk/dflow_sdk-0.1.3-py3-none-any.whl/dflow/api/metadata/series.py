"""Series API for DFlow SDK."""

from dflow.types import Series
from dflow.utils.http import HttpClient


class SeriesAPI:
    """API for retrieving series/category information.

    Series group related events together (e.g., all Bitcoin price events,
    all election events). Use series to browse events by category.

    Example:
        >>> dflow = DFlowClient()
        >>> series = dflow.series.get_series()
        >>> for s in series:
        ...     print(f"{s.ticker}: {s.title}")
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def get_series(self) -> list[Series]:
        """Get all available series.

        Returns:
            Array of all series

        Example:
            >>> series = dflow.series.get_series()
            >>> for s in series:
            ...     print(f"{s.ticker}: {s.title}")
        """
        data = self._http.get("/series")
        return [Series.model_validate(s) for s in data.get("series", [])]

    def get_series_by_ticker(self, ticker: str) -> Series:
        """Get a specific series by its ticker.

        Args:
            ticker: The series ticker (e.g., 'KXBTC', 'KXETH')

        Returns:
            The series data

        Example:
            >>> series = dflow.series.get_series_by_ticker("KXBTC")
            >>> print(f"{series.title}: {series.description}")
        """
        data = self._http.get(f"/series/{ticker}")
        return Series.model_validate(data)
