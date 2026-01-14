"""Orderbook API for DFlow SDK."""

from dflow.types import Orderbook
from dflow.utils.http import HttpClient


class OrderbookAPI:
    """API for retrieving orderbook snapshots.

    The orderbook shows current bid/ask prices and quantities for YES and NO
    outcome tokens in a market.

    Example:
        >>> dflow = DFlowClient()
        >>> orderbook = dflow.orderbook.get_orderbook("BTCD-25DEC0313-T92749.99")
        >>> print(f"YES Bid: {orderbook.yes_bid[0].price}")
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def get_orderbook(self, market_ticker: str) -> Orderbook:
        """Get the orderbook for a market by ticker.

        Args:
            market_ticker: The market ticker

        Returns:
            Orderbook with YES/NO bid and ask prices and quantities

        Example:
            >>> orderbook = dflow.orderbook.get_orderbook("BTCD-25DEC0313-T92749.99")
            >>> print(f"YES: Bid {orderbook.yes_bid[0].price} / Ask {orderbook.yes_ask[0].price}")
            >>> print(f"NO:  Bid {orderbook.no_bid[0].price} / Ask {orderbook.no_ask[0].price}")
        """
        data = self._http.get(f"/orderbook/{market_ticker}")
        return Orderbook.model_validate(data)

    def get_orderbook_by_mint(self, mint_address: str) -> Orderbook:
        """Get the orderbook for a market by mint address.

        Alternative to get_orderbook when you have the mint address.

        Args:
            mint_address: The Solana mint address of the market's outcome token

        Returns:
            Orderbook with YES/NO bid and ask prices and quantities
        """
        data = self._http.get(f"/orderbook/by-mint/{mint_address}")
        return Orderbook.model_validate(data)
