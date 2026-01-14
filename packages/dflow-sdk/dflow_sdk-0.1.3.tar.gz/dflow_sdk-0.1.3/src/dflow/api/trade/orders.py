"""Orders API for DFlow SDK."""

from dflow.types import OrderResponse, OrderStatusResponse
from dflow.utils.http import HttpClient


class OrdersAPI:
    """API for creating and tracking orders.

    Orders provide a way to get a quote and transaction for trading
    prediction market outcome tokens. Use this for straightforward
    order execution.

    Example:
        >>> from dflow import DFlowClient, USDC_MINT
        >>>
        >>> dflow = DFlowClient(environment="production", api_key="your-key")
        >>>
        >>> # Get an order quote and transaction
        >>> order = dflow.orders.get_order(
        ...     input_mint=USDC_MINT,
        ...     output_mint=market.accounts["usdc"].yes_mint,
        ...     amount=1000000,
        ...     slippage_bps=50,
        ...     user_public_key=str(wallet.pubkey()),
        ... )
        >>>
        >>> # Sign and send the transaction, then check status
        >>> status = dflow.orders.get_order_status(signature)
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def get_order(
        self,
        input_mint: str,
        output_mint: str,
        amount: int | str,
        slippage_bps: int,
        user_public_key: str,
        platform_fee_bps: int | None = None,
        platform_fee_account: str | None = None,
    ) -> OrderResponse:
        """Get an order quote and transaction for a trade.

        Returns a ready-to-sign transaction for swapping tokens.

        Args:
            input_mint: The mint address of the token to sell (e.g., USDC)
            output_mint: The mint address of the token to buy (e.g., YES token)
            amount: The amount to trade in base units (e.g., 1000000 for 1 USDC)
            slippage_bps: Maximum slippage in basis points (e.g., 50 = 0.5%)
            user_public_key: The user's Solana wallet public key
            platform_fee_bps: Optional platform fee in basis points
            platform_fee_account: Optional account to receive platform fees

        Returns:
            Order response with transaction and quote details

        Example:
            >>> from dflow import USDC_MINT
            >>>
            >>> order = dflow.orders.get_order(
            ...     input_mint=USDC_MINT,
            ...     output_mint=market.accounts["usdc"].yes_mint,
            ...     amount=1000000,  # 1 USDC (6 decimals)
            ...     slippage_bps=50,  # 0.5% slippage
            ...     user_public_key=str(wallet.pubkey()),
            ... )
            >>> print(f"Input: {order.in_amount}, Output: {order.out_amount}")
        """
        data = self._http.get(
            "/order",
            {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": slippage_bps,
                "userPublicKey": user_public_key,
                "platformFeeBps": platform_fee_bps,
                "platformFeeAccount": platform_fee_account,
            },
        )
        return OrderResponse.model_validate(data)

    def get_order_status(self, signature: str) -> OrderStatusResponse:
        """Check the status of a submitted order.

        Use this to track async order completion or check if an order
        was successfully executed.

        Args:
            signature: The transaction signature from submitting the order

        Returns:
            Order status ('open', 'closed', 'failed', or 'pendingClose')

        Example:
            >>> status = dflow.orders.get_order_status(signature)
            >>> if status.status == "closed":
            ...     print("Order completed successfully!")
            >>> elif status.status == "failed":
            ...     print(f"Order failed: {status.error}")
        """
        data = self._http.get("/order-status", {"signature": signature})
        return OrderStatusResponse.model_validate(data)
