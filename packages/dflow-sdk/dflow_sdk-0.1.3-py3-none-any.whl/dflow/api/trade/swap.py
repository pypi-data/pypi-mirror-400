"""Swap API for DFlow SDK."""

from dflow.types import PriorityFeeConfig, SwapInstructionsResponse, SwapQuote, SwapResponse
from dflow.utils.http import HttpClient


class SwapAPI:
    """API for imperative swap operations with route preview.

    The Swap API provides a two-step process: first get a quote to preview
    the trade, then create a swap transaction. This gives you control over
    trade execution and allows displaying quotes to users before committing.

    Example:
        >>> from dflow import DFlowClient, USDC_MINT
        >>>
        >>> dflow = DFlowClient()
        >>>
        >>> # Step 1: Get a quote
        >>> quote = dflow.swap.get_quote(
        ...     input_mint=USDC_MINT,
        ...     output_mint=yes_mint,
        ...     amount=1000000,
        ... )
        >>> print(f"You'll receive: {quote.out_amount} tokens")
        >>>
        >>> # Step 2: Create and execute swap
        >>> swap = dflow.swap.create_swap(
        ...     input_mint=USDC_MINT,
        ...     output_mint=yes_mint,
        ...     amount=1000000,
        ...     slippage_bps=50,
        ...     user_public_key=str(wallet.pubkey()),
        ... )
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int | str,
        slippage_bps: int | None = None,
    ) -> SwapQuote:
        """Get a quote for a swap without creating a transaction.

        Use this to preview trade amounts before committing. The quote
        shows expected input/output amounts and price impact.

        Args:
            input_mint: The mint address of the token to sell
            output_mint: The mint address of the token to buy
            amount: The amount to trade in base units
            slippage_bps: Optional slippage tolerance in basis points

        Returns:
            Quote with expected amounts and route information

        Example:
            >>> quote = dflow.swap.get_quote(
            ...     input_mint=USDC_MINT,
            ...     output_mint=market.accounts["usdc"].yes_mint,
            ...     amount=1000000,  # 1 USDC
            ...     slippage_bps=50,
            ... )
            >>> print(f"Input: {quote.in_amount}")
            >>> print(f"Output: {quote.out_amount}")
            >>> print(f"Price impact: {quote.price_impact_pct}%")
        """
        data = self._http.get(
            "/quote",
            {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": slippage_bps,
            },
        )
        return SwapQuote.model_validate(data)

    def create_swap(
        self,
        input_mint: str,
        output_mint: str,
        amount: int | str,
        slippage_bps: int,
        user_public_key: str,
        wrap_unwrap_sol: bool | None = None,
        priority_fee: PriorityFeeConfig | None = None,
    ) -> SwapResponse:
        """Create a swap transaction ready for signing.

        Combines getting a quote and creating a transaction in one call.
        Returns a base64-encoded transaction that can be signed and sent.

        Args:
            input_mint: The mint address of the token to sell
            output_mint: The mint address of the token to buy
            amount: The amount to trade in base units
            slippage_bps: Slippage tolerance in basis points
            user_public_key: The user's Solana wallet public key
            wrap_unwrap_sol: Whether to wrap/unwrap SOL automatically
            priority_fee: Optional priority fee configuration

        Returns:
            Swap response with transaction and quote details

        Example:
            >>> swap = dflow.swap.create_swap(
            ...     input_mint=USDC_MINT,
            ...     output_mint=market.accounts["usdc"].yes_mint,
            ...     amount=1000000,
            ...     slippage_bps=50,
            ...     user_public_key=str(wallet.pubkey()),
            ...     wrap_unwrap_sol=True,
            ...     priority_fee=PriorityFeeConfig(type="exact", amount=10000),
            ... )
            >>> # Sign and send swap.swap_transaction
        """
        # First get a quote
        quote_response = self.get_quote(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=amount,
            slippage_bps=slippage_bps,
        )

        # Build request body
        body: dict = {
            "quoteResponse": quote_response.model_dump(by_alias=True),
            "userPublicKey": user_public_key,
        }
        if wrap_unwrap_sol is not None:
            body["wrapUnwrapSol"] = wrap_unwrap_sol
        if priority_fee is not None:
            body["priorityFee"] = priority_fee.model_dump()

        data = self._http.post("/swap", body)
        return SwapResponse.model_validate(data)

    def get_swap_instructions(
        self,
        input_mint: str,
        output_mint: str,
        amount: int | str,
        slippage_bps: int,
        user_public_key: str,
        wrap_unwrap_sol: bool | None = None,
        priority_fee: PriorityFeeConfig | None = None,
    ) -> SwapInstructionsResponse:
        """Get swap instructions for custom transaction composition.

        Instead of a complete transaction, returns individual instructions
        that can be combined with other instructions in a custom transaction.
        Useful for advanced use cases like atomic multi-step operations.

        Args:
            input_mint: The mint address of the token to sell
            output_mint: The mint address of the token to buy
            amount: The amount to trade in base units
            slippage_bps: Slippage tolerance in basis points
            user_public_key: The user's Solana wallet public key
            wrap_unwrap_sol: Whether to wrap/unwrap SOL automatically
            priority_fee: Optional priority fee configuration

        Returns:
            Instructions and accounts for building a custom transaction
        """
        # First get a quote
        quote_response = self.get_quote(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=amount,
            slippage_bps=slippage_bps,
        )

        # Build request body
        body: dict = {
            "quoteResponse": quote_response.model_dump(by_alias=True),
            "userPublicKey": user_public_key,
        }
        if wrap_unwrap_sol is not None:
            body["wrapUnwrapSol"] = wrap_unwrap_sol
        if priority_fee is not None:
            body["priorityFee"] = priority_fee.model_dump()

        data = self._http.post("/swap-instructions", body)
        return SwapInstructionsResponse.model_validate(data)
