"""Series types for DFlow SDK."""

from pydantic import BaseModel


class Series(BaseModel):
    """Series/category information."""

    ticker: str
    title: str
    category: str
    tags: list[str]
    frequency: str | None = None
    description: str | None = None


class SeriesResponse(BaseModel):
    """Response from series endpoint."""

    series: list[Series]
