# DFlow Python SDK

[![PyPI version](https://badge.fury.io/py/dflow-sdk.svg)](https://badge.fury.io/py/dflow-sdk)
[![Python versions](https://img.shields.io/pypi/pyversions/dflow-sdk.svg)](https://pypi.org/project/dflow-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

🐍 **Python SDK for DFlow on Solana - prediction markets and trading**

## Installation

```bash
pip install dflow-sdk
```

Or with a package manager:

```bash
# Poetry
poetry add dflow-sdk

# UV
uv add dflow-sdk

# PDM
pdm add dflow-sdk
```

## Quick Start

```python
from dflow import DFlowClient

# Development environment (no API key required)
client = DFlowClient()

# Get active markets
response = client.markets.get_markets(status="active")
for market in response.markets:
    print(f"{market.ticker}: YES={market.yes_price}, NO={market.no_price}")

# Get a specific market
market = client.markets.get_market("BTCD-25DEC0313-T92749.99")
print(f"Volume: {market.volume}")
```

## Production Usage

```python
from dflow import DFlowClient

# Production environment (API key required)
client = DFlowClient(environment="production", api_key="your-api-key")

# Get a swap quote
quote = client.swap.get_quote(
    input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    output_mint=market.accounts["usdc"].yes_mint,
    amount=1_000_000,  # 1 USDC
)
print(f"You'll receive: {quote.out_amount} tokens")
```

## Trading with Solana

```python
from solders.keypair import Keypair
from solana.rpc.api import Client
from dflow import DFlowClient, sign_send_and_confirm, USDC_MINT

# Setup
dflow = DFlowClient(environment="production", api_key="your-api-key")
connection = Client("https://api.mainnet-beta.solana.com")
keypair = Keypair.from_bytes(your_secret_key)

# Create a swap transaction
swap = dflow.swap.create_swap(
    input_mint=USDC_MINT,
    output_mint=yes_mint,
    amount=1_000_000,
    slippage_bps=50,
    user_public_key=str(keypair.pubkey()),
)

# Sign and send
result = sign_send_and_confirm(connection, swap.swap_transaction, keypair)
print(f"Transaction confirmed: {result.signature}")
```

## WebSocket Streaming

```python
import asyncio
from dflow import DFlowClient

async def main():
    client = DFlowClient()
    
    # Connect to WebSocket
    await client.ws.connect()
    
    # Subscribe to price updates
    await client.ws.subscribe_prices(["BTCD-25DEC0313-T92749.99"])
    
    # Handle updates
    def on_price(update):
        print(f"{update.ticker}: YES={update.yes_price}")
    
    client.ws.on_price(on_price)
    
    # Keep running
    await asyncio.sleep(60)
    client.ws.disconnect()

asyncio.run(main())
```

## Features

- **Full API Coverage**: Events, Markets, Orderbook, Trades, Series, Tags, Sports, Search
- **Trading APIs**: Orders, Swap, Intent-based swaps, Prediction market initialization
- **Solana Integration**: Transaction signing, token balances, position tracking
- **WebSocket Support**: Real-time price, trade, and orderbook updates
- **Type Safety**: Full Pydantic models for all API responses
- **Async Support**: Both sync and async HTTP clients available

## API Modules

| Module | Description |
|--------|-------------|
| `client.events` | Event discovery and queries |
| `client.markets` | Market data, pricing, batch queries |
| `client.orderbook` | Orderbook snapshots |
| `client.trades` | Historical trade data |
| `client.live_data` | Real-time milestone data |
| `client.series` | Series/category information |
| `client.tags` | Tag-based filtering |
| `client.sports` | Sports-specific filters |
| `client.search` | Full-text search |
| `client.orders` | Order creation and status |
| `client.swap` | Imperative swaps with route preview |
| `client.intent` | Declarative intent-based swaps |
| `client.prediction_market` | Market initialization |
| `client.tokens` | Token information |
| `client.venues` | Trading venue information |
| `client.ws` | WebSocket for real-time updates |

## Documentation

See the [full documentation](https://dflow-sdk.vercel.app/docs) for detailed API reference.

## License

MIT
