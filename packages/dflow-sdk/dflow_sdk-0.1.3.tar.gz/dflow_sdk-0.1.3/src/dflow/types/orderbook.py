"""Orderbook types for DFlow SDK."""

from pydantic import BaseModel, Field


class OrderbookLevel(BaseModel):
    """Single price level in the orderbook."""

    price: float
    quantity: float


class Orderbook(BaseModel):
    """Orderbook snapshot for a market.

    Note: The API returns bids as dicts mapping price strings to quantities.
    The `yes_bids` and `no_bids` represent buy orders for YES and NO tokens.
    """

    yes_bids: dict[str, int] = Field(default_factory=dict, alias="yes_bids")
    no_bids: dict[str, int] = Field(default_factory=dict, alias="no_bids")
    sequence: int = 0

    model_config = {"populate_by_name": True}

    def get_yes_levels(self) -> list[OrderbookLevel]:
        """Convert yes_bids dict to list of OrderbookLevel objects."""
        return [
            OrderbookLevel(price=float(price), quantity=float(qty))
            for price, qty in sorted(self.yes_bids.items(), key=lambda x: float(x[0]), reverse=True)
        ]

    def get_no_levels(self) -> list[OrderbookLevel]:
        """Convert no_bids dict to list of OrderbookLevel objects."""
        return [
            OrderbookLevel(price=float(price), quantity=float(qty))
            for price, qty in sorted(self.no_bids.items(), key=lambda x: float(x[0]), reverse=True)
        ]

    @property
    def yes_bid(self) -> list[OrderbookLevel]:
        """Backwards-compatible alias for get_yes_levels()."""
        return self.get_yes_levels()

    @property
    def no_bid(self) -> list[OrderbookLevel]:
        """Backwards-compatible alias for get_no_levels()."""
        return self.get_no_levels()

    @property
    def timestamp(self) -> int:
        """Backwards-compatible alias for sequence."""
        return self.sequence
