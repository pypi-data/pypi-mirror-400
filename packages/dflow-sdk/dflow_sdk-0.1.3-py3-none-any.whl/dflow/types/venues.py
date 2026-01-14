"""Venue types for DFlow SDK."""

from pydantic import BaseModel


class Venue(BaseModel):
    """Trading venue information."""

    id: str
    name: str
    label: str
