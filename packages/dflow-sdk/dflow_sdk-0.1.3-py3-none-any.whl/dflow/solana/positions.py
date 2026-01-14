"""Position tracking utilities for DFlow SDK."""

from solana.rpc.api import Client
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_2022_PROGRAM_ID, TOKEN_PROGRAM_ID

from dflow.api.metadata.markets import MarketsAPI
from dflow.types import Market, TokenBalance, UserPosition


def get_token_balances(
    connection: Client,
    wallet_address: Pubkey,
) -> list[TokenBalance]:
    """Get all token balances for a wallet.

    Queries both the standard Token Program and Token-2022 Program to find
    all token holdings. Returns only tokens with non-zero balances.

    Args:
        connection: Solana RPC connection
        wallet_address: Wallet public key to query

    Returns:
        Array of token balances with mint, balance, and decimal info

    Example:
        >>> from solana.rpc.api import Client
        >>> from solders.pubkey import Pubkey
        >>> from dflow import get_token_balances
        >>>
        >>> connection = Client("https://api.mainnet-beta.solana.com")
        >>> wallet = Pubkey.from_string("...")
        >>>
        >>> balances = get_token_balances(connection, wallet)
        >>> for token in balances:
        ...     print(f"{token.mint}: {token.balance} ({token.decimals} decimals)")
    """
    # Query both Token Program and Token-2022 Program
    token_accounts = connection.get_token_accounts_by_owner(
        wallet_address,
        {"programId": TOKEN_PROGRAM_ID},
    )
    token_2022_accounts = connection.get_token_accounts_by_owner(
        wallet_address,
        {"programId": TOKEN_2022_PROGRAM_ID},
    )

    all_accounts = list(token_accounts.value) + list(token_2022_accounts.value)

    balances = []
    for account in all_accounts:
        # Parse the account data
        try:
            data = account.account.data
            if hasattr(data, "parsed"):
                info = data.parsed["info"]
                ui_amount = info["tokenAmount"]["uiAmount"]
                if ui_amount and ui_amount > 0:
                    balances.append(
                        TokenBalance(
                            mint=info["mint"],
                            raw_balance=info["tokenAmount"]["amount"],
                            balance=ui_amount,
                            decimals=info["tokenAmount"]["decimals"],
                        )
                    )
        except (KeyError, AttributeError):
            continue

    return balances


def get_user_positions(
    connection: Client,
    wallet_address: Pubkey,
    markets_api: MarketsAPI,
) -> list[UserPosition]:
    """Get a user's prediction market positions.

    Finds all prediction market outcome tokens in a wallet and enriches them
    with market data and position type (YES/NO).

    Args:
        connection: Solana RPC connection
        wallet_address: Wallet public key to query
        markets_api: Markets API instance for looking up market data

    Returns:
        Array of user positions with market context

    Example:
        >>> from solana.rpc.api import Client
        >>> from solders.pubkey import Pubkey
        >>> from dflow import DFlowClient, get_user_positions
        >>>
        >>> dflow = DFlowClient()
        >>> connection = Client("https://api.mainnet-beta.solana.com")
        >>> wallet = Pubkey.from_string("...")
        >>>
        >>> positions = get_user_positions(connection, wallet, dflow.markets)
        >>> for pos in positions:
        ...     print(f"{pos.position} position: {pos.balance} tokens")
        ...     if pos.market:
        ...         print(f"  Market: {pos.market.title}")
    """
    token_balances = get_token_balances(connection, wallet_address)

    if not token_balances:
        return []

    all_mints = [t.mint for t in token_balances]
    prediction_mints = markets_api.filter_outcome_mints(all_mints)

    if not prediction_mints:
        return []

    outcome_tokens = [t for t in token_balances if t.mint in prediction_mints]
    markets = markets_api.get_markets_batch(mints=prediction_mints)

    # Build lookup map
    markets_by_mint: dict[str, Market] = {}
    for market in markets:
        for account in market.accounts.values():
            markets_by_mint[account.yes_mint] = market
            markets_by_mint[account.no_mint] = market
            markets_by_mint[account.market_ledger] = market

    positions = []
    for token in outcome_tokens:
        market = markets_by_mint.get(token.mint)

        if not market:
            positions.append(
                UserPosition(
                    mint=token.mint,
                    balance=token.balance,
                    decimals=token.decimals,
                    position="UNKNOWN",
                    market=None,
                )
            )
            continue

        is_yes_token = any(
            account.yes_mint == token.mint for account in market.accounts.values()
        )
        is_no_token = any(
            account.no_mint == token.mint for account in market.accounts.values()
        )

        positions.append(
            UserPosition(
                mint=token.mint,
                balance=token.balance,
                decimals=token.decimals,
                position="YES" if is_yes_token else "NO" if is_no_token else "UNKNOWN",
                market=market,
            )
        )

    return positions


def is_redemption_eligible(market: Market, outcome_mint: str) -> bool:
    """Check if a position is eligible for redemption.

    A position is eligible if:
    - The market is 'determined' or 'finalized'
    - The redemption window is open
    - The position is on the winning side (or it's a scalar market)

    Args:
        market: The market data
        outcome_mint: The mint address of the outcome token to check

    Returns:
        True if the position can be redeemed

    Example:
        >>> from dflow import is_redemption_eligible
        >>>
        >>> positions = get_user_positions(connection, wallet, dflow.markets)
        >>> for pos in positions:
        ...     if pos.market and is_redemption_eligible(pos.market, pos.mint):
        ...         print(f"Position {pos.mint} is redeemable!")
    """
    if market.status not in ("determined", "finalized"):
        return False

    for account in market.accounts.values():
        if account.redemption_status != "open":
            continue

        is_winning_yes = market.result == "yes" and account.yes_mint == outcome_mint
        is_winning_no = market.result == "no" and account.no_mint == outcome_mint
        is_scalar_outcome = (
            market.result == ""
            and account.scalar_outcome_pct is not None
            and (account.yes_mint == outcome_mint or account.no_mint == outcome_mint)
        )

        if is_winning_yes or is_winning_no or is_scalar_outcome:
            return True

    return False


def calculate_scalar_payout(
    market: Market,
    outcome_mint: str,
    amount: float,
) -> float:
    """Calculate the payout for a scalar market position.

    Scalar markets pay out based on where the outcome falls within a range.
    YES tokens pay the outcome percentage, NO tokens pay the inverse.

    Args:
        market: The market data
        outcome_mint: The mint address of the outcome token
        amount: The number of tokens held

    Returns:
        The payout amount in settlement tokens

    Example:
        >>> from dflow import calculate_scalar_payout, is_redemption_eligible
        >>>
        >>> for pos in positions:
        ...     if pos.market and is_redemption_eligible(pos.market, pos.mint):
        ...         payout = calculate_scalar_payout(pos.market, pos.mint, pos.balance)
        ...         print(f"Expected payout: {payout} USDC")
    """
    for account in market.accounts.values():
        if account.scalar_outcome_pct is None:
            continue

        if account.yes_mint == outcome_mint:
            return (amount * account.scalar_outcome_pct) / 10000

        if account.no_mint == outcome_mint:
            return (amount * (10000 - account.scalar_outcome_pct)) / 10000

    return 0.0
