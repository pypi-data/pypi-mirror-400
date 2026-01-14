"""Search types for DFlow SDK."""

from pydantic import BaseModel

from .events import Event


class SearchParams(BaseModel):
    """Parameters for search queries."""

    query: str
    limit: int | None = None


class SearchResult(BaseModel):
    """Search result response."""

    events: list[Event]
