"""Solana-related types for DFlow SDK."""

from typing import Literal

from pydantic import BaseModel

from .markets import Market

PositionType = Literal["YES", "NO", "UNKNOWN"]
ConfirmationStatus = Literal["processed", "confirmed", "finalized"]


class TokenBalance(BaseModel):
    """Token balance information."""

    mint: str
    raw_balance: str
    balance: float
    decimals: int


class UserPosition(BaseModel):
    """User's position in a prediction market."""

    mint: str
    balance: float
    decimals: int
    position: PositionType
    market: Market | None


class RedemptionResult(BaseModel):
    """Result of a redemption operation."""

    signature: str
    input_amount: str
    output_amount: str
    outcome_mint: str
    settlement_mint: str


class TransactionConfirmation(BaseModel):
    """Transaction confirmation details."""

    signature: str
    slot: int
    confirmation_status: ConfirmationStatus
    err: str | None = None
