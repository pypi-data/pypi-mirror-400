"""Trade types for DFlow SDK."""

from typing import Literal

from pydantic import BaseModel, Field

TradeSide = Literal["yes", "no"]
TradeAction = Literal["buy", "sell"]


class Trade(BaseModel):
    """Historical trade data."""

    trade_id: str = Field(alias="tradeId")
    ticker: str
    price: int  # Price in cents
    count: int  # Quantity
    yes_price: int = Field(alias="yesPrice")
    no_price: int = Field(alias="noPrice")
    yes_price_dollars: str = Field(alias="yesPriceDollars")
    no_price_dollars: str = Field(alias="noPriceDollars")
    taker_side: TradeSide = Field(alias="takerSide")
    created_time: int = Field(alias="createdTime")

    model_config = {"populate_by_name": True}

    # Backwards-compatible properties
    @property
    def id(self) -> str:
        """Alias for trade_id for backwards compatibility."""
        return self.trade_id

    @property
    def market_ticker(self) -> str:
        """Alias for ticker for backwards compatibility."""
        return self.ticker

    @property
    def side(self) -> TradeSide:
        """Alias for taker_side for backwards compatibility."""
        return self.taker_side

    @property
    def quantity(self) -> int:
        """Alias for count for backwards compatibility."""
        return self.count

    @property
    def timestamp(self) -> int:
        """Alias for created_time for backwards compatibility."""
        return self.created_time


class TradesResponse(BaseModel):
    """Response from trades endpoint."""

    cursor: str | int | None = None
    trades: list[Trade]
