"""Tag types for DFlow SDK."""

from typing import Any

from pydantic import BaseModel, Field


# CategoryTags is a dict mapping category names to lists of tag strings
CategoryTags = dict[str, list[str]]


class SportFilterInfo(BaseModel):
    """Filter information for a specific sport."""

    competitions: dict[str, Any] = Field(default_factory=dict)
    scopes: list[str] = Field(default_factory=list)


class SportsFilters(BaseModel):
    """Response from sports filters endpoint.

    The structure is: {"filtersBySports": {"Sport Name": {"competitions": {...}, "scopes": [...]}, ...}}
    """

    filters_by_sports: dict[str, SportFilterInfo] = Field(
        default_factory=dict, alias="filtersBySports"
    )

    model_config = {"populate_by_name": True}

    @property
    def sport_names(self) -> list[str]:
        """Get list of all sport names."""
        return list(self.filters_by_sports.keys())

    def get_sport_filter(self, sport_name: str) -> SportFilterInfo | None:
        """Get filter info for a specific sport."""
        return self.filters_by_sports.get(sport_name)


# Keep for backwards compatibility
class SportsFilter(BaseModel):
    """Sports filter with leagues and teams (legacy type)."""

    sport: str
    leagues: list[str] = Field(default_factory=list)
    teams: list[str] | None = None
