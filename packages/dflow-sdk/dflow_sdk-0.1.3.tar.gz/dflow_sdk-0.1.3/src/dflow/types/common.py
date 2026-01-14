"""Common types for DFlow SDK."""

from typing import Literal

from pydantic import BaseModel


class PaginationParams(BaseModel):
    """Parameters for paginated API requests."""

    cursor: str | None = None
    limit: int | None = None


class Candlestick(BaseModel):
    """OHLCV candlestick data point."""

    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


CandlestickPeriod = Literal["1m", "5m", "15m", "1h", "4h", "1d"]
