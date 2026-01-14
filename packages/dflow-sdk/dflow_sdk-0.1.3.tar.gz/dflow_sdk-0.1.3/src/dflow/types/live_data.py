"""Live data types for DFlow SDK."""

from typing import Any

from pydantic import BaseModel, Field


class LiveDataMilestone(BaseModel):
    """Milestone in live data."""

    id: str | None = None
    name: str | None = None
    value: str | int | float | None = None
    timestamp: str | int | None = None


class LiveData(BaseModel):
    """Live data for an event or market.

    Note: The actual structure depends on the specific event type.
    Use model_extra to access additional fields.
    """

    model_config = {"extra": "allow"}


class LiveDataResponse(BaseModel):
    """Response from live data endpoint."""

    live_datas: list[dict[str, Any]] = Field(default_factory=list, alias="live_datas")

    model_config = {"populate_by_name": True}
