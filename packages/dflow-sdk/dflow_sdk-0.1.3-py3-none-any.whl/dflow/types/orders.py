"""Order types for DFlow SDK."""

from typing import Literal

from pydantic import BaseModel, Field

ExecutionMode = Literal["sync", "async"]
OrderStatusType = Literal["open", "closed", "failed", "pendingClose"]
IntentMode = Literal["ExactIn", "ExactOut"]
PriorityFeeType = Literal["exact", "max"]


class PriorityFeeConfig(BaseModel):
    """Priority fee configuration for transactions."""

    type: PriorityFeeType
    amount: int


class OrderParams(BaseModel):
    """Parameters for creating an order."""

    input_mint: str = Field(alias="inputMint")
    output_mint: str = Field(alias="outputMint")
    amount: int | str
    slippage_bps: int = Field(alias="slippageBps")
    user_public_key: str = Field(alias="userPublicKey")
    platform_fee_bps: int | None = Field(default=None, alias="platformFeeBps")
    platform_fee_account: str | None = Field(default=None, alias="platformFeeAccount")

    model_config = {"populate_by_name": True}


class OrderResponse(BaseModel):
    """Response from order creation."""

    transaction: str
    in_amount: str = Field(alias="inAmount")
    out_amount: str = Field(alias="outAmount")
    execution_mode: ExecutionMode = Field(alias="executionMode")
    price_impact_pct: float | None = Field(default=None, alias="priceImpactPct")

    model_config = {"populate_by_name": True}


class OrderFill(BaseModel):
    """Information about a filled order."""

    input_mint: str = Field(alias="inputMint")
    output_mint: str = Field(alias="outputMint")
    in_amount: str = Field(alias="inAmount")
    out_amount: str = Field(alias="outAmount")
    price: float
    timestamp: str | int

    model_config = {"populate_by_name": True}


class OrderStatusResponse(BaseModel):
    """Response from order status query."""

    status: OrderStatusType
    signature: str
    in_amount: str | None = Field(default=None, alias="inAmount")
    out_amount: str | None = Field(default=None, alias="outAmount")
    fills: list[OrderFill] | None = None
    error: str | None = None

    model_config = {"populate_by_name": True}


class SwapInfo(BaseModel):
    """Swap information in a route plan step."""

    amm_key: str = Field(alias="ammKey")
    label: str
    input_mint: str = Field(alias="inputMint")
    output_mint: str = Field(alias="outputMint")
    in_amount: str = Field(alias="inAmount")
    out_amount: str = Field(alias="outAmount")
    fee_amount: str = Field(alias="feeAmount")
    fee_mint: str = Field(alias="feeMint")

    model_config = {"populate_by_name": True}


class RoutePlanStep(BaseModel):
    """Step in a swap route plan."""

    swap_info: SwapInfo = Field(alias="swapInfo")
    percent: int

    model_config = {"populate_by_name": True}


class SwapQuote(BaseModel):
    """Quote for a swap operation."""

    input_mint: str = Field(alias="inputMint")
    output_mint: str = Field(alias="outputMint")
    in_amount: str = Field(alias="inAmount")
    out_amount: str = Field(alias="outAmount")
    price_impact_pct: float = Field(alias="priceImpactPct")
    route_plan: list[RoutePlanStep] | None = Field(default=None, alias="routePlan")

    model_config = {"populate_by_name": True}


class SwapResponse(BaseModel):
    """Response from swap creation."""

    swap_transaction: str = Field(alias="swapTransaction")
    last_valid_block_height: int | None = Field(
        default=None, alias="lastValidBlockHeight"
    )
    prioritization_fee_lamports: int | None = Field(
        default=None, alias="prioritizationFeeLamports"
    )
    compute_unit_limit: int | None = Field(default=None, alias="computeUnitLimit")
    prioritization_type: str | None = Field(default=None, alias="prioritizationType")
    quote: SwapQuote | None = None

    model_config = {"populate_by_name": True}


class SerializedAccountMeta(BaseModel):
    """Account metadata for a serialized instruction."""

    pubkey: str
    is_signer: bool = Field(alias="isSigner")
    is_writable: bool = Field(alias="isWritable")

    model_config = {"populate_by_name": True}


class SerializedInstruction(BaseModel):
    """Serialized Solana instruction."""

    program_id: str = Field(alias="programId")
    accounts: list[SerializedAccountMeta]
    data: str

    model_config = {"populate_by_name": True}


class SwapInstructionsResponse(BaseModel):
    """Response containing swap instructions for custom transaction building."""

    setup_instructions: list[SerializedInstruction] = Field(alias="setupInstructions")
    swap_instruction: SerializedInstruction = Field(alias="swapInstruction")
    cleanup_instruction: SerializedInstruction | None = Field(
        default=None, alias="cleanupInstruction"
    )
    address_lookup_table_addresses: list[str] = Field(
        alias="addressLookupTableAddresses"
    )

    model_config = {"populate_by_name": True}


class IntentQuote(BaseModel):
    """Quote for an intent-based swap."""

    input_mint: str = Field(alias="inputMint")
    output_mint: str = Field(alias="outputMint")
    in_amount: str = Field(alias="inAmount")
    out_amount: str = Field(alias="outAmount")
    min_out_amount: str = Field(alias="minOutAmount")
    max_in_amount: str = Field(alias="maxInAmount")
    expires_at: str = Field(alias="expiresAt")

    model_config = {"populate_by_name": True}


class IntentResponse(BaseModel):
    """Response from intent submission."""

    transaction: str
    intent_id: str = Field(alias="intentId")
    quote: IntentQuote

    model_config = {"populate_by_name": True}


class PredictionMarketInitResponse(BaseModel):
    """Response from prediction market initialization."""

    transaction: str
    yes_mint: str = Field(alias="yesMint")
    no_mint: str = Field(alias="noMint")

    model_config = {"populate_by_name": True}
