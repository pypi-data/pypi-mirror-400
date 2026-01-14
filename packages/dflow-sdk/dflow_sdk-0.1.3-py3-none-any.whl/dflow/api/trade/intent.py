"""Intent API for DFlow SDK."""

from typing import Literal

from dflow.types import IntentQuote, IntentResponse, PriorityFeeConfig
from dflow.utils.http import HttpClient


class IntentAPI:
    """API for declarative intent-based swaps.

    Intents provide a declarative approach to trading where you specify
    what you want (exact input or exact output) and the system handles
    the execution details. This is useful for "sell exactly X" or
    "buy exactly Y" scenarios.

    Example:
        >>> from dflow import DFlowClient, USDC_MINT
        >>>
        >>> dflow = DFlowClient()
        >>>
        >>> # ExactIn: Sell exactly 1 USDC, receive variable YES tokens
        >>> intent = dflow.intent.submit_intent(
        ...     input_mint=USDC_MINT,
        ...     output_mint=yes_mint,
        ...     amount=1000000,
        ...     mode="ExactIn",
        ...     slippage_bps=50,
        ...     user_public_key=str(wallet.pubkey()),
        ... )
        >>>
        >>> # ExactOut: Receive exactly 100 YES tokens, pay variable USDC
        >>> intent = dflow.intent.submit_intent(
        ...     input_mint=USDC_MINT,
        ...     output_mint=yes_mint,
        ...     amount=100000000,
        ...     mode="ExactOut",
        ...     slippage_bps=50,
        ...     user_public_key=str(wallet.pubkey()),
        ... )
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def get_intent_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int | str,
        mode: Literal["ExactIn", "ExactOut"],
    ) -> IntentQuote:
        """Get a quote for an intent-based swap.

        Preview what you'll receive (ExactIn) or what you'll pay (ExactOut)
        before submitting the intent.

        Args:
            input_mint: The mint address of the token to sell
            output_mint: The mint address of the token to buy
            amount: The exact amount (input or output based on mode)
            mode: 'ExactIn' to specify input amount, 'ExactOut' for output amount

        Returns:
            Quote showing expected amounts

        Example:
            >>> # How much YES will I get for exactly 1 USDC?
            >>> quote = dflow.intent.get_intent_quote(
            ...     input_mint=USDC_MINT,
            ...     output_mint=yes_mint,
            ...     amount=1000000,
            ...     mode="ExactIn",
            ... )
            >>> print(f"You'll receive: {quote.out_amount} YES tokens")
            >>>
            >>> # How much USDC do I need to get exactly 100 YES tokens?
            >>> quote = dflow.intent.get_intent_quote(
            ...     input_mint=USDC_MINT,
            ...     output_mint=yes_mint,
            ...     amount=100000000,
            ...     mode="ExactOut",
            ... )
            >>> print(f"You'll pay: {quote.in_amount} USDC")
        """
        data = self._http.get(
            "/intent",
            {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "mode": mode,
            },
        )
        return IntentQuote.model_validate(data)

    def submit_intent(
        self,
        input_mint: str,
        output_mint: str,
        amount: int | str,
        mode: Literal["ExactIn", "ExactOut"],
        user_public_key: str,
        slippage_bps: int | None = None,
        priority_fee: PriorityFeeConfig | None = None,
    ) -> IntentResponse:
        """Submit an intent-based swap for execution.

        Creates and returns a transaction for the intent. The transaction
        will execute the swap according to the specified mode (ExactIn/ExactOut).

        Args:
            input_mint: The mint address of the token to sell
            output_mint: The mint address of the token to buy
            amount: The exact amount (input or output based on mode)
            mode: 'ExactIn' or 'ExactOut'
            user_public_key: The user's Solana wallet public key
            slippage_bps: Slippage tolerance in basis points
            priority_fee: Optional priority fee configuration

        Returns:
            Intent response with transaction to sign

        Example:
            >>> intent = dflow.intent.submit_intent(
            ...     input_mint=USDC_MINT,
            ...     output_mint=market.accounts["usdc"].yes_mint,
            ...     amount=1000000,
            ...     mode="ExactIn",
            ...     slippage_bps=50,
            ...     user_public_key=str(wallet.pubkey()),
            ... )
            >>> # Sign and send intent.transaction
        """
        # First get a quote
        quote_response = self.get_intent_quote(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=amount,
            mode=mode,
        )

        # Build request body
        body: dict = {
            "quoteResponse": quote_response.model_dump(by_alias=True),
            "userPublicKey": user_public_key,
        }
        if slippage_bps is not None:
            body["slippageBps"] = slippage_bps
        if priority_fee is not None:
            body["priorityFee"] = priority_fee.model_dump()

        data = self._http.post("/submit-intent", body)
        return IntentResponse.model_validate(data)
