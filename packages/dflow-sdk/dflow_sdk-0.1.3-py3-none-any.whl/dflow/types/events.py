"""Event types for DFlow SDK."""

from pydantic import BaseModel, Field

from .markets import Market


class SettlementSource(BaseModel):
    """Settlement source information."""

    name: str
    url: str


class Event(BaseModel):
    """Prediction event data."""

    ticker: str
    title: str
    subtitle: str | None = None
    series_ticker: str = Field(alias="seriesTicker")
    
    # Optional fields from API
    strike_date: str | int | None = Field(default=None, alias="strikeDate")
    strike_period: str | None = Field(default=None, alias="strikePeriod")
    image_url: str | None = Field(default=None, alias="imageUrl")
    competition: str | None = None
    competition_scope: str | None = Field(default=None, alias="competitionScope")
    settlement_sources: list[SettlementSource] | None = Field(default=None, alias="settlementSources")
    
    # Volume and liquidity
    volume: float | None = None
    volume_24h: float | None = Field(default=None, alias="volume24h")
    liquidity: float | None = None
    open_interest: float | None = Field(default=None, alias="openInterest")
    
    # Legacy fields (may not be present)
    category: str | None = None
    mutually_exclusive: bool | None = Field(default=None, alias="mutuallyExclusive")
    
    # Nested markets
    markets: list[Market] | None = None

    model_config = {"populate_by_name": True}


class EventsResponse(BaseModel):
    """Response from events list endpoint."""

    cursor: str | int | None = None
    events: list[Event]


class ForecastHistoryPoint(BaseModel):
    """Single point in forecast history."""

    timestamp: int
    yes_price: float = Field(alias="yesPrice")
    no_price: float = Field(alias="noPrice")
    percentile: float | None = None

    model_config = {"populate_by_name": True}


class ForecastHistory(BaseModel):
    """Forecast history data for an event."""

    event_ticker: str = Field(alias="eventTicker")
    history: list[ForecastHistoryPoint]

    model_config = {"populate_by_name": True}
