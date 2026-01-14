"""Prediction Market API for DFlow SDK."""

from dflow.types import PredictionMarketInitResponse
from dflow.utils.constants import USDC_MINT
from dflow.utils.http import HttpClient


class PredictionMarketAPI:
    """API for initializing new prediction markets.

    Create new prediction markets on-chain. This initializes the market
    accounts and creates YES/NO outcome token mints.

    Example:
        >>> dflow = DFlowClient(environment="production", api_key="your-key")
        >>>
        >>> init = dflow.prediction_market.initialize_market(
        ...     market_ticker="MY-MARKET-TICKER",
        ...     user_public_key=str(wallet.pubkey()),
        ... )
        >>>
        >>> print(f"YES mint: {init.yes_mint}")
        >>> print(f"NO mint: {init.no_mint}")
        >>> # Sign and send init.transaction to create the market
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def initialize_market(
        self,
        market_ticker: str,
        user_public_key: str,
        settlement_mint: str | None = None,
    ) -> PredictionMarketInitResponse:
        """Initialize a new prediction market.

        Creates a new prediction market with YES and NO outcome tokens.
        The returned transaction must be signed and sent to complete
        market creation.

        Args:
            market_ticker: Unique ticker for the new market
            user_public_key: The creator's Solana wallet public key
            settlement_mint: Token mint for settlement (defaults to USDC)

        Returns:
            Initialization response with transaction and mint addresses

        Example:
            >>> from dflow import USDC_MINT
            >>>
            >>> init = dflow.prediction_market.initialize_market(
            ...     market_ticker="BTCPRICE-25DEC-100K",
            ...     user_public_key=str(wallet.pubkey()),
            ...     settlement_mint=USDC_MINT,  # Optional, defaults to USDC
            ... )
            >>>
            >>> # Sign and send the initialization transaction
            >>> # result = sign_send_and_confirm(connection, init.transaction, keypair)
            >>>
            >>> print(f"Market created!")
            >>> print(f"YES token: {init.yes_mint}")
            >>> print(f"NO token: {init.no_mint}")
        """
        data = self._http.get(
            "/prediction-market-init",
            {
                "marketTicker": market_ticker,
                "userPublicKey": user_public_key,
                "settlementMint": settlement_mint or USDC_MINT,
            },
        )
        return PredictionMarketInitResponse.model_validate(data)
