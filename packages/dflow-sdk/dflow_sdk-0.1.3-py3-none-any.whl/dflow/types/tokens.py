"""Token types for DFlow SDK."""

from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token information."""

    mint: str
    symbol: str
    name: str
    logo_uri: str | None = Field(default=None, alias="logoUri")

    model_config = {"populate_by_name": True}


class TokenWithDecimals(Token):
    """Token information with decimal precision."""

    decimals: int
