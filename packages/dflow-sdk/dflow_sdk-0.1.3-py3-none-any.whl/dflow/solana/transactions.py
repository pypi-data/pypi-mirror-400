"""Solana transaction utilities for DFlow SDK."""

import asyncio
import base64
import time
from typing import Literal

from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

from dflow.types import TransactionConfirmation

Commitment = Literal["processed", "confirmed", "finalized"]


def sign_and_send_transaction(
    connection: Client,
    transaction_base64: str,
    signer: Keypair,
) -> str:
    """Sign and send a base64-encoded transaction to the Solana network.

    Deserializes the transaction, signs it with the provided keypair,
    and sends it to the network.

    Args:
        connection: Solana RPC connection
        transaction_base64: Base64-encoded transaction (from DFlow API responses)
        signer: Keypair to sign the transaction with

    Returns:
        Transaction signature

    Example:
        >>> from solana.rpc.api import Client
        >>> from solders.keypair import Keypair
        >>> from dflow import sign_and_send_transaction
        >>>
        >>> connection = Client("https://api.mainnet-beta.solana.com")
        >>> keypair = Keypair.from_bytes(secret_key)
        >>>
        >>> order = dflow.orders.get_order(...)
        >>> signature = sign_and_send_transaction(connection, order.transaction, keypair)
        >>> print(f"Transaction sent: {signature}")
    """
    # Decode base64 transaction
    transaction_buffer = base64.b64decode(transaction_base64)
    transaction = VersionedTransaction.from_bytes(transaction_buffer)

    # Sign with keypair
    transaction.sign([signer])

    # Send transaction
    result = connection.send_transaction(transaction)

    return str(result.value)


def wait_for_confirmation(
    connection: Client,
    signature: str,
    commitment: Commitment = "confirmed",
    timeout_ms: int = 60000,
) -> TransactionConfirmation:
    """Wait for a transaction to be confirmed on-chain.

    Polls the network until the transaction reaches the desired confirmation
    level or times out.

    Args:
        connection: Solana RPC connection
        signature: Transaction signature to wait for
        commitment: Desired confirmation level (default: 'confirmed')
        timeout_ms: Maximum time to wait in milliseconds (default: 60000)

    Returns:
        Confirmation details including slot and status

    Raises:
        Exception: If transaction fails or times out

    Example:
        >>> from dflow import wait_for_confirmation
        >>>
        >>> confirmation = wait_for_confirmation(connection, signature, "confirmed")
        >>> print(f"Confirmed at slot {confirmation.slot}")
    """
    start_time = time.time()

    while (time.time() - start_time) * 1000 < timeout_ms:
        response = connection.get_signature_statuses([signature])
        status = response.value[0] if response.value else None

        if status:
            if status.err:
                raise Exception(f"Transaction failed: {status.err}")

            confirmation_status = status.confirmation_status
            if confirmation_status:
                status_str = str(confirmation_status).lower()
                if (
                    status_str == "finalized"
                    or (commitment == "confirmed" and status_str in ("confirmed", "finalized"))
                    or (commitment == "processed" and status_str in ("processed", "confirmed", "finalized"))
                ):
                    return TransactionConfirmation(
                        signature=signature,
                        slot=status.slot,
                        confirmation_status=status_str,  # type: ignore
                        err=str(status.err) if status.err else None,
                    )

        time.sleep(2)

    raise TimeoutError(f"Transaction confirmation timeout after {timeout_ms}ms")


def sign_send_and_confirm(
    connection: Client,
    transaction_base64: str,
    signer: Keypair,
    commitment: Commitment = "confirmed",
) -> TransactionConfirmation:
    """Sign, send, and wait for confirmation in one call.

    Convenience function that combines sign_and_send_transaction and
    wait_for_confirmation into a single operation.

    Args:
        connection: Solana RPC connection
        transaction_base64: Base64-encoded transaction (from DFlow API responses)
        signer: Keypair to sign the transaction with
        commitment: Desired confirmation level (default: 'confirmed')

    Returns:
        Confirmation details including signature, slot, and status

    Raises:
        Exception: If transaction fails or times out

    Example:
        >>> from solana.rpc.api import Client
        >>> from solders.keypair import Keypair
        >>> from dflow import DFlowClient, sign_send_and_confirm, USDC_MINT
        >>>
        >>> dflow = DFlowClient()
        >>> connection = Client("https://api.mainnet-beta.solana.com")
        >>> keypair = Keypair.from_bytes(secret_key)
        >>>
        >>> # Get a swap transaction
        >>> swap = dflow.swap.create_swap(
        ...     input_mint=USDC_MINT,
        ...     output_mint=yes_mint,
        ...     amount=1000000,
        ...     slippage_bps=50,
        ...     user_public_key=str(keypair.pubkey()),
        ... )
        >>>
        >>> # Sign, send, and wait for confirmation
        >>> result = sign_send_and_confirm(connection, swap.swap_transaction, keypair)
        >>> print(f"Transaction confirmed: {result.signature}")
        >>> print(f"Slot: {result.slot}")
    """
    signature = sign_and_send_transaction(connection, transaction_base64, signer)
    return wait_for_confirmation(connection, signature, commitment)


async def wait_for_confirmation_async(
    connection: Client,
    signature: str,
    commitment: Commitment = "confirmed",
    timeout_ms: int = 60000,
) -> TransactionConfirmation:
    """Async version of wait_for_confirmation.

    Args:
        connection: Solana RPC connection
        signature: Transaction signature to wait for
        commitment: Desired confirmation level (default: 'confirmed')
        timeout_ms: Maximum time to wait in milliseconds (default: 60000)

    Returns:
        Confirmation details including slot and status

    Raises:
        Exception: If transaction fails or times out
    """
    start_time = time.time()

    while (time.time() - start_time) * 1000 < timeout_ms:
        response = connection.get_signature_statuses([signature])
        status = response.value[0] if response.value else None

        if status:
            if status.err:
                raise Exception(f"Transaction failed: {status.err}")

            confirmation_status = status.confirmation_status
            if confirmation_status:
                status_str = str(confirmation_status).lower()
                if (
                    status_str == "finalized"
                    or (commitment == "confirmed" and status_str in ("confirmed", "finalized"))
                    or (commitment == "processed" and status_str in ("processed", "confirmed", "finalized"))
                ):
                    return TransactionConfirmation(
                        signature=signature,
                        slot=status.slot,
                        confirmation_status=status_str,  # type: ignore
                        err=str(status.err) if status.err else None,
                    )

        await asyncio.sleep(2)

    raise TimeoutError(f"Transaction confirmation timeout after {timeout_ms}ms")
