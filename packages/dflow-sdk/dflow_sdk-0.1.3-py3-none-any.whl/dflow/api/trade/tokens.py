"""Tokens API for DFlow SDK."""

from dflow.utils.http import HttpClient


class TokenMintWithDecimals:
    """Token mint address with decimal information."""

    def __init__(self, mint: str, decimals: int):
        self.mint = mint
        self.decimals = decimals

    def __repr__(self) -> str:
        return f"TokenMintWithDecimals(mint='{self.mint}', decimals={self.decimals})"


class TokensAPI:
    """API for retrieving available token information.

    Get information about tokens supported for trading, including
    their mint addresses and decimal precision.

    Example:
        >>> dflow = DFlowClient()
        >>> tokens = dflow.tokens.get_tokens()
        >>> for mint in tokens[:5]:
        ...     print(f"Mint: {mint}")
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def get_tokens(self) -> list[str]:
        """Get all available token mint addresses for trading.

        Returns:
            List of token mint addresses (Solana public keys)

        Example:
            >>> mints = dflow.tokens.get_tokens()
            >>> print(f"Found {len(mints)} tokens")
        """
        data = self._http.get("/tokens")
        return data

    def get_tokens_with_decimals(self) -> list[TokenMintWithDecimals]:
        """Get all available tokens with decimal information.

        Note: The API returns a list of [mint, decimals] tuples.

        Returns:
            List of TokenMintWithDecimals objects

        Example:
            >>> tokens = dflow.tokens.get_tokens_with_decimals()
            >>> for token in tokens[:5]:
            ...     print(f"{token.mint}: {token.decimals} decimals")
        """
        data = self._http.get("/tokens-with-decimals")
        return [TokenMintWithDecimals(mint=item[0], decimals=item[1]) for item in data]
