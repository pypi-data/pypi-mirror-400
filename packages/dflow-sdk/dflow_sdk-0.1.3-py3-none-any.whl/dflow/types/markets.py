"""Market types for DFlow SDK."""

from typing import Literal

from pydantic import BaseModel, Field

MarketStatus = Literal[
    "initialized", "active", "inactive", "closed", "determined", "finalized"
]
MarketResult = Literal["yes", "no", ""]
RedemptionStatus = Literal["open", "closed", "pending"]
MarketType = Literal["binary", "scalar"]


class MarketAccount(BaseModel):
    """Market account information for a specific settlement token."""

    yes_mint: str = Field(alias="yesMint")
    no_mint: str = Field(alias="noMint")
    market_ledger: str = Field(alias="marketLedger")
    is_initialized: bool = Field(default=False, alias="isInitialized")
    redemption_status: RedemptionStatus | None = Field(default=None, alias="redemptionStatus")
    scalar_outcome_pct: int | None = Field(default=None, alias="scalarOutcomePct")

    model_config = {"populate_by_name": True}


class Market(BaseModel):
    """Prediction market data."""

    ticker: str
    title: str
    subtitle: str | None = None
    event_ticker: str = Field(alias="eventTicker")
    market_type: MarketType | None = Field(default=None, alias="marketType")
    status: MarketStatus
    result: MarketResult
    
    # Price fields - API returns bid/ask as strings like "0.3500"
    yes_bid: str | None = Field(default=None, alias="yesBid")
    yes_ask: str | None = Field(default=None, alias="yesAsk")
    no_bid: str | None = Field(default=None, alias="noBid")
    no_ask: str | None = Field(default=None, alias="noAsk")
    
    # Subtitles
    yes_sub_title: str | None = Field(default=None, alias="yesSubTitle")
    no_sub_title: str | None = Field(default=None, alias="noSubTitle")
    
    # Volume and interest
    volume: float | None = None
    volume_24h: float | None = Field(default=None, alias="volume24h")
    open_interest: float | None = Field(default=None, alias="openInterest")
    liquidity: float | None = None
    
    # Timestamps
    open_time: str | int | None = Field(default=None, alias="openTime")
    close_time: str | int | None = Field(default=None, alias="closeTime")
    expiration_time: str | int | None = Field(default=None, alias="expirationTime")
    
    # Rules
    rules_primary: str | None = Field(default=None, alias="rulesPrimary")
    rules_secondary: str | None = Field(default=None, alias="rulesSecondary")
    can_close_early: bool | None = Field(default=None, alias="canCloseEarly")
    early_close_condition: str | None = Field(default=None, alias="earlyCloseCondition")
    
    # Accounts
    accounts: dict[str, MarketAccount]

    model_config = {"populate_by_name": True}

    # Backwards-compatible properties
    @property
    def yes_price(self) -> float | None:
        """Get YES price (uses yes_bid as the price)."""
        if self.yes_bid:
            return float(self.yes_bid)
        return None

    @property
    def no_price(self) -> float | None:
        """Get NO price (uses no_bid as the price)."""
        if self.no_bid:
            return float(self.no_bid)
        return None

    @property
    def rules(self) -> str | None:
        """Backwards-compatible alias for rules_primary."""
        return self.rules_primary


class MarketsResponse(BaseModel):
    """Response from markets list endpoint."""

    cursor: str | int | None = None
    markets: list[Market]


class MarketsBatchParams(BaseModel):
    """Parameters for batch market queries."""

    tickers: list[str] | None = None
    mints: list[str] | None = None


class MarketsBatchResponse(BaseModel):
    """Response from batch markets endpoint."""

    markets: list[Market]


class FilterOutcomeMintsParams(BaseModel):
    """Parameters for filtering outcome mints."""

    addresses: list[str]


class FilterOutcomeMintsResponse(BaseModel):
    """Response from filter outcome mints endpoint."""

    outcome_mints: list[str] = Field(alias="outcomeMints")

    model_config = {"populate_by_name": True}
