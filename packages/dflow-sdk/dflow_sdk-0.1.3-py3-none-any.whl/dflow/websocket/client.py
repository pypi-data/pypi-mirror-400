"""WebSocket client for DFlow SDK."""

import asyncio
import json
from collections.abc import Callable
from typing import Any

import websockets
from websockets import ClientConnection

from dflow.types import OrderbookUpdate, PriceUpdate, TradeUpdate, WebSocketChannel
from dflow.utils.constants import WEBSOCKET_URL


class DFlowWebSocket:
    """WebSocket client for real-time price, trade, and orderbook updates.

    Provides streaming market data with automatic reconnection support.
    Subscribe to specific markets or all markets for each data channel.

    Example:
        >>> import asyncio
        >>> from dflow import DFlowClient
        >>>
        >>> async def main():
        ...     dflow = DFlowClient()
        ...
        ...     # Connect to WebSocket
        ...     await dflow.ws.connect()
        ...
        ...     # Subscribe to price updates for specific markets
        ...     await dflow.ws.subscribe_prices(["BTCD-25DEC0313-T92749.99"])
        ...
        ...     # Handle price updates
        ...     def on_price(update):
        ...         print(f"{update.ticker}: YES={update.yes_price} NO={update.no_price}")
        ...
        ...     unsubscribe = dflow.ws.on_price(on_price)
        ...
        ...     # Keep running for a while
        ...     await asyncio.sleep(60)
        ...
        ...     # Cleanup
        ...     unsubscribe()
        ...     dflow.ws.disconnect()
        >>>
        >>> asyncio.run(main())
    """

    def __init__(
        self,
        url: str | None = None,
        reconnect: bool = True,
        reconnect_interval: float = 5.0,
        max_reconnect_attempts: int = 10,
    ):
        """Create a new WebSocket client.

        Args:
            url: Custom WebSocket URL (defaults to DFlow WebSocket)
            reconnect: Whether to auto-reconnect on disconnect (default: True)
            reconnect_interval: Seconds between reconnect attempts (default: 5.0)
            max_reconnect_attempts: Max reconnection attempts (default: 10)
        """
        self.url = url or WEBSOCKET_URL
        self.reconnect = reconnect
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts

        self._ws: ClientConnection | None = None
        self._reconnect_attempts = 0
        self._is_connecting = False
        self._listen_task: asyncio.Task[Any] | None = None

        self._price_callbacks: list[Callable[[PriceUpdate], None]] = []
        self._trade_callbacks: list[Callable[[TradeUpdate], None]] = []
        self._orderbook_callbacks: list[Callable[[OrderbookUpdate], None]] = []
        self._error_callbacks: list[Callable[[Exception], None]] = []
        self._close_callbacks: list[Callable[[], None]] = []

    async def connect(self) -> None:
        """Connect to the WebSocket server.

        Must be called before subscribing to any channels.
        Resolves when connection is established.

        Raises:
            Exception: If connection fails

        Example:
            >>> await dflow.ws.connect()
            >>> print("Connected!", dflow.ws.is_connected)
        """
        if self._ws is not None and not self._ws.closed:
            return

        if self._is_connecting:
            return

        self._is_connecting = True

        try:
            self._ws = await websockets.connect(self.url)
            self._is_connecting = False
            self._reconnect_attempts = 0

            # Start listening for messages
            self._listen_task = asyncio.create_task(self._listen())
        except Exception as e:
            self._is_connecting = False
            raise e

    async def _listen(self) -> None:
        """Listen for incoming messages."""
        if self._ws is None:
            return

        try:
            async for message in self._ws:
                self._handle_message(message)
        except websockets.ConnectionClosed:
            for cb in self._close_callbacks:
                cb()
            await self._attempt_reconnect()
        except Exception as e:
            for cb in self._error_callbacks:
                cb(e)
            await self._attempt_reconnect()

    def _handle_message(self, message: str | bytes) -> None:
        """Handle an incoming WebSocket message."""
        try:
            if isinstance(message, bytes):
                message = message.decode("utf-8")

            data = json.loads(message)
            channel = data.get("channel")

            if channel == "prices":
                update = PriceUpdate.model_validate(data)
                for cb in self._price_callbacks:
                    cb(update)
            elif channel == "trades":
                update = TradeUpdate.model_validate(data)
                for cb in self._trade_callbacks:
                    cb(update)
            elif channel == "orderbook":
                update = OrderbookUpdate.model_validate(data)
                for cb in self._orderbook_callbacks:
                    cb(update)
        except Exception as e:
            for cb in self._error_callbacks:
                cb(e)

    async def _attempt_reconnect(self) -> None:
        """Attempt to reconnect to the WebSocket server."""
        if not self.reconnect:
            return

        if self._reconnect_attempts >= self.max_reconnect_attempts:
            error = Exception("Max reconnection attempts reached")
            for cb in self._error_callbacks:
                cb(error)
            return

        self._reconnect_attempts += 1
        await asyncio.sleep(self.reconnect_interval)

        try:
            await self.connect()
        except Exception:
            pass  # Will retry on next attempt

    def disconnect(self) -> None:
        """Disconnect from the WebSocket server.

        Disables auto-reconnect and closes the connection.

        Example:
            >>> dflow.ws.disconnect()
        """
        self.reconnect = False

        if self._listen_task:
            self._listen_task.cancel()
            self._listen_task = None

        if self._ws:
            asyncio.create_task(self._ws.close())
            self._ws = None

    async def _send(self, message: dict[str, Any]) -> None:
        """Send a message to the WebSocket server."""
        if self._ws is None or self._ws.closed:
            raise Exception("WebSocket is not connected")
        await self._ws.send(json.dumps(message))

    async def subscribe_prices(self, tickers: list[str]) -> None:
        """Subscribe to price updates for specific markets.

        Args:
            tickers: Array of market tickers to subscribe to

        Raises:
            Exception: If WebSocket is not connected

        Example:
            >>> await dflow.ws.subscribe_prices(["BTCD-25DEC0313-T92749.99"])
        """
        await self._send({"type": "subscribe", "channel": "prices", "tickers": tickers})

    async def subscribe_all_prices(self) -> None:
        """Subscribe to price updates for all markets.

        Raises:
            Exception: If WebSocket is not connected

        Example:
            >>> await dflow.ws.subscribe_all_prices()
        """
        await self._send({"type": "subscribe", "channel": "prices", "all": True})

    async def subscribe_trades(self, tickers: list[str]) -> None:
        """Subscribe to trade updates for specific markets.

        Args:
            tickers: Array of market tickers to subscribe to

        Raises:
            Exception: If WebSocket is not connected

        Example:
            >>> await dflow.ws.subscribe_trades(["BTCD-25DEC0313-T92749.99"])
        """
        await self._send({"type": "subscribe", "channel": "trades", "tickers": tickers})

    async def subscribe_all_trades(self) -> None:
        """Subscribe to trade updates for all markets.

        Raises:
            Exception: If WebSocket is not connected

        Example:
            >>> await dflow.ws.subscribe_all_trades()
        """
        await self._send({"type": "subscribe", "channel": "trades", "all": True})

    async def subscribe_orderbook(self, tickers: list[str]) -> None:
        """Subscribe to orderbook updates for specific markets.

        Args:
            tickers: Array of market tickers to subscribe to

        Raises:
            Exception: If WebSocket is not connected

        Example:
            >>> await dflow.ws.subscribe_orderbook(["BTCD-25DEC0313-T92749.99"])
        """
        await self._send({"type": "subscribe", "channel": "orderbook", "tickers": tickers})

    async def subscribe_all_orderbook(self) -> None:
        """Subscribe to orderbook updates for all markets.

        Raises:
            Exception: If WebSocket is not connected

        Example:
            >>> await dflow.ws.subscribe_all_orderbook()
        """
        await self._send({"type": "subscribe", "channel": "orderbook", "all": True})

    async def unsubscribe(
        self, channel: WebSocketChannel, tickers: list[str] | None = None
    ) -> None:
        """Unsubscribe from a channel.

        Args:
            channel: The channel to unsubscribe from ('prices', 'trades', or 'orderbook')
            tickers: Optional specific tickers to unsubscribe. If omitted, unsubscribes from all.

        Raises:
            Exception: If WebSocket is not connected

        Example:
            >>> # Unsubscribe from specific markets
            >>> await dflow.ws.unsubscribe("prices", ["BTCD-25DEC0313-T92749.99"])
            >>>
            >>> # Unsubscribe from all on a channel
            >>> await dflow.ws.unsubscribe("trades")
        """
        if tickers:
            await self._send({"type": "unsubscribe", "channel": channel, "tickers": tickers})
        else:
            await self._send({"type": "unsubscribe", "channel": channel, "all": True})

    def on_price(self, callback: Callable[[PriceUpdate], None]) -> Callable[[], None]:
        """Register a callback for price updates.

        Args:
            callback: Function called when a price update is received

        Returns:
            Unsubscribe function to remove the callback

        Example:
            >>> def handle_price(update):
            ...     print(f"{update.ticker}: YES={update.yes_price} NO={update.no_price}")
            >>>
            >>> unsubscribe = dflow.ws.on_price(handle_price)
            >>> # Later: remove callback
            >>> unsubscribe()
        """
        self._price_callbacks.append(callback)
        return lambda: self._price_callbacks.remove(callback)

    def on_trade(self, callback: Callable[[TradeUpdate], None]) -> Callable[[], None]:
        """Register a callback for trade updates.

        Args:
            callback: Function called when a trade update is received

        Returns:
            Unsubscribe function to remove the callback

        Example:
            >>> def handle_trade(trade):
            ...     print(f"Trade: {trade.side} {trade.quantity} @ {trade.price}")
            >>>
            >>> unsubscribe = dflow.ws.on_trade(handle_trade)
        """
        self._trade_callbacks.append(callback)
        return lambda: self._trade_callbacks.remove(callback)

    def on_orderbook(
        self, callback: Callable[[OrderbookUpdate], None]
    ) -> Callable[[], None]:
        """Register a callback for orderbook updates.

        Args:
            callback: Function called when an orderbook update is received

        Returns:
            Unsubscribe function to remove the callback

        Example:
            >>> def handle_orderbook(book):
            ...     print(f"{book.ticker}: Bid={book.yes_bid[0].price}")
            >>>
            >>> unsubscribe = dflow.ws.on_orderbook(handle_orderbook)
        """
        self._orderbook_callbacks.append(callback)
        return lambda: self._orderbook_callbacks.remove(callback)

    def on_error(self, callback: Callable[[Exception], None]) -> Callable[[], None]:
        """Register a callback for WebSocket errors.

        Args:
            callback: Function called when an error occurs

        Returns:
            Unsubscribe function to remove the callback

        Example:
            >>> def handle_error(error):
            ...     print(f"WebSocket error: {error}")
            >>>
            >>> unsubscribe = dflow.ws.on_error(handle_error)
        """
        self._error_callbacks.append(callback)
        return lambda: self._error_callbacks.remove(callback)

    def on_close(self, callback: Callable[[], None]) -> Callable[[], None]:
        """Register a callback for WebSocket close events.

        Args:
            callback: Function called when the connection closes

        Returns:
            Unsubscribe function to remove the callback

        Example:
            >>> def handle_close():
            ...     print("WebSocket closed")
            >>>
            >>> unsubscribe = dflow.ws.on_close(handle_close)
        """
        self._close_callbacks.append(callback)
        return lambda: self._close_callbacks.remove(callback)

    @property
    def is_connected(self) -> bool:
        """Check if the WebSocket is currently connected.

        Returns:
            True if connected, False otherwise

        Example:
            >>> if dflow.ws.is_connected:
            ...     await dflow.ws.subscribe_prices(["BTCD-25DEC0313-T92749.99"])
        """
        return self._ws is not None and not self._ws.closed
