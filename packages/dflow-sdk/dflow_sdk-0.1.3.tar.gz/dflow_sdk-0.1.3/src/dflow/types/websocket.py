"""WebSocket types for DFlow SDK."""

from typing import Literal

from pydantic import BaseModel, Field

WebSocketChannel = Literal["prices", "trades", "orderbook"]


class WebSocketOptions(BaseModel):
    """Options for WebSocket connection."""

    url: str | None = None
    reconnect: bool = True
    reconnect_interval: float = 5.0
    max_reconnect_attempts: int = 10


class PriceLevel(BaseModel):
    """Price level in orderbook update."""

    price: float
    quantity: float


class PriceUpdate(BaseModel):
    """Real-time price update from WebSocket."""

    channel: Literal["prices"]
    ticker: str
    timestamp: int
    yes_price: float = Field(alias="yesPrice")
    no_price: float = Field(alias="noPrice")
    yes_bid: float | None = Field(default=None, alias="yesBid")
    yes_ask: float | None = Field(default=None, alias="yesAsk")
    no_bid: float | None = Field(default=None, alias="noBid")
    no_ask: float | None = Field(default=None, alias="noAsk")

    model_config = {"populate_by_name": True}


class TradeUpdate(BaseModel):
    """Real-time trade update from WebSocket."""

    channel: Literal["trades"]
    ticker: str
    timestamp: int
    side: Literal["yes", "no"]
    price: float
    quantity: float
    trade_id: str = Field(alias="tradeId")

    model_config = {"populate_by_name": True}


class OrderbookUpdate(BaseModel):
    """Real-time orderbook update from WebSocket."""

    channel: Literal["orderbook"]
    ticker: str
    timestamp: int
    yes_ask: list[PriceLevel] = Field(alias="yesAsk")
    yes_bid: list[PriceLevel] = Field(alias="yesBid")
    no_ask: list[PriceLevel] = Field(alias="noAsk")
    no_bid: list[PriceLevel] = Field(alias="noBid")

    model_config = {"populate_by_name": True}


WebSocketUpdate = PriceUpdate | TradeUpdate | OrderbookUpdate
